"""SIMULATION - offline tests for governance/vendor-risk/check_governance.py."""
import importlib.util
import shutil
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
            return cg.scenario_findings(p, link_base=SCENARIO.parent)

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
        self.assertFlags(BASE + "\nJack Henry restores the core quickly.\n", "outside the 'Real vendor vs fictional system'")

    def test_jack_henry_statement_required(self):
        txt = BASE.replace("Jack Henry", "A vendor")
        self.assertFlags(txt, "does not name the real vendor")

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

    def test_banno_outside_context_section_flagged(self):
        self.assertFlags(BASE + "\nThe Banno app shows stale balances.\n", "outside the 'Real vendor vs fictional system'")

    def test_real_vendor_in_injects_flagged(self):
        txt = BASE.replace("The fictional vendor status page", "The Jack Henry status page", 1)
        self.assertNotEqual(txt, BASE)
        self.assertFlags(txt, "outside the 'Real vendor vs fictional system'")

    def test_context_section_statements_required(self):
        for remove, needle in [("does **not** reflect", "does not reflect"),
                               ("integrations/vendor-mock", "integrations/vendor-mock"),
                               ("job posting", "job posting")]:
            with self.subTest(needle):
                txt = BASE.replace(remove, "XXX")
                if needle == "job posting":
                    txt = txt.replace("job description", "XXX")
                self.assertFlags(txt, f"missing statement containing {needle!r}")

    def test_broken_relative_link_flagged(self):
        self.assertFlags(BASE + "\nSee [x](../does-not-exist.md).\n", "broken relative link")

    def test_unknown_mock_scenario_flagged(self):
        self.assertFlags(BASE + "\nAnalogue: `malformed_does_not_exist`.\n", "unknown vendor-mock scenario")

    def test_no_mock_analogue_flagged(self):
        txt = cg.MOCK_SCENARIO_RX.sub("`x`", BASE)
        self.assertFlags(txt, "no vendor-mock failure scenarios cited")

    def test_mock_scenarios_parsed(self):
        self.assertIn("malformed_extra_field", cg.mock_scenarios())
        self.assertGreaterEqual(len(cg.mock_scenarios()), 20)


class AssessmentVendorNumbers(unittest.TestCase):
    EX = HERE / "examples" / "acme-core-ledger-SIMULATION-assessment.md"

    def test_assessment_example_has_no_vendor_numbers(self):
        self.assertEqual(cg.vendor_number_findings(self.EX, strict=True), [])
        self.assertIn(cg.CONTRACT_PLACEHOLDER, self.EX.read_text(encoding="utf-8"))

    def test_injected_vendor_sla_in_assessment_flagged(self):
        for line in ["| C7 | `[x]` 99.9 % monthly uptime SLA; status page | — |",
                     "| B1 | Vendor RTO 4 h / RPO 15 min |",
                     "| E2 | Vendor gives 90 days for API deprecation |",
                     "| X2 | Vendor deletion certificate within 60 days |",
                     "| C1 | SOC 2-style report for a 12-month period |"]:
            with self.subTest(line):
                with tempfile.TemporaryDirectory() as d:
                    p = Path(d) / "a.md"
                    p.write_text(self.EX.read_text(encoding="utf-8") + "\n" + line + "\n")
                    self.assertTrue(cg.vendor_number_findings(p, strict=True))


class MockNaming(unittest.TestCase):
    def test_committed_mock_never_names_real_vendor(self):
        self.assertEqual(cg.mock_naming_findings(), [])

    def test_real_vendor_in_mock_flagged(self):
        for rel, text in [("fixtures/accounts.json", '"_note": "Jack Henry account"'),
                          ("vendor_mock/client.py", "# compatible with BANNO"),
                          ("contract/openapi.json", "jackhenry")]:
            with self.subTest(rel):
                with tempfile.TemporaryDirectory() as d:
                    root = Path(d) / "vendor-mock"
                    shutil.copytree(cg.MOCK_ROOT, root, ignore=shutil.ignore_patterns("__pycache__"))
                    f = root / rel
                    f.write_text(f.read_text(encoding="utf-8") + "\n" + text + "\n", encoding="utf-8")
                    self.assertTrue(any(rel in x for x in cg.mock_naming_findings(root)))

    def test_mock_readme_disclaimer_is_allowed(self):
        self.assertRegex((cg.MOCK_ROOT / "README.md").read_text(encoding="utf-8"), "Jack Henry")


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
