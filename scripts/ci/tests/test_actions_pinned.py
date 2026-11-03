"""T-11: every `uses:` in .github/workflows is a local reusable workflow or pinned to a full 40-hex commit SHA."""
import re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
USES = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.M)


def unpinned(text):
    return [u for u in USES.findall(text) if not u.startswith("./") and not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", u)]


class ActionsPinned(unittest.TestCase):
    def test_all_workflows_pinned(self):
        bad = {p.name: unpinned(p.read_text()) for p in sorted((ROOT / ".github/workflows").glob("*.yml"))}
        self.assertEqual({k: v for k, v in bad.items() if v}, {})

    def test_detector_rejects_tags_branches_and_short_shas(self):
        for line in ("- uses: actions/checkout@v4", "  uses: actions/deploy-pages@main", "- uses: actions/setup-node@49933ea",
                     "- uses: actions/checkout@V4 # 11d5960a326750d5838078e36cf38b85af677262"):
            with self.subTest(line=line):
                self.assertTrue(unpinned(line))
        self.assertFalse(unpinned("- uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4\n    uses: ./.github/workflows/aws-cdk.yml"))


if __name__ == "__main__":
    unittest.main()
