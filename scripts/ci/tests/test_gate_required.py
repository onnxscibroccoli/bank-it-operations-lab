"""final-summary and merge-eligibility must fail when a required check is missing, skipped, cancelled or failed."""
import io, json, os, sys, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import final_summary, merge_eligibility  # noqa: E402

_REG = json.loads((Path(__file__).resolve().parents[3] / "coordination/modules.json").read_text())
REQ = _REG["required_gate_jobs"]
OUTS = _REG.get("required_gate_outputs") or {}
INCIDENT = ["incident-committed-runs", "incident-fresh-run", "incident-not-executed-negative", "labeling-markers"]
M365 = ["m365-scenario-evaluation", "m365-unit-tests", "m365-evidence-verification", "plan-only-assertions"]


def needs(**override):
    n = {j: {"result": "success", "outputs": {k: "PASS" for k in OUTS.get(j, [])}} for j in REQ}
    for k, v in override.items():
        k = k.replace("_", "-")
        if v is None:
            n.pop(k, None)
        else:
            n[k] = {"result": v}
    return n


def run(mod, n, extra=()):
    with mock.patch.dict(os.environ, {"NEEDS_JSON": json.dumps(n)}), redirect_stdout(io.StringIO()) as out:
        rc = mod.main(list(extra))
    return rc, out.getvalue()


class Gate(unittest.TestCase):
    def test_incident_jobs_and_outputs_are_required(self):
        for j in INCIDENT:
            self.assertIn(j, REQ)
        self.assertEqual(sorted(OUTS.get("incident-fresh-run", [])),
                         sorted(["injection", "detection", "diagnosis", "recovery", "timeline", "simulation"]))

    def test_not_executed_requirement_fails_both(self):
        for k in OUTS["incident-fresh-run"]:
            for bad in ("NOT_EXECUTED", "FAIL", "", None):
                n = needs()
                n["final-summary"] = {"result": "success"}
                if bad is None:
                    n["incident-fresh-run"]["outputs"].pop(k)
                else:
                    n["incident-fresh-run"]["outputs"][k] = bad
                with self.subTest(output=k, value=bad):
                    self.assertEqual(run(final_summary, n)[0], 1)
                    rc, out = run(merge_eligibility, n, ["--sha", "abc"])
                    self.assertEqual(rc, 1)
                    self.assertIn("required check incident-fresh-run." + k, out)

    def test_incident_jobs_fail_closed(self):
        for j in INCIDENT:
            for bad in (None, "skipped", "failure"):
                with self.subTest(job=j, result=bad):
                    self.assertEqual(run(final_summary, needs(**{j: bad}))[0], 1)

    def test_m365_jobs_are_required(self):
        for j in M365:
            self.assertIn(j, REQ)

    def test_all_success_passes_final_summary(self):
        self.assertEqual(run(final_summary, needs())[0], 0)

    def test_final_summary_fails_closed(self):
        for j in M365:
            for bad in (None, "skipped", "cancelled", "failure"):
                with self.subTest(job=j, result=bad):
                    rc, out = run(final_summary, needs(**{j: bad}))
                    self.assertEqual(rc, 1)
                    self.assertIn(j, out)

    def test_merge_eligibility_fails_closed_on_required_checks(self):
        for j in M365 + ["final-summary"]:
            for bad in (None, "skipped", "failure"):
                n = needs(**{j: bad})
                if j != "final-summary":
                    n["final-summary"] = {"result": "success"}
                with self.subTest(job=j, result=bad):
                    rc, out = run(merge_eligibility, n, ["--sha", "abc"])
                    self.assertEqual(rc, 1)
                    self.assertIn("required check " + j, out)


if __name__ == "__main__":
    unittest.main()
