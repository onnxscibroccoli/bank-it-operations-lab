# USER ACTIONS REQUIRED (Ian)

> **DEADLINE: midnight ET (00:00 EDT, Thursday 2026-10-29), the end of Wednesday 2026-10-28.**
> **Remaining window at commit time (2026-10-28 18:08 EDT): about 5 h 51 min.**
> Status: **not complete.** Nothing is merged into `main`, and no workstream meets every acceptance criterion: no human GitHub review exists anywhere. The acceptance vertical slice runs green in CI on a draft PR (#26). That is a working gate, not a merge. Nothing here claims completion that was not verified.

Snapshot: 2026-10-28, about 18:08 EDT. The #7 integration head is `4f54a01`, and the acceptance slice #26 is at `eb42b23` (CI green, decision REVIEW_PENDING). This reports agent never merges, closes PRs or deploys. Since #7 @ `4f54a01` (C6), coordination policy allows *independently proven* automated merges. None has happened, and none is currently provable (UA-1, UA-2). Only the USER_ACTION_REQUIRED items need Ian; the AUTONOMOUS_FIX items belong to the lane owners. See `FINAL_REPORT.md` §2 for the merge policy (gates G1–G9) and the status of each PR.

```
USER ACTION REQUIRED: 6 — authenticated reviewer for exact-SHA approval; branch protection on main; EX-03/EX-04 sign-off; Entra baseline; #6 Terraform-vs-CDK; final portfolio acceptance
```

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

## USER_ACTION_REQUIRED items (as of 2026-10-28 18:08 EDT)
| ID | Action | Reason it can't be automated | Observed error | Smallest permission | Link | Blocks | Continuing | Deadline impact |
|---|---|---|---|---|---|---|---|---|
| UA-1 | Decide how independent review is authenticated for exact-SHA approval | All 27 PRs are authored by the single account `onnxscibroccoli`, and GitHub does not let a PR author approve their own PR. An authenticated GitHub review therefore needs a second identity (a collaborator or bot account) or an explicit owner policy that names an alternative provenance (for example signed review commits on an audit branch). | No GitHub review exists on any PR. Reviewer names in agent notes are unauthenticated strings (PR #27, C4). | Repo admin: add a reviewer collaborator or GitHub App, or record the policy decision | https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/access | The G1 / AC1 gate for every merge to main | All implementation, CI, integration and agent review | YES: no merge can be gate-proven tonight without it |
| UA-2 | Approve enabling a branch-protection rule or ruleset on main that requires the final acceptance gate | This is a repository-wide setting. The account has admin (verified through the API), but changing settings is outside this reports-only role and needs your explicit approval. #27 says to query first and never bypass. | GET branches/main/protection returns 404 "Branch not protected"; rulesets: [] (checked 18:08 EDT) | Repo admin (the account already has it) | https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/branches | #27 P0: wire the final decision into an actual merge gate | Lanes A–E | Partly: merges can still be serialized manually, but they are not enforced |
| UA-3 | Give the final risk sign-off on EX-03 (wildcard scope) and EX-04 (Backup role), and have EX-01/EX-02 recorded as approved in #5 | This is a material risk decision outside delegated lab scope. The supporting verifications can be done autonomously; the sign-off cannot. | EX-03 is OPEN and EX-04 is CONDITIONAL in the register. #14 lists B5-1 (suppressions applied before approval). | Owner decision | https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5 | #5, #7, #26 (they carry #5) | The B5-2 KMS fix and the other lanes | YES for #5, #7 and #26 |
| UA-4 | Confirm the #4 Entra baseline choices: risk policies report-only, device compliance for All users on All apps, the 12 privileged roles | This is a policy decision that belongs to the owner | Marked unconfirmed in #4 and in #7 AC4 | Owner decision | https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4 | #4 acceptance (C2 criterion) | Everything else | YES for #4 |
| UA-5 | Decide on #6: accept CDK, or require Terraform as the original plan asked | Scope decision (#14 B6-3) | #6 delivers CDK. The Terraform items are MISSING and the deviation is undocumented. | Owner decision | https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6 | #6 only (it is already excluded from #7) | Everything else | YES for #6 |
| UA-6 | Final human portfolio acceptance (AC6) at the deadline | #7 tasks.json makes portfolio acceptance a separate human gate; technical eligibility is not acceptance | n/a (this is a future step) | Owner decision | https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/11 | Declaring the portfolio accepted | All technical work | It is the final step before midnight |

## Classification of the remaining A/B items below
| Class | Items |
|---|---|
| USER_ACTION_REQUIRED | A1 final sign-off (→ UA-3), A3 (→ UA-4), A4 (→ UA-1), A6 B6-3 decision (→ UA-5), B4 (→ UA-2), the AC6 final acceptance (→ UA-6) |
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
| EX-01 | NIST.800.53.R5-S3DefaultEncryptionKMS | BankItLabSecureStorage/AccessLogsBucket | **ACCEPTED for the lab** | Bucket-policy verification (A1) |
| EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled | AccessLogsBucket, DataBucket | **ACCEPTED as an explicit limitation.** The "env-agnostic makes it impossible" claim is **REJECTED** | Reword the register (A1) |
| EX-03 | AwsSolutions-IAM5 (`log-group:RDSOSMetrics:log-stream:*`) | BankItLabNetworkDatabase/RdsMonitoringPolicy | **OPEN** | Verify the exact wildcard scope (A1) |
| EX-04 | AwsSolutions-IAM4 (AWSBackupServiceRolePolicyForBackup) | BankItLabNetworkDatabase/BackupPlan/Postgres/Role | **CONDITIONALLY ACCEPTABLE** | Role review (A1) |
