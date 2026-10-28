import shutil
import unittest

from _helpers import TmpMixin, copytree, non_pass, by_id
from acceptance.modules import entra_offline as E

# smallest valid expectation set (keeps unrelated checks green so each test isolates one fault)
MIN = ({"neg-missing-mfa.json": {"BASE-003"}}, {"malformed-nan.json": "SCHEMA-001"})


class EntraAdapterTest(TmpMixin, unittest.TestCase):
    def test_baseline_and_all_declared_fixtures_pass(self):
        r = E.run()
        d = r.to_dict()
        self.assertEqual(d["status"], "PASS", non_pass(r))
        neg, mal = E.module_expectations()
        self.assertEqual(sum(c.id.startswith("ENTRA-NEG-") and c.id != "ENTRA-NEG-COUNT" for c in r.checks), len(neg))
        self.assertEqual(sum(c.id.startswith("ENTRA-MAL-") for c in r.checks), len(mal))
        self.assertGreaterEqual(len(neg), 17)
        self.assertGreaterEqual(len(mal), 19)

    # --- negatives
    def test_removed_mfa_policy_fails_baseline_for_base_003(self):
        pol = copytree(E.ENTRA / "policies", self.td)
        (pol / "CA002-Require-MFA-All-Users.json").unlink()
        r = E.run(policies=pol, expectations=MIN)
        c = by_id(r)["ENTRA-BASE-001"]
        self.assertEqual(c.reason_code, "BASELINE_RULE_FAILED")
        self.assertIn("BASE-003", c.detail)

    def test_malformed_policy_set_fails_closed(self):
        pol = self.td / "pol"
        pol.mkdir()
        shutil.copy(E.FIXTURES / "malformed-truncated.json", pol / "x.json")
        r = E.run(policies=pol, expectations=MIN)
        c = by_id(r)["ENTRA-BASE-001"]
        self.assertEqual(c.reason_code, "INPUT_MALFORMED")
        self.assertIn("SCHEMA-001", c.detail)

    def test_negative_rejected_by_other_rule_is_wrong_reason(self):
        r = E.run(expectations=({"neg-missing-mfa.json": {"BASE-006"}}, {"malformed-nan.json": "SCHEMA-001"}))
        self.assertEqual(non_pass(r), {"ENTRA-NEG-neg-missing-mfa": "NEGATIVE_WRONG_REASON"})
        self.assertIn("BASE-003", by_id(r)["ENTRA-NEG-neg-missing-mfa"].detail)

    def test_valid_fixture_declared_negative_is_unexpected_success(self):
        r = E.run(expectations=({"valid-graph-envelope.json": {"BASE-003"}}, {"malformed-nan.json": "SCHEMA-001"}))
        self.assertEqual(non_pass(r), {"ENTRA-NEG-valid-graph-envelope": "NEGATIVE_UNEXPECTED_SUCCESS"})

    def test_malformed_fixture_declared_as_baseline_negative_is_wrong_reason(self):
        # right rule family, wrong exit class: malformed input exits 2 (fail closed), not 1
        r = E.run(expectations=({"malformed-nan.json": {"SCHEMA-001"}}, {"malformed-nan.json": "SCHEMA-001"}))
        self.assertEqual(non_pass(r), {"ENTRA-NEG-malformed-nan": "NEGATIVE_WRONG_REASON"})
        self.assertIn("exit 2 (want 1)", by_id(r)["ENTRA-NEG-malformed-nan"].detail)

    def test_no_declared_negatives_fails_count(self):
        r = E.run(expectations=({}, {}))
        self.assertEqual(non_pass(r), {"ENTRA-NEG-COUNT": "NEGATIVE_COUNT"})

    def test_tampered_evidence_run_fails_on_hash(self):
        runs = copytree(E.EVIDENCE_RUNS, self.td)
        run = next(p for p in runs.iterdir() if p.is_dir())
        (run / "SUMMARY.md").write_text("tampered\n")
        r = E.run(evidence_runs=runs, expectations=MIN)
        self.assertEqual(non_pass(r), {f"ENTRA-EV-{run.name}": "EVIDENCE_HASH_MISMATCH"})

    def test_missing_evidence_runs_is_missing_evidence(self):
        r = E.run(evidence_runs=self.td / "none", expectations=MIN)
        self.assertEqual(non_pass(r), {"ENTRA-EV-000": "EVIDENCE_MISSING"})


if __name__ == "__main__":
    unittest.main()
