import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('portfolio_summary', ROOT / 'portfolio_summary.py')
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class PortfolioSummaryTests(unittest.TestCase):
    def success(self):
        return {job: {'result': 'success'} for job in summary.REQUIRED}

    def test_all_required_jobs_must_succeed(self):
        self.assertTrue(summary.evaluate(self.success())[1])
        for job in summary.REQUIRED:
            for state in ('failure', 'cancelled', 'skipped', '', None):
                with self.subTest(job=job, state=state):
                    jobs = self.success()
                    jobs[job]['result'] = state
                    self.assertFalse(summary.evaluate(jobs)[1])

    def test_missing_and_malformed_results_fail(self):
        for data in (None, [], {}, {'offline': None}):
            self.assertFalse(summary.evaluate(data)[1])
        for job in summary.REQUIRED:
            jobs = self.success()
            del jobs[job]
            self.assertFalse(summary.evaluate(jobs)[1])

    def test_unexpected_failure_is_not_ignored(self):
        jobs = self.success()
        jobs['additional-check'] = {'result': 'failure'}
        self.assertFalse(summary.evaluate(jobs)[1])

    def test_failure_still_writes_artifact_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            out, md = Path(directory) / 'report.json', Path(directory) / 'summary.md'
            with patch.dict(os.environ, {'NEEDS_JSON': '{bad', 'GITHUB_SHA': 'a' * 40}):
                self.assertEqual(summary.main(['--out', str(out), '--summary', str(md)]), 1)
            report = json.loads(out.read_text())
            self.assertFalse(report['validationPassed'])
            self.assertFalse(report['approvalEffective'])
            self.assertIn('USER ACTION REQUIRED:', md.read_text())
            self.assertEqual(report['testedSha'], 'a' * 40)

    def test_workflow_dependencies_match_summary_inventory(self):
        # JSON-compatible inline needs lists avoid a PyYAML runtime dependency.
        workflow = (ROOT.parents[1] / '.github/workflows/portfolio-validation.yml').read_text()
        block = workflow.split('  run-summary:\n', 1)[1]
        needs = block.split('    needs: ', 1)[1].splitlines()[0]
        self.assertEqual(set(json.loads(needs)), set(summary.REQUIRED))
        self.assertIn('    if: always()', block)


if __name__ == '__main__':
    unittest.main()
