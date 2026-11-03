"""The staged rulesets (acceptance/rulesets/) never trust the shared agent account or a bot, are not active, require the
real checks, and never leave the repository without an update path (stage 0 needs no human approval)."""
import json, re, subprocess, unittest
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True,
                           cwd=Path(__file__).resolve().parent).stdout.strip())
D = ROOT / "acceptance/rulesets"
FORBIDDEN = re.compile(r"onnxscibroccoli|\[bot\]|github-actions|dependabot|copilot", re.I)
MAIN, EV = "refs/heads/main", "refs/heads/evidence/acceptance"
FILES = {"stage0-main.ruleset.json": (MAIN, 0), "stage0-evidence-acceptance.ruleset.json": (EV, 0),
         "stage1-main.ruleset.json": (MAIN, 1), "stage1-evidence-acceptance.ruleset.json": (EV, 1),
         "stage2-main.ruleset.json": (MAIN, 2)}


def load(n):
    return json.loads((D / n).read_text())


def rules(j):
    return {r["type"]: r.get("parameters") for r in j["rules"]}


def listed():
    return [l for l in (D / "required-status-checks.main.txt").read_text().splitlines() if l and not l.startswith("#")]


class Rulesets(unittest.TestCase):
    def test_exactly_the_staged_files(self):
        self.assertEqual(sorted(p.name for p in D.glob("*.ruleset.json")), sorted(FILES))

    def test_no_bypass_no_agent_or_bot_not_active(self):
        for n in FILES:
            j = load(n)
            self.assertEqual(j["bypass_actors"], [], n)
            self.assertIsNone(FORBIDDEN.search(json.dumps(j)), n)
            self.assertEqual(j["enforcement"], "disabled", "prepared rulesets must not be active (owner activates)")
        owners = [l for l in (D / "CODEOWNERS.proposed").read_text().splitlines() if l.strip() and not l.startswith("#")]
        self.assertTrue(owners) ; self.assertFalse(any(FORBIDDEN.search(l) for l in owners))

    def test_every_stage_blocks_force_push_and_deletion(self):
        for n, (ref, _) in FILES.items():
            j = load(n); r = rules(j)
            self.assertEqual(j["conditions"]["ref_name"]["include"], [ref], n)
            self.assertIn("deletion", r, n); self.assertIn("non_fast_forward", r, n)
            self.assertEqual("required_linear_history" in r, ref == EV, n)

    def test_stage0_keeps_an_update_path(self):
        # With one collaborator (the PR author), any required approval would block every merge.
        for n, (_, st) in FILES.items():
            r = rules(load(n))
            if st == 0:
                self.assertNotIn("pull_request", r, n)
            else:
                p = r["pull_request"]
                self.assertTrue(p["required_approving_review_count"] >= 1 and p["require_code_owner_review"]
                                and p["require_last_push_approval"] and p["dismiss_stale_reviews_on_push"], n)

    def test_required_checks_per_stage(self):
        names = listed()
        self.assertEqual(len(names), len(set(names))); self.assertNotIn("deploy", names); self.assertIn("merge-eligibility", names)
        for n, (ref, st) in FILES.items():
            r = rules(load(n))
            if ref == EV:
                self.assertNotIn("required_status_checks", r, n); continue
            sc = r["required_status_checks"]
            got = sorted(c["context"] for c in sc["required_status_checks"])
            self.assertEqual({c["integration_id"] for c in sc["required_status_checks"]}, {15368})
            self.assertTrue(sc["strict_required_status_checks_policy"])
            want = sorted(names) if st == 2 else sorted(x for x in names if x != "merge-eligibility")
            self.assertEqual(got, want, n)
        for must in ("acceptance @ target SHA", "gate self-test (FAIL / required UNKNOWN must not pass)",
                     "defect control (injected CA002 report-only MUST make acceptance fail)", "module-registry", "final-summary"):
            self.assertIn(must, names)


if __name__ == "__main__":
    unittest.main()
