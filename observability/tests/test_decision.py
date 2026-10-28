"""Fail-closed decision semantics on in-memory payloads."""

import copy
import json
import os
import unittest

from _support import FIXTURES, NOW
from healthcheck.decision import PolicyError, decide, make_policy, malformed_result
from healthcheck.payload import MalformedPayload, loads, validate
from healthcheck.timeutil import parse_ts

with open(os.path.join(FIXTURES, "healthy.json"), encoding="utf-8") as fh:
    HEALTHY = json.load(fh)


def evaluate(mutator=None, now=NOW, policy=None):
    doc = copy.deepcopy(HEALTHY)
    if mutator:
        mutator(doc)
    return decide(validate(doc), parse_ts(now), make_policy(policy))


def failed(result):
    return sorted(c["check"] for c in result["checks"] if c["status"] != "PASS")


class DecisionTests(unittest.TestCase):
    def test_baseline_healthy(self):
        r = evaluate()
        self.assertEqual((r["overall"], r["exit_code"]), ("HEALTHY", 0))

    def test_no_expected_probes_is_unhealthy(self):
        def m(d):
            d["expected_probes"] = []
            d["probes"] = []
        r = evaluate(m)
        self.assertEqual(r["overall"], "UNHEALTHY")
        self.assertIn("probes:expected_declared", failed(r))

    def test_unexpected_probe_result_is_unhealthy(self):
        r = evaluate(lambda d: d["expected_probes"].remove("db-tcp"))
        self.assertEqual(failed(r), ["probe:db-tcp"])

    def test_duplicate_probe_result_is_unhealthy(self):
        r = evaluate(lambda d: d["probes"].append(copy.deepcopy(d["probes"][0])))
        self.assertEqual(r["overall"], "UNHEALTHY")

    def test_duplicate_expected_name_is_unhealthy(self):
        r = evaluate(lambda d: d["expected_probes"].append("db-tcp"))
        self.assertIn("probes:expected_unique", failed(r))

    def test_every_non_ok_status_is_unhealthy(self):
        for status in ("FAIL", "TIMEOUT", "ERROR", "UNKNOWN"):
            with self.subTest(status=status):
                r = evaluate(lambda d: d["probes"][0].update(status=status))
                self.assertEqual((r["overall"], r["exit_code"]), ("UNHEALTHY", 1))

    def test_future_timestamp_is_unhealthy(self):
        r = evaluate(lambda d: d.update(collected_at="2026-10-28T12:30:00Z"))
        self.assertIn("freshness:payload", failed(r))

    def test_small_future_skew_tolerated(self):
        r = evaluate(lambda d: d.update(collected_at="2026-10-28T12:01:20Z"))
        self.assertEqual(r["overall"], "HEALTHY")

    def test_stale_boundary(self):
        self.assertEqual(evaluate(now="2026-10-28T12:05:00Z")["overall"], "HEALTHY")  # age 300
        self.assertEqual(evaluate(now="2026-10-28T12:05:01Z")["overall"], "UNHEALTHY")

    def test_probe_latency_over_policy(self):
        r = evaluate(lambda d: d["probes"][0].update(latency_ms=5000.1))
        self.assertEqual(failed(r), ["probe:app-http:latency"])

    def test_host_thresholds(self):
        cases = {
            "host:disk_free_ratio": lambda d: d["host"].update(disk_free_bytes=1),
            "host:load_per_cpu": lambda d: d["host"].update(load_avg_1m=9.0),
            "host:mem_available_ratio": lambda d: d["host"].update(mem_available_ratio=0.01),
        }
        for check, m in cases.items():
            with self.subTest(check=check):
                self.assertEqual(failed(evaluate(m)), [check])

    def test_inconsistent_host_figures(self):
        self.assertIn("host:disk_free_ratio",
                      failed(evaluate(lambda d: d["host"].update(disk_free_bytes=10**12))))
        self.assertIn("host:load_per_cpu", failed(evaluate(lambda d: d["host"].update(cpu_count=0))))
        self.assertIn("host:mem_available_ratio",
                      failed(evaluate(lambda d: d["host"].update(mem_available_ratio=1.5))))

    def test_every_null_host_metric_is_unhealthy(self):
        for k in ("load_avg_1m", "cpu_count", "disk_total_bytes", "disk_free_bytes",
                  "mem_available_ratio", "uptime_s"):
            with self.subTest(metric=k):
                r = evaluate(lambda d: d["host"].update({k: None}))
                self.assertIn("host:metrics_present", failed(r))

    def test_policy_override_and_rejection(self):
        r = evaluate(lambda d: d["host"].update(load_avg_1m=9.0), policy={"max_load_per_cpu": 3})
        self.assertEqual(r["overall"], "HEALTHY")
        with self.assertRaises(PolicyError):
            make_policy({"max_load": 1})
        with self.assertRaises(PolicyError):
            make_policy({"max_age_s": True})

    def test_malformed_result_shape(self):
        r = malformed_result(parse_ts(NOW), "boom")
        self.assertEqual((r["overall"], r["exit_code"], r["endpoint_decision"]["serve"]),
                         ("UNHEALTHY", 2, False))


class PayloadValidationTests(unittest.TestCase):
    def bad(self, mutator):
        doc = copy.deepcopy(HEALTHY)
        mutator(doc)
        with self.assertRaises(MalformedPayload):
            validate(doc)

    def test_rejections(self):
        self.bad(lambda d: d.pop("host"))
        self.bad(lambda d: d.update(schema="v0"))
        self.bad(lambda d: d.update(collected_at="2026-10-28 12:00:00"))
        self.bad(lambda d: d.update(extra=1))
        self.bad(lambda d: d["host"].update(cpu_count=True))
        self.bad(lambda d: d["probes"][0].update(kind="icmp"))
        self.bad(lambda d: d["probes"][0].update(latency_ms=-1))
        self.bad(lambda d: d.update(probes=[d["probes"][0]] * 17))
        self.bad(lambda d: d.update(expected_probes=["p%d" % i for i in range(17)]))
        self.bad(lambda d: d.update(expected_probes=[""]))

    def test_strict_json(self):
        for raw in (b'{"a":1,"a":2}', b'{"a": NaN}', b'{"a": Infinity}', b"\xff\xfe", b"{",
                    b"x" * (1_048_577)):
            with self.subTest(raw=raw[:20]):
                with self.assertRaises(MalformedPayload):
                    loads(raw)

    def test_non_object_payload(self):
        with self.assertRaises(MalformedPayload):
            validate([])


if __name__ == "__main__":
    unittest.main()
