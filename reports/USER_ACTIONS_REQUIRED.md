# USER ACTIONS REQUIRED (Ian)

> **DEADLINE: midnight ET (00:00 EDT, Thursday 2026-10-29), the end of Wednesday 2026-10-28.**
> **Remaining window at commit time (2026-10-28 21:04 EDT): about 2 h 55 min.**
> Status: **not complete.** Nothing is merged into `main`, and no workstream meets every acceptance criterion: no human GitHub review exists anywhere. The acceptance vertical slice runs green in CI on a draft PR (#26). That is a working gate, not a merge. Nothing here claims completion that was not verified.

Snapshot: 2026-10-28, about 21:04 EDT. The #7 integration head is `08cdf11` (final candidate `7fe6d72`: every technical CI job green, merge-eligibility NOT ELIGIBLE, review packet prepared but **not yet requested**, so the AC1 gate is unmet), and the acceptance slice #26 is at `eb42b23` (CI green, decision REVIEW_PENDING). This reports agent never merges, closes PRs or deploys. Since #7 @ `4f54a01` (C6), coordination policy allows *independently proven* automated merges. No merge into `main` has happened, and none is currently provable (AC1 gate unmet; `main` unprotected). The integrator did merge #20 @ `1b3c240` and #22 @ `9f21329` into the integration branch (#7), not into `main`. Only the USER_ACTION_REQUIRED items need Ian; the AUTONOMOUS_FIX items belong to the lane owners. See `FINAL_REPORT.md` §2 for the merge policy (gates G1–G9) and the status of each PR.

```
USER ACTION REQUIRED: 2 — UA-1/EX-04 Backup-role risk decision; UA-2 Entra CA baseline choices
```
CI currently prints `USER ACTION REQUIRED: 4 — UA-1; UA-2; UA-3; UA-4` (see the reconciliation below; the difference is intentional and explained).

## User-action reporting format (implements PR #27, "User intervention without stopping the project")
- **Top line, always present, even when the overall status is failing:** `USER ACTION REQUIRED: NONE`, or `USER ACTION REQUIRED: <number> — <short action>`.
- **Classification at every checkpoint.** Every blocker gets exactly one class:
  - **AUTONOMOUS_FIX:** test failures, conflicts, docs, agent review, code fixes.
  - **USER_ACTION_REQUIRED:** only interactive login or MFA after a real failure, an admin setting outside available permissions or that needs approval, approval to spend money, or a material risk or scope decision.
  - **OUT_OF_SCOPE:** for example live AWS or Entra validation, which is intentionally excluded. Credentials are never requested.
- **Typed fields for each USER_ACTION_REQUIRED item.** These are the #27 list, in fixed order:
  - `id`
  - `action` (exact)
  - `reason` (why it cannot be automated)
  - `error` (observed, sanitized)
  - `permission` (smallest permission needed)
  - `link` (instructions)
  - `blocks` (blocked tasks; only these are BLOCKED_USER)
  - `continuing` (work that continues)
  - `deadline` (whether it affects the midnight deadline)
- **Machine-readable copy:** [`user-actions.json`](user-actions.json), schema `bank-it-operations-lab/user-actions@1`. Values are plain data and must never be interpolated as shell code.
- **Not implemented here (outside this reports-only role):** #27 also asks for a fast Actions reporting job that writes this top line to `$GITHUB_STEP_SUMMARY`, emits a warning annotation, uploads the JSON as a small artifact, and repeats it in the final `always()` summary. That belongs to lane B (the integrator, `.github/workflows/**`). The JSON file is shaped so that job can consume it directly.
- **Not proof of notification:** a report or summary does not mean Ian was notified. GitHub email or push delivery depends on his notification settings.
- **Choices made where #27 is not precise:**
  1. `<short action>` is a semicolon-separated list of every item's short label.
  2. IDs are stable `UA-n`; resolved items stay listed with `status: RESOLVED` and a verification note.
  3. The JSON is the canonical copy and the table below is generated from the same data in this commit.

## Reconciliation with the Actions log (about 21:04 EDT)
Exact log lines, `user-actions (USER ACTION REQUIRED report)` job, [run 40794058923](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40794058923) (#7 head `08cdf11`, pull_request, 2026-10-29T00:26:41Z = 20:26 EDT):
```
USER ACTION REQUIRED: 4 — UA-1; UA-2; UA-3; UA-4
##[warning]Approve or reject the AWS security exceptions EX-01..EX-04 in evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md, and the cdk-nag suppressions that are already applied for them (PR #14 B5-1). Where: https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5
##[warning]Confirm the Entra Conditional Access baseline choices: risk policies stay report-only, device compliance applies to All users on All apps, and the 12-role privileged list. Where: https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4
##[warning]Decide whether to protect main and require the integration-gate checks final-summary and merge-eligibility. Where: https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/branches
##[warning]Close PR #1 as superseded by PR #5, or tell the integrator to keep it open. Where: https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1
```
The same top line also appears in that run's `offline-validation / validate` and `final-summary` jobs, and identically in runs [40794054069](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40794054069) (`08cdf11` push), [40793225624](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225624) / [40793219129](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793219129) (final candidate `7fe6d72`), [40792426144](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426144) (`5f159f1`, line at 00:11:57Z) and [40778896261](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40778896261) (`82ab7e6`, first occurrence 22:18:16Z).

| ID (same as CI) | CI item (exact `##[warning]` text, abridged) | Reconciled class | Evidence |
|---|---|---|---|
| UA-1 / EX-01 | "Approve or reject the AWS security exceptions EX-01..EX-04 … (PR #14 B5-1)" | **RESOLVED_BY_RECORD** | Decision on record (Ian via ChatGPT security review, 14:10 EDT): accepted for the lab, pending bucket-policy verification. Verification exists in #5's committed synth template [`synth/BankItLabSecureStorage.template.json`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/099479e6d23968adb17762d88d84131998fca07c/evidence/aws/aws-remediation-vpc-rds/synth/BankItLabSecureStorage.template.json) @ `099479e` (sha256 `0b0eda0fed541fe0…`, listed in the bundle's `SHA256SUMS`): `AccessLogsBucketPolicy` = Deny `s3:*` when `aws:SecureTransport=false`; Allow `s3:PutObject` only to `logging.s3.amazonaws.com` with `aws:SourceArn` = DataBucket ARN and `aws:SourceAccount` = this account. Template only; never deployed |
| UA-1 / EX-02 | same | **RESOLVED_BY_RECORD** (+ AUTONOMOUS_FIX docs) | Decision on record: accepted as an explicit lab limitation; the "not expressible in an env-agnostic stack" wording is rejected. Rewording [`SECURITY_EXCEPTIONS.md`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/099479e6d23968adb17762d88d84131998fca07c/evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md) is a docs fix for the #5 owner, not a user action |
| UA-1 / EX-03 | same | **RESOLVED_BY_RECORD** | Decision on record: open pending exact wildcard-scope verification. Verified in [`synth/BankItLabNetworkDatabase.template.json`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/099479e6d23968adb17762d88d84131998fca07c/evidence/aws/aws-remediation-vpc-rds/synth/BankItLabNetworkDatabase.template.json) @ `099479e` (sha256 `44d48d2e43e73725…`): `RdsMonitoringPolicy` wildcard is only `arn:…:logs:<region>:<account>:log-group:RDSOSMetrics:log-stream:*` (CreateLogStream, PutLogEvents, DescribeLogStreams, GetLogEvents); the group-level statement has no wildcard; role trust `monitoring.rds.amazonaws.com` with `aws:SourceAccount`. Matches the register's claim |
| UA-1 / EX-04 | same | **USER_ACTION_REQUIRED** (real risk decision; can collapse to AUTONOMOUS_FIX) | Decision on record: conditionally acceptable, pending role review. The role review in the same template **finds a gap**: `BackupPlanPostgresRole` trust is `backup.amazonaws.com` with **no `aws:SourceAccount` condition** (unlike the monitoring role). #14 also notes the vault has no access policy or Vault Lock and shares the DB CMK. Choose: (a) accept as is, or (b) require the #5 owner to add `aws:SourceAccount` (an AUTONOMOUS_FIX), after which EX-04 becomes RESOLVED_BY_RECORD |
| UA-2 | "Confirm the Entra Conditional Access baseline choices: risk policies stay report-only, device compliance applies to All users on All apps, and the 12-role privileged list" | **USER_ACTION_REQUIRED** (real risk decision) | No decision is recorded anywhere: PR [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) has 0 comments and its body still lists these under "Notes / open questions"; `identity/entra/baseline.json` encodes the proposed choice only |
| UA-3 | "Decide whether to protect main and require the integration-gate checks final-summary and merge-eligibility" | **OWNER_DECISION, non-blocking** (not escalated) | **No admin-permission failure occurred.** `GET /repos/…/branches/main/protection` → `HTTP 404 {"message":"Branch not protected"}` (unset, not 403); `GET /repos/…/rulesets` → `[]`; `GET /repos/…` → `permissions.admin: true` for the owner account (all checked about 20:58 EDT). tasks.json itself records `"blocks": []`. Without protection the gate is advisory; nothing tonight is blocked |
| UA-4 | "Close PR #1 as superseded by PR #5, or tell the integrator to keep it open" | **HOUSEKEEPING** (not a user blocker) | Routine PR hygiene after #7 lands. tasks.json marks its impact "Minor (docs consistency)" |
| UA-5 | (not printed: `status: NOT_YET_ACTIONABLE`, so CI does not count it) | **NOT_YET_ACTIONABLE** | AC6 final human portfolio acceptance; only after AC1–AC5 are MET for one SHA |

**Why this differs from the CI count (intentional):** CI prints `USER ACTION REQUIRED: 4 — UA-1; UA-2; UA-3; UA-4` from `coordination/tasks.json` `user_actions` on #7. Its UA-1 text says "Register lists EX-01..EX-04 as PROPOSED … no approval is recorded", which is stale: Ian's decisions were recorded in this report at 14:10 EDT, and the committed #5 templates verify EX-01 and EX-03. Its UA-3 is a decision with no permission failure and `blocks: []`, and its UA-4 is housekeeping. Net: **4 printed → 2 user blockers** (UA-1 narrowed to EX-04, UA-2 unchanged). This report does not edit `coordination/tasks.json` (integrator-owned). Proposed change for the integrator: set UA-1 `observed` to the recorded decisions and narrow its action to EX-04; reclassify UA-3 as non-blocking owner decision and UA-4 as housekeeping (`classification` ≠ `USER_ACTION_REQUIRED`), so the CI top line becomes `USER ACTION REQUIRED: 2 — UA-1; UA-2`.

**"NONE" relay:** no Actions run printed `USER ACTION REQUIRED: NONE`. All 72 runs created since 21:00 UTC (17:00 EDT) were scanned; every integration-gate and #7 offline-validation run since `82ab7e6` (first run 22:18 UTC = 18:18 EDT) prints `USER ACTION REQUIRED: 4 — UA-1; UA-2; UA-3; UA-4`; the others (aws-cdk, postgres, #26 acceptance) print no top line. The NONE relay was wrong.

### Gates and deferred items (not counted as user actions)
| Item | Class | Evidence |
|---|---|---|
| AC1 independent review of the exact final candidate `7fe6d72` | **GATE** (tracked by `merge-eligibility`, not by user-actions) | [run 40794058923](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40794058923) and [40793225624](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225624): `NOT ELIGIBLE`, `AC1: UNMET`. The review packet `coordination/review-requests/PR-7-candidate-7fe6d72.md` is prepared but **not yet requested** (integrator step). Previously listed here as UA-1 "authenticated reviewer"; it needs the owner only if a GitHub-authenticated approval from a second identity is required, because all PRs share one author account |
| #6 Terraform-vs-CDK (#14 B6-3) | **DEFERRED owner scope decision**, non-blocking | #6 is excluded from the #7 candidate (B6-1, B6-2 open), so nothing tonight depends on it |
| B5-2 KMS key-admin escalation | AUTONOMOUS_FIX (#5 owner) | #14 finding; blocks AC2 regardless of the exception decisions |

## Classification of the remaining A/B items below
| Class | Items |
|---|---|
| USER_ACTION_REQUIRED | EX-04 decision (→ UA-1), A3 Entra baseline (→ UA-2) |
| RESOLVED_BY_RECORD | EX-01, EX-02, EX-03 (decisions on record; EX-01/EX-03 verified in #5 synth templates) |
| OWNER_DECISION, non-blocking | B4 branch protection (→ UA-3; 404 unset, admin held, no failure) |
| HOUSEKEEPING | A5 close #1 (→ UA-4) |
| GATE / DEFERRED / NOT_YET_ACTIONABLE | A4 independent review (AC1 gate), A6 B6-3 Terraform-vs-CDK (deferred), AC6 (→ UA-5) |
| AUTONOMOUS_FIX | A1 verifications, A2 (B5-2 KMS fix), A5 (close #1 after #7 lands; integrator), A6 B6-1/B6-2 fixes, A7 reviews (agent review possible; human acceptance stays UA-6), A8 (#21 exceptions file and CI), A9 (pins, CI, lifecycle), A10 post-merge verify, A12 (#26 gaps and #25 integration), A13 (#22 CI), C5, the #27 hardening items, module CI registration |
| OUT_OF_SCOPE (per #27: no speculative AWS/Entra setup, no new spend) | B1 AWS sandbox, B2 Entra tenant, B3 rclone client_id |

## Merge policy (recorded)
- A PR merges only when G1–G7 pass for its **exact head SHA**:
  - G1: a human reviewed that SHA
  - G2: exceptions are adjudicated
  - G3: checks pass
  - G4: docs match the code
  - G5: integration-tested
  - G6: revalidated against current `main`
  - G7: verified on `main` after the merge
- G8 (no false-pass tests) and G9 (no superseded unsafe code) must also hold.
- A passing scanner alone never meets a gate.
- Proposed order: #7, after its blockers are fixed. Then close #1 as superseded and close #2–#5 as landed through #7. Every other PR lands on its own.

## A. Decisions, verifications and approvals
| ID | Action | Where |
|---|---|---|
| A1 | **Finish the remaining exception verifications.** EX-01..EX-04 are DECIDED (see the register below), but four checks are still open:<br>• **EX-01:** verify the AccessLogsBucket policy (TLS-only deny, PutObject only from `logging.s3.amazonaws.com` with SourceArn = DataBucket and SourceAccount), then sign off.<br>• **EX-02:** have #5's `SECURITY_EXCEPTIONS.md` reworded as an explicit lab limitation. Remove the "not expressible in an env-agnostic stack" rationale and note that the exception covers 2 resources.<br>• **EX-03:** verify the exact wildcard scope (`…:log-group:RDSOSMetrics:log-stream:*`, 4 log actions, this account and region; trust `monitoring.rds.amazonaws.com` + `aws:SourceAccount`), then accept or reject.<br>• **EX-04:** review the Backup role. Its trust lacks `aws:SourceAccount`; the vault has no access policy or Vault Lock and shares the DB CMK. Then accept or reject.<br>Afterwards, record the decisions in #5 (register status plus approver) so that B5-1 is closed | [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` |
| A2 | **Fix B5-2 (KMS key-admin escalation) before #5 or #7 can merge:**<br>• use a named key-admin principal<br>• drop `kms:CreateGrant` from the admin actions, or add `kms:GrantIsForAWSResource`<br>• restrict `kms:PutKeyPolicy`<br>• add a negative test<br>• withdraw the "least-privilege CMK" claim until it is fixed<br>Correct #7's AC5 ("MET" at `afb41278`) as well | [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5), [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7), [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) |
| A3 | **Confirm the Entra CA baseline choices:** risk policies stay report-only, device compliance applies to All users on All apps, and the list of 12 privileged roles | [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) |
| A4 | **Do a human GitHub review of each exact head SHA** (G1). No PR has one. #14's agent notes: #3 approve, #4 approve with comments, #5 and #6 request changes, and (checkpoint 2) **#2's false-PASS fix remediated at `e7399fb`**. That review item is done and verified here, so #2 now needs only your human review. Optional #2 hardening: regex ordering, verifier EXPECTATIONS check, cdk-synth skip status | all PRs, [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) |
| A5 | **Close #1 as superseded by #5** once #7 lands | [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) |
| A6 | **Send #6 back for changes:**<br>• B6-1: self-logging on `TrailAccessLogsBucket`<br>• B6-2: SCP exempt-role-name bypass<br>• B6-3: decide whether to accept CDK or redo it in **Terraform**, as your plan asked<br>• also adjudicate its 2 parliament allowlist entries | [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) |
| A7 | **Review the docs and simulation PRs:**<br>• #8: links verified, prose not checked<br>• #9: SIMULATION wording<br>• #10: tests and evidence verified, code not reviewed<br>• #12: job matrix<br>• #13: synthetic team model<br>• #15: learning guide, citations verified<br>• #16: FFIEC mapping; confirm it is lab-only<br>• #17: patching and hardening<br>• #18: identity governance<br>• #19: hybrid/AD runbooks<br>• #20: M365, which has **no tests or committed evidence** | [#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8), [#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9), [#10](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/10), [#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12), [#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13), #15–#20 |
| A8 | **Backup/DR:** draft PR [#21](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/21) @ `10da54f` now exists. Adjudicate its `SECURITY_EXCEPTIONS.md` and add CI. All recovery items are NOT_EXECUTED: proving a real restore needs an AWS sandbox (B1) | #21 |
| A9 | **Accept or ticket the known gaps:**<br>• Actions pinned by tag, not SHA<br>• no CI on #6, #8–#10, #12 or #13<br>• the cdk-nag 2.x pin<br>• no lifecycle or retention rules on the #5 buckets<br>• the allowlist test misses stack-level suppressions | — |
| A12 | **Acceptance slice #26 (`181bcdd`, CI [40749373581](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749373581) green): decide whether it is the merge vehicle.** It carries all of #7 (#2–#5), including the unresolved B5-2. Also:<br>• integrate #25's newer `ce39504`, or drop it<br>• close the `ACCEPTANCE.md` §5 UNKNOWN gaps: emit results as a contract document, and add an independent `concur` record<br>The packet itself does not approve a merge | [#26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26), #23–#25 |
| A13 | **Incident demo #22:** review it and keep the **SIMULATION** label on every use. It is a loopback lab DB crash, not a live incident. Add CI if you want it gated | [#22](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/22) |
| A11 | **Before midnight ET, choose what ships as-is and what slips.** With no human reviews and B5-2 unresolved, nothing can meet the merge gates without your action. The realistic end state for tonight is documented drafts plus your decisions on A1–A3 | — |
| A10 | **Post-merge (G7):** after each merge, re-run CI and evidence verification on `main`, and revert if anything fails | — |

## B. Credentials, secrets and access (only if you want more than static evidence)
| ID | Action | Notes |
|---|---|---|
| B1 | **Choose an AWS sandbox role with OIDC (no long-lived keys)** for a real deploy, Access Analyzer checks of the #6 SCPs, or live checks of the exceptions | Nothing exists today. Do not add AWS keys as repo secrets |
| B2 | **Choose a sandbox Entra tenant** for checking #4 against real tenant state | #4 is offline and synthetic only today |
| B3 | **Set up a dedicated rclone Google client_id** for Drive evidence checkpoints | The shared client_id is being retired [#1 MORNING_REPORT] |
| B4 | **Turn on branch protection for `main`:** require a review plus the checks `aws-cdk`, `offline-validation` and `postgres-restore-evidence` | Repo admin setting; not done |

## Security exception register: EX-01..EX-04 (#5), DECIDED
Source: the ChatGPT security review as adopted by Ian, relayed 2026-10-28 at about 14:10 EDT. It is not yet recorded in #5.

| ID | cdk-nag rule | Resource | Decision | Open condition |
|---|---|---|---|---|
| EX-01 | NIST.800.53.R5-S3DefaultEncryptionKMS | BankItLabSecureStorage/AccessLogsBucket | **ACCEPTED for the lab** | **RESOLVED_BY_RECORD**: bucket policy verified in the #5 synth template (see reconciliation) |
| EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled | AccessLogsBucket, DataBucket | **ACCEPTED as an explicit limitation.** The "env-agnostic makes it impossible" claim is **REJECTED** | **RESOLVED_BY_RECORD**; register rewording is an AUTONOMOUS_FIX for the #5 owner |
| EX-03 | AwsSolutions-IAM5 (`log-group:RDSOSMetrics:log-stream:*`) | BankItLabNetworkDatabase/RdsMonitoringPolicy | was OPEN pending scope verification | **RESOLVED_BY_RECORD**: scope verified in the #5 synth template (log streams of the one RDSOSMetrics group, this account/region) |
| EX-04 | AwsSolutions-IAM4 (AWSBackupServiceRolePolicyForBackup) | BankItLabNetworkDatabase/BackupPlan/Postgres/Role | **CONDITIONALLY ACCEPTABLE** | **Still open (UA-1)**: role review found no `aws:SourceAccount` on the trust policy |
