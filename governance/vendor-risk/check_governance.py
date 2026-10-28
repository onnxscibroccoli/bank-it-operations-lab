#!/usr/bin/env python3
"""SIMULATION - lint for governance/vendor-risk (stdlib only, offline).

Checks: (1) each RACI matrix has exactly one 'A' per activity row; (2) the assessment template has
all required sections; (3) SIMULATION examples carry the SIMULATION label and the explicit
no-compatibility-evidence disclaimer. Exit 0 = pass, 1 = findings, 2 = usage error.

    python3 governance/vendor-risk/check_governance.py [--raci FILE ...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQUIRED_SECTIONS = [
    "Inherent risk and tiering", "Data classification", "Access", "Security control questions",
    "Business continuity and disaster recovery", "Continuity, escalation and exit",
    "Findings and treatment", "Data minimization and retention", "Sign-off",
]
DISCLAIMER = "no authoritative compatibility evidence exists"


def raci_findings(path: Path) -> list[str]:
    out, rows = [], 0
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) < 4 or not cells[0].isdigit():
            continue
        rows += 1
        roles = cells[2:]
        n_a = sum(1 for c in roles if "A" in c.split("/"))
        if n_a != 1:
            out.append(f"{path.name}:{ln}: activity {cells[0]} has {n_a} Accountable (need exactly 1)")
        bad = [c for c in roles if c and not re.fullmatch(r"[RACI](/[RACI])*", c)]
        if bad:
            out.append(f"{path.name}:{ln}: invalid RACI codes {bad}")
    if rows == 0:
        out.append(f"{path.name}: no activity rows found")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raci", nargs="*", type=Path,
                    default=[HERE / "examples" / "acme-core-ledger-SIMULATION-raci.md"])
    a = ap.parse_args(argv)
    findings: list[str] = []
    for p in a.raci:
        if not p.is_file():
            print(f"ERROR: {p} not found", file=sys.stderr)
            return 2
        findings += raci_findings(p)
    tpl = (HERE / "vendor-risk-assessment-template.md").read_text(encoding="utf-8")
    findings += [f"template: missing section '{s}'" for s in REQUIRED_SECTIONS if s not in tpl]
    for ex in sorted((HERE / "examples").glob("*SIMULATION*.md")):
        txt = ex.read_text(encoding="utf-8")
        if not txt.startswith("# SIMULATION"):
            findings.append(f"{ex.name}: title not labelled SIMULATION")
        if "assessment" in ex.name and DISCLAIMER not in txt.lower():
            findings.append(f"{ex.name}: missing disclaimer '{DISCLAIMER}'")
    for f in findings:
        print("FINDING:", f)
    print(f"SIMULATION governance lint: {'PASS' if not findings else 'FAIL'} ({len(findings)} findings)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
