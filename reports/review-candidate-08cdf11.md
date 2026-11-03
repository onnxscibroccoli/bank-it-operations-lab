# Independent review: frozen candidate `08cdf11` (PR #7, `overnight/integration`)

- **SHA reviewed:** `08cdf11aecfdae56867f21cbec33e7505c8ce8a9`. It is the head of `overnight/integration` and PR #7 (draft, into `main`). VERIFIED via `gh pr list` and `git rev-parse origin/overnight/integration`.
- **Parent:** `7fe6d72`. VERIFIED
  - `git diff 7fe6d72 08cdf11` touches only `coordination/` and `reports/`: `tasks.json`, `review-requests/PR-7-candidate-7fe6d72.md`, `review-requests/README.md` and `INTEGRATION.md`.
  - No code, workflow or evidence changed between the two.
- **Reviewer:** an independent lane. I did not implement any of this. This is a findings note, **not an approval**. I have not approved, merged or commented on any PR.
- **Date:** 2026-10-28 (EDT).

Labels: **VERIFIED** means I checked it in this session via `gh`, `git`, a code read or a local run. **UNVERIFIED** means I did not reproduce it.

## 1. Integration-gate runs

| Run | Event | Tested SHA | Execution jobs | merge-eligibility | Run conclusion |
|---|---|---|---|---|---|
| 40794054069 | push | `08cdf11…` (checkout log: `git log -1` = `08cdf11aecfd…`) | 18/18 success | **failure** (job 123186512074) | failure |
| 40794058923 | pull_request | synthetic merge `771045ee413f7550cd0279db06915dddba548dfd` (`refs/pull/7/merge`) | 18/18 success | **failure** (job 123186552219) | failure |

- All of the table is VERIFIED via `gh run view --json jobs` and the job logs.
- `NEEDS_JSON` in the push log shows every required job `success`. `incident-fresh-run` outputs injection, detection, diagnosis, recovery, timeline and simulation are all `PASS`. VERIFIED
- Both logs print `merge-eligibility for <sha>: NOT ELIGIBLE` and the notices `AC1: UNMET`, `AC2: PARTIAL`, `AC3: MET for 7fe6d7281316190d9b39e35a448fb9fb81b92d50, not this SHA`, `AC4: PARTIAL`, `AC5: UNMET`, then exit code 1. VERIFIED
- So the only reasons for the failure are the AC statuses; no required-check problem was listed. VERIFIED
- I did not fetch `771045e` locally, so its tree is UNVERIFIED.

### Local re-run at 08cdf11

| Run | Result | Status |
|---|---|---|
| `python3 -m unittest discover -s scripts/ci/tests` | 43 tests OK | VERIFIED |
| `scripts/ci/merge_eligibility.py --sha 08cdf11…` with the same all-success `NEEDS_JSON` | `NOT ELIGIBLE`, the same 5 notices, rc 1. This matches CI. | VERIFIED |

## 2. Where AC1–AC5 are defined

- **Definitions:** `coordination/tasks.json` → `acceptance_conditions_for_main.conditions[]`. Each entry has an `id`, `condition`, `status` and `detail`; AC3 also has `met_for_sha`. VERIFIED
- **Gate:** `scripts/ci/merge_eligibility.py` (job `merge-eligibility` in `.github/workflows/integration-gate.yml:229`). For each AC it requires `status == "MET"`. If `met_for_sha` is present, it must prefix-match the tested SHA. It also requires every job in `coordination/modules.json` `required_gate_jobs` plus `final-summary` to be `success`. AC6 (Ian's human acceptance) is reported, not gated. VERIFIED

## 3. AC1: UNMET (precise finding at 08cdf11)

- **Condition** (`tasks.json` AC1): an independent review approves the **exact** candidate SHA, with reviewer evidence bound to that SHA through a GitHub review or commit provenance. Self-review by the author or the integration agent does not count.
- **What is unmet** (VERIFIED):
  1. PR #7 has **0 GitHub reviews**: `gh pr view 7` → `reviews: 0`, `reviewDecision: ""`, `isDraft: true`.
  2. `tasks.json` AC1 `detail_round4` says: "Final review packet for 7fe6d72 prepared; NOT YET REQUESTED; no verdict exists". `review_requests[3]` (`PR-7-candidate-7fe6d72.md`) has `status: NOT_YET_REQUESTED`, `verdict: null`.
  3. That packet names **7fe6d72**, not 08cdf11. 08cdf11's tree differs from 7fe6d72 only in coordination/reports files, but under AC1's own wording a 7fe6d72 approval would not be an approval of 08cdf11.
  4. The only independent notes that exist do not cover this SHA:
     - PR #14 @ `eb8d259` covers PR #2's harness, and it REQUESTS CHANGES on PR #5.
     - PR #27 covers PR #26 @ `181bcdd`.
     - My PR #26 review @ `eb42b23` is unpushed and does not cover this SHA either.
- **What would satisfy it:**
  - An independent reviewer approves `08cdf11aecfd…`, or whichever SHA is finally frozen, through a GitHub PR review on PR #7 with `commit_id` equal to that SHA, from an account other than the author.
  - Caveat: every agent here pushes as `onnxscibroccoli`. GitHub does not allow approving your own PR, so a genuine approval requires a second account.
  - Afterwards `tasks.json` AC1 must be set to MET with `met_for_sha`. Note the gate does not check GitHub itself (see R1′ in section 9).
  - This note does **not** satisfy AC1. It records findings, its verdict is "not approved", and it comes from the same GitHub account.

## 4. AC5: UNMET (precise finding at 08cdf11)

- **Condition:** no unresolved blocking findings in integrated code.
- **Open blocking findings, re-checked in the code at this SHA:**
  - **B5-1: suppressions are applied before approval.** VERIFIED
    - `infra/aws-cdk/lib/secure-storage-stack.ts:56` (AccessLogsBucket) and `:68` (DataBucket) call `NagSuppressions.addResourceSuppressions`.
    - So do `infra/aws-cdk/lib/network-database-stack.ts:228` and `:242` (RdsMonitoringPolicy).
    - Meanwhile `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md:3` says: "Status of every entry: **PROPOSED, pending owner approval.**" (EX-01..EX-04).
    - *Satisfied by:* an owner approval of EX-01..EX-04, recorded with approver, date and SHA, and the register flipped to APPROVED. Alternatively, remove the suppressions so cdk-nag fails visibly until approval. The same action closes most of AC2.
  - **B5-2: KMS key-admin escalation.** VERIFIED
    - In `infra/aws-cdk/lib/least-privilege-key.ts:7-20`, `KEY_ADMIN_ACTIONS` includes `kms:Create*` (line 8) and `kms:Put*` (line 12).
    - Statement `KeyAdministrationByAccountRoot` (line ~52) grants them to `AccountRootPrincipal` with **no conditions**.
    - `kms:Create*` covers `kms:CreateGrant`, which bypasses the conditioned grant statement at line 72 (`kms:GrantIsForAWSResource`, `kms:ViaService`). `kms:Put*` covers `kms:PutKeyPolicy`.
    - Any account principal with matching IAM permissions can therefore grant itself Decrypt or rewrite the key policy. The comment "no cryptographic use" (line 42) does not hold.
    - *Satisfied by:* listing explicit admin actions and dropping `Create*`/`Put*`. Keep `kms:CreateAlias` if needed, keep `kms:CreateGrant` only in the conditioned statement, and restrict `kms:PutKeyPolicy` to a named key-admin role. Add a guard in `infra/aws-cdk/lib/guards.ts` that fails on unconditioned `CreateGrant`/`PutKeyPolicy`/`Create*`/`Put*`, with a test.
  - **Scope:** PR #6 (B6-1/B6-2) is excluded from this candidate; `infra/` contains only `aws-cdk`. VERIFIED. So B6 findings do not block AC5 here.
  - **Status record:** `tasks.json` AC5 `detail` lists B5-1 and B5-2 as open. VERIFIED. This is consistent with the code.
- **Missing in the record** (UNVERIFIED as blocking): PR #14 also raised B5-3, a conflict with PR #1. PR #5 supersedes PR #1 in this candidate. AC5 `detail` does not mention B5-3 explicitly; it should record a disposition.

## 5. AC3: why it is "MET for 7fe6d72, not this SHA"

- `tasks.json` AC3 has `status: MET` and `met_for_sha: 7fe6d7281316190d9b39e35a448fb9fb81b92d50`, based on runs 40793219129, 40793225624 and main-validation 770cf33 (run 40793236453). `merge_eligibility.py:31-33` rejects it because the tested SHA does not start with that value. VERIFIED
- The root cause is structural. 08cdf11 is the commit that *records* 7fe6d72's results in `tasks.json`. Any commit that records AC3 for itself creates a new SHA, so a file-recorded AC3 can never match the commit that contains it. VERIFIED (by construction plus the diff in the header)
- In substance, 08cdf11's own runs above passed every required job. So the technical checks *did* pass at 08cdf11; only the self-referential record fails.
  - VERIFIED for the CI jobs.
  - `scripts/validate-all.sh` was not re-run by me at 08cdf11: UNVERIFIED (the record claims 43 steps PASS for 7fe6d72).
- Stale field: AC3 also carries `met_at_sha: afb41278…`, which is the previous branch head. It disagrees with `met_for_sha`. VERIFIED
- *Fix:* have merge-eligibility derive AC3 from this run's `NEEDS_JSON` plus a `validate-all` job instead of from `tasks.json`.

## 6. AC2 and AC4: what is missing

- **AC2 (PARTIAL):** EX-01..EX-04 are recorded but **none is owner-approved**. The register status is PROPOSED (`SECURITY_EXCEPTIONS.md:3`), and the suppressions are already active (B5-1). It needs owner approval per exception: approver, date, scope and the SHA it applies to. VERIFIED
- **AC4 (PARTIAL), per `tasks.json` AC4 detail:**
  - PR #1 is still open and describes the superseded S3 self-logging design.
  - PR #4's baseline policy choices are unconfirmed by the owner.
  - PR #6 is excluded.
  - Also VERIFIED: `tasks.json` `accelerated_plan.gates.merge_eligibility` still cites AC3 "MET for 82ab7e6" and older runs, so the docs/state disagree inside the same file.
  - PR #1 still being open: VERIFIED (`gh pr list`: #1 `bank-aws-001` open).
  - I did not re-read PR bodies: UNVERIFIED.

## 7. SIMULATION / PLAN_ONLY constraints

- **Workflows:** all four workflows declare `permissions: contents: read`. No `secrets.*` and no `id-token` are referenced. Checkout uses `persist-credentials: false`. VERIFIED
- **No live mutation paths found.** VERIFIED (grep, a code-level search rather than proof):
  - I searched for `cdk deploy`, `terraform apply`, mutating `aws <svc> create/put/delete/update/...`, `boto3.client`, `requests.post/patch/put/delete`, `graph.microsoft.com`, `Invoke-RestMethod` and `New-/Update-/Remove-/Set-Mg*`, excluding `node_modules`.
  - The only hit is `tests/entra/test_ca_validator.py:304`. It is a test that *asserts the absence* of network modules.
- **Incident demo is local and disposable** (`scenarios/incident/run_incident_demo.sh`). VERIFIED (read)
  - Its "crash" is `pg_ctl stop -m immediate` on a throwaway cluster in `PGDATA="$WORK/pgdata"`, with `WORK=$(mktemp -d /tmp/incident-sim.XXXXXX)`, cleaned up on exit.
  - Without binaries it writes NOT_EXECUTED with exit 3 rather than fabricating results.
  - Every event is tagged `"simulation":"SIMULATION"`.
- **PLAN_ONLY checks:** `scripts/ci/check_plan_only.py` fails closed. Every plan step must have `mode == "PLAN_ONLY"` and `executed == false`, with `mutationsExecuted=0`.
  - Locally, the negative test rejects `mode: 'EXECUTE'`. VERIFIED
  - The CI job `plan-only-assertions` succeeded in both runs. VERIFIED

## 8. Re-check of R1–R7 (from my `eb42b23` review of PR #26) at 08cdf11

PR #26's `scripts/acceptance/` and `acceptance.yml` are **not integrated** at this SHA: `ls scripts/acceptance` fails, and the only workflows are aws-cdk, integration-gate, offline-validation and postgres-restore-evidence. VERIFIED. The merge gate here is `merge_eligibility.py`. So each R item is re-judged as "does the same weakness exist in this candidate's gate?"

| ID | At eb42b23 | At 08cdf11 | Status |
|---|---|---|---|
| R1: fabricated bundle plus a string review gives ACCEPTED | open | **The code is absent, but the same weakness remains in another form (R1′):** AC statuses are free-text, self-reported fields in `coordination/tasks.json`. Probe: a copy of `tasks.json` with AC1–AC5 set to `MET` and `met_for_sha` removed, plus the real all-success `NEEDS_JSON`, makes `merge_eligibility.py --sha 08cdf11… --tasks <copy>` print **`ELIGIBLE`, rc 0**. The gate never queries GitHub for an approving review (AC1), an owner approval (AC2) or finding status (AC5). | **REMAINS** (VERIFIED) |
| R2: inventory binding fails open | open | Not applicable here (no inventory). The same pattern exists, though: `met_for_sha` is checked **only if present** (`merge_eligibility.py:31`), so a MET without a SHA passes. Matching is also by prefix, so a short value like `"0"` would match any SHA starting with 0. | **REMAINS, in analogous form** (VERIFIED by code read and the probe above) |
| R3: self-review only blocked by exact string | open | Not applicable: there is no reviewer field at all, and AC1 is a status string. Covered by R1′. | REMAINS via R1′ (VERIFIED) |
| R4: `execution_state` self-reported | open | Not applicable. Required-job results come from the Actions `needs` context (`NEEDS_JSON`), which is platform-provided, not self-reported. Missing `NEEDS_JSON` → NOT ELIGIBLE (probe rc 1). | **CLOSED here** (VERIFIED) |
| R5: no executable merge gate (main unprotected) | open | `main`: `protected: false`, 0 rulesets (`gh api`). PR #7 is `MERGEABLE` even though `merge-eligibility` failed. The red job is advisory only. | **REMAINS** (VERIFIED) |
| R6: CI trusts the candidate's own gate code | open | `merge-eligibility` sparse-checks-out the **candidate's** `coordination/` and `scripts/ci/`. The PR under test supplies both the gate and the AC statuses it grades. | **REMAINS** (VERIFIED, read) |
| R7: `postgres-run/` outside top-level hashes | open | Not applicable (the PR #26 bundle format is not present). | N/A (VERIFIED absent) |
| C5 hygiene | open | All `actions/*` are pinned to 40-hex SHAs in all 4 workflows (30 pins, 0 unpinned). integration-gate and aws-cdk retention is 7 days; postgres-restore-evidence is still **90 days**. The PR run tests the synthetic merge (main+candidate). | Mostly closed; retention on one workflow remains (VERIFIED) |

## 9. Summary

- **Reviewed:** `08cdf11aecfdae56867f21cbec33e7505c8ce8a9`.
- **Execution:** every required job is green on both push and PR runs. merge-eligibility is NOT ELIGIBLE by design.
- **AC1 UNMET:** there is no GitHub review on PR #7, the 7fe6d72 packet has not been requested, and no exact-SHA approval exists.
- **AC5 UNMET:** B5-1 (4 suppressions active while the register is PROPOSED) and B5-2 (unconditioned `kms:Create*`/`kms:Put*` to account root in `least-privilege-key.ts`).
- **AC3:** the passing results are recorded for the parent 7fe6d72, so the record cannot match any commit that contains it.
- **AC2 and AC4 PARTIAL:** owner approvals and the PR #1/#4 doc dispositions are missing.
- **SIMULATION/PLAN_ONLY:** holds.
- **R1′/R2′/R5/R6 remain:** the gate trusts self-edited `tasks.json` and candidate-supplied gate code, and main is unprotected.
- **Not an approval.**
