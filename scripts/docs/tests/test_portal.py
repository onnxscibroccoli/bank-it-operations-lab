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
            # GitHub Pages artifacts omit dot-prefixed paths; such URLs would 404 when published.
            self.assertFalse(any(seg.startswith('.') for seg in p['url'].split('/')), p['url'])
            self.assertTrue(p['owner_module'], p['path'])
        sections = ['start', 'topics', 'tutorials', 'reference', 'troubleshooting', 'development', 'ai']
        home = (ROOT/'dist/docs/index.html').read_text()
        for name in sections:
            url = f'pages/docs/knowledge/{name}.html'
            self.assertTrue((ROOT/'dist/docs'/url).is_file(), url)
            self.assertIn(f'href="{url}"', home)
        topics = (ROOT/'dist/docs/pages/docs/knowledge/topics.html').read_text()
        for p in pages:
            self.assertIn('/'+p['url'].split('pages/',1)[1], topics.replace('../../../pages', ''), p['path'])
    def test_internal_heading_anchors_resolve(self):
        import html, posixpath, re
        from urllib.parse import urlsplit, unquote
        out = ROOT/'dist/docs'
        if not (out/'search-index.json').is_file():
            subprocess.run(['python3', 'scripts/docs/build.py'], cwd=ROOT, check=True, capture_output=True)
        pages = json.loads((out/'search-index.json').read_text())
        cache, broken = {}, []
        for p in pages:
            for href in re.findall(r'href="([^"]+)"', (out/p['url']).read_text()):
                u = urlsplit(html.unescape(href))
                if u.scheme or not u.fragment:
                    continue
                target = posixpath.normpath(posixpath.join(posixpath.dirname(p['url']), unquote(u.path))) if u.path else p['url']
                if target not in cache:
                    f = out/target
                    cache[target] = set(re.findall(r'id="([^"]+)"', f.read_text())) if f.is_file() else set()
                if u.fragment not in cache[target]:
                    broken.append((p['path'], href))
        self.assertEqual(broken, [])
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
