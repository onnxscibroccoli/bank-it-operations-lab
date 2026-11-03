"""Invariant + regression tests for the acceptance gate.

I1: a required FAIL or UNKNOWN can never yield ACCEPTED.     I2: a change of source commit invalidates prior acceptance.
C1-C4: regressions for reports/independent/chatgpt/acceptance-181bcdd-review.md (PR #27).
ACCEPTED(dir, sha) <=> `decide.py DIR --sha SHA` (= `verify_results.py DIR --accept-for SHA`) exits 0.
Output dirs are fabricated in the exact run.sh layout so each test isolates one property. Stdlib only, offline.
"""
import hashlib, importlib.util, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path

ACC = Path(__file__).resolve().parents[1]
VR, DECIDE, INV = ACC / "verify_results.py", ACC / "decide.py", ACC / "required-checks.v1.json"
A, B = "a" * 40, "b" * 40
inv = json.loads(INV.read_text())
spec = importlib.util.spec_from_file_location("vr", VR); vr = importlib.util.module_from_spec(spec); spec.loader.exec_module(vr)
HDR = ["check_id", "required", "verdict", "exit_code", "detail", "log"]


def default_rows(sha):
    rows = []
    for c in inv["checks"]:
        detail = {"CHECKOUT": f"worktree HEAD == {sha}", "SOURCE-BINDING": f"verdicts bound to {sha}: HEAD unchanged, worktree clean"}.get(c["id"], c["title"])
        rows.append(dict(check_id=c["id"], required="yes", verdict="PASS", exit_code="1" if c["kind"] == "defect" else "0", detail=detail, log=f"logs/{c['id']}.log"))
    for g in inv["groups"]:
        for n in range(1, g["min"] + 1):
            i = g["pattern"].replace("^", "").replace("$", "").replace("([0-9]+)", str(n)).replace("\\.", ".")
            rows.append(dict(check_id=i, required="yes", verdict="PASS", exit_code="0", detail=g["title"], log=f"logs/{i}.log"))
    rows += [dict(check_id="REPORT-INTEGRATION", required="no", verdict="PASS", exit_code="0", detail="present", log="-")]
    return rows


def build(d, sha=A, mutate=None, json_mutate=None, injected=None, json_sha=None, overall=None):
    d = Path(d); (d / "logs").mkdir(parents=True)
    rows = default_rows(sha)
    if mutate: rows = mutate(rows)
    exp = {c["id"]: c.get("expect_output") for c in inv["checks"]}
    for r in rows:
        if r["log"] in ("", "-"): continue
        if exp.get(r["check_id"]):
            body = f"# reason_regex: {re.escape(exp[r['check_id']])}\n{exp[r['check_id']] if r['exit_code'] != '0' else 'accepted'}\n"
        else:
            body = "output\n"
        (d / r["log"]).write_text(f"# check: {r['check_id']}\n{body}# exit_code: {r['exit_code']}\n")
    (d / "results.tsv").write_text("\t".join(HDR) + "\n" + "".join("\t".join(r[h] for h in HDR) + "\n" for r in rows))
    g = vr.gate(rows)
    j = {"target_sha": json_sha or sha, "injected_defect": injected, "overall": overall or g, **vr.counters(rows),
         "inventory_version": inv["version"], "inventory_sha256": vr.sha256_file(INV),
         "execution_state": {"PASS": "EXECUTION_PASS", "FAIL": "EXECUTION_FAIL"}.get(g, "EXECUTION_UNKNOWN"),
         "checks": [dict(r) for r in rows]}
    if json_mutate: json_mutate(j)
    (d / "results.json").write_text(json.dumps(j))
    (d / "SUMMARY.md").write_text("x\n")
    seal(d)
    return d


def seal(d):
    files = sorted(p for p in Path(d).rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (Path(d) / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(d)}\n" for p in files))


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


def verify(d, *extra): return run(VR, d, *extra).returncode
def decide(d, sha=A, reviews=None, tmp=None):
    args = [DECIDE, d, "--sha", sha]
    if reviews is not None:
        p = Path(tmp) / "reviews.json"; p.write_text(json.dumps(reviews)); args += ["--reviews", p]
    return run(*args)


def review(verdict="concur", commit=A, who="independent-reviewer (not the recorder)"):
    return [{"reviewer": who, "reviewed_commit": commit, "verdict": verdict, "finding": "re-ran and compared", "date": "2026-10-28"}]


def setv(i, verdict, code=None, required=None):
    def m(rows):
        for r in rows:
            if r["check_id"] == i:
                r["verdict"] = verdict
                if code is not None: r["exit_code"] = code
                if required is not None: r["required"] = required
                if verdict == "UNKNOWN" and code is None: r["exit_code"], r["log"] = "-", "-"
        return rows
    return m


class Base(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); self.d = Path(self.t.name) / "out"
    def tearDown(self):
        self.t.cleanup()


class Control(Base):
    def test_full_pass_is_consistent_and_execution_pass(self):
        build(self.d); self.assertEqual(verify(self.d), 0); self.assertEqual(verify(self.d, "--execution-pass-for", A), 0)


class C1Inventory(Base):
    def test_review_probe_arbitrary_single_row_rejected(self):
        # exact reproduction from the review: one ARBITRARY required PASS row with matching log/hash
        p = self.d; p.mkdir()
        row = dict(check_id="ARBITRARY", required="yes", verdict="PASS", exit_code="0", detail="probe", log="check.log")
        (p / "check.log").write_text("# exit_code: 0\n")
        (p / "results.tsv").write_text("\t".join(HDR) + "\n" + "\t".join(row[k] for k in HDR) + "\n")
        (p / "results.json").write_text(json.dumps(dict(overall="PASS", target_sha="0" * 40, checks=[dict(row)])))
        seal(p); self.assertEqual(verify(p), 1)
    def test_omitted_required_check_rejected(self):
        build(self.d, mutate=lambda rs: [r for r in rs if r["check_id"] != "PG-01"]); self.assertEqual(verify(self.d), 1)
    def test_downgraded_required_flag_rejected(self):
        build(self.d, mutate=setv("ENTRA-02", "FAIL", "1", required="no")); self.assertEqual(verify(self.d), 1)
    def test_arbitrary_replacement_rejected(self):
        build(self.d, mutate=lambda rs: [dict(r, check_id="ARBITRARY", log="logs/ARBITRARY.log") if r["check_id"] == "AWS-03" else r for r in rs])
        self.assertEqual(verify(self.d), 1)
    def test_duplicate_id_rejected(self):
        build(self.d, mutate=lambda rs: rs + [dict(rs[1])]); self.assertEqual(verify(self.d), 1)
    def test_dynamic_group_gap_and_shortfall_rejected(self):
        build(self.d, mutate=lambda rs: [r for r in rs if r["check_id"] != "HASH-5"]); self.assertEqual(verify(self.d), 1)
    def test_inventory_hash_mismatch_rejected(self):
        build(self.d, json_mutate=lambda j: j.update(inventory_sha256="0" * 64)); self.assertEqual(verify(self.d), 1)


class C2Info(Base):
    def test_review_probe_gate_required_info(self):
        self.assertEqual(vr.gate([dict(check_id="mandatory", required="yes", verdict="INFO")]), "FAIL")
    def test_required_info_in_full_bundle_rejected(self):
        build(self.d, mutate=setv("AWS-02", "INFO")); self.assertNotEqual(verify(self.d, "--execution-pass-for", A), 0)
    def test_advisory_info_not_allowed_where_inventory_forbids(self):
        build(self.d, mutate=setv("REPORT-INTEGRATION", "INFO")); self.assertEqual(verify(self.d), 1)
    def test_exhaustive_gate_selftest(self):
        self.assertEqual(run(VR, "--selftest").returncode, 0)


class C3Records(Base):
    def test_review_probe_json_disagrees_minimal(self):
        p = self.d; p.mkdir()
        row = dict(check_id="AWS-02", required="yes", verdict="PASS", exit_code="0", detail="probe", log="check.log")
        (p / "check.log").write_text("# exit_code: 0\n")
        (p / "results.tsv").write_text("\t".join(HDR) + "\n" + "\t".join(row[k] for k in HDR) + "\n")
        (p / "results.json").write_text(json.dumps(dict(overall="PASS", target_sha="0" * 40, checks=[dict(row, verdict="FAIL", exit_code="1")])))
        seal(p); self.assertEqual(verify(p), 1)
    def test_json_record_disagrees_in_full_bundle_rejected(self):
        def jm(j):
            for c in j["checks"]:
                if c["check_id"] == "AWS-02": c.update(verdict="FAIL", exit_code="1")
        build(self.d, json_mutate=jm); self.assertEqual(verify(self.d), 1)
    def test_counter_disagrees_rejected(self):
        build(self.d, json_mutate=lambda j: j.update(fail=[])) ; self.assertEqual(verify(self.d), 0)  # control: equal
        self.t.cleanup(); self.setUp()
        build(self.d, json_mutate=lambda j: j.update(**{"pass": j["pass"] + 1})); self.assertEqual(verify(self.d), 1)
    def test_untyped_field_rejected(self):
        build(self.d, json_mutate=lambda j: j["checks"][0].update(exit_code=0)); self.assertEqual(verify(self.d), 1)
    def test_forged_overall_rejected(self):
        build(self.d, mutate=setv("ENTRA-01", "FAIL", "1"), overall="PASS"); self.assertEqual(verify(self.d), 1)
    def test_verdict_flipped_against_log_rejected(self):
        build(self.d); log = self.d / "logs" / "ENTRA-01.log"; log.write_text(log.read_text().replace("# exit_code: 0", "# exit_code: 1")); seal(self.d)
        self.assertEqual(verify(self.d), 1)
    def test_expected_commit_argument_binds(self):
        build(self.d); self.assertEqual(verify(self.d, "--sha", A), 0); self.assertEqual(verify(self.d, "--sha", B), 1)


class C4Decision(Base):
    def test_execution_pass_without_review_is_review_pending_not_accepted(self):
        build(self.d); p = decide(self.d)
        self.assertEqual(p.returncode, 5, p.stdout); self.assertIn("decision: REVIEW_PENDING", p.stdout)
        self.assertEqual(run(VR, self.d, "--accept-for", A).returncode, 5)
    def test_concur_review_of_tested_commit_is_the_only_path_to_accepted(self):
        build(self.d); p = decide(self.d, reviews=review(), tmp=self.t.name); self.assertEqual(p.returncode, 0, p.stdout)
    def test_dispute_blocks(self):
        build(self.d); self.assertEqual(decide(self.d, reviews=review("dispute"), tmp=self.t.name).returncode, 6)
    def test_self_review_invalid(self):
        build(self.d); self.assertEqual(decide(self.d, reviews=review(who="worker-d scripts/acceptance/run.sh (recorder)"), tmp=self.t.name).returncode, 1)


class I1(Base):
    def test_required_fail_never_accepted_even_with_concur(self):
        build(self.d, mutate=setv("ENTRA-02", "FAIL", "1")); self.assertEqual(decide(self.d, reviews=review(), tmp=self.t.name).returncode, 1)
    def test_required_unknown_never_accepted_even_with_concur(self):
        build(self.d, mutate=setv("PG-01", "UNKNOWN")); self.assertEqual(decide(self.d, reviews=review(), tmp=self.t.name).returncode, 2)
    def test_defect_injection_run_never_accepted(self):
        build(self.d, injected="entra-mfa-report-only"); self.assertNotEqual(decide(self.d, reviews=review(), tmp=self.t.name).returncode, 0)
    def test_tampered_output_rejected(self):
        build(self.d); (self.d / "results.tsv").write_text((self.d / "results.tsv").read_text() + "\n")
        self.assertEqual(decide(self.d, reviews=review(), tmp=self.t.name).returncode, 1)


class I2(Base):
    def test_acceptance_does_not_transfer_to_another_commit(self):
        build(self.d, sha=A)
        self.assertEqual(decide(self.d, A, reviews=review(commit=A), tmp=self.t.name).returncode, 0)
        self.assertEqual(decide(self.d, B, reviews=review(commit=B), tmp=self.t.name).returncode, 1)
    def test_review_of_previous_commit_does_not_carry_over(self):
        build(self.d, sha=B); self.assertEqual(decide(self.d, B, reviews=review(commit=A), tmp=self.t.name).returncode, 1)
    def test_rebinding_results_json_to_new_commit_rejected(self):
        build(self.d, sha=A, json_sha=B); self.assertEqual(verify(self.d), 1)
    def test_dirty_or_moved_worktree_not_accepted(self):
        build(self.d, mutate=setv("SOURCE-BINDING", "FAIL", "1")); self.assertEqual(decide(self.d, reviews=review(), tmp=self.t.name).returncode, 1)
    def test_short_or_symbolic_sha_rejected(self):
        build(self.d, json_sha="HEAD"); self.assertEqual(verify(self.d), 1)


if __name__ == "__main__":
    unittest.main()
