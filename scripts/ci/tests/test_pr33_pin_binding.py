"""PR #33 regressions on candidate 2e3041a.
D3-a: the expected hash of every gate file (incl. integration-gate.yml) comes from the PINNED commit (git show
<pin>:path, hashed at runtime) and must equal the manifest AND the files executing in the run; the candidate's copy
never defines it. Reproduces the probe: a workflow that just writes/prints VERIFIED + a manifest whose workflow hash
was updated to match it + a valid independent review of the pin => UNVERIFIED / NOT ELIGIBLE.
Nit: every attested tested_merge must have parents exactly (main, candidate)."""
import copy, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_exceptions, reviews, verify_trusted_gate as vtg  # noqa: E402
from test_merge_eligibility_binding import (APPROVED_REVIEWS, AUTHOR, BASE, CAND, CONFIG, IDENT, MERGE, OWNER, REVIEWER,  # noqa: E402
                                            attestation, run)

ROOT = Path(__file__).resolve().parents[3]
CI = ROOT / "scripts/ci"
WF = ".github/workflows/integration-gate.yml"
CFG = ".github/acceptance/trusted-config.json"
FAKE_WF = "name: integration-gate\non: [push, pull_request]\njobs:\n  merge-eligibility:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo '{\"status\":\"VERIFIED\"}' > gate-trust.json && echo 'TRUSTED GATE VERIFIED'\n"
EXC = check_exceptions.evaluate(ROOT)
SCOPES = reviews.exception_scopes(EXC)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, check=True, text=True).stdout.strip()


def commit(repo, msg):
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


def sha256_text(s):
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()


class PinBoundToExecutingFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); r = cls.repo = Path(cls.tmp.name) / "repo"
        shutil.copytree(CI, r / "scripts/ci", ignore=shutil.ignore_patterns("__pycache__"))
        (r / ".github/acceptance").mkdir(parents=True); (r / ".github/workflows").mkdir(parents=True)
        (r / CFG).write_text(json.dumps(CONFIG))              # identical bytes to the --config the harness writes
        shutil.copy(ROOT / WF, r / WF)
        git(r, "init", "-q")
        cls.pin = commit(r, "gate (pinned, independently reviewed)")
        (r / "records.md").write_text("records only\n")
        cls.cand = commit(r, "candidate: records on top of the gate")
        (r / WF).write_text(FAKE_WF)
        cls.fake = commit(r, "fake workflow that just prints VERIFIED")
        git(r, "checkout", "-q", "--detach", cls.pin)
        cls.man = vtg.build(r, cls.pin)
        cls.man["independent_review"] = {"pr": 40, "review_id": 55}
        cls.forged = copy.deepcopy(cls.man)
        cls.forged["files"][WF] = sha256_text(FAKE_WF)       # the shared account updates only the manifest's workflow hash

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def review(m):
        return ({"id": 55, "state": "APPROVED", "commit_id": m["gate_sha"], "user": {"login": REVIEWER}}, AUTHOR, "write")

    def trust(self, man=None, wsha=None, ci=CI, cfg=None, repo=None):
        return vtg.gate_trust_at_runtime(man or self.man, "c" * 40, repo or self.repo, ci, cfg or (self.repo / CFG), self.repo,
                                         self.cand if wsha is None else wsha, self.review)

    def test_control_pinned_workflow_executing_is_verified(self):
        t = self.trust()
        self.assertEqual(t["status"], "VERIFIED", t["reasons"])

    def test_manifest_hashes_come_from_the_pin(self):
        self.assertEqual(self.man["files"][WF], sha256_text((ROOT / WF).read_text()))
        self.assertEqual(self.man["gate_sha"], self.pin)

    def test_probe_fake_workflow_plus_updated_manifest_plus_valid_review_is_unverified(self):
        t = self.trust(man=self.forged, wsha=self.fake)
        self.assertEqual(t["status"], "UNVERIFIED")
        self.assertTrue(any("manifest hash differs from the file at the pinned commit" in w for w in t["reasons"]), t["reasons"])
        self.assertTrue(any("EXECUTING workflow" in w for w in t["reasons"]), t["reasons"])

    def test_probe_end_to_end_forged_gate_trust_file_is_ignored_and_not_eligible(self):
        comments = [attestation(OWNER, "EXCEPTION", "APPROVED", cid=200 + i, at="2026-10-28T23:20:00Z",
                                extra=(f"exception: {ex}", f"scope: {SCOPES[ex]}")) for i, ex in enumerate(sorted(SCOPES))]
        comments += [attestation(REVIEWER, "AC4", "ACCEPT", cid=301), attestation(REVIEWER, "AC5", "ACCEPT", cid=302)]
        rv = copy.deepcopy(APPROVED_REVIEWS); rv["comments"] = comments
        with tempfile.TemporaryDirectory() as d:
            for name, man, wsha, want in (("control", self.man, self.cand, 0), ("probe", self.forged, self.fake, 1),
                                          ("fake workflow, honest manifest", self.man, self.fake, 1)):
                with self.subTest(case=name):
                    mp = Path(d) / f"{name}.json"; mp.write_text(json.dumps(man))
                    gt = Path(d) / "gate-trust.json"; gt.write_text('{"status": "VERIFIED", "reasons": []}')
                    import merge_eligibility as me
                    from unittest import mock
                    with mock.patch.object(vtg, "fetch_pin_review", lambda m, *a, **k: self.review(m)):
                        rc, out = run(reviews=rv, exc=EXC, gate_trust="REAL",
                                      extra=("--manifest", str(mp), "--gate-repo", str(self.repo), "--workflow-repo", str(self.repo),
                                             "--gate-trust", str(gt)),
                                      env_extra={"GITHUB_WORKFLOW_SHA": wsha, "GITHUB_TOKEN": "x", "GITHUB_REPOSITORY": "o/r"})
                    self.assertEqual(rc, want, out)
                    if want:
                        self.assertIn("TRUSTED GATE UNVERIFIED", out)
                        self.assertIn("NOT ELIGIBLE", out)
                    self.assertIn("ignored", out)

    def test_honest_manifest_but_fake_executing_workflow_is_unverified(self):
        t = self.trust(wsha=self.fake)
        self.assertEqual(t["status"], "UNVERIFIED")
        self.assertTrue(any("EXECUTING workflow" in w for w in t["reasons"]))

    def test_unknown_executing_workflow_commit_fails_closed(self):
        for w in ("", "abc", None):
            with self.subTest(w=w):
                self.assertEqual(self.trust(wsha=w or "")["status"], "UNVERIFIED")

    def test_gate_checkout_not_at_pin_is_unverified(self):
        r2 = Path(self.tmp.name) / "r2"
        if not r2.exists():
            git(self.repo, "worktree", "add", "-q", "--detach", str(r2), self.cand)
        self.assertEqual(self.trust(repo=r2)["status"], "UNVERIFIED")

    def test_executing_scripts_or_config_differ_from_pin(self):
        with tempfile.TemporaryDirectory() as d:
            ci = Path(d) / "ci"; shutil.copytree(CI, ci, ignore=shutil.ignore_patterns("__pycache__"))
            (ci / "merge_eligibility.py").write_text((ci / "merge_eligibility.py").read_text() + "\n# weakened\n")
            self.assertEqual(self.trust(ci=ci)["status"], "UNVERIFIED")
            ci2 = Path(d) / "ci2"; shutil.copytree(CI, ci2, ignore=shutil.ignore_patterns("__pycache__"))
            (ci2 / "shadow.py").write_text("print('ELIGIBLE')\n")
            self.assertEqual(self.trust(ci=ci2)["status"], "UNVERIFIED")
            cfg = Path(d) / "cfg.json"; cfg.write_text(json.dumps(dict(CONFIG, reviewer_allowlist=[REVIEWER, "me"])))
            self.assertEqual(self.trust(cfg=cfg)["status"], "UNVERIFIED")

    def test_manifest_file_missing_at_pin_is_unverified(self):
        m = copy.deepcopy(self.man); m["files"]["scripts/ci/not_in_pin.py"] = "0" * 64
        self.assertEqual(self.trust(man=m)["status"], "UNVERIFIED")

    def test_valid_binding_still_needs_review_and_no_self_pin(self):
        t = vtg.gate_trust_at_runtime(self.man, self.pin, self.repo, CI, self.repo / CFG, self.repo, self.cand, self.review)
        self.assertEqual(t["status"], "UNVERIFIED")                       # self-pin
        t = vtg.gate_trust_at_runtime(dict(self.man, independent_review=None), "c" * 40, self.repo, CI, self.repo / CFG,
                                      self.repo, self.cand, self.review)
        self.assertEqual(t["status"], "UNVERIFIED")                       # no review


class TestedMergeParents(unittest.TestCase):
    OTHER = "d" * 40

    def dec(self, tested, commits):
        r = copy.deepcopy(APPROVED_REVIEWS); r["comments"] = [attestation(REVIEWER, "AC4", "ACCEPT", tested=tested)]; r["commits"] = commits
        return reviews.decisions_from_comments(r, IDENT, CONFIG, EXC)["AC4"][0]

    def test_unverified_extra_tested_merge_is_rejected(self):
        self.assertEqual(self.dec((MERGE, self.OTHER), {}), "UNMET")

    def test_wrong_parents_or_order_is_rejected(self):
        for parents in ([CAND, BASE], [BASE], [BASE, "e" * 40], [BASE, CAND, "f" * 40]):
            with self.subTest(parents=parents):
                self.assertEqual(self.dec((MERGE, self.OTHER), {self.OTHER: {"parents": parents}}), "UNMET")

    def test_this_runs_merge_needs_a_valid_merge_identity(self):
        ident = dict(IDENT, kind="direct")
        r = copy.deepcopy(APPROVED_REVIEWS); r["comments"] = [attestation(REVIEWER, "AC4", "ACCEPT")]
        self.assertEqual(reviews.decisions_from_comments(r, ident, CONFIG, EXC)["AC4"][0], "UNMET")

    def test_control_parents_main_candidate_accepted(self):
        self.assertEqual(self.dec((MERGE, self.OTHER), {self.OTHER: {"parents": [BASE, CAND]}}), "MET_AT_RUNTIME")
        self.assertEqual(self.dec((MERGE,), {}), "MET_AT_RUNTIME")


if __name__ == "__main__":
    unittest.main()
