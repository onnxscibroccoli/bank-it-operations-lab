import json
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
class PortalTests(unittest.TestCase):
    def test_build_and_inventory(self):
        result = subprocess.run(['python3', 'scripts/docs/build.py'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        pages = json.loads((ROOT/'dist/docs/search-index.json').read_text())
        self.assertGreaterEqual(len(pages), 207)
        self.assertTrue(any(p['path']=='tests/integration/README.md' for p in pages))
        for p in pages:
            self.assertTrue((ROOT/'dist/docs'/p['url']).is_file(), p['path'])
            self.assertTrue(p['status'])
    def test_unsafe_html_is_inert(self):
        import sys
        sys.path.insert(0, str(ROOT/'scripts/docs'))
        import build
        rendered = build.render('[bad](javascript:alert(1))<script>alert(1)</script>')
        self.assertNotIn('href="javascript:', rendered)
        self.assertNotIn('<script>', rendered)
    def test_invalid_metadata_rejected(self):
        import sys
        sys.path.insert(0, str(ROOT/'scripts/docs'))
        import build
        with self.assertRaises(Exception):
            build.validate_metadata({'bad': {'status': 'Production Verified'}})
if __name__ == '__main__': unittest.main()
