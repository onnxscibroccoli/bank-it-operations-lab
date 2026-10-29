#!/usr/bin/env python3
"""Merge-eligibility check (PR #27 C6 policy). It never merges anything.

main may be merged automatically only when AC1-AC5 are satisfied for the EXACT identity under evaluation, and
every required check job (coordination/modules.json required_gate_jobs, plus final-summary) and every required
output succeeded in THIS run. AC6 (human portfolio acceptance) is a separate gate: it is reported, not checked.

Identity: a run-identity file from provenance.py (--identity), giving candidate_sha, base_sha, tested_sha and kind:
  kind "merge"   the tested commit is a merge of the candidate into base (PR synthetic merge or candidate/main-validation)
  kind "direct"  tested == candidate (no base)
AC status values in coordination/tasks.json:
  "COMPUTED_AT_RUNTIME" (AC1 and AC3 only; anything else is rejected):
      AC3: satisfied only when the identity is a valid kind "merge" (base verified == current main, provenance.py F1)
           AND every required job and output in this run succeeded.
      AC1: satisfied only from the GitHub reviews API (--reviews, written by reviews.py with the read-only
           GITHUB_TOKEN): an APPROVED review on the exact candidate SHA by an account other than the PR author
           (reviews.ac1_from_reviews). A same-account review can never satisfy AC1. AC1 "MET" in tasks.json is
           rejected: an approval cannot be self-asserted in the tree it approves (PR #30 F3).
      The decision is written to --decision-out (uploaded as a run artifact), never stored as MET in the candidate
      tree, so recording it cannot change the SHA it describes.
  Security exceptions (B5-1): check_exceptions.py is evaluated on the data root (or --exceptions FILE). Any applied
      cdk-nag suppression tied to a non-APPROVED exception (or an inconsistent register) is a blocking user action
      (UA-1) and forces AC2 and AC5 UNMET, whatever tasks.json says.
  "MET": requires met_for = {candidate_sha, base_sha, tested_sha} (each exactly 40 hex, case-normalized) equal to
      this run's identity, and a non-empty evidence string. A missing, abbreviated, non-hex or different SHA is NOT
      eligible; a candidate SHA given where the tested-merge SHA belongs (or the reverse) is reported as a mixup.
      A legacy bare met_for_sha is not accepted.
  anything else: not satisfied.
--root DIR: the tree whose data (coordination/tasks.json, coordination/modules.json, the exception register and
  synthesized templates) is evaluated. In CI this is the candidate checkout, while the gate CODE runs from a trusted
  checkout (main if it carries the gate, else a pinned SHA): the candidate does not grade itself with its own copy.
--lint-tasks: fail if tasks.json carries a MET without a complete met_for binding, COMPUTED_AT_RUNTIME on an AC other
  than AC1/AC3, or AC1 as MET.
Exit 0 = eligible (or lint clean), 1 = not eligible (expected while conditions are open) or lint violations.
"""
import argparse, json, os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import user_actions  # noqa: E402
import check_exceptions, reviews  # noqa: E402

RUNTIME_ACS = ("AC1", "AC3")
TECH = ["AC1", "AC2", "AC3", "AC4", "AC5"]
RUNTIME = "COMPUTED_AT_RUNTIME"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
FIELDS = ("candidate_sha", "base_sha", "tested_sha")


def norm(v):
    if not isinstance(v, str):
        return None
    v = v.strip().lower()
    return v if HEX40.match(v) else None


def binding_problems(ac, c, ident):
    """Problems with a MET condition's binding to this identity (empty list = bound to exactly this identity)."""
    p = []
    mf = c.get("met_for")
    if not isinstance(mf, dict):
        if "met_for_sha" in c:
            return [f"{ac}: MET bound only by legacy met_for_sha={c.get('met_for_sha')!r}; a full met_for {{candidate_sha, base_sha, tested_sha}} is required"]
        return [f"{ac}: MET without met_for binding (naked MET)"]
    if not (isinstance(c.get("evidence"), str) and c["evidence"].strip()):
        p.append(f"{ac}: MET without evidence")
    for k in FIELDS:
        raw = mf.get(k)
        v = norm(raw)
        if raw is None or raw == "":
            p.append(f"{ac}: met_for.{k} missing")
        elif v is None:
            p.append(f"{ac}: met_for.{k}={raw!r} is not a full 40-hex SHA")
        elif ident is None:
            p.append(f"{ac}: no run identity to compare met_for.{k} with")
        elif v != norm(ident.get(k)):
            other = [o for o in FIELDS if o != k and norm(ident.get(o)) == v]
            if other:
                p.append(f"{ac}: met_for.{k} is this run's {other[0]} ({v}): candidate/merge/base mixup")
            else:
                p.append(f"{ac}: MET for {k} {v}, not this run's {ident.get(k)}")
    return p


def lint(conds):
    v = []
    for ac, c in conds.items():
        st = c.get("status")
        if st == RUNTIME and ac not in RUNTIME_ACS:
            v.append(f"{ac}: {RUNTIME} is only allowed for AC1 and AC3")
        if ac == "AC1" and st == "MET":
            v.append("AC1: MET in tasks.json is not accepted; AC1 must be COMPUTED_AT_RUNTIME from the GitHub reviews API")
        if st == "MET":
            v += [x for x in binding_problems(ac, c, None) if "no run identity" not in x]
    return v


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary")
    ap.add_argument("--identity", default=os.environ.get("RUN_IDENTITY"))
    ap.add_argument("--decision-out")
    ap.add_argument("--lint-tasks", action="store_true")
    ap.add_argument("--root", default=str(user_actions.ROOT), help="data root (candidate checkout)")
    ap.add_argument("--tasks")
    ap.add_argument("--reviews", help="reviews.py output (AC1 at runtime)")
    ap.add_argument("--exceptions", help="check_exceptions.py --out JSON (default: evaluate --root)")
    a = ap.parse_args(argv)
    root = Path(a.root)
    d = json.loads(Path(a.tasks or root / "coordination/tasks.json").read_text())
    conds = {c.get("id"): c for c in (d.get("acceptance_conditions_for_main") or {}).get("conditions") or []}
    if a.lint_tasks:
        v = lint(conds)
        for x in v:
            print("TASKS LINT " + x)
        print("TASKS LINT " + ("FAILED: %d violation(s)" % len(v) if v else "OK: no naked or mis-bound MET"))
        return 1 if v else 0

    problems, ident = [], None
    if a.identity and Path(a.identity).exists():
        ident = json.loads(Path(a.identity).read_text())
        if not ident.get("valid"):
            problems.append("run identity INVALID: " + "; ".join(map(str, ident.get("errors") or [])))
    else:
        problems.append("run identity not available (provenance.py --out): not verified for any exact SHA")

    # Required checks for this exact run: missing, skipped, cancelled or failed all make the identity ineligible.
    reg = json.loads((root / "coordination/modules.json").read_text())
    required = reg.get("required_gate_jobs") or []
    req_problems = []
    if not required:
        req_problems.append("required_gate_jobs missing from coordination/modules.json")
    raw = os.environ.get("NEEDS_JSON")
    needs = json.loads(raw) if raw else None
    if not isinstance(needs, dict):
        req_problems.append("required check results not available (NEEDS_JSON unset): not verified for this SHA")
    else:
        for job in required + ["final-summary"]:
            res = (needs.get(job) or {}).get("result", "missing") if job in needs else "missing"
            if res != "success":
                req_problems.append(f"required check {job}: {res}")
        import final_summary
        for job, k, v in final_summary.output_problems(needs, reg):
            req_problems.append(f"required check {job}.{k}: {v}")
    problems += req_problems

    rv = None
    if a.reviews and Path(a.reviews).exists():
        rv = json.loads(Path(a.reviews).read_text())
    exc = json.loads(Path(a.exceptions).read_text()) if a.exceptions else check_exceptions.evaluate(root)
    exc_block = []
    if exc.get("errors"):
        exc_block += ["security exception register inconsistent: " + "; ".join(exc["errors"])]
    if exc.get("unapproved"):
        ids = sorted({u.get("exception") for u in exc["unapproved"]})
        exc_block += [f"BLOCKING USER ACTION UA-1: {len(exc['unapproved'])} applied cdk-nag suppression(s) tied to non-APPROVED exception(s) {', '.join(ids)}"]
    if not isinstance(exc.get("applied"), list):
        exc_block += ["security exception check did not run"]

    ac_results = {}
    for ac in TECH:
        c = conds.get(ac)
        if c is None:
            ac_results[ac] = ("UNMET", ["missing"])
            continue
        st = c.get("status")
        if ac == "AC1" and st == "MET":
            ac_results[ac] = ("UNMET", ["AC1: MET in tasks.json is self-asserted; AC1 must be computed from the GitHub reviews API"])
        elif st == RUNTIME and ac == "AC1":
            ac_results[ac] = reviews.ac1_from_reviews(rv, ident) if rv is not None else ("UNMET", ["reviews not fetched (--reviews)"])
        elif st == RUNTIME:
            if ac != "AC3":
                ac_results[ac] = ("UNMET", [f"{RUNTIME} not allowed for {ac}"])
            elif ident is None or not ident.get("valid"):
                ac_results[ac] = ("UNMET", ["no valid run identity"])
            elif ident.get("kind") != "merge":
                ac_results[ac] = ("UNMET", ["direct run: the candidate was not tested as a merge with main in this run"])
            elif req_problems:
                ac_results[ac] = ("UNMET", ["required checks did not all succeed in this run"])
            else:
                ac_results[ac] = ("MET_AT_RUNTIME", [f"candidate {ident['candidate_sha']} merged into base {ident['base_sha']} "
                                                      f"as {ident['tested_sha']}; run {ident.get('run_id')} attempt {ident.get('run_attempt')}"])
        elif st == "MET":
            bp = binding_problems(ac, c, ident)
            ac_results[ac] = ("MET", []) if not bp else ("UNMET", bp)
        else:
            ac_results[ac] = ("UNMET", [f"{ac}: {st}"])
    for ac in ("AC2", "AC5"):
        if exc_block:
            st, why = ac_results[ac]
            ac_results[ac] = ("UNMET", ([f"{ac}: {st} in tasks.json overridden"] if st != "UNMET" else []) + list(why) + exc_block)
    for ac, (st, why) in ac_results.items():
        if st not in ("MET", "MET_AT_RUNTIME"):
            problems += why if any(w.startswith(ac) for w in why) else [f"{ac}: {'; '.join(why)}"]

    ac6 = (conds.get("AC6") or {}).get("status", "missing")
    verdict = "ELIGIBLE" if not problems else "NOT ELIGIBLE"
    label = (ident or {}).get("tested_sha") or "local"
    print(f"merge-eligibility for tested {label} (candidate {(ident or {}).get('candidate_sha')}): {verdict}")
    for ac, (st, why) in ac_results.items():
        print(f"  {ac}: {st}" + (f" ({'; '.join(why)})" if why else ""))
    for p in problems:
        print("::notice title=merge-eligibility::" + user_actions.esc_cmd(p))
    if a.decision_out:
        Path(a.decision_out).write_text(json.dumps({
            "schema": "bank-lab/merge-eligibility-decision/v1", "identity": ident, "verdict": verdict,
            "acceptance": {ac: {"status": st, "detail": why} for ac, (st, why) in ac_results.items()},
            "AC6": ac6, "required_check_problems": req_problems, "problems": problems,
            "gate_code": {"source": os.environ.get("GATE_SOURCE", "local"), "sha": os.environ.get("GATE_SHA"),
                          "data_root": str(root)},
            "reviews": {k: (rv or {}).get(k) for k in ("ok", "pr", "pr_author", "head_sha", "error")} if rv is not None else None,
            "security_exceptions": {"applied": len(exc.get("applied") or []), "unapproved": sorted({u.get("exception") for u in exc.get("unapproved") or []}),
                                    "errors": exc.get("errors"), "blocking_user_action": bool(exc_block)},
            "required_jobs": {j: (needs or {}).get(j, {}).get("result", "missing") for j in required + ["final-summary"]} if isinstance(needs, dict) else None,
            "policy": "PR #27 C6"}, indent=2) + "\n")
    if a.summary:
        md = [f"### Merge eligibility: **{verdict}**", "",
              f"Candidate `{(ident or {}).get('candidate_sha')}`, base `{(ident or {}).get('base_sha')}`, tested `{label}` ({(ident or {}).get('kind')}).", "",
              "Policy: PR #27 finding C6. AC1-AC5 must be satisfied for this exact identity; AC6 is a separate human gate "
              f"(currently {user_actions.esc_md(str(ac6))}).", "", "| AC | status |", "|---|---|"]
        md += [f"| {ac} | {st} |" for ac, (st, _) in ac_results.items()]
        md += [""] + [f"- {user_actions.esc_md(p)}" for p in problems]
        with open(a.summary, "a") as f:
            f.write("\n".join(md) + "\n")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
