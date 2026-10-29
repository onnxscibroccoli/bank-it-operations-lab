"""Regression tests for merge_eligibility.py SHA binding (PR #27 checkpoint pt15u).

A MET acceptance condition must be bound to the exact run identity (candidate, base, tested merge), each as a full
40-hex SHA. Missing, abbreviated, wrong, non-hex and candidate-vs-merge mix-ups must all be NOT ELIGIBLE, and
AC3 COMPUTED_AT_RUNTIME must only hold for a valid merge identity whose required checks all succeeded in this run."""
import io, json, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import merge_eligibility as me  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
REG = json.loads((ROOT / "coordination/modules.json").read_text())
CAND = "08cdf11aecfdae56867f21cbec33e7505c8ce8a9"
BASE = "7f50348bf1370381615eaed91c02607fe41de2f5"
MERGE = "771045ee413f7550cd0279db06915dddba548dfd"
IDENT = {"valid": True, "errors": [], "kind": "merge", "candidate_sha": CAND, "base_sha": BASE, "tested_sha": MERGE,
         "run_id": "1", "run_attempt": "1", "event": "pull_request"}
BIND = {"candidate_sha": CAND, "base_sha": BASE, "tested_sha": MERGE}


def all_green():
    return {j: {"result": "success", "outputs": {k: "PASS" for k in (REG.get("required_gate_outputs") or {}).get(j, [])}}
            for j in REG["required_gate_jobs"] + ["final-summary"]}


def met(binding=BIND, evidence="https://example.invalid/run/1", **extra):
    c = {"status": "MET", "evidence": evidence}
    if binding is not None:
        c["met_for"] = binding
    c.update(extra)
    return c


def tasks(ac_over):
    conds = [dict({"id": ac}, **met()) for ac in ("AC1", "AC2", "AC4", "AC5")]
    conds += [{"id": "AC3", "status": "COMPUTED_AT_RUNTIME"}, {"id": "AC6", "status": "UNMET"}]
    conds = [dict({"id": c["id"]}, **ac_over[c["id"]]) if c["id"] in ac_over else c for c in conds]
    return {"acceptance_conditions_for_main": {"conditions": conds}}


def run(ac_over=None, ident=IDENT, needs=None, extra=()):
    with tempfile.TemporaryDirectory() as d:
        tp = Path(d) / "tasks.json"
        tp.write_text(json.dumps(tasks(ac_over or {})))
        args = ["--tasks", str(tp), *extra]
        if ident is not None:
            ip = Path(d) / "id.json"
            ip.write_text(json.dumps(ident))
            args += ["--identity", str(ip)]
        env = {"NEEDS_JSON": json.dumps(all_green() if needs is None else needs)}
        with mock.patch.dict(os.environ, env), redirect_stdout(io.StringIO()) as out:
            rc = me.main(args)
    return rc, out.getvalue()


class Binding(unittest.TestCase):
    def test_control_everything_bound_and_green_is_eligible(self):
        rc, out = run()
        self.assertEqual(rc, 0, out)
        self.assertIn("AC3: MET_AT_RUNTIME", out)

    def test_met_without_met_for_is_not_eligible(self):
        rc, out = run({"AC2": met(binding=None)})
        self.assertEqual(rc, 1)
        self.assertIn("naked MET", out)

    def test_legacy_met_for_sha_alone_is_not_eligible(self):
        rc, out = run({"AC2": met(binding=None, met_for_sha=CAND)})
        self.assertEqual(rc, 1)
        self.assertIn("legacy met_for_sha", out)

    def test_missing_field_is_not_eligible(self):
        for k in BIND:
            b = dict(BIND); b.pop(k)
            with self.subTest(field=k):
                rc, out = run({"AC4": met(b)})
                self.assertEqual(rc, 1)
                self.assertIn(f"met_for.{k} missing", out)

    def test_abbreviated_sha_is_not_eligible(self):
        for n in (7, 12, 39):
            with self.subTest(length=n):
                rc, out = run({"AC4": met(dict(BIND, candidate_sha=CAND[:n]))})
                self.assertEqual(rc, 1)
                self.assertIn("not a full 40-hex SHA", out)

    def test_non_hex_sha_is_not_eligible(self):
        for bad in ("g" * 40, CAND[:-1] + "z", " " * 40, 12345, CAND + "0"):
            with self.subTest(value=bad):
                rc, out = run({"AC4": met(dict(BIND, tested_sha=bad))})
                self.assertEqual(rc, 1)

    def test_uppercase_is_normalized_not_rejected(self):
        rc, out = run({"AC4": met({k: v.upper() for k, v in BIND.items()})})
        self.assertEqual(rc, 0, out)

    def test_wrong_sha_is_not_eligible(self):
        rc, out = run({"AC5": met(dict(BIND, candidate_sha="7fe6d7281316190d9b39e35a448fb9fb81b92d50"))})
        self.assertEqual(rc, 1)
        self.assertIn("not this run's", out)

    def test_candidate_vs_merge_mixup_is_reported(self):
        rc, out = run({"AC5": met(dict(BIND, candidate_sha=MERGE, tested_sha=CAND))})
        self.assertEqual(rc, 1)
        self.assertIn("mixup", out)

    def test_met_without_evidence_is_not_eligible(self):
        rc, out = run({"AC1": met(evidence="")})
        self.assertEqual(rc, 1)

    def test_runtime_status_only_for_ac3(self):
        rc, out = run({"AC2": {"status": "COMPUTED_AT_RUNTIME"}})
        self.assertEqual(rc, 1)
        self.assertIn("not allowed for AC2", out)

    def test_ac3_runtime_needs_merge_identity(self):
        rc, out = run(ident=dict(IDENT, kind="direct", tested_sha=CAND, base_sha=None))
        self.assertEqual(rc, 1)
        self.assertIn("not tested as a merge", out)

    def test_ac3_runtime_needs_valid_identity(self):
        rc, out = run(ident=dict(IDENT, valid=False, errors=["synthetic merge second parent mismatch"]))
        self.assertEqual(rc, 1)
        self.assertIn("identity INVALID", out)

    def test_ac3_runtime_needs_identity(self):
        rc, out = run(ident=None)
        self.assertEqual(rc, 1)
        self.assertIn("run identity not available", out)

    def test_ac3_runtime_needs_all_required_checks(self):
        n = all_green(); n["incident-fresh-run"]["outputs"]["recovery"] = "NOT_EXECUTED"
        rc, out = run(needs=n)
        self.assertEqual(rc, 1)
        self.assertIn("AC3: UNMET", out)

    def test_ac3_naked_met_in_tasks_is_rejected(self):
        rc, out = run({"AC3": {"status": "MET", "met_for_sha": CAND}})
        self.assertEqual(rc, 1)

    def test_lint_flags_naked_met(self):
        with tempfile.TemporaryDirectory() as d:
            tp = Path(d) / "t.json"
            tp.write_text(json.dumps(tasks({"AC2": met(binding=None)})))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(me.main(["--tasks", str(tp), "--lint-tasks"]), 1)

    def test_lint_passes_repo_tasks(self):
        with redirect_stdout(io.StringIO()) as out:
            rc = me.main(["--lint-tasks"])
        self.assertEqual(rc, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
