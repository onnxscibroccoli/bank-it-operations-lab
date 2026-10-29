"""Negative tests for scripts/ci/check_incident_run.py: tampered or unexecuted runs must never PASS."""
import io, json, shutil, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_incident_run as cir  # noqa: E402

RUNS = sorted(p for p in (cir.ROOT / "evidence/incident/runs").glob("*") if p.is_dir() and not p.name.endswith(".console")) \
    if (cir.ROOT / "evidence/incident/runs").is_dir() else []


@unittest.skipUnless(RUNS, "incident module not integrated (the required incident jobs fail closed separately)")
class IncidentRequirements(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = Path(self.tmp) / "run"
        shutil.copytree(RUNS[0], self.run)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def check(self, *extra):
        with redirect_stdout(io.StringIO()) as out:
            rc = cir.main([str(self.run), *extra])
        return rc, out.getvalue()

    def test_pristine_passes(self):
        self.assertEqual(self.check()[0], 0)

    def test_not_executed_summary_is_never_pass(self):
        (self.run / "SUMMARY.json").write_text(json.dumps({"simulation": "SIMULATION", "status": "NOT_EXECUTED",
                                                           "reason": "PostgreSQL server binaries (initdb/pg_ctl) not found"}))
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("INCIDENT REQUIREMENTS NOT_EXECUTED", out)
        for r in cir.REQS:
            self.assertRegex(out, rf"(?m)^{r} +NOT_EXECUTED")
        self.assertNotRegex(out, r"(?m)^[a-z]+ +PASS ")

    def test_missing_summary_is_not_executed(self):
        (self.run / "SUMMARY.json").unlink()
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("NOT_EXECUTED", out)

    def _drop_event(self, name):
        p = self.run / "events.jsonl"
        p.write_text("".join(l + "\n" for l in p.read_text().splitlines() if f'"event":"{name}"' not in l))

    def test_missing_injection_fails(self):
        self._drop_event("failure_injected")
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertRegex(out, r"(?m)^injection +FAIL")

    def test_missing_detection_fails(self):
        self._drop_event("detected")
        self.assertRegex(self.check()[1], r"(?m)^detection +FAIL")

    def test_missing_diagnosis_fails(self):
        self._drop_event("diagnosed")
        self.assertRegex(self.check()[1], r"(?m)^diagnosis +FAIL")

    def test_missing_recovery_fails(self):
        self._drop_event("service_restored")
        self.assertRegex(self.check()[1], r"(?m)^recovery +FAIL")

    def test_failed_diag_step_fails(self):
        p = self.run / "COMMANDS.tsv"
        lines = p.read_text().splitlines()
        lines = [l.replace("\tPASS\t", "\tFAIL\t") if "\tdiag_db_ping\t" in l else l for l in lines]
        p.write_text("\n".join(lines) + "\n")
        self.assertRegex(self.check()[1], r"(?m)^diagnosis +FAIL")

    def test_forged_timeline_fails(self):
        p = self.run / "SUMMARY.json"
        d = json.loads(p.read_text())
        d["metrics"]["mttr_s"] = 1.0
        p.write_text(json.dumps(d))
        self.assertRegex(self.check()[1], r"(?m)^timeline +FAIL")

    def test_unlabelled_event_fails_simulation(self):
        p = self.run / "events.jsonl"
        p.write_text(p.read_text().replace('"simulation":"SIMULATION"', '"simulation":"PRODUCTION"', 1))
        self.assertRegex(self.check()[1], r"(?m)^simulation +FAIL")

    def test_missing_directory_label_fails_simulation(self):
        (self.run / "SIMULATION.md").unlink()
        self.assertRegex(self.check()[1], r"(?m)^simulation +FAIL")


if __name__ == "__main__":
    unittest.main()
