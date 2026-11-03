# Executed checks, independent review and owner approval are separate things

Recorded 2026-11-03 (EST) for `acceptance/t16-pin-review`. No agent output in this repository may be read as either
of the last two.

| | executed checks (CI) | independent review | owner approval |
|---|---|---|---|
| what | GitHub Actions jobs run on an exact SHA (`acceptance.yml`, `integration-gate.yml`, `offline-validation.yml`, `portfolio-validation.yml`, `documentation.yml`) | an APPROVED GitHub review, on the exact commit, by an allow-listed human with write access who is not the PR author | the owner's decision to install a pin or ruleset, merge, or accept the portfolio |
| who | GitHub Actions | a human other than the shared agent account (`onnxscibroccoli`) | the owner |
| done by us? | yes, we trigger and report them | **no**; we write no review records | **no**; we claim none |
| best possible output | `EXECUTION_PASS` + `REVIEW_PENDING` (`decide.py` has no ACCEPTED state); `merge-eligibility` `TRUSTED GATE VERIFIED` only with a qualifying review | `independent_review {pr, review_id}` in the trusted manifest, fetched and checked at runtime | an installed manifest and an active ruleset |
| current state | acceptance jobs green on main `8e2df97b`; `merge-eligibility` **red** (T-16) | **none**: `independent_review` null, `reviewer_allowlist` empty, no second collaborator | **none**: proposed manifest not installed; rulesets prepared, not created (evaluate mode refused by plan) |

## Why the gate cannot approve itself

- `decide.py` exits at `REVIEW_PENDING` (5) at best. A review whose reviewer looks like the recorder or integrator is
  rejected, and blanket (unscoped) reviews are rejected. `REVIEW_CONCURRED_UNAUTHENTICATED` (7) is never acceptance.
- `merge_eligibility.py` ignores `--gate-trust` files and recomputes pin trust from the GitHub API. A self-pin, an
  approval by the PR author (every PR here is authored by the shared account), a reviewer not on the allowlist, and a
  reviewer without write permission all fail it (`tools/acceptance/gate/tests/test_pin_review.py`).
- The proposed T-16 manifest has `independent_review: null` and is not in a trusted location.
- The prepared rulesets have no bypass actors and name no agent or bot (`tools/acceptance/gate/tests/test_rulesets.py`).
