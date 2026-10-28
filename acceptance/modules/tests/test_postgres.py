import json
import re
import shutil
import unittest

from _helpers import TmpMixin, copytree, non_pass, reseal_all, by_id
from acceptance.modules import postgres as pg

GOOD = "ci-offline-40741329107-1"
CONTROL = "ci-mismatch-control-40741329107-1"
N01_LOG = "logs/24_N01_restore_truncated_dump.log"


class PostgresAdapterTest(TmpMixin, unittest.TestCase):
    def runs(self):
        return copytree(pg.RUNS, self.td)

    def check_of(self, r, run_name):
        return next(c for c in r.checks if c.title.startswith(run_name + ":") and c.id.startswith("PG-RUN")
                    and not c.id.endswith(("N", "X")))

    def test_committed_runs_pass(self):
        r = pg.run()
        d = r.to_dict()
        self.assertEqual(d["status"], "PASS", non_pass(r))
        cls = pg.parse_index(pg.RUNS / "INDEX.md")
        self.assertIn(GOOD, cls["verified"])
        self.assertEqual(cls["control"], [CONTROL])
        self.assertEqual(len(cls["historical"]), 3)
        self.assertTrue(any(c["id"] == "PG-CTL-001" and c["status"] == "PASS" for c in d["checks"]))

    # --- negatives
    def test_tampered_log_fails_on_hash(self):
        runs = self.runs()
        (runs / GOOD / N01_LOG).write_text("tampered\n")
        r = pg.run(runs_dir=runs)
        c = self.check_of(r, GOOD)
        self.assertEqual((c.status, c.reason_code), ("FAIL", "EVIDENCE_HASH_MISMATCH"))
        self.assertEqual(set(non_pass(r).values()), {"EVIDENCE_HASH_MISMATCH"})

    def test_negative_failing_for_other_reason_is_wrong_reason(self):
        runs = self.runs()
        p = runs / GOOD / N01_LOG
        p.write_text(p.read_text().replace("pg_restore: error: could not read from input file: end of file",
                                           "pg_restore: error: connection to server failed: permission denied"))
        reseal_all(runs / GOOD)
        r = pg.run(runs_dir=runs)
        c = self.check_of(r, GOOD)
        self.assertEqual((c.status, c.reason_code), ("FAIL", "NEGATIVE_WRONG_REASON"))
        self.assertIn("N01_restore_truncated_dump", c.detail)
        self.assertEqual(set(non_pass(r).values()), {"NEGATIVE_WRONG_REASON"})

    def test_negative_that_succeeds_is_unexpected_success(self):
        runs = self.runs()
        d = runs / GOOD
        p = d / N01_LOG
        p.write_text(p.read_text().replace("# exit_code=1 ", "# exit_code=0 "))
        tsv = d / "COMMANDS.tsv"
        tsv.write_text(re.sub(r"(N01_restore_truncated_dump\tnegative\tnonzero\t)1\t", r"\g<1>0\t", tsv.read_text()))
        reseal_all(d)
        r = pg.run(runs_dir=runs)
        c = self.check_of(r, GOOD)
        self.assertEqual((c.status, c.reason_code), ("FAIL", "NEGATIVE_UNEXPECTED_SUCCESS"))

    def test_historical_run_cannot_count_as_pass(self):
        runs = self.runs()
        (runs / GOOD / "STATUS.json").write_text(json.dumps({"status": "HISTORICAL-KNOWN-INVALID", "reason": "test"}))
        reseal_all(runs / GOOD)
        r = pg.run(runs_dir=runs)
        self.assertEqual(self.check_of(r, GOOD).reason_code, "EVIDENCE_HISTORICAL")

    def test_control_that_verifies_is_not_rejected(self):
        runs = self.runs()
        shutil.rmtree(runs / CONTROL)
        shutil.copytree(runs / GOOD, runs / CONTROL)
        r = pg.run(runs_dir=runs)
        self.assertEqual(non_pass(r), {"PG-CTL-001": "CONTROL_NOT_REJECTED"})

    def test_control_rejected_for_other_reason_is_wrong_reason(self):
        runs = self.runs()
        tsv = runs / CONTROL / "COMMANDS.tsv"
        tsv.write_text(tsv.read_text().replace("\tversion_mismatch\t", "\tsetup_failure\t"))
        reseal_all(runs / CONTROL)
        r = pg.run(runs_dir=runs)
        self.assertEqual(non_pass(r), {"PG-CTL-001": "NEGATIVE_WRONG_REASON"})

    def test_missing_index_is_missing_evidence(self):
        r = pg.run(runs_dir=self.td)
        self.assertEqual(r.to_dict()["reason_code"], "EVIDENCE_MISSING")

    def test_classifier_priority(self):
        out = ("ERROR N01: reason_regex not found in log output: x\nERROR hash: mismatch: logs/a.log\n"
               "ERROR SUMMARY.json overall=FAIL\nERROR S04: result ERROR/version_mismatch\n")
        self.assertEqual(pg.classify_verifier_output(out),
                         ["EVIDENCE_HASH_MISMATCH", "NEGATIVE_WRONG_REASON", "CASE_FAILED", "RUN_FAILED"])


if __name__ == "__main__":
    unittest.main()
