"""Host collector, collect CLI end-to-end (fake transports), privacy and logging."""

import getpass
import json
import os
import tempfile
import unittest
from unittest import mock

from _support import CONFIG_EXAMPLE, FIXTURES, NOW, fake_readers, ok_transports, run_cli
from healthcheck.collector import HOST_METRICS, collect_host, read_meminfo_ratio, read_uptime
from healthcheck.jsonlog import JsonLineLogger
from healthcheck.timeutil import fixed_clock

CLOCK = fixed_clock(NOW)
SENTINEL = "OBS_PRIVACY_SENTINEL_7f3a"


def _dump(obj, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


class CollectorTests(unittest.TestCase):
    def test_snapshot_from_fake_readers(self):
        snap = collect_host(readers=fake_readers(), clock=CLOCK)
        self.assertEqual(snap, {"collected_at": NOW, "disk_path": "/", "errors": [],
                                "load_avg_1m": 0.5, "cpu_count": 4, "disk_total_bytes": 100000,
                                "disk_free_bytes": 60000, "mem_available_ratio": 0.5,
                                "uptime_s": 1234.5})

    def test_failing_or_missing_reader_yields_null_and_error(self):
        def boom():
            raise PermissionError("/proc/meminfo")
        readers = fake_readers(mem_available_ratio=boom)
        del readers["disk"]
        snap = collect_host(readers=readers, clock=CLOCK)
        self.assertIsNone(snap["mem_available_ratio"])
        self.assertIsNone(snap["disk_total_bytes"])
        self.assertEqual(snap["errors"], ["mem_available_ratio: PermissionError", "disk: reader missing"])

    def test_only_allowlisted_fields(self):
        snap = collect_host(readers=fake_readers(), clock=CLOCK)
        self.assertEqual(set(snap), {"collected_at", "disk_path", "errors"} | set(HOST_METRICS))

    def test_proc_parsers(self):
        meminfo = "MemTotal:  1000 kB\nMemFree: 100 kB\nMemAvailable:   250 kB\n"
        self.assertEqual(read_meminfo_ratio(lambda p: meminfo), 0.25)
        self.assertEqual(read_uptime(lambda p: "350735.47 234388.90\n"), 350735.5)
        with self.assertRaises(ValueError):
            read_meminfo_ratio(lambda p: "MemTotal: 0 kB\n")


class CollectCliTests(unittest.TestCase):
    def test_collect_healthy_end_to_end(self):
        code, result, logs, _ = run_cli(["collect", "--config", CONFIG_EXAMPLE],
                                        transports=ok_transports(), host_readers=fake_readers())
        self.assertEqual((code, result["overall"]), (0, "HEALTHY"), result["reasons"])
        events = [r["event"] for r in logs]
        self.assertEqual(events, ["config.loaded", "host.collected", "probe.result", "probe.result",
                                  "probe.result", "health.decision"])

    def test_collect_payload_out_matches_evaluate(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "payload.json")
            code, _, _, _ = run_cli(["collect", "--config", CONFIG_EXAMPLE, "--payload-out", p,
                                     "--out", os.path.join(d, "r.json")],
                                    transports=ok_transports(), host_readers=fake_readers())
            self.assertEqual(code, 0)
            code2, result2, _, _ = run_cli(["evaluate", p])
            self.assertEqual((code2, result2["overall"]), (0, "HEALTHY"))

    def test_collect_fail_closed_paths(self):
        t = ok_transports()
        cases = {
            "http 500": dict(transports={**t, "http": lambda u, s, m: (500, b"")}),
            "tcp timeout": dict(transports={**t, "tcp": self._raise(TimeoutError())}),
            "dns error": dict(transports={**t, "dns": self._raise(OSError())}),
            "host reader error": dict(transports=t,
                                      host_readers=fake_readers(cpu_count=self._raise(OSError()))),
        }
        for label, kw in cases.items():
            kw.setdefault("host_readers", fake_readers())
            with self.subTest(case=label):
                code, result, _, _ = run_cli(["collect", "--config", CONFIG_EXAMPLE], **kw)
                self.assertEqual((code, result["overall"]), (1, "UNHEALTHY"))

    def test_missing_probe_in_config_is_unhealthy(self):
        with tempfile.TemporaryDirectory() as d:
            with open(CONFIG_EXAMPLE, encoding="utf-8") as fh:
                cfg = json.load(fh)
            cfg["probes"] = cfg["probes"][:1]
            path = os.path.join(d, "c.json")
            _dump(cfg, path)
            code, result, _, _ = run_cli(["collect", "--config", path], transports=ok_transports(),
                                         host_readers=fake_readers())
            self.assertEqual(code, 1)
            self.assertTrue(any("missing" in r for r in result["reasons"]))

    def test_bad_config_exit_2(self):
        with tempfile.TemporaryDirectory() as d:
            for i, cfg in enumerate([{"probes": [{"name": "x", "kind": "http", "url": "ftp://a"}]},
                                     {"probes": [], "surprise": 1}, [],
                                     {"probes": [{"name": "p%d" % n, "kind": "dns", "hostname": "a.example"}
                                                 for n in range(17)]}]):
                path = os.path.join(d, "c%d.json" % i)
                _dump(cfg, path)
                with self.subTest(cfg=i):
                    code, result, _, _ = run_cli(["collect", "--config", path],
                                                 transports=ok_transports(), host_readers=fake_readers())
                    self.assertEqual((code, result["overall"]), (2, "UNHEALTHY"))

    def test_internal_error_fails_closed(self):
        code, result, logs, _ = run_cli(["collect", "--config", CONFIG_EXAMPLE],
                                        transports=ok_transports(), host_readers=["not", "a", "dict"])
        self.assertEqual((code, result["overall"]), (2, "UNHEALTHY"))
        self.assertEqual(logs[-1]["event"], "internal.error")

    @staticmethod
    def _raise(exc):
        def f(*a):
            raise exc
        return f


class CliEdgeTests(unittest.TestCase):
    def test_missing_payload_file(self):
        code, result, _, _ = run_cli(["evaluate", os.path.join(FIXTURES, "does-not-exist.json")])
        self.assertEqual((code, result["overall"]), (2, "UNHEALTHY"))

    def test_usage_error(self):
        self.assertEqual(run_cli(["frobnicate"])[0], 2)

    def test_policy_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "policy.json")
            json.dump({"min_disk_free_ratio": 0.01}, open(p, "w"))
            code, _, _, _ = run_cli(["evaluate", os.path.join(FIXTURES, "unhealthy.json"), "--policy", p])
            self.assertEqual(code, 1)  # probe still failing
            json.dump({"nope": 1}, open(p, "w"))
            code, result, _, _ = run_cli(["evaluate", os.path.join(FIXTURES, "healthy.json"), "--policy", p])
            self.assertEqual((code, result["overall"]), (2, "UNHEALTHY"))

    def test_host_command(self):
        code, _, _, out = run_cli(["host"], host_readers=fake_readers())
        self.assertEqual(code, 0)
        self.assertIn('"cpu_count": 4', out)
        self.assertEqual(run_cli(["host"], host_readers={})[0], 1)


class PrivacyTests(unittest.TestCase):
    def test_no_personal_data_in_output_or_logs(self):
        with mock.patch.dict(os.environ, {"OBS_TEST_VAR": SENTINEL}):
            _, _, _, text = run_cli(["collect", "--config", CONFIG_EXAMPLE],
                                    transports=ok_transports(), host_readers=fake_readers())
        self.assertNotIn(SENTINEL, text)
        try:
            user = getpass.getuser()
        except Exception:
            user = None
        if user and len(user) > 3:
            self.assertNotIn('"%s"' % user, text)
        home = os.path.expanduser("~")
        if home not in ("/", "~"):
            self.assertNotIn(home, text)
        for key in ('"user', '"env', '"argv', '"pid"', '"hostname"', '"home'):
            self.assertNotIn(key, text)

    def test_logger_refuses_sensitive_keys(self):
        log = JsonLineLogger(None, clock=CLOCK)
        for key in ("username", "env", "argv", "home", "hostname", "cmdline", "Password"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    log.info("x", **{key: "v"})

    def test_logger_shape_and_truncation(self):
        log = JsonLineLogger(None, clock=CLOCK)
        rec = log.info("evt", note="a" * 1000)
        self.assertEqual(rec["ts"], NOW)
        self.assertTrue(rec["note"].endswith("...[truncated]"))
        with self.assertRaises(TypeError):
            log.info("evt", obj={"nested": 1})
        with self.assertRaises(ValueError):
            log.log("TRACE", "evt")


if __name__ == "__main__":
    unittest.main()
