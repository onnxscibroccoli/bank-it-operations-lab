#!/usr/bin/env python3
"""Run identity / provenance for the integration gate (AC3 binding).

Computes the tuple the gate is evaluating and writes it as JSON (--out). Nothing is stored in the candidate tree:
the file is uploaded as a run artifact, so the evidence lives with the authenticated GitHub run, outside the tree.

  kind = "merge"   the tested commit is a two-parent merge of the candidate into the base:
                   pull_request events (GitHub's synthetic refs/pull/N/merge commit) and pushes to
                   candidate/main-validation-<sha> branches. tested_sha != candidate_sha.
  kind = "direct"  any other push: tested_sha == candidate_sha, no base. Such a run cannot satisfy AC3,
                   because the candidate was not tested as a merge with main.

Every SHA is validated as 40 lowercase hex. Cross-checks (any mismatch -> exit 1, identity INVALID):
  pull_request: tested^2 == event.pull_request.head.sha (candidate); tested^1 recorded as base_sha and compared
                with event.pull_request.base.sha (a moved base is recorded as base_moved, not hidden)
  candidate/main-validation-<abbrev>: tested^2 starts with <abbrev>; tested^1 == base
  F1 (PR #30): for every kind "merge", base_sha (tested^1) MUST equal the CURRENT main SHA, read at runtime from the
  base ref (env TRUSTED_MAIN_SHA, set by the workflow from `git ls-remote origin refs/heads/main`, or --main-sha).
  A merge into any other commit (an old candidate, a side branch) is INVALID, as is a missing main SHA.
  pull_request: the event's base ref must be main and a moved base (event base != tested^1) is INVALID.
Usage: provenance.py --out FILE [--summary FILE] [--main-sha SHA]. Standard library + git only; no token.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def norm(s):
    s = (s or "").strip().lower()
    return s if HEX40.match(s) else None


def git(*args):
    p = subprocess.run(["git", *args], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def parents(sha):
    out = git("rev-list", "--parents", "-n", "1", sha)
    return [norm(x) for x in out.split()[1:]] if out else None


def compute(env):
    errs = []
    event = env.get("GITHUB_EVENT_NAME", "local")
    tested = norm(env.get("GITHUB_SHA") or git("rev-parse", "HEAD"))
    ref = env.get("GITHUB_REF_NAME", "") or ""
    ident = {"schema": "bank-lab/run-identity/v1", "event": event, "ref_name": ref,
             "repository": env.get("GITHUB_REPOSITORY"), "run_id": env.get("GITHUB_RUN_ID"),
             "run_attempt": env.get("GITHUB_RUN_ATTEMPT"), "tested_sha": tested}
    if not tested:
        return ident | {"valid": False, "errors": ["tested SHA is not 40-hex"]}
    ps = parents(tested)
    if ps is None:
        errs.append("cannot read parents of the tested commit (fetch-depth too shallow?)")
        ps = []
    payload = {}
    if env.get("GITHUB_EVENT_PATH") and Path(env["GITHUB_EVENT_PATH"]).exists():
        payload = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text())
    if event == "pull_request":
        pr = payload.get("pull_request") or {}
        head, base_ev = norm((pr.get("head") or {}).get("sha")), norm((pr.get("base") or {}).get("sha"))
        ident.update(kind="merge", pr=pr.get("number"), candidate_sha=head,
                     base_sha=ps[0] if len(ps) == 2 else None, event_base_sha=base_ev)
        if len(ps) != 2:
            errs.append(f"pull_request tested commit has {len(ps)} parent(s), expected the 2-parent synthetic merge")
        elif ps[1] != head:
            errs.append(f"synthetic merge second parent {ps[1]} != pull_request.head.sha {head}")
        if base_ev and ident["base_sha"] and base_ev != ident["base_sha"]:
            ident["base_moved"] = True
            errs.append(f"base moved: tested^1 {ident['base_sha']} != pull_request.base.sha {base_ev}")
        if (pr.get("base") or {}).get("ref") not in (None, "main"):
            errs.append(f"pull_request base ref is {(pr.get('base') or {}).get('ref')!r}, not main")
    elif event == "push" and ref.startswith("candidate/main-validation-"):
        abbrev = ref.rsplit("-", 1)[-1].lower()
        ident.update(kind="merge", candidate_sha=ps[1] if len(ps) == 2 else None, base_sha=ps[0] if len(ps) == 2 else None)
        if len(ps) != 2:
            errs.append(f"main-validation commit has {len(ps)} parent(s), expected a --no-ff merge")
        elif not (re.fullmatch(r"[0-9a-f]{7,40}", abbrev) and ps[1].startswith(abbrev)):
            errs.append(f"branch suffix {abbrev!r} does not identify the merged candidate {ps[1]}")
    else:
        ident.update(kind="direct", candidate_sha=tested, base_sha=None)
    if ident.get("kind") == "merge":
        raw_main = env.get("TRUSTED_MAIN_SHA")
        main_sha = norm(raw_main)
        ident["main_sha_at_runtime"] = main_sha
        if not main_sha:
            errs.append(f"current main SHA not available or not 40-hex (TRUSTED_MAIN_SHA={raw_main!r}): base cannot be verified as main")
        elif ident.get("base_sha") and ident["base_sha"] != main_sha:
            errs.append(f"base {ident['base_sha']} is not the current main {main_sha}: candidate was merged into a non-main parent")
    # Correct parent SHAs alone do not prove the tested contents. Recompute the
    # clean merge tree using Git; conflict or unavailable objects is fail-closed.
    if ident.get("kind") == "merge" and len(ps) == 2:
        actual_tree = norm(git("rev-parse", tested + "^{tree}"))
        merged = git("merge-tree", "--write-tree", ps[0], ps[1])
        expected_tree = norm(merged.splitlines()[0]) if merged else None
        ident["tested_tree_sha"] = actual_tree
        ident["expected_tree_sha"] = expected_tree
        if not expected_tree or actual_tree != expected_tree:
            errs.append("tested tree does not match the clean merge of main and candidate (or merge conflicts)")
    for k in ("candidate_sha", "tested_sha") + (("base_sha",) if ident.get("kind") == "merge" else ()):
        if not ident.get(k):
            errs.append(f"{k} missing or not 40-hex")
    if ident.get("kind") == "merge" and ident.get("candidate_sha") and ident["candidate_sha"] == tested:
        errs.append("merge identity with candidate_sha == tested_sha")
    ident["valid"] = not errs
    ident["errors"] = errs
    return ident


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary")
    ap.add_argument("--main-sha", help="current main SHA (overrides env TRUSTED_MAIN_SHA)")
    a = ap.parse_args(argv)
    env = dict(os.environ)
    if a.main_sha:
        env["TRUSTED_MAIN_SHA"] = a.main_sha
    ident = compute(env)
    Path(a.out).write_text(json.dumps(ident, indent=2) + "\n")
    print(json.dumps(ident, indent=2))
    if a.summary:
        with open(a.summary, "a") as f:
            f.write("### Run identity (AC3 provenance)\n\n| field | value |\n|---|---|\n")
            for k in ("event", "kind", "candidate_sha", "base_sha", "main_sha_at_runtime", "tested_sha", "run_id", "run_attempt", "valid"):
                f.write(f"| {k} | `{ident.get(k)}` |\n")
    return 0 if ident["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
