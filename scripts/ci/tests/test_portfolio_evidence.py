"""Strict evidence rejection tests. Historical evidence bundles are untouched."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))
import verify_evidence as v  # noqa: E402

A = "a" * 40
B = "b" * 40
DIGEST = "f" * 64


class StrictEvidenceContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.evidence = Path(self.tmp.name)
        self.report = self.evidence / "report.json"
        self.report_data = {
            "tests": 3, "assertions": 3, "skipped": 0, "failed": 0, "exitCode": 0,
            "negativeControls": [
                {"id": "replay-denied", "status": "REJECTED_AS_EXPECTED",
                 "observedReason": "untrusted operation correctly blocked"},
            ],
        }
        self.flush_report()
        producer = ROOT / "scripts" / "ci" / "verify_evidence.py"
        readme = ROOT / "README.md"
        configs = {"README.md": v.sha_file(readme)}
        self.manifest = {
            "schemaVersion": "1.0.0",
            "repository": "onnxscibroccoli/bank-it-operations-lab",
            "module": "evidence-test",
            "candidateSha": A, "testedSha": A, "baseSha": None,
            "producer": {"name": "scripts/ci/verify_evidence.py",
                         "sourceSha": A, "sha256": v.sha_file(producer)},
            "workflow": "engineering-evidence",
            "runId": "123456", "runAttempt": 1, "event": "push",
            "environment": {"runner": "test-runner", "os": "Linux",
                            "toolVersions": {"python": "3.12"},
                            "sourceTreeDigest": DIGEST,
                            "configurationDigest": v.configuration_digest(configs),
                            "configurationFiles": configs, "lockfiles": {}},
            "verification": {
                "mode": "EXECUTED_CI", "result": "PASS",
                "checks": [
                    {"id": "check-1", "commandId": "unittest-contract",
                     "exitCode": 0, "testCount": 3, "expectedAssertions": 3,
                     "skippedTests": 0, "report": "report.json",
                     "negativeControls": deepcopy(self.report_data["negativeControls"])}
                ],
            },
            "artifacts": [self.file_entry("report.json")],
            "limitations": ["Synthetic unit fixture, not a real GitHub Actions run."],
            "approvalEffective": False,
            "timing": {"startedAt": "2026-11-04T00:00:00Z",
                       "finishedAt": "2026-11-04T00:00:01Z",
                       "verifiedAt": "2026-11-04T00:00:02Z"},
            "retention": {"days": 7, "provider": "github-actions",
                          "expiresAt": "2026-11-11T00:00:00Z"},
            "attestations": [],
        }
        self.expected = {
            "repository": self.manifest["repository"],
            "candidateSha": A, "testedSha": A, "baseSha": None,
            "runId": "123456", "runAttempt": 1, "event": "push",
            "sourceTreeDigest": DIGEST,
        }

    def flush_report(self):
        self.report.write_text(json.dumps(self.report_data, sort_keys=True) + "\n")

    def file_entry(self, relative):
        path = self.evidence / relative
        return {"path": relative, "sha256": v.sha_file(path),
                "bytes": path.stat().st_size}

    def issues(self):
        return v.verify(self.manifest, self.evidence, ROOT, expected=self.expected)

    def assert_rejected(self):
        problems = self.issues()
        self.assertTrue(problems, "malformed evidence unexpectedly accepted")
        return problems

    def test_positive_fixture_is_structurally_accepted(self):
        self.assertEqual(self.issues(), [])

    def test_negative_01_post_hash_tampering(self):
        self.report.write_text(self.report.read_text() + "tampered\n")
        self.assertIn("hash or size mismatch", " ".join(self.assert_rejected()))

    def test_negative_02_candidate_sha_substitution(self):
        self.manifest["candidateSha"] = B
        self.assertIn("mismatched expected", " ".join(self.assert_rejected()))

    def test_negative_03_required_report_missing(self):
        self.report.unlink()
        self.assertIn("file missing", " ".join(self.assert_rejected()))

    def test_negative_04_duplicate_json_key(self):
        path = self.evidence / "manifest.json"
        raw = json.dumps(self.manifest)
        raw = raw.replace('"schemaVersion": "1.0.0",',
                          '"schemaVersion": "1.0.0", "schemaVersion": "1.0.0",')
        path.write_text(raw)
        with self.assertRaises(v.EvidenceError):
            v.read_json(path)

    def test_negative_05_directory_traversal(self):
        self.manifest["artifacts"][0]["path"] = "../report.json"
        self.assertIn("unsafe", " ".join(self.assert_rejected()))

    def test_negative_06_symlink_outside_bundle(self):
        outer = Path(self.tmp.name).parent / ("outside-evidence-" + self.tmp.name.split("/")[-1])
        outer.write_text(self.report.read_text())
        self.addCleanup(lambda: outer.unlink(missing_ok=True))
        self.report.unlink()
        self.report.symlink_to(outer)
        self.assertIn("symlink traversal", " ".join(self.assert_rejected()))

    def test_negative_07_zero_suite_success(self):
        self.manifest["verification"]["checks"][0]["testCount"] = 0
        self.report_data["tests"] = 0
        self.flush_report()
        self.manifest["artifacts"][0] = self.file_entry("report.json")
        self.assertIn("must be positive", " ".join(self.assert_rejected()))

    def test_negative_08_wrong_expected_failure_reason(self):
        n = self.manifest["verification"]["checks"][0]["negativeControls"][0]
        n["observedReason"] = "not the observed failure"
        self.assertIn("reason/outcome mismatch", " ".join(self.assert_rejected()))

    def test_negative_09_missing_execution_marked_pass(self):
        self.manifest["verification"]["mode"] = "NOT_EXECUTED"
        self.assertIn("requires EXECUTED_CI/PASS", " ".join(self.assert_rejected()))

    def test_negative_10_fabricated_human_approval(self):
        self.manifest["approvalEffective"] = True
        self.assertIn("cannot grant human approval", " ".join(self.assert_rejected()))

    def test_unknown_schema_property(self):
        self.manifest["verification"]["checks"][0]["unreviewed"] = True
        self.assertIn("unknown fields", " ".join(self.assert_rejected()))

    def test_duplicate_artifact_paths(self):
        self.manifest["artifacts"].append(deepcopy(self.manifest["artifacts"][0]))
        self.assertIn("duplicate path", " ".join(self.assert_rejected()))

    def test_unexpected_skipped_tests(self):
        self.manifest["verification"]["checks"][0]["skippedTests"] = 1
        self.assertIn("unexpected skipped", " ".join(self.assert_rejected()))

    def test_mismatched_workflow_retry_identity(self):
        self.manifest["runAttempt"] = 2
        self.assertIn("mismatched expected", " ".join(self.assert_rejected()))

    def test_pr_synthetic_merge_parent_order(self):
        self.manifest["event"] = "pull_request"
        self.manifest["candidateSha"] = B
        self.manifest["testedSha"] = A
        self.manifest["baseSha"] = "c" * 40
        self.manifest["producer"]["sourceSha"] = A
        self.expected.update(event="pull_request", candidateSha=B, baseSha="c" * 40)
        problems = v.verify(self.manifest, self.evidence, ROOT, expected=self.expected,
                            parents=(B, "c" * 40))
        self.assertIn("merge parents differ", " ".join(problems))
        valid_order = v.verify(self.manifest, self.evidence, ROOT, expected=self.expected,
                               parents=("c" * 40, B))
        self.assertEqual(valid_order, [])


if __name__ == "__main__":
    unittest.main()
