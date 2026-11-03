"""The prepared rulesets (acceptance/rulesets/) never trust the shared agent account or a bot, and require the real checks."""
import json, re, subprocess, unittest
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True,
                           cwd=Path(__file__).resolve().parent).stdout.strip())
D = ROOT / "acceptance/rulesets"
FORBIDDEN = re.compile(r"onnxscibroccoli|\[bot\]|github-actions|dependabot|copilot", re.I)


def load(n):
    return json.loads((D / n).read_text())


class Rulesets(unittest.TestCase):
    def test_no_bypass_and_no_agent_or_bot_named(self):
        for n in ("main.ruleset.json", "evidence-acceptance.ruleset.json"):
            j = load(n)
            self.assertEqual(j["bypass_actors"], [], n)
            self.assertIsNone(FORBIDDEN.search(json.dumps(j)), n)
        owners = [l for l in (D / "CODEOWNERS.proposed").read_text().splitlines() if l.strip() and not l.startswith("#")]
        self.assertTrue(owners)
        self.assertFalse(any(FORBIDDEN.search(l) for l in owners))

    def test_review_and_history_rules(self):
        for n, branch, linear in (("main.ruleset.json", "refs/heads/main", False),
                                  ("evidence-acceptance.ruleset.json", "refs/heads/evidence/acceptance", True)):
            j = load(n); rules = {r["type"]: r.get("parameters") for r in j["rules"]}
            self.assertEqual(j["conditions"]["ref_name"]["include"], [branch])
            self.assertIn(j["enforcement"], ("evaluate", "disabled"), "an agent-prepared ruleset must not be active")
            self.assertIn("deletion", rules); self.assertIn("non_fast_forward", rules)
            self.assertEqual("required_linear_history" in rules, linear, n)
            p = rules["pull_request"]
            self.assertGreaterEqual(p["required_approving_review_count"], 1)
            self.assertTrue(p["require_code_owner_review"] and p["require_last_push_approval"] and p["dismiss_stale_reviews_on_push"])

    def test_main_requires_exactly_the_listed_real_checks(self):
        listed = [l for l in (D / "required-status-checks.main.txt").read_text().splitlines() if l and not l.startswith("#")]
        req = load("main.ruleset.json")
        sc = [r for r in req["rules"] if r["type"] == "required_status_checks"][0]["parameters"]
        self.assertTrue(sc["strict_required_status_checks_policy"])
        self.assertEqual(sorted(c["context"] for c in sc["required_status_checks"]), sorted(listed))
        self.assertEqual(len(set(listed)), len(listed))
        self.assertTrue({c["integration_id"] for c in sc["required_status_checks"]} == {15368})
        for must in ("merge-eligibility", "acceptance @ target SHA", "gate self-test (FAIL / required UNKNOWN must not pass)",
                     "defect control (injected CA002 report-only MUST make acceptance fail)", "module-registry", "final-summary"):
            self.assertIn(must, listed)
        self.assertNotIn("deploy", listed)


if __name__ == "__main__":
    unittest.main()
