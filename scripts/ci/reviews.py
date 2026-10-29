#!/usr/bin/env python3
"""Runtime acceptance evidence from GitHub (PR #30 F3/R6, PR #31 F4/F5/F6/F7). Read-only.

Uses only the workflow's own GITHUB_TOKEN (job permissions pull-requests: read, issues: read); never another
credential, never writes. Who may approve or decide comes from the TRUSTED config (.github/acceptance/trusted-config.json
read from main, or from the pinned gate commit), never from the candidate.

AC1 (ac1_from_reviews) is MET_AT_RUNTIME only when ALL hold:
  * the PR's current head SHA == the run identity's candidate_sha;
  * an approver whose latest decisive review is APPROVED with commit_id == candidate_sha, and who is
      - not the PR author (case-insensitive),
      - on the trusted reviewer_allowlist, and
      - has write / maintain / admin permission (GET /repos/{repo}/collaborators/{login}/permission);
  * no non-author account's latest decisive review is CHANGES_REQUESTED, on ANY commit (F5: GitHub keeps such a
    review blocking until it is dismissed).
  A random account approving (public repo) or a same-account review can never satisfy AC1. Any fetch error -> UNMET.

AC2 / AC4 / AC5 (decisions_from_comments): INDEPENDENT ACCEPTANCE lives outside the candidate, as attestation comments
  on the trusted decision_pr. GitHub vouches for the comment's LOGIN and timestamp, not for the person: decisions are
  owner-LOGIN-bound / reviewer-login-bound, not owner-authenticated (D2). Attestations from the PR author (the shared
  account all agents use) never count (D1); exception decisions from it are reported INSUFFICIENT_INDEPENDENCE
  (blocking) until a separate owner identity exists (O-5 / UA-6). workflow_run must be a completed integration-gate
  run (name + path) of the candidate or an attested tested merge whose jobs all succeeded except the fail-closed
  merge-eligibility job (D1):

    ACCEPTANCE-ATTESTATION v2
    candidate: <40-hex candidate SHA>
    main: <40-hex main SHA the candidate was tested against>
    tested_merge: <40-hex tested merge SHA> [<another tested merge SHA>]
    workflow_run: <Actions run id of that candidate (verified via the API: run.head_sha == candidate)>
    criterion: AC4 | AC5 | EXCEPTION
    decision: ACCEPT | REJECT                                    (AC4 / AC5)
              PROPOSED | APPROVED | REJECTED | APPROVED_WITH_CONDITIONS | SUPERSEDED | CONDITIONS_VERIFIED   (EXCEPTION)
    exception: EX-NN                                             (EXCEPTION only)
    scope: <rule> <applied resource logical ids, sorted>         (EXCEPTION only; must equal the applied suppressions)
    conditions: <text>                                           (required iff APPROVED_WITH_CONDITIONS)
    evidence: <ref> [<ref> ...]

  One criterion per comment; strict parse; edited comments ignored; latest authorized attestation wins. An
  attestation counts only for this run's exact candidate, main and tested merge. EXCEPTION decisions only from a
  trusted owner login with admin permission (F7); AC4/AC5 and CONDITIONS_VERIFIED from the owner or an allow-listed,
  write-permitted non-author reviewer. APPROVED_WITH_CONDITIONS is effective only after a later CONDITIONS_VERIFIED
  attestation for the same exception and scope. AC2 needs an effective approval for EVERY applied exception; AC5 also
  needs AC2. Candidate-produced evidence (tasks.json statuses, the register's status text) never satisfies anything.
Usage: reviews.py --identity FILE --config FILE --out FILE   (env GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_API_URL)
"""
import argparse, json, os, re, sys, urllib.error, urllib.request
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
DECISIVE = {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}
EXID = re.compile(r"^EX-\d{2}$")


def norm(v):
    v = (v or "").strip().lower() if isinstance(v, str) else ""
    return v if HEX40.match(v) else None


def _l(s):
    return (s or "").strip().lower()


def has_perm(rv, login, allowed):
    p = (rv.get("permissions") or {}).get(_l(login)) or {}
    return bool({_l(p.get("role_name")), _l(p.get("permission"))} & {_l(a) for a in allowed})


def ac1_from_reviews(rv, ident, cfg=None):
    """Pure. Returns (status, [details]). status is MET_AT_RUNTIME or UNMET."""
    if not isinstance(rv, dict) or not rv.get("ok"):
        return "UNMET", ["reviews not available: " + str((rv or {}).get("error") if isinstance(rv, dict) else "no reviews file")]
    if not isinstance(cfg, dict):
        return "UNMET", ["trusted config not available: no reviewer allow-list"]
    cand = norm((ident or {}).get("candidate_sha"))
    if not cand:
        return "UNMET", ["no valid candidate SHA in the run identity"]
    if norm(rv.get("head_sha")) != cand:
        return "UNMET", [f"PR #{rv.get('pr')} head {rv.get('head_sha')} is not the candidate {cand}"]
    author = _l(rv.get("pr_author"))
    if not author:
        return "UNMET", ["PR author unknown"]
    allow = {_l(x) for x in cfg.get("reviewer_allowlist") or []} - {author}
    perms = cfg.get("reviewer_required_permission") or ["admin", "maintain", "write"]
    latest = {}
    for r in sorted(rv.get("reviews") or [], key=lambda r: (r.get("submitted_at") or "", r.get("id") or 0)):
        st, login = r.get("state"), _l((r.get("user") or {}).get("login"))
        if st in DECISIVE and login:
            latest[login] = r
    notes, approvals, blockers = [], [], []
    if author in latest:
        notes.append(f"review(s) by the PR author {author} ignored: a same-account review cannot satisfy AC1")
    for login, r in latest.items():
        if login == author:
            continue
        if r["state"] == "CHANGES_REQUESTED":
            blockers.append(f"{login}@{(r.get('commit_id') or '')[:12]}")
            continue
        if r["state"] != "APPROVED" or norm(r.get("commit_id")) != cand:
            continue
        if login not in allow:
            notes.append(f"approval by {login} ignored: not on the trusted reviewer_allowlist")
        elif not has_perm(rv, login, perms):
            notes.append(f"approval by {login} ignored: lacks {'/'.join(perms)} permission on the repository")
        else:
            approvals.append(f"{login} (review {r.get('id')}, {r.get('submitted_at')})")
    if blockers:
        return "UNMET", notes + [f"CHANGES_REQUESTED (not dismissed) by: {', '.join(sorted(blockers))}"]
    if not allow:
        notes.append("trusted reviewer_allowlist is empty")
    if not approvals:
        return "UNMET", notes + [f"no APPROVED review on exact candidate {cand} by an allow-listed, write-permitted account other than the PR author {author}"]
    return "MET_AT_RUNTIME", notes + [f"APPROVED on {cand} by " + "; ".join(approvals)]


ATT_HEADER = "ACCEPTANCE-ATTESTATION v2"
EXC_STATES = {"PROPOSED", "APPROVED", "REJECTED", "APPROVED_WITH_CONDITIONS", "SUPERSEDED", "CONDITIONS_VERIFIED"}
AC_STATES = {"ACCEPT", "REJECT"}
KEYS = {"candidate", "main", "tested_merge", "workflow_run", "criterion", "decision", "exception", "scope", "conditions", "evidence"}


def parse_attestation(body):
    """Strict 'key: value' attestation. Returns dict or None (any unknown/duplicate key or malformed value -> None)."""
    lines = [x.strip() for x in (body or "").strip().splitlines() if x.strip()]
    if not lines or lines[0] != ATT_HEADER:
        return None
    a = {}
    for x in lines[1:]:
        k, sep, v = x.partition(":")
        k, v = k.strip(), v.strip()
        if not sep or k not in KEYS or k in a or not v:
            return None
        a[k] = v
    for k in ("candidate", "main"):
        if not HEX40.match(a.get(k, "").lower()):
            return None
        a[k] = a[k].lower()
    tm = a.get("tested_merge", "").lower().split()
    if not tm or not all(HEX40.match(x) for x in tm):
        return None
    a["tested_merge"] = tm
    if not re.fullmatch(r"\d{5,20}", a.get("workflow_run", "")):
        return None
    a["evidence"] = a.get("evidence", "").split()
    if not a["evidence"]:
        return None
    c, d = a.get("criterion"), a.get("decision")
    if c in ("AC4", "AC5"):
        if d not in AC_STATES or {"exception", "scope", "conditions"} & set(a):
            return None
    elif c == "EXCEPTION":
        if d not in EXC_STATES or not EXID.match(a.get("exception", "")) or not a.get("scope"):
            return None
        if (d == "APPROVED_WITH_CONDITIONS") != ("conditions" in a):
            return None
    else:
        return None
    return a


def exception_scopes(exc):
    """{EX-id: 'RULE RES1 RES2...'} from the applied suppressions (resources sorted)."""
    sc = {}
    for u in (exc or {}).get("applied") or []:
        if u.get("exception"):
            sc.setdefault(u["exception"], {"rule": u.get("rule"), "res": set()})["res"].add(u.get("resource"))
    return {k: f"{v['rule']} " + " ".join(sorted(v["res"])) for k, v in sc.items()}


GATE_WORKFLOW_PATH = ".github/workflows/integration-gate.yml"
GATE_WORKFLOW_NAME = "integration-gate"
FAIL_CLOSED_JOB = "merge-eligibility"


def run_problem(run, cand, tested_list):
    """None if `run` (from GET /actions/runs/{id} + /jobs) is a completed, successful integration-gate run of the candidate
    or of one of its attested tested merges; else the reason. 'Successful' = conclusion success, or every job succeeded
    except the fail-closed merge-eligibility job (which fails by design while NOT ELIGIBLE), with final-summary success."""
    if not isinstance(run, dict) or not run:
        return "run not fetched"
    if run.get("error"):
        return run["error"]
    path = (run.get("path") or "").split("@")[0]
    if path != GATE_WORKFLOW_PATH or run.get("name") != GATE_WORKFLOW_NAME:
        return f"not an {GATE_WORKFLOW_NAME} run (workflow {run.get('name')!r}, path {run.get('path')!r})"
    if norm(run.get("head_sha")) not in {cand, *tested_list}:
        return f"head_sha {run.get('head_sha')} is neither the candidate nor an attested tested merge"
    if run.get("status") != "completed":
        return f"run status {run.get('status')!r}, not completed"
    if run.get("conclusion") == "success":
        return None
    jobs = run.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        return f"conclusion {run.get('conclusion')!r} and job results unavailable"
    bad = [j.get("name") for j in jobs if j.get("name") != FAIL_CLOSED_JOB and j.get("conclusion") != "success"]
    if bad:
        return f"conclusion {run.get('conclusion')!r}; jobs not successful: {', '.join(map(str, bad))}"
    if not any(j.get("name") == "final-summary" and j.get("conclusion") == "success" for j in jobs):
        return "final-summary job missing or not successful"
    return None


def attestations(rv, ident, cfg):
    """Attestations bound to this exact run identity, from accounts the trusted config authorizes, EXCLUDING the PR
    author (D1/D2). Returns (accepted list, notes, author_attestations)."""
    cand = norm((ident or {}).get("candidate_sha")); main = norm((ident or {}).get("base_sha")); tested = norm((ident or {}).get("tested_sha"))
    owners = {_l(x) for x in (cfg or {}).get("owner_logins") or []}
    reviewers = {_l(x) for x in (cfg or {}).get("reviewer_allowlist") or []}
    runs = rv.get("runs") or {}
    author = _l(rv.get("pr_author"))
    out, notes, by_author = [], [], []
    for c in sorted(rv.get("comments") or [], key=lambda c: (c.get("created_at") or "", c.get("id") or 0)):
        if not (c.get("body") or "").lstrip().startswith(ATT_HEADER):
            continue
        login = _l((c.get("user") or {}).get("login")); cid = c.get("id")
        a = parse_attestation(c.get("body"))
        if a is None:
            notes.append(f"attestation {cid} by {login} ignored: malformed"); continue
        if c.get("updated_at") != c.get("created_at"):
            notes.append(f"attestation {cid} by {login} ignored: edited after posting"); continue
        if a["candidate"] != cand:
            continue
        if not main or a["main"] != main:
            notes.append(f"attestation {cid} ignored: main {a['main'][:12]} is not this run's base/main {main}"); continue
        if tested not in a["tested_merge"]:
            notes.append(f"attestation {cid} ignored: this run's tested merge {tested} is not attested"); continue
        rp = run_problem(runs.get(a["workflow_run"]), cand, a["tested_merge"])
        if rp:
            notes.append(f"attestation {cid} ignored: workflow run {a['workflow_run']}: {rp}"); continue
        if not author or login == author:
            # D1/D2: the PR author (here the shared account all agents use) can never supply independent acceptance.
            by_author.append(dict(a, by=login, comment=cid, at=c.get("created_at")))
            notes.append(f"attestation {cid} by {login} ignored: INSUFFICIENT INDEPENDENCE (PR author / shared account"
                         + ("; PR author unknown" if not author else "") + ")"); continue
        is_owner = login in owners and has_perm(rv, login, (cfg or {}).get("owner_required_permission") or ["admin"])
        is_rev = login in reviewers and has_perm(rv, login, (cfg or {}).get("reviewer_required_permission") or ["admin", "maintain", "write"])
        if a["criterion"] == "EXCEPTION" and a["decision"] != "CONDITIONS_VERIFIED":
            ok = is_owner                      # F7: exception decisions are the owner-LOGIN's (owner-login-bound, not owner-authenticated)
        else:
            ok = is_owner or is_rev            # AC4/AC5 and verification of conditions: owner or allow-listed reviewer
        if not ok:
            notes.append(f"attestation {cid} by {login} ignored: not authorized by the trusted config / runtime permission"); continue
        out.append(dict(a, by=login, comment=cid, at=c.get("created_at")))
    return out, notes, by_author


def decisions_from_comments(rv, ident, cfg, exc):
    """Pure. Returns {"AC2": (status, why), "AC4": ..., "AC5": ..., "exceptions": {EX: state}}."""
    if not isinstance(rv, dict) or not rv.get("ok") or not rv.get("comments_ok"):
        why = ["attestations not available: " + str((rv or {}).get("comments_error") or (rv or {}).get("error") if isinstance(rv, dict) else "no file")]
        return {k: ("UNMET", why) for k in ("AC2", "AC4", "AC5")} | {"exceptions": {}}
    if not isinstance(cfg, dict):
        return {k: ("UNMET", ["trusted config not available"]) for k in ("AC2", "AC4", "AC5")} | {"exceptions": {}}
    atts, notes, by_author = attestations(rv, ident, cfg)
    author = _l(rv.get("pr_author"))
    owners = {_l(x) for x in cfg.get("owner_logins") or []}
    shared = sorted(owners & {author}) if author else sorted(owners)
    if shared:
        notes = notes + [f"owner login(s) {', '.join(shared)} = the PR author / shared account: owner decisions are owner-login-bound, "
                         "NOT owner-authenticated, and are insufficient-independence until a separate owner identity exists (O-5 / UA-6)"]
    cand = norm((ident or {}).get("candidate_sha"))
    res = {}
    scopes = exception_scopes(exc)
    state, why2 = {}, []
    for ex in sorted(scopes):
        mine = [a for a in atts if a["criterion"] == "EXCEPTION" and a["exception"] == ex]
        decs = [a for a in mine if a["decision"] != "CONDITIONS_VERIFIED"]
        last = decs[-1] if decs else None
        if last is None:
            if any(a["criterion"] == "EXCEPTION" and a["exception"] == ex for a in by_author):
                state[ex] = "INSUFFICIENT_INDEPENDENCE"
                why2.append(f"{ex}: INSUFFICIENT_INDEPENDENCE (decision posted by the PR author / shared account; blocking until O-5 / UA-6)")
            else:
                state[ex] = "PROPOSED"; why2.append(f"{ex}: PROPOSED (no owner-login-bound decision on {cand})")
            continue
        if " ".join(last["scope"].split()) != scopes[ex]:
            state[ex] = "PROPOSED"; why2.append(f"{ex}: owner decision scope '{last['scope']}' != applied '{scopes[ex]}'"); continue
        d = last["decision"]
        if d == "APPROVED_WITH_CONDITIONS":
            ver = [a for a in mine if a["decision"] == "CONDITIONS_VERIFIED" and (a["at"] or "") > (last["at"] or "")
                   and " ".join(a["scope"].split()) == scopes[ex]]
            state[ex] = "APPROVED_WITH_CONDITIONS (verified)" if ver else "APPROVED_WITH_CONDITIONS (conditions NOT verified)"
            why2.append(f"{ex}: {state[ex]} by {last['by']} (comment {last['comment']}); conditions: {last['conditions']}")
        else:
            state[ex] = d
            why2.append(f"{ex}: {d} by {last['by']} (comment {last['comment']}, {last['at']}, evidence {' '.join(last['evidence'])})")
    effective = {ex for ex, s in state.items() if s in ("APPROVED", "APPROVED_WITH_CONDITIONS (verified)")}
    if (exc or {}).get("errors") or not isinstance((exc or {}).get("applied"), list):
        res["AC2"] = ("UNMET", ["security exception register inconsistent or not checked"])
    elif set(scopes) - effective:
        res["AC2"] = ("UNMET", notes + why2 + [f"BLOCKING USER ACTION UA-1: applied exceptions without an effective owner-login-bound approval from an account distinct from the PR author: {' '.join(sorted(set(scopes) - effective))}"])
    else:
        res["AC2"] = ("MET_AT_RUNTIME", why2 or ["no cdk-nag suppression is applied"])
    for ac in ("AC4", "AC5"):
        mine = [a for a in atts if a["criterion"] == ac]
        d = mine[-1] if mine else None
        if not d:
            res[ac] = ("UNMET", notes + [f"no authorized {ac} attestation bound to candidate {cand} / this run's main and tested merge"])
        elif d["decision"] != "ACCEPT":
            res[ac] = ("UNMET", [f"{ac} REJECT by {d['by']} (comment {d['comment']})"])
        elif ac == "AC5" and res["AC2"][0] != "MET_AT_RUNTIME":
            res[ac] = ("UNMET", [f"AC5 ACCEPT by {d['by']}, but B5-1 is open until AC2 (UA-1) is met"])
        else:
            res[ac] = ("MET_AT_RUNTIME", [f"{ac} ACCEPT on {cand} by {d['by']} (comment {d['comment']}, {d['at']}, run {d['workflow_run']}, evidence {' '.join(d['evidence'])})"])
    res["exceptions"] = state
    return res


def api(path, token, base):
    req = urllib.request.Request(base.rstrip("/") + path, headers={
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": f"Bearer {token}"} if token else {})})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def fetch(ident, env, cfg=None):
    repo, token, base = env.get("GITHUB_REPOSITORY"), env.get("GITHUB_TOKEN"), env.get("GITHUB_API_URL", "https://api.github.com")
    cand = norm((ident or {}).get("candidate_sha"))
    out = {"schema": "bank-lab/pr-reviews/v2", "repository": repo, "candidate_sha": cand, "ok": False, "comments_ok": False}
    try:
        if not (repo and cand):
            raise ValueError("GITHUB_REPOSITORY or candidate_sha missing")
        n = (ident or {}).get("pr")
        if not n:
            pulls = [p for p in api(f"/repos/{repo}/commits/{cand}/pulls", token, base)
                     if p.get("state") == "open" and norm((p.get("head") or {}).get("sha")) == cand and (p.get("base") or {}).get("ref") == "main"]
            if len(pulls) != 1:
                raise ValueError(f"expected exactly one open PR into main with head {cand}, found {len(pulls)}")
            n = pulls[0]["number"]
        pr = api(f"/repos/{repo}/pulls/{int(n)}", token, base)
        revs, page = [], 1
        while True:
            chunk = api(f"/repos/{repo}/pulls/{int(n)}/reviews?per_page=100&page={page}", token, base)
            revs += chunk
            if len(chunk) < 100 or page >= 20:
                break
            page += 1
        out.update(ok=True, pr=int(n), pr_author=(pr.get("user") or {}).get("login"), head_sha=(pr.get("head") or {}).get("sha"),
                   base_ref=(pr.get("base") or {}).get("ref"),
                   reviews=[{"id": r.get("id"), "user": {"login": (r.get("user") or {}).get("login")}, "state": r.get("state"),
                             "commit_id": r.get("commit_id"), "submitted_at": r.get("submitted_at")} for r in revs])
    except Exception as e:  # any failure -> AC1 UNMET (fail closed)
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    try:
        dpr = int((cfg or {}).get("decision_pr") or out["pr"])
        com, page = [], 1
        while True:
            chunk = api(f"/repos/{repo}/issues/{dpr}/comments?per_page=100&page={page}", token, base)
            com += chunk
            if len(chunk) < 100 or page >= 20:
                break
            page += 1
        out.update(comments_ok=True, decision_pr=dpr, comments=[
            {"id": c.get("id"), "user": {"login": (c.get("user") or {}).get("login")}, "created_at": c.get("created_at"),
             "updated_at": c.get("updated_at"), "body": c.get("body") if (c.get("body") or "").lstrip().startswith("ACCEPTANCE-") else None}
            for c in com])
        runs = {}
        for c in out["comments"]:
            m = re.search(r"^\s*workflow_run:\s*(\d{5,20})\s*$", c.get("body") or "", re.M)
            if m and m.group(1) not in runs and len(runs) < 50:
                try:
                    r = api(f"/repos/{repo}/actions/runs/{m.group(1)}", token, base)
                    runs[m.group(1)] = {"head_sha": r.get("head_sha"), "event": r.get("event"), "name": r.get("name"),
                                        "path": r.get("path"), "status": r.get("status"),
                                        "conclusion": r.get("conclusion"), "html_url": r.get("html_url")}
                    js = api(f"/repos/{repo}/actions/runs/{m.group(1)}/jobs?per_page=100", token, base)
                    runs[m.group(1)]["jobs"] = [{"name": j.get("name"), "conclusion": j.get("conclusion")} for j in (js or {}).get("jobs") or []]
                except Exception as e:
                    runs[m.group(1)] = {"error": f"{type(e).__name__}: {e}"}
        out["runs"] = runs
    except Exception as e:
        out["comments_error"] = f"{type(e).__name__}: {e}"
    # permissions only for accounts the trusted config could authorize (limits calls; others never count)
    logins = {_l(x) for x in ((cfg or {}).get("owner_logins") or []) + ((cfg or {}).get("reviewer_allowlist") or [])}
    perms = {}
    for login in sorted(logins):
        try:
            p = api(f"/repos/{repo}/collaborators/{login}/permission", token, base)
            perms[login] = {"permission": p.get("permission"), "role_name": p.get("role_name")}
        except urllib.error.HTTPError as e:
            perms[login] = {"permission": "none", "role_name": None, "error": f"HTTP {e.code}"}
        except Exception as e:
            perms[login] = {"permission": "none", "role_name": None, "error": f"{type(e).__name__}: {e}"}
    out["permissions"] = perms
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", required=True)
    ap.add_argument("--config", help="TRUSTED config (never the candidate's copy)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    ident = json.loads(Path(a.identity).read_text()) if Path(a.identity).exists() else {}
    cfg = json.loads(Path(a.config).read_text()) if a.config and Path(a.config).exists() else None
    rv = fetch(ident, os.environ, cfg)
    rv["trusted_config"] = cfg
    Path(a.out).write_text(json.dumps(rv, indent=2) + "\n")
    st, why = ac1_from_reviews(rv, ident, cfg)
    print(f"AC1 (reviews API, PR #{rv.get('pr')}, author {rv.get('pr_author')}): {st}")
    for w in why:
        print("  " + w)
    print("permissions:", json.dumps(rv.get("permissions")))
    return 0  # informational; merge_eligibility.py decides


if __name__ == "__main__":
    sys.exit(main())
