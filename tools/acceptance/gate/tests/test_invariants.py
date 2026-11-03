"""Invariant + false-acceptance regression tests for the acceptance gate (tools/acceptance/gate).

I1: a required FAIL or UNKNOWN can never yield acceptance.   I2: a change of source commit invalidates prior results.
C1-C4: PR #27 (reports/independent/chatgpt/acceptance-181bcdd-review.md).   R1-R7: PR #29 Lane E review of eb42b23.
FA-*: false-acceptance cases closed in acceptance/integration-v2 (acceptance/INTEGRATION-V2.md, regression table).

Every test builds a REAL temporary git repository (gate + shared contract + a minimal registered tree), commits it,
fabricates a run.sh-layout output bound to that commit, and runs the gate's own CLI as a subprocess. The same tests
can be pointed at an older gate to prove they fail there:
    ACC_GATE_SRC=<old checkout>/scripts/acceptance ACC_GATE_REL=scripts/acceptance python3 -m unittest ...
(see prove_regressions.sh). Stdlib only, offline, no network.
"""
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL_ROOT = HERE.parents[3]                                   # repo that holds schemas/acceptance + evidence/shared
GATE_SRC = Path(os.environ.get("ACC_GATE_SRC", HERE.parent)).resolve()
GATE_REL = os.environ.get("ACC_GATE_REL", "tools/acceptance/gate")
INV_NAME = "required-checks.json" if (GATE_SRC / "required-checks.json").exists() else "required-checks.v1.json"
inv = json.loads((GATE_SRC / INV_NAME).read_text())
HDR = ["check_id", "required", "verdict", "exit_code", "detail", "log"]
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]
DEFAULT_PATHS = ["infra/aws-cdk/", "tests/integration/postgres/", "identity/entra/", "tests/entra/", "tests/acceptance-contract/",
                 "acceptance/modules/", "tools/acceptance/README.md", "scripts/acceptance/", "README.md"]
CANARY = "c" * 40                                             # a commit that does not exist in any test repo


def group(name):
    return next(g for g in inv["groups"] if g["name"] == name)


def gid(g, n):
    return g["pattern"].replace("^", "").replace("$", "").replace("([0-9]+)", str(n)).replace("\\.", ".")


def make_repo(tmp, n_hash=None, n_entra=1, extra=None, untrack=()):
    """A committed tree that satisfies the gate's scope rules. Returns (root, sha, members)."""
    root = Path(tmp) / "repo"
    shutil.copytree(GATE_SRC, root / GATE_REL, ignore=shutil.ignore_patterns("__pycache__", "tests", "*.pyc"))
    shutil.copytree(REAL_ROOT / "schemas" / "acceptance", root / "schemas" / "acceptance", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "evidence" / "shared").mkdir(parents=True)
    for f in (REAL_ROOT / "evidence" / "shared").iterdir():
        if f.is_file() and f.suffix in (".py", ".json"): shutil.copy(f, root / "evidence" / "shared" / f.name)
    paths = set(DEFAULT_PATHS)
    for m in inv.get("scope", {}).get("modules", []): paths.update(m["paths"])
    for pth in paths:
        f = root / pth / "PLACEHOLDER" if pth.endswith("/") else root / pth
        if not f.exists(): f.parent.mkdir(parents=True, exist_ok=True); f.write_text("placeholder\n")
    n_hash = group("HASH")["min"] if n_hash is None else n_hash
    hashes = [f"evidence/b{i:02d}/SHA256SUMS" for i in range(1, n_hash + 1)]
    entras = [f"evidence/entra/runs/run-{i}" for i in range(1, n_entra + 1)]
    for h in hashes: (root / h).parent.mkdir(parents=True, exist_ok=True); (root / h).write_text("")
    for e in entras: (root / e).mkdir(parents=True, exist_ok=True); (root / e / "run.json").write_text("{}\n")
    for rel, body in (extra or {}).items(): (root / rel).parent.mkdir(parents=True, exist_ok=True); (root / rel).write_text(body)
    subprocess.run([*GIT, "init", "-q", str(root)], check=True)
    subprocess.run([*GIT, "-C", str(root), "add", "-A"], check=True)
    for u in untrack: subprocess.run([*GIT, "-C", str(root), "rm", "-q", "--cached", u], check=True)
    subprocess.run([*GIT, "-C", str(root), "commit", "-q", "-m", "fixture"], check=True)
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    return root, sha, {"HASH": sorted(hashes), "ENTRA-04": sorted(entras)}


def load_vr(root):
    spec = importlib.util.spec_from_file_location(f"vr_{abs(hash(str(root)))}", root / GATE_REL / "verify_results.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def default_rows(sha, members):
    rows = []
    for c in inv["checks"]:
        detail = {"CHECKOUT": f"worktree HEAD == {sha}", "SOURCE-BINDING": f"verdicts bound to {sha}: HEAD unchanged, worktree clean"}.get(c["id"], c["title"])
        rows.append(dict(check_id=c["id"], required="yes", verdict="PASS", exit_code="1" if c["kind"] == "defect" else "0", detail=detail, log=f"logs/{c['id']}.log"))
    for g in inv["groups"]:
        for n, path in enumerate(members[g["name"]], 1):
            i = gid(g, n)
            rows.append(dict(check_id=i, required="yes", verdict="PASS", exit_code="0", detail=f"{g['title']} {path}", log=f"logs/{i}.log"))
    rows += [dict(check_id="REPORT-INTEGRATION", required="no", verdict="PASS", exit_code="0", detail="present", log="-")]
    return rows


def seal(d, skip=lambda p: False):
    d = Path(d)
    files = sorted(p for p in d.rglob("*") if p.is_file() and p.relative_to(d).as_posix() != "SHA256SUMS" and not skip(p.relative_to(d).as_posix()))
    (d / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(d).as_posix()}\n" for p in files))


def build(d, root, sha, members, mutate=None, json_mutate=None, injected=None, json_sha=None, overall=None, provenance="local",
          summary=None, postgres_run=False, seal_skip=lambda p: False):
    vr = load_vr(root)
    d = Path(d); (d / "logs").mkdir(parents=True)
    rows = default_rows(sha, members)
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
    es = vr.execution_state(rows, injected) if hasattr(vr, "execution_state") else \
        {"PASS": "EXECUTION_PASS", "FAIL": "EXECUTION_FAIL"}.get(g, "EXECUTION_UNKNOWN")
    j = {"target_sha": json_sha or sha, "injected_defect": injected, "overall": overall or g, **vr.counters(rows),
         "inventory_version": inv["version"], "inventory_sha256": vr.sha256_file(root / GATE_REL / INV_NAME),
         "execution_state": es, "checks": [dict(r) for r in rows]}
    if provenance == "local": j["provenance"] = {"kind": "local", "authenticated": False}
    elif isinstance(provenance, dict): j["provenance"] = provenance
    if json_mutate: json_mutate(j)
    (d / "results.json").write_text(json.dumps(j))
    if summary is not None: (d / "SUMMARY.md").write_text(summary)
    elif hasattr(vr, "render_summary"): (d / "SUMMARY.md").write_text(vr.render_summary(j))
    else: (d / "SUMMARY.md").write_text("x\n")
    if postgres_run:
        (d / "postgres-run").mkdir()
        (d / "postgres-run" / "result.txt").write_text("restore PASS\n")
        (d / "postgres-run" / "SHA256SUMS").write_text(f"{hashlib.sha256(b'restore PASS' + bytes([10])).hexdigest()}  result.txt\n")
    seal(d, seal_skip)
    return d


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, timeout=300)


ALL_REQ = [c["contract_id"] for c in inv["checks"]] + [g["contract_id"] for g in inv["groups"]]


def review(sha, verdict="concur", who="independent-reviewer (separate account)", ids=ALL_REQ):
    r = {"reviewer": who, "reviewed_commit": sha, "verdict": verdict, "finding": "re-ran and compared", "date": "2026-11-03"}
    if ids is not None: r["requirement_ids"] = list(ids)
    return [r]


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
    repo_kw = {}

    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); self.tmp = Path(self.t.name)
        self.root, self.sha, self.members = make_repo(self.tmp, **self.repo_kw)
        self.vrp, self.dcp = self.root / GATE_REL / "verify_results.py", self.root / GATE_REL / "decide.py"
        self.d = self.tmp / "out"

    def tearDown(self):
        self.t.cleanup()

    def build(self, **kw):
        kw.setdefault("sha", self.sha); kw.setdefault("members", self.members)
        return build(self.d, self.root, **kw)

    def verify(self, sha=None, *extra):
        return run(self.vrp, self.d, "--sha", sha or self.sha, *extra).returncode

    def decide(self, sha=None, reviews=None):
        args = [self.dcp, self.d, "--sha", sha or self.sha]
        if reviews is not None:
            p = self.tmp / "reviews.json"; p.write_text(json.dumps(reviews)); args += ["--reviews", p]
        return run(*args)


class Control(Base):
    def test_full_pass_is_consistent_execution_pass_and_review_pending(self):
        self.build()
        self.assertEqual(self.verify(), 0)
        self.assertEqual(run(self.vrp, self.d, "--execution-pass-for", self.sha).returncode, 0)
        p = self.decide(); self.assertEqual(p.returncode, 5, p.stdout + p.stderr); self.assertIn("decision: REVIEW_PENDING", p.stdout)


class C1Inventory(Base):
    def test_review_probe_arbitrary_single_row_rejected(self):
        p = self.d; p.mkdir()
        row = dict(check_id="ARBITRARY", required="yes", verdict="PASS", exit_code="0", detail="probe", log="check.log")
        (p / "check.log").write_text("# exit_code: 0\n")
        (p / "results.tsv").write_text("\t".join(HDR) + "\n" + "\t".join(row[k] for k in HDR) + "\n")
        (p / "results.json").write_text(json.dumps(dict(overall="PASS", target_sha=self.sha, checks=[dict(row)])))
        seal(p); self.assertEqual(self.verify(), 1)
    def test_omitted_required_check_rejected(self):
        self.build(mutate=lambda rs: [r for r in rs if r["check_id"] != "PG-01"]); self.assertEqual(self.verify(), 1)
    def test_downgraded_required_flag_rejected(self):
        self.build(mutate=setv("ENTRA-02", "FAIL", "1", required="no")); self.assertEqual(self.verify(), 1)
    def test_arbitrary_replacement_rejected(self):
        self.build(mutate=lambda rs: [dict(r, check_id="ARBITRARY", log="logs/ARBITRARY.log") if r["check_id"] == "AWS-03" else r for r in rs])
        self.assertEqual(self.verify(), 1)
    def test_duplicate_id_rejected(self):
        self.build(mutate=lambda rs: rs + [dict(rs[1])]); self.assertEqual(self.verify(), 1)
    def test_dynamic_group_gap_rejected(self):
        self.build(mutate=lambda rs: [r for r in rs if r["check_id"] != "HASH-5"]); self.assertEqual(self.verify(), 1)
    def test_inventory_hash_mismatch_rejected(self):
        self.build(json_mutate=lambda j: j.update(inventory_sha256="0" * 64)); self.assertEqual(self.verify(), 1)


class C2Info(Base):
    def test_review_probe_gate_required_info(self):
        self.assertEqual(load_vr(self.root).gate([dict(check_id="mandatory", required="yes", verdict="INFO")]), "FAIL")
    def test_required_info_in_full_bundle_rejected(self):
        self.build(mutate=setv("AWS-02", "INFO")); self.assertNotEqual(run(self.vrp, self.d, "--execution-pass-for", self.sha).returncode, 0)
    def test_advisory_info_not_allowed_where_inventory_forbids(self):
        self.build(mutate=setv("REPORT-INTEGRATION", "INFO")); self.assertEqual(self.verify(), 1)
    def test_exhaustive_gate_selftest(self):
        self.assertEqual(run(self.vrp, "--selftest").returncode, 0)


class C3Records(Base):
    def test_review_probe_json_disagrees_minimal(self):
        p = self.d; p.mkdir()
        row = dict(check_id="AWS-02", required="yes", verdict="PASS", exit_code="0", detail="probe", log="check.log")
        (p / "check.log").write_text("# exit_code: 0\n")
        (p / "results.tsv").write_text("\t".join(HDR) + "\n" + "\t".join(row[k] for k in HDR) + "\n")
        (p / "results.json").write_text(json.dumps(dict(overall="PASS", target_sha=self.sha, checks=[dict(row, verdict="FAIL", exit_code="1")])))
        seal(p); self.assertEqual(self.verify(), 1)
    def test_json_record_disagrees_in_full_bundle_rejected(self):
        def jm(j):
            for c in j["checks"]:
                if c["check_id"] == "AWS-02": c.update(verdict="FAIL", exit_code="1")
        self.build(json_mutate=jm); self.assertEqual(self.verify(), 1)
    def test_counter_disagrees_rejected(self):
        self.build(json_mutate=lambda j: j.update(**{"pass": j["pass"] + 1})); self.assertEqual(self.verify(), 1)
    def test_untyped_field_rejected(self):
        self.build(json_mutate=lambda j: j["checks"][0].update(exit_code=0)); self.assertEqual(self.verify(), 1)
    def test_forged_overall_rejected(self):
        self.build(mutate=setv("ENTRA-01", "FAIL", "1"), overall="PASS"); self.assertEqual(self.verify(), 1)
    def test_verdict_flipped_against_log_rejected(self):
        self.build(); log = self.d / "logs" / "ENTRA-01.log"; log.write_text(log.read_text().replace("# exit_code: 0", "# exit_code: 1")); seal(self.d)
        self.assertEqual(self.verify(), 1)
    def test_expected_commit_argument_binds(self):
        self.build(); self.assertEqual(self.verify(), 0); self.assertEqual(self.verify("b" * 40), 1)


class C4Decision(Base):
    def test_dispute_blocks(self):
        self.build(); self.assertEqual(self.decide(reviews=review(self.sha, "dispute")).returncode, 6)
    def test_exact_recorder_string_invalid(self):
        self.build(); self.assertEqual(self.decide(reviews=review(self.sha, who="worker-d tools/acceptance/gate/run.sh (recorder)")).returncode, 1)


class I1(Base):
    def test_required_fail_never_accepted_even_with_concur(self):
        self.build(mutate=setv("ENTRA-02", "FAIL", "1")); self.assertEqual(self.decide(reviews=review(self.sha)).returncode, 1)
    def test_required_unknown_never_accepted_even_with_concur(self):
        self.build(mutate=setv("PG-01", "UNKNOWN")); self.assertEqual(self.decide(reviews=review(self.sha)).returncode, 2)
    def test_defect_injection_run_never_accepted(self):
        self.build(injected="entra-mfa-report-only"); self.assertNotEqual(self.decide(reviews=review(self.sha)).returncode, 0)
    def test_tampered_output_rejected(self):
        self.build(); (self.d / "results.tsv").write_text((self.d / "results.tsv").read_text() + "\n")
        self.assertEqual(self.decide(reviews=review(self.sha)).returncode, 1)


class I2(Base):
    def test_results_do_not_transfer_to_another_commit(self):
        self.build(); self.assertEqual(self.decide("b" * 40, reviews=review("b" * 40)).returncode, 1)
    def test_review_of_previous_commit_does_not_carry_over(self):
        self.build(); self.assertEqual(self.decide(reviews=review("a" * 40)).returncode, 1)
    def test_rebinding_results_json_to_new_commit_rejected(self):
        self.build(json_sha="b" * 40); self.assertEqual(self.verify(), 1)
    def test_dirty_or_moved_worktree_not_accepted(self):
        self.build(mutate=setv("SOURCE-BINDING", "FAIL", "1")); self.assertEqual(self.decide(reviews=review(self.sha)).returncode, 1)
    def test_short_or_symbolic_sha_rejected(self):
        self.build(json_sha="HEAD"); self.assertEqual(self.verify(), 1)


# ------------------------------------------------------------------ v2 false-acceptance regressions (fail on eb42b23)
class FA01NoGateAcceptance(Base):
    """PR #29 R1: a fully concurred bundle (any reviewer string) reached ACCEPTED (exit 0). The gate must never."""
    def test_any_reviewer_string_concur_is_not_accepted(self):
        # the exact R1 probe: full-PASS bundle + one {"reviewer": "anyone", "verdict": "concur"} record
        self.build(); p = self.decide(reviews=review(self.sha, who="anyone", ids=None))
        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr); self.assertNotIn("decision: ACCEPTED", p.stdout)
    def test_accept_for_never_exits_zero(self):
        self.build(); rp = self.tmp / "r.json"; rp.write_text(json.dumps(review(self.sha, ids=None)))
        self.assertNotEqual(run(self.vrp, self.d, "--accept-for", self.sha, "--reviews", rp).returncode, 0)
    def test_scoped_full_concur_is_only_review_concurred_unauthenticated_hardening(self):
        self.build(); p = self.decide(reviews=review(self.sha))
        self.assertEqual(p.returncode, 7, p.stdout + p.stderr); self.assertIn("decision: REVIEW_CONCURRED_UNAUTHENTICATED", p.stdout)


class FA02UnreadableCommit(Base):
    """PR #29 R1/R2: results for a commit that does not exist were accepted (inventory binding failed open)."""
    def test_nonexistent_commit_rejected(self):
        self.build(sha=CANARY); self.assertEqual(self.verify(CANARY), 1)
    def test_nonexistent_commit_never_reaches_a_review_state(self):
        self.build(sha=CANARY); self.assertEqual(self.decide(CANARY, reviews=review(CANARY, ids=None)).returncode, 1)


class FA03InventoryAbsentAtCommit(Base):
    """PR #29 R2: inventory absent at the tested commit -> comparison skipped -> accepted."""
    repo_kw = {"untrack": (f"{GATE_REL}/{INV_NAME}",)}
    def test_inventory_missing_at_commit_rejected(self):
        self.build(); self.assertEqual(self.verify(), 1)


class FA04DerivedGroupMembers(Base):
    """Plan: a group meeting 'min' hid a dropped end member (tree has 18 bundles, run reports 17)."""
    repo_kw = {"n_hash": group("HASH")["min"] + 1}
    def test_dropped_end_member_rejected(self):
        g = group("HASH"); last = gid(g, len(self.members["HASH"]))
        self.build(mutate=lambda rs: [r for r in rs if r["check_id"] != last]); self.assertEqual(self.verify(), 1)
    def test_member_naming_wrong_path_rejected(self):
        self.build(mutate=lambda rs: [dict(r, detail="committed bundle evidence/zz/SHA256SUMS verifies") if r["check_id"] == "HASH-3" else r for r in rs])
        self.assertEqual(self.verify(), 1)
    def test_control_all_members_pass(self):
        self.build(); self.assertEqual(self.verify(), 0)


class FA05UnregisteredPath(Base):
    """Plan: a module present at the commit but registered nowhere was silently outside acceptance."""
    repo_kw = {"extra": {"newmodule/deploy.py": "print('unchecked')\n"}}
    def test_unregistered_tracked_path_rejected(self):
        self.build(); self.assertEqual(self.verify(), 1)


class FA06Provenance(Base):
    """Plan: run provenance (run id, attempt, workflow identity) was not recorded or checked."""
    def test_missing_provenance_rejected(self):
        self.build(provenance=None); self.assertEqual(self.verify(), 1)
    def test_malformed_ci_provenance_rejected(self):
        self.build(provenance={"kind": "github-actions", "repository": "o/r", "run_id": "abc", "run_attempt": "1",
                               "workflow_ref": "o/r/.github/workflows/other.yml@refs/heads/x", "github_sha": "0" * 40, "authenticated": False})
        self.assertEqual(self.verify(), 1)
    def test_claimed_authenticated_provenance_rejected(self):
        self.build(provenance={"kind": "local", "authenticated": True}); self.assertEqual(self.verify(), 1)


class FA07ExecutionStateContradiction(Base):
    """PR #29 R4: execution_state=EXECUTION_PASS with a required UNKNOWN was accepted and reported."""
    def test_self_reported_execution_state_rejected(self):
        self.build(mutate=setv("PG-01", "UNKNOWN"), json_mutate=lambda j: j.update(execution_state="EXECUTION_PASS"))
        self.assertEqual(self.verify(), 1)


class FA08SummaryContradiction(Base):
    """SUMMARY.md claiming PASS for a FAIL run was hashed but never compared."""
    def test_contradictory_summary_rejected(self):
        self.build(mutate=setv("ENTRA-02", "FAIL", "1"), summary="# Acceptance run\n\nOverall: **PASS**\n"); self.assertEqual(self.verify(), 1)


class FA09PostgresRunCoverage(Base):
    """PR #29 R7: postgres-run/** was excluded from the top-level SHA256SUMS, so editing it went undetected."""
    def test_postgres_run_outside_top_level_hashes_rejected(self):
        self.build(postgres_run=True, seal_skip=lambda p: p.startswith("postgres-run/")); self.assertEqual(self.verify(), 1)
    def test_postgres_run_tampered_after_seal_rejected_control(self):
        self.build(postgres_run=True); (self.d / "postgres-run" / "result.txt").write_text("restore FAIL\n"); self.assertEqual(self.verify(), 1)


class FA10ReviewScope(Base):
    """Plan / PR #29: one review record was copied to every requirement (narrow review -> blanket approval)."""
    def test_blanket_review_without_requirement_ids_invalid(self):
        self.build(); self.assertEqual(self.decide(reviews=review(self.sha, ids=None)).returncode, 1)
    def test_review_naming_unknown_requirement_invalid_hardening(self):
        self.build(); self.assertEqual(self.decide(reviews=review(self.sha, ids=["ACC-WD-NOT-A-REQUIREMENT"])).returncode, 1)
    def test_narrow_review_covers_only_what_it_names_hardening(self):
        self.build(); p = self.decide(reviews=review(self.sha, ids=[ALL_REQ[0]]))
        self.assertEqual(p.returncode, 5, p.stdout + p.stderr)


class FA11SelfReviewVariants(Base):
    """PR #29 R3: only the exact recorder string was rejected; 'Worker D (recorder)' was ACCEPTED."""
    def test_recorder_variant_invalid(self):
        self.build(); self.assertEqual(self.decide(reviews=review(self.sha, who="Worker D (recorder)", ids=None)).returncode, 1)
    def test_integrator_variant_with_scope_invalid_hardening(self):
        self.build(); self.assertEqual(self.decide(reviews=review(self.sha, who="integrator")).returncode, 1)


class FA12UnboundVerify(Base):
    """The CI re-verification step ran verify_results.py DIR without --sha (consistency only, no source binding)."""
    def test_verify_without_sha_refused(self):
        self.build(); self.assertNotEqual(run(self.vrp, self.d).returncode, 0)


if __name__ == "__main__":
    unittest.main()
