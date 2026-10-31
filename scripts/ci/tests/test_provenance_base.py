"""PR #30 F1: the merge base of a kind-"merge" identity must be the CURRENT main SHA read at runtime.
Builds a throwaway git repo: main M, candidate C (child of M), an old candidate O (child of M, not main)."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import provenance  # noqa: E402


def g(d, *a):
    return subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True,
                          env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t",
                               "GIT_COMMITTER_EMAIL": "t@x", "GIT_CONFIG_GLOBAL": "/dev/null"}).stdout.strip()


class BaseMustBeMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); d = cls.d = cls.tmp.name
        g(d, "init", "-q", "-b", "main")
        Path(d, "f").write_text("m"); g(d, "add", "f"); g(d, "commit", "-qm", "main")
        cls.M = g(d, "rev-parse", "HEAD")
        g(d, "checkout", "-qb", "old"); Path(d, "o").write_text("o"); g(d, "add", "o"); g(d, "commit", "-qm", "old candidate")
        cls.O = g(d, "rev-parse", "HEAD")
        g(d, "checkout", "-q", cls.M); g(d, "checkout", "-qb", "cand"); Path(d, "c").write_text("c"); g(d, "add", "c"); g(d, "commit", "-qm", "cand")
        cls.C = g(d, "rev-parse", "HEAD")
        g(d, "checkout", "-q", cls.M); g(d, "merge", "-q", "--no-ff", "-m", "mv into main", cls.C); cls.GOOD = g(d, "rev-parse", "HEAD")
        g(d, "checkout", "-q", cls.O); g(d, "merge", "-q", "--no-ff", "-m", "mv into old candidate", cls.C); cls.BAD = g(d, "rev-parse", "HEAD")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def ident(self, tested, ref=None, main=None, event="push", payload=None):
        env = {"GITHUB_EVENT_NAME": event, "GITHUB_SHA": tested, "GITHUB_REF_NAME": ref or f"candidate/main-validation-{self.C[:7]}"}
        if main is not None:
            env["TRUSTED_MAIN_SHA"] = main
        if payload is not None:
            p = Path(self.d) / "event.json"; p.write_text(json.dumps(payload)); env["GITHUB_EVENT_PATH"] = str(p)
        cwd = os.getcwd(); os.chdir(self.d)
        try:
            return provenance.compute(env)
        finally:
            os.chdir(cwd)

    def test_control_merge_into_current_main_is_valid(self):
        i = self.ident(self.GOOD, main=self.M)
        self.assertTrue(i["valid"], i["errors"])
        self.assertEqual((i["base_sha"], i["candidate_sha"], i["main_sha_at_runtime"]), (self.M, self.C, self.M))

    def test_local_merge_into_non_main_parent_under_candidate_branch_name_is_invalid(self):
        i = self.ident(self.BAD, main=self.M)
        self.assertFalse(i["valid"])
        self.assertTrue(any("is not the current main" in e for e in i["errors"]), i["errors"])

    def test_missing_or_bad_main_sha_is_invalid(self):
        for m in (None, "", self.M[:7], "z" * 40):
            with self.subTest(main=m):
                i = self.ident(self.GOOD, main=m)
                self.assertFalse(i["valid"])
                self.assertTrue(any("current main SHA not available" in e for e in i["errors"]), i["errors"])

    def test_main_moved_since_the_merge_is_invalid(self):
        i = self.ident(self.GOOD, main=self.O)
        self.assertFalse(i["valid"])

    def test_pull_request_moved_base_and_non_main_base_ref_are_invalid(self):
        pl = {"pull_request": {"number": 7, "head": {"sha": self.C}, "base": {"sha": self.O, "ref": "main"}}}
        i = self.ident(self.GOOD, ref="7/merge", main=self.M, event="pull_request", payload=pl)
        self.assertFalse(i["valid"]); self.assertTrue(any("base moved" in e for e in i["errors"]))
        pl = {"pull_request": {"number": 7, "head": {"sha": self.C}, "base": {"sha": self.M, "ref": "develop"}}}
        i = self.ident(self.GOOD, ref="7/merge", main=self.M, event="pull_request", payload=pl)
        self.assertFalse(i["valid"]); self.assertTrue(any("not main" in e for e in i["errors"]))
        pl = {"pull_request": {"number": 7, "head": {"sha": self.C}, "base": {"sha": self.M, "ref": "main"}}}
        i = self.ident(self.GOOD, ref="7/merge", main=self.M, event="pull_request", payload=pl)
        self.assertTrue(i["valid"], i["errors"])

    def test_correct_parents_cannot_hide_a_different_tested_tree(self):
        tree = g(self.d, "rev-parse", self.M + "^{tree}")
        fake = g(self.d, "commit-tree", tree, "-p", self.M, "-p", self.C, "-m", "fake merge")
        i = self.ident(fake, main=self.M)
        self.assertFalse(i["valid"], "Correct parents must not authenticate altered merge contents")
        self.assertTrue(any("tree" in e for e in i["errors"]))

    def test_direct_push_needs_no_main_and_stays_direct(self):
        i = self.ident(self.C, ref="overnight/integration")
        self.assertEqual(i["kind"], "direct")
        self.assertTrue(i["valid"], i["errors"])


if __name__ == "__main__":
    unittest.main()
