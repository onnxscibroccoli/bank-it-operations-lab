"""Offline unit tests for cost_model.py: python3 -m unittest discover -s docs/runbooks/aws-backup/cost-capacity -p 'test_*.py' -v"""
import copy
import json
import unittest
from pathlib import Path

import cost_model as m

INPUTS = json.loads((Path(__file__).parent / "cost-inputs.estimate.json").read_text())


class CostModel(unittest.TestCase):
    def test_monthly_points_cold_capable(self):
        self.assertEqual(m.monthly_points(365, 90, 30.4, True), (3, 10))

    def test_monthly_points_not_cold_capable_stays_warm(self):
        self.assertEqual(m.monthly_points(365, 90, 30.4, False), (13, 0))

    def test_pitr_logs_not_in_dr_vault(self):
        r = dict(INPUTS["resources"][0])
        q = m.resource_quantities(r, INPUTS["retention"])
        self.assertAlmostEqual(q["primary_vault"]["warm_gb_month"] - q["dr_vault"]["warm_gb_month"], r["pitr_log_gb_per_day"] * 35)

    def test_early_cold_delete(self):
        self.assertEqual(m.early_cold_delete_billable_days(30), 60)
        self.assertEqual(m.early_cold_delete_billable_days(120), 0)

    def test_quantities_formula(self):
        r = {"name": "x", "type": "EFS", "source_size_gb": 100, "daily_change_fraction": 0.1, "monthly_unique_fraction": 1.0, "cold_capable": True, "pitr_log_gb_per_day": 0}
        q = m.resource_quantities(r, INPUTS["retention"])
        self.assertAlmostEqual(q["primary_vault"]["warm_gb_month"], 100 + 100 * 0.1 * 34 + 3 * 100)
        self.assertAlmostEqual(q["primary_vault"]["cold_gb_month"], 10 * 100)
        self.assertEqual(q["dr_vault"], q["primary_vault"])
        self.assertAlmostEqual(q["cross_region_transfer_gb_month"], 100 * 0.1 * 30.4 + 100)

    def test_null_prices_give_null_costs(self):
        out = m.run(INPUTS)
        self.assertEqual(out["label"], "ESTIMATE")
        self.assertTrue(all(l["estimate_cost"] is None for l in out["lines"]))
        self.assertIsNone(out["estimate_total_known"])
        self.assertTrue(out["inputs_placeholder"])

    def test_filled_price_is_used(self):
        i = copy.deepcopy(INPUTS)
        i["prices"]["kms_key_month"] = 2.0  # test-only value, not a real price
        out = m.run(i)
        kms = [l for l in out["lines"] if l["driver"] == "KMS: vault CMKs"][0]
        self.assertEqual(kms["estimate_cost"], 4.0)

    def test_shipped_inputs_have_no_prices(self):
        p = INPUTS["prices"]
        flat = [v for k, v in p.items() if k not in ("references", "label", "currency", "$comment") and not isinstance(v, dict)]
        flat += [v for d in p.values() if isinstance(d, dict) for v in d.values()]
        self.assertTrue(all(v is None for v in flat), "shipped inputs must not contain unverified prices")


if __name__ == "__main__":
    unittest.main()
