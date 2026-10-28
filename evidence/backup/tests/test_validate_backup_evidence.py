"""Unit tests (temp dirs only): python3 -m unittest discover -s evidence/backup/tests -v"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import validate_backup_evidence as v  # noqa: E402

REPO = HERE.parents[2]


class Validator(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "evidence" / "backup", self.tmp / "evidence" / "backup", ignore=shutil.ignore_patterns("SHA256SUMS", "__pycache__"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def edit(self, rel, fn):
        p = self.tmp / "evidence" / "backup" / rel
        d = json.loads(p.read_text())
        fn(d)
        p.write_text(json.dumps(d))

    def test_repo_evidence_passes(self):
        self.assertEqual(v.validate(self.tmp), [])

    def test_invented_rto_is_rejected(self):
        self.edit("aws-backup-dr/rto-rpo-observations.json", lambda d: d["scenarios"][0]["observed"].update(rto_minutes=42))
        self.assertTrue(any("has values" in e for e in v.validate(self.tmp)))

    def test_observed_status_flip_is_rejected(self):
        self.edit("aws-backup-dr/rto-rpo-observations.json", lambda d: d["scenarios"][0]["observed"].update(status="EXECUTED_PASS"))
        self.assertTrue(any("must be NOT_EXECUTED" in e for e in v.validate(self.tmp)))

    def test_invented_billing_amount_is_rejected(self):
        self.edit("cost-capacity/actual-billing-observation.json", lambda d: d["lines"][0].update(amount=12.5))
        self.assertTrue(any("has values" in e for e in v.validate(self.tmp)))

    def test_recovery_item_executed_is_rejected(self):
        self.edit("aws-backup-dr/RECOVERY_EXECUTION_STATUS.json", lambda d: d["items"][0].update(status="EXECUTED_PASS", job_id="x"))
        self.assertTrue(v.validate(self.tmp))

    def test_unlabelled_hypothesis_is_rejected(self):
        self.edit("aws-backup-dr/rto-rpo-observations.json", lambda d: d["scenarios"][1]["hypothesis"].update(label="TARGET"))
        self.assertTrue(any("HYPOTHESIS" in e for e in v.validate(self.tmp)))

    def test_estimate_cost_without_price_is_rejected(self):
        self.edit("cost-capacity/estimate-output.json", lambda d: d["lines"][0].update(estimate_cost=1.0))
        self.assertTrue(any("cost without a price" in e for e in v.validate(self.tmp)))

    def test_capacity_value_without_observation_is_rejected(self):
        self.edit("cost-capacity/capacity-observation.template.json", lambda d: d["checks"][0].update(value=99))
        self.assertTrue(any("has values" in e for e in v.validate(self.tmp)))


if __name__ == "__main__":
    unittest.main()
