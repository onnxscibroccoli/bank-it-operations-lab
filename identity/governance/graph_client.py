"""Offline Microsoft Graph read client for the identity-governance lab.

OFFLINE / SYNTHETIC ONLY. This module deliberately contains NO network transport: the only
transport shipped is ``FixtureTransport``, which answers requests from JSON files under
``fixtures/graph/scenarios/``. There is no code path that opens a socket, reads a credential or
authenticates to a tenant. A real deployment would have to supply its own transport object with a
``get(url) -> Response`` method; that is intentionally out of scope for this repository.

Behaviour modelled on documented Microsoft Graph semantics:
  * paging: follow ``@odata.nextLink`` until absent (https://learn.microsoft.com/en-us/graph/paging)
  * throttling: HTTP 429 (and 503/504) with ``Retry-After`` seconds
    (https://learn.microsoft.com/en-us/graph/throttling)
  * errors: ``{"error": {"code", "message", "innerError": {"request-id"}}}``
    (https://learn.microsoft.com/en-us/graph/errors)

Python 3 standard library only.
"""
import json
import os
import time

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"
RETRYABLE = (429, 503, 504)


class GraphError(Exception):
    """Base class. Carries HTTP status, Graph error code and request-id when present."""

    kind = "graph-error"

    def __init__(self, message, status=None, code=None, request_id=None, url=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.request_id = request_id
        self.url = url

    def as_dict(self):
        return {"kind": self.kind, "status": self.status, "code": self.code,
                "requestId": self.request_id, "url": self.url, "message": str(self)}


class GraphAuthError(GraphError):
    """401 (no/invalid token) or 403 (token lacks permission / role / license). Never retried."""

    kind = "authorization"


class GraphThrottledError(GraphError):
    """Still throttled (429/503/504) after the retry budget was spent."""

    kind = "throttled"


class GraphResponseError(GraphError):
    """Unexpected status, malformed body, or a paging loop."""

    kind = "response"


class Response(object):
    def __init__(self, status, body=None, headers=None):
        self.status = int(status)
        self.body = body
        self.headers = {str(k).lower(): str(v) for k, v in (headers or {}).items()}


def _graph_error_parts(body):
    err = body.get("error") if isinstance(body, dict) else None
    if not isinstance(err, dict):
        return None, None, None
    inner = err.get("innerError") or err.get("innererror") or {}
    rid = inner.get("request-id") if isinstance(inner, dict) else None
    return err.get("code"), err.get("message"), rid


class FixtureTransport(object):
    """Serves Graph responses from a scenario directory.

    ``routes.json``::

        {"inherit": "baseline",                      # optional parent scenario
         "asOfUtc": "2026-10-28T12:00:00Z",          # evaluation clock for the scenario
         "routes": {"/users?$select=...": [ {"status": 200, "bodyFile": "users.json"},
                                              {"status": 429, "headers": {"Retry-After": "2"}} ]}}

    Each route is a list of responses served in order; the last one repeats. ``bodyFile`` is
    resolved relative to the scenario that declared it. Unknown routes return a Graph-shaped 404.
    """

    def __init__(self, scenario_dir):
        self.scenario_dir = os.path.abspath(scenario_dir)
        self.routes, self.meta = self._load(self.scenario_dir, set())
        self.calls = []
        self._served = {}

    @staticmethod
    def _load(scenario_dir, seen):
        if scenario_dir in seen:
            raise GraphResponseError("fixture inherit cycle at %s" % scenario_dir)
        seen.add(scenario_dir)
        path = os.path.join(scenario_dir, "routes.json")
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        routes, meta = {}, {}
        if doc.get("inherit"):
            parent = os.path.join(os.path.dirname(scenario_dir), doc["inherit"])
            routes, meta = FixtureTransport._load(parent, seen)
        for key, seq in (doc.get("routes") or {}).items():
            if seq is None:
                routes.pop(key, None)
                continue
            if isinstance(seq, dict):
                seq = [seq]
            resolved = []
            for r in seq:
                r = dict(r)
                if "bodyFile" in r:
                    r["bodyFile"] = os.path.join(scenario_dir, r["bodyFile"])
                resolved.append(r)
            routes[key] = resolved
        meta.update({k: v for k, v in doc.items() if k not in ("routes", "inherit")})
        return routes, meta

    def get(self, url):
        if not url.startswith(GRAPH_ROOT + "/"):
            raise GraphResponseError("refusing non-Graph URL %r" % url, url=url)
        key = url[len(GRAPH_ROOT):]
        self.calls.append(key)
        seq = self.routes.get(key)
        if not seq:
            return Response(404, {"error": {"code": "Request_ResourceNotFound",
                                            "message": "no fixture route for %s" % key,
                                            "innerError": {"request-id": "synthetic-404"}}})
        n = self._served.get(key, 0)
        self._served[key] = n + 1
        r = seq[min(n, len(seq) - 1)]
        body = r.get("body")
        if "bodyFile" in r:
            with open(r["bodyFile"], encoding="utf-8") as fh:
                text = fh.read()
            try:
                body = json.loads(text)
            except ValueError:
                body = text  # deliberately malformed fixture body
        return Response(r.get("status", 200), body, r.get("headers"))


class GraphClient(object):
    """Read-only Graph client with paging, throttling back-off and fail-closed auth errors."""

    def __init__(self, transport, max_retries=4, sleep=time.sleep, max_pages=500, max_retry_after=120):
        self.transport = transport
        self.max_retries = max_retries
        self.sleep = sleep
        self.max_pages = max_pages
        self.max_retry_after = max_retry_after
        self.retry_log = []
        self.pages_fetched = 0

    def _wait_seconds(self, resp, attempt):
        raw = resp.headers.get("retry-after")
        try:
            secs = int(str(raw).strip())
            if secs < 0:
                raise ValueError
        except (TypeError, ValueError):
            secs = min(2 ** attempt, 32)  # documented fallback: exponential back-off
        return min(secs, self.max_retry_after)

    def get_json(self, url):
        attempt = 0
        while True:
            resp = self.transport.get(url)
            if resp.status == 200:
                if not isinstance(resp.body, dict):
                    raise GraphResponseError("non-JSON-object body", status=200, url=url)
                return resp.body
            code, msg, rid = _graph_error_parts(resp.body)
            if resp.status in (401, 403):
                raise GraphAuthError("HTTP %d %s: %s" % (resp.status, code, msg), resp.status, code, rid, url)
            if resp.status in RETRYABLE:
                if attempt >= self.max_retries:
                    raise GraphThrottledError("HTTP %d after %d retries" % (resp.status, attempt),
                                              resp.status, code, rid, url)
                wait = self._wait_seconds(resp, attempt)
                self.retry_log.append({"url": url, "status": resp.status, "attempt": attempt + 1,
                                       "retryAfterHeader": resp.headers.get("retry-after"), "waitSeconds": wait})
                self.sleep(wait)
                attempt += 1
                continue
            raise GraphResponseError("HTTP %d %s: %s" % (resp.status, code, msg), resp.status, code, rid, url)

    def list_all(self, path):
        """GET a collection and follow @odata.nextLink. Returns the concatenated ``value`` items."""
        url = path if path.startswith("https://") else GRAPH_ROOT + path
        items, seen = [], set()
        while url:
            if url in seen:
                raise GraphResponseError("@odata.nextLink loop", url=url)
            seen.add(url)
            if len(seen) > self.max_pages:
                raise GraphResponseError("page limit %d exceeded" % self.max_pages, url=url)
            body = self.get_json(url)
            self.pages_fetched += 1
            value = body.get("value")
            if not isinstance(value, list):
                raise GraphResponseError("collection page without a 'value' array", url=url)
            items.extend(value)
            nxt = body.get("@odata.nextLink")
            if nxt is not None and not isinstance(nxt, str):
                raise GraphResponseError("@odata.nextLink is not a string", url=url)
            url = nxt
        return items
