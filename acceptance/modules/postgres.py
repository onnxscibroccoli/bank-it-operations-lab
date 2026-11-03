"""Acceptance adapter: PostgreSQL backup/restore exercise, harness v2 (PR #2 @ e7399fb via overnight/integration).

Wraps -- does not rebuild -- the existing module:
  * committed harness-v2 runs listed in evidence/postgres/runs/INDEX.md
  * PR #2's independent verifier  tests/integration/postgres/verify_evidence.py (0 verified / 1 rejected / 3 historical)
  * PR #3's shared cross-check    evidence/shared/validate_evidence.py postgres-negatives
  * live-offline mode only: tests/integration/postgres/run_restore_scenario.sh offline (unix-socket throwaway
    cluster under a temp dir; needs PG binaries via PG_BIN or PATH), then the verifier with --require-artifacts.
"""
from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from . import _util as U
from .contract import ModuleResult, check

VERSION = "0.1.0"
MODULE = "postgres"
RUNS = U.ROOT / "evidence/postgres/runs"
VERIFIER = U.ROOT / "tests/integration/postgres/verify_evidence.py"
SCENARIO = U.ROOT / "tests/integration/postgres/run_restore_scenario.sh"
SHARED_V = U.ROOT / "evidence/shared/validate_evidence.py"
MIN_NEGATIVES = 6  # N01..N06 in tests/integration/postgres/expectations.tsv
CONTROL_REASON = "version_mismatch"  # the mismatch control must be rejected for this declared class

# verifier ERROR line -> reason code; first match wins, and the primary reason follows this priority.
_PATTERNS = [
    (re.compile(r"^(hash:|artifact hash|SHA256SUMS missing)"), "EVIDENCE_HASH_MISMATCH"),
    (re.compile(r"unexpected success"), "NEGATIVE_UNEXPECTED_SUCCESS"),
    (re.compile(r"reason_regex not found|negative case without declared reason"), "NEGATIVE_WRONG_REASON"),
    (re.compile(r"^SUMMARY\.json"), "RUN_FAILED"),
]
_PRIORITY = ["EVIDENCE_HASH_MISMATCH", "NEGATIVE_UNEXPECTED_SUCCESS", "NEGATIVE_WRONG_REASON", "CASE_FAILED", "RUN_FAILED"]


def classify_verifier_output(out: str) -> List[str]:
    codes = []
    for line in out.splitlines():
        if not line.startswith("ERROR "):
            continue
        msg = line[6:]
        code = next((c for rx, c in _PATTERNS if rx.search(msg)), "CASE_FAILED")
        if code not in codes:
            codes.append(code)
    return sorted(codes, key=_PRIORITY.index)


def parse_index(index: Path) -> Dict[str, List[str]]:
    """Classify runs from INDEX.md: verified (v2 CURRENT), control (v2 negative control), historical."""
    out = {"verified": [], "control": [], "historical": []}
    for line in index.read_text().splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|", line)
        if not m:
            continue
        name, harness, status = m.group(1), m.group(2).strip(), m.group(3)
        if "HISTORICAL" in status:
            out["historical"].append(name)
        elif harness == "v2" and "CURRENT" in status:
            if "negative control" in status:
                out["control"].append(name)
            elif "selftest" not in name:
                out["verified"].append(name)
    return out


def _verify(run_dir: Path, extra=()):
    rc, out = U.py(str(VERIFIER), str(run_dir), *extra)
    m = re.search(r"negative=(\d+)", out)
    return rc, out, int(m.group(1)) if m else 0


def _verified_run_checks(res: ModuleResult, run_dir: Path, cid: str, extra=()):
    rc, out, neg = _verify(run_dir, extra)
    if rc == 3:
        res.add(check(cid, f"{run_dir.name}: v2 verifier VERIFIED", "integrity", False, "EVIDENCE_HISTORICAL",
                      out.strip().splitlines()[0][:300], [U.rel(run_dir)]))
        return False
    codes = classify_verifier_output(out) if rc != 0 else []
    if rc not in (0, 1) and not codes:
        codes = ["TOOL_ERROR"]
    errs = [l[6:] for l in out.splitlines() if l.startswith("ERROR ")]
    res.add(check(cid, f"{run_dir.name}: v2 verifier VERIFIED (hashes, 1 row/case, reason re-derived from logs)",
                  "positive", rc == 0, codes[0] if codes else "CASE_FAILED",
                  ("; ".join(errs[:6]) if errs else out.strip().splitlines()[-1])[:600], [U.rel(run_dir)]))
    if rc != 0:
        return False
    res.add(check(cid + "N", f"{run_dir.name}: >= {MIN_NEGATIVES} negative cases declared", "negative",
                  neg >= MIN_NEGATIVES, "NEGATIVE_COUNT", f"negative={neg}", [U.rel(run_dir)]))
    rc2, out2 = U.py(str(SHARED_V), "postgres-negatives", str(run_dir))
    res.add(check(cid + "X", f"{run_dir.name}: shared validator agrees every negative failed for its intended reason",
                  "negative", rc2 == 0, "NEGATIVE_WRONG_REASON", out2.strip().splitlines()[-1][:300] if out2.strip() else "",
                  [U.rel(run_dir)]))
    return True


def run(mode: str = "static-evidence", runs_dir: Optional[Path] = None, pg_bin: Optional[str] = None) -> ModuleResult:
    runs = Path(runs_dir or RUNS)
    res = ModuleResult(MODULE, f"acceptance/modules/postgres.py@{VERSION}",
                       {"prs": [2, 3], "paths": ["tests/integration/postgres", U.rel(runs),
                                                 "evidence/shared/validate_evidence.py"]},
                       mode, git_sha=U.git_sha())
    index = runs / "INDEX.md"
    if not index.is_file():
        res.add(check("PG-INT-000", "run index present", "integrity", False, "EVIDENCE_MISSING", f"{U.rel(index)} missing"))
        return res
    cls = parse_index(index)
    res.add(check("PG-INT-000", "INDEX.md lists >=1 CURRENT v2 run and the mismatch negative control", "integrity",
                  bool(cls["verified"]) and bool(cls["control"]), "EVIDENCE_MISSING", str(cls), [U.rel(index)]))
    ev_files = [index]
    for i, name in enumerate(cls["verified"], 1):
        d = runs / name
        _verified_run_checks(res, d, f"PG-RUN-{i:03d}")
        ev_files += [d / "SHA256SUMS", d / "SUMMARY.json"]
    for i, name in enumerate(cls["control"], 1):
        d = runs / name
        rc, out, _ = _verify(d)
        tsv = (d / "COMMANDS.tsv").read_text() if (d / "COMMANDS.tsv").is_file() else ""
        declared = any(r.split("\t")[6:7] == [CONTROL_REASON] for r in tsv.splitlines()[1:] if r.count("\t") >= 11)
        if rc == 0:
            ok, code, det = False, "CONTROL_NOT_REJECTED", "verifier VERIFIED a negative-control run"
        elif not declared:
            ok, code, det = False, "NEGATIVE_WRONG_REASON", f"rejected, but no step has class {CONTROL_REASON}"
        else:
            ok, code, det = True, "OK", f"REJECTED (exit {rc}) with declared class {CONTROL_REASON}"
        res.add(check(f"PG-CTL-{i:03d}", f"{name}: negative control is REJECTED for {CONTROL_REASON}", "negative",
                      ok, code, det, [U.rel(d)]))
        ev_files += [d / "SHA256SUMS", d / "SUMMARY.json"]
    for i, name in enumerate(cls["historical"], 1):
        rc, out, _ = _verify(runs / name)
        res.add(check(f"PG-HIST-{i:03d}", f"{name}: historical run is NOT counted as a pass (verifier exit 3)",
                      "negative", rc == 3, "CONTROL_NOT_REJECTED" if rc == 0 else "TOOL_ERROR",
                      f"verifier exit {rc}", [U.rel(runs / name)]))
    res.evidence = U.evidence_entries(ev_files)
    if mode == "live-offline":
        _live(res, pg_bin)
    return res


def find_pg_bin(pg_bin: Optional[str] = None) -> Optional[str]:
    for cand in [pg_bin, os.environ.get("PG_BIN")]:
        if cand and (Path(cand) / "initdb").exists():
            return cand
    w = shutil.which("initdb")
    if w:
        return str(Path(w).parent)
    for p in sorted(Path("/usr/lib/postgresql").glob("*/bin"), reverse=True):
        if (p / "initdb").exists():
            return str(p)
    return None


def _live(res: ModuleResult, pg_bin: Optional[str]):
    b = find_pg_bin(pg_bin)
    if not b:
        res.add(check("PG-LIVE-000", "PostgreSQL binaries available (PG_BIN/PATH)", "positive", False,
                      "TOOL_UNAVAILABLE", "set PG_BIN", status_if_fail="NOT_EXECUTED"))
        return
    with tempfile.TemporaryDirectory(prefix="acc-pg-") as td:
        env = U.offline_env({"RUN_LABEL": "acceptance-live", "EVIDENCE_DIR": td, "PG_BIN": b,
                             "PATH": b + os.pathsep + os.environ.get("PATH", "")})
        rc, out = U.run(["bash", str(SCENARIO), "offline"], env=env, timeout=900)
        res.add(check("PG-LIVE-001", "fresh offline v2 restore exercise exits 0", "positive", rc == 0, "RUN_FAILED",
                      out.strip()[-300:]))
        _verified_run_checks(res, Path(td), "PG-LIVE-002", extra=("--require-artifacts",))
