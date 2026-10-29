#!/usr/bin/env python3
"""Publish USER ACTION REQUIRED items from coordination/tasks.json (the machine-readable source of truth).

Usage: user_actions.py [--summary FILE] [--annotations] [--out FILE]
Exit 0 when the file is valid, whether or not actions are open. Exit 1 when tasks.json is malformed.
Values are treated as data: escaped, never executed.
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ["id", "task_id", "classification", "status", "action", "reason", "observed",
            "smallest_permission", "instructions", "blocks", "continuing", "deadline_impact"]
CLASSES = {"USER_ACTION_REQUIRED", "AUTONOMOUS_FIX", "OUT_OF_SCOPE"}
STATES = {"OPEN", "NOT_YET_ACTIONABLE", "RESOLVED"}


def esc_cmd(s):
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def esc_md(s):
    return s.replace("|", "\\|").replace("\n", " ")


def load(path):
    d = json.loads(Path(path).read_text())
    items, errs = d.get("user_actions"), []
    if not isinstance(items, list):
        return d, [], ["tasks.json: user_actions must be a list"]
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            errs.append(f"user_actions[{i}] is not an object")
            continue
        name = it.get("id", i)
        for k in REQUIRED:
            if k not in it:
                errs.append(f"{name}: missing field {k}")
                continue
            v = it[k]
            if k == "blocks":
                if not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
                    errs.append(f"{name}: blocks must be a list of strings")
            elif not (isinstance(v, str) and v.strip()):
                errs.append(f"{name}: {k} must be a non-empty string")
        if it.get("classification") not in CLASSES:
            errs.append(f"{name}: bad classification")
        if it.get("status") not in STATES:
            errs.append(f"{name}: bad status")
    return d, items, errs


def render(d, items):
    open_items = [i for i in items if i["classification"] == "USER_ACTION_REQUIRED" and i["status"] == "OPEN"]
    later = [i for i in items if i["classification"] == "USER_ACTION_REQUIRED" and i["status"] == "NOT_YET_ACTIONABLE"]
    if open_items:
        top = f"USER ACTION REQUIRED: {len(open_items)} — " + "; ".join(i["id"] for i in open_items)
    else:
        top = "USER ACTION REQUIRED: NONE"
    rem = d.get("remaining_window") or {}
    md = [f"## {top}", "",
          f"Deadline: `{d.get('deadline', 'unknown')}`; remaining window as of {rem.get('as_of', '?')}: **{rem.get('remaining', '?')}**.",
          "Source: `coordination/tasks.json` user_actions. This report is not proof that anyone was notified.", "",
          "| id | task | action | why not automatable | blocks | deadline impact | where |",
          "|---|---|---|---|---|---|---|"]
    for i in open_items + later:
        tag = "" if i["status"] == "OPEN" else " (not yet actionable)"
        cells = [i["id"] + tag, i["task_id"], i["action"], i["reason"],
                 ", ".join(i["blocks"]) or "-", i["deadline_impact"], i["instructions"]]
        md.append("| " + " | ".join(esc_md(c) for c in cells) + " |")
    ab = d.get("autonomous_blockers") or []
    if ab:
        md += ["", "### Technical blockers being fixed autonomously (not user actions)", ""]
        md += [f"- **{esc_md(str(b.get('id')))}** ({esc_md(str(b.get('source')))}): {esc_md(str(b.get('item')))}" for b in ab]
    acs = (d.get("acceptance_conditions_for_main") or {}).get("conditions") or []
    if acs:
        md += ["", "### Acceptance conditions for main", "", "| AC | status |", "|---|---|"]
        md += [f"| {esc_md(str(c.get('id')))} | {esc_md(str(c.get('status')))} |" for c in acs]
    return top, open_items, later, ab, md


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default=str(ROOT / "coordination/tasks.json"))
    ap.add_argument("--summary")
    ap.add_argument("--out")
    ap.add_argument("--annotations", action="store_true")
    a = ap.parse_args(argv)
    d, items, errs = load(a.tasks)
    if errs:
        for e in errs:
            print(("::error title=user-actions::" + esc_cmd(e)) if a.annotations else ("ERROR " + e))
        return 1
    top, open_items, later, ab, md = render(d, items)
    print(top)
    if a.annotations:
        for i in open_items:
            msg = i["action"] + " Where: " + i["instructions"]
            print("::warning title=USER ACTION REQUIRED " + esc_cmd(i["id"]) + "::" + esc_cmd(msg))
    if a.summary:
        with open(a.summary, "a") as f:
            f.write("\n".join(md) + "\n")
    if a.out:
        out = {"top_line": top, "open": open_items, "not_yet_actionable": later, "autonomous_blockers": ab}
        Path(a.out).write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
