"""Tests for the acceptance contract (stdlib unittest; reads committed SYNTHETIC fixtures only).

Run from the repo root:
    python3 -m unittest discover -s tests/acceptance-contract -v
"""
import contextlib
import io
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FX = HERE / "fixtures"
sys.path.insert(0, str(REPO / "schemas" / "acceptance"))
import check_acceptance as ca  # noqa: E402

INDEX = json.loads((FX / "INDEX.json").read_text())
ROOT = FX / INDEX["repo_root"]
CODE = re.compile(r"^\[(E_[A-Z_]+)\]")


def evaluate(kind, name):
    return ca.evaluate(FX / "docs" / kind / f"{name}.json", ROOT)


class ReusesSharedValidator(unittest.TestCase):
    def test_imports_shared_module_not_a_copy(self):
        self.assertEqual(Path(ca.ve.__file__).resolve(), (REPO / "evidence/shared/validate_evidence.py").resolve())

    def test_schema_refs_resolve_into_shared_evidence_schema(self):
        raw = json.loads(ca.SCHEMA.read_text())
        ref = raw["properties"]["requirements"]["items"]["properties"]["evidence_refs"]["items"]["properties"]["sha256"]["$ref"]
        self.assertTrue(ref.startswith("../../evidence/shared/evidence-manifest.schema.json#"))
        shared = json.loads((REPO / "evidence/shared/evidence-manifest.schema.json").read_text())
        inlined = ca.load_schema()["properties"]["requirements"]["items"]["properties"]["evidence_refs"]["items"]["properties"]["sha256"]
        self.assertEqual(inlined, shared["properties"]["anchors"]["items"]["properties"]["sha256"])
        self.assertNotIn("$ref", json.dumps(ca.load_schema()))

    def test_fixture_manifests_pass_shared_manifest_check(self):
        for m in sorted((ROOT / "evidence").glob("*/MANIFEST.json")):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = ca.ve.main(["manifest", str(m)])
            self.assertEqual(rc, 1 if "bad-manifest" in str(m) else 0, f"{m}: {out.getvalue()}")


class Fixtures(unittest.TestCase):
    def test_fixtures_not_drifted(self):
        r = subprocess.run([sys.executable, str(HERE / "make_fixtures.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_every_fixture_is_synthetic(self):
        for p in (FX / "docs").rglob("*.json"):
            self.assertIs(json.loads(p.read_text())["document"]["synthetic"], True, p)

    def test_valid_fixtures_decide_as_indexed(self):
        for name, exp in INDEX["valid"].items():
            with self.subTest(name):
                rep = evaluate("valid", name)
                self.assertTrue(rep["valid"], rep["errors"])
                self.assertEqual(rep["decision"], exp["decision"], rep.get("blockers"))
                self.assertEqual(rep["exit"], 0 if exp["decision"] == "AUTOMATIC_TECHNICAL_ACCEPTANCE" else 4)

    def test_invalid_fixtures_rejected_with_exact_codes(self):
        for name, exp in INDEX["invalid"].items():
            with self.subTest(name):
                rep = evaluate("invalid", name)
                self.assertFalse(rep["valid"])
                self.assertEqual(rep["decision"], "INVALID")
                self.assertEqual(rep["exit"], 1)
                codes = {CODE.match(e).group(1) for e in rep["errors"]}
                self.assertEqual(codes, set(exp["errors"]), rep["errors"])


class Rules(unittest.TestCase):
    """One named test per contract rule, so a regression points at the rule it breaks."""

    def assertCode(self, name, code):
        rep = evaluate("invalid", name)
        self.assertIn(code, {CODE.match(e).group(1) for e in rep["errors"]}, rep["errors"])

    def test_pass_and_fail_require_evidence(self):
        self.assertCode("pass-without-evidence", "E_RESULT_NEEDS_EVIDENCE")
        self.assertCode("fail-without-evidence", "E_RESULT_NEEDS_EVIDENCE")

    def test_evidence_refs_must_resolve_to_evidence_records(self):
        for name, code in [("evidence-missing-manifest", "E_EVIDENCE_UNRESOLVED"), ("evidence-missing-artifact", "E_EVIDENCE_UNRESOLVED"),
                           ("evidence-outside-bundle", "E_EVIDENCE_UNRESOLVED"), ("evidence-hash-mismatch", "E_EVIDENCE_HASH_MISMATCH"),
                           ("evidence-not-covered", "E_EVIDENCE_NOT_COVERED"), ("evidence-manifest-invalid", "E_EVIDENCE_MANIFEST_INVALID"),
                           ("evidence-bundle-tampered", "E_EVIDENCE_BUNDLE_HASHES"), ("evidence-other-commit", "E_EVIDENCE_COMMIT_MISMATCH")]:
            with self.subTest(name):
                self.assertCode(name, code)

    def test_skipped_unavailable_not_run_stay_unknown(self):
        for name in ("skipped-but-pass", "unavailable-but-fail", "not-run-but-pass", "skipped-but-not-applicable"):
            with self.subTest(name):
                self.assertCode(name, "E_RESULT_NOT_EXECUTED")

    def test_result_matches_expected_vs_observed(self):
        for name in ("pass-but-exit-mismatch", "pass-but-output-unmatched", "fail-but-expectation-met"):
            with self.subTest(name):
                self.assertCode(name, "E_RESULT_INCONSISTENT")

    def test_not_applicable_requires_rationale(self):
        self.assertCode("not-applicable-without-rationale", "E_RATIONALE_REQUIRED")
        self.assertCode("not-applicable-blank-rationale", "E_RATIONALE_REQUIRED")

    def test_malformed_exception_dispositions_rejected(self):
        for name in ("exception-on-pass", "exception-missing-expiry", "exception-expiry-before-approval", "exception-impossible-date",
                     "exception-self-approved", "exception-compensating-without-control"):
            with self.subTest(name):
                self.assertCode(name, "E_EXCEPTION_MALFORMED")
        for name in ("exception-unknown-disposition", "exception-missing-approver", "exception-extra-key"):
            with self.subTest(name):
                self.assertCode(name, "E_SCHEMA")

    def test_reviewer_must_be_independent_and_review_tested_commit(self):
        self.assertCode("reviewer-is-recorder", "E_REVIEWER_NOT_INDEPENDENT")
        self.assertCode("review-of-other-commit", "E_REVIEW_COMMIT_MISMATCH")

    def test_exact_40_hex_tested_commit(self):
        self.assertCode("short-commit-sha", "E_SCHEMA")
        self.assertCode("branch-name-as-commit", "E_SCHEMA")
        self.assertCode("commit-differs-from-document", "E_COMMIT_MISMATCH")

    def test_fail_blocks_even_with_exception(self):
        rep = evaluate("valid", "blocked-fail-with-exception")
        self.assertEqual(rep["decision"], "BLOCKED")
        self.assertTrue(any(b["reason"].startswith("FAIL") for b in rep["blockers"]))

    def test_required_unknown_blocks_but_advisory_unknown_does_not(self):
        self.assertEqual(evaluate("valid", "blocked-required-unknown")["decision"], "BLOCKED")
        acc = evaluate("valid", "accept")
        self.assertEqual(acc["decision"], "AUTOMATIC_TECHNICAL_ACCEPTANCE")
        self.assertEqual(acc["counts"]["UNKNOWN"], 1)  # advisory UNKNOWN present, not blocking

    def test_empty_document_fails_closed(self):
        self.assertEqual(evaluate("valid", "blocked-empty")["decision"], "BLOCKED")

    def test_cli_exit_codes(self):
        cli = [sys.executable, str(REPO / "schemas/acceptance/check_acceptance.py")]
        for kind, name, rc in [("valid", "accept", 0), ("valid", "blocked-required-unknown", 4), ("invalid", "pass-without-evidence", 1)]:
            with self.subTest(name):
                r = subprocess.run(cli + [str(FX / "docs" / kind / f"{name}.json"), "--repo-root", str(ROOT)], capture_output=True, text=True)
                self.assertEqual(r.returncode, rc, r.stdout + r.stderr)
        r = subprocess.run(cli + [str(FX / "nope.json")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
