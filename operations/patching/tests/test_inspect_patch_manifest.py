"""Fixture tests for operations/patching/tools/inspect_patch_manifest.py (stdlib unittest; pytest-compatible).

Run from the repo root:
  python3 -m unittest discover -s operations/patching/tests -v
  python3 -m pytest operations/patching/tests        # if pytest is installed
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")
TOOL = os.path.join(HERE, "..", "tools", "inspect_patch_manifest.py")
EXAMPLE = os.path.join(HERE, "..", "manifests", "patch-manifest.example.json")
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import inspect_patch_manifest as ipm  # noqa: E402

# The rule(s) each negative fixture must trip -- and nothing else.
NEG_RULES = {
    "neg-bad-operation.json": {"PM-OPERATION"},
    "neg-bad-reboot.json": {"PM-REBOOT", "PM-TASK-REBOOT"},
    "neg-baseline-no-delay.json": {"PM-BASELINE-DELAY", "PM-BASELINE-REJECT-BLOCK"},
    "neg-baseline-os-mismatch.json": {"PM-BASELINE-OS"},
    "neg-canary-concurrency-5.json": {"PM-CANARY-SIZE", "PM-TASK-RATES"},
    "neg-canary-concurrency-percent.json": {"PM-CANARY-SIZE", "PM-TASK-RATES"},
    "neg-canary-errors.json": {"PM-CANARY-ERRORS", "PM-TASK-RATES"},
    "neg-canary-gated.json": {"PM-CANARY-NOGATE", "PM-TASK-GATED-SCAN"},
    "neg-duplicate-patchgroup.json": {"PM-PATCHGROUP-UNIQUE"},
    "neg-gate-no-compliance-evidence.json": {"PM-GATE-EVIDENCE"},
    "neg-gate-wrong-order.json": {"PM-GATE-ORDER"},
    "neg-gated-task-install.json": {"PM-TASK-GATED-SCAN"},
    "neg-missing-baseline-file.json": {"PM-REF-BASELINE"},
    "neg-missing-gate.json": {"PM-GATE-PRESENT", "PM-TASK-OPERATION"},
    "neg-no-approver.json": {"PM-GATE-APPROVERS"},
    "neg-no-escalation-contacts.json": {"PM-ESCALATION-CONTACTS"},
    "neg-no-presnapshot.json": {"PM-PRESNAPSHOT"},
    "neg-real-account-id.json": {"PM-NO-REAL-IDS"},
    "neg-ring-order-gap.json": {"PM-RING-ORDER"},
    "neg-rollback-no-procedure.json": {"PM-ROLLBACK-PROCEDURE"},
    "neg-rollback-too-slow.json": {"PM-ROLLBACK-TIME"},
    "neg-rollback-unknown-strategy.json": {"PM-ROLLBACK-STRATEGY"},
    "neg-short-soak.json": {"PM-GATE-SOAK"},
    "neg-task-rate-mismatch.json": {"PM-TASK-RATES"},
    "neg-unknown-patchgroup.json": {"PM-PATCHGROUP-KNOWN"},
}


def index():
    with open(os.path.join(FIX, "INDEX.json"), encoding="utf-8") as fh:
        return json.load(fh)["fixtures"]


class FixtureDrift(unittest.TestCase):
    def test_fixtures_match_generator(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "make_fixtures.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_neg_fixture_has_expected_rules(self):
        negs = {f["file"] for f in index() if f["file"].startswith("neg-")}
        self.assertEqual(negs, set(NEG_RULES))


class ExampleManifest(unittest.TestCase):
    def test_example_passes(self):
        rep = ipm.inspect(EXAMPLE)
        self.assertEqual(rep["overall"], "PASS", [r for r in rep["rules"] if r["result"] == "FAIL"])
        self.assertFalse(rep["awsCallsMade"])
        self.assertEqual(rep["mode"], "dry-run")

    def test_plan_order(self):
        rep = ipm.inspect(EXAMPLE)
        self.assertEqual([p["ring"] for p in rep["plan"]], ["canary", "wave1", "wave2"])


class Fixtures(unittest.TestCase):
    def test_exit_codes_via_cli(self):
        for f in index():
            with self.subTest(fixture=f["file"]):
                r = subprocess.run([sys.executable, TOOL, os.path.join(FIX, f["file"]), "--json"],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, f["expectedExit"], r.stdout[-800:] + r.stderr)
                json.loads(r.stdout)  # report is always valid JSON

    def test_negative_fixtures_fail_only_intended_rules(self):
        for name, rules in NEG_RULES.items():
            with self.subTest(fixture=name):
                rep = ipm.inspect(os.path.join(FIX, name))
                failed = {r["rule"] for r in rep["rules"] if r["result"] == "FAIL"}
                self.assertEqual(failed, rules)

    def test_malformed_raise(self):
        for f in index():
            if f["file"].startswith("malformed-"):
                with self.subTest(fixture=f["file"]):
                    with self.assertRaises(ipm.Malformed):
                        ipm.inspect(os.path.join(FIX, f["file"]))


class NoSideEffects(unittest.TestCase):
    def test_tool_never_invokes_aws(self):
        with open(TOOL, encoding="utf-8") as fh:
            src = fh.read()
        for needle in ("subprocess", "boto3", "botocore", "urllib", "socket", "os.system"):
            self.assertNotIn(needle, src, needle)


class CliInputs(unittest.TestCase):
    CLI = os.path.join(HERE, "..", "ssm", "cli")

    def test_all_cli_inputs_are_json_with_placeholders_only(self):
        for fn in sorted(os.listdir(self.CLI)):
            with self.subTest(file=fn):
                with open(os.path.join(self.CLI, fn), encoding="utf-8") as fh:
                    text = fh.read()
                doc = json.loads(text)
                self.assertIsInstance(doc, dict)
                self.assertIsNone(ipm.ACCOUNT_ID_RE.search(text))
                self.assertIsNone(ipm.REAL_ID_RE.search(text))
                for k in ("WindowId", "BaselineId"):
                    if k in doc:
                        self.assertRegex(doc[k], r"^<[A-Z0-9_]+>$")


if __name__ == "__main__":
    unittest.main()
