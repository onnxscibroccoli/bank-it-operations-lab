"""Bounded synthetic probes with injected (offline) transports."""

import socket
import threading
import unittest

import _support  # noqa: F401  (sys.path setup)
from healthcheck import MAX_PROBES
from healthcheck.jsonlog import JsonLineLogger
from healthcheck.probes import (DnsProbe, HttpProbe, ProbeConfigError, TcpProbe,
                                probe_from_config, run_probe, run_probes)
from healthcheck.timeutil import StepMonotonic, fixed_clock

CLOCK = fixed_clock("2026-10-28T12:00:00Z")


def run(probe, **kw):
    return run_probe(probe, clock=CLOCK, monotonic=StepMonotonic(0.010), **kw)


def http(transport, **kw):
    return HttpProbe("web", "https://svc.example.com/healthz?token=abc", transport=transport, **kw)


class HttpProbeTests(unittest.TestCase):
    def test_ok(self):
        r = run(http(lambda u, t, m: (200, b"ok")))
        self.assertEqual((r["status"], r["detail"], r["latency_ms"]), ("OK", "HTTP 200", 10.0))
        self.assertEqual(r["observed_at"], "2026-10-28T12:00:00Z")

    def test_target_drops_query_string(self):
        r = run(http(lambda u, t, m: (200, b"")))
        self.assertEqual(r["target"], "https://svc.example.com/healthz")
        self.assertNotIn("token", repr(r))

    def test_unexpected_status_fails(self):
        self.assertEqual(run(http(lambda u, t, m: (503, b"")))["status"], "FAIL")

    def test_expected_substring(self):
        self.assertEqual(run(http(lambda u, t, m: (200, b"degraded"), expect_substring="ok"))["status"],
                         "FAIL")
        self.assertEqual(run(http(lambda u, t, m: (200, b"all ok"), expect_substring="ok"))["status"],
                         "OK")

    def test_body_over_max_bytes_is_error(self):
        seen = {}

        def transport(url, timeout_s, max_bytes):
            seen.update(timeout_s=timeout_s, max_bytes=max_bytes)
            return 200, b"x" * (max_bytes + 1)

        r = run(http(transport, max_bytes=16, timeout_s=1.5))
        self.assertEqual(r["status"], "ERROR")
        self.assertEqual(seen, {"timeout_s": 1.5, "max_bytes": 16})

    def test_malformed_transport_response_is_error(self):
        self.assertEqual(run(http(lambda u, t, m: ("200", "ok")))["status"], "ERROR")

    def test_transport_timeout_maps_to_timeout(self):
        for exc in (socket.timeout("t"), TimeoutError("t")):
            def transport(u, t, m, exc=exc):
                raise exc
            with self.subTest(exc=type(exc).__name__):
                self.assertEqual(run(http(transport))["status"], "TIMEOUT")

    def test_transport_exception_is_error_without_message_leak(self):
        def transport(u, t, m):
            raise ConnectionRefusedError("secret-detail")
        r = run(http(transport))
        self.assertEqual((r["status"], r["detail"]), ("ERROR", "ConnectionRefusedError"))

    def test_config_validation(self):
        bad = [
            dict(url="ftp://x.example.com/"),
            dict(url="https://user:pw@x.example.com/"),
            dict(url="https:///nohost"),
            dict(url="https://x.example.com/", timeout_s=0),
            dict(url="https://x.example.com/", timeout_s=10.01),
            dict(url="https://x.example.com/", timeout_s=True),
            dict(url="https://x.example.com/", max_bytes=0),
            dict(url="https://x.example.com/", max_bytes=65537),
            dict(url="https://x.example.com/", expect_status=[]),
        ]
        for kw in bad:
            with self.subTest(kw=kw):
                with self.assertRaises(ProbeConfigError):
                    HttpProbe("web", **kw)
        with self.assertRaises(ProbeConfigError):
            HttpProbe("bad name!", "https://x.example.com/")


class HardTimeoutTests(unittest.TestCase):
    def test_hung_transport_is_abandoned_as_timeout(self):
        release = threading.Event()
        self.addCleanup(release.set)

        def hang(url, timeout_s, max_bytes):
            release.wait(30)
            return 200, b"too late"

        r = run(http(hang, timeout_s=0.05))
        self.assertEqual(r["status"], "TIMEOUT")
        self.assertIn("hard timeout", r["detail"])


class TcpDnsTests(unittest.TestCase):
    def test_tcp(self):
        calls = []
        ok = TcpProbe("db", "db.example.internal", 5432, connect=lambda h, p, t: calls.append((h, p, t)))
        self.assertEqual(run(ok)["status"], "OK")
        self.assertEqual(calls, [("db.example.internal", 5432, 2.0)])

        def refuse(h, p, t):
            raise ConnectionRefusedError()
        self.assertEqual(run(TcpProbe("db", "db.example.internal", 5432, connect=refuse))["status"],
                         "ERROR")
        for port in (0, 65536, "22", True):
            with self.assertRaises(ProbeConfigError):
                TcpProbe("db", "h", port)

    def test_dns(self):
        self.assertEqual(run(DnsProbe("dns", "a.example.com", resolver=lambda n: ["192.0.2.1"]))["status"],
                         "OK")
        self.assertEqual(run(DnsProbe("dns", "a.example.com", resolver=lambda n: []))["status"], "FAIL")
        self.assertEqual(run(DnsProbe("dns", "a.example.com", min_answers=2,
                                      resolver=lambda n: ["192.0.2.1"]))["status"], "FAIL")
        self.assertEqual(run(DnsProbe("dns", "a.example.com", resolver=lambda n: None))["status"], "ERROR")

        def nx(n):
            raise socket.gaierror(-2, "Name or service not known")
        self.assertEqual(run(DnsProbe("dns", "a.example.com", resolver=nx))["status"], "ERROR")


class RunnerTests(unittest.TestCase):
    def test_unrecognised_status_becomes_unknown(self):
        p = TcpProbe("db", "h", 1, connect=lambda *a: None)
        p.check = lambda: ("GREEN", "?")
        self.assertEqual(run(p)["status"], "UNKNOWN")

    def test_max_probes_and_duplicates(self):
        mk = lambda i: TcpProbe("p%d" % i, "h", 1, connect=lambda *a: None)  # noqa: E731
        with self.assertRaises(ProbeConfigError):
            run_probes([mk(i) for i in range(MAX_PROBES + 1)], clock=CLOCK)
        with self.assertRaises(ProbeConfigError):
            run_probes([mk(1), mk(1)], clock=CLOCK)
        self.assertEqual(len(run_probes([mk(i) for i in range(MAX_PROBES)], clock=CLOCK,
                                        monotonic=StepMonotonic())), MAX_PROBES)

    def test_probe_from_config(self):
        p = probe_from_config({"name": "d", "kind": "dns", "hostname": "a.example.com"},
                              {"dns": lambda n: ["192.0.2.1"]})
        self.assertEqual(run(p)["status"], "OK")
        for cfg in ({"name": "x", "kind": "icmp"}, {"name": "x", "kind": "tcp", "host": "h", "port": 1,
                                                     "retries": 3}, "nope"):
            with self.assertRaises(ProbeConfigError):
                probe_from_config(cfg)

    def test_logs_probe_result(self):
        log = JsonLineLogger(None, clock=CLOCK)
        run(TcpProbe("db", "h", 1, connect=lambda *a: None), logger=log)
        self.assertEqual(log.records[0]["event"], "probe.result")
        self.assertEqual(log.records[0]["status"], "OK")


if __name__ == "__main__":
    unittest.main()
