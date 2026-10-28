#!/usr/bin/env python3
"""SIMULATION - lint for governance/vendor-risk (stdlib only, offline).

Checks: (1) each RACI matrix has exactly one 'A' per activity row; (2) the assessment template has
all required sections; (3) SIMULATION examples carry the SIMULATION label and the explicit
no-compatibility-evidence disclaimer; (4) escalation scenarios (scenarios/*.md) have the required
sections, the SIMULATION label, contract placeholders, mention Jack Henry only as the vendor named
in the job description, and contain no vendor-attributed SLA-like numeric commitments, phone
numbers, e-mail addresses or URLs. Exit 0 = pass, 1 = findings, 2 = usage error.

    python3 governance/vendor-risk/check_governance.py [--raci FILE ...] [--scenario FILE ...]
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
SCENARIO_SECTIONS = [
    "Impact assessment", "Customer impact", "Channel impact", "Operational impact",
    "Regulatory and notification considerations", "Evidence collection", "Chain of custody",
    "Escalation", "Internal tiers", "Vendor-facing questions", "Update cadence",
    "Restoration criteria", "Post-incident review",
]
CONTRACT_PLACEHOLDER = "[PLACEHOLDER: confirm from contract]"
PLACEHOLDER_RX = re.compile(r"\[PLACEHOLDER:[^\]]*\]")
VENDOR_RX = re.compile(r"\b(vendors?|vendor's|providers?|suppliers?|acme|jack henry)\b", re.I)
NUMERIC_COMMITMENT_RX = re.compile(
    r"\d+(\.\d+)?\s*(%|percent\b|(business\s+)?(seconds?|secs?|minutes?|mins?|hours?|hrs?|h|days?|weeks?|months?)\b)"
    r"|\b(SLA|SLO|RTO|RPO|uptime|availability|response time|resolution time)\b[^|]*?\d", re.I)
PHONE_RX = re.compile(r"(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")
EMAIL_RX = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
URL_RX = re.compile(r"https?://", re.I)


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


def scenario_findings(path: Path) -> list[str]:
    txt = path.read_text(encoding="utf-8")
    out = []
    if not txt.startswith("# SIMULATION"):
        out.append(f"{path.name}: title not labelled SIMULATION")
    headings = [ln.lstrip("#* ").rstrip("* ") for ln in txt.splitlines() if ln.startswith("#") or ln.startswith("**")]
    for sec in SCENARIO_SECTIONS:
        if not any(re.sub(r"^\d+\.\s*", "", h).lower().startswith(sec.lower()) for h in headings):
            out.append(f"{path.name}: missing required section '{sec}'")
    if CONTRACT_PLACEHOLDER not in txt:
        out.append(f"{path.name}: no '{CONTRACT_PLACEHOLDER}' marker")
    if DISCLAIMER not in txt.lower():
        out.append(f"{path.name}: missing disclaimer '{DISCLAIMER}'")
    jh = [ln for ln in txt.splitlines() if "jack henry" in ln.lower()]
    if not jh:
        out.append(f"{path.name}: missing explicit statement that Jack Henry is named only as the job-description vendor")
    for ln_no, line in enumerate(txt.splitlines(), 1):
        if "jack henry" in line.lower() and "job description" not in line.lower():
            out.append(f"{path.name}:{ln_no}: Jack Henry mentioned outside the job-description statement")
        bare = PLACEHOLDER_RX.sub("", line)
        if VENDOR_RX.search(bare) and NUMERIC_COMMITMENT_RX.search(bare):
            out.append(f"{path.name}:{ln_no}: SLA-like numeric commitment attributed to vendor: "
                       f"{NUMERIC_COMMITMENT_RX.search(bare).group(0)!r}")
        for rx, what in ((PHONE_RX, "phone number"), (EMAIL_RX, "e-mail address"), (URL_RX, "URL")):
            if rx.search(bare):
                out.append(f"{path.name}:{ln_no}: contains a {what}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raci", nargs="*", type=Path,
                    default=[HERE / "examples" / "acme-core-ledger-SIMULATION-raci.md"])
    ap.add_argument("--scenario", nargs="*", type=Path,
                    default=sorted((HERE / "scenarios").glob("*.md")))
    a = ap.parse_args(argv)
    findings: list[str] = []
    for p in a.raci:
        if not p.is_file():
            print(f"ERROR: {p} not found", file=sys.stderr)
            return 2
        findings += raci_findings(p)
    if not a.scenario:
        findings.append("no escalation scenarios found under scenarios/")
    for p in a.scenario:
        if not p.is_file():
            print(f"ERROR: {p} not found", file=sys.stderr)
            return 2
        findings += scenario_findings(p)
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
