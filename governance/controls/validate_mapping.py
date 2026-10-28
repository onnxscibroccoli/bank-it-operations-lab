#!/usr/bin/env python3
"""Validate the FFIEC AIO control mapping (stdlib only).

Checks:
  * ffiec-aio-mapping.csv: required columns, unique row ids, allowed status values,
    AIO section ids that exist in the June 2021 booklet table of contents.
  * ffiec-aio-artifacts.csv: every referenced (commit, path) exists in git
    (`git cat-file -e <commit>:<path>`), commits are full 40-hex SHAs, every row id
    is mapped, every mapping row has at least one artifact, and SIMULATION / OBSERVED
    rows cite at least one artifact with role=evidence.
  * Optionally (--check-branches) each commit is an ancestor of origin/<source_branch>.
  * ffiec-aio-mapping.md mentions every row id and avoids certification wording.

Exit 0 = valid, 1 = findings, 2 = usage / environment error.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

STATUSES = {"STATIC", "SIMULATION", "OBSERVED", "NOT_EXECUTED"}
EVIDENCE_REQUIRED = {"SIMULATION", "OBSERVED"}
ROLES = {"implementation", "test", "evidence", "documentation"}

# Section ids from the AIO booklet (June 2021) table of contents.
AIO_SECTIONS = set("""
I II II.A II.A.1 II.A.2 II.B II.B.1 II.B.1(a) II.B.1(b) II.B.1(c) II.B.2 II.C II.D II.E II.F
III III.A III.A.1 III.A.2 III.A.2(a) III.A.3 III.A.4 III.B III.B.1 III.B.1(a) III.B.1(b) III.B.2 III.B.3
III.C III.C.1 III.C.2 III.C.3 III.D III.D.1 III.D.2 III.E III.F III.G III.H III.I
IV IV.A IV.B IV.C IV.D
V V.A V.B V.B.1 V.B.2 V.B.2(a) V.B.2(b) V.C V.C.1 V.C.2 V.C.2(a) V.C.2(b) V.C.2(c) V.C.3
V.D V.D.1 V.D.2 V.D.3 V.D.4 V.E
VI VI.A VI.A.1 VI.A.2 VI.A.3 VI.A.4 VI.B VI.B.1 VI.B.2 VI.B.3 VI.B.3(a) VI.B.3(b) VI.B.4 VI.B.5
VI.B.6 VI.B.7 VI.B.8 VI.C VI.C.1 VI.C.2 VI.C.3 VI.C.4 VI.D VI.D.1 VI.D.2 VI.D.3 VI.D.4
VII VII.A VII.A.1 VII.A.2 VII.A.3 VII.A.4 VII.A.5 VII.A.5(a) VII.B VII.C VII.D VII.E
""".split())

MAPPING_COLS = ["row_id", "aio_id", "aio_title", "booklet_page", "status", "lab_claim",
                "limitations", "organizational_dependencies"]
ARTIFACT_COLS = ["row_id", "role", "path", "commit", "source_branch", "pr", "note"]

# Wording that would read as a compliance opinion. Matched case-insensitively.
BANNED = [r"\bis compliant\b", r"\bare compliant\b", r"\bfully compliant\b", r"\bcertified\b",
          r"\bsatisfies\b", r"\bfully meets\b", r"\bmeets (the )?(ffiec )?requirements?\b",
          r"\bin compliance with\b", r"\bpasses (the )?exam"]

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def read_csv(path: Path, cols: list[str]) -> tuple[list[dict], list[str]]:
    errs: list[str] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != cols:
            errs.append(f"{path.name}: columns {reader.fieldnames} != expected {cols}")
            return [], errs
        rows = list(reader)
    return rows, errs


def git_has(repo: Path, commit: str, path: str) -> bool:
    r = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}:{path}"],
                       capture_output=True)
    return r.returncode == 0


def git_is_ancestor(repo: Path, commit: str, ref: str) -> bool | None:
    if subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", ref],
                      capture_output=True).returncode != 0:
        return None
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, ref],
                          capture_output=True).returncode == 0


def validate(mapping_csv: Path, artifacts_csv: Path, mapping_md: Path | None, repo: Path,
             check_branches: bool = False) -> list[str]:
    errs: list[str] = []
    mapping, e = read_csv(mapping_csv, MAPPING_COLS)
    errs += e
    artifacts, e = read_csv(artifacts_csv, ARTIFACT_COLS)
    errs += e
    if errs:
        return errs

    ids: dict[str, dict] = {}
    for i, row in enumerate(mapping, start=2):
        rid = row["row_id"]
        if rid in ids:
            errs.append(f"mapping line {i}: duplicate row_id {rid}")
        ids[rid] = row
        if row["status"] not in STATUSES:
            errs.append(f"mapping {rid}: status {row['status']!r} not in {sorted(STATUSES)}")
        if row["aio_id"] not in AIO_SECTIONS:
            errs.append(f"mapping {rid}: aio_id {row['aio_id']!r} is not an AIO booklet section id")
        if not row["booklet_page"].isdigit():
            errs.append(f"mapping {rid}: booklet_page {row['booklet_page']!r} is not a page number")
        for col in ("lab_claim", "limitations", "organizational_dependencies"):
            if not row[col].strip():
                errs.append(f"mapping {rid}: empty {col}")

    by_row: dict[str, list[dict]] = {rid: [] for rid in ids}
    for i, a in enumerate(artifacts, start=2):
        rid = a["row_id"]
        where = f"artifacts line {i} ({rid} {a['path']})"
        if rid not in ids:
            errs.append(f"{where}: unknown row_id")
            continue
        by_row[rid].append(a)
        if a["role"] not in ROLES:
            errs.append(f"{where}: role {a['role']!r} not in {sorted(ROLES)}")
        if not SHA_RE.match(a["commit"]):
            errs.append(f"{where}: commit {a['commit']!r} is not a full 40-hex SHA")
            continue
        if not git_has(repo, a["commit"], a["path"]):
            errs.append(f"{where}: path does not exist at commit {a['commit'][:12]}")
        if check_branches:
            anc = git_is_ancestor(repo, a["commit"], f"origin/{a['source_branch']}")
            if anc is None:
                errs.append(f"{where}: ref origin/{a['source_branch']} not found")
            elif not anc:
                errs.append(f"{where}: commit is not on origin/{a['source_branch']}")

    for rid, row in ids.items():
        arts = by_row.get(rid, [])
        if not arts:
            errs.append(f"mapping {rid}: no artifacts referenced")
        if row["status"] in EVIDENCE_REQUIRED and not any(a["role"] == "evidence" for a in arts):
            errs.append(f"mapping {rid}: status {row['status']} needs at least one role=evidence artifact")

    if mapping_md is not None:
        text = mapping_md.read_text(encoding="utf-8")
        for rid in ids:
            if rid not in text:
                errs.append(f"{mapping_md.name}: row {rid} not mentioned")
        for pat in BANNED:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                errs.append(f"{mapping_md.name}: certification-style wording {m.group(0)!r}")
    return errs


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mapping", type=Path, default=HERE / "ffiec-aio-mapping.csv")
    p.add_argument("--artifacts", type=Path, default=HERE / "ffiec-aio-artifacts.csv")
    p.add_argument("--markdown", type=Path, default=HERE / "ffiec-aio-mapping.md")
    p.add_argument("--repo", type=Path, default=HERE.parent.parent)
    p.add_argument("--check-branches", action="store_true",
                   help="also require each commit to be on origin/<source_branch>")
    args = p.parse_args(argv)
    if subprocess.run(["git", "-C", str(args.repo), "rev-parse"], capture_output=True).returncode:
        print(f"error: {args.repo} is not a git repository", file=sys.stderr)
        return 2
    errs = validate(args.mapping, args.artifacts, args.markdown, args.repo, args.check_branches)
    with args.mapping.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with args.artifacts.open(newline="", encoding="utf-8") as fh:
        n_art = sum(1 for _ in csv.DictReader(fh))
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in sorted(STATUSES)}
    print(f"rows={len(rows)} artifacts={n_art} " + " ".join(f"{k}={v}" for k, v in counts.items()))
    for e in errs:
        print(f"FINDING: {e}")
    print("MAPPING VALID" if not errs else f"MAPPING INVALID ({len(errs)} findings)")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
