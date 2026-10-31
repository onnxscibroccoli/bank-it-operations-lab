"""Negative tests for scripts/ci/check_plan_only.py: every violation must fail; a valid record must pass."""
import copy, json, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_plan_only as cpo  # noqa: E402

GOOD = {"tool": "t", "mode": "offline-synthetic", "mutationsExecuted": 0,
        "scenarios": [{"id": "S1", "plan": [{"action": "a", "mode": "PLAN_ONLY", "executed": False},
                                            {"action": "b", "mode": "PLAN_ONLY", "executed": False}]}]}


def run_on(obj, min_steps=1, raw=None):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "r.json"
        p.write_text(raw if raw is not None else json.dumps(obj))
        return cpo.main(["report", str(p), "--min-plan-steps", str(min_steps)])


def mutate(fn):
    o = copy.deepcopy(GOOD)
    fn(o)
    return o


class PlanOnly(unittest.TestCase):
    def test_valid_record_passes(self):
        self.assertEqual(run_on(GOOD), 0)

    def test_step_mode_not_plan_only_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o["scenarios"][0]["plan"][1].update(mode="EXECUTE"))), 1)

    def test_step_executed_true_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o["scenarios"][0]["plan"][0].update(executed=True))), 1)

    def test_step_executed_string_false_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o["scenarios"][0]["plan"][0].update(executed="false"))), 1)

    def test_step_executed_missing_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o["scenarios"][0]["plan"][0].pop("executed"))), 1)

    def test_mutations_executed_nonzero_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o.update(mutationsExecuted=1))), 1)

    def test_mutations_executed_bool_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o.update(mutationsExecuted=False))), 1)

    def test_mutations_executed_missing_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o.pop("mutationsExecuted"))), 1)

    def test_nested_mutations_executed_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o["scenarios"][0].update(mutationsExecuted=3))), 1)

    def test_executed_elsewhere_true_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o["scenarios"][0].update(executed=True))), 1)

    def test_no_plan_steps_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o["scenarios"][0].update(plan=[]))), 1)

    def test_plan_not_list_fails(self):
        self.assertEqual(run_on(mutate(lambda o: o["scenarios"][0].update(plan={"mode": "PLAN_ONLY"}))), 1)

    def test_duplicate_key_is_input_error(self):
        self.assertEqual(run_on(None, raw='{"mutationsExecuted": 0, "mutationsExecuted": 1}'), 2)

    def test_missing_run_files_is_input_error(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(cpo.main(["run", d]), 2)


if __name__ == "__main__":
    unittest.main()
