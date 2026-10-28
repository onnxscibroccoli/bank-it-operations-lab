#!/usr/bin/env python3
"""ESTIMATE-only AWS Backup cost-driver model (stdlib only, offline, no AWS calls).

Turns placeholder sizes/rates (cost-inputs.estimate.json) into quantities (GB-month, GB transferred, requests) and, only
where a unit price has been filled in from the AWS public pricing pages, into ESTIMATE cost. Any unknown price yields
cost = null. The output is never an ACTUAL_BILLING_OBSERVATION; see evidence/backup/cost-capacity/.

Usage: python3 cost_model.py [inputs.json] > estimate-output.json
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def monthly_points(retention_days: int, cold_after_days: int, days_per_month: float, cold_capable: bool):
    """Steady-state count of monthly recovery points held warm vs cold."""
    total = math.ceil(retention_days / days_per_month)
    warm = min(total, math.ceil(cold_after_days / days_per_month)) if cold_capable else total
    return warm, total - warm


def early_cold_delete_billable_days(days_in_cold: float, cold_min_days: int = 90) -> float:
    """Days still billed if a cold recovery point is deleted early (only possible in an unlocked vault)."""
    return max(0.0, cold_min_days - days_in_cold)


def resource_quantities(r: dict, ret: dict) -> dict:
    size, chg = r["source_size_gb"], r["daily_change_fraction"]
    # Incremental chain: one full + (retention-1) daily increments, plus PITR transaction logs for the window.
    pitr = r.get("pitr_log_gb_per_day", 0) * ret["daily_retention_days"]
    daily_warm = size + size * chg * (ret["daily_retention_days"] - 1) + pitr
    warm_n, cold_n = monthly_points(ret["monthly_retention_days"], ret["monthly_cold_after_days"], ret["days_per_month"], r["cold_capable"])
    point = size * r["monthly_unique_fraction"]
    per_vault = {"warm_gb_month": daily_warm + warm_n * point, "cold_gb_month": cold_n * point}
    transfer = size * chg * ret["days_per_month"] + point  # steady state: daily increments + one monthly point
    return {
        "name": r["name"], "type": r["type"], "label": "ESTIMATE",
        "primary_vault": per_vault,
        # Copy lifecycle mirrors the source (backup-policy.json), but PITR logs are not copied: continuous points arrive as snapshots.
        "dr_vault": {"warm_gb_month": per_vault["warm_gb_month"] - pitr, "cold_gb_month": per_vault["cold_gb_month"]},
        "monthly_points_warm": warm_n, "monthly_points_cold": cold_n,
        "cross_region_transfer_gb_month": transfer,
        "initial_full_copy_gb_one_time": size,
    }


def cost(qty, price):
    return None if price is None or qty is None else round(qty * price, 2)


def run(inputs: dict) -> dict:
    ret, act, pr = inputs["retention"], inputs["activity"], inputs["prices"]
    lines, resources = [], []
    for r in inputs["resources"]:
        q = resource_quantities(r, ret)
        resources.append(q)
        warm_p = pr["warm_gb_month_by_type"].get(r["type"])
        cold_p = pr["cold_gb_month_by_type"].get(r["type"])
        warm = q["primary_vault"]["warm_gb_month"] + q["dr_vault"]["warm_gb_month"]
        cold = q["primary_vault"]["cold_gb_month"] + q["dr_vault"]["cold_gb_month"]
        lines += [
            {"driver": f"{r['name']}: warm storage (both vaults)", "quantity": round(warm, 2), "unit": "GB-month", "unit_price": warm_p, "estimate_cost": cost(warm, warm_p)},
            {"driver": f"{r['name']}: cold storage (both vaults)", "quantity": round(cold, 2), "unit": "GB-month", "unit_price": cold_p, "estimate_cost": cost(cold, cold_p)},
            {"driver": f"{r['name']}: cross-region copy transfer", "quantity": round(q["cross_region_transfer_gb_month"], 2), "unit": "GB", "unit_price": pr["cross_region_transfer_per_gb"], "estimate_cost": cost(q["cross_region_transfer_gb_month"], pr["cross_region_transfer_per_gb"])},
        ]
        rg = r["source_size_gb"] * act["restore_drill_fraction_of_source"] * act["restore_drills_per_month"]
        rp = pr["restore_warm_per_gb_by_type"].get(r["type"])
        lines.append({"driver": f"{r['name']}: restore drills (warm)", "quantity": round(rg, 2), "unit": "GB", "unit_price": rp, "estimate_cost": cost(rg, rp)})
    lines += [
        {"driver": "restore testing: restored instance runtime", "quantity": act["restore_test_instance_hours_per_month"], "unit": "instance-hour", "unit_price": pr["restore_test_instance_hour"], "estimate_cost": cost(act["restore_test_instance_hours_per_month"], pr["restore_test_instance_hour"])},
        {"driver": "KMS: vault CMKs", "quantity": act["vault_cmk_count"], "unit": "key-month", "unit_price": pr["kms_key_month"], "estimate_cost": cost(act["vault_cmk_count"], pr["kms_key_month"])},
        {"driver": "KMS: API requests", "quantity": act["kms_requests_per_month"] / 10000, "unit": "10k requests", "unit_price": pr["kms_per_10k_requests"], "estimate_cost": cost(act["kms_requests_per_month"] / 10000, pr["kms_per_10k_requests"])},
    ]
    known = [l["estimate_cost"] for l in lines if l["estimate_cost"] is not None]
    return {
        "label": "ESTIMATE",
        "not_billing": "This is a model output from placeholder inputs. It is not an ACTUAL_BILLING_OBSERVATION.",
        "inputs_placeholder": any(r.get("placeholder") for r in inputs["resources"]) or act.get("placeholder", False),
        "resources": resources,
        "lines": lines,
        "estimate_total_known": round(sum(known), 2) if known else None,
        "lines_without_price": sum(1 for l in lines if l["unit_price"] is None),
        "vault_lock_committed_storage_note": "With Vault Lock, warm/cold GB-month above is committed until each recovery point's lifecycle ends; it cannot be reduced by deletion.",
        "price_references": pr["references"],
    }


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "cost-inputs.estimate.json"
    print(json.dumps(run(json.loads(src.read_text())), indent=2))
