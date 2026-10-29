#!/usr/bin/env python3
"""Validate coordination/modules.json against the working tree, scripts/validate-all.sh and .github/workflows.

Fails (exit 1) when:
  * a module entry is malformed, or a module id or a claimed path is duplicated;
  * an INTEGRATED module path is missing, or it lists a validate-all step / CI job that does not exist;
  * an EXCLUDED / NOT_INTEGRATED module path exists on this branch (a module slipped in without registration);
  * any tracked top-level path (or evidence/<x>, infra/<x>, identity/<x>, tests/<x>) is not claimed by an INTEGRATED module;
  * coverage (fail closed): a module lacks category/owner, a functional module lacks a delivery_location inside its paths
    (or, when INTEGRATED, its delivery_location is missing from the tree or it has no required_checks.present), a BLOCKED
    module lacks a reason, a SUPERSEDED module lacks a valid superseded_by, or the module count drops below
    coverage.denominator_floor (the portfolio denominator may not be narrowed silently).
Prints the denominator and coverage. --coverage-json FILE also writes them as JSON.
Stdlib only; reads files, never executes anything from them.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUSES = {"INTEGRATED", "EXCLUDED", "NOT_INTEGRATED", "BLOCKED", "SUPERSEDED", "NOT_STARTED"}
CATEGORIES = {"functional", "documentation", "review_record", "superseded", "blocked"}


def _as_list(v):
    return [v] if isinstance(v, str) else v


def coverage(reg):
    """Pure (no tree access): returns (summary dict, errors). Used by check_modules and user_actions."""
    errors, mods = [], reg.get("modules") or []
    ids = {m.get("id") for m in mods if isinstance(m, dict)}
    for m in mods:
        mid, st, cat = m.get("id"), m.get("status"), m.get("category")
        if cat not in CATEGORIES:
            errors.append(f"{mid}: category must be one of {sorted(CATEGORIES)}"); continue
        own = m.get("owner")
        if not (isinstance(own, dict) and isinstance(own.get("agent"), str) and own["agent"].strip()):
            errors.append(f"{mid}: owner.agent required (use 'unassigned' when none fits)")
        if (cat == "blocked") != (st == "BLOCKED"):
            errors.append(f"{mid}: category 'blocked' and status BLOCKED must go together")
        if (cat == "superseded") != (st == "SUPERSEDED"):
            errors.append(f"{mid}: category 'superseded' and status SUPERSEDED must go together")
        if st == "SUPERSEDED" and m.get("superseded_by") not in ids:
            errors.append(f"{mid}: SUPERSEDED needs superseded_by naming an existing module id")
        if st in ("BLOCKED", "NOT_STARTED", "EXCLUDED", "NOT_INTEGRATED") and not (isinstance(m.get("reason"), str) and m["reason"].strip()):
            errors.append(f"{mid}: {st} needs a reason")
        if cat == "functional" or st == "BLOCKED":
            dl = _as_list(m.get("delivery_location"))
            if not (isinstance(dl, list) and dl and all(isinstance(x, str) and x.strip() for x in dl)):
                errors.append(f"{mid}: functional module has no delivery_location"); continue
            for x in dl:
                if not claims(x, m.get("paths") or []):
                    errors.append(f"{mid}: delivery_location {x} is not inside the module's paths")
        rc = m.get("required_checks")
        if not (isinstance(rc, dict) and isinstance(rc.get("present"), list) and isinstance(rc.get("proposed"), list)):
            errors.append(f"{mid}: required_checks must be {{present: [...], proposed: [...]}}")
        elif st == "INTEGRATED" and cat == "functional" and not rc["present"]:
            errors.append(f"{mid}: INTEGRATED functional module has no required_checks.present")
    cov = reg.get("coverage") or {}
    floor = cov.get("denominator_floor")
    if not isinstance(floor, int) or floor < 1:
        errors.append("coverage.denominator_floor must be a positive integer")
    elif len(mods) < floor:
        errors.append(f"portfolio denominator narrowed: {len(mods)} modules < denominator_floor {floor}")
    by_cat, by_st = {}, {}
    for m in mods:
        by_cat.setdefault(m.get("category"), {}).setdefault(m.get("status"), 0)
        by_cat[m.get("category")][m.get("status")] += 1
        by_st[m.get("status")] = by_st.get(m.get("status"), 0) + 1
    sup = by_st.get("SUPERSEDED", 0)
    integ = by_st.get("INTEGRATED", 0)
    func = [m for m in mods if m.get("category") == "functional"]
    summary = {
        "denominator": len(mods),
        "completion_denominator": len(mods) - sup,
        "integrated": integ,
        "completion_pct": round(100.0 * integ / max(1, len(mods) - sup), 1),
        "functional": len(func),
        "functional_integrated": sum(m.get("status") == "INTEGRATED" for m in func),
        "functional_missing_delivery_location": sorted(m.get("id") for m in func if not _as_list(m.get("delivery_location"))),
        "by_status": by_st,
        "by_category": by_cat,
        "incomplete": sorted(f"{m.get('id')}({m.get('status')})" for m in mods if m.get("status") not in ("INTEGRATED", "SUPERSEDED")),
    }
    return summary, errors


def coverage_line(c):
    return (f"MODULE COVERAGE: {c['integrated']}/{c['completion_denominator']} integrated ({c['completion_pct']}%), "
            f"functional {c['functional_integrated']}/{c['functional']}; denominator {c['denominator']} "
            f"(" + ", ".join(f"{k}={v}" for k, v in sorted(c["by_status"].items())) + ")")
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


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cov_out = argv[argv.index("--coverage-json") + 1] if "--coverage-json" in argv else None
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
            for x in _as_list(m.get("delivery_location")) or []:
                if not any(claims(f, [x]) for f in files): errors.append(f"{mid}: delivery_location missing from tree: {x}")
            for j in (m.get("required_checks") or {}).get("present") or []:
                if j not in (m.get("ci_jobs") or []): errors.append(f"{mid}: required_checks.present {j} is not one of its ci_jobs")
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
    cov, cerr = coverage(reg)
    errors += cerr
    for e in errors: print("ERROR", e)
    print(coverage_line(cov))
    if cov_out:
        Path(cov_out).write_text(json.dumps(cov, indent=2) + "\n")
    n_int = sum(m.get("status") == "INTEGRATED" for m in mods)
    if errors:
        print(f"MODULE REGISTRY INVALID: {len(errors)} error(s)"); return 1
    print(f"MODULE REGISTRY OK: {len(mods)} modules ({n_int} INTEGRATED), {len(files)} tracked files all claimed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
