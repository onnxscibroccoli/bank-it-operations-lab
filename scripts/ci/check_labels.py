#!/usr/bin/env python3
"""Labeling-marker check (separate from the functional checks).

SIMULATION markers (incident module, PR #22):
  L1 every directory under evidence/incident/runs/ (runs and .console captures) has SIMULATION.md that starts with
     '# SIMULATION' and contains the '**SIMULATION.**' banner
  L2 evidence/incident/*.md and scenarios/incident/README.md say SIMULATION in their first 3 lines
  L3 every script under scenarios/incident/ (*.sh, lib/*.py) says SIMULATION in its first 3 lines
PLAN_ONLY markers (M365 module, PR #20):
  L4 identity/m365/README.md states PLAN_ONLY and executed: false; evidence/m365/README.md states mutationsExecuted: 0
  L5 every evidence/m365/runs/*/validation-report.md lists PLAN_ONLY steps and 'Mutations executed | 0';
     every SUMMARY.md has 'Mutations executed | `0`'
Fails closed: a missing module or zero labelled runs is an error. Usage: check_labels.py [--root DIR]
"""
import argparse, re, sys
from pathlib import Path


def head(p, n=3):
    return "".join(p.read_text(errors="replace").splitlines(True)[:n])


def check(root):
    e = []
    runs = root / "evidence/incident/runs"
    if not runs.is_dir():
        return ["L1 evidence/incident/runs missing (incident module not integrated)"]
    dirs = sorted(d for d in runs.iterdir() if d.is_dir())
    if not dirs:
        e.append("L1 no incident run directories")
    for d in dirs:
        lab = d / "SIMULATION.md"
        if not lab.exists():
            e.append(f"L1 {d.relative_to(root)}: SIMULATION.md missing")
            continue
        t = lab.read_text()
        if not t.startswith("# SIMULATION") or "**SIMULATION.**" not in t:
            e.append(f"L1 {lab.relative_to(root)}: does not start with '# SIMULATION' / lacks the **SIMULATION.** banner")
    docs = sorted((root / "evidence/incident").glob("*.md")) + [root / "scenarios/incident/README.md"]
    for p in docs:
        if not p.exists() or "SIMULATION" not in head(p):
            e.append(f"L2 {p.relative_to(root)}: SIMULATION marker missing from the first 3 lines")
    scripts = sorted((root / "scenarios/incident").glob("*.sh")) + sorted((root / "scenarios/incident/lib").glob("*.py"))
    if not scripts:
        e.append("L3 no scripts under scenarios/incident")
    for p in scripts:
        if "SIMULATION" not in head(p):
            e.append(f"L3 {p.relative_to(root)}: SIMULATION marker missing from the first 3 lines")
    ir, er = root / "identity/m365/README.md", root / "evidence/m365/README.md"
    if not ir.exists() or "PLAN_ONLY" not in ir.read_text() or "executed: false" not in ir.read_text():
        e.append("L4 identity/m365/README.md: PLAN_ONLY / executed: false statement missing")
    if not er.exists() or "mutationsExecuted: 0" not in er.read_text():
        e.append("L4 evidence/m365/README.md: mutationsExecuted: 0 statement missing")
    mruns = sorted(d for d in (root / "evidence/m365/runs").glob("*") if d.is_dir()) if (root / "evidence/m365/runs").is_dir() else []
    if not mruns:
        e.append("L5 no M365 evidence runs")
    for d in mruns:
        vr, sm = d / "validation-report.md", d / "SUMMARY.md"
        vt = vr.read_text() if vr.exists() else ""
        if "PLAN_ONLY" not in vt or not re.search(r"Mutations executed \| 0 \|", vt):
            e.append(f"L5 {vr.relative_to(root)}: PLAN_ONLY / 'Mutations executed | 0' missing")
        if not sm.exists() or "Mutations executed | `0`" not in sm.read_text():
            e.append(f"L5 {sm.relative_to(root)}: 'Mutations executed | `0`' missing")
    return e, len(dirs), len(mruns)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    a = ap.parse_args(argv)
    r = check(Path(a.root))
    errs, nd, nm = (r, 0, 0) if isinstance(r, list) else r
    for x in errs:
        print("LABEL ERROR " + x)
    if errs:
        print(f"LABELS INVALID: {len(errs)} error(s)")
        return 1
    print(f"LABELS OK: {nd} incident run/console dirs labelled SIMULATION; {nm} M365 run(s) marked PLAN_ONLY, mutations 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
