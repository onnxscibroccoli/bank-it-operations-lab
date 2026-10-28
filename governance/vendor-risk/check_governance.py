#!/usr/bin/env python3
"""SIMULATION - lint for governance/vendor-risk (stdlib only, offline).

Checks: (1) each RACI matrix has exactly one 'A' per activity row; (2) the assessment template has
all required sections; (3) SIMULATION examples carry the SIMULATION label and the explicit
no-compatibility-evidence disclaimer; (4) escalation scenarios (scenarios/*.md) have the required
sections, the SIMULATION label and contract placeholders; keep Jack Henry / Banno mentions inside the
"Real vendor vs fictional system" section, which must state that Jack Henry is only the vendor named
in the job posting and that the vendor-mock API is fictional and reflects no Jack Henry/Banno API;
relative links resolve; cited vendor-mock failure scenarios exist; and no phone numbers, e-mail
addresses or URLs; (5) scenarios and the SIMULATION assessment examples contain no vendor-attributed
SLA-like numeric commitments (SLA/RTO/RPO/uptime/notice periods must be placeholders); (6) the
fictional vendor-mock contract, code, fixtures and tests never name Jack Henry or Banno.
Exit 0 = pass, 1 = findings, 2 = usage error.

    python3 governance/vendor-risk/check_governance.py [--raci FILE ...] [--scenario FILE ...] [--link-base DIR]
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MOCK_ROOT = REPO / "integrations" / "vendor-mock"
MOCK_CHECKED_DIRS = ("contract", "vendor_mock", "fixtures", "tests")
REAL_VENDOR_RX = re.compile(r"jack\s*henry|banno", re.I)
CONTEXT_SECTION = "Real vendor vs fictional system"
CONTEXT_REQUIRED = [  # phrases (lower-case, '*' stripped) the context section must contain
    ("job posting", "job description"), ("acme core ledger simulation",), ("integrations/vendor-mock",),
    ("does not reflect",), ("fictional",),
]
MOCK_SCENARIO_RX = re.compile(r"`((?:normal|timeout\w*|rate_limit\w*|auth_\w+|malformed_\w+))`")
LINK_RX = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
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
    CONTEXT_SECTION, "Exercise overview and objectives", "Roles", "Injects and facilitator notes",
    "Completion and sign-off", "Cross-references",
]
CONTRACT_PLACEHOLDER = "[PLACEHOLDER: confirm from contract]"
PLACEHOLDER_RX = re.compile(r"\[PLACEHOLDER:[^\]]*\]")
VENDOR_RX = re.compile(r"\b(vendors?|vendor's|providers?|suppliers?|acme|jack henry)\b", re.I)
NUMERIC_COMMITMENT_RX = re.compile(
    r"\d+(\.\d+)?\s*-?\s*(%|percent\b|(business\s+)?(seconds?|secs?|minutes?|mins?|hours?|hrs?|h|days?|weeks?|months?)\b)"
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


def vendor_number_findings(path: Path, strict: bool = False) -> list[str]:
    """Flag lines attributing an SLA-like number to a vendor (placeholder text is ignored).

    strict=True (used for vendor assessments, where every answer is about the vendor) flags any
    SLA-like numeric commitment, whether or not the line names the vendor."""
    out = []
    for ln_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        bare = PLACEHOLDER_RX.sub("", line)
        m = NUMERIC_COMMITMENT_RX.search(bare)
        if m and (strict or VENDOR_RX.search(bare)):
            out.append(f"{path.name}:{ln_no}: SLA-like numeric commitment attributed to vendor: {m.group(0)!r}")
    return out


def mock_scenarios(mock_root: Path = MOCK_ROOT) -> set[str]:
    tree = ast.parse((mock_root / "vendor_mock" / "mock.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SCENARIOS" for t in node.targets):
            return set(ast.literal_eval(node.value))
    return set()


def mock_naming_findings(mock_root: Path = MOCK_ROOT) -> list[str]:
    """The fictional mock's contract/code/fixtures/tests must never name the real vendor."""
    out = []
    for d in MOCK_CHECKED_DIRS:
        for f in sorted((mock_root / d).rglob("*")):
            if not f.is_file() or "__pycache__" in f.parts:
                continue
            for ln_no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if REAL_VENDOR_RX.search(line):
                    out.append(f"{f.relative_to(mock_root).as_posix()}:{ln_no}: real vendor named in "
                               "fictional vendor-mock (keep Jack Henry/Banno out of contract/code/fixtures/tests)")
    return out


def _norm_heading(h: str) -> str:
    return re.sub(r"^\d+\.\s*", "", h.lstrip("#* ").rstrip("* ")).lower()


def scenario_findings(path: Path, mock_root: Path = MOCK_ROOT, link_base: Path | None = None) -> list[str]:
    txt = path.read_text(encoding="utf-8")
    lines = txt.splitlines()
    out = []
    if not txt.startswith("# SIMULATION"):
        out.append(f"{path.name}: title not labelled SIMULATION")
    headings = [_norm_heading(ln) for ln in lines if ln.startswith("#") or ln.startswith("**")]
    for sec in SCENARIO_SECTIONS:
        if not any(h.startswith(sec.lower()) for h in headings):
            out.append(f"{path.name}: missing required section '{sec}'")
    if CONTRACT_PLACEHOLDER not in txt:
        out.append(f"{path.name}: no '{CONTRACT_PLACEHOLDER}' marker")
    if DISCLAIMER not in txt.lower():
        out.append(f"{path.name}: missing disclaimer '{DISCLAIMER}'")

    # Real vendor vs fictional system: Jack Henry / Banno only inside the context section.
    section, ctx_lines = None, []
    for ln_no, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = _norm_heading(line)
        in_ctx = section is not None and section.startswith(CONTEXT_SECTION.lower())
        if in_ctx:
            ctx_lines.append(line)
        if REAL_VENDOR_RX.search(line) and not in_ctx:
            out.append(f"{path.name}:{ln_no}: Jack Henry/Banno mentioned outside the "
                       f"'{CONTEXT_SECTION}' section")
    ctx = " ".join(ctx_lines).replace("*", "").lower()
    if ctx:
        if "jack henry" not in ctx:
            out.append(f"{path.name}: '{CONTEXT_SECTION}' section does not name the real vendor (Jack Henry)")
        for alts in CONTEXT_REQUIRED:
            if not any(a in ctx for a in alts):
                out.append(f"{path.name}: '{CONTEXT_SECTION}' section missing statement containing {alts[0]!r}")

    # Cross-links resolve; cited mock failure scenarios exist.
    for target in LINK_RX.findall(txt):
        if "://" not in target and not ((link_base or path.parent) / target).exists():
            out.append(f"{path.name}: broken relative link {target!r}")
    cited = set(MOCK_SCENARIO_RX.findall(txt))
    known = mock_scenarios(mock_root)
    if not cited:
        out.append(f"{path.name}: no vendor-mock failure scenarios cited as technical analogue")
    for c in sorted(cited - known):
        out.append(f"{path.name}: cites unknown vendor-mock scenario {c!r}")

    for ln_no, line in enumerate(lines, 1):
        bare = PLACEHOLDER_RX.sub("", line)
        for rx, what in ((PHONE_RX, "phone number"), (EMAIL_RX, "e-mail address"), (URL_RX, "URL")):
            if rx.search(bare):
                out.append(f"{path.name}:{ln_no}: contains a {what}")
    out += vendor_number_findings(path)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raci", nargs="*", type=Path,
                    default=[HERE / "examples" / "acme-core-ledger-SIMULATION-raci.md"])
    ap.add_argument("--scenario", nargs="*", type=Path,
                    default=sorted((HERE / "scenarios").glob("*.md")))
    ap.add_argument("--link-base", type=Path, default=None,
                    help="directory to resolve scenario relative links from (default: the file's directory)")
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
        findings += scenario_findings(p, link_base=a.link_base)
    tpl = (HERE / "vendor-risk-assessment-template.md").read_text(encoding="utf-8")
    findings += [f"template: missing section '{s}'" for s in REQUIRED_SECTIONS if s not in tpl]
    for ex in sorted((HERE / "examples").glob("*SIMULATION*.md")):
        txt = ex.read_text(encoding="utf-8")
        if not txt.startswith("# SIMULATION"):
            findings.append(f"{ex.name}: title not labelled SIMULATION")
        if "assessment" in ex.name:
            if DISCLAIMER not in txt.lower():
                findings.append(f"{ex.name}: missing disclaimer '{DISCLAIMER}'")
            findings += vendor_number_findings(ex, strict=True)
    findings += mock_naming_findings()
    for f in findings:
        print("FINDING:", f)
    print(f"SIMULATION governance lint: {'PASS' if not findings else 'FAIL'} ({len(findings)} findings)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
