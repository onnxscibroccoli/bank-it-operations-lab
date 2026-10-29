"""R6 hardening: the candidate must not be able to weaken the verifier (verify_trusted_gate.py)."""
import io, shutil, subprocess, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify_trusted_gate as v  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True, text=True).stdout.strip()


def commit_all(repo, msg="gate"):
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


class TrustedGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); d = Path(self.tmp.name)
        for side in ("gate", "cand"):
            shutil.copytree(ROOT / "scripts/ci", d / side / "scripts/ci", ignore=shutil.ignore_patterns("__pycache__"))
            (d / side / ".github/acceptance").mkdir(parents=True)
            shutil.copy(ROOT / ".github/acceptance/trusted-config.json", d / side / ".github/acceptance/")
            (d / side / ".github/workflows").mkdir(parents=True)
            shutil.copy(ROOT / ".github/workflows/integration-gate.yml", d / side / ".github/workflows/")
        self.g, self.c = d / "gate", d / "cand"
        git(self.g, "init", "-q")
        global SHA
        SHA = commit_all(self.g)
        self.man = v.build(self.g, SHA)

    def tearDown(self):
        self.tmp.cleanup()

    def test_control_matching_candidate_verifies(self):
        self.assertEqual(v.verify(self.man, self.g, self.c, SHA), [])

    def test_candidate_weakening_merge_eligibility_is_rejected(self):
        p = self.c / "scripts/ci/merge_eligibility.py"; p.write_text(p.read_text().replace('verdict = "ELIGIBLE" if not problems', 'verdict = "ELIGIBLE" if True'))
        self.assertTrue(any("merge_eligibility.py differs" in e for e in v.verify(self.man, self.g, self.c, SHA)))

    def test_candidate_editing_workflow_or_allowlist_is_rejected(self):
        (self.c / ".github/workflows/integration-gate.yml").write_text("# removed the gate\n")
        (self.c / ".github/acceptance/trusted-config.json").write_text('{"reviewer_allowlist": ["me"]}')
        e = v.verify(self.man, self.g, self.c, SHA)
        self.assertTrue(any("integration-gate.yml differs" in x for x in e))
        self.assertTrue(any("trusted-config.json differs" in x for x in e))

    def test_candidate_adding_a_script_is_rejected(self):
        (self.c / "scripts/ci/shadow.py").write_text("print('ELIGIBLE')\n")
        self.assertTrue(any("not in the trusted manifest" in x for x in v.verify(self.man, self.g, self.c, SHA)))

    def test_tampered_gate_checkout_or_wrong_pin_is_rejected(self):
        (self.g / "scripts/ci/reviews.py").write_text("")
        self.assertTrue(any("trusted gate: scripts/ci/reviews.py differs" in x for x in v.verify(self.man, self.g, self.c, SHA)))
        self.assertTrue(any("manifest pins" in x for x in v.verify(self.man, self.g, self.c, "5" * 40)))

    def test_missing_or_malformed_manifest_fails_closed(self):
        self.assertTrue(v.verify({}, self.g, self.c, SHA))
        self.assertTrue(v.verify({"gate_sha": SHA, "files": {}}, self.g, self.c, SHA))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(v.main(["--manifest", str(self.g / "nope.json"), "--gate-dir", str(self.g), "--candidate-dir", str(self.c), "--gate-head", SHA]), 1)


if __name__ == "__main__":
    unittest.main()
