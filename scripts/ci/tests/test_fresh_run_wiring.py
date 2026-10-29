"""Static guard: the fresh incident run must use apt-installed PostgreSQL SERVER binaries, never a services container,
and harness exit 3 (NOT_EXECUTED) must fail the required check."""
import re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATE = (ROOT / ".github/workflows/integration-gate.yml").read_text()
CHECKS = (ROOT / "scripts/ci/incident_checks.sh").read_text()


def job_block(name):
    m = re.search(r"(?ms)^  " + re.escape(name) + r":\n(.*?)(?=^  [a-z0-9-]+:\n|\Z)", GATE)
    return m.group(1) if m else ""


class FreshRunWiring(unittest.TestCase):
    def test_no_services_container(self):
        b = job_block("incident-fresh-run")
        self.assertTrue(b, "incident-fresh-run job missing")
        self.assertNotRegex(b, r"(?m)^    services:")
        self.assertNotIn("container:", b)

    def test_apt_installs_server_binaries_and_path(self):
        b = job_block("incident-fresh-run")
        self.assertIn("apt-get install -y -qq postgresql-16", b)
        self.assertIn("GITHUB_PATH", b)
        self.assertIn("command -v initdb", b)

    def test_fresh_step_not_skippable_or_continue_on_error(self):
        b = job_block("incident-fresh-run")
        step = b[b.index("Fresh SIMULATION incident run"):]
        step = step[:step.index("- name: Requirement outputs")]
        self.assertNotIn("continue-on-error", step)
        self.assertNotIn("if:", step)
        self.assertNotIn("continue-on-error", b.split("steps:")[0])

    def test_exit_3_fails(self):
        self.assertRegex(CHECKS, r'\[ "\$rc" -eq 3 \] && fail ')


if __name__ == "__main__":
    unittest.main()
