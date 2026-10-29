"""Offline unit tests for identity/m365/m365_ops.py (stdlib unittest, synthetic data only)."""
import copy
import glob
import io
import json
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
M365 = os.path.dirname(HERE)
sys.path.insert(0, M365)
sys.dont_write_bytecode = True
import m365_ops as m  # noqa: E402

TENANT = os.path.join(M365, "tenant", "tenant.json")
SCEN = os.path.join(M365, "scenarios")
FIX = os.path.join(HERE, "fixtures")


def load(name):
    with open(os.path.join(SCEN, name), encoding="utf-8") as fh:
        return json.load(fh)


def cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = m.main(list(argv) + ["--quiet"])
    return rc, out.getvalue() + err.getvalue()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = m.strict_load(TENANT)
        cls.idx = m.check_tenant(cls.t)

    def ev(self, scen):
        return m.evaluate(self.t, self.idx, m.check_scenario(scen, "test", self.idx))

    def codes(self, scen):
        return set(self.ev(scen)["findingCodes"])


class TestCorpus(Base):
    def test_all_scenarios_match_expectations(self):
        rc, out = cli()
        self.assertEqual(rc, 0, out)
        rep = m.run(TENANT, [SCEN])
        self.assertEqual(rep["totals"]["failed"], 0)
        self.assertGreaterEqual(rep["totals"]["scenarios"], 13)

    def test_every_scenario_type_covered(self):
        types = {load(os.path.basename(p))["type"] for p in glob.glob(os.path.join(SCEN, "*.json"))}
        self.assertEqual(types, set(m.SCENARIO_TYPES))

    def test_nothing_is_ever_executed(self):
        rep = m.run(TENANT, [SCEN])
        self.assertEqual(rep["mutationsExecuted"], 0)
        self.assertFalse(rep["tenantStateClaimed"])
        for r in rep["scenarios"]:
            for p in r["plan"]:
                self.assertEqual((p["mode"], p["executed"]), ("PLAN_ONLY", False))

    def test_engine_has_no_network_or_subprocess_imports(self):
        with open(os.path.join(M365, "m365_ops.py"), encoding="utf-8") as fh:
            src = fh.read()
        for mod in ("socket", "urllib", "http", "requests", "subprocess", "ssl", "msal", "azure"):
            self.assertIsNone(re.search(r"^\s*(import|from)\s+%s\b" % mod, src, re.M), mod)


class TestLicensing(Base):
    def test_f3_lacks_desktop_apps(self):
        self.assertIn("LIC-WORKLOAD-MISSING", self.codes(load("M365-ONB-002-teller-f3-desktop-apps.json")))

    def test_prereq_disabled_by_group(self):
        u = self.idx["users"]["0a110000-0000-4000-8000-000000000006"]
        f = m.license_findings(self.t, self.idx, u, ["intune"])
        self.assertEqual({x["code"] for x in f}, {"LIC-PREREQ", "LIC-WORKLOAD-MISSING"})
        self.assertTrue(any("GRP-LIC-E3-CONTRACTOR" in x["detail"] for x in f))

    def test_e3_staff_satisfies_all_standard_workloads(self):
        u = self.idx["users"]["0a110000-0000-4000-8000-000000000005"]
        self.assertEqual(m.license_findings(self.t, self.idx, u, ["mailbox", "teams", "onedrive", "desktop-apps", "intune"]), [])

    def test_no_seats_blocks(self):
        r = self.ev(load("M365-ONB-003-secops-e5-no-seats.json"))
        self.assertEqual(r["verdict"], "BLOCKED")
        self.assertIn("LIC-NO-SEATS", r["findingCodes"])

    def test_direct_license_without_usage_location_is_error(self):
        s = load("M365-ONB-002-teller-f3-desktop-apps.json")
        t = copy.deepcopy(self.t)
        u = next(x for x in t["users"] if x["id"] == s["input"]["userId"])
        u["directLicenses"] = [{"skuPartNumber": "LAB_M365_F3"}]
        idx = m.check_tenant(t)
        f, _ = m.eval_onboarding(t, idx, s, m.utc(t["asOfUtc"], "x"))
        self.assertIn(("LIC-USAGE-LOCATION", "error"), {(x["code"], x["severity"]) for x in f})


class TestDevices(Base):
    def dev(self, did):
        return copy.deepcopy(self.idx["devices"][did])

    def test_compliant_device(self):
        state, f = m.device_eval(self.t, self.dev("0d110000-0000-4000-8000-000000000001"), m.utc(self.t["asOfUtc"], "x"))
        self.assertEqual((state, f), ("compliant", []))

    def test_noncompliant_past_grace(self):
        state, f = m.device_eval(self.t, self.dev("0d110000-0000-4000-8000-000000000006"), m.utc(self.t["asOfUtc"], "x"))
        self.assertEqual(state, "noncompliant")
        self.assertEqual({x["code"] for x in f}, {"DEV-OS-MIN", "DEV-BITLOCKER"})

    def test_within_grace_period(self):
        d = self.dev("0d110000-0000-4000-8000-000000000006")
        d["firstNoncompliantUtc"] = "2026-10-28T10:00:00Z"
        state, f = m.device_eval(self.t, d, m.utc(self.t["asOfUtc"], "x"))
        self.assertEqual(state, "inGracePeriod")
        self.assertIn("DEV-IN-GRACE", {x["code"] for x in f})

    def test_missing_fact_fails_closed(self):
        d = self.dev("0d110000-0000-4000-8000-000000000001")
        del d["bitLocker"]
        state, f = m.device_eval(self.t, d, m.utc(self.t["asOfUtc"], "x"))
        self.assertEqual(state, "noncompliant")
        self.assertIn("DEV-BITLOCKER", {x["code"] for x in f})

    def test_stale_checkin_and_unmanaged(self):
        asof = m.utc(self.t["asOfUtc"], "x")
        self.assertIn("DEV-STALE-CHECKIN", {x["code"] for x in m.device_eval(self.t, self.dev("0d110000-0000-4000-8000-00000000000c"), asof)[1]})
        self.assertEqual(m.device_eval(self.t, self.dev("0d110000-0000-4000-8000-000000000007"), asof)[0], "unmanaged")


class TestOffboarding(Base):
    def test_good_runbook_approved(self):
        self.assertEqual(self.ev(load("M365-OFF-001-involuntary-lender-legal-hold.json"))["verdict"], "APPROVED")

    def test_involuntary_must_disable_first(self):
        s = load("M365-OFF-001-involuntary-lender-legal-hold.json")
        rb = s["input"]["runbook"]
        s["input"]["runbook"] = [rb[3]] + rb[:3] + rb[4:]
        self.assertIn("OFF-INVOLUNTARY-ORDER", self.codes(s))

    def test_synced_user_cloud_disable(self):
        s = load("M365-OFF-001-involuntary-lender-legal-hold.json")
        s["input"]["runbook"][0] = {"step": "DISABLE_SIGNIN"}
        c = self.codes(s)
        self.assertIn("OFF-SYNCED-SOURCE", c)
        self.assertIn("OFF-MISSING-STEP", c)

    def test_corporate_retire_warns(self):
        s = load("M365-OFF-001-involuntary-lender-legal-hold.json")
        s["input"]["runbook"][6]["step"] = "RETIRE_DEVICE"
        r = self.ev(s)
        self.assertIn("OFF-CORP-RETIRE", r["findingCodes"])
        self.assertEqual(r["verdict"], "APPROVED_WITH_WARNINGS")

    def test_break_glass_cannot_be_offboarded_by_runbook(self):
        s = load("M365-OFF-002-voluntary-leaver-bad-runbook.json")
        s["input"]["userId"] = "b9a5e000-0000-4000-8000-000000000001"
        s["input"]["runbook"] = [x for x in s["input"]["runbook"] if x["step"] not in m.DEVICE_STEPS]
        self.assertIn("OFF-BREAK-GLASS", self.codes(s))

    def test_missing_evidence_and_approval(self):
        s = load("M365-OFF-001-involuntary-lender-legal-hold.json")
        s["auditEvidence"] = s["auditEvidence"][:2]
        del s["input"]["approvalRef"]
        r = self.ev(s)
        self.assertTrue({"AUD-MISSING", "AUD-NO-APPROVAL"} <= set(r["findingCodes"]))
        self.assertEqual(r["verdict"], "REJECTED")


class TestAccessAndServiceHealth(Base):
    def test_signin_code_map_is_closed(self):
        s = load("M365-ACC-004-treasury-mfa-registration.json")
        s["input"]["signIns"][0]["errorCode"] = 12345
        with self.assertRaises(m.Malformed):
            self.ev(s)

    def test_each_mapped_code_yields_root_cause(self):
        for code, spec in m.SIGNIN_ERRORS.items():
            if not code or code == 53000:
                continue
            s = load("M365-ACC-004-treasury-mfa-registration.json")
            s["input"]["signIns"][0]["errorCode"] = code
            r = self.ev(s)
            self.assertIn(spec[0], r["findingCodes"])
            self.assertEqual(r["verdict"], "ROOT_CAUSE_IDENTIFIED")

    def test_no_incident_many_reports_escalates(self):
        s = load("M365-SH-001-teams-known-incident.json")
        for r in s["input"]["reports"]:
            r["reportedUtc"] = "2026-10-28T12:00:00Z"
        r = self.ev(s)
        self.assertEqual(r["verdict"], "ESCALATE_TO_MICROSOFT")


class TestBreakGlass(Base):
    def test_ca_exclusion_removed(self):
        t = copy.deepcopy(self.t)
        t["conditionalAccess"]["policies"][3]["excludeUsers"] = t["conditionalAccess"]["policies"][3]["excludeUsers"][:1]
        f, _ = m.eval_bg_review(t, m.check_tenant(t), {}, m.utc(t["asOfUtc"], "x"))
        self.assertIn("BG-CA-NOT-EXCLUDED", {x["code"] for x in f})

    def test_synced_federated_no_fido(self):
        t = copy.deepcopy(self.t)
        u = next(x for x in t["users"] if x["id"] == "b9a5e000-0000-4000-8000-000000000002")
        u.update(onPremisesSynced=True, upn="bg.bravo@nwlab-bank.example", mfaMethods=["sms"], roles=[{"role": "Global Administrator", "assignment": "eligible"}])
        t["breakGlass"]["alertRules"][0]["enabled"] = False
        f, _ = m.eval_bg_review(t, m.check_tenant(t), {}, m.utc(t["asOfUtc"], "x"))
        self.assertTrue({"BG-SYNCED", "BG-DOMAIN", "BG-METHOD", "BG-ROLE", "BG-ALERT"} <= {x["code"] for x in f})

    def test_usage_without_rotation_or_ticket(self):
        s = load("M365-BG-002-usage-during-mfa-outage.json")
        s["input"]["credentialRotatedUtc"] = "2026-09-16T09:40:00Z"
        del s["input"]["incidentRef"]
        r = self.ev(s)
        self.assertEqual(r["verdict"], "POST_USE_INCOMPLETE")
        self.assertTrue({"BG-USE-ROTATION-LATE", "BG-USE-NO-TICKET"} <= set(r["findingCodes"]))


class TestFailClosed(Base):
    def test_fixtures_exit_codes(self):
        names = sorted(os.listdir(FIX))
        self.assertTrue(names)
        for n in names:
            want = 2 if n.startswith("malformed-") else 1 if n.startswith("mismatch-") else None
            self.assertIsNotNone(want, n)
            rc, out = cli(os.path.join(FIX, n))
            self.assertEqual(rc, want, "%s: %s" % (n, out))

    def test_non_synthetic_tenant_rejected(self):
        t = copy.deepcopy(self.t)
        t["synthetic"] = False
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(t, fh)
        try:
            rc, out = cli("--tenant", fh.name)
            self.assertEqual(rc, 2)
            self.assertIn("SYN-000", out)
        finally:
            os.unlink(fh.name)

    def test_malformed_json_out_records_error(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.json")
            rc, _ = cli(os.path.join(FIX, "malformed-execute-flag.json"), "--json-out", p)
            self.assertEqual(rc, 2)
            with open(p, encoding="utf-8") as fh:
                rep = json.load(fh)
            self.assertEqual((rep["exitCode"], rep["error"]["rule"]), (2, "SAFE-001"))


if __name__ == "__main__":
    unittest.main()
