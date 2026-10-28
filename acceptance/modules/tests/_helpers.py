"""Test helpers: copy existing evidence to a temp dir and re-seal hashes so a tamper is isolated
to the one fault under test (otherwise every negative test would just fail on hashes)."""
import hashlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def copytree(src, td):
    dst = Path(td) / Path(src).name
    shutil.copytree(src, dst)
    return dst


def reseal_listed(sums: Path):
    """Recompute every hash already listed in SHA256SUMS ("<hex>  <path>"), dropping missing files."""
    out = []
    for line in sums.read_text().splitlines():
        h, _, name = line.partition("  ")
        p = sums.parent / name
        if p.is_file():
            out.append(f"{sha(p)}  {name}")
    sums.write_text("\n".join(out) + "\n")


def reseal_all(run_dir: Path):
    """Postgres v2 layout: SHA256SUMS covers every file except itself and artifacts/."""
    lines = []
    for root, _, files in os.walk(run_dir):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), run_dir)
            if rel == "SHA256SUMS" or rel.startswith("artifacts" + os.sep):
                continue
            lines.append(f"{sha(run_dir / rel)}  {rel}")
    (run_dir / "SHA256SUMS").write_text("\n".join(sorted(lines, key=lambda l: l.split('  ', 1)[1])) + "\n")


def by_id(result):
    return {c.id: c for c in result.checks}


def non_pass(result):
    return {c.id: c.reason_code for c in result.checks if c.status != "PASS"}


class TmpMixin:
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="acc-test-")
        self.td = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()
