#!/usr/bin/env python3
"""Validate coordination/modules.json against the working tree, scripts/validate-all.sh and .github/workflows.

Fails (exit 1) when:
  * a module entry is malformed, or a module id or a claimed path is duplicated;
  * an INTEGRATED module path is missing, or it lists a validate-all step / CI job that does not exist;
  * an EXCLUDED / NOT_INTEGRATED module path exists on this branch (a module slipped in without registration);
  * any tracked top-level path (or evidence/<x>, infra/<x>, identity/<x>, tests/<x>) is not claimed by an INTEGRATED module.
Stdlib only; reads files, never executes anything from them.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUSES = {"INTEGRATED", "EXCLUDED", "NOT_INTEGRATED"}
NESTED = {"evidence", "infra", "identity", "tests", "scripts", "reports"}


def tracked_paths():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def claims(path, prefixes):
    return any(path == p or path.startswith(p.rstrip("/") + "/") for p in prefixes)


def workflow_jobs():
    jobs = {}
    for wf in (ROOT / ".github/workflows").glob("*.yml"):
        text = wf.read_text()
        m = re.search(r"^jobs:\n(.*)", text, re.S | re.M)
        jobs[wf.name] = set(re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", m.group(1), re.M)) if m else set()
    return jobs


def main():
    errors = []
    reg = json.loads((ROOT / "coordination/modules.json").read_text())
    mods = reg.get("modules")
    if not isinstance(mods, list) or not mods:
        print("ERROR modules.json: 'modules' must be a non-empty list"); return 1
    va = (ROOT / "scripts/validate-all.sh").read_text()
    wjobs = workflow_jobs()
    files = tracked_paths()
    seen_ids, seen_paths, integrated_prefixes = set(), {}, []
    for m in mods:
        mid = m.get("id")
        if not isinstance(mid, str) or not re.fullmatch(r"[a-z0-9-]+", mid or ""):
            errors.append(f"bad module id {mid!r}"); continue
        if mid in seen_ids: errors.append(f"{mid}: duplicate id")
        seen_ids.add(mid)
        st = m.get("status")
        if st not in STATUSES: errors.append(f"{mid}: bad status {st!r}"); continue
        paths = m.get("paths")
        if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p for p in paths):
            errors.append(f"{mid}: 'paths' must be a non-empty list of strings"); continue
        if not isinstance(m.get("prs"), list) or not all(isinstance(n, int) for n in m["prs"]):
            errors.append(f"{mid}: 'prs' must be a list of PR numbers")
        for p in paths:
            if p in seen_paths: errors.append(f"{mid}: path {p} already claimed by {seen_paths[p]}")
            seen_paths[p] = mid
        if m.get("required") is True:
            rs, rj = m.get("validate_all_steps") or [], m.get("ci_jobs") or []
            if not rs or not rj:
                errors.append(f"{mid}: required module must list validate_all_steps and ci_jobs")
            for s_ in rs:
                if f'"{s_}' not in va: errors.append(f"{mid}: required validate-all step not found: {s_!r}")
            for j in rj:
                wf, _, job = j.partition(":")
                if job not in wjobs.get(wf, set()): errors.append(f"{mid}: required CI job not found: {j}")
        present = [p for p in paths if any(claims(f, [p]) for f in files)]
        if st == "INTEGRATED":
            integrated_prefixes += paths
            for p in paths:
                if p not in present: errors.append(f"{mid}: INTEGRATED path missing from tree: {p}")
            steps, cij = m.get("validate_all_steps") or [], m.get("ci_jobs") or []
            if not steps and not cij: errors.append(f"{mid}: INTEGRATED module has no executable check")
            for s in steps:
                if f'"{s}' not in va: errors.append(f"{mid}: validate-all step not found: {s!r}")
            for j in cij:
                wf, _, job = j.partition(":")
                if job not in wjobs.get(wf, set()): errors.append(f"{mid}: CI job not found: {j}")
        else:
            if not isinstance(m.get("reason"), str) or not m["reason"]:
                errors.append(f"{mid}: {st} module needs a 'reason'")
            for p in present: errors.append(f"{mid}: {st} module path is present on this branch: {p} (register it as INTEGRATED with checks, or remove it)")
    gate = reg.get("required_gate_jobs")
    if not isinstance(gate, list) or not gate or not all(isinstance(j, str) for j in gate):
        errors.append("modules.json: 'required_gate_jobs' must be a non-empty list of integration-gate.yml job ids")
        gate = []
    gjobs = wjobs.get("integration-gate.yml", set())
    for m in mods:
        if m.get("required") is True:
            for j in m.get("ci_jobs") or []:
                wf, _, job = j.partition(":")
                if wf == "integration-gate.yml" and job not in gate:
                    errors.append(f"{m.get('id')}: required job {job} is not in required_gate_jobs")
    gtext = (ROOT / ".github/workflows/integration-gate.yml").read_text() if (ROOT / ".github/workflows/integration-gate.yml").exists() else ""
    for need_of in ("final-summary", "merge-eligibility"):
        mm = re.search(r"^  " + need_of + r":\n(?:    .*\n)*?    needs: \[([^\]]*)\]", gtext, re.M)
        listed = {x.strip() for x in mm.group(1).split(",")} if mm else set()
        for j in gate:
            if j not in gjobs: errors.append(f"required gate job not defined in integration-gate.yml: {j}")
            if j not in listed: errors.append(f"required gate job {j} is not in {need_of}.needs")
    for f in files:
        if not claims(f, integrated_prefixes):
            top = f.split("/")[0] if f.split("/")[0] not in NESTED or "/" not in f else "/".join(f.split("/")[:2])
            errors.append(f"unregistered tracked path: {f} (area {top})")
            if len(errors) > 200: break
    for e in errors: print("ERROR", e)
    n_int = sum(m.get("status") == "INTEGRATED" for m in mods)
    if errors:
        print(f"MODULE REGISTRY INVALID: {len(errors)} error(s)"); return 1
    print(f"MODULE REGISTRY OK: {len(mods)} modules ({n_int} INTEGRATED), {len(files)} tracked files all claimed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
