"""Negative tests for scripts/ci/check_labels.py: removing any SIMULATION / PLAN_ONLY marker must fail."""
import io, shutil, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_labels as cl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
PARTS = ["evidence/incident", "scenarios/incident", "identity/m365/README.md", "evidence/m365"]
PRESENT = all((ROOT / p).exists() for p in PARTS)


@unittest.skipUnless(PRESENT, "modules not integrated (the required label job fails closed separately)")
class Labels(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for p in PARTS:
            src, dst = ROOT / p, self.tmp / p
            dst.parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree if src.is_dir() else shutil.copy2)(src, dst)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rc(self):
        with redirect_stdout(io.StringIO()):
            return cl.main(["--root", str(self.tmp)])

    def first_run(self):
        return sorted(d for d in (self.tmp / "evidence/incident/runs").iterdir() if d.is_dir())[0]

    def test_pristine_passes(self):
        self.assertEqual(self.rc(), 0)

    def test_missing_run_label_fails(self):
        (self.first_run() / "SIMULATION.md").unlink()
        self.assertEqual(self.rc(), 1)

    def test_weakened_run_label_fails(self):
        p = self.first_run() / "SIMULATION.md"
        p.write_text(p.read_text().replace("**SIMULATION.**", "Note."))
        self.assertEqual(self.rc(), 1)

    def test_unlabelled_script_fails(self):
        p = self.tmp / "scenarios/incident/selftest.sh"
        lines = p.read_text().splitlines(True)
        p.write_text("".join(l.replace("SIMULATION", "demo") for l in lines[:3]) + "".join(lines[3:]))
        self.assertEqual(self.rc(), 1)

    def test_m365_plan_only_statement_removed_fails(self):
        p = self.tmp / "identity/m365/README.md"
        p.write_text(p.read_text().replace("PLAN_ONLY", "PLANNED"))
        self.assertEqual(self.rc(), 1)

    def test_m365_mutations_marker_changed_fails(self):
        p = next((self.tmp / "evidence/m365/runs").glob("*/SUMMARY.md"))
        p.write_text(p.read_text().replace("Mutations executed | `0`", "Mutations executed | `2`"))
        self.assertEqual(self.rc(), 1)

    def test_missing_module_fails_closed(self):
        shutil.rmtree(self.tmp / "evidence/incident")
        self.assertEqual(self.rc(), 1)


if __name__ == "__main__":
    unittest.main()
