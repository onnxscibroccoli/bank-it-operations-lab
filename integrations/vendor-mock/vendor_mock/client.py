"""SIMULATION - reference client for the fictional Acme Core Ledger SIMULATION API.

Fail-closed: every response is validated against contract/openapi.json before use.
Handles auth failure, timeouts, 429 + Retry-After and malformed responses. The transport
is injected; tests use the in-process mock transport, so no network is ever used.
"""
from __future__ import annotations

from urllib.parse import quote, urlencode

from .contract import ContractError, load_contract, validate_response


class VendorError(Exception):
    """SIMULATION - base error."""


class AuthenticationError(VendorError):
    pass


class AuthorizationError(VendorError):
    pass


class NotFoundError(VendorError):
    pass


class VendorTimeoutError(VendorError):
    pass


class RateLimitedError(VendorError):
    def __init__(self, msg, retry_after=None):
        super().__init__(msg)
        self.retry_after = retry_after


class MalformedResponseError(VendorError):
    pass


class VendorUnavailableError(VendorError):
    pass


class AcmeLedgerClient:
    def __init__(self, transport, client_id: str, client_secret: str, *, timeout: float = 2.0,
                 max_retries: int = 2, max_retry_after: int = 30, sleep=None, contract=None):
        self._transport = transport
        self._client_id = client_id
        self._secret = client_secret
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_retry_after = max_retry_after
        self._sleep = sleep or (lambda s: None)
        self._contract = contract or load_contract()
        self._token = None
        self.sleeps: list[float] = []

    def __repr__(self):  # never expose the secret or token
        return f"AcmeLedgerClient(client_id={self._client_id!r}, SIMULATION)"

    # -- low level ---------------------------------------------------------------------
    def _send(self, method, path, headers, body=b""):
        try:
            resp = self._transport(method, path, headers, body, self.timeout)
        except TimeoutError as exc:
            raise VendorTimeoutError(f"SIMULATION {method} {path.split('?')[0]} timed out after {self.timeout}s") from exc
        try:
            parsed = validate_response(self._contract, method, path, resp.status, resp.headers, resp.body)
        except ContractError as exc:
            raise MalformedResponseError(f"SIMULATION {method} {path.split('?')[0]} status {resp.status}: {exc}") from exc
        return resp, parsed

    def _authenticate(self):
        body = urlencode({"grant_type": "client_credentials", "client_id": self._client_id,
                          "client_secret": self._secret}).encode()
        resp, parsed = self._send("POST", "/oauth/token",
                                  {"Content-Type": "application/x-www-form-urlencoded"}, body)
        if resp.status == 200:
            self._token = parsed["access_token"]
            return
        if resp.status == 429:
            raise RateLimitedError("SIMULATION token endpoint rate limited",
                                   int(resp.headers.get("Retry-After", 0)))
        raise AuthenticationError(f"SIMULATION client authentication failed ({parsed['error']})")

    def _get(self, path):
        if self._token is None:
            self._authenticate()
        reauthed = False
        attempt = 0
        while True:
            try:
                resp, parsed = self._send("GET", path, {"Authorization": f"Bearer {self._token}",
                                                        "Accept": "application/json"})
            except VendorTimeoutError:
                if attempt >= self.max_retries:
                    raise
                attempt += 1
                self._backoff(min(2 ** attempt, self.max_retry_after))
                continue
            if resp.status == 200:
                return parsed
            if resp.status == 401:
                if reauthed:
                    raise AuthenticationError(f"SIMULATION token rejected ({parsed['error']})")
                reauthed = True
                self._token = None
                self._authenticate()
                continue
            if resp.status == 429:
                retry_after = int(resp.headers["Retry-After"])  # validated by contract
                if retry_after > self.max_retry_after:
                    raise RateLimitedError(f"SIMULATION Retry-After {retry_after}s exceeds cap "
                                           f"{self.max_retry_after}s", retry_after)
                if attempt >= self.max_retries:
                    raise RateLimitedError("SIMULATION rate limited; retries exhausted", retry_after)
                attempt += 1
                self._backoff(retry_after)
                continue
            if resp.status == 403:
                raise AuthorizationError(f"SIMULATION {parsed['error']}")
            if resp.status == 404:
                raise NotFoundError(f"SIMULATION {parsed['error']}")
            if resp.status == 503:
                raise VendorUnavailableError(f"SIMULATION {parsed['error']}")
            raise MalformedResponseError(f"SIMULATION unhandled status {resp.status}")

    def _backoff(self, seconds):
        self.sleeps.append(seconds)
        self._sleep(seconds)

    # -- API -----------------------------------------------------------------------------
    def health(self):
        return self._send("GET", "/v1/health", {"Accept": "application/json"})[1]

    def get_account(self, account_id: str):
        return self._get(f"/v1/accounts/{quote(account_id, safe='')}")

    def list_transactions(self, account_id: str, limit: int = 2):
        out, cursor = [], None
        while True:
            q = {"limit": limit} | ({"cursor": cursor} if cursor else {})
            page = self._get(f"/v1/accounts/{quote(account_id, safe='')}/transactions?{urlencode(q)}")
            out.extend(page["transactions"])
            cursor = page["next_cursor"]
            if cursor is None:
                return out
