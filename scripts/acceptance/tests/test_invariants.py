"""Invariant tests for the acceptance gate (reports/ACCEPTANCE_INVARIANT_ASSURANCE.md).

I1: a required FAIL or UNKNOWN can never yield ACCEPTED.
I2: a change to the source commit invalidates any prior acceptance.
ACCEPTED(dir, sha) is `verify_results.py DIR --accept-for SHA` exiting 0. Output dirs are fabricated in the
run.sh layout so each test isolates one property; stdlib only, no network, no repo mutation.
"""
import hashlib, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

VR = Path(__file__).resolve().parents[1] / "verify_results.py"
A, B = "a" * 40, "b" * 40
BASE = ["CHECKOUT", "AWS-00", "AWS-01", "PG-01", "ENTRA-01", "ACC-A-01", "ACC-B-01", "ACC-C-01", "HASH-1", "DEFECT-HASH", "SOURCE-BINDING"]


def build(d, sha=A, verdicts=None, drop=(), overall=None, injected=None, json_sha=None):
    """Write a run.sh-shaped output dir. verdicts: {id: (verdict, exit)}; defaults to all PASS/0."""
    d = Path(d); (d / "logs").mkdir(parents=True)
    rows = []
    for i in BASE:
        if i in drop: continue
        v, rc = (verdicts or {}).get(i, ("PASS", 0))
        detail = {"CHECKOUT": f"worktree HEAD == {sha}", "SOURCE-BINDING": f"verdicts bound to {sha}: HEAD unchanged, worktree clean"}.get(i, i)
        if v == "UNKNOWN":
            rows.append(dict(check_id=i, required="yes", verdict=v, exit_code="-", detail=detail, log="-")); continue
        if i.startswith("DEFECT-"):
            rc = 1 if v == "PASS" else 0
            body = f"# reason_regex: sha256 mismatch\n{'sha256 mismatch for x' if rc else 'HASHES OK'}\n"
        else:
            body = "output\n"
        (d / "logs" / f"{i}.log").write_text(f"# check: {i}\n{body}# exit_code: {rc}\n")
        rows.append(dict(check_id=i, required="yes", verdict=v, exit_code=str(rc), detail=detail, log=f"logs/{i}.log"))
    req = [r for r in rows if r["required"] == "yes"]
    calc = "FAIL" if any(r["verdict"] == "FAIL" for r in req) else ("UNKNOWN" if any(r["verdict"] == "UNKNOWN" for r in req) else "PASS")
    hdr = ["check_id", "required", "verdict", "exit_code", "detail", "log"]
    (d / "results.tsv").write_text("\t".join(hdr) + "\n" + "".join("\t".join(r[h] for h in hdr) + "\n" for r in rows))
    (d / "results.json").write_text(json.dumps({"target_sha": json_sha or sha, "injected_defect": injected,
                                                 "overall": overall or calc, "checks": rows}))
    (d / "SUMMARY.md").write_text("x\n")
    seal(d)
    return d


def seal(d):
    files = sorted(p for p in Path(d).rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (Path(d) / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(d)}\n" for p in files))


def vr(*args):
    return subprocess.run([sys.executable, str(VR), *map(str, args)], capture_output=True, text=True).returncode


class Invariants(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); self.d = Path(self.t.name) / "out"

    def tearDown(self):
        self.t.cleanup()

    # control: the predicate can say yes at all
    def test_control_all_pass_is_accepted_for_its_sha(self):
        build(self.d); self.assertEqual(vr(self.d), 0); self.assertEqual(vr(self.d, "--accept-for", A), 0)

    # ---- I1
    def test_I1_gate_exhaustive_selftest(self):
        self.assertEqual(vr("--selftest"), 0)

    def test_I1_required_fail_not_accepted(self):
        build(self.d, verdicts={"ENTRA-01": ("FAIL", 1)}); self.assertEqual(vr(self.d, "--accept-for", A), 3)

    def test_I1_required_unknown_not_accepted(self):
        build(self.d, verdicts={"PG-01": ("UNKNOWN", None)}); self.assertEqual(vr(self.d, "--accept-for", A), 3)

    def test_I1_forged_overall_pass_over_required_fail_rejected_even_if_resealed(self):
        build(self.d, verdicts={"ENTRA-01": ("FAIL", 1)}, overall="PASS")
        self.assertEqual(vr(self.d), 1); self.assertEqual(vr(self.d, "--accept-for", A), 1)

    def test_I1_verdict_flipped_against_log_rejected(self):
        build(self.d)
        log = self.d / "logs" / "ENTRA-01.log"; log.write_text(log.read_text().replace("# exit_code: 0", "# exit_code: 1")); seal(self.d)
        self.assertEqual(vr(self.d, "--accept-for", A), 1)

    def test_I1_silently_skipped_required_check_rejected(self):
        build(self.d, drop=("PG-01",)); self.assertEqual(vr(self.d, "--accept-for", A), 1)

    def test_I1_defect_injection_run_never_accepted(self):
        build(self.d, injected="entra-mfa-report-only"); self.assertEqual(vr(self.d, "--accept-for", A), 3)

    def test_I1_tampered_output_rejected(self):
        build(self.d); (self.d / "results.tsv").write_text((self.d / "results.tsv").read_text() + "\n")
        self.assertEqual(vr(self.d, "--accept-for", A), 1)

    # ---- I2
    def test_I2_acceptance_does_not_transfer_to_another_commit(self):
        build(self.d, sha=A); self.assertEqual(vr(self.d, "--accept-for", A), 0); self.assertEqual(vr(self.d, "--accept-for", B), 3)

    def test_I2_rebinding_results_json_to_new_commit_rejected(self):
        build(self.d, sha=A, json_sha=B)   # results.json claims B, CHECKOUT/SOURCE-BINDING logs say A
        self.assertEqual(vr(self.d), 1); self.assertEqual(vr(self.d, "--accept-for", B), 1)

    def test_I2_dirty_or_moved_worktree_not_accepted(self):
        build(self.d, verdicts={"SOURCE-BINDING": ("FAIL", 1)}); self.assertEqual(vr(self.d, "--accept-for", A), 3)

    def test_I2_short_or_symbolic_sha_rejected(self):
        build(self.d, sha=A, json_sha="HEAD"); self.assertEqual(vr(self.d), 1)


if __name__ == "__main__":
    unittest.main()
