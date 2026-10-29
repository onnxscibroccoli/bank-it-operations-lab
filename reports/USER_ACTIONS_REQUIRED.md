# USER ACTIONS REQUIRED (Ian)

> **DEADLINE: midnight ET (00:00 EDT, Thursday 2026-10-29), the end of Wednesday 2026-10-28.**
> **Remaining window at commit time (2026-10-28 21:54 EDT): about 2 h 5 min.**
> Status: **not complete.** Nothing is merged into `main` (`7f50348`). The live candidate is PR #7 @ `e9310f3`: 7 of 25 active modules integrated, every technical CI job green, and merge-eligibility **NOT ELIGIBLE** (AC1, AC2, AC4 and AC5 UNMET). No approval is stated here that Ian did not give.

Snapshot: 2026-10-28, about 21:54 EDT, against #7 @ `e9310f3a94162a5dae31ee1cca9e35452de033ed`, gate run [40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048).

```
USER ACTION REQUIRED: 4 — UA-1 owner decision comment for EX-01..EX-04/AC4/AC5 (EX-04 role-review gap); UA-2 Entra CA baseline; UA-3 protect main; AC1 independent reviewer account
```
CI prints `USER ACTION REQUIRED: 4 — UA-1; UA-2; UA-3; UA-4`. The counts match, but the items differ: UA-4 is housekeeping, and the AC1 reviewer account is added. The reconciliation is below.

Module status (exactly one class each, 25 active modules): **integrated 7 · verified 7 · independently accepted 0 · blocked 8 · not-started 3 = 25**. The per-module table is in [`MODULE_REQUIREMENT_MAP.md`](MODULE_REQUIREMENT_MAP.md) §1.

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

## Reconciliation with the Actions log (re-done about 21:54 EDT at `e9310f3`)
Exact log lines from integration-gate [40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048) (#7 @ `e9310f3`, pull_request, about 21:48 EDT); the BLOCKING lines are from its `offline-validation / validate` job:
```
USER ACTION REQUIRED: 4 — UA-1; UA-2; UA-3; UA-4
MODULE COVERAGE: 7/25 integrated (28.0%), functional 7/17; denominator 26 (BLOCKED=1, INTEGRATED=7, NOT_INTEGRATED=14, NOT_STARTED=3, SUPERSEDED=1)
BLOCKING USER ACTION (UA-1): suppression AwsSolutions-IAM5 on BankItLabNetworkDatabase.template.json:RdsMonitoringPolicy5DA8ACAC is applied while EX-03 is PROPOSED
BLOCKING USER ACTION (UA-1): suppression AwsSolutions-IAM4 on BankItLabNetworkDatabase.template.json:BackupPlanPostgresRole2A2CEBDF is applied while EX-04 is PROPOSED
BLOCKING USER ACTION (UA-1): suppression NIST.800.53.R5-S3DefaultEncryptionKMS on BankItLabSecureStorage.template.json:AccessLogsBucket83982689 is applied while EX-01 is PROPOSED
BLOCKING USER ACTION (UA-1): suppression NIST.800.53.R5-S3BucketReplicationEnabled on BankItLabSecureStorage.template.json:AccessLogsBucket83982689 is applied while EX-02 is PROPOSED
BLOCKING USER ACTION (UA-1): suppression NIST.800.53.R5-S3BucketReplicationEnabled on BankItLabSecureStorage.template.json:DataBucketE3889A50 is applied while EX-02 is PROPOSED
merge-eligibility for tested 9ff24a445edf5ea8cb8428b3ce238180ecf3a207 (candidate e9310f3a94162a5dae31ee1cca9e35452de033ed): NOT ELIGIBLE
  AC1: UNMET (trusted reviewer_allowlist is empty; no APPROVED review on exact candidate e9310f3a94162a5dae31ee1cca9e35452de033ed by an allow-listed, write-permitted account other than the PR author onnxscibroccoli)
  AC2: UNMET (BLOCKING USER ACTION UA-1: no owner decision on candidate e9310f3a94162a5dae31ee1cca9e35452de033ed for applied exceptions EX-01 EX-02 EX-03 EX-04)
  AC4: UNMET (no authorized AC4 decision on candidate e9310f3a94162a5dae31ee1cca9e35452de033ed)
  AC5: UNMET (no authorized AC5 decision on candidate e9310f3a94162a5dae31ee1cca9e35452de033ed)
```

**Correction to the 21:04 EDT version:** it called EX-01, EX-02 and EX-03 "RESOLVED_BY_RECORD" and narrowed UA-1 to EX-04. That overstated the record:
- Ian's decisions on EX-01, EX-03 and EX-04 are **conditional**.
- EX-02 is accepted, but it is not recorded in the register.
- The live gate (`e9310f3`) takes UA-1 only from Ian's `ACCEPTANCE-DECISION v1` comment on PR #7 for the exact SHA.

So UA-1 covers all four exceptions.

| ID | CI item | Reconciled class | Evidence |
|---|---|---|---|
| **UA-1** | Approve or reject EX-01..EX-04 and their 5 applied suppressions | **USER_ACTION_REQUIRED** (blocks AC2 and AC5) | Register @ `e9310f3`: all entries PROPOSED. The decisions Ian relayed and the verification evidence are in the register section below |
| **UA-2** | Confirm the Entra CA baseline: risk policies report-only, device compliance on All users / All apps, the 12-role privileged list | **USER_ACTION_REQUIRED** (blocks AC4) | `evidence/entra/BASELINE-CHOICES-PENDING.md` @ `e9310f3` says PENDING. No decision is recorded |
| **UA-3** | Protect `main` with the exact settings in the CI text: ruleset on `main`, empty bypass list, 1 approval, dismiss stale approvals, required gate checks | **USER_ACTION_REQUIRED for ELIGIBLE** | `path_to_eligible` step 1 at `e9310f3`. Still unprotected: 404, 0 rulesets |
| **AC1 reviewer** | Name an independent reviewer and add the account as a collaborator with Write. The integrator then adds it to `reviewer_allowlist` | **USER_ACTION_REQUIRED** | `reviewer_allowlist: []` @ `e9310f3`. The gate says "trusted reviewer_allowlist is empty" |
| UA-4 | Close PR #1 | HOUSEKEEPING | `bank-aws-001` is SUPERSEDED in the registry |
| UA-5 | AC6 final acceptance | NOT_YET_ACTIONABLE | Applies after AC1–AC5 |

**What Ian can do for UA-1, AC4 and AC5 (format from `tasks.json` @ `e9310f3`):** Ian posts ONE new, never edited, comment on [PR #7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) from the owner account. The body must read exactly:
```
ACCEPTANCE-DECISION v1
candidate: <exact 40-hex candidate SHA>
UA-1: APPROVE EX-01 EX-02 EX-03 EX-04
AC4: ACCEPT
AC5: ACCEPT
```
`REJECT` is used instead of `APPROVE` to reject. **This report does not post or pre-fill it, and it is not an approval.** On Ian's relayed decisions:
- **EX-02** is accepted.
- **EX-01 and EX-03** are conditional. Their verification evidence is below.
- **EX-04** is conditional, and its role review found a gap (no `aws:SourceAccount`).
- **`AC4: ACCEPT`** would also need UA-2 settled first.

Posting all-APPROVE now would therefore go beyond what Ian has decided. He should settle EX-01, EX-03, EX-04 and UA-2 first. Any new commit to #7 needs a new comment for the new SHA. `tasks.json` (F7 residual) notes that the comment proves the account, not the person, so Ian should post it himself.

**ETA dependency:** UA-1, UA-2, UA-3 and the AC1 reviewer account are all on `path_to_eligible`. The earliest merge is about 01:00–02:30 EDT Thursday. See [`MODULE_REQUIREMENT_MAP.md`](MODULE_REQUIREMENT_MAP.md) §4.

### Gates and deferred items (not counted as user actions)
| Item | Class | Evidence |
|---|---|---|
| AC1 approval itself | **GATE** | Needs an allow-listed reviewer (see the AC1 reviewer row above) to approve the exact SHA |
| #31 F4 / F5 / F6 / F7 / R6 | Repairs claimed in `ce69f84`/`e9310f3`, **unreviewed** | 114 CI self-tests OK here; the logic was not audited |
| B5-2 KMS key-admin escalation | **FIXED** in `80f01d6` | `tasks.json` AC5 detail and #31. The key policy was not audited here |
| #6 Terraform-vs-CDK (B6-3) | DEFERRED | `orgs-security` is BLOCKED in the registry |

## Classification of the remaining A/B items below
| Class | Items |
|---|---|
| USER_ACTION_REQUIRED | EX-01..EX-04 decision comment (→ UA-1, with AC4/AC5), A3 Entra baseline (→ UA-2), B4 protect main (→ UA-3), AC1 reviewer account |
| CONDITIONAL (Ian's decision relayed, not APPROVED) | EX-01 (policy evidence verified), EX-03 (scope evidence verified), EX-04 (role review finds a gap); EX-02 accepted but not recorded |
| OWNER_DECISION, non-blocking | none (UA-3 moved to USER_ACTION_REQUIRED at `e9310f3`) |
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
| A1 | **Close UA-1.** Decisions are relayed for EX-01..EX-04 (see the register below), but none is APPROVED in the register. The verification evidence at `e9310f3` is below:<br>• **EX-01:** verify the AccessLogsBucket policy (TLS-only deny, PutObject only from `logging.s3.amazonaws.com` with SourceArn = DataBucket and SourceAccount), then sign off.<br>• **EX-02:** have #5's `SECURITY_EXCEPTIONS.md` reworded as an explicit lab limitation. Remove the "not expressible in an env-agnostic stack" rationale and note that the exception covers 2 resources.<br>• **EX-03:** verify the exact wildcard scope (`…:log-group:RDSOSMetrics:log-stream:*`, 4 log actions, this account and region; trust `monitoring.rds.amazonaws.com` + `aws:SourceAccount`), then accept or reject.<br>• **EX-04:** review the Backup role. Its trust lacks `aws:SourceAccount`; the vault has no access policy or Vault Lock and shares the DB CMK. Then accept or reject.<br>Afterwards, record the decisions in #5 (register status plus approver) so that B5-1 is closed | [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` |
| A2 | **B5-2: recorded FIXED in #7 @ `80f01d6`** (confirmed by #31; not audited here). Original ask, kept for history:<br>• use a named key-admin principal<br>• drop `kms:CreateGrant` from the admin actions, or add `kms:GrantIsForAWSResource`<br>• restrict `kms:PutKeyPolicy`<br>• add a negative test<br>• withdraw the "least-privilege CMK" claim until it is fixed<br>Correct #7's AC5 ("MET" at `afb41278`) as well | [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5), [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7), [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) |
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

## Security exception register: EX-01..EX-04 (#5), reconciled at `e9310f3`
Decisions are recorded exactly as Ian relayed them (21:41 EDT, consistent with the 14:10 EDT relay). The register file in the repo still reads PROPOSED. The evidence comes from the synth templates @ `e9310f3`:
- `BankItLabSecureStorage.template.json` sha256 `9ba9be1d…`
- `BankItLabNetworkDatabase.template.json` sha256 `c3dd0a0c…`

The bundle's `SHA256SUMS` re-checked 44/44 OK.

| ID | cdk-nag rule / resource | Ian's decision | Register | Verification evidence | Status |
|---|---|---|---|---|---|
| EX-01 | NIST.800.53.R5-S3DefaultEncryptionKMS / AccessLogsBucket | Accepted, pending policy verification | PROPOSED | **Bucket:** SSE-S3 (AES256), Block Public Access ×4, versioning, BucketOwnerEnforced.<br>**Policy:** denies `s3:*` without TLS. Allows `s3:PutObject` only to `logging.s3.amazonaws.com` on `/data-bucket/*`, with SourceArn = DataBucket and SourceAccount = this account.<br>**AWS docs:** "The destination bucket must use Amazon S3 managed keys (SSE-S3)" | **Conditional.** Evidence verified; awaiting Ian's confirmation. Not APPROVED |
| EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled / AccessLogsBucket, DataBucket | Accepted as a limitation | PROPOSED | Versioning Enabled and Retain on both buckets; no replication. The register wording "not expressible…" still needs the docs fix | **Accepted (Ian).** Not yet recorded in the register |
| EX-03 | AwsSolutions-IAM5 / RdsMonitoringPolicy | Conditional on scope verification | PROPOSED | The wildcard covers only `log-group:RDSOSMetrics:log-stream:*` in this account and region. The group statement has no wildcard. The trust is `monitoring.rds.amazonaws.com` + `aws:SourceAccount` | **Conditional.** Evidence verified; awaiting Ian's confirmation. Not APPROVED |
| EX-04 | AwsSolutions-IAM4 / BackupPlan/Postgres/Role | Conditional on role review | PROPOSED | The trust is `backup.amazonaws.com` with **no `aws:SourceAccount`**. The policy is AWS's documented `AWSBackupServiceRolePolicyForBackup`. The vault has no access policy or Vault Lock (#14) | **Conditional; gap found.** Ian decides: accept, or require the fix |
