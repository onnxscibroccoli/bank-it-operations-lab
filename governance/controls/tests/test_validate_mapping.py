"""Unit tests for validate_mapping.py (stdlib unittest; needs git on PATH).

Run from the repo root:  python3 -m unittest discover -s governance/controls/tests -v
"""
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_mapping as vm  # noqa: E402


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


class ValidateMappingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.invalid")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "logs").mkdir()
        (self.repo / "logs" / "run.log").write_text("exit 0\n")
        (self.repo / "lib.ts").write_text("// code\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "fixture")
        self.sha = git(self.repo, "rev-parse", "HEAD")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, mapping_rows, artifact_rows, md="AIO-01\n"):
        m = self.repo / "m.csv"
        a = self.repo / "a.csv"
        d = self.repo / "m.md"
        with m.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=vm.MAPPING_COLS)
            w.writeheader()
            w.writerows(mapping_rows)
        with a.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=vm.ARTIFACT_COLS)
            w.writeheader()
            w.writerows(artifact_rows)
        d.write_text(md)
        return m, a, d

    def mrow(self, **kw):
        row = dict(row_id="AIO-01", aio_id="VI.B.4", aio_title="Backup", booklet_page="75",
                   status="SIMULATION", lab_claim="c", limitations="l",
                   organizational_dependencies="o")
        row.update(kw)
        return row

    def arow(self, **kw):
        row = dict(row_id="AIO-01", role="evidence", path="logs/run.log", commit=self.sha,
                   source_branch="main", pr="", note="")
        row.update(kw)
        return row

    def run_validate(self, *files):
        return vm.validate(*files, repo=self.repo)

    def test_valid(self):
        self.assertEqual(self.run_validate(*self.write([self.mrow()], [self.arow()])), [])

    def test_missing_path(self):
        errs = self.run_validate(*self.write([self.mrow()], [self.arow(path="logs/nope.log")]))
        self.assertTrue(any("does not exist" in e for e in errs), errs)

    def test_short_sha_rejected(self):
        errs = self.run_validate(*self.write([self.mrow()], [self.arow(commit=self.sha[:7])]))
        self.assertTrue(any("40-hex" in e for e in errs), errs)

    def test_bad_status(self):
        errs = self.run_validate(*self.write([self.mrow(status="GAP")], [self.arow()]))
        self.assertTrue(any("status" in e for e in errs), errs)

    def test_unknown_section(self):
        errs = self.run_validate(*self.write([self.mrow(aio_id="VI.B.99")], [self.arow()]))
        self.assertTrue(any("section id" in e for e in errs), errs)

    def test_simulation_needs_evidence(self):
        errs = self.run_validate(*self.write([self.mrow()],
                                             [self.arow(role="implementation", path="lib.ts")]))
        self.assertTrue(any("role=evidence" in e for e in errs), errs)

    def test_static_without_evidence_ok(self):
        errs = self.run_validate(*self.write([self.mrow(status="STATIC")],
                                             [self.arow(role="implementation", path="lib.ts")]))
        self.assertEqual(errs, [])

    def test_row_without_artifacts(self):
        errs = self.run_validate(*self.write([self.mrow(), self.mrow(row_id="AIO-02")],
                                             [self.arow()], md="AIO-01 AIO-02"))
        self.assertTrue(any("no artifacts" in e for e in errs), errs)

    def test_markdown_wording(self):
        errs = self.run_validate(*self.write([self.mrow()], [self.arow()],
                                             md="AIO-01 the lab is compliant"))
        self.assertTrue(any("certification-style" in e for e in errs), errs)

    def test_markdown_missing_row(self):
        errs = self.run_validate(*self.write([self.mrow()], [self.arow()], md="nothing"))
        self.assertTrue(any("not mentioned" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
