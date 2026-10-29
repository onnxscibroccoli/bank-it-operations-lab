#!/usr/bin/env python3
"""R6 hardening (PR #30/#31): the candidate must not be able to weaken the verifier. Stdlib only.

The gate manifest (gate-manifest.json) is read from a TRUSTED location, never from the candidate: from main
(.github/acceptance/gate-manifest.json) when main carries one, else from the evidence/acceptance branch
(trusted-gate/gate-manifest.json). It records:
  gate_sha   the commit whose scripts/ci and .github/acceptance/trusted-config.json are executed/read by the gate;
  files      {path: sha256} for every verifier file (scripts/ci/**, the trusted config) and for
             .github/workflows/integration-gate.yml.
Checks (any failure -> exit 1, AC3 cannot be met in that run):
  1. the trusted gate checkout is exactly gate_sha;
  2. every verifier file in the trusted checkout hashes to the manifest value, and scripts/ci has no extra file;
  3. the CANDIDATE's copies of all manifest files hash to the manifest value, and the candidate's scripts/ci has no
     extra file: a candidate that modifies integration-gate.yml, scripts/ci or the trusted config without a matching
     trusted manifest update is rejected.
D3 (PR #32), pin independence (--check-pin): hash consistency is not trust. The pin is TRUSTED only if
  - gate_sha is not the candidate under evaluation (no self-pin), and
  - the manifest names an independent review {"pr": N, "review_id": ID} that, fetched from the GitHub API at runtime,
    is APPROVED with commit_id == gate_sha, by an account that is not that PR's author, is on the gate commit's trusted
    reviewer_allowlist and has write/maintain/admin permission.
  Otherwise the result is "TRUSTED GATE UNVERIFIED" and merge-eligibility is NOT ELIGIBLE (fail closed).
  evidence/acceptance (where the manifest lives until main carries it) must be protected (UA-3).
Residual: the job that runs this check is defined in the candidate's workflow file. A candidate could delete the step;
only UA-3 (branch protection / ruleset on main requiring the gate, with the gate run from main) closes that fully.
Usage: verify_trusted_gate.py --manifest FILE --gate-dir DIR --candidate-dir DIR --gate-head SHA [--out FILE]
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
GATE_SIDE = ("scripts/ci/",  ".github/acceptance/trusted-config.json", ".github/workflows/integration-gate.yml")
WORKFLOW_PATH = ".github/workflows/integration-gate.yml"
CONFIG_PATH = ".github/acceptance/trusted-config.json"


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def listing(root, sub="scripts/ci"):
    base = Path(root) / sub
    return sorted(str(p.relative_to(root)) for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts) if base.is_dir() else []


def build(gate_repo, gate_sha):
    """Manifest whose hashes are taken from the commit gate_sha itself (git objects), never from a working tree."""
    import subprocess
    names = subprocess.run(["git", "-C", str(gate_repo), "ls-tree", "-r", "--name-only", gate_sha, "scripts/ci"],
                           capture_output=True, check=True, text=True).stdout.split()
    names = [n for n in names if "__pycache__" not in n] + [CONFIG_PATH, WORKFLOW_PATH]
    files = {}
    for n in names:
        b = git_blob(gate_repo, gate_sha, n)
        if b is None:
            raise SystemExit(f"{n} not present at {gate_sha}")
        files[n] = hashlib.sha256(b).hexdigest()
    return {"schema": "bank-lab/gate-manifest/v2", "gate_sha": gate_sha, "hash_source": f"git show {gate_sha}:<path>",
            "files": dict(sorted(files.items()))}


def verify(man, gate_dir, cand_dir, gate_head):
    errs = []
    gs = (man or {}).get("gate_sha") or ""
    if not HEX40.match(gs):
        return ["manifest gate_sha missing or not 40-hex"]
    if (gate_head or "").strip().lower() != gs:
        errs.append(f"trusted gate checkout is {gate_head}, manifest pins {gs}")
    files = (man or {}).get("files") or {}
    if not files or ".github/workflows/integration-gate.yml" not in files or not any(f.startswith("scripts/ci/") for f in files):
        errs.append("manifest must list scripts/ci/** and .github/workflows/integration-gate.yml")
    man_ci = sorted(f for f in files if f.startswith("scripts/ci/"))
    for side, root in (("trusted gate", gate_dir), ("candidate", cand_dir)):
        for f, h in files.items():
            if side == "trusted gate" and not f.startswith(GATE_SIDE):
                continue
            p = Path(root) / f
            if not p.is_file():
                errs.append(f"{side}: {f} missing")
            elif sha256(p) != h:
                errs.append(f"{side}: {f} differs from the trusted manifest" + (" (candidate modifies the verifier without a matching trusted update)" if side == "candidate" else ""))
        extra = sorted(set(listing(root)) - set(man_ci))
        if extra:
            errs.append(f"{side}: files in scripts/ci not in the trusted manifest: {', '.join(extra)}")
    return errs


REVIEW_PERMS = ("admin", "maintain", "write")


def pin_trust(man, candidate_sha, cfg, review, pr_author, permission):
    """Pure. -> (status, reasons). status is "VERIFIED" or "UNVERIFIED"."""
    why = []
    g = str((man or {}).get("gate_sha") or "").lower()
    c = str(candidate_sha or "").lower()
    if not HEX40.match(g):
        return "UNVERIFIED", ["manifest gate_sha missing or not 40-hex"]
    if not HEX40.match(c):
        why.append("candidate SHA unknown: self-pin cannot be excluded")
    elif g == c:
        why.append(f"self-pin: gate_sha {g} is the candidate under evaluation")
    ir = (man or {}).get("independent_review")
    if not isinstance(ir, dict) or not ir.get("pr") or not ir.get("review_id"):
        why.append(f"no independently reviewed gate pin: the manifest records no qualifying review of gate_sha {g}")
    else:
        r = review if isinstance(review, dict) else {}
        login = str((r.get("user") or {}).get("login") or "").lower()
        allow = {str(x).lower() for x in (cfg or {}).get("reviewer_allowlist") or []}
        if r.get("error") or not r:
            why.append(f"review {ir.get('review_id')} on PR {ir.get('pr')} not fetched: {r.get('error')}")
        else:
            if r.get("state") != "APPROVED":
                why.append(f"review {r.get('id')} state {r.get('state')!r}, not APPROVED")
            if str(r.get("commit_id") or "").lower() != g:
                why.append(f"review {r.get('id')} is on {r.get('commit_id')}, not gate_sha {g}")
            if not login or login == str(pr_author or "").lower():
                why.append(f"review {r.get('id')} is by the PR author {login!r}")
            if login not in allow:
                why.append(f"reviewer {login!r} is not on the gate's trusted reviewer_allowlist")
            if permission not in REVIEW_PERMS:
                why.append(f"reviewer {login!r} has permission {permission!r}, not write/maintain/admin")
    return ("VERIFIED" if not why else "UNVERIFIED"), why


def fetch_pin_review(man, repo, token, base="https://api.github.com"):
    import urllib.request
    def api(path):
        rq = urllib.request.Request(base + path, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                                         "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "bank-lab-gate"})
        with urllib.request.urlopen(rq, timeout=30) as f:
            return json.loads(f.read().decode())
    ir = (man or {}).get("independent_review")
    if not isinstance(ir, dict) or not ir.get("pr") or not ir.get("review_id"):
        return None, None, None
    try:
        r = api(f"/repos/{repo}/pulls/{int(ir['pr'])}/reviews/{int(ir['review_id'])}")
        author = (api(f"/repos/{repo}/pulls/{int(ir['pr'])}").get("user") or {}).get("login")
        login = (r.get("user") or {}).get("login")
        perm = api(f"/repos/{repo}/collaborators/{login}/permission").get("permission") if login else None
        return r, author, perm
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, None, None


WORKFLOW = ".github/workflows/integration-gate.yml"
CONFIG = ".github/acceptance/trusted-config.json"


def git_blob(repo, sha, path):
    """Bytes of path at commit sha (git show sha:path), or None."""
    import subprocess
    try:
        return subprocess.run(["git", "-C", str(repo), "show", f"{sha}:{path}"], capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def git_head(repo):
    import subprocess
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, check=True, text=True).stdout.strip().lower()
    except (OSError, subprocess.CalledProcessError):
        return None


def pin_binding(man, gate_repo, executing_ci_dir, executing_config, workflow_repo, workflow_sha):
    """D3-a (PR #33). The EXPECTED hash of every gate file comes from the PINNED commit itself (git show <gate_sha>:path,
    hashed now), never from the candidate. Each must equal (1) the manifest's recorded hash and (2) the file actually
    executing in this run: the scripts/ci modules that are running, the trusted config being read, and the workflow
    file at GITHUB_WORKFLOW_SHA (the workflow GitHub is executing). Returns a list of errors (empty = bound)."""
    errs = []
    gs = str((man or {}).get("gate_sha") or "").lower()
    files = (man or {}).get("files") or {}
    if not HEX40.match(gs):
        return ["manifest gate_sha missing or not 40-hex"]
    if WORKFLOW not in files or CONFIG not in files or not any(f.startswith("scripts/ci/") for f in files):
        return ["manifest must list scripts/ci/**, the trusted config and the integration-gate workflow"]
    if git_head(gate_repo) != gs:
        errs.append(f"gate checkout HEAD {git_head(gate_repo)} is not the pinned gate_sha {gs}")
    wsha = str(workflow_sha or "").lower()
    if not HEX40.match(wsha):
        errs.append(f"executing workflow commit unknown (GITHUB_WORKFLOW_SHA={workflow_sha!r}): cannot bind the deciding workflow")
    pin_ci = set()
    for f, h in sorted(files.items()):
        blob = git_blob(gate_repo, gs, f)
        if blob is None:
            errs.append(f"{f}: not present at pinned commit {gs[:12]}"); continue
        expected = hashlib.sha256(blob).hexdigest()
        if expected != h:
            errs.append(f"{f}: manifest hash differs from the file at the pinned commit {gs[:12]} (manifest not derived from the pin)")
        if f.startswith("scripts/ci/"):
            pin_ci.add(f)
            run_p = Path(executing_ci_dir) / f[len("scripts/ci/"):]
            if not run_p.is_file() or sha256(run_p) != expected:
                errs.append(f"{f}: the executing copy differs from the pinned commit")
        elif f == CONFIG:
            if not Path(executing_config or "").is_file() or sha256(executing_config) != expected:
                errs.append(f"{f}: the trusted config being read differs from the pinned commit")
        elif f == WORKFLOW:
            if HEX40.match(wsha):
                run_wf = git_blob(workflow_repo, wsha, WORKFLOW)
                if run_wf is None:
                    errs.append(f"{WORKFLOW} at executing workflow commit {wsha[:12]} not readable")
                elif hashlib.sha256(run_wf).hexdigest() != expected:
                    errs.append(f"{WORKFLOW}: the EXECUTING workflow (at {wsha[:12]}) differs from the pinned commit {gs[:12]}")
    base = Path(executing_ci_dir)
    running = {"scripts/ci/" + str(q.relative_to(base)) for q in base.rglob("*") if q.is_file() and "__pycache__" not in q.parts}
    extra = sorted(running - pin_ci)
    if extra:
        errs.append("executing scripts/ci has files not in the pinned manifest: " + ", ".join(extra))
    return errs


def gate_trust_at_runtime(man, candidate_sha, gate_repo, executing_ci_dir, executing_config, workflow_repo, workflow_sha,
                          review_fetch=None):
    """D3 + D3-a, computed by the gate code itself (never read from a file the workflow could write)."""
    bind = pin_binding(man, gate_repo, executing_ci_dir, executing_config, workflow_repo, workflow_sha)
    try:
        cfg = json.loads(Path(executing_config).read_text())
    except (OSError, ValueError, TypeError):
        cfg = None
    rv, author, perm = (review_fetch or (lambda m: (None, None, None)))(man)
    status, why = pin_trust(man, candidate_sha, cfg, rv, author, perm)
    why = bind + why
    return {"schema": "bank-lab/gate-trust/v2", "status": "VERIFIED" if not why else "UNVERIFIED", "reasons": why,
            "gate_sha": (man or {}).get("gate_sha"), "candidate_sha": candidate_sha, "workflow_sha": workflow_sha,
            "independent_review": (man or {}).get("independent_review")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--gate-dir")
    ap.add_argument("--candidate-dir")
    ap.add_argument("--gate-head")
    ap.add_argument("--out")
    ap.add_argument("--build", action="store_true", help="write a manifest for commit --gate-head from git objects in repo --gate-dir to --out")
    ap.add_argument("--workflow")
    ap.add_argument("--check-pin", action="store_true", help="D3: decide pin independence (--manifest, --gate-dir, --candidate-sha) -> --out")
    ap.add_argument("--candidate-sha")
    ap.add_argument("--workflow-repo", help="git repo holding the executing workflow commit (GITHUB_WORKFLOW_SHA)")
    a = ap.parse_args(argv)
    if a.check_pin:
        import os
        try:
            man = json.loads(Path(a.manifest).read_text())
        except (OSError, ValueError, TypeError) as e:
            man = None
        env = os.environ
        res = gate_trust_at_runtime(man, a.candidate_sha, a.gate_dir, Path(a.gate_dir) / "scripts/ci", Path(a.gate_dir) / CONFIG,
                                    a.workflow_repo or ".", env.get("GITHUB_WORKFLOW_SHA"),
                                    lambda m: fetch_pin_review(m, env.get("GITHUB_REPOSITORY", ""), env.get("GITHUB_TOKEN", ""),
                                                               env.get("GITHUB_API_URL", "https://api.github.com")))
        if a.out:
            Path(a.out).write_text(json.dumps(res, indent=2) + "\n")
        for w in res["reasons"]:
            print("UNVERIFIED " + w)
        print(f"TRUSTED GATE {res['status']} (informational; merge_eligibility.py recomputes this itself and never reads this file)")
        return 0
    if a.build:
        m = build(a.gate_dir, a.gate_head)
        Path(a.out).write_text(json.dumps(m, indent=1) + "\n")
        print(f"manifest: gate_sha {a.gate_head}, {len(m['files'])} files"); return 0
    try:
        man = json.loads(Path(a.manifest).read_text())
    except (OSError, ValueError, TypeError) as e:
        man, errs = None, [f"trusted manifest unreadable: {e}"]
    else:
        errs = verify(man, a.gate_dir, a.candidate_dir, a.gate_head)
    if a.out:
        Path(a.out).write_text(json.dumps({"schema": "bank-lab/gate-verification/v1", "manifest_gate_sha": (man or {}).get("gate_sha"),
                                           "gate_head": a.gate_head, "ok": not errs, "errors": errs}, indent=2) + "\n")
    for e in errs:
        print("ERROR " + e)
    print("GATE HASHES " + ("MATCH: verifier code, trusted config and workflow match the manifest (hash consistency only; trust of the pin is decided by --check-pin, D3)" if not errs else f"REJECTED: {len(errs)} error(s)"))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
