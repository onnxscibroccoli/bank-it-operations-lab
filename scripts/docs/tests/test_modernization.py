import copy,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/docs'))
import build
class ModernizationTests(unittest.TestCase):
    def test_every_document_has_metadata(self):
        data=json.loads((ROOT/'docs/metadata/pages.json').read_text())
        self.assertEqual(set(build.files())-set(data),set())
    def test_bad_verification_date_is_rejected(self):
        data=json.loads((ROOT/'docs/metadata/pages.json').read_text())
        data['docs/knowledge/start.md']['verification']['last_verified']='yesterday'
        with self.assertRaises(Exception): build.validate_metadata(data)
    def test_nonexistent_evidence_is_rejected(self):
        data=json.loads((ROOT/'docs/metadata/pages.json').read_text())
        data['docs/knowledge/start.md']['verification'].update(level='Locally Verified',last_verified='2026-10-31',evidence=['missing-evidence.json'])
        with self.assertRaises(Exception): build.validate_metadata(data)
    def test_frozen_records_unchanged(self):
        import hashlib
        manifest=json.loads((ROOT/'docs/metadata/preserved-records.json').read_text())
        self.assertGreater(len(manifest),67)
        for path,digest in manifest.items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
    def test_terminology_is_consistent_and_discoverable(self):
        terms=json.loads((ROOT/'docs/metadata/terminology.json').read_text())
        self.assertEqual(terms['schema_version'],1)
        glossary=(ROOT/'docs/knowledge/glossary.md').read_text().casefold()
        for term,definition in terms['definitions'].items():
            self.assertTrue(definition.strip(),term)
            self.assertIn(term.casefold(),glossary)
        pages=json.loads((ROOT/'docs/metadata/pages.json').read_text())
        for page in pages.values():
            for term,definition in page.get('reading_guide',{}).get('terms',{}).items():
                self.assertEqual(terms['definitions'][term],definition)
