#!/usr/bin/env python3
"""Security-exception consistency gate (PR #14 / PR #30 finding B5-1). Stdlib only; reads files, executes nothing.

Every cdk-nag suppression applied in the synthesized templates (Metadata.cdk_nag.rules_to_suppress) must name a
registered exception (reason "EX-NN: ...") whose rule matches the register row in
evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md. Otherwise: ERROR, exit 1.

An applied suppression whose exception is not APPROVED is a BLOCKING USER ACTION (UA-1): reported, exit 0 by default
(the lab is still buildable), and consumed by merge_eligibility.py, which then keeps AC2 and AC5 UNMET whatever
tasks.json says. --strict exits 3 in that case. Approval is the owner's decision (UA-1); this script never grants it.

Status: per-entry "EX-NN status: <STATUS>" lines override the register-wide "Status of every entry: **<STATUS>"
line. Only the exact word APPROVED counts as approved; anything else (PROPOSED, missing, ...) is not approved.
Usage: check_exceptions.py [--root DIR] [--out FILE] [--strict]
"""
import argparse, json, re, sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
REGISTER = "evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md"
SYNTH = "evidence/aws/aws-remediation-vpc-rds/synth"
ROW = re.compile(r"^\|\s*(EX-\d{2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
GLOBAL = re.compile(r"Status of every entry:\s*\*{0,2}([A-Z_]+)")
PER = re.compile(r"\b(EX-\d{2})\s+status:\s*\*{0,2}([A-Z_]+)")


def parse_register(text):
    rows, g, per = {}, None, {}
    for line in text.splitlines():
        m = ROW.match(line)
        if m:
            rows[m.group(1)] = {"rule": m.group(2).split(" (")[0].strip(), "resource": m.group(3)}
        mg = GLOBAL.search(line)
        if mg and g is None:
            g = mg.group(1)
        for mp in PER.finditer(line):
            per[mp.group(1)] = mp.group(2)
    for k, r in rows.items():
        r["status"] = per.get(k) or g or "MISSING"
    return rows


def applied_suppressions(synth_dir):
    out = []
    for t in sorted(Path(synth_dir).glob("*.template.json")):
        res = (json.loads(t.read_text()).get("Resources") or {})
        for rid, r in res.items():
            for s in (((r.get("Metadata") or {}).get("cdk_nag") or {}).get("rules_to_suppress") or []):
                out.append({"template": t.name, "resource": rid, "rule": s.get("id"), "reason": s.get("reason") or ""})
    return out


def evaluate(root):
    root = Path(root)
    errors, rows = [], {}
    reg = root / REGISTER
    if not reg.exists():
        return {"errors": [f"register missing: {REGISTER}"], "applied": [], "unapproved": [], "blocking_user_action": True}
    rows = parse_register(reg.read_text())
    if not rows:
        errors.append("register has no EX-NN rows")
    if not (root / SYNTH).is_dir():
        errors.append(f"synthesized templates missing: {SYNTH}")
    applied = applied_suppressions(root / SYNTH) if (root / SYNTH).is_dir() else []
    unapproved = []
    for s in applied:
        m = re.match(r"^(EX-\d{2}):", s["reason"])
        if not m:
            errors.append(f"{s['template']}:{s['resource']}: suppression of {s['rule']} names no registered exception (reason must start 'EX-NN:')")
            continue
        ex = rows.get(m.group(1))
        if ex is None:
            errors.append(f"{s['template']}:{s['resource']}: {m.group(1)} is not in the register")
            continue
        if s["rule"] != ex["rule"]:
            errors.append(f"{s['template']}:{s['resource']}: {m.group(1)} registers rule {ex['rule']} but suppresses {s['rule']}")
        s["exception"], s["status"] = m.group(1), ex["status"]
        if ex["status"] != "APPROVED":
            unapproved.append(s)
    return {"schema": "bank-lab/security-exceptions-check/v1", "register": REGISTER,
            "exceptions": rows, "applied": applied, "unapproved": unapproved, "errors": errors,
            "blocking_user_action": bool(unapproved) or bool(errors),
            "user_action": "UA-1: approve or reject " + ", ".join(sorted({u["exception"] for u in unapproved})) if unapproved else None}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--out")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    r = evaluate(a.root)
    for e in r["errors"]:
        print("ERROR " + e)
    for u in r["unapproved"]:
        print(f"BLOCKING USER ACTION (UA-1): suppression {u['rule']} on {u['template']}:{u['resource']} is applied while {u['exception']} is {u['status']}")
    n = len(r["applied"])
    if a.out:
        Path(a.out).write_text(json.dumps(r, indent=2) + "\n")
    if r["errors"]:
        print(f"SECURITY EXCEPTIONS INVALID: {len(r['errors'])} error(s)"); return 1
    if r["unapproved"]:
        print(f"SECURITY EXCEPTIONS: {n} applied suppression(s), {len(r['unapproved'])} tied to non-APPROVED exceptions -> AC2/AC5 stay UNMET until the owner decides (UA-1)")
        return 3 if a.strict else 0
    print(f"SECURITY EXCEPTIONS OK: {n} applied suppression(s), all registered and APPROVED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
