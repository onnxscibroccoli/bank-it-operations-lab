"""Tests for identity/entra/ca_validator.py (offline, synthetic fixtures only).

Run:  python3 -m unittest discover -s tests/entra -v
"""
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENTRA = os.path.join(ROOT, "identity", "entra")
sys.path.insert(0, ENTRA)
sys.path.insert(0, HERE)

import ca_validator as v  # noqa: E402
import make_fixtures  # noqa: E402

POLICIES = os.path.join(ENTRA, "policies")
BASELINE = os.path.join(ENTRA, "baseline.json")
FIX = os.path.join(HERE, "fixtures")
VALIDATOR = os.path.join(ENTRA, "ca_validator.py")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def run(path, baseline=BASELINE):
    return v.validate(path, baseline)


def statuses(report):
    return {r["id"]: r["status"] for r in report["rules"]}


def failing(report):
    return {r["id"] for r in report["rules"] if r["status"] == "FAIL"}


class TestValidPolicySet(unittest.TestCase):
    def test_baseline_policy_directory_passes(self):
        rep = run(POLICIES)
        self.assertEqual(rep["overall"], "PASS", json.dumps(rep, indent=1))
        self.assertEqual(rep["exitCode"], v.EXIT_PASS)
        self.assertEqual(set(statuses(rep).values()), {"PASS"})
        self.assertEqual(rep["input"]["policyCount"], 7)

    def test_graph_envelope_passes(self):
        rep = run(os.path.join(FIX, "valid-graph-envelope.json"))
        self.assertEqual(rep["overall"], "PASS")

    def test_every_rule_is_reported(self):
        rep = run(POLICIES)
        self.assertEqual([r["id"] for r in rep["rules"]], [r[0] for r in v.RULES])

    def test_report_is_labelled_offline_and_claims_no_tenant_state(self):
        rep = run(POLICIES)
        self.assertEqual(rep["mode"], "offline-synthetic")
        self.assertIs(rep["tenantStateClaimed"], False)
        self.assertIn("OFFLINE", rep["disclaimer"])
        self.assertIn("NO claim", rep["disclaimer"])
        self.assertIn("OFFLINE", v.render_markdown(rep))

    def test_fixtures_cover_policies_conditions_and_grant_controls(self):
        loaded, errs = v.load_policy_set(POLICIES)
        self.assertEqual(errs, [])
        controls, cond_keys, states = set(), set(), set()
        for _, p in loaded:
            controls |= set(p["grantControls"]["builtInControls"])
            if p["grantControls"].get("authenticationStrength"):
                controls.add("authenticationStrength")
            cond_keys |= {k for k, val in p["conditions"].items() if val}
            states.add(p["state"])
        self.assertTrue({"block", "mfa", "compliantDevice", "authenticationStrength", "passwordChange"} <= controls)
        self.assertTrue({"users", "applications", "clientAppTypes", "platforms", "locations",
                         "signInRiskLevels", "userRiskLevels"} <= cond_keys)
        self.assertTrue({"enabled", "enabledForReportingButNotEnforced"} <= states)


# fixture -> rule ids that must FAIL (others may also fail, these must be among them)
BASELINE_NEGATIVES = {
    "neg-missing-mfa.json": {"BASE-003"},
    "neg-mfa-policy-removed.json": {"BASE-003"},
    "neg-mfa-or-bypass.json": {"BASE-003"},
    "neg-mfa-report-only.json": {"BASE-003"},
    "neg-mfa-extra-exclusion.json": {"BASE-003"},
    "neg-missing-compliant-device.json": {"BASE-006"},
    "neg-device-or-bypass.json": {"BASE-006"},
    "neg-device-disabled.json": {"BASE-006"},
    "neg-break-glass-not-excluded.json": {"BASE-001"},
    "neg-break-glass-included.json": {"BASE-001"},
    "neg-unscoped-block.json": {"BASE-005", "BASE-001"},
    "neg-legacy-auth-not-blocked.json": {"BASE-002"},
    "neg-legacy-auth-partial.json": {"BASE-002"},
    "neg-admin-weak-strength.json": {"BASE-004"},
    "neg-admin-role-missing.json": {"BASE-004"},
    "neg-admin-role-excluded.json": {"BASE-004"},
    "neg-risk-enforced.json": {"BASE-007"},
}

MALFORMED = {
    "malformed-truncated.json": "SCHEMA-001",
    "malformed-nan.json": "SCHEMA-001",
    "malformed-duplicate-key.json": "SCHEMA-001",
    "malformed-empty-set.json": "SCHEMA-001",
    "malformed-not-object.json": "SCHEMA-002",
    "malformed-unknown-top-key.json": "SCHEMA-002",
    "malformed-missing-state.json": "SCHEMA-002",
    "malformed-invalid-state.json": "SCHEMA-003",
    "malformed-unknown-condition.json": "SCHEMA-004",
    "malformed-wrong-type.json": "SCHEMA-004",
    "malformed-bad-guid.json": "SCHEMA-004",
    "malformed-unknown-client-app.json": "SCHEMA-004",
    "malformed-bad-risk-level.json": "SCHEMA-004",
    "malformed-no-users-target.json": "SCHEMA-004",
    "malformed-unknown-control.json": "SCHEMA-005",
    "malformed-bad-operator.json": "SCHEMA-005",
    "malformed-block-combined.json": "SCHEMA-005",
    "malformed-empty-grant.json": "SCHEMA-005",
    "malformed-duplicate-id.json": "SCHEMA-006",
}


class TestBaselineNegatives(unittest.TestCase):
    def test_each_negative_fixture_fails_expected_rule(self):
        for name, expected in BASELINE_NEGATIVES.items():
            with self.subTest(fixture=name):
                rep = run(os.path.join(FIX, name))
                self.assertEqual(rep["overall"], "FAIL")
                self.assertEqual(rep["exitCode"], v.EXIT_BASELINE_FAIL)
                self.assertTrue(expected <= failing(rep), "%s: expected %s, got %s" % (name, expected, failing(rep)))
                # schema must still pass: these are well-formed, policy-level violations
                self.assertFalse({r for r in failing(rep) if r.startswith("SCHEMA")})

    def test_missing_mfa_is_reported_with_reason(self):
        rep = run(os.path.join(FIX, "neg-missing-mfa.json"))
        msgs = [m for r in rep["rules"] if r["id"] == "BASE-003" for m in r["findings"]]
        self.assertTrue(any("requires MFA" in m for m in msgs), msgs)

    def test_non_compliant_device_path_fails(self):
        # compliantDevice OR mfa means a non-compliant device can satisfy the grant with MFA alone
        rep = run(os.path.join(FIX, "neg-device-or-bypass.json"))
        msgs = [m for r in rep["rules"] if r["id"] == "BASE-006" for m in r["findings"]]
        self.assertTrue(any("operator OR" in m for m in msgs), msgs)
        self.assertEqual(statuses(rep)["BASE-006"], "FAIL")

    def test_missing_compliant_device_grant_fails(self):
        rep = run(os.path.join(FIX, "neg-missing-compliant-device.json"))
        self.assertEqual(failing(rep), {"BASE-006"})


class TestFailClosed(unittest.TestCase):
    def test_each_malformed_fixture_fails_closed(self):
        for name, rule in MALFORMED.items():
            with self.subTest(fixture=name):
                rep = run(os.path.join(FIX, name))
                self.assertEqual(rep["overall"], "FAIL")
                self.assertEqual(rep["exitCode"], v.EXIT_MALFORMED)
                self.assertIn(rule, failing(rep), "%s: %s" % (name, failing(rep)))
                base = {r["id"]: r["status"] for r in rep["rules"] if r["category"] == "baseline"}
                self.assertEqual(set(base.values()), {"NOT_EVALUATED"}, base)

    def test_missing_path_fails_closed(self):
        rep = run(os.path.join(FIX, "does-not-exist.json"))
        self.assertEqual(rep["exitCode"], v.EXIT_MALFORMED)

    def test_empty_directory_fails_closed(self):
        d = tempfile.mkdtemp()
        try:
            self.assertEqual(run(d)["exitCode"], v.EXIT_MALFORMED)
        finally:
            shutil.rmtree(d)

    def test_stray_non_json_file_in_policy_dir_fails_closed(self):
        d = tempfile.mkdtemp()
        try:
            for f in os.listdir(POLICIES):
                shutil.copy(os.path.join(POLICIES, f), d)
            _write(os.path.join(d, "CA999.yaml"), "state: enabled\n")
            self.assertEqual(run(d)["exitCode"], v.EXIT_MALFORMED)
        finally:
            shutil.rmtree(d)

    def test_malformed_baseline_fails_closed(self):
        d = tempfile.mkdtemp()
        try:
            b = json.loads(_read(BASELINE))
            cases = {
                "no-break-glass": dict(b, breakGlass={"userIds": [], "groupIds": []}),
                "unknown-key": dict(b, allowEverything=True),
                "bad-guid": dict(b, breakGlass={"userIds": ["bg@bank.example"], "groupIds": []}),
            }
            for name, doc in cases.items():
                with self.subTest(case=name):
                    p = os.path.join(d, name + ".json")
                    _write(p, json.dumps(doc))
                    rep = run(POLICIES, p)
                    self.assertEqual(rep["exitCode"], v.EXIT_MALFORMED)
                    self.assertEqual(statuses(rep)["SCHEMA-001"], "FAIL")
        finally:
            shutil.rmtree(d)

    def test_unexpected_types_never_crash(self):
        for doc in (None, 0, "x", [], [None], {"value": "x"}, {"value": [1]},
                    {"displayName": "x", "state": "enabled", "conditions": [], "grantControls": []}):
            with self.subTest(doc=doc):
                d = tempfile.mkdtemp()
                try:
                    p = os.path.join(d, "p.json")
                    _write(p, json.dumps(doc))
                    rep = run(p)
                    self.assertEqual(rep["overall"], "FAIL")
                    self.assertEqual(rep["exitCode"], v.EXIT_MALFORMED)
                finally:
                    shutil.rmtree(d)


class TestRuleUnits(unittest.TestCase):
    def setUp(self):
        self.baseline = v.load_baseline(BASELINE)
        self.policies = [p for _, p in v.load_policy_set(POLICIES)[0]]

    def p(self, prefix):
        return next(p for p in self.policies if p["displayName"].startswith(prefix))

    def test_break_glass_group_exclusion_is_accepted(self):
        b = copy.deepcopy(self.baseline)
        b["breakGlass"]["groupIds"] = ["a11ab000-0000-4000-8000-0000000000bb"]
        ps = copy.deepcopy(self.policies)
        for p in ps:
            p["conditions"]["users"]["excludeUsers"] = []
            p["conditions"]["users"]["excludeGroups"] = ["a11ab000-0000-4000-8000-0000000000bb"]
        self.assertEqual(v.rule_break_glass(ps, b), [])

    def test_report_only_does_not_satisfy_legacy_block(self):
        ps = copy.deepcopy(self.policies)
        next(p for p in ps if p["displayName"].startswith("CA001"))["state"] = "enabledForReportingButNotEnforced"
        self.assertNotEqual(v.rule_legacy_auth(ps, self.baseline), [])

    def test_mfa_scoped_by_location_does_not_count(self):
        ps = copy.deepcopy(self.policies)
        mfa = next(p for p in ps if p["displayName"].startswith("CA002"))
        mfa["conditions"]["locations"] = {"includeLocations": ["All"], "excludeLocations": ["AllTrusted"]}
        self.assertNotEqual(v.rule_all_users_mfa(ps, self.baseline), [])

    def test_authentication_strength_satisfies_all_users_mfa(self):
        ps = copy.deepcopy(self.policies)
        g = next(p for p in ps if p["displayName"].startswith("CA002"))["grantControls"]
        g["builtInControls"] = []
        g["authenticationStrength"] = {"id": "00000000-0000-0000-0000-000000000002"}
        self.assertEqual(v.rule_all_users_mfa(ps, self.baseline), [])

    def test_risk_rule_can_be_disabled_in_baseline(self):
        ps = copy.deepcopy(self.policies)
        next(p for p in ps if p["displayName"].startswith("CA005"))["state"] = "enabled"
        b = dict(self.baseline, riskPoliciesMustBeReportOnly=False)
        self.assertEqual(v.rule_risk_report_only(ps, b), [])


class TestFixturesAndCli(unittest.TestCase):
    def test_committed_fixtures_match_generator(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(make_fixtures.main(["--check"]), 0)

    def test_every_fixture_is_classified(self):
        names = {f for f in os.listdir(FIX) if f.endswith(".json") and f != "INDEX.json"}
        classified = set(BASELINE_NEGATIVES) | set(MALFORMED) | {"valid-graph-envelope.json"}
        self.assertEqual(names, classified)

    def test_cli_exit_codes(self):
        cases = [(POLICIES, 0), (os.path.join(FIX, "neg-missing-mfa.json"), 1),
                 (os.path.join(FIX, "malformed-truncated.json"), 2)]
        for path, code in cases:
            with self.subTest(path=os.path.basename(path)):
                r = subprocess.run([sys.executable, VALIDATOR, path, "--quiet"], capture_output=True, text=True)
                self.assertEqual(r.returncode, code, r.stderr)

    def test_cli_writes_reports(self):
        d = tempfile.mkdtemp()
        try:
            j, m = os.path.join(d, "r.json"), os.path.join(d, "r.md")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(v.main([POLICIES, "--json-out", j, "--md-out", m, "--quiet"]), 0)
            self.assertEqual(json.loads(_read(j))["overall"], "PASS")
            self.assertIn("| BASE-003 | baseline | PASS |", _read(m))
        finally:
            shutil.rmtree(d)

    def test_no_network_or_credential_code_paths(self):
        src = _read(VALIDATOR)
        for needle in ("urllib", "http.client", "requests", "socket", "graph.microsoft.com",
                       "login.microsoftonline.com", "msal", "azure"):
            self.assertNotIn(needle, src)


if __name__ == "__main__":
    unittest.main()
