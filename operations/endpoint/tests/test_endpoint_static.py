"""Static checks for the endpoint module. No Windows host and no tenant calls."""
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS1 = ROOT / "powershell" / "Invoke-LabIdentityChange.ps1"
BASELINE = ROOT / "baselines" / "intune-compliance.json"
FIREWALL = ROOT / "baselines" / "firewall-rules.csv"
FORBIDDEN = ("Invoke-Expression", "ConvertTo-SecureString", "password", "-ExecutionPolicy Bypass", "net user")


class EndpointStatic(unittest.TestCase):
    def test_script_refuses_secret_material_and_dynamic_execution(self):
        text = PS1.read_text()
        lowered = text.lower()
        for token in FORBIDDEN:
            self.assertNotIn(token.lower(), lowered, token)
        for action in ("joiner", "mover", "leaver"):
            self.assertIn(f"'{action}'", text)
        self.assertIn("disable-account", text)
        self.assertLess(text.index("disable-account"), text.index("remove-job-role"))

    def test_intune_baseline_is_explicitly_not_executed(self):
        doc = json.loads(BASELINE.read_text())
        self.assertFalse(doc["executed"])
        self.assertEqual(doc["evidenceClass"], "STATIC_VALIDATED")
        settings = doc["settings"]
        for key in ("bitLocker", "secureBoot", "defenderRealTime", "firewallPublic"):
            self.assertIs(settings[key], True)
        self.assertGreaterEqual(settings["passwordMinimumLength"], 14)

    def test_firewall_default_deny_and_no_ssh_allow(self):
        with FIREWALL.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(any(r["name"] == "deny-inbound-any" and r["action"] == "block" for r in rows))
        ssh_allows = [r for r in rows if r["local_port"] == "22" and r["action"] == "allow"]
        self.assertEqual(ssh_allows, [])
        any_allow = [r for r in rows if r["remote_address"] == "any" and r["action"] == "allow"]
        self.assertEqual(any_allow, [])


if __name__ == "__main__":
    unittest.main()
