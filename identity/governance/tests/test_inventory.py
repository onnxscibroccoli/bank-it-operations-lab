"""inventory.py against synthetic Graph fixture scenarios (offline, mocked transport only)."""
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import _common
import inventory as inv

SCEN = _common.SCEN
GA = "62e90394-69f5-4237-9190-012177145e10"
BG1 = "b9a5e000-0000-4000-8000-000000000001"


def run(name, **kw):
    return inv.run(os.path.join(SCEN, name), **kw)


def rules(rep):
    return sorted({f["rule"] for f in rep["findings"]})


EXPECTED_EXIT = {"baseline": 0, "findings": 1, "missing-fields": 1, "auth-401": 2, "auth-403": 2,
                 "throttled-recover": 0, "throttled-exhausted": 2, "paging-loop": 2, "malformed-page": 2,
                 "free-tier": 0}


class TestScenarioExitCodes(unittest.TestCase):
    def test_every_scenario_is_covered(self):
        self.assertEqual(sorted(os.listdir(SCEN)), sorted(EXPECTED_EXIT))

    def test_expected_exit_codes(self):
        for name, code in EXPECTED_EXIT.items():
            with self.subTest(scenario=name):
                rep = run(name)
                self.assertEqual(rep["exitCode"], code, json.dumps(rep.get("error") or rep.get("findings"), indent=1))
                self.assertTrue(rep["offline"])
                self.assertFalse(rep["tenantStateClaimed"])


class TestBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = run("baseline")

    def test_pass_without_findings(self):
        self.assertEqual(self.rep["overall"], "PASS")
        self.assertEqual(self.rep["findings"], [])

    def test_pagination_collected_every_page(self):
        # active 8 items / 5 per page = 2 pages, eligible 8 / 3 = 3 pages, users 9 / 5 = 2 pages,
        # roleDefinitions, servicePrincipals, groups = 1 page each -> 10 pages, 10 requests, 0 retries.
        g = self.rep["graph"]
        self.assertEqual((g["pages"], g["requests"], g["retries"]), (10, 10, []))
        self.assertEqual(self.rep["summary"]["inventoryRows"], 16)
        self.assertEqual(sum(r["state"] == "eligible" for r in self.rep["inventory"]), 8)

    def test_break_glass_permanent_ga_is_allowed(self):
        bg = [r for r in self.rep["inventory"] if r["breakGlass"]]
        self.assertEqual(len(bg), 2)
        self.assertTrue(all(r["permanent"] and r["roleTemplateId"] == GA and r["state"] == "active" for r in bg))

    def test_non_privileged_roles_not_counted_as_privileged(self):
        names = {r["roleDisplayName"] for r in self.rep["inventory"] if not r["privileged"]}
        self.assertEqual(names, {"Global Reader", "Directory Readers"})

    def test_group_assignment_resolved(self):
        g = [r for r in self.rep["inventory"] if r["principalType"] == "group"]
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["roleDisplayName"], "Security Administrator")

    def test_tier_zero_sorted_first(self):
        self.assertTrue(self.rep["inventory"][0]["tierZero"])


class TestFindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = run("findings")

    def test_rules_fired(self):
        self.assertEqual(rules(self.rep), ["INV-001", "INV-002", "INV-003", "INV-004", "INV-005", "INV-006",
                                           "INV-007", "INV-008", "INV-009"])

    def test_expired_assignments_excluded_from_inventory(self):
        ids = {r["recordId"] for r in self.rep["inventory"]}
        expired = [f["recordId"] for f in self.rep["findings"] if f["rule"] == "INV-003"]
        self.assertEqual(len(expired), 2)
        self.assertTrue(ids.isdisjoint(expired))

    def test_global_admin_count(self):
        f = [f for f in self.rep["findings"] if f["rule"] == "INV-002"]
        self.assertEqual(f[0]["detail"], "5 active principals > 4")

    def test_missing_break_glass_reported(self):
        f = [f for f in self.rep["findings"] if f["rule"] == "INV-007"]
        self.assertEqual([x["subject"] for x in f], ["b9a5e000-0000-4000-8000-000000000002"])

    def test_findings_sorted_by_severity(self):
        order = [inv.SEVERITY_ORDER[f["severity"]] for f in self.rep["findings"]]
        self.assertEqual(order, sorted(order))


class TestMissingFields(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = run("missing-fields")

    def test_does_not_crash_and_reports_data_quality(self):
        self.assertEqual(self.rep["overall"], "FINDINGS")
        dq = [f for f in self.rep["findings"] if f["rule"].startswith("DQ-")]
        self.assertEqual(sorted({f["rule"] for f in dq}), ["DQ-001", "DQ-002", "DQ-003"])
        missing = sorted(f["detail"] for f in dq if f["rule"] == "DQ-001")
        self.assertEqual(missing, ["active record missing id", "active record missing principalId",
                                   "active record missing roleDefinitionId"])

    def test_records_missing_required_fields_are_skipped(self):
        ids = {r["recordId"] for r in self.rep["inventory"]}
        self.assertNotIn("rasi-b9a5e000-0000-4000-8000-000000000221", ids)
        self.assertNotIn("rasi-b9a5e000-0000-4000-8000-000000000222", ids)

    def test_unknown_role_treated_as_privileged(self):
        r = [r for r in self.rep["inventory"] if r["roleDisplayName"] == "UNKNOWN"]
        self.assertEqual(len(r), 1)
        self.assertTrue(r[0]["privileged"])

    def test_missing_optional_user_fields(self):
        devon = [r for r in self.rep["inventory"] if r["principalId"].endswith("000000000013")]
        self.assertEqual(devon[0]["userType"], "Unknown")
        self.assertIsNone(devon[0]["startDateTime"])

    def test_bad_timestamp_treated_conservatively_as_permanent(self):
        r = [r for r in self.rep["inventory"] if r["recordId"] == "rasi-b9a5e000-0000-4000-8000-000000000225"][0]
        self.assertTrue(r["permanent"])
        self.assertIn("INV-001", {f["rule"] for f in self.rep["findings"] if f["recordId"] == r["recordId"]})


class TestExpiry(unittest.TestCase):
    def test_activation_expires_when_clock_moves(self):
        rep = run("baseline", as_of="2026-10-28T13:00:00Z")  # Avery's GA activation ends exactly now
        exp = [f for f in rep["findings"] if f["rule"] == "INV-003"]
        self.assertEqual([f["recordId"] for f in exp], ["rasi-b9a5e000-0000-4000-8000-000000000203"])
        self.assertEqual(rep["exitCode"], 1)

    def test_future_dated_schedule_not_effective(self):
        rep = run("baseline", as_of="2026-01-01T00:00:00Z")
        self.assertFalse(any(r["state"] == "eligible" for r in rep["inventory"]))
        self.assertEqual(rules(rep), ["INV-007"])  # break-glass GA starts 2026-01-05

    def test_everything_expired(self):
        rep = run("baseline", as_of="2030-01-01T00:00:00Z")
        self.assertIn("INV-003", rules(rep))
        self.assertTrue(all(r["permanent"] for r in rep["inventory"]))

    def test_naive_as_of_rejected(self):
        rep = run("baseline", as_of="2026-10-28T12:00:00")
        self.assertEqual((rep["exitCode"], rep["error"]["kind"]), (2, "input"))


class TestFailClosed(unittest.TestCase):
    def test_401(self):
        rep = run("auth-401")
        self.assertEqual(rep["error"]["kind"], "authorization")
        self.assertEqual(rep["error"]["status"], 401)
        self.assertEqual(rep["inventory"], [])
        self.assertEqual(rep["graph"]["requests"], 1)
        self.assertEqual(rep["graph"]["retries"], [])

    def test_403(self):
        rep = run("auth-403")
        self.assertEqual((rep["error"]["status"], rep["error"]["code"]), (403, "Authorization_RequestDenied"))
        self.assertEqual(rep["inventory"], [])
        self.assertEqual(rep["graph"]["retries"], [])

    def test_throttled_recover_waits_retry_after(self):
        slept = []
        rep = run("throttled-recover", sleep=slept.append)
        self.assertEqual(rep["exitCode"], 0)
        self.assertEqual(slept, [1, 3, 1])  # users 503 (no header, backoff 1s), then active 429 x2
        self.assertEqual([r["status"] for r in rep["graph"]["retries"]], [503, 429, 429])
        self.assertEqual(rep["summary"]["inventoryRows"], run("baseline")["summary"]["inventoryRows"])

    def test_throttled_exhausted(self):
        slept = []
        rep = run("throttled-exhausted", sleep=slept.append)
        self.assertEqual(rep["error"]["kind"], "throttled")
        self.assertEqual(slept, [5, 5, 5, 5])

    def test_paging_loop_and_malformed(self):
        self.assertEqual(run("paging-loop")["error"]["message"], "@odata.nextLink loop")
        self.assertIn("value", run("malformed-page")["error"]["message"])

    def test_missing_scenario_dir(self):
        rep = inv.run(os.path.join(SCEN, "does-not-exist"))
        self.assertEqual((rep["exitCode"], rep["error"]["kind"]), (2, "input"))


class TestFreeTier(unittest.TestCase):
    def test_free_mode_uses_role_assignments_only(self):
        rep = run("free-tier")
        self.assertEqual(rep["mode"], "free")
        self.assertEqual(rules(rep), ["INV-010"])
        self.assertTrue(all(r["permanent"] is None for r in rep["inventory"]))
        self.assertEqual(rep["summary"]["inventoryRows"], 7)

    def test_pim_mode_on_free_tier_fails_closed_403(self):
        rep = run("free-tier", mode="pim")
        self.assertEqual(rep["error"]["status"], 403)


class TestBuildUnit(unittest.TestCase):
    def setUp(self):
        self.base = inv.load_baseline(inv.BASELINE)
        self.now = inv.parse_ts("2026-10-28T12:00:00Z")

    def data(self, **kw):
        d = {"roleDefinitions": [{"id": GA, "templateId": GA, "displayName": "Global Administrator"}],
             "users": [{"id": BG1, "displayName": "bg1", "userType": "Member", "accountEnabled": True}],
             "servicePrincipals": [], "groups": [], "active": [], "eligible": []}
        d.update(kw)
        return d

    def test_non_object_record(self):
        rows, f = inv.build(self.data(active=["oops"]), self.base, self.now, "pim")
        self.assertIn("DQ-001", {x["rule"] for x in f})

    def test_ga_count_threshold_boundary(self):
        users = [{"id": "u%d" % i, "userType": "Member"} for i in range(4)]
        act = [{"id": "a%d" % i, "principalId": "u%d" % i, "roleDefinitionId": GA, "assignmentType": "Activated",
                "startDateTime": "2026-10-28T11:00:00Z", "endDateTime": "2026-10-28T13:00:00Z"} for i in range(4)]
        _, f = inv.build(self.data(users=users, active=act), self.base, self.now, "pim")
        self.assertNotIn("INV-002", {x["rule"] for x in f})
        users.append({"id": "u4", "userType": "Member"})
        act.append(dict(act[0], id="a4", principalId="u4"))
        _, f = inv.build(self.data(users=users, active=act), self.base, self.now, "pim")
        self.assertIn("INV-002", {x["rule"] for x in f})


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(_common.GOV, "inventory.py")] + list(args),
                              capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))

    def test_outputs_and_exit_codes(self):
        j, m, c = (os.path.join(self.tmp, n) for n in ("r.json", "r.md", "r.csv"))
        r = self.cli("--scenario", "findings", "--json-out", j, "--md-out", m, "--csv-out", c, "--quiet")
        self.assertEqual(r.returncode, 1, r.stderr)
        with open(j) as fh:
            rep = json.load(fh)
        self.assertEqual(rep["schema"], inv.SCHEMA)
        with open(m) as fh:
            md = fh.read()
        self.assertIn("OFFLINE / SYNTHETIC", md)
        self.assertIn("INV-007", md)
        with open(c) as fh:
            rows = list(csv.DictReader(io.StringIO(fh.read())))
        self.assertEqual(len(rows), sum(x["privileged"] for x in rep["inventory"]))
        self.assertEqual(self.cli("--scenario", "baseline", "--quiet").returncode, 0)
        r = self.cli("--scenario", "auth-403", "--quiet")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Authorization_RequestDenied", r.stderr)

    def test_error_markdown(self):
        md = inv.render_markdown(run("auth-401"))
        self.assertIn("fail-closed", md)


if __name__ == "__main__":
    unittest.main()
