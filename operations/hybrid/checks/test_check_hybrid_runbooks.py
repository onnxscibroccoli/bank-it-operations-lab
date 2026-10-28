"""Offline tests for check_hybrid_runbooks.py (stdlib unittest)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_hybrid_runbooks as chk  # noqa: E402

GOOD = """# Runbook: x

> **Execution status: NOT_EXECUTED.** Plan only.

## Purpose
## Scope
## Preconditions
## Procedure
```
Execution status: EXECUTED_IN_LAB | PARTIAL
```
## Verification
## Rollback
## Evidence
"""


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs/runbooks/hybrid").mkdir(parents=True)
        (self.root / "operations/hybrid").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.write_text(text, encoding="utf-8")
        return p

    def findings(self, rel, text):
        return chk.check_file(self.write(rel, text), self.root)

    def test_good_runbook_passes(self):
        self.assertEqual(self.findings("docs/runbooks/hybrid/a.md", GOOD), [])

    def test_missing_banner(self):
        f = self.findings("docs/runbooks/hybrid/a.md", GOOD.replace("NOT_EXECUTED", "TBD"))
        self.assertTrue(any("banner" in x for x in f))

    def test_missing_section(self):
        f = self.findings("docs/runbooks/hybrid/a.md", GOOD.replace("## Rollback\n", ""))
        self.assertTrue(any("Rollback" in x for x in f))

    def test_broken_link(self):
        f = self.findings("operations/hybrid/r.md", GOOD + "\n[x](missing.md)\n")
        self.assertTrue(any("broken link" in x for x in f))

    def test_secret_detected(self):
        f = self.findings("operations/hybrid/r.md", GOOD + "\npassword = Hunter2!!\n")
        self.assertTrue(any("secret-like" in x for x in f))

    def test_read_host_not_flagged(self):
        f = self.findings("operations/hybrid/r.md", GOOD + "\nPassword: (Read-Host -AsSecureString)\n")
        self.assertEqual(f, [])

    def test_executed_claim_outside_code(self):
        f = self.findings("operations/hybrid/r.md", GOOD + "\nExecution status: EXECUTED_IN_LAB\n")
        self.assertTrue(any("claims execution" in x for x in f))

    def test_public_ip_flagged(self):
        f = self.findings("operations/hybrid/r.md", GOOD + "\n8.8.8.8\n")
        self.assertTrue(any("IPv4" in x for x in f))

    def test_status_table_row(self):
        body = GOOD + "\n| [a](a.md) | EXECUTED_IN_LAB | x |\n"
        self.write("operations/hybrid/a.md", GOOD)
        f = self.findings("operations/hybrid/EXECUTION_STATUS.md", body)
        self.assertTrue(any("status row" in x for x in f))

    def test_real_tree_passes(self):
        self.assertEqual(chk.main(chk.REPO), 0)


if __name__ == "__main__":
    unittest.main()
