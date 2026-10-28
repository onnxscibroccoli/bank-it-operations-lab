# Restore validation runbook (AWS Backup, RDS PostgreSQL first)

Status: **NOT_EXECUTED.** Written for a future, approved exercise. Commands are for an operator with an approved change
ticket. They were **not** run while building this repo. Restores create billable resources (cost-capacity worksheet).

Roles: **Operator** (runs steps), **Verifier** (independent check of V-steps), **Approver** (change owner).
Evidence: copy `evidence/backup/aws-backup-dr/templates/restore-test-record.template.{md,json}` to
`evidence/backup/aws-backup-dr/runs/<UTC-timestamp>-<scenario>/`. Log each command with `run-cmd.sh`-style
`COMMANDS.tsv` rows: UTC start, exit code, duration, log, command. Keep failures.

## 0. Preconditions (stop if any fail)
- P1 Change approved. Scenario chosen (S1-S5 in RTO_RPO.md). Restore target name follows `bank-it-lab-restore-<yyyymmdd>-<scenario>`.
- P2 Prerequisites A1-A8 and K1-K6 met (PREREQUISITES.md).
- P3 Target network ready: DB subnet group and security group in the target region (isolated subnets, no 0.0.0.0/0).
- P4 Source fingerprint captured before the incident point, or a known reference dataset exists (same approach as `evidence/postgres` on `ci-evidence-postgres`: row counts and an ordered checksum per table).
- P5 Never restore over the production identifier. Always restore to a **new** resource.

## 1. Restore (R-steps)
| Step | Action | Command (template, NOT run) | Record |
|---|---|---|---|
| R0 | Declare start | `date -u +%FT%TZ` | `declared_utc` |
| R1 | Pick the recovery point | `aws backup list-recovery-points-by-backup-vault --backup-vault-name bank-it-lab-primary-vault --by-resource-type RDS --region us-east-1`. For DR use `bank-it-lab-dr-copy-vault` and `--region us-west-2`. | ARN, creation time, `Status=COMPLETED`, `IsEncrypted=true`, lifecycle |
| R2 | Read restore metadata | `aws backup get-recovery-point-restore-metadata --backup-vault-name <vault> --recovery-point-arn <rp>` | Metadata JSON |
| R3 | Start restore, new identifier, private subnets | `aws backup start-restore-job --recovery-point-arn <rp> --iam-role-arn arn:aws:iam::<acct>:role/bank-it-lab-restore-role --metadata file://restore-metadata.json` (DBInstanceIdentifier=new name, DBSubnetGroupName, VpcSecurityGroupIds, PubliclyAccessible=false, MultiAZ per scenario). PITR: use `RestoreDBInstanceToPointInTime`-type metadata and `RestoreTime`. | `restore_job_id` |
| R4 | Wait | `aws backup describe-restore-job --restore-job-id <id>` until `COMPLETED` or `FAILED`/`ABORTED` | Status, `CreationDate`, `CompletionDate`, `ExpectedCompletionTimeMinutes` |

## 2. Validate (V-steps, Verifier signs)
| Step | Check | Pass criterion |
|---|---|---|
| V1 | Resource properties | `aws rds describe-db-instances --db-instance-identifier <new>`: `PubliclyAccessible=false`, `StorageEncrypted=true`, expected `KmsKeyId`, expected subnet group, port 5433, deletion protection decided for the drill |
| V2 | Connectivity (from inside the VPC only) | TLS connection succeeds (`sslmode=verify-full`). `rds.force_ssl=1` is honored. IAM auth works if used. |
| V3 | Data integrity | Fingerprints (row counts, ordered checksums) equal the reference for the chosen point in time. Any mismatch = FAIL. |
| V4 | RPO measurement | Latest committed business timestamp in the restored DB vs incident/target time is the observed RPO |
| V5 | Application smoke test | Read-only query set from the app role succeeds |
| V6 | Declare validated | `date -u +%FT%TZ`. Observed RTO = V6 - R0. |
| V7 | Negative check | Restore of a deliberately tampered or out-of-window point is rejected, or detected by V3 (mirrors the Postgres negative tests) |

## 3. Clean up (C-steps)
- C1 Export evidence, then delete the restored instance (`aws rds delete-db-instance ... --skip-final-snapshot` only when approved for a drill instance).
- C2 Confirm no restored resources remain (`aws resourcegroupstaggingapi get-resources --tag-filters Key=restore-drill,Values=<label>`).
- C3 Recovery points are **not** deleted by the drill (Vault Lock).

## 4. DR-region variant (S3/S4)
Same steps with `--region us-west-2`, vault `bank-it-lab-dr-copy-vault`, and the DR key. Also record the copy lag:
`aws backup list-copy-jobs --by-destination-vault-arn <dr-vault-arn>` (`CreationDate`, `CompletionDate`).
PITR is not available for copies. Choose a snapshot recovery point.

## 5. Automated restore testing (AWS Backup restore testing)
`bank_it_lab_monthly_restore_test` restores the latest RDS snapshot (30-day window) of tagged resources monthly, with a
24 h validation window, then AWS Backup deletes the restored resource. It shows the restore *job* works. It does not run
V2-V5. Add a validation hook (`PutRestoreValidationResult`) before treating it as data validation. Gap: no metadata
overrides for the isolated VPC (README gap 4).

## 6. Record
Fill every field in the record template. `status` is one of `NOT_EXECUTED | EXECUTED_PASS | EXECUTED_FAIL | ABORTED`.
Never leave numbers without attached job IDs and logs.
