"""SIMULATION - offline tests for governance/vendor-risk/check_governance.py."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_governance", HERE / "check_governance.py")
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)

SCENARIO = HERE / "scenarios" / "core-banking-vendor-outage-SIMULATION.md"
RACI = HERE / "examples" / "acme-core-ledger-SIMULATION-raci.md"
BASE = SCENARIO.read_text(encoding="utf-8")


class ScenarioLint(unittest.TestCase):
    def lint(self, text):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "scenario-SIMULATION.md"
            p.write_text(text, encoding="utf-8")
            return cg.scenario_findings(p)

    def assertFlags(self, text, needle):
        f = self.lint(text)
        self.assertTrue(any(needle in x for x in f), f"expected finding containing {needle!r}, got {f}")

    def test_committed_scenario_passes(self):
        self.assertEqual(cg.scenario_findings(SCENARIO), [])

    def test_whole_lint_passes(self):
        self.assertEqual(cg.main([]), 0)

    def test_missing_simulation_label(self):
        self.assertFlags(BASE.replace("# SIMULATION — ", "# ", 1), "not labelled SIMULATION")

    def test_each_required_section_enforced(self):
        for sec in cg.SCENARIO_SECTIONS:
            with self.subTest(sec):
                self.assertFlags(BASE.replace(sec, "Renamed"), f"missing required section '{sec}'")

    def test_missing_contract_placeholder(self):
        self.assertFlags(BASE.replace(cg.CONTRACT_PLACEHOLDER, "[TBD]"), "confirm from contract")

    def test_jack_henry_outside_job_description_statement(self):
        self.assertFlags(BASE + "\nJack Henry restores the core quickly.\n", "outside the job-description")

    def test_jack_henry_statement_required(self):
        txt = "\n".join(ln for ln in BASE.splitlines() if "Jack Henry" not in ln)
        self.assertFlags(txt, "job-description vendor")

    def test_vendor_sla_like_commitments_flagged(self):
        for line in ["The vendor will restore service within 4 hours.",
                     "Vendor uptime is 99.9% monthly.",
                     "Provider SLA: response in 15 min.",
                     "Acme RTO 2 business days.",
                     "The vendor's RPO is 30 seconds.",
                     "| Vendor status requests | every 30 minutes | Vendor manager |"]:
            with self.subTest(line):
                self.assertFlags(BASE + "\n" + line + "\n", "SLA-like numeric commitment")

    def test_placeholders_and_internal_numbers_not_flagged(self):
        ok = [BASE + "\n- Vendor obligations: [PLACEHOLDER: confirm from contract, e.g. 4 hours]\n",
              BASE + "\n- Bridge updates every [PLACEHOLDER: bank-set interval].\n",
              BASE + "\n- Step 3 of 8: reconcile SHA-256 hashes at T+0.\n"]
        for txt in ok:
            self.assertEqual(self.lint(txt), [])

    def test_contacts_and_urls_flagged(self):
        self.assertFlags(BASE + "\nCall 555-123-4567.\n", "phone number")
        self.assertFlags(BASE + "\nEmail incident@example.com\n", "e-mail address")
        self.assertFlags(BASE + "\nSee https://status.example.invalid\n", "URL")

    def test_detector_catches_fictional_vendor_numbers_in_assessment_example(self):
        # The Acme assessment example intentionally contains fictional vendor numbers; the
        # scenario rule must flag them if such text were pasted into a scenario.
        ex = (HERE / "examples" / "acme-core-ledger-SIMULATION-assessment.md").read_text(encoding="utf-8")
        self.assertTrue(any("SLA-like" in f for f in self.lint(ex)))


class RaciLint(unittest.TestCase):
    def test_example_raci_passes(self):
        self.assertEqual(cg.raci_findings(RACI), [])

    def test_blank_template_fails(self):
        self.assertTrue(cg.raci_findings(HERE / "raci-matrix-template.md"))

    def test_two_accountables_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.md"
            p.write_text(RACI.read_text().replace("| A | R | I | C | C | C | I | I |",
                                                  "| A | A | I | C | C | C | I | I |", 1))
            self.assertTrue(any("2 Accountable" in f for f in cg.raci_findings(p)))


if __name__ == "__main__":
    unittest.main()
