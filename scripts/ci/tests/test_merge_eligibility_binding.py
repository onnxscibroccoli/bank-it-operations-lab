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


AUTHOR = "onnxscibroccoli"
REVIEWER = "independent-reviewer"
OWNER = "ian-separate-owner"   # O-5: an owner identity distinct from the PR author / shared account
CONFIG = {"owner_logins": [OWNER], "owner_required_permission": ["admin"], "reviewer_allowlist": [REVIEWER],
          "reviewer_required_permission": ["admin", "maintain", "write"], "decision_pr": 7, "decision_header": "ACCEPTANCE-ATTESTATION v2"}


RUN = "40800364073"
GATE_JOBS = [{"name": n, "conclusion": "success"} for n in ("module-registry", "aws-cdk / synth-and-test", "final-summary")]


def gate_run(head=CAND, name="integration-gate", path=".github/workflows/integration-gate.yml", status="completed",
             conclusion="failure", jobs=None):
    """An integration-gate run as fetched: everything green, merge-eligibility failed closed (NOT ELIGIBLE)."""
    return {"head_sha": head, "name": name, "path": path, "status": status, "conclusion": conclusion,
            "jobs": GATE_JOBS + [{"name": "merge-eligibility", "conclusion": "failure"}] if jobs is None else jobs}


GATE_TRUST_OK = {"status": "VERIFIED", "reasons": []}


def attestation(login, criterion, decision, cand=CAND, main=BASE, tested=(MERGE,), run=RUN, cid=100,
                at="2026-10-28T23:10:00Z", edited=False, extra=(), evidence="https://github.com/o/r/actions/runs/40800364073"):
    lines = ["ACCEPTANCE-ATTESTATION v2", f"candidate: {cand}", f"main: {main}", "tested_merge: " + " ".join(tested),
             f"workflow_run: {run}", f"criterion: {criterion}", f"decision: {decision}", *extra, f"evidence: {evidence}"]
    return {"id": cid, "user": {"login": login}, "created_at": at, "updated_at": "2026-10-28T23:59:00Z" if edited else at,
            "body": "\n".join(lines)}


def decision_comment(login, lines, cand=CAND, cid=100, at="2026-10-28T23:10:00Z", edited=False):  # legacy v1 (ignored by the gate)
    return {"id": cid, "user": {"login": login}, "created_at": at, "updated_at": "2026-10-28T23:59:00Z" if edited else at,
            "body": "ACCEPTANCE-DECISION v1\ncandidate: " + cand + "\n" + "\n".join(lines)}


APPROVED_REVIEWS = {"ok": True, "pr": 7, "pr_author": AUTHOR, "head_sha": CAND, "base_ref": "main",
                    "reviews": [{"id": 1, "user": {"login": REVIEWER}, "state": "APPROVED", "commit_id": CAND,
                                 "submitted_at": "2026-10-28T23:00:00Z"}],
                    "comments_ok": True,
                    "comments": [attestation(REVIEWER, "AC4", "ACCEPT", cid=101), attestation(REVIEWER, "AC5", "ACCEPT", cid=102)],
                    "runs": {RUN: gate_run()},
                    "permissions": {AUTHOR: {"permission": "admin", "role_name": "admin"}, OWNER: {"permission": "admin", "role_name": "admin"}, REVIEWER: {"permission": "write", "role_name": "write"}}}
CLEAN_EXC = {"applied": [], "unapproved": [], "errors": [], "blocking_user_action": False}


def tasks(ac_over):
    conds = [{"id": ac, "status": "COMPUTED_AT_RUNTIME"} for ac in ("AC1", "AC2", "AC3", "AC4", "AC5")] + [{"id": "AC6", "status": "UNMET"}]
    conds = [dict({"id": c["id"]}, **ac_over[c["id"]]) if c["id"] in ac_over else c for c in conds]
    return {"acceptance_conditions_for_main": {"conditions": conds}}


def run(ac_over=None, ident=IDENT, needs=None, extra=(), reviews=APPROVED_REVIEWS, exc=CLEAN_EXC, config=CONFIG, gate_trust=GATE_TRUST_OK):
    with tempfile.TemporaryDirectory() as d:
        tp = Path(d) / "tasks.json"
        tp.write_text(json.dumps(tasks(ac_over or {})))
        args = ["--tasks", str(tp), *extra]
        if reviews is not None:
            (Path(d) / "rv.json").write_text(json.dumps(reviews)); args += ["--reviews", str(Path(d) / "rv.json")]
        if config is not None:
            (Path(d) / "cfg.json").write_text(json.dumps(config)); args += ["--config", str(Path(d) / "cfg.json")]
        if gate_trust is not None:
            (Path(d) / "gt.json").write_text(json.dumps(gate_trust)); args += ["--gate-trust", str(Path(d) / "gt.json")]
        if exc is not None:
            (Path(d) / "exc.json").write_text(json.dumps(exc)); args += ["--exceptions", str(Path(d) / "exc.json")]
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
        # in-tree MET is never accepted any more (PR #31 F6); the binding itself must still normalize case
        self.assertEqual(me.binding_problems("AC4", met({k: v.upper() for k, v in BIND.items()}), IDENT), [])
        rc, out = run({"AC4": met({k: v.upper() for k, v in BIND.items()})})
        self.assertEqual(rc, 1)
        self.assertIn("AC4: MET in tasks.json is self-asserted", out)

    def test_wrong_sha_is_not_eligible(self):
        rc, out = run({"AC5": met(dict(BIND, candidate_sha="7fe6d7281316190d9b39e35a448fb9fb81b92d50"))})
        self.assertEqual(rc, 1)
        self.assertIn("not this run's", out)

    def test_candidate_vs_merge_mixup_is_reported(self):
        rc, out = run({"AC5": met(dict(BIND, candidate_sha=MERGE, tested_sha=CAND))})
        self.assertEqual(rc, 1)
        self.assertIn("mixup", out)

    def test_met_without_evidence_is_not_eligible(self):
        rc, out = run({"AC2": met(evidence="")})
        self.assertEqual(rc, 1)

    def test_runtime_status_needs_runtime_evidence(self):
        # COMPUTED_AT_RUNTIME is allowed for AC1-AC5 now, but without runtime evidence nothing is met
        rc, out = run({"AC2": {"status": "COMPUTED_AT_RUNTIME"}}, reviews=None)
        self.assertEqual(rc, 1)
        self.assertIn("runtime evidence not fetched", out)

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
