"""SIMULATION - in-process mock of the fictional 'Acme Core Ledger SIMULATION' API.

No sockets, no network. Responses are built from fixtures/*.json and labelled SIMULATION
(body field "simulation": "SIMULATION" and header X-Simulation: SIMULATION).
Scenarios inject failure modes used by the offline client contract tests.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"

SCENARIOS = (
    "normal",
    "auth_invalid_client",        # /oauth/token -> 401 invalid_client
    "auth_token_rejected",        # resource calls always 401 invalid_token
    "auth_token_expired_once",    # first resource call 401 invalid_token, then OK
    "timeout",                    # simulated latency always exceeds any client timeout
    "timeout_once",               # first resource call times out, then OK
    "rate_limit_once",            # first resource call 429 Retry-After: 1, then OK
    "rate_limit_always",          # every resource call 429 Retry-After: 1
    "rate_limit_long",            # 429 Retry-After: 3600 (beyond client cap)
    "rate_limit_bad_retry_after", # 429 with non-numeric Retry-After
    "rate_limit_no_retry_after",  # 429 with no Retry-After header
    "malformed_truncated_json",
    "malformed_missing_field",
    "malformed_extra_field",
    "malformed_wrong_type",
    "malformed_nan",
    "malformed_wrong_content_type",
    "malformed_missing_sim_header",
    "malformed_undeclared_status",
    "malformed_non_utf8",
)


class SimulatedTimeout(TimeoutError):
    """SIMULATION - raised by the in-process transport instead of a real socket timeout."""


@dataclass
class Response:
    status: int
    headers: dict
    body: bytes


def _load(name: str) -> dict:
    with open(FIXTURES / name, encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class AcmeLedgerMock:
    scenario: str = "normal"
    latency_s: float = 0.01
    calls: list = field(default_factory=list)
    _resource_calls: int = 0
    _tokens: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.scenario not in SCENARIOS:
            raise ValueError(f"unknown SIMULATION scenario {self.scenario!r}")
        self.accounts = {a["account_id"]: a for a in _load("accounts.json")["accounts"]}
        self.transactions = _load("transactions.json")["transactions"]
        self.clients = _load("clients.json")["clients"]

    # -- helpers ---------------------------------------------------------------------
    def _rid(self) -> str:
        n = len(self.calls)
        return "SIM-REQ-" + hashlib.sha256(f"{self.scenario}:{n}".encode()).hexdigest()[:12]

    def _json(self, status: int, payload, extra_headers=None) -> Response:
        headers = {"Content-Type": "application/json", "X-Simulation": "SIMULATION"}
        headers.update(extra_headers or {})
        return Response(status, headers, json.dumps(payload).encode("utf-8"))

    def _error(self, status: int, code: str, msg: str, extra_headers=None) -> Response:
        return self._json(status, {"simulation": "SIMULATION", "error": code,
                                   "message": f"SIMULATION {msg}", "request_id": self._rid()},
                          extra_headers)

    # -- entry point -----------------------------------------------------------------
    def handle(self, method: str, url: str, headers: dict, body: bytes, timeout: float) -> Response:
        self.calls.append((method, url))
        parts = urlsplit(url)
        path = parts.path
        sc = self.scenario
        if method == "GET" and path == "/v1/health":
            return self._json(200, {"simulation": "SIMULATION", "status": "OK"})
        if method == "POST" and path == "/oauth/token":
            return self._token(body)

        # resource endpoints
        self._resource_calls += 1
        first = self._resource_calls == 1
        if sc == "timeout" or (sc == "timeout_once" and first):
            raise SimulatedTimeout(f"SIMULATION latency exceeded client timeout {timeout}s")
        if self.latency_s > timeout:
            raise SimulatedTimeout(f"SIMULATION latency {self.latency_s}s > timeout {timeout}s")
        if sc == "rate_limit_always" or (sc == "rate_limit_once" and first):
            return self._error(429, "rate_limited", "rate limit exceeded", {"Retry-After": "1"})
        if sc == "rate_limit_long":
            return self._error(429, "rate_limited", "rate limit exceeded", {"Retry-After": "3600"})
        if sc == "rate_limit_bad_retry_after":
            return self._error(429, "rate_limited", "rate limit exceeded", {"Retry-After": "soon"})
        if sc == "rate_limit_no_retry_after":
            return self._error(429, "rate_limited", "rate limit exceeded")

        auth = {k.lower(): v for k, v in headers.items()}.get("authorization", "")
        token = auth[7:] if auth.startswith("Bearer ") else None
        if sc == "auth_token_rejected" or (sc == "auth_token_expired_once" and first):
            return self._error(401, "invalid_token", "token rejected")
        if token not in self._tokens:
            return self._error(401, "invalid_token", "missing or unknown token")
        scopes = self._tokens[token]

        segs = path.strip("/").split("/")
        if method == "GET" and len(segs) == 3 and segs[:2] == ["v1", "accounts"]:
            if "accounts:read" not in scopes:
                return self._error(403, "insufficient_scope", "accounts:read required")
            acct = self.accounts.get(segs[2])
            if acct is None:
                return self._error(404, "not_found", "unknown account")
            return self._mutate(dict(acct))
        if method == "GET" and len(segs) == 4 and segs[:2] == ["v1", "accounts"] and segs[3] == "transactions":
            if "transactions:read" not in scopes:
                return self._error(403, "insufficient_scope", "transactions:read required")
            if segs[2] not in self.accounts:
                return self._error(404, "not_found", "unknown account")
            q = parse_qs(parts.query)
            limit = int(q.get("limit", ["2"])[0])
            start = int(q.get("cursor", ["0"])[0])
            txns = self.transactions.get(segs[2], [])
            page = txns[start:start + limit]
            nxt = str(start + limit) if start + limit < len(txns) else None
            return self._mutate({"simulation": "SIMULATION", "account_id": segs[2],
                                 "transactions": page, "next_cursor": nxt})
        return self._error(404, "not_found", "unknown route")

    def _token(self, body: bytes) -> Response:
        if self.scenario == "auth_invalid_client":
            return self._error(401, "invalid_client", "client authentication failed")
        form = {k: v[0] for k, v in parse_qs(body.decode("utf-8")).items()}
        client = self.clients.get(form.get("client_id", ""))
        if (form.get("grant_type") != "client_credentials" or client is None
                or form.get("client_secret") != client["secret"]):
            return self._error(401, "invalid_client", "client authentication failed")
        tok = "SIMULATION-tok-" + hashlib.sha256(f"{len(self._tokens)}".encode()).hexdigest()[:24]
        self._tokens[tok] = client["scopes"]
        return self._json(200, {"simulation": "SIMULATION", "access_token": tok,
                                "token_type": "Bearer", "expires_in": 300,
                                "scope": " ".join(client["scopes"])})

    def _mutate(self, payload: dict) -> Response:
        """Apply malformed_* scenarios to an otherwise valid 200 payload."""
        sc = self.scenario
        if sc == "malformed_truncated_json":
            r = self._json(200, payload)
            return Response(200, r.headers, r.body[: len(r.body) // 2])
        if sc == "malformed_missing_field":
            payload.pop(next(k for k in payload if k != "simulation"))
        elif sc == "malformed_extra_field":
            payload["ssn"] = "SIMULATION-000-00-0000"
        elif sc == "malformed_wrong_type":
            key = "available_balance" if "available_balance" in payload else "transactions"
            payload[key] = "SIMULATION-not-an-object"
        elif sc == "malformed_nan":
            r = self._json(200, payload)
            body = r.body.replace(b'"simulation": "SIMULATION"', b'"simulation": "SIMULATION", "x": NaN', 1)
            return Response(200, r.headers, body)
        elif sc == "malformed_wrong_content_type":
            r = self._json(200, payload)
            r.headers["Content-Type"] = "text/html"
            return r
        elif sc == "malformed_missing_sim_header":
            r = self._json(200, payload)
            del r.headers["X-Simulation"]
            return r
        elif sc == "malformed_undeclared_status":
            return self._json(418, payload)
        elif sc == "malformed_non_utf8":
            r = self._json(200, payload)
            return Response(200, r.headers, b"\xff\xfe" + r.body)
        return self._json(200, payload)


class InProcessTransport:
    """SIMULATION - transport that calls the mock directly. Opens no sockets."""

    def __init__(self, mock: AcmeLedgerMock):
        self.mock = mock

    def __call__(self, method, url, headers, body, timeout) -> Response:
        return self.mock.handle(method, url, headers, body, timeout)
