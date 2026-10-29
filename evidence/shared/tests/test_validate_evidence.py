"""Self-contained tests for evidence/shared/validate_evidence.py (stdlib unittest; temp dirs only).

Run from the repo root:  python3 -m unittest discover -s evidence/shared/tests -v
"""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SHARED = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SHARED))
import validate_evidence as ve  # noqa: E402


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = ve.main(list(argv))
    return rc, out.getvalue()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Hashes(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        (self.d / "a.txt").write_bytes(b"a\n")

    def test_ok_and_uncovered(self):
        (self.d / "SHA256SUMS").write_text(f"{sha(b'a' + bytes([10]))}  a.txt\n")
        (self.d / "extra.md").write_text("x")
        rc, out = run("hashes", str(self.d / "SHA256SUMS"), "--cover", str(self.d))
        self.assertEqual(rc, 0)
        self.assertIn("UNCOVERED", out)

    def test_mismatch(self):
        (self.d / "SHA256SUMS").write_text(f"{'0' * 64}  a.txt\n")
        rc, out = run("hashes", str(self.d / "SHA256SUMS"))
        self.assertEqual(rc, 1)
        self.assertIn("mismatch", out)

    def test_self_listing_is_an_error(self):
        (self.d / "SHA256SUMS").write_text(f"{'0' * 64}  SHA256SUMS\n")
        rc, out = run("hashes", str(self.d / "SHA256SUMS"))
        self.assertEqual(rc, 1)
        self.assertIn("lists itself", out)


class Commands(unittest.TestCase):
    def test_aws_trailer_mismatch_and_orphan(self):
        d = Path(tempfile.mkdtemp())
        (d / "01-x.log").write_text("# command: x\n# exit_code: 1\n")
        (d / "02-orphan.log").write_text("# exit_code: 0\n")
        (d / "COMMANDS.tsv").write_text("01-x.log\t0\tx\n")
        rc, out = run("commands", str(d / "COMMANDS.tsv"), "--format", "aws-3col")
        self.assertEqual(rc, 1)
        self.assertIn("trailer exit 1 != TSV exit 0", out)
        self.assertIn("ORPHAN log 02-orphan.log", out)

    def test_postgres_result_consistency(self):
        d = Path(tempfile.mkdtemp())
        (d / "logs").mkdir()
        (d / "logs/01_s.log").write_text("# cmd: s\n# exit_code=0 duration_ms=1\n")
        hdr = "seq\tstep_id\tkind\texpected\texit_code\tresult\tstarted_utc\tduration_ms\tlog\tcommand\n"
        (d / "COMMANDS.tsv").write_text(hdr + "1\ts\tnegative\tnonzero\t0\tPASS\tt\t1\tlogs/01_s.log\ts\n")
        rc, out = run("commands", str(d / "COMMANDS.tsv"), "--format", "postgres-10col")
        self.assertEqual(rc, 1)
        self.assertIn("inconsistent", out)


class Negatives(unittest.TestCase):
    def _run_dir(self, log_body):
        d = Path(tempfile.mkdtemp())
        (d / "logs").mkdir()
        (d / "logs/01_N04_fk_enforced_after_restore.log").write_text(f"# cmd: x\n{log_body}\n# exit_code=1 duration_ms=1\n")
        hdr = "seq\tstep_id\tkind\texpected\texit_code\tresult\tstarted_utc\tduration_ms\tlog\tcommand\n"
        row = "1\tN04_fk_enforced_after_restore\tnegative\tnonzero\t1\tPASS\tt\t1\tlogs/01_N04_fk_enforced_after_restore.log\tx\n"
        (d / "COMMANDS.tsv").write_text(hdr + row)
        return d

    def test_intended_failure(self):
        rc, _ = run("postgres-negatives", str(self._run_dir('ERROR:  insert violates foreign key constraint "f"')))
        self.assertEqual(rc, 0)

    def test_false_pass(self):
        rc, out = run("postgres-negatives", str(self._run_dir('ERROR:  relation "lab.ledger_entries" does not exist')))
        self.assertEqual(rc, 1)
        self.assertIn("FALSE-PASS", out)

    def test_harness_v2_layout(self):
        d = Path(tempfile.mkdtemp()); (d / "logs").mkdir()
        (d / "logs/01_N04.log").write_text('# cmd: x\nERROR:  23503: insert violates foreign key constraint "f"\n')
        hdr = "seq\tstep_id\tkind\texpected\texit_code\tresult\tclass\tstarted_utc\tduration_ms\tlog\treason_regex\tcommand\n"
        row = "1\tN04_fk_enforced_after_restore\tnegative\tnonzero\t1\tPASS\texpected_fault_detected\tt\t1\tlogs/01_N04.log\t23503\tx\n"
        (d / "COMMANDS.tsv").write_text(hdr + row)
        rc, out = run("postgres-negatives", str(d))
        self.assertEqual(rc, 0, out)
        self.assertIn("1 negative", out)

    def test_not_run_negatives_are_an_error(self):
        d = Path(tempfile.mkdtemp())
        hdr = "seq\tstep_id\tkind\texpected\texit_code\tresult\tclass\tstarted_utc\tduration_ms\tlog\treason_regex\tcommand\n"
        row = "1\tN04_fk_enforced_after_restore\tnegative\tnonzero\t-\tNOT_RUN\tdependency_failed\tt\t0\tlogs/none.log\t23503\tx\n"
        (d / "COMMANDS.tsv").write_text(hdr + row)
        rc, out = run("postgres-negatives", str(d))
        self.assertEqual(rc, 1, out)
        self.assertIn("NOT_RUN", out)
        self.assertNotIn("NEGATIVES OK", out)

    def test_zero_negatives_is_an_error(self):
        d = Path(tempfile.mkdtemp())
        (d / "COMMANDS.tsv").write_text("seq\tstep_id\tkind\tresult\tlog\n1\tS00\tsetup\tPASS\tlogs/x.log\n")
        rc, _ = run("postgres-negatives", str(d))
        self.assertEqual(rc, 1)


class CfnSelfLog(unittest.TestCase):
    def _tpl(self, resources):
        p = Path(tempfile.mkdtemp()) / "t.json"
        p.write_text(json.dumps({"Resources": resources}))
        return str(p)

    def test_self_logging_without_destination(self):
        t = self._tpl({"Logs": {"Type": "AWS::S3::Bucket", "Properties": {"LoggingConfiguration": {"LogFilePrefix": "self/"}}}})
        self.assertEqual(run("cfn-s3-selflog", t)[0], 1)

    def test_self_logging_explicit_ref(self):
        t = self._tpl({"Logs": {"Type": "AWS::S3::Bucket", "Properties": {"LoggingConfiguration": {"DestinationBucketName": {"Ref": "Logs"}}}}})
        self.assertEqual(run("cfn-s3-selflog", t)[0], 1)

    def test_logging_to_other_bucket_ok(self):
        t = self._tpl({
            "Logs": {"Type": "AWS::S3::Bucket", "Properties": {}},
            "Data": {"Type": "AWS::S3::Bucket", "Properties": {"LoggingConfiguration": {"DestinationBucketName": {"Ref": "Logs"}}}},
        })
        self.assertEqual(run("cfn-s3-selflog", t)[0], 0)


class Manifest(unittest.TestCase):
    GOOD = {
        "schema_version": "1.0.0",
        "bundle": {"id": "x", "root": "evidence/x", "kind": "integration-run"},
        "producer": {"script": "s.sh", "source_commit": "uncommitted", "script_sha256": "a" * 64},
        "hashes": {"file": "SHA256SUMS", "base": "bundle", "algorithm": "sha256"},
        "commands": {"file": "COMMANDS.tsv", "format": "postgres-10col", "rows_written_by": "producer-script"},
        "exclusions": [{"path": "SHA256SUMS", "reason": "self-reference"}],
        "anchors": [{"type": "github-actions-run", "ref": "123"}],
    }

    def _write(self, m):
        p = Path(tempfile.mkdtemp()) / "MANIFEST.json"
        p.write_text(json.dumps(m))
        return str(p)

    def test_good(self):
        self.assertEqual(run("manifest", self._write(self.GOOD))[0], 0)

    def test_uncommitted_requires_script_hash(self):
        m = json.loads(json.dumps(self.GOOD))
        del m["producer"]["script_sha256"]
        rc, out = run("manifest", self._write(m))
        self.assertEqual(rc, 1)
        self.assertIn("script_sha256", out)

    def test_hashes_file_must_be_self_excluded(self):
        m = json.loads(json.dumps(self.GOOD))
        m["exclusions"] = []
        self.assertEqual(run("manifest", self._write(m))[0], 1)


if __name__ == "__main__":
    unittest.main()
