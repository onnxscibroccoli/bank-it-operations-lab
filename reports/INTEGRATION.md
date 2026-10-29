# Overnight integration: `overnight/integration`

> **Deadline:** 2026-10-29T00:00:00-04:00 (midnight America/New_York). At commit time (2026-10-28 17:48 EDT), **6h11m** remained.
> **Branch name:** `overnight/integration` is a historical name only. Keep using it and do not rename it.

- Base: `main` @ `7f50348` (contains only `README.md`; verified it was not broken). This agent has merged nothing into `main`, closed no PR, deployed nothing, and made no AWS, Entra or Graph calls.
- Machine-readable status: [`coordination/tasks.json`](../coordination/tasks.json).
- Full validation: `scripts/validate-all.sh` (Node 20, npm, and PostgreSQL binaries via `PG_BIN` or PATH). For the Python-only subset, run `scripts/validate-all.sh --python-only`.

## Round 9 (2026-10-28 ~22:30 EDT): repairs for PR #32 (CHANGES REQUIRED on `5a75d9c`)

| Finding | Fix |
|---|---|
| **D1**: AC4/AC5 accepted from the PR author; `workflow_run` checked only by head SHA | No attestation from the PR author counts, for any criterion: AC4, AC5, EXCEPTION or CONDITIONS_VERIFIED. An unknown PR author fails closed. `workflow_run` must be an `integration-gate` run (name and `.github/workflows/integration-gate.yml` path), completed, with head SHA = the candidate or an attested tested merge. Every job must have succeeded except the fail-closed `merge-eligibility` job, which by design fails while NOT ELIGIBLE, so a run's conclusion cannot be `success` before acceptance. `final-summary` must be green. |
| **D2**: "owner-authenticated" was only a login check on the shared account | Relabelled **owner-login-bound, not owner-authenticated** in code, docs and `tasks.json`. Exception decisions from the PR author / shared account are `INSUFFICIENT_INDEPENDENCE` (blocking). The trusted config's only owner login is `onnxscibroccoli`, who is also the PR author, so AC2 stays blocked until Ian has a separate identity: **O-5, recorded as UA-6** |
| **D3**: the manifest self-pinned the candidate on an unprotected branch | `verify_trusted_gate.py --check-pin` makes the gate TRUSTED only when two things hold. First, `gate_sha` is not the candidate. Second, the manifest's `independent_review` names a GitHub review, fetched at runtime, that is APPROVED on `gate_sha` by a non-author, allow-listed, write+ account. Otherwise the result is **TRUSTED GATE UNVERIFIED** and merge-eligibility is NOT ELIGIBLE. The manifest now pins the gate commit (not the candidate) with `independent_review: null`, so this candidate is UNVERIFIED by construction. UA-3 now also protects `evidence/acceptance` |
| Nits | The Round 8 time is corrected to 21:56 EDT, and the `5a75d9c` re-pin row is added to `trusted-gate/README.md` |

## Round 8 (2026-10-28 21:56 EDT): Ian's 21:50 execution alignment (P1-P5)

- `e9310f3` was frozen before the 21:50 alignment. **It is not the review candidate**: its decision comments did not bind main, tested merge, workflow run or exception scope, and it had no exception states.
- **P1 (AC1):** design unchanged (non-author; write+ via `GET /collaborators/{login}/permission`; trusted `reviewer_allowlist` outside the candidate; APPROVED with `commit_id` = exact 40-hex SHA; latest decisive review per account; any undismissed CHANGES_REQUESTED fails closed). New regressions: superseded by a later CHANGES_REQUESTED, dismissed, wrong / 12-char / 39-char SHA, author on the allow-list.
- **P2 (AC2/AC4/AC5):** only `ACCEPTANCE-ATTESTATION v2` comments on PR #7 count. Each binds candidate, main, tested merge(s), criterion, decision, evidence refs and `workflow_run`; the run is checked through the API (`run.head_sha == candidate`, new `actions: read`). Decision-maker and timestamp come from GitHub. Strict parse; edited comments are ignored. The decision artifact has separate `candidate_produced` and `independent_acceptance` sections. Regressions: forged in-tree MET (tasks.json and register text) leaves NOT ELIGIBLE; valid external attestations give ELIGIBLE with the tree unchanged.
- **P3 (exceptions):** PROPOSED / APPROVED / REJECTED / APPROVED_WITH_CONDITIONS / SUPERSEDED (+ CONDITIONS_VERIFIED). Only the owner (admin) decides; scope must equal the applied rule + resources; a conditional approval is effective only after a later CONDITIONS_VERIFIED. Nothing is approved.
- **Exception reconciliation** (no approver is recorded anywhere; none is invented):

| ID | Register | Suppression in code | Scope the gate requires | State |
|---|---|---|---|---|
| EX-01 | PROPOSED | `infra/aws-cdk/lib/secure-storage-stack.ts:60` | `NIST.800.53.R5-S3DefaultEncryptionKMS AccessLogsBucket83982689` | PROPOSED (reconciled) |
| EX-02 | PROPOSED | `secure-storage-stack.ts:65,72` | `NIST.800.53.R5-S3BucketReplicationEnabled AccessLogsBucket83982689 DataBucketE3889A50` | PROPOSED (reconciled) |
| EX-03 | PROPOSED | `network-database-stack.ts:241-246` | `AwsSolutions-IAM5 RdsMonitoringPolicy5DA8ACAC` | PROPOSED (reconciled) |
| EX-04 | PROPOSED | `network-database-stack.ts:226-234` | `AwsSolutions-IAM4 BackupPlanPostgresRole2A2CEBDF` | **UNRESOLVED** (left open) |

- **P4 (R6):** no `pull_request_target` is used. The gate stays manifest-pinned and hash-verified. Full closure is UA-3, an owner action. Residual until then: on `pull_request` the job definition comes from the candidate's workflow file.
- **P5:** B6-3 is in `orgs-security.blocker.ids`; the DatabaseKey CreateGrant wording is fixed; README says 7/25; historical checksums are kept (`superseded/pass3-pre-B5-2/`).

## Round 7 (2026-10-28 ~22:00 EDT): repairs for PR #31 (CHANGES REQUIRED on `1fdf25a`)

- **Reconciled at start (no drift):**
  - `origin/overnight/integration` = `1fdf25ad10c56bb457d6242392f9305c539d1209`
  - `origin/main` = `7f50348bf1370381615eaed91c02607fe41de2f5`
  - `refs/pull/7/merge` = `07eea1cefdc15873af2a579d3795af402961edd6`
  - gate run 40800364073 = 18/19, with only merge-eligibility failing
- **PR #31** (`eccac83`) is a same-account findings note. It is not an AC1 approval; same-account reviews never count.
- **KMS wildcards removed since `b908a66`:**
  - At `b908a66`, `infra/aws-cdk/lib/least-privilege-key.ts:8` was `'kms:Create*'`, `:12` was `'kms:Put*'`, and `:52` was `sid: 'KeyAdministrationByAccountRoot'` (unconditioned).
  - Now the admin list is explicit (`:17` `'kms:CreateAlias'`, `:24` `'kms:PutKeyPolicy'`), `:73` is `sid: 'KeyAdministrationByKeyAdminRoleOnly'`, `:78` is `ArnEquals aws:PrincipalArn` and `:84` is `BoolIfExists kms:BypassPolicyLockoutSafetyCheck=false`.
  - Committed synth templates: `"kms:Create*"` 2 → 0 (NetworkDatabase) and 1 → 0 (SecureStorage); `"kms:Put*"` → 0.

| Finding | Fix |
|---|---|
| **F4**: any GitHub account's approval counted | AC1 approver must be on the trusted `reviewer_allowlist` and have write/maintain/admin permission (`/collaborators/{login}/permission`), and must not be the author. Negative test: a random account approving gives UNMET |
| **F5**: CHANGES_REQUESTED on an earlier commit ignored | An undismissed CHANGES_REQUESTED by a non-author on any commit blocks AC1 |
| **F6**: AC2/AC4/AC5 only satisfiable in-tree | All of AC1–AC5 are `COMPUTED_AT_RUNTIME`. AC2/AC4/AC5 come from `ACCEPTANCE-DECISION v1` comments on PR #7. Each is bound to the exact candidate SHA, unedited, and from an authorized account with runtime permission. In-tree MET is rejected (gate and `--lint-tasks`). ELIGIBLE is reachable in principle (test `test_owner_decision_on_exact_sha_meets_ac2_ac4_ac5_and_eligible_is_reachable`) |
| **F7**: UA-1 approval was a text edit | AC2 needs an owner decision comment by a trusted `owner_logins` account with admin permission, naming **exactly** the applied EX ids. The register's "APPROVED" text never approves (test `test_register_text_approved_does_not_approve`). Residual: the owner login is also the PR author and the agents' push account, so the comment proves the account, not the person; Ian should post it himself |
| **R6**: candidate controls the verifier | The gate manifest (`evidence/acceptance:trusted-gate/gate-manifest.json`, or `main` once it carries one) pins `gate_sha`. The gate code and trusted config are checked out **by SHA** and hash-verified. The candidate's `scripts/ci/**`, trusted config and `integration-gate.yml` must hash-match the manifest, or merge-eligibility runs no decision and fails. Trusted `required_gate_jobs` cannot be dropped by candidate data. **Only UA-3** closes the residual (the job definition sits in the candidate's workflow); the exact settings are in the UA-3 instructions |
| **M1** | `least-privilege-key.ts` comment now documents the CDK Secret's `CreateGrant` statement on DatabaseKey (conditioned only on `kms:ViaService=secretsmanager`). Synth unchanged |
| **Minor** | `orgs-security.blocker.ids` now `[B6-1, B6-2, B6-3]` with a Terraform unblock step. The README states coverage 7/25. The test count is corrected to 93 at `1fdf25a` |

**EX-01..EX-04 reconciliation** (from `check_exceptions.py` on this tree; none approved, and nothing here approves them):

| ID | Register status | Rule | Applied suppression(s) |
|---|---|---|---|
| EX-01 | PROPOSED | NIST.800.53.R5-S3DefaultEncryptionKMS | BankItLabSecureStorage:AccessLogsBucket83982689 |
| EX-02 | PROPOSED | NIST.800.53.R5-S3BucketReplicationEnabled | BankItLabSecureStorage:AccessLogsBucket83982689, BankItLabSecureStorage:DataBucketE3889A50 |
| EX-03 | PROPOSED | AwsSolutions-IAM5 | BankItLabNetworkDatabase:RdsMonitoringPolicy5DA8ACAC |
| EX-04 | PROPOSED | AwsSolutions-IAM4 | BankItLabNetworkDatabase:BackupPlanPostgresRole2A2CEBDF |

**Approval path (UA-1):** the owner posts one new comment on PR #7 with the body `ACCEPTANCE-DECISION v1` / `candidate: <exact 40-hex SHA>` / `UA-1: APPROVE EX-01 EX-02 EX-03 EX-04` (use `REJECT` to reject). The integrator never posts it.

## Round 6 (2026-10-28 ~21:25 EDT): repairs for PR #30 (CHANGES REQUIRED on `b908a66`)

PR #30 (`review/candidate-b908a66` @ `eb82d7d`) is an independent-lane findings note on `b908a669b302ff37f2c2ca79ed828f65e5a9f432`, pushed by the same GitHub account as PR #7's author. Its verdict is CHANGES REQUIRED. **It is not an AC1 approval: a same-account review can never satisfy AC1.** AC1 now comes only from the GitHub reviews API and needs a different account.

| Finding | Fix | Commit |
|---|---|---|
| **B5-2**: root `kms:Create*`/`kms:Put*` unconditioned (`least-privilege-key.ts:8/12`) | `KeyAdministrationByKeyAdminRoleOnly`:<br>• explicit admin actions, no wildcard, no `CreateGrant`<br>• `ArnEquals aws:PrincipalArn` = role `BankItLabKmsKeyAdmin` or the account root user (break-glass)<br>• `BoolIfExists kms:BypassPolicyLockoutSafetyCheck=false`<br>• `PutKeyPolicy` kept, so the key stays manageable<br><br>New guard `KMS_UNCONDITIONED_ADMIN`/`KMS_ADMIN_WILDCARD` with a negative control. Jest 36/36, cdk-nag 0 Non-Compliant. Evidence pass 4 is added; the pass-3 outputs are kept in `superseded/pass3-pre-B5-2/`, and SHA256SUMS is regenerated | `80f01d6` |
| **B5-1**: suppressions applied while the register says PROPOSED | `scripts/ci/check_exceptions.py` (validate-all + merge-eligibility):<br>• every applied suppression must name a registered EX-NN with the same rule, otherwise ERROR<br>• suppressions tied to non-APPROVED exceptions are a **BLOCKING USER ACTION (UA-1)**, and merge-eligibility keeps **AC2 and AC5 UNMET** whatever `tasks.json` says<br><br>Nothing is approved here; that is UA-1 | `4e6fef4` |
| **F1**: AC3 accepted a merge into any base | `provenance.py`:<br>• `base_sha` must equal the **current** `main` SHA read at runtime (`TRUSTED_MAIN_SHA`, from a checkout of `main` in the job)<br>• a moved PR base or a non-main base ref is INVALID<br><br>Regression: a local `--no-ff` merge into a non-main parent under the `candidate/main-validation-*` name is INVALID | `4e6fef4` |
| **F3/R6**: AC1 self-asserted; the candidate grades itself | • AC1 is `COMPUTED_AT_RUNTIME` from `GET /pulls/{n}/reviews` (`reviews.py`, read-only `GITHUB_TOKEN`, `pull-requests: read`): an APPROVED review with `commit_id` = the exact candidate, from a non-author<br>• AC1 MET in `tasks.json` is rejected<br>• merge-eligibility runs `scripts/ci` from `main` (if `main` has the gate) or from pinned `TRUSTED_GATE_SHA=4e6fef4…`, and reads the candidate's data via `--root` | `4e6fef4` + workflow |
| **N1**: PR #6's Terraform track (B6-3) was dropped | B6-3 restored in the `orgs-security` BLOCKED reason and in the README | records |
| **B5-3**: conflict with PR #1 | Resolved in code (PR #1 superseded by PR #5; `bank-aws-001` SUPERSEDED). PR #1 stays open pending UA-4 | records |

- **Residual R6:** on `pull_request` the workflow file comes from the candidate merge, so a candidate could edit the pin. Only branch protection, or a ruleset requiring this workflow from `main` (UA-3), closes that.
- **Residual F2:** CI runs `validate-all --python-only`. The full suite runs locally, and its Node/PostgreSQL parts run as separate CI jobs.
- **Residual R5:** `main` is unprotected (UA-3).
- **New tests:**
  - `scripts/ci/tests/test_provenance_base.py`: 6 tests
  - `scripts/ci/tests/test_ac_repairs_b908a66.py`: 15 tests
  - `scripts/ci/tests` had 93 tests in total at `1fdf25a` (corrected from 87; 72 + 6 + 15), run by validate-all and by the module-registry job

## Post-candidate coverage delta pt16u (2026-10-28 ~21:15 EDT): module coverage registry

- **The review candidate is unchanged:** `b908a669b302ff37f2c2ca79ed828f65e5a9f432`. It was not re-frozen or replaced, and the Bank IT Lab PR Reviewer is reviewing it. The commits below sit on top of it on `overnight/integration`; they are not part of what is under review, and no approval of `b908a66` covers them.
- **`51e404c`** applies Ian's `00-all.patch` unchanged:
  - `coordination/modules.json` now lists **26 modules**, with `coverage.denominator_floor = 26`.
  - Each module has a category (functional, documentation, review_record, superseded or blocked), an owner, a `delivery_location` and `required_checks {present, proposed}`.
  - `orgs-security` moves from EXCLUDED to **BLOCKED** (B6-1: the trail access-logs bucket logs to itself; B6-2: the exempt-role SCP bypass), and still counts in the denominator.
  - `bank-aws-001` (PR #1) becomes SUPERSEDED by `aws-cdk`.
  - Three NOT_STARTED modules come from the job-matrix top gaps: `aws-network-edge`, `endpoint-windows-automation` and `inventory-diagrams`.
  - `check_modules.py` gains fail-closed coverage checks, `user_actions.py` prints the coverage line and fails on invalid coverage, and there are 11 new tests in `scripts/ci/tests/test_module_coverage.py`.
- **Integrator review fixes (next commit):**
  1. `scripts/ci/tests` was never run by `validate-all.sh` or any Actions job. That includes the 18 binding regressions on `b908a66`, which so far had only run locally. A validate-all step `ci self-tests (scripts/ci/tests)` and a `module-registry` job step now run the suite.
  2. `--coverage-json` without a file crashed; it now exits 2.
  3. The module-registry job writes `--coverage-json`.

  No checks were removed.
- **Coverage:** `MODULE COVERAGE: 7/25 integrated (28.0%), functional 7/17; denominator 26 (BLOCKED=1, INTEGRATED=7, NOT_INTEGRATED=14, NOT_STARTED=3, SUPERSEDED=1)`.
- **Effect on AC1–AC5 for `b908a66`:** none. Actions results for this HEAD are recorded on `evidence/acceptance`, not here.

## Checkpoint pt15u (2026-10-28 ~21:00 EDT): AC3 provenance, binding fix, AC4 docs

- **What `771045e` is:** `771045ee413f7550cd0279db06915dddba548dfd` is GitHub's synthetic merge for PR #7 (`refs/pull/7/merge`), with parents `7f50348` (main) and `08cdf11` (head). Pull-request runs test that commit, so their `GITHUB_SHA` is `771045e` while the candidate is `08cdf11`.
- **AC3 provenance design: computed at runtime, with evidence kept outside the tree.**
  1. `scripts/ci/provenance.py` builds the run identity: `candidate_sha`, `base_sha`, `tested_sha`, `kind`, run id/attempt and event.
     - For a PR, it requires the tested commit's second parent to equal `pull_request.head.sha`, and records the first parent as the base.
     - For `candidate/main-validation-<sha>`, it requires a `--no-ff` merge whose second parent matches the branch suffix.
     - Any other push is `kind: direct` and **cannot** satisfy AC3, because it is not a test against main.
  2. `merge-eligibility` evaluates AC3 (`COMPUTED_AT_RUNTIME`) inside that same run. It holds only for a valid merge identity whose required jobs and outputs all succeeded in that run.
  3. The identity and decision are uploaded as run artifact `acceptance-decision-<tested_sha>` (90 days) and mirrored afterwards to the **`evidence/acceptance`** branch.
  4. Nothing is committed back into the candidate, which breaks the loop of results changing the SHA they describe. `tasks.json` never carries MET for AC3.
  5. This needs only the workflow's read-only `GITHUB_TOKEN` (`contents: read`).
  6. Rejected options: commit status or check-run, because they need write scopes; per-run tags, because they add clutter; vouching for a run from another run's API record.
- **`merge_eligibility.py` fix:** a MET condition must carry `met_for {candidate_sha, base_sha, tested_sha}`, plus evidence.
  - Each SHA must be full 40-hex (case-normalized) and equal to this run's identity.
  - Missing, legacy bare `met_for_sha`, abbreviated, non-hex or wrong SHAs, and candidate-vs-merge mixups are all **not eligible**.
  - `--lint-tasks` rejects any naked MET; it is the new validate-all step "tasks lint (no naked MET)".
  - The regression tests are in `scripts/ci/tests/test_merge_eligibility_binding.py`. No check was removed.
- **AC4 docs:**
  - The root `README.md` now covers the modules, the M365 and incident modules (including what 13 and 43 count), the gate behaviour, and PR #1 being superseded.
  - `evidence/entra/BASELINE-CHOICES-PENDING.md` lists the PR #4 baseline choices (it lives outside `identity/entra/` because those files are hash-pinned inputs of the committed Entra evidence run) as **pending owner confirmation (UA-2)**. No confirmation is claimed.
  - `infra/aws-cdk/README.md` carries the PR #1 superseded note.
  - AC4 stays **PARTIAL** for reasons outside the tree: PR #1 is still open (UA-4), the PR #4 choices are unconfirmed (UA-2), and the PR #7 description is out of date. I wasn't authorized to edit PR descriptions.
- **Records after freezing:** none are committed to `overnight/integration`. Results for the frozen candidate are on branch `evidence/acceptance`.

## Final candidate (2026-10-28 ~20:18 EDT, Ian 20:16 EDT final sprint)

- **M365:** stays at `1b3c240374285d7b0760b946e861dee15197dcf3`. At ~20:18 EDT that was still the head of `m365-endpoint` and PR #20, which has 0 reviews, so no newer reviewed head existed to refresh to.
- **Incident demo:** stays at exactly `9f21329f0e796362c4498d49687fd0f99ce3a042`.
- **Fresh incident run:** `incident-fresh-run` now **apt-installs the PostgreSQL server binaries on the runner**. It tries `postgresql-16` first and falls back to the distro `postgresql` package, then puts `initdb`/`pg_ctl` on `PATH`. **No services container is used.** `scripts/ci/tests/test_fresh_run_wiring.py` enforces this.
- **Exit code 3:** the harness exit 3 means NOT_EXECUTED. It fails the step and therefore the required job. The step has no `if:` and no `continue-on-error`.
- **`5f159f1`:** superseded. Its results above are history only.

- **FINAL frozen acceptance candidate `7fe6d7281316190d9b39e35a448fb9fb81b92d50`**, tested against current main `7f50348` on `candidate/main-validation-7fe6d72` @ `770cf3360aeb4cca8f339c412f4cc5c907b88e09`. The `--no-ff` merge was clean and the merged tree is identical to the candidate. Local `validate-all` PASSED 43/43 on both.

  In every gate run below, 18 of 19 jobs succeeded. **Every required job succeeded**, and `final-summary` succeeded. `merge-eligibility` **failed, by design** (AC1, AC2, AC4 and AC5 are open).

  | Run | Fresh incident run |
  |---|---|
  | [integration-gate, main-validation 40793236453](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793236453) | All six requirements PASS; MTTD 3.481 s, MTTR 8.671 s |
  | [integration-gate push 40793219129](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793219129) | MTTD 3.483 s, MTTR 8.675 s |
  | [integration-gate PR 40793225624](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225624) | MTTD 3.447 s, MTTR 8.499 s |

  The other workflows also succeeded:
  - [postgres-restore-evidence 40793225365](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225365): 5/5
  - [aws-cdk 40793225339](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225339)
  - [offline-validation PR 40793225341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225341)
  - [offline-validation push 40793219059](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793219059)
- **PostgreSQL actually used by the fresh CI run:** `postgresql-16` could not be installed on `ubuntu-latest`, so the fallback ran. The distro `postgresql` package via apt gave `/usr/lib/postgresql/18/bin` (PostgreSQL 18.6, from the image's PGDG packages), with `initdb` and `pg_ctl` on `PATH`. No services container was used.
- **NOT_EXECUTED items for this SHA:** none. The harness's exit-3 path appears only in the negative job, where it correctly fails.
- **Independent review of `7fe6d72`:** **not yet requested.** The packet is `coordination/review-requests/PR-7-candidate-7fe6d72.md`. Earlier approvals do not transfer, including `eb42b23`, `82ab7e6`, `02ac2de`, `5f159f1`, PR #14 and PR #27.

## Round 3 (2026-10-28 ~20:10 EDT, Ian 20:03 EDT): M365 and incident demo integrated at exact SHAs

- **Merged by exact commit, not branch tip:**
  - PR #20 (M365) `1b3c240374285d7b0760b946e861dee15197dcf3`, merge `c6c1061`
  - PR #22 (incident demo, SIMULATION) `9f21329f0e796362c4498d49687fd0f99ce3a042`, merge `0964281`

  Both commits exist, descend from main `7f50348`, and add only `identity/m365`, `evidence/m365`, `scenarios/incident` and `evidence/incident`, so there were no conflicts. Both PRs are drafts with **0 reviews**. Integrating them on Ian's instruction does not approve either one.
- **Required gate jobs.** All are in `required_gate_jobs` and in the `needs` of `final-summary` and `merge-eligibility`:

  | Area | Jobs |
  |---|---|
  | M365 | `m365-scenario-evaluation`, `m365-unit-tests`, `m365-evidence-verification`, `plan-only-assertions` |
  | Incident | `incident-committed-runs`, `incident-fresh-run`, `incident-not-executed-negative` |
  | Labeling | `labeling-markers` (a separate job) |

  `incident-fresh-run` publishes six outputs: injection, detection, diagnosis, recovery, timeline and simulation. Each must be exactly `PASS`. A job that is missing, skipped, cancelled or failed, or an output that is `NOT_EXECUTED`, `FAIL` or missing, fails both `final-summary` and `merge-eligibility`.
- **Fresh incident run in Actions:**
  - It uses PostgreSQL server binaries from the runner image, installing them with apt only if they are absent.
  - It needs a full-history checkout, because the scenario extracts pinned component commits.
  - Output goes to the runner's temp dir and is uploaded as artifact `incident-fresh-run-<sha>` (7 days). It is never written over committed runs.
  - **If the binaries are missing, every requirement is NOT_EXECUTED and the job fails. That never counts as PASS.** This is proven by `incident-not-executed-negative` and `scripts/ci/tests/test_incident_requirements.py`.
- **Evidence preserved:** `evidence/incident/runs/local-20261028T181818Z` and `evidence/m365/runs/local-offline-20261028T181845Z` are untouched. A new local SIMULATION run, `evidence/incident/runs/local-20261029T000545Z` (+ `.console`), was added alongside it:
  - 2026-10-28 20:05 EDT, PostgreSQL 16.15
  - 19/19 steps passed
  - MTTD 3.590 s, MTTR 8.677 s
  - all six requirements passed
  - labelled with `SIMULATION.md`
- **What the M365 "13" and "43" count:**

  | Number | What it counts | Source in the engine report |
  |---|---|---|
  | **13** | Scenario files evaluated. Each matched its recorded expected verdict **and** expected finding codes | `totals.scenarios` = `totals.passed` = 13 |
  | **43** | PLAN_ONLY remediation plan steps emitted across those 13 scenarios, each `executed: false`. These are planned actions, **not assertions or tests** | `totals.plannedSteps` |
  | 28 | Findings across the 13 scenarios | |
  | 29 | Unit tests | `identity/m365/tests` |
  | 15 | Commands in the committed evidence run, all with the expected exit code | |

  These are counts produced by the scenario engine; they are not a measure of how many checks the module was tested against.
- **Local `validate-all`:** PASS (43 steps; coincidentally the same number as the plan steps) with `PG_BIN=/workspace/pg16/bin`.
- **Round 2 record (`02ac2de`):** CI showed the fail-closed behaviour with the M365 module absent: the M365 jobs, offline-validation, final-summary and merge-eligibility failed. It is history only and was never a review target.

- **Frozen combined candidate `5f159f1c757d7fbf2964e4d8b615fcb9a810f7ca`**, tested against current main `7f50348` on `candidate/main-validation-5f159f1` @ `ba4d5e02146b33b74957a60b62a055f4c46ad089`. The `--no-ff` merge was clean and the merged tree is identical to the candidate. Local `validate-all` PASSED 43/43 on both.

  In every gate run below, **every required job succeeded** and `final-summary` reported "gate: PASS". `merge-eligibility` **failed, by design**, because AC1, AC2, AC4 and AC5 are open.

  | Run | Notes |
  |---|---|
  | [integration-gate, main-validation 40792435152](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792435152) | Fresh SIMULATION run on PostgreSQL 18.6: all six requirements PASS; MTTD 3.704 s, MTTR 8.73 s |
  | [integration-gate push 40792418163](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792418163) | Fresh run MTTD 3.501 s |
  | [integration-gate PR 40792426144](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426144) | Fresh run MTTD 3.489 s, MTTR 8.695 s |
  | [postgres-restore-evidence 40792426140](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426140) | 5/5 succeeded |
  | [aws-cdk 40792426294](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426294) | Succeeded |
  | [offline-validation PR 40792426193](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426193) | Succeeded |
  | [offline-validation push 40792418146](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792418146) | Succeeded |

- **NOT_EXECUTED items in these runs:** none. The PostgreSQL binaries were present on the runner. The NOT_EXECUTED path runs only in the negative job, where it correctly fails.
- **Independent review of `5f159f1`:** **not yet requested.** The packet is `coordination/review-requests/PR-7-candidate-5f159f1.md`. Earlier reviews and approvals (`eb42b23`, `82ab7e6`, `02ac2de`, PR #14, PR #27) do not transfer.

## Round 2 (2026-10-28 ~20:00 EDT, request pt12u): M365 required checks, checkpoint, new candidate

- **Reconcile:** remote `overnight/integration` was still at `82ab7e6`. Local `1a3cea0` was a fast-forward, so I pushed it normally (no rebase, no force).
- **Checkpoint:** annotated tag `checkpoint/eb42b23` → `eb42b23747d5b686d9540c93e445a713b4e56c5d` (PR #26 head), pushed. It marks a point in history only. It is not a review or an approval and is not integrated. Do not move or rewrite it.
- **M365 module:** found in PR #20, branch `m365-endpoint` @ `1b3c240`. It is a draft with no reviews and no CI, so it is **not integrated**. It is registered in `coordination/modules.json` as `required: true`.
- **Required checks:** wired in both `validate-all.sh` and `integration-gate.yml`, and they **fail closed**:

  | Check | validate-all.sh step | integration-gate.yml job | What it does |
  |---|---|---|---|
  | Scenario evaluation | `m365 scenario evaluation` | `m365-scenario-evaluation` | Runs every scenario. Every expectation must match and every scenario file must be covered. PLAN_ONLY assertion on the fresh report |
  | Unit tests | `m365 unit tests` | `m365-unit-tests` | `identity/m365/tests` |
  | Evidence verification | `m365 evidence verification` | `m365-evidence-verification` | `generate_evidence.py --verify` on every committed run, plus the PLAN_ONLY assertion |
  | Negative tests | `plan-only negative tests` | `plan-only-assertions` | 14 PLAN_ONLY violation tests and 4 required-check tests (missing, skipped, cancelled and failed must each fail) |

- **PLAN_ONLY assertions** (`scripts/ci/check_plan_only.py`):
  - every plan step has mode `PLAN_ONLY` and `executed: false`
  - every `executed` key is `false`
  - `mutationsExecuted` is the integer 0
  - at least one plan step exists

  Only the M365 module produces such records.
- **Fail-closed gate:** `final-summary` and `merge-eligibility` fail if any job in `required_gate_jobs` is missing, skipped, cancelled or failed. `check_modules.py` fails if a required job is undefined or missing from either job's `needs`. **A clean merge without these checks is not acceptance.**
- **Local trial (not committed, not pushed):** this branch plus a `--no-ff` merge of `1b3c240` passed all four checks:
  - 13/13 scenarios
  - 29 unit tests
  - evidence verify OK
  - 43 PLAN_ONLY steps
  - `mutationsExecuted` 0

  A run copy with one step set to `executed: true` was rejected.
- **Acceptance workflow:** there is none on this branch. `acceptance.yml` exists only on PR #26's branch, which was not modified.
- **Expected result:** on this branch the M365 jobs, `offline-validation` (its `--python-only` suite includes the M365 steps), `final-summary` and `merge-eligibility` **fail by design** until PR #20 is reviewed and integrated. AC3 is therefore UNMET for the new candidate. AC3 was MET for `82ab7e6`, but that is history only and does not transfer.

## Accelerated completion plan (PR #27 @ 72aa8b7, lane B): progress as of 2026-10-28 18:27 EDT (see Round 2/3 above for later work)

Deadline 2026-10-29 00:00 EDT. Remaining window at commit time: about 5h33m. This commit started from `4f54a016`.

| # | Item | Status |
|---|---|---|
| 1 | USER ACTION REQUIRED reporting in Actions (`integration-gate.yml`: `user-actions` early job, `final-summary` with `if: always()`) | Done; pending CI on the candidate |
| 2 | Actions pinned to full commit SHAs | Done (all `actions/*`). Only the same-repo reusable workflows (`./.github/workflows/*.yml`) are not SHA-pinned, because they always resolve at the commit under test |
| 3 | Module registry `coordination/modules.json` + `scripts/ci/check_modules.py` | Done; runs in validate-all.sh and in CI |
| 4 | Freeze candidate; test against current `main` on `candidate/main-validation-<sha>` | Done: candidate `82ab7e6` tested on `candidate/main-validation-82ab7e6` @ `ccbb442`; passed |
| 5 | tasks.json / INTEGRATION.md updated | Done for this commit (`accelerated_plan`, `user_actions`, `autonomous_blockers`) |

The USER ACTION REQUIRED top line is currently **USER ACTION REQUIRED: 4 — UA-1; UA-2; UA-3; UA-4**, plus UA-5 (AC6), which isn't actionable yet. The user actions are: exception approval, Entra baseline choices, branch-protection decision and closing PR #1.

Component workflows also accept `workflow_call`, so the gate runs them for the exact SHA. Their own push and pull_request triggers are unchanged, which means some jobs run twice on a PR. aws-cdk's concurrency group now includes the caller workflow name, so a gate run and a standalone run don't cancel each other.

**Gates**
- Exact-SHA review: **UNMET** (AC1).
- Current-main validation: **PASSED**. Frozen candidate `82ab7e6bbec1d20e034494c987253f3a81f3296c` was merged with `--no-ff` onto main `7f50348` as throwaway branch `candidate/main-validation-82ab7e6` @ `ccbb44216a777174b688767e0fb900db599e8eb1`. The merge was clean with no conflicts (main is an ancestor), and the tree is identical to the candidate. Local `validate-all` PASSED 35/35. In [integration-gate run 40778969827](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778969827), user-actions, module-registry, offline-validation, aws-cdk, all 5 postgres jobs and final-summary succeeded. merge-eligibility failed, as designed.

**Frozen candidate `82ab7e6` CI** (later commits on this branch change only `coordination/tasks.json` and this report):

| Run | Result |
|---|---|
| [integration-gate push 40778886245](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778886245) | All jobs succeeded except merge-eligibility (failed, by design) |
| [integration-gate PR 40778896261](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778896261) | Same |
| [postgres-restore-evidence PR 40778896275](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778896275) | 5/5 succeeded |
| [aws-cdk PR 40778896256](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778896256) | Succeeded |
| [aws-cdk push 40778886053](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778886053) | Succeeded |
| [offline-validation PR 40778896220](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778896220) | Succeeded |
| [offline-validation push 40778886069](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778886069) | Succeeded |
- Merge eligibility (C6): **NOT ELIGIBLE**. The `merge-eligibility` job is expected to fail until AC1–AC5 are MET for one exact SHA.

PR #27 C1–C5 are about PR #26's acceptance verifier. That verifier is not integrated, so none of C1–C5 is addressed here, and PR #26's branch was not touched.

## Merge policy (updated per [PR #27](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27) finding C6)
- **Automated merges into `main` are allowed once independently proven.** That means an independent review approving the *exact* candidate SHA (AC1), with every other acceptance condition (AC2–AC5) met for that same SHA.
- **Final human portfolio acceptance (AC6) is a separate gate.** Technical merge eligibility is not portfolio acceptance.
- **No technical blocker is relaxed.** The following all still block:
  - failing or missing checks
  - unapproved security exceptions
  - the PR #6 self-logging defect
  - docs mismatches
  - the open findings PR #14 B5-1/B5-2 and PR #27 C1–C5
- This replaces the earlier wording "never merge into main from automation" and the requirement for an independent *human* review. This integration agent still does not merge into `main` itself and makes no production changes.

## Per-PR disposition

| PR | Branch @ head | Disposition | Why |
|---|---|---|---|
| [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) | `review/pr1-pr2-evidence-audit` @ `fb36341` | **Integrated** (1st) | Shared, dependency-free tooling (`evidence/shared/`) that later checks rely on. It is the review of #1/#2. |
| [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) | `aws-remediation-vpc-rds` @ `099479e` | **Integrated** (2nd) | Newer `infra/aws-cdk` that includes #1's app and fixes #3's blocking self-logging finding. |
| [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) | `bank-aws-001` @ `e494bcf` | **Superseded by #5** | 14 duplicate `infra/aws-cdk` files. Its top-level `evidence/aws/**` is for the self-logging template, which fails `cfn-s3-selflog`. Only its CI workflow was carried forward, adapted as `.github/workflows/aws-cdk.yml`. |
| [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) | `entra-ca-offline` @ `d302c99` | **Integrated** (3rd) | Disjoint paths, stdlib only, all checks pass. |
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | `ci-evidence-postgres` @ `e7399fb` | **Integrated, harness v2** (4th; re-merged in `e76d8a4`) | The owner's harness v2 (`2aac93c`, `e7399fb`) fixes #3's false-PASS finding. It replaces the interim integration hardening from `f3a8f17`. GitHub CI at `e7399fb`: 5/5 jobs green. |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | `orgs-security-refs` @ `e5e7f46` | **Awaiting changes, not integrated** | `TrailAccessLogsBucket` logs to itself (`infra/orgs/lib/org-cloudtrail-stack.ts:50`), which is the same defect #3 blocked in #1. `cfn-s3-selflog` reports an ERROR on `evidence/orgs/synth/BankItLabOrgCloudTrail.template.json`. The PR is also a self-declared draft. A trial merge was clean, and tsc, Jest 49/49 and synth passed. |

No PR has a formal GitHub review, and none of the open PRs has a review comment. The only review is #3's report (`reports/review-pr1-pr2.md`), which covers #1 and #2. Every integrated PR still needs an independent review of the exact candidate SHA (AC1). PR #14's notes and PR #27's review are recorded below.

## Related PRs verified on 2026-10-28 (~17:45 EDT; recorded, not integrated)
| PR | Exact head | What we found | Disposition |
|---|---|---|---|
| [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) `review/pr3-pr6` | `eb8d259588f2d1ba8a8787cf2c37044617cbcbdb` | **Review notes only** (1 file, `reports/review-pr3-pr6.md`). No GitHub reviews, comments or CI. The author account is the same as every other PR, so the independence is asserted, not demonstrable. Checkpoint 2 verifies PR #2's harness v2 at `2aac93c`/`e7399fb`: the 4 v1 false PASSes are remediated (on replay, N01/N05/N06 → ERROR/version_mismatch and N04 → ERROR/environment_error). The same notes **request changes** on #5 (B5-1, B5-2: both in integrated code) and #6. **Discrepancy:** the claim "verification on PR #14" describes content at `eb8d259` about PR #2's code, not a review of PR #14. | Recorded. Counts toward AC1 **only for PR #2's harness v2**. |
| [#26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26) `acceptance/vertical-slice` | `181bcdd1420d699c37aa928b636b9332aca83e57` | Built on `49122f2` (+99 files). Run [40749373581](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749373581) is on that SHA and succeeded with **3 jobs, 3 success**. The "43 required checks" are internal to the acceptance job (artifact: 43/43 PASS + 2 non-required). Planted defect (CA002 report-only) **detected**: overall FAIL, 35/43, 8 required FAILs incl. ENTRA-02. Other runs on the SHA: [40749387217](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387217), [40749387209](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387209), [40749387223](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387223), [40749387416](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387416), all success. **Discrepancies:** 43 is not a GitHub check count; PR #26 is stale against PR #25 head `ce39504` (integrated `c6aa238`). | Not integrated: **CHANGES REQUIRED** per PR #27 (C1–C5). |
| [#27](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27) `review/chatgpt-acceptance-181bcdd` | `703f6a71840559e98f49b4c897ca5216d4018133` | External ChatGPT review of #26 @ `181bcdd`: **CHANGES REQUIRED**. C1 no required-check inventory; C2 required INFO → PASS; C3 JSON/TSV disagreement undetected; C4 contract approval not the final gate; C5 tag pins, 30-day retention, head-not-merge testing; C6 obsolete coordination wording (fixed here). | Recorded; source of the merge-policy update. |

External review packets (self-contained, verdict requested on the exact SHA): `coordination/review-requests/` (README, PR-14, PR-26).

## File overlap and conflicts
- **#1 and #5** share 14 `infra/aws-cdk/**` files. #5's commit 1 imports #1 @ `e494bcf`, minus `lib/evidence-validator.ts`, `scripts/validate-evidence.ts`, `test/evidence-validator.test.ts` and the `validate:evidence` npm script. #5 is used, and #1's copy is dropped.
- Every other pair is disjoint. #2 and #1 both add `.github/workflows/*`, but with different filenames.
- No textual merge conflicts.

## Integration changes
1. `.github/workflows/aws-cdk.yml`: PR #1's workflow adapted to PR #5.
   - covers both stacks and both cdk-nag packs; requires exactly 4 reports with 0 Non-Compliant
   - uses the evidence path `evidence/aws/aws-remediation-vpc-rds/SHA256SUMS`
   - adds the `cfn-s3-selflog` gate, a synth-drift diff, `npm ci --ignore-scripts`, and a wider credential-variable check
2. `.github/workflows/offline-validation.yml`: runs `scripts/validate-all.sh --python-only`.
3. PR #2 re-merge (`e76d8a4`, merging `e7399fb`):
   - My interim changes to `run_restore_scenario.sh`, `postgres-restore-evidence.yml` and `ci-service-40630856041-1/NOTE.md` (from `f3a8f17`) conflicted with the owner's v2. I resolved all three to the **owner's version**.
   - The interim evidence run `integration-offline-20261028T180134Z` was removed in `e76d8a4`. It was then **restored byte-for-byte** from `fb70afd`, with a `STATUS.json` marking it HISTORICAL-KNOWN-INVALID and a row in `evidence/postgres/runs/INDEX.md`, so that no earlier evidence record is deleted.
   - Every v1 failure record (`ci-service-40630856041-1`) is unchanged from `e610015`, apart from the owner's added NOTE.md text and STATUS.json.
   - The #2 source commit `e7399fbb538504f723d1fb83e32ce50604807b8e` is an ancestor of HEAD. Re-merging it reports "Already up to date".
   - The v2 workflow has its own pinned `cdk-synth` job with no `CDK_DEFAULT_*`, so it overlaps `aws-cdk.yml`. That is harmless.
4. Interface fix between #3 and #2 (`05941a9`): on v2's 12-column `COMMANDS.tsv`, `evidence/shared/validate_evidence.py postgres-negatives` silently reported `NEGATIVES OK: 0 negative steps`.
   - It now finds columns by header name, so it handles v1 and v2.
   - It errors when it finds zero negatives.
   - 2 new unit tests (15/15).
   - It agrees with v2's `verify_evidence.py` on every committed run: 6/6 on the current runs, and 4 false PASSes on the v1 CI run.
5. `infra/aws-cdk/README.md` and `evidence/shared/README.md`: fixed stale paths and stale "not wired into CI" text.
6. `scripts/validate-all.sh`, `.gitignore`, this report, and `coordination/tasks.json`.

## Validation result
I ran `PG_BIN=<conda-forge PG 16.15>/bin scripts/validate-all.sh` on the box with no AWS credentials (Node 20.19.2, Python 3.13.5). Result: **PASS, all 33 steps** (latest run 2026-10-28 ~17:45 EDT, PG 16.15). The full step list is in the draft PR description.
- Shared validator: 16/16 (stricter: a negative that is not PASS is an error).
- Entra:
  - 25/25 tests
  - baseline exit 0
  - fixture drift OK
  - evidence verify OK
- aws-cdk:
  - tsc OK, Jest 33/33, synth OK
  - 4 nag reports with 0 Non-Compliant
  - no S3 self-logging
  - no synth drift
  - SHA256SUMS OK
- Postgres v2:
  - The committed CURRENT runs `ci-service-40741329107-1`, `ci-offline-40741329107-1` and `local-offline-v2-20261028T180208Z` are VERIFIED.
  - `ci-mismatch-control-40741329107-1` is REJECTED, as intended.
  - The v1 runs report HISTORICAL (exit 3).
  - The self-test passes.
  - A fresh offline v2 run passes 38/38 and is verified with `--require-artifacts`.
  - The shared validator cross-check agrees.

## Acceptance conditions for merging PR #7 into `main`
Evaluated at the PR #7 head pushed with this report. Under the merge policy above, an automated merge needs AC1–AC5 MET for the same SHA, and AC6 is a separate gate. Machine-readable copy: `coordination/tasks.json` → `acceptance_conditions_for_main`.

| # | Condition | Status | Detail |
|---|---|---|---|
| AC1 | An independent review (human or independent reviewer, e.g. ChatGPT) approves the **exact** candidate SHA. Provenance must be bound to that SHA, and author or agent self-review does not count. *Reworded per PR #27 C6.* | **UNMET** | No approval for any PR #7 head. PR #14 @ `eb8d259` counts only for PR #2's harness v2, and it requests changes on integrated #5. PR #27 reviewed #26, not #7. |
| AC2 | Security exceptions recorded **and approved**. | **PARTIAL** | EX-01..EX-04 are recorded and test-enforced, but not approved. PR #14 B5-1: the suppressions are already applied. |
| AC3 | All checks pass on that SHA (PR #7 CI + `scripts/validate-all.sh`). | **COMPUTED_AT_RUNTIME** by merge-eligibility for each run's identity (candidate, base, tested merge); the decision is in run artifact `acceptance-decision-<tested_sha>` and on branch `evidence/acceptance`. Earlier MET records (82ab7e6, 5f159f1, 7fe6d72) are history only. | See checkpoint pt15u. |
| AC4 | Docs match the code (READMEs, PR bodies, INTEGRATION.md, tasks.json). | **PARTIAL**: in-tree docs updated (pt15u). Open: PR #1 still open (UA-4), PR #4 baseline choices unconfirmed (UA-2; none claimed), PR #7 description out of date. | See checkpoint pt15u. |
| AC5 | No unresolved blocking findings in integrated code. | **UNMET** | PR #14 B5-1/B5-2 on integrated #5. Fixed in this commit: the shared `postgres-negatives` reported OK on all-NOT_RUN runs. |
| AC6 | Final human portfolio acceptance (Ian). Separate gate. | **UNMET** | Not requested; it follows AC1–AC5. |

## Open issues / blockers before `main`
- #6 needs the self-logging fix and regenerated evidence. Once that is done it can merge cleanly, because its paths are disjoint.
- #5's security exceptions EX-01..EX-04 need an owner's approval.
- #4's baseline choices need an owner's confirmation: risk policies stay report-only, the device-compliance scope, and the 12 privileged roles.
- #2's v2 `cdk-synth` job duplicates `aws-cdk.yml`. It is not a blocker.
- #1 should be closed as superseded by its owner. Integration did not close it.
- No PR has a GitHub review approving an exact SHA. Review evidence so far is in PR #3, #14 and #27 report files.
- PR #14 B5-1/B5-2 on #5: fix the KMS key-admin statement, and approve or revoke the suppressions.
- PR #27 C1–C5 on #26 (acceptance verifier): required-check inventory, INFO handling, JSON/TSV consistency, contract as final gate, workflow pinning.
- Actions are pinned by tag, not SHA (carried over from #1/#2).
