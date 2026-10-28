"""Guards: fixtures are synthetic and in sync; governance code has no network/credential path."""
import ast
import json
import os
import re
import subprocess
import sys
import unittest

import _common

GOV = _common.GOV
GUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
SYNTHETIC = re.compile(r"^b9a5e000-0000-4000-8000-[0-9a-f]{12}$")
EMAIL = re.compile(r"[A-Za-z0-9._%+#-]+@([A-Za-z0-9.-]+)")


def allowed_constants():
    with open(os.path.join(GOV, "baseline.json")) as fh:
        b = json.load(fh)
    ids = set(b["privilegedRoleTemplateIds"]) | {
        "f2ef992c-3afb-46b9-b7cf-a126ee74c451",  # Global Reader (built-in template)
        "88d8e3e3-8f55-4a1e-953a-9b9898b8876b",  # Directory Readers (built-in template)
        "00000000-0000-0000-0000-000000000000",  # Graph "no reviewer" placeholder
    }
    return ids


def fixture_files():
    for dp, _, fns in os.walk(os.path.join(GOV, "fixtures")):
        for fn in sorted(fns):
            yield os.path.join(dp, fn)


class TestSynthetic(unittest.TestCase):
    def test_every_guid_is_synthetic_or_published_constant(self):
        allowed = allowed_constants()
        for p in fixture_files():
            with open(p) as fh:
                text = fh.read()
            for g in GUID.findall(text):
                with self.subTest(file=os.path.relpath(p, GOV), guid=g):
                    self.assertTrue(SYNTHETIC.match(g) or g in allowed, g)

    def test_every_email_domain_is_reserved(self):
        for p in fixture_files():
            with open(p) as fh:
                for dom in EMAIL.findall(fh.read()):
                    self.assertTrue(dom.endswith(".example") or dom.endswith(".invalid"), (p, dom))

    def test_only_graph_urls(self):
        for p in fixture_files():
            with open(p) as fh:
                for url in re.findall(r"https?://[^\s\"']+", fh.read()):
                    self.assertTrue(url.startswith("https://graph.microsoft.com/v1.0/"), (p, url))

    def test_fixtures_in_sync_with_generator(self):
        r = subprocess.run([sys.executable, os.path.join(GOV, "make_fixtures.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestNoNetwork(unittest.TestCase):
    FORBIDDEN = {"socket", "ssl", "http", "urllib", "requests", "httpx", "aiohttp", "msal", "azure", "boto3"}

    def test_no_network_or_identity_sdk_imports(self):
        for fn in sorted(os.listdir(GOV)):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(GOV, fn)) as fh:
                tree = ast.parse(fh.read())
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for n in names:
                    with self.subTest(file=fn, module=n):
                        self.assertNotIn(n.split(".")[0], self.FORBIDDEN)


if __name__ == "__main__":
    unittest.main()
