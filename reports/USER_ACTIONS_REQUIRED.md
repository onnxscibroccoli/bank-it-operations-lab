# USER ACTIONS REQUIRED (Ian)

Snapshot: 2026-10-28 about 14:10 EDT. Automation never merges into `main`, never closes PRs and never deploys. Everything below needs a human.

## Merge policy (proposed; needs your OK)
1. Merge only after a human review on GitHub and green CI on the PR head.
2. Order: review and merge **#7 `overnight/integration`**, which already carries #3, #5, #4 and #2. Then close #1, #2 (only once it has been reconciled with #7, see A4), #3, #4 and #5 as "landed via #7". #6, #8 and #9 each land separately after their own fixes.
3. No secrets or credentials go into CI. All workflows stay credential-free (`permissions: contents: read`).

## A. Decisions and approvals
| ID | Action | Where |
|---|---|---|
| A1 | **Approve or reject security exceptions EX-01..EX-04** (register below) | [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` |
| A2 | **Confirm the Entra CA baseline choices:** risk policies stay report-only (`riskPoliciesMustBeReportOnly`); device compliance applies to All users on All apps; the list of 12 privileged roles | [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) |
| A3 | **Review PR #7 on GitHub and decide on it.** It is the integration of #3, #5, #4 and #2. No PR has any review yet | [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) |
| A4 | **Pick the Postgres harness version.** #2 moved on to harness v2 (`2aac93c`, `e7399fb`, CI green) after #7 integrated `e610015` with its own negative-test fixes. Ask someone to rebase or reconcile #7 onto #2's v2, or keep #7's version | [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2), [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) |
| A5 | **Close #1 as superseded by #5** once #7 lands. The automation did not close it | [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) |
| A6 | **Send #6 back for changes:** remove the `TrailAccessLogsBucket` self-logging (`infra/orgs/lib/org-cloudtrail-stack.ts:50`), regenerate `evidence/orgs` and `SHA256SUMS`, and optionally add CI | [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) |
| A7 | **Review the portfolio (#8), vendor-mock (#9) and observability (#10, not verified in this report) drafts.** #9 is a SIMULATION, so confirm the wording. #8 citations have not been verified | [#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8), [#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) |
| A8 | **Backup/DR has no PR.** Its work is uncommitted in the box worktree `/workspace/bkp-dr-aws-worker` (branch `backup-dr-aws`, untracked `backup/`). Decide whether to finish and push it or drop it | box |
| A9 | **Accept the remaining known gaps or ticket them:** Actions are pinned by tag, not SHA; there is no CI for #6, #8 or #9; and the cdk-nag 2.x pin is in place (ADR-0001 on #1/#5) | — |

## B. Credentials, secrets and access (only if you want more than static evidence)
| ID | Action | Notes |
|---|---|---|
| B1 | **Choose an AWS sandbox account/role (OIDC, no long-lived keys)** if you want a real deploy, AWS Access Analyzer validation of the #6 SCPs, or a live check of the cdk-nag exceptions | None of this exists today. Everything so far is a credential-free synth. Do not add AWS keys as repo secrets |
| B2 | **Choose a sandbox Entra tenant** if you want the #4 CA policies checked against real tenant state | Today #4 is offline and synthetic only (`tenantStateClaimed: false`) |
| B3 | **Set up a dedicated rclone Google client_id** if you want Drive evidence checkpoints to continue | The shared client_id is being retired [#1 MORNING_REPORT] |
| B4 | **Turn on branch protection for `main`** (required review plus required checks `aws-cdk`, `offline-validation` and `postgres-restore-evidence`) | Repo admin setting. Not done |

## Security exception register: EX-01..EX-04 (from #5, all PENDING owner approval)
| ID | cdk-nag rule | Resource | Rationale (from #5 `SECURITY_EXCEPTIONS.md`) | Exit criteria | Status |
|---|---|---|---|---|---|
| EX-01 | NIST.800.53.R5-S3DefaultEncryptionKMS | BankItLabSecureStorage/AccessLogsBucket | S3 server access log delivery supports only SSE-S3 on the target bucket (ADR-0002) | Use CloudTrail S3 data events into a KMS-encrypted bucket if CMK-encrypted logs are mandated | **PROPOSED, pending your approval** |
| EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled | AccessLogsBucket, DataBucket | Cross-region replication needs a second region or account, which an env-agnostic, never-deployed stack cannot express | Add a replica stack per target at deployment design time | **PROPOSED, pending your approval** |
| EX-03 | AwsSolutions-IAM5 (`log-group:RDSOSMetrics:log-stream:*`) | BankItLabNetworkDatabase/RdsMonitoringPolicy | RDS enhanced monitoring writes service-named streams. The wildcard is limited to one log group | None expected (this is how the service behaves) | **PROPOSED, pending your approval** |
| EX-04 | AwsSolutions-IAM4 (AWSBackupServiceRolePolicyForBackup) | BankItLabNetworkDatabase/BackupPlan/Postgres/Role | AWS's documented AWS Backup service-role policy, needed for NIST RDSInBackupPlan | Use a customer-managed RDS-only policy if the IAM standard forbids AWS-managed policies | **PROPOSED, pending your approval** |

Per #5, each suppression covers one rule on one resource, and its tests fail if any suppression outside this list appears. That statement comes from the PR body and was not re-verified here.
