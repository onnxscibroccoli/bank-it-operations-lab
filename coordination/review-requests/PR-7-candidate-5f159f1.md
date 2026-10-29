# Review request: PR #7 combined candidate `5f159f1c757d7fbf2964e4d8b615fcb9a810f7ca`

**Review exactly this SHA:** `5f159f1c757d7fbf2964e4d8b615fcb9a810f7ca` on branch `overnight/integration` (PR [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7), draft, into `main`).
Browse: https://github.com/onnxscibroccoli/bank-it-operations-lab/tree/5f159f1c757d7fbf2964e4d8b615fcb9a810f7ca

> **Earlier reviews and approvals do not transfer to this SHA.** That includes any review, verdict or check result for `eb42b23` (PR #26 head, tagged `checkpoint/eb42b23`), `82ab7e6` and `02ac2de` (earlier frozen candidates), `1a3cea0`, `4f54a01` or any earlier PR #7 head. It also includes PR #14's review notes, PR #27's findings on PR #26, and every per-PR review of #2, #3, #4, #5, #20 or #22 (PR #20 and PR #22 have none). A verdict on this request applies only to `5f159f1…`. Commits on `overnight/integration` after `5f159f1` change only `coordination/tasks.json`, `reports/INTEGRATION.md` and `coordination/review-requests/`, and they are not covered by this review. If any code changes, a new candidate and a new request are required.

Nothing here is secret. The lab is offline and synthetic: no cloud or tenant calls, no credentials, nothing deployed.

## What the candidate contains

`main` (`7f50348`) plus these merges, in dependency order:
- PR #3: shared evidence validator
- PR #5: AWS CDK private VPC + RDS with cdk-nag (it supersedes PR #1)
- PR #4: offline Entra Conditional Access validator
- PR #2: PostgreSQL restore harness v2 @ `e7399fb`
- **PR #20: M365 offline scenarios, merged at the exact SHA `1b3c240374285d7b0760b946e861dee15197dcf3`**
- **PR #22: SIMULATION incident demo, merged at the exact SHA `9f21329f0e796362c4498d49687fd0f99ce3a042`**

On top of the merges is the integration gate (`.github/workflows/integration-gate.yml`). Its **required** jobs (`coordination/modules.json` → `required_gate_jobs`) are:
- user-actions, module-registry
- offline-validation, aws-cdk, postgres
- m365-scenario-evaluation, m365-unit-tests, m365-evidence-verification, plan-only-assertions
- incident-committed-runs, incident-fresh-run, incident-not-executed-negative
- labeling-markers

`incident-fresh-run` must output `PASS` for each of injection, detection, diagnosis, recovery, timeline and simulation (`required_gate_outputs`). final-summary (`if: always()`) and merge-eligibility fail when any required job is missing, skipped, cancelled or failed, or when any required output is not PASS. That includes NOT_EXECUTED.

The scripts are in `scripts/ci/`, with tests in `scripts/ci/tests/` (39 tests). Every `actions/*` use is pinned to a full commit SHA.

Not included: PR #6 (excluded: B6-1, B6-2), and PRs #8–#19, #21 and #23–#27.

## Known state at this SHA (verify; don't take it on trust)

| Item | Claimed state |
|---|---|
| `validate-all.sh` (full, PostgreSQL 16.15) | PASS, 43 steps, on the candidate and on the main-validation merge |
| M365 | 13 scenarios match their expected verdicts and finding codes. 43 PLAN_ONLY plan steps (planned actions, not assertions), all `executed: false`, `mutationsExecuted` 0. 29 unit tests |
| Incident | The committed run `local-20261028T181818Z` (original, untouched) and the new run `local-20261029T000545Z` both meet all six requirements. A fresh run happens in CI |
| NOT_EXECUTED | Missing PostgreSQL binaries give NOT_EXECUTED for all six requirements and the check fails, never PASS |
| Merge eligibility | NOT ELIGIBLE: AC1 UNMET (this review), AC2 PARTIAL, AC4 PARTIAL, AC5 UNMET. AC3 depends on CI for this SHA. AC6 is a separate human gate |
| Current-main validation | `candidate/main-validation-5f159f1` @ `ba4d5e02146b33b74957a60b62a055f4c46ad089`: clean `--no-ff` merge onto `main` `7f50348`, tree identical to the candidate. See `coordination/tasks.json` → `accelerated_plan.round3` for the Actions results |

## Questions for the reviewer

1. Do the required checks really fail closed? Look for any path where an M365 or incident check, final-summary or merge-eligibility could succeed even though a module is missing, a job is skipped or cancelled, a job is absent from `needs`, or a requirement is NOT_EXECUTED. Relevant files: `scripts/ci/m365_checks.sh`, `incident_checks.sh`, `check_incident_run.py`, `check_labels.py`, `final_summary.py`, `merge_eligibility.py`, `check_modules.py`, `integration-gate.yml`.
1a. Do the six incident requirements actually prove injection, detection, diagnosis, recovery, timeline integrity and SIMULATION labelling? Could a forged or partial run pass?
2. Is the PLAN_ONLY assertion (`check_plan_only.py`) sound? Could a record with an executed step, a non-zero or non-integer `mutationsExecuted`, or no plan steps pass? Do the 14 negative tests cover the rules?
3. Is the user-actions report correct and safe? Are values escaped before they reach workflow commands and Markdown? Is anything interpolated into a shell?
4. Are all third-party actions pinned to full SHAs? Is anything unpinned besides the same-repo reusable workflows?
5. Do the integrated modules (shared validator, Entra, AWS CDK, Postgres v2) still pass their own checks at this SHA?
6. Were the PR #20 and PR #22 merges really of the exact SHAs `1b3c240` and `9f21329`, and does the earlier evidence remain byte-identical?
7. Is any technical blocker relaxed or hidden? These must stay open: B5-1, B5-2, AC1–AC6 and UA-1..UA-4.

## Verdict format

Reply with:
- `APPROVE` / `REQUEST CHANGES` / `COMMENT`
- the exact SHA `5f159f1c757d7fbf2964e4d8b615fcb9a810f7ca`
- the reviewer's identity and the date
- numbered findings, each with file and line

A verdict that doesn't name this SHA, or that names another SHA, does not count for AC1.

## Review disposition

**NOT YET REQUESTED.** This packet is prepared but has not been sent to any reviewer. No independent review exists for `5f159f1c757d7fbf2964e4d8b615fcb9a810f7ca`, so AC1 is UNMET.
