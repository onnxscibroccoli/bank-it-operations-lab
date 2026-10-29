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

AC2 / AC4 / AC5 (decisions_from_comments): decisions are PR comments on the trusted decision_pr whose body is exactly

    ACCEPTANCE-DECISION v1
    candidate: <40-hex candidate SHA>
    UA-1: APPROVE EX-01 EX-02 EX-03 EX-04        (owner only: binds the exception approval to the owner account)
    AC4: ACCEPT                                  (owner or allow-listed reviewer)
    AC5: ACCEPT                                  (owner or allow-listed reviewer)

  (any subset of decision lines; REJECT instead of APPROVE/ACCEPT records a rejection). A decision counts only when
  the comment author is authorized in the trusted config AND has the required permission at runtime, the candidate
  line equals this run's candidate exactly, and the comment was never edited. The latest authorized decision per
  item wins. AC2 needs UA-1 APPROVE naming EXACTLY the set of exceptions whose suppressions are applied; AC5 also
  needs AC2. In-tree statuses (tasks.json, the register's "APPROVED" text) never approve anything (F6/F7).
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


DEC_LINE = re.compile(r"^(UA-1|AC4|AC5):\s*(APPROVE|ACCEPT|REJECT)((?:\s+EX-\d{2})*)\s*$")


def parse_decision(body, header):
    lines = [x.strip() for x in (body or "").strip().splitlines() if x.strip()]
    if len(lines) < 3 or lines[0] != header:
        return None
    m = re.fullmatch(r"candidate:\s*([0-9A-Fa-f]{40})", lines[1])
    if not m:
        return None
    out = {"candidate": m.group(1).lower(), "items": {}}
    for x in lines[2:]:
        d = DEC_LINE.match(x)
        if not d:
            return None  # strict: any unrecognized line invalidates the whole comment
        out["items"][d.group(1)] = {"verb": d.group(2), "ids": sorted(set(d.group(3).split()))}
    return out


def decisions_from_comments(rv, ident, cfg, exc):
    """Pure. Returns {"AC2": (status, why), "AC4": ..., "AC5": ...}."""
    res = {}
    if not isinstance(rv, dict) or not rv.get("ok") or not rv.get("comments_ok"):
        why = ["decision comments not available: " + str((rv or {}).get("comments_error") or (rv or {}).get("error") if isinstance(rv, dict) else "no file")]
        return {k: ("UNMET", why) for k in ("AC2", "AC4", "AC5")}
    if not isinstance(cfg, dict):
        return {k: ("UNMET", ["trusted config not available"]) for k in ("AC2", "AC4", "AC5")}
    cand = norm((ident or {}).get("candidate_sha"))
    owners = {_l(x) for x in cfg.get("owner_logins") or []}
    reviewers = {_l(x) for x in cfg.get("reviewer_allowlist") or []}
    header = cfg.get("decision_header") or "ACCEPTANCE-DECISION v1"
    latest, notes = {}, []
    for c in sorted(rv.get("comments") or [], key=lambda c: (c.get("created_at") or "", c.get("id") or 0)):
        dec = parse_decision(c.get("body"), header)
        if dec is None:
            continue
        login = _l((c.get("user") or {}).get("login"))
        if c.get("updated_at") and c.get("created_at") and c["updated_at"] != c["created_at"]:
            notes.append(f"decision comment {c.get('id')} by {login} ignored: edited after posting"); continue
        if not cand or dec["candidate"] != cand:
            continue
        for item, v in dec["items"].items():
            if item == "UA-1":
                ok = login in owners and has_perm(rv, login, cfg.get("owner_required_permission") or ["admin"])
            else:
                ok = (login in owners and has_perm(rv, login, cfg.get("owner_required_permission") or ["admin"])) or \
                     (login in reviewers and has_perm(rv, login, cfg.get("reviewer_required_permission") or ["admin", "maintain", "write"]))
            if not ok:
                notes.append(f"{item} decision by {login} ignored: not authorized by the trusted config / permission"); continue
            latest[item] = dict(v, by=login, comment=c.get("id"), at=c.get("created_at"))
    applied = sorted({u.get("exception") for u in (exc or {}).get("applied") or [] if u.get("exception")})
    ua1 = latest.get("UA-1")
    if (exc or {}).get("errors") or not isinstance((exc or {}).get("applied"), list):
        res["AC2"] = ("UNMET", ["security exception register inconsistent or not checked"])
    elif not applied:
        res["AC2"] = ("MET_AT_RUNTIME", ["no cdk-nag suppression is applied"])
    elif not ua1:
        res["AC2"] = ("UNMET", notes + [f"BLOCKING USER ACTION UA-1: no owner decision on candidate {cand} for applied exceptions {' '.join(applied)}"])
    elif ua1["verb"] != "APPROVE":
        res["AC2"] = ("UNMET", [f"UA-1 REJECTED by {ua1['by']} (comment {ua1['comment']})"])
    elif ua1["ids"] != applied:
        res["AC2"] = ("UNMET", [f"UA-1 approval by {ua1['by']} names {' '.join(ua1['ids']) or 'nothing'}, applied exceptions are {' '.join(applied)} (must match exactly)"])
    else:
        res["AC2"] = ("MET_AT_RUNTIME", [f"UA-1 APPROVE {' '.join(applied)} on {cand} by owner {ua1['by']} (comment {ua1['comment']}, {ua1['at']})"])
    for ac in ("AC4", "AC5"):
        d = latest.get(ac)
        if not d:
            res[ac] = ("UNMET", notes + [f"no authorized {ac} decision on candidate {cand}"])
        elif d["verb"] != "ACCEPT":
            res[ac] = ("UNMET", [f"{ac} REJECTED by {d['by']} (comment {d['comment']})"])
        elif ac == "AC5" and res["AC2"][0] != "MET_AT_RUNTIME":
            res[ac] = ("UNMET", [f"AC5 accepted by {d['by']}, but B5-1 is open until AC2 (UA-1) is met"])
        else:
            res[ac] = ("MET_AT_RUNTIME", [f"{ac} ACCEPT on {cand} by {d['by']} (comment {d['comment']}, {d['at']})"])
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
             "updated_at": c.get("updated_at"), "body": c.get("body") if (c.get("body") or "").lstrip().startswith("ACCEPTANCE-DECISION") else None}
            for c in com])
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
