"""Module coverage must fail closed: no functional module without a delivery_location, no silent denominator narrowing."""
import copy, json, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_modules, user_actions  # noqa: E402

REG = json.loads((Path(__file__).resolve().parents[3] / "coordination/modules.json").read_text())


def errs(reg):
    return check_modules.coverage(reg)[1]


def mod(reg, mid):
    return next(m for m in reg["modules"] if m["id"] == mid)


class Coverage(unittest.TestCase):
    def test_committed_registry_is_valid(self):
        self.assertEqual(errs(REG), [])

    def test_denominator_counts_every_status(self):
        c, _ = check_modules.coverage(REG)
        self.assertEqual(c["denominator"], len(REG["modules"]))
        self.assertEqual(c["completion_denominator"], c["denominator"] - c["by_status"].get("SUPERSEDED", 0))
        self.assertIn("orgs-security(BLOCKED)", c["incomplete"])

    def test_functional_without_delivery_location_fails(self):
        for mid in ("aws-cdk", "observability", "aws-network-edge"):
            r = copy.deepcopy(REG); mod(r, mid).pop("delivery_location")
            self.assertTrue(any("no delivery_location" in e for e in errs(r)), mid)
            r = copy.deepcopy(REG); mod(r, mid)["delivery_location"] = []
            self.assertTrue(any("no delivery_location" in e for e in errs(r)), mid)

    def test_delivery_location_outside_paths_fails(self):
        r = copy.deepcopy(REG); mod(r, "observability")["delivery_location"] = ["somewhere/else"]
        self.assertTrue(any("not inside the module's paths" in e for e in errs(r)))

    def test_dropping_a_module_below_floor_fails(self):
        r = copy.deepcopy(REG); r["modules"] = [m for m in r["modules"] if m["id"] != "orgs-security"]
        self.assertTrue(any("denominator narrowed" in e for e in errs(r)))

    def test_missing_floor_fails(self):
        r = copy.deepcopy(REG); r["coverage"].pop("denominator_floor")
        self.assertTrue(any("denominator_floor" in e for e in errs(r)))

    def test_blocked_needs_reason_and_category(self):
        r = copy.deepcopy(REG); mod(r, "orgs-security")["reason"] = ""
        self.assertTrue(any("BLOCKED needs a reason" in e for e in errs(r)))
        r = copy.deepcopy(REG); mod(r, "orgs-security")["category"] = "functional"
        self.assertTrue(any("must go together" in e for e in errs(r)))

    def test_superseded_needs_successor(self):
        r = copy.deepcopy(REG); mod(r, "bank-aws-001")["superseded_by"] = "nope"
        self.assertTrue(any("superseded_by" in e for e in errs(r)))

    def test_integrated_functional_needs_present_checks(self):
        r = copy.deepcopy(REG); mod(r, "incident-demo")["required_checks"]["present"] = []
        self.assertTrue(any("no required_checks.present" in e for e in errs(r)))

    def test_owner_required(self):
        r = copy.deepcopy(REG); mod(r, "vendor-mock").pop("owner")
        self.assertTrue(any("owner.agent" in e for e in errs(r)))

    def test_user_actions_fails_closed_on_bad_coverage(self):
        import tempfile, io
        from contextlib import redirect_stdout
        r = copy.deepcopy(REG); mod(r, "aws-cdk").pop("delivery_location")
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(r, f)
        with redirect_stdout(io.StringIO()) as out:
            rc = user_actions.main(["--modules", f.name])
        self.assertEqual(rc, 1)
        self.assertIn("no delivery_location", out.getvalue())
        with redirect_stdout(io.StringIO()) as out:
            rc = user_actions.main([])
        self.assertEqual(rc, 0)
        self.assertIn("MODULE COVERAGE:", out.getvalue())


if __name__ == "__main__":
    unittest.main()
