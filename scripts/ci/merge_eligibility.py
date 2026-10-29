#!/usr/bin/env python3
"""Merge-eligibility check (PR #27 C6 policy): main may be merged automatically only when AC1-AC5 are MET
for the exact SHA under test and every required check job
(coordination/modules.json required_gate_jobs, plus final-summary) succeeded in this run; AC6 (human portfolio acceptance) is a separate gate and is reported, not checked.
Exit 0 = eligible, 1 = not eligible (expected while conditions are open). Never merges anything."""
import argparse, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import user_actions  # noqa: E402

TECH = ["AC1", "AC2", "AC3", "AC4", "AC5"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary")
    ap.add_argument("--sha", default=os.environ.get("GITHUB_SHA", ""))
    ap.add_argument("--tasks", default=str(user_actions.ROOT / "coordination/tasks.json"))
    a = ap.parse_args(argv)
    d = json.loads(Path(a.tasks).read_text())
    acm = d.get("acceptance_conditions_for_main") or {}
    conds = {c.get("id"): c for c in acm.get("conditions") or []}
    problems = []
    for ac in TECH:
        c = conds.get(ac)
        if c is None:
            problems.append(f"{ac}: missing")
        elif c.get("status") != "MET":
            problems.append(f"{ac}: {c.get('status')}")
        elif a.sha and c.get("met_for_sha") and not a.sha.startswith(str(c.get("met_for_sha"))) \
                and not str(c.get("met_for_sha")).startswith(a.sha):
            problems.append(f"{ac}: MET for {c.get('met_for_sha')}, not this SHA")
    # Required checks for this exact run: missing, skipped, cancelled or failed all make the SHA ineligible.
    reg = json.loads((user_actions.ROOT / "coordination/modules.json").read_text())
    required = reg.get("required_gate_jobs") or []
    if not required:
        problems.append("required_gate_jobs missing from coordination/modules.json")
    raw = os.environ.get("NEEDS_JSON")
    needs = json.loads(raw) if raw else None
    if not isinstance(needs, dict):
        problems.append("required check results not available (NEEDS_JSON unset): not verified for this SHA")
    else:
        for job in required + ["final-summary"]:
            res = (needs.get(job) or {}).get("result", "missing") if job in needs else "missing"
            if res != "success":
                problems.append(f"required check {job}: {res}")
    ac6 = (conds.get("AC6") or {}).get("status", "missing")
    verdict = "ELIGIBLE" if not problems else "NOT ELIGIBLE"
    print(f"merge-eligibility for {a.sha or 'local'}: {verdict}")
    for p in problems:
        print("::notice title=merge-eligibility::" + user_actions.esc_cmd(p))
    if a.summary:
        md = [f"### Merge eligibility for `{a.sha or 'local'}`: **{verdict}**", "",
              "Policy: PR #27 finding C6. AC1-AC5 must be MET for this exact SHA; AC6 is a separate human gate "
              f"(currently {user_actions.esc_md(str(ac6))}).", ""] + [f"- {user_actions.esc_md(p)}" for p in problems]
        with open(a.summary, "a") as f:
            f.write("\n".join(md) + "\n")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
