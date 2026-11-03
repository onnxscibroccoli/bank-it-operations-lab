"""Mapping onto PR #23's shared acceptance contract.

Structural checks use the shared evidence validator (always present). Full contract evaluation uses PR #23's
schemas/acceptance/check_acceptance.py when available (merged, or ACCEPTANCE_CONTRACT_ROOT=<checkout of #23>);
those tests are skipped, not passed, when it is absent."""
import copy
import json
import unittest

from _helpers import ROOT, TmpMixin, copytree, reseal_listed
from acceptance.modules import aws_cdk, emit_shared, entra_offline, postgres, _util as U

SHARED_V = ROOT / "evidence/shared/validate_evidence.py"
SHA = U.git_sha()
CHECKER = emit_shared.contract_checker()
needs_checker = unittest.skipIf(CHECKER is None, "PR #23 check_acceptance.py not available (set ACCEPTANCE_CONTRACT_ROOT)")


class EmitSharedTest(TmpMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = [m.run().to_dict() for m in (aws_cdk, postgres, entra_offline)]

    def emit(self, results=None):
        return emit_shared.emit(results or self.results, self.td, "t1", SHA)

    def evaluate(self, doc):
        rc, out = U.py(str(CHECKER), str(doc), "--repo-root", str(self.td), "--json")
        return rc, json.loads(out)

    def test_bundle_passes_shared_validator(self):
        self.emit()
        b = self.td / "evidence/acceptance-modules/t1"
        for argv in (["manifest", str(b / "MANIFEST.json")], ["hashes", str(b / "SHA256SUMS")],
                     ["commands", str(b / "logs/COMMANDS.tsv"), "--format", "aws-3col"]):
            rc, out = U.py(str(SHARED_V), *argv)
            self.assertEqual(rc, 0, out)

    def test_requirement_mapping(self):
        doc = json.loads(self.emit().read_text())
        self.assertEqual([q["id"] for q in doc["requirements"]], ["ACC-MOD-AWS-001", "ACC-MOD-PG-001", "ACC-MOD-ENTRA-001"])
        for q in doc["requirements"]:
            self.assertEqual((q["result"], q["check"]["observed"]["exit_code"], q["tested_source_commit"]), ("PASS", 0, SHA))
            self.assertEqual(len(q["evidence_refs"]), 2)
            self.assertEqual(q["reviewer_findings"], [])

    def test_rejects_non_40_hex_commit(self):
        with self.assertRaisesRegex(ValueError, "40-hex"):
            emit_shared.emit(self.results, self.td, "t1", "acceptance-adapters")

    @needs_checker
    def test_valid_document_is_blocked_only_for_missing_independent_review(self):
        rc, rep = self.evaluate(self.emit())
        self.assertEqual((rc, rep["decision"], rep["errors"]), (4, "BLOCKED", []))
        self.assertEqual({b["reason"] for b in rep["blockers"]}, {"required PASS lacks an independent reviewer concurrence"})

    @needs_checker
    def test_with_independent_concur_document_is_accepted(self):
        dp = self.emit()
        doc = json.loads(dp.read_text())
        for q in doc["requirements"]:
            q["reviewer_findings"] = [{"reviewer": "SYNTHETIC-test-reviewer", "reviewed_commit": SHA, "verdict": "concur",
                                       "finding": "test only", "date": "2026-10-28"}]
        dp.write_text(json.dumps(doc))
        rc, rep = self.evaluate(dp)
        self.assertEqual((rc, rep["decision"]), (0, "AUTOMATIC_TECHNICAL_ACCEPTANCE"))

    # --- negatives
    @needs_checker
    def test_failing_adapter_maps_to_fail_and_blocks(self):
        (self.td / "src").mkdir()
        ev = copytree(aws_cdk.EVIDENCE, self.td / "src")
        p = ev / "cdk-nag/AwsSolutions--BankItLabNetworkDatabase-NagReport.csv"
        p.write_text(p.read_text() + '"AwsSolutions-RDS3","X","Non-Compliant","N/A","Error","x"\n')
        reseal_listed(ev / "SHA256SUMS")
        bad = aws_cdk.run(evidence_dir=ev).to_dict()
        doc = json.loads(self.emit([bad] + self.results[1:]).read_text())
        q = doc["requirements"][0]
        self.assertEqual((q["result"], q["check"]["observed"]["exit_code"]), ("FAIL", 1))
        self.assertIn("NAG_NON_COMPLIANT", q["result_rationale"])
        rc, rep = self.evaluate(self.td / "acceptance-modules-t1.json")
        self.assertEqual((rc, rep["decision"], rep["errors"]), (4, "BLOCKED", []))
        self.assertIn({"id": "ACC-MOD-AWS-001", "reason": "FAIL"}, rep["blockers"])

    @needs_checker
    def test_tampered_emitted_artifact_is_invalid_for_bundle_hashes(self):
        dp = self.emit()
        (self.td / "evidence/acceptance-modules/t1/logs/postgres.result.json").write_text("{}")
        rc, rep = self.evaluate(dp)
        self.assertEqual((rc, rep["decision"]), (1, "INVALID"))
        self.assertTrue(rep["errors"] and all("[E_EVIDENCE_BUNDLE_HASHES]" in e for e in rep["errors"]), rep["errors"])

    @needs_checker
    def test_other_commit_is_invalid_for_commit_mismatch(self):
        dp = self.emit()
        doc = json.loads(dp.read_text())
        other = "0" * 40
        doc["document"]["tested_source_commit"] = other
        for q in doc["requirements"]:
            q["tested_source_commit"] = other
        dp.write_text(json.dumps(doc))
        rc, rep = self.evaluate(dp)
        self.assertEqual(rc, 1)
        self.assertTrue(all("[E_EVIDENCE_COMMIT_MISMATCH]" in e for e in rep["errors"]), rep["errors"])

    def test_tampered_emitted_artifact_fails_shared_hashes_even_without_checker(self):
        self.emit()
        b = self.td / "evidence/acceptance-modules/t1"
        (b / "logs/aws-cdk.log").write_text("tampered\n")
        rc, out = U.py(str(SHARED_V), "hashes", str(b / "SHA256SUMS"))
        self.assertEqual(rc, 1)
        self.assertIn("sha256 mismatch for logs/aws-cdk.log", out)


if __name__ == "__main__":
    unittest.main()
