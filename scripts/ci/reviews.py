#!/usr/bin/env python3
"""AC1 at runtime (PR #30 F3/R6): read the pull request's reviews from the GitHub REST API, read-only.

Uses only the workflow's own GITHUB_TOKEN (job permission pull-requests: read); never another credential, never
writes. Writes a reviews JSON (--out) that merge_eligibility.py --reviews evaluates with ac1_from_reviews():

  AC1 is MET_AT_RUNTIME only when ALL hold:
   * the PR's current head SHA == the run identity's candidate_sha (40-hex);
   * some account OTHER than the PR author has, as its latest APPROVED / CHANGES_REQUESTED / DISMISSED review,
     an APPROVED review whose commit_id == candidate_sha (an approval of any other commit does not count);
   * no account other than the author has CHANGES_REQUESTED as its latest decisive review on that exact SHA.
  A same-account review (reviewer login == PR author login) can never satisfy AC1. Any fetch error -> UNMET.

PR lookup: pull_request events use the event's PR number; pushes (candidate/main-validation-*) use
GET /repos/{repo}/commits/{candidate}/pulls and keep the open PR whose head.sha == candidate and base.ref == main.
Usage: reviews.py --identity FILE --out FILE   (env GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_API_URL)
"""
import argparse, json, os, re, sys, urllib.request
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
DECISIVE = {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}


def norm(v):
    v = (v or "").strip().lower() if isinstance(v, str) else ""
    return v if HEX40.match(v) else None


def ac1_from_reviews(rv, ident):
    """Pure. Returns (status, [details]). status is MET_AT_RUNTIME or UNMET."""
    if not isinstance(rv, dict) or not rv.get("ok"):
        return "UNMET", ["reviews not available: " + str((rv or {}).get("error") if isinstance(rv, dict) else "no reviews file")]
    cand = norm((ident or {}).get("candidate_sha"))
    if not cand:
        return "UNMET", ["no valid candidate SHA in the run identity"]
    if norm(rv.get("head_sha")) != cand:
        return "UNMET", [f"PR #{rv.get('pr')} head {rv.get('head_sha')} is not the candidate {cand}"]
    author = (rv.get("pr_author") or "").lower()
    if not author:
        return "UNMET", ["PR author unknown"]
    latest = {}
    for r in sorted(rv.get("reviews") or [], key=lambda r: (r.get("submitted_at") or "", r.get("id") or 0)):
        st, login = r.get("state"), ((r.get("user") or {}).get("login") or "").lower()
        if st in DECISIVE and login:
            latest[login] = r
    same = [l for l in latest if l == author]
    approvals, blockers = [], []
    for login, r in latest.items():
        if login == author:
            continue
        if norm(r.get("commit_id")) != cand:
            continue
        if r["state"] == "APPROVED":
            approvals.append(f"{login} (review {r.get('id')}, {r.get('submitted_at')})")
        elif r["state"] == "CHANGES_REQUESTED":
            blockers.append(login)
    notes = []
    if same:
        notes.append(f"review(s) by the PR author {author} ignored: a same-account review cannot satisfy AC1")
    if blockers:
        return "UNMET", notes + [f"CHANGES_REQUESTED on {cand} by: {', '.join(sorted(blockers))}"]
    if not approvals:
        return "UNMET", notes + [f"no APPROVED review on exact candidate {cand} by an account other than the PR author {author}"]
    return "MET_AT_RUNTIME", notes + [f"APPROVED on {cand} by " + "; ".join(approvals)]


def api(path, token, base):
    req = urllib.request.Request(base.rstrip("/") + path, headers={
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": f"Bearer {token}"} if token else {})})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def fetch(ident, env):
    repo, token, base = env.get("GITHUB_REPOSITORY"), env.get("GITHUB_TOKEN"), env.get("GITHUB_API_URL", "https://api.github.com")
    cand = norm((ident or {}).get("candidate_sha"))
    out = {"schema": "bank-lab/pr-reviews/v1", "repository": repo, "candidate_sha": cand, "ok": False}
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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    ident = json.loads(Path(a.identity).read_text()) if Path(a.identity).exists() else {}
    rv = fetch(ident, os.environ)
    Path(a.out).write_text(json.dumps(rv, indent=2) + "\n")
    st, why = ac1_from_reviews(rv, ident)
    print(f"AC1 (reviews API, PR #{rv.get('pr')}, author {rv.get('pr_author')}): {st}")
    for w in why:
        print("  " + w)
    return 0  # informational; merge_eligibility.py decides


if __name__ == "__main__":
    sys.exit(main())
