#!/usr/bin/env python3
"""Offline validator for hybrid runbooks (stdlib only, no network, no credentials).

Checks every Markdown file under operations/hybrid/ and docs/runbooks/hybrid/:
  1. an "Execution status: NOT_EXECUTED" banner within the first 10 lines;
  2. runbooks (docs/runbooks/hybrid/*.md except README.md) have the required sections;
  3. relative Markdown links resolve to existing files;
  4. no secret-like values (tokens, keys, inline passwords);
  5. outside fenced code, no execution status other than NOT_EXECUTED is claimed;
  6. IPv4 literals are documentation (RFC 5737) or private (RFC 1918) addresses;
  7. every status row in EXECUTION_STATUS.md is NOT_EXECUTED.
Exit code 0 = pass, 1 = findings.
"""
from __future__ import annotations

import ipaddress
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCAN_DIRS = ("operations/hybrid", "docs/runbooks/hybrid")
RUNBOOK_DIR = "docs/runbooks/hybrid"
REQUIRED_SECTIONS = ("Purpose", "Scope", "Preconditions", "Procedure", "Verification", "Rollback", "Evidence")
BANNER = re.compile(r"Execution status:\s*\**\s*NOT_EXECUTED", re.I)
STATUS_CLAIM = re.compile(r"Execution status:\s*\**\s*([A-Z_]+)")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
IPV4 = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?:/\d{1,2})?(?![\d.])")
SECRETS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bpassword\s*[:=]\s*['\"]?(?!\(|<|\$|Read-Host)[^\s'\"]{4,}"),
    re.compile(r"(?i)ConvertTo-SecureString\s+['\"][^'\"]+['\"]\s+-AsPlainText"),
]
ALLOWED_NETS = [ipaddress.ip_network(n) for n in (
    "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24",
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8")]


def md_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for d in SCAN_DIRS:
        out.extend(sorted((root / d).rglob("*.md")))
    return out


def check_file(path: Path, root: Path) -> list[str]:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    findings: list[str] = []
    head = "\n".join(text.splitlines()[:10])
    if not BANNER.search(head):
        findings.append(f"{rel}: missing 'Execution status: NOT_EXECUTED' banner in first 10 lines")
    if rel.startswith(RUNBOOK_DIR + "/") and path.name != "README.md":
        headings = set(re.findall(r"^##\s+(.+?)\s*$", text, re.M))
        for s in REQUIRED_SECTIONS:
            if s not in headings:
                findings.append(f"{rel}: missing section '## {s}'")
    prose = FENCE.sub("", text)
    for m in LINK.finditer(prose):
        target = m.group(1)
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        if not (path.parent / target.split("#", 1)[0]).resolve().exists():
            findings.append(f"{rel}: broken link -> {target}")
    for pat in SECRETS:
        if pat.search(text):
            findings.append(f"{rel}: secret-like value matches /{pat.pattern}/")
    for m in STATUS_CLAIM.finditer(prose):
        if m.group(1).upper() != "NOT_EXECUTED":
            findings.append(f"{rel}: claims execution status {m.group(1)} outside code")
    for m in IPV4.finditer(text):
        try:
            ip = ipaddress.ip_address(m.group(1))
        except ValueError:
            continue
        if not any(ip in n for n in ALLOWED_NETS):
            findings.append(f"{rel}: non-documentation IPv4 address {ip}")
    if path.name == "EXECUTION_STATUS.md":
        rows = [r for r in text.splitlines() if r.startswith("| [")]
        if not rows:
            findings.append(f"{rel}: no status rows found")
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            if len(cells) < 2 or cells[1] != "NOT_EXECUTED":
                findings.append(f"{rel}: status row not NOT_EXECUTED: {r[:60]}")
    return findings


def main(root: Path = REPO) -> int:
    files = md_files(root)
    if not files:
        print("FAIL: no hybrid Markdown files found")
        return 1
    findings = [f for p in files for f in check_file(p, root)]
    for f in findings:
        print("FAIL:", f)
    print(f"checked {len(files)} files, {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
