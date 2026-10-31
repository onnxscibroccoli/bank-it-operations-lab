"""Every fixture under observability/fixtures evaluates to its recorded expectation."""

import json
import os
import unittest

from _support import FIXTURES, run_cli

with open(os.path.join(FIXTURES, "EXPECTED.json"), encoding="utf-8") as fh:
    EXPECTED = json.load(fh)


class FixtureTests(unittest.TestCase):
    def test_every_fixture_has_expectation(self):
        files = {f for f in os.listdir(FIXTURES) if f.endswith(".json") and f != "EXPECTED.json"}
        self.assertEqual(files, set(EXPECTED["cases"]))

    def test_required_scenarios_present(self):
        names = set(EXPECTED["cases"])
        for required in ("healthy.json", "unhealthy.json", "timeout.json", "stale.json"):
            self.assertIn(required, names)
        self.assertTrue(any(n.startswith("malformed-") for n in names))

    def test_only_healthy_fixture_is_healthy(self):
        healthy = [n for n, c in EXPECTED["cases"].items() if c["overall"] == "HEALTHY"]
        self.assertEqual(healthy, ["healthy.json"])

    def _check(self, name):
        exp = EXPECTED["cases"][name]
        code, result, logs, _ = run_cli(["evaluate", os.path.join(FIXTURES, name)],
                                        clock_ts=EXPECTED["now"])
        self.assertEqual(code, exp["exit"], name)
        self.assertEqual(result["exit_code"], exp["exit"])
        self.assertEqual(result["overall"], exp["overall"])
        failed = sorted(c["check"] for c in result["checks"] if c["status"] != "PASS")
        self.assertEqual(failed, sorted(exp["failed_checks"]), name)
        healthy = exp["overall"] == "HEALTHY"
        self.assertEqual(result["endpoint_decision"], {"serve": healthy,
                                                       "http_status": 200 if healthy else 503})
        self.assertEqual(result["evaluated_at"], EXPECTED["now"])
        self.assertEqual(logs[-1]["event"], "health.decision")
        self.assertEqual(logs[-1]["overall"], exp["overall"])
        return result

    def test_healthy(self):
        r = self._check("healthy.json")
        self.assertEqual(r["reasons"], [])

    def test_unhealthy(self):
        self._check("unhealthy.json")

    def test_timeout(self):
        r = self._check("timeout.json")
        self.assertTrue(any("TIMEOUT" in x for x in r["reasons"]))

    def test_stale(self):
        r = self._check("stale.json")
        self.assertTrue(all("stale" in x for x in r["reasons"]))

    def test_stale_fixture_is_fresh_if_clock_matches(self):
        code, result, _, _ = run_cli(["evaluate", os.path.join(FIXTURES, "stale.json")],
                                     clock_ts="2026-10-28T11:01:00Z")
        self.assertEqual((code, result["overall"]), (0, "HEALTHY"))

    def test_missing_probe(self):
        r = self._check("missing-probe.json")
        self.assertIn("missing", r["reasons"][0])

    def test_unknown_status(self):
        self._check("unknown-status.json")

    def test_host_metric_missing(self):
        self._check("host-metric-missing.json")

    def test_malformed_payloads(self):
        for name in sorted(EXPECTED["cases"]):
            if name.startswith("malformed-"):
                with self.subTest(name=name):
                    r = self._check(name)
                    self.assertEqual(r["exit_code"], 2)
                    self.assertEqual(r["endpoint_decision"]["http_status"], 503)

    def test_deterministic_output(self):
        a = run_cli(["evaluate", os.path.join(FIXTURES, "unhealthy.json")])
        b = run_cli(["evaluate", os.path.join(FIXTURES, "unhealthy.json")])
        self.assertEqual(a[3], b[3])


if __name__ == "__main__":
    unittest.main()
