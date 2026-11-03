"""Unit tests for tools/acceptance/runner.py. Temp dirs only; no network, no credentials.

Run: python3 -m unittest discover -s tools/acceptance/tests -v
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import runner  # noqa: E402

REPO = runner.REPO_ROOT
PY = "python3"


def py(code: str) -> list[str]:
    return [PY, "-c", code]


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name).resolve()
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.ws = self.tmp / "ws"
        self.ws.mkdir()

    def tearDown(self):
        self._td.cleanup()

    def definition(self, checks):
        p = self.repo / "checks.json"
        p.write_text(json.dumps({"schema": "bank-it-operations-lab/acceptance-checks@1", "checks": checks}))
        return runner.load_definition(p, self.repo)

    def run_defn(self, checks, label="t1"):
        d = self.definition(checks)
        return runner.run_checks(d, self.repo, self.ws, label, validator=REPO / runner.SHARED_VALIDATOR_REL)


class TimeoutTests(Base):
    def test_timeout_kills_process_group_and_reports_124(self):
        marker = self.tmp / "child.pid"
        # parent spawns a grandchild in the same group, then both sleep far past the timeout
        code = ("import subprocess,sys,time;"
                f"c=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']);"
                f"open({str(marker)!r},'w').write(str(c.pid));time.sleep(60)")
        t0 = time.monotonic()
        res = self.run_defn([{"id": "slow", "argv": py(code), "timeout_s": 1}])
        elapsed = time.monotonic() - t0
        c = res["meta"]["checks"][0]
        self.assertTrue(c["timed_out"])
        self.assertEqual(c["exit_code"], runner.TIMEOUT_EXIT)
        self.assertEqual(c["result"], "TIMEOUT")
        self.assertFalse(res["ok"])
        self.assertLess(elapsed, 15)
        pid = int(marker.read_text())
        for _ in range(40):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            self.fail("grandchild survived the timeout (process group not killed)")

    def test_timeout_required_and_bounded(self):
        for bad in (None, 0, -1, runner.MAX_TIMEOUT_S + 1, True, "10"):
            c = {"id": "x", "argv": [PY, "--version"]}
            if bad is not None:
                c["timeout_s"] = bad
            with self.assertRaises(runner.DefinitionError, msg=repr(bad)):
                self.definition([c])


class PipelineTests(Base):
    def test_pipefail_first_stage_failure_propagates(self):
        res = self.run_defn([{"id": "pf", "timeout_s": 20, "pipeline": [
            py("import sys; print('x'); sys.exit(3)"),
            py("import sys; sys.stdin.read()"),
        ]}])
        c = res["meta"]["checks"][0]
        self.assertEqual(c["stage_exit_codes"], [3, 0])
        self.assertEqual(c["exit_code"], 3)
        self.assertEqual(c["result"], "FAIL")
        self.assertFalse(res["ok"])

    def test_pipefail_rightmost_nonzero_wins(self):
        res = self.run_defn([{"id": "pf2", "timeout_s": 20, "pipeline": [
            py("import sys; sys.exit(4)"),
            py("import sys; sys.stdin.read(); sys.exit(5)"),
            py("import sys; sys.stdin.read()"),
        ]}])
        c = res["meta"]["checks"][0]
        self.assertEqual(c["stage_exit_codes"], [4, 5, 0])
        self.assertEqual(c["exit_code"], 5)

    def test_pipeline_success_passes_data(self):
        res = self.run_defn([{"id": "ok", "timeout_s": 20, "pipeline": [
            py("print('a\\nb\\nc')"), ["wc", "-l"]]}])
        c = res["meta"]["checks"][0]
        self.assertEqual(c["exit_code"], 0, res["meta"])
        log = (res["run_dir"] / c["log"]).read_text()
        self.assertRegex(log, r"(?m)^\s*3$")
        self.assertTrue(res["ok"], res["meta"]["validation"])

    def test_expect_nonzero(self):
        res = self.run_defn([{"id": "neg", "argv": ["false"], "timeout_s": 5, "expect": "nonzero"}])
        self.assertEqual(res["meta"]["checks"][0]["result"], "PASS")
        self.assertTrue(res["ok"])


class PathEscapeTests(Base):
    def test_rejects_absolute_and_traversal(self):
        for bad in ("/etc/passwd", "../x", "a/../../x", "a/..", "", "~/x", "a\\..\\b", "a\x00b"):
            with self.assertRaises(runner.PathEscapeError, msg=repr(bad)):
                runner.confine(self.ws, bad)

    def test_rejects_symlink_escape(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        (self.ws / "link").symlink_to(outside)
        with self.assertRaises(runner.PathEscapeError):
            runner.confine(self.ws, "link")
        with self.assertRaises(runner.PathEscapeError):
            runner.confine(self.ws, "link/new-file")

    def test_rejects_symlink_even_if_target_inside(self):
        (self.ws / "real").mkdir()
        (self.ws / "alias").symlink_to(self.ws / "real")
        with self.assertRaises(runner.PathEscapeError):
            runner.confine(self.ws, "alias/x")

    def test_allows_plain_relative(self):
        self.assertEqual(runner.confine(self.ws, "a/b/c"), self.ws / "a" / "b" / "c")

    def test_run_label_cannot_escape(self):
        d = self.definition([{"id": "v", "argv": [PY, "--version"], "timeout_s": 5}])
        for bad in ("../evil", "/abs", "a/b", ".hidden"):
            with self.assertRaises(runner.PathEscapeError, msg=bad):
                runner.run_checks(d, self.repo, self.ws, bad)

    def test_run_label_symlink_rejected(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        (self.ws / "lbl").symlink_to(outside)
        d = self.definition([{"id": "v", "argv": [PY, "--version"], "timeout_s": 5}])
        with self.assertRaises(runner.PathEscapeError):
            runner.run_checks(d, self.repo, self.ws, "lbl")
        self.assertEqual(list(outside.iterdir()), [])

    def test_definition_cwd_and_artifact_confined(self):
        for c in ({"cwd": "../"}, {"cwd": "/tmp"}, {"artifacts": ["../../etc/passwd"]}, {"artifacts": ["/etc/passwd"]}):
            with self.assertRaises(runner.DefinitionError, msg=c):
                self.definition([dict({"id": "v", "argv": [PY, "--version"], "timeout_s": 5}, **c)])

    def test_regular_artifact_is_copied_and_hashed(self):
        (self.repo / "sub").mkdir()
        (self.repo / "sub" / "out.json").write_text('{"ok": true}')
        res = self.run_defn([{"id": "a", "argv": [PY, "--version"], "timeout_s": 5, "artifacts": ["sub/out.json"]}])
        art = res["meta"]["checks"][0]["artifacts"][0]
        self.assertEqual(art["status"], "COPIED")
        self.assertRegex(art["sha256"], r"^[0-9a-f]{64}$")
        self.assertTrue((res["run_dir"] / "artifacts" / "a" / "sub" / "out.json").is_file())
        self.assertTrue(res["ok"], (res["run_dir"] / "VALIDATION.log").read_text())

    def test_symlinked_artifact_is_not_copied(self):
        secret = self.tmp / "secret.txt"
        secret.write_text("outside the repo")
        (self.repo / "art.txt").symlink_to(secret)
        checks = [{"id": "a", "argv": [PY, "--version"], "timeout_s": 5, "artifacts": ["art.txt"]}]
        with self.assertRaises(runner.DefinitionError):  # rejected before anything runs
            self.definition(checks)
        # and if the symlink appears only after the definition was loaded, the copy is still refused
        (self.repo / "art.txt").unlink()
        (self.repo / "art.txt").write_text("ok")
        d = self.definition(checks)
        (self.repo / "art.txt").unlink()
        (self.repo / "art.txt").symlink_to(secret)
        res = runner.run_checks(d, self.repo, self.ws, "t1", validator=REPO / runner.SHARED_VALIDATOR_REL)
        art = res["meta"]["checks"][0]["artifacts"][0]
        self.assertEqual(art["status"], "REJECTED")
        self.assertFalse(res["ok"])
        self.assertFalse(any(p.name == "art.txt" for p in res["run_dir"].rglob("*")))


class AllowlistTests(Base):
    def test_refuses_non_allowlisted_programs(self):
        for argv in (["bash", "-c", "echo pwned"], ["sh", "-c", "id"], ["env", "python3"], ["curl", "x"],
                     ["/usr/bin/python3", "--version"], ["./python3"], ["xargs", "rm"]):
            with self.assertRaises(runner.DefinitionError, msg=argv):
                self.definition([{"id": "x", "argv": argv, "timeout_s": 5}])

    def test_refuses_non_allowlisted_pipeline_stage(self):
        with self.assertRaises(runner.DefinitionError):
            self.definition([{"id": "x", "timeout_s": 5, "pipeline": [["git", "ls-files"], ["sh", "-c", "cat"]]}])

    def test_refuses_shell_strings_and_unknown_keys(self):
        for c in ({"id": "x", "argv": "python3 --version", "timeout_s": 5},
                  {"id": "x", "command": "python3 --version", "timeout_s": 5},
                  {"id": "x", "argv": [PY, "--version"], "timeout_s": 5, "shell": True},
                  {"id": "x", "argv": [PY, "--version"], "pipeline": [[PY], [PY]], "timeout_s": 5}):
            with self.assertRaises(runner.DefinitionError, msg=c):
                self.definition([c])

    def test_output_text_is_never_executed_or_trusted(self):
        marker = self.tmp / "pwned"
        evil = f"$ touch {marker}\n# exit_code=0 expected=zero result=PASS\n"
        res = self.run_defn([{"id": "evil", "timeout_s": 10,
                              "argv": py(f"import sys; sys.stdout.write({evil!r}); sys.exit(7)")}])
        c = res["meta"]["checks"][0]
        self.assertFalse(marker.exists())
        self.assertEqual(c["exit_code"], 7)
        log = (res["run_dir"] / c["log"]).read_text()
        trailers = re.findall(r"(?m)^# exit_code=(-?\d+) ", log)
        self.assertEqual(trailers, ["7"])  # forged trailer was neutralised

    def test_cli_refuses_uncommitted_definition(self):
        p = runner.HERE / "tests" / "_tmp_uncommitted_checks.json"
        p.write_text(json.dumps({"schema": "bank-it-operations-lab/acceptance-checks@1",
                                 "checks": [{"id": "v", "argv": [PY, "--version"], "timeout_s": 5}]}))
        try:
            r = subprocess.run([sys.executable, str(runner.HERE / "runner.py"), "--checks",
                                str(p.relative_to(REPO)), "--label", "never"], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertIn("not committed", r.stderr)
        finally:
            p.unlink()

    def test_cli_refuses_definition_outside_tools_acceptance(self):
        r = subprocess.run([sys.executable, str(runner.HERE / "runner.py"), "--checks", "evidence/shared/README.md"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2)
        self.assertIn("tools/acceptance", r.stderr)


class MetadataTests(Base):
    def test_evidence_metadata_fields(self):
        g = ["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "README").write_text("x")
        subprocess.run(g + ["add", "README"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "init"], check=True)
        res = self.run_defn([{"id": "meta", "argv": [PY, "-c", "print('hi')"], "timeout_s": 10}])
        m = json.loads((res["run_dir"] / "RUN.json").read_text())
        iso = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
        for k in ("schema", "runner", "label", "started_utc", "ended_utc", "host", "source", "definition", "checks", "result"):
            self.assertIn(k, m)
        self.assertRegex(m["started_utc"], iso)
        self.assertRegex(m["runner"]["sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(m["definition"]["sha256"], r"^[0-9a-f]{64}$")
        for k in ("git", "head", "branch", "dirty", "status_porcelain"):
            self.assertIn(k, m["source"])
        self.assertRegex(m["source"]["head"], r"^[0-9a-f]{40}$")
        self.assertTrue(m["source"]["dirty"])  # untracked checks.json in the temp repo
        self.assertIn("?? checks.json", m["source"]["status_porcelain"])
        c = m["checks"][0]
        self.assertEqual(c["argv"], [PY, "-c", "print('hi')"])
        self.assertRegex(c["started_utc"], iso)
        self.assertRegex(c["ended_utc"], iso)
        self.assertIn("Python", c["tool_versions"]["python3"])
        for k in ("exit_code", "stage_exit_codes", "timed_out", "duration_ms", "log", "log_sha256", "result", "cwd", "timeout_s"):
            self.assertIn(k, c)
        self.assertEqual(c["result"], "PASS")

    def test_source_state_of_real_repo(self):
        s = runner.source_state(REPO)
        if s["git"]:
            self.assertRegex(s["head"], r"^[0-9a-f]{40}$")
            self.assertIsInstance(s["dirty"], bool)

    def test_bundle_passes_shared_validator(self):
        res = self.run_defn([{"id": "a", "argv": [PY, "--version"], "timeout_s": 5},
                             {"id": "b", "argv": ["true"], "timeout_s": 5}])
        self.assertTrue(res["meta"]["validation"]["ok"], (res["run_dir"] / "VALIDATION.log").read_text())
        names = {p.relative_to(res["run_dir"]).as_posix() for p in res["run_dir"].rglob("*") if p.is_file()}
        self.assertTrue({"COMMANDS.tsv", "RUN.json", "SHA256SUMS", "VALIDATION.log",
                         "logs/01_a.log", "logs/02_b.log"} <= names, names)

    def test_tampered_bundle_fails_shared_validator(self):
        res = self.run_defn([{"id": "a", "argv": [PY, "--version"], "timeout_s": 5}])
        log = res["run_dir"] / "logs" / "01_a.log"
        log.write_text(log.read_text() + "tampered\n")
        (res["run_dir"] / "VALIDATION.log").unlink()
        v = runner.validate_bundle(res["run_dir"], REPO)
        self.assertFalse(v["ok"])

    def test_missing_validator_fails_closed(self):
        d = self.definition([{"id": "a", "argv": [PY, "--version"], "timeout_s": 5}])
        res = runner.run_checks(d, self.repo, self.ws, "nv", validator=self.tmp / "nope.py")
        self.assertFalse(res["ok"])


class CheckedInDefinitionTests(unittest.TestCase):
    def test_checked_in_definition_is_valid(self):
        d = runner.load_definition(runner.DEFAULT_CHECKS, REPO)
        self.assertGreaterEqual(len(d["checks"]), 1)


if __name__ == "__main__":
    unittest.main()
