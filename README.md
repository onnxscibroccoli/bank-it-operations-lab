# evidence/acceptance

An orphan branch holding acceptance **run evidence and review requests about exact candidate SHAs** of PR #7. It is kept
outside the candidate tree, so writing it never changes the SHA it describes (the AC3 self-reference loop, pt15u).

- `candidates/<40-hex candidate sha>/runs/<run_id>/` holds the `acceptance-decision-<tested_sha>` artifacts, copied unmodified from GitHub Actions.
- `candidates/<sha>/SUMMARY.md` is the AC decision per run plus per-job results for every run on that candidate.
- `coordination/review-requests/` holds the review packets for those exact SHAs (prepared, not sent unless stated).

Append-only by convention: entries for earlier candidates are never edited or removed. Normal pushes only.
