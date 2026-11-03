"""Negative tests for scripts/ci/check_registries.py (each mutation must produce its rule's error)."""
import copy, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/ci"))
import check_registries as cr


class Registries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live = cr.load(ROOT)

    def run_with(self, mutate):
        mods, tasks, pages, pres, md = copy.deepcopy(self.live)
        mutate(mods, tasks, pages, pres, md)
        return cr.check(mods, tasks, pages, pres, md, root=ROOT)

    def assertRule(self, errs, rule):
        self.assertTrue(any(e.startswith(rule) for e in errs), errs)

    def test_live_registries_consistent(self):
        self.assertEqual(cr.check(*self.live, root=ROOT), [])

    def test_r1_status_disagreement_without_reconciliation(self):
        def m(mods, tasks, *_):
            next(r for r in tasks["tasks"] if r["pr"] == 6).pop("reconciled")
        self.assertRule(self.run_with(m), "R1")

    def test_r1_reconciled_with_wrong_status(self):
        def m(mods, tasks, *_):
            next(r for r in tasks["related_prs"] if r["pr"] == 14)["reconciled"]["current_status"] = "NOT_INTEGRATED"
        self.assertRule(self.run_with(m), "R1")

    def test_r1_integrated_record_but_module_not_integrated(self):
        def m(mods, *_):
            next(x for x in mods["modules"] if 5 in x.get("prs", []))["status"] = "BLOCKED"
        self.assertRule(self.run_with(m), "R1")

    def test_r1_pr_claimed_by_two_modules(self):
        def m(mods, *_):
            next(x for x in mods["modules"] if x["id"] == "observability")["prs"].append(3)
        self.assertRule(self.run_with(m), "R1")

    def test_r2_missing_and_orphan_page_entries(self):
        def m(mods, tasks, pages, pres, md):
            pages.pop("reports/review-pr3-pr6.md"); pages["no/such/file.md"] = {}
        errs = self.run_with(m)
        self.assertTrue(any("missing pages.json entry: reports/review-pr3-pr6.md" in e for e in errs), errs)
        self.assertTrue(any("orphan pages.json entry" in e for e in errs), errs)

    def test_r3_preserved_record_hash_changed(self):
        def m(mods, tasks, pages, pres, md):
            pres["reports/review-pr3-pr6.md"] = "0" * 64
        self.assertRule(self.run_with(m), "R3")

    def test_r4_review_record_not_frozen_or_not_archived(self):
        def m(mods, tasks, pages, pres, md):
            pres.pop("reports/review-candidate-a9d0f64.md"); pages["reports/review-candidate-08cdf11.md"]["lifecycle_status"] = "Stable"
        errs = self.run_with(m)
        self.assertTrue(any("not frozen" in e for e in errs) and any("not lifecycle Archived" in e for e in errs), errs)

    def test_r5_unknown_user_action(self):
        def m(mods, *_):
            next(x for x in mods["modules"] if x["id"] == "aws-cdk")["limitations"] += " See UA-99."
        self.assertRule(self.run_with(m), "R5")

    def test_r5_open_pr_user_action_not_cited_by_its_module(self):
        # The pre-candidate registry cited UA-3 for the Entra baseline, which is UA-2 (task PR-4).
        def m(mods, *_):
            x = next(x for x in mods["modules"] if x["id"] == "entra-offline"); x["limitations"] = "Baseline choices await owner confirmation (UA-3)."
        self.assertRule(self.run_with(m), "R5")


if __name__ == "__main__":
    unittest.main()
