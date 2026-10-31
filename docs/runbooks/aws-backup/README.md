# AWS Backup DR runbooks (bank-it-operations-lab)

Scope: the static AWS Backup reference in `backup/aws/` and its evidence in `evidence/backup/`. **Nothing has been deployed
and no AWS backup, copy, or restore has been executed.** Every "observed" value in this tree is `NOT_EXECUTED` (recovery)
or `NOT_OBSERVED` (billing/capacity). Numbers labelled `HYPOTHESIS` or `ESTIMATE` are planning inputs, not measurements.

| Document | Purpose |
|---|---|
| [PREREQUISITES.md](PREREQUISITES.md) | KMS, account, region, and resource-type support prerequisites |
| [RETENTION_AND_DELETION.md](RETENTION_AND_DELETION.md) | Vault Lock, cold-storage 90-day minimum, copy retention, deletion behavior |
| [RESTORE_VALIDATION_RUNBOOK.md](RESTORE_VALIDATION_RUNBOOK.md) | Step-by-step restore validation (in-region and DR region) with evidence capture |
| [RTO_RPO.md](RTO_RPO.md) | HYPOTHESIS targets vs OBSERVED lab measurements (all NOT_EXECUTED) |
| [cost-capacity/](cost-capacity/README.md) | Cost-driver worksheet (ESTIMATE) and capacity troubleshooting exercise |

Evidence templates: `evidence/backup/aws-backup-dr/templates/`. Status files: `evidence/backup/aws-backup-dr/RECOVERY_EXECUTION_STATUS.json`,
`evidence/backup/aws-backup-dr/rto-rpo-observations.json`, `evidence/backup/cost-capacity/`.

## Gaps
1. Never deployed: CloudFormation Rules (`PinRegion`), vault access policy, restore testing plan and copy actions are validated only by synth, cdk-nag, and Jest.
2. Same-account cross-region copy only. No separate backup account, no cross-account copy, no logically air-gapped vault.
3. No job-failure alerting (vault notifications / EventBridge to SNS) and no AWS Backup Audit Manager framework (needs AWS Config recording).
4. Restore testing selection has no `RestoreMetadataOverrides` (DB subnet group, security groups). In the isolated VPC from `aws-remediation-vpc-rds` an RDS restore test needs them.
5. Not wired to `infra/aws-cdk` (owned by another worker). That stack already has its own 35-day plan and CMK vault for RDS (`BankItLabNetworkDatabase/BackupPlan`). Before deploying, consolidate it into one plan or tag the DB `backup-plan=bank-it-lab-standard` and drop the duplicate. Its `DatabaseKey` must stay usable by AWS Backup and RDS (it already allows `backup` and `rds` via `kms:ViaService`).
6. Vault Lock is GOVERNANCE mode. COMPLIANCE mode, legal holds, and 7-year retention for regulated records still need an approved change.
7. Shared evidence validator (`evidence/shared/`, PR #3) is not on `main`. It was run from a separate checkout and not vendored.
8. No CI workflow. `.github/` is outside the owned paths.
