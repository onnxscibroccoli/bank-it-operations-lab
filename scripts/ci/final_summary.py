#!/usr/bin/env python3
"""Aggregate job results for the integration gate. Reads NEEDS_JSON (toJSON(needs)) from the environment,
plus the user-action list from coordination/tasks.json. Writes Markdown to --summary.
Exit 1 if any required job is not 'success' (failure, cancelled or skipped all count as not passed)."""
import argparse, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import user_actions  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary")
    ap.add_argument("--tasks", default=str(user_actions.ROOT / "coordination/tasks.json"))
    a = ap.parse_args(argv)
    needs = json.loads(os.environ.get("NEEDS_JSON") or "{}")
    if not isinstance(needs, dict) or not needs:
        print("::error title=final-summary::NEEDS_JSON missing or empty")
        return 1
    rows, bad = [], []
    for job in sorted(needs):
        res = str((needs[job] or {}).get("result", "unknown"))
        rows.append(f"| {user_actions.esc_md(job)} | {user_actions.esc_md(res)} |")
        if res != "success":
            bad.append(job)
    counts = {}
    for job in needs:
        r = str((needs[job] or {}).get("result", "unknown"))
        counts[r] = counts.get(r, 0) + 1
    d, items, errs = user_actions.load(a.tasks)
    top = "USER ACTION REQUIRED: (tasks.json invalid)" if errs else user_actions.render(d, items)[0]
    verdict = "PASS" if not bad else "FAIL: " + ", ".join(bad)
    sha = os.environ.get("GITHUB_SHA", "local")
    md = [f"## {top}", "", f"### Integration gate for `{sha}`: **{verdict}**", "",
          "Counts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())), "",
          "| job | result |", "|---|---|"] + rows + ["",
          "A green gate means the checks ran and passed for this SHA. It does not mean AC1-AC6 are met; "
          "see the merge-eligibility job and coordination/tasks.json."]
    print(top)
    print("gate:", verdict)
    for job in bad:
        print("::error title=integration-gate::job " + user_actions.esc_cmd(job) + " did not succeed")
    if a.summary:
        with open(a.summary, "a") as f:
            f.write("\n".join(md) + "\n")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
