"""Owner-authentication design stays fail-closed. No key is enrolled and no reviewer is named."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(HERE))
from verify_owner_attestation import load_enrolled, verify  # noqa: E402


class OwnerAuth(unittest.TestCase):
    def test_allow_list_and_enrollment_are_empty(self):
        allow = json.loads((HERE / "reviewer-allowlist.json").read_text())
        keys = json.loads((HERE / "enrolled-owner-keys.json").read_text())
        self.assertEqual(allow["users"], [])
        self.assertEqual(keys["keys"], [])
        self.assertEqual(load_enrolled(HERE / "enrolled-owner-keys.json"), {})

    def test_empty_enrollment_rejects_a_well_formed_payload(self):
        payload = {
            "candidateSha": "a" * 40,
            "decision": "approve-exception",
            "exceptionId": "EX-04",
            "keyFingerprint": "ab" * 32,
        }
        self.assertFalse(verify(payload, "AA==", {}))

    def test_required_checks_match_the_integration_gate(self):
        listed = json.loads((HERE / "required-checks.json").read_text())["checks"]
        workflow = (ROOT / ".github/workflows/integration-gate.yml").read_text()
        for name in listed:
            self.assertIn(f"\n  {name}:\n", workflow)
        self.assertIn("merge-eligibility", listed)
        self.assertIn("final-summary", listed)


if __name__ == "__main__":
    unittest.main()
