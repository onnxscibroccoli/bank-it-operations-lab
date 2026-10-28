#!/usr/bin/env python3
"""Offline checks for evidence/backup/** (stdlib only, read-only).

Enforces the separation between planning numbers and observations:
  * recovery status / RTO-RPO observed / billing / capacity entries are NOT_EXECUTED or NOT_OBSERVED and carry no values;
  * hypothesis blocks are labelled HYPOTHESIS, estimate output is labelled ESTIMATE, with null costs when prices are unknown;
  * all JSON parses, and SHA256SUMS (if present) verifies.
Exit 1 on any error. Usage: python3 evidence/backup/validate_backup_evidence.py [--root <repo>]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

UNOBSERVED = {"NOT_EXECUTED", "NOT_OBSERVED"}
META_KEYS = {"status", "id", "driver", "unit", "name", "reason", "label", "allowed_status", "template", "source", "aws_api_calls_made"}


def values_present(obj, path=""):
    """Paths of non-null values in an unobserved entry, ignoring descriptive keys and nested statuses."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in META_KEYS:
                continue
            out += values_present(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += values_present(v, f"{path}[{i}]")
    elif obj is not None:
        out.append(path)
    return out


def check_unobserved_tree(obj, where, errors):
    """Any dict whose status is unobserved must not carry values (recursively)."""
    if isinstance(obj, dict):
        if obj.get("status") in UNOBSERVED:
            leaked = [p for p in values_present(obj) if not p.endswith("_note")]
            if leaked:
                errors.append(f"{where}: status {obj['status']} but has values at {leaked}")
        for k, v in obj.items():
            check_unobserved_tree(v, f"{where}.{k}", errors)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_unobserved_tree(v, f"{where}[{i}]", errors)


def load(p: Path, errors):
    try:
        return json.loads(p.read_text())
    except Exception as e:  # noqa: BLE001
        errors.append(f"{p}: invalid JSON ({e})")
        return None


def validate(root: Path):
    errors = []
    ev = root / "evidence" / "backup"
    for p in sorted(ev.rglob("*.json")):
        d = load(p, errors)
        if d is not None:
            check_unobserved_tree(d, str(p.relative_to(root)), errors)

    st = load(ev / "aws-backup-dr" / "RECOVERY_EXECUTION_STATUS.json", errors) or {}
    if st.get("status") != "NOT_EXECUTED" or st.get("aws_api_calls_made") is not False:
        errors.append("RECOVERY_EXECUTION_STATUS.json: must be NOT_EXECUTED with aws_api_calls_made=false")
    if any(i.get("status") != "NOT_EXECUTED" for i in st.get("items", [])):
        errors.append("RECOVERY_EXECUTION_STATUS.json: every item must be NOT_EXECUTED")

    rr = load(ev / "aws-backup-dr" / "rto-rpo-observations.json", errors) or {}
    for s in rr.get("scenarios", []):
        if s.get("hypothesis", {}).get("label") != "HYPOTHESIS":
            errors.append(f"rto-rpo {s.get('id')}: hypothesis block must be labelled HYPOTHESIS")
        if s.get("observed", {}).get("status") != "NOT_EXECUTED":
            errors.append(f"rto-rpo {s.get('id')}: observed must be NOT_EXECUTED (no recovery has run)")

    bill = load(ev / "cost-capacity" / "actual-billing-observation.json", errors) or {}
    if bill.get("label") != "ACTUAL_BILLING_OBSERVATION" or bill.get("status") != "NOT_OBSERVED":
        errors.append("actual-billing-observation.json: must be ACTUAL_BILLING_OBSERVATION / NOT_OBSERVED")

    est_p = ev / "cost-capacity" / "estimate-output.json"
    if est_p.exists():
        est = load(est_p, errors) or {}
        if est.get("label") != "ESTIMATE":
            errors.append("estimate-output.json: label must be ESTIMATE")
        for line in est.get("lines", []):
            if line.get("unit_price") is None and line.get("estimate_cost") is not None:
                errors.append(f"estimate-output.json: cost without a price on '{line.get('driver')}'")
        if "ACTUAL" in json.dumps({k: v for k, v in est.items() if k != "not_billing"}):
            errors.append("estimate-output.json: must not contain ACTUAL labels")

    sums = ev / "aws-backup-dr" / "SHA256SUMS"
    if sums.exists():
        for line in sums.read_text().splitlines():
            if not line.strip():
                continue
            digest, rel = line.split(maxsplit=1)
            f = root / rel.strip().lstrip("*")
            if not f.exists():
                errors.append(f"SHA256SUMS: missing {rel}")
            elif hashlib.sha256(f.read_bytes()).hexdigest() != digest:
                errors.append(f"SHA256SUMS: mismatch {rel}")
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    a = ap.parse_args(argv)
    errors = validate(Path(a.root))
    print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
