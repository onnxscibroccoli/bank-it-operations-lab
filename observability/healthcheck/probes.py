"""Bounded synthetic probes (HTTP, TCP connect, DNS resolve) with injectable transports.

Bounds enforced here:
  * timeout_s must be in (0, MAX_TIMEOUT_S]; the runner also enforces it as a HARD
    wall-clock limit by running each probe in a daemon thread and abandoning it on expiry.
  * HTTP bodies are read up to max_bytes (<= MAX_BODY_BYTES); a larger body is an ERROR.
  * At most MAX_PROBES probes per run; more is a configuration error (fail closed).
  * URLs with embedded credentials (user:pass@) are rejected.

Transports (tests inject fakes, so no network is used in tests):
  http_transport(url, timeout_s, max_bytes) -> (status_code:int, body:bytes)
  tcp_connect(host, port, timeout_s) -> None   (raise on failure)
  resolver(hostname) -> list of address strings
"""

import http.client
import socket
import threading
from urllib.parse import urlsplit

from . import DEFAULT_BODY_BYTES, DEFAULT_TIMEOUT_S, MAX_BODY_BYTES, MAX_PROBES, MAX_TIMEOUT_S
from .timeutil import format_ts, system_clock, system_monotonic

STATUSES = ("OK", "FAIL", "TIMEOUT", "ERROR", "UNKNOWN")
KINDS = ("http", "tcp", "dns")


class ProbeConfigError(ValueError):
    pass


def _check_timeout(t):
    if isinstance(t, bool) or not isinstance(t, (int, float)) or not (0 < t <= MAX_TIMEOUT_S):
        raise ProbeConfigError("timeout_s must be a number in (0, %s]" % MAX_TIMEOUT_S)
    return float(t)


def _check_name(name):
    if not isinstance(name, str) or not name or len(name) > 64 or not all(
            c.isalnum() or c in "-_." for c in name):
        raise ProbeConfigError("probe name must be 1-64 chars of [A-Za-z0-9-_.]")
    return name


# ---- default (real) transports: only used by `collect`, never by tests ------------------

def default_http_transport(url, timeout_s, max_bytes):
    parts = urlsplit(url)
    conn_cls = http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
    conn = conn_cls(parts.hostname, parts.port, timeout=timeout_s)
    try:
        path = parts.path or "/"
        if parts.query:
            path += "?" + parts.query
        conn.request("GET", path, headers={"User-Agent": "bank-it-lab-healthcheck/0.1",
                                           "Connection": "close"})
        resp = conn.getresponse()
        body = resp.read(max_bytes + 1)
        return resp.status, body
    finally:
        conn.close()


def default_tcp_connect(host, port, timeout_s):
    with socket.create_connection((host, port), timeout=timeout_s):
        return None


def default_resolver(hostname):
    return sorted({ai[4][0] for ai in socket.getaddrinfo(hostname, None)})


# ---- probe definitions ---------------------------------------------------------------

class Probe:
    kind = None

    def __init__(self, name, timeout_s=DEFAULT_TIMEOUT_S):
        self.name = _check_name(name)
        self.timeout_s = _check_timeout(timeout_s)

    def target(self):  # redacted, log-safe description
        raise NotImplementedError

    def check(self):
        """Return (status, detail). May raise; the runner maps exceptions."""
        raise NotImplementedError


class HttpProbe(Probe):
    kind = "http"

    def __init__(self, name, url, expect_status=(200,), timeout_s=DEFAULT_TIMEOUT_S,
                 max_bytes=DEFAULT_BODY_BYTES, expect_substring=None, transport=None):
        super().__init__(name, timeout_s)
        parts = urlsplit(url) if isinstance(url, str) else None
        if parts is None or parts.scheme not in ("http", "https") or not parts.hostname:
            raise ProbeConfigError("url must be http(s)://host[...]")
        if parts.username or parts.password:
            raise ProbeConfigError("url must not embed credentials")
        if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or not (
                0 < max_bytes <= MAX_BODY_BYTES):
            raise ProbeConfigError("max_bytes must be an int in (0, %d]" % MAX_BODY_BYTES)
        if not expect_status or not all(isinstance(s, int) and 100 <= s <= 599 for s in expect_status):
            raise ProbeConfigError("expect_status must be a non-empty list of HTTP codes")
        self.url = url
        self._parts = parts
        self.expect_status = tuple(expect_status)
        self.max_bytes = max_bytes
        self.expect_substring = expect_substring
        self.transport = transport or default_http_transport

    def target(self):
        p = self._parts
        port = ":%d" % p.port if p.port else ""
        return "%s://%s%s%s" % (p.scheme, p.hostname, port, p.path or "/")  # query dropped

    def check(self):
        status, body = self.transport(self.url, self.timeout_s, self.max_bytes)
        if not isinstance(status, int) or not isinstance(body, (bytes, bytearray)):
            return "ERROR", "transport returned malformed response"
        if len(body) > self.max_bytes:
            return "ERROR", "response body exceeded max_bytes=%d" % self.max_bytes
        if status not in self.expect_status:
            return "FAIL", "HTTP %d not in %s" % (status, list(self.expect_status))
        if self.expect_substring is not None and self.expect_substring.encode() not in body:
            return "FAIL", "HTTP %d but expected substring missing" % status
        return "OK", "HTTP %d" % status


class TcpProbe(Probe):
    kind = "tcp"

    def __init__(self, name, host, port, timeout_s=DEFAULT_TIMEOUT_S, connect=None):
        super().__init__(name, timeout_s)
        if not isinstance(host, str) or not host:
            raise ProbeConfigError("host must be a non-empty string")
        if isinstance(port, bool) or not isinstance(port, int) or not (0 < port < 65536):
            raise ProbeConfigError("port must be 1-65535")
        self.host, self.port = host, port
        self.connect = connect or default_tcp_connect

    def target(self):
        return "%s:%d" % (self.host, self.port)

    def check(self):
        self.connect(self.host, self.port, self.timeout_s)
        return "OK", "connected"


class DnsProbe(Probe):
    kind = "dns"

    def __init__(self, name, hostname, timeout_s=DEFAULT_TIMEOUT_S, min_answers=1, resolver=None):
        super().__init__(name, timeout_s)
        if not isinstance(hostname, str) or not hostname or len(hostname) > 253:
            raise ProbeConfigError("hostname must be a non-empty string <= 253 chars")
        if isinstance(min_answers, bool) or not isinstance(min_answers, int) or min_answers < 1:
            raise ProbeConfigError("min_answers must be an int >= 1")
        self.hostname, self.min_answers = hostname, min_answers
        self.resolver = resolver or default_resolver

    def target(self):
        return self.hostname

    def check(self):
        answers = self.resolver(self.hostname)
        if not isinstance(answers, (list, tuple)):
            return "ERROR", "resolver returned malformed answer"
        if len(answers) < self.min_answers:
            return "FAIL", "%d answers < min %d" % (len(answers), self.min_answers)
        return "OK", "%d answers" % len(answers)


def probe_from_config(cfg, transports=None):
    """Build a probe from a config dict. transports: optional {'http','tcp','dns'} fakes."""
    transports = transports or {}
    if not isinstance(cfg, dict):
        raise ProbeConfigError("probe config must be an object")
    kind = cfg.get("kind")
    allowed = {
        "http": {"name", "kind", "url", "expect_status", "timeout_s", "max_bytes", "expect_substring"},
        "tcp": {"name", "kind", "host", "port", "timeout_s"},
        "dns": {"name", "kind", "hostname", "timeout_s", "min_answers"},
    }
    if kind not in allowed:
        raise ProbeConfigError("kind must be one of %s" % list(KINDS))
    extra = set(cfg) - allowed[kind]
    if extra:
        raise ProbeConfigError("unknown probe keys: %s" % sorted(extra))
    kw = {k: v for k, v in cfg.items() if k != "kind"}
    if kind == "http":
        return HttpProbe(transport=transports.get("http"), **kw)
    if kind == "tcp":
        return TcpProbe(connect=transports.get("tcp"), **kw)
    return DnsProbe(resolver=transports.get("dns"), **kw)


# ---- runner --------------------------------------------------------------------------

def run_probe(probe, clock=system_clock, monotonic=system_monotonic, logger=None):
    """Run one probe under a hard wall-clock timeout. Never raises."""
    box = {}

    def _target():
        try:
            box["result"] = probe.check()
        except (socket.timeout, TimeoutError) as exc:
            box["result"] = ("TIMEOUT", "transport timeout (%s)" % type(exc).__name__)
        except Exception as exc:
            box["result"] = ("ERROR", type(exc).__name__)

    started = monotonic()
    worker = threading.Thread(target=_target, name="probe-%s" % probe.name, daemon=True)
    worker.start()
    worker.join(probe.timeout_s)
    if worker.is_alive():
        status, detail = "TIMEOUT", "hard timeout %.3fs exceeded" % probe.timeout_s
    else:
        status, detail = box.get("result", ("UNKNOWN", "probe produced no result"))
    if status not in STATUSES:
        status, detail = "UNKNOWN", "probe returned unrecognised status"
    latency_ms = round(max(0.0, monotonic() - started) * 1000.0, 3)
    res = {"name": probe.name, "kind": probe.kind, "target": probe.target(), "status": status,
           "detail": str(detail)[:200], "latency_ms": latency_ms,
           "observed_at": format_ts(clock())}
    if logger is not None:
        logger.log("INFO" if status == "OK" else "WARNING", "probe.result", probe=probe.name,
                   kind=probe.kind, target=res["target"], status=status, detail=res["detail"],
                   latency_ms=latency_ms)
    return res


def run_probes(probes, clock=system_clock, monotonic=system_monotonic, logger=None,
               max_probes=MAX_PROBES):
    probes = list(probes)
    if len(probes) > max_probes:
        raise ProbeConfigError("too many probes: %d > max %d" % (len(probes), max_probes))
    names = [p.name for p in probes]
    if len(set(names)) != len(names):
        raise ProbeConfigError("duplicate probe names")
    return [run_probe(p, clock=clock, monotonic=monotonic, logger=logger) for p in probes]
