# Security exception register: backup-dr-aws

Status of every entry: **PROPOSED, pending owner approval.** Nothing is deployed. Each exception is a scoped cdk-nag
suppression on one rule and one resource, with `appliesTo` pinned. `test/stacks.test.ts` (`only registered exceptions are
suppressed`) fails on any other suppression.

| ID | Rule | Resource | Why | Compensating controls | Exit criteria |
|----|------|----------|-----|-----------------------|---------------|
| BKP-EX-01 | AwsSolutions-IAM4 (appliesTo `service-role/AWSBackupServiceRolePolicyForBackup`, `AWSBackupServiceRolePolicyForS3Backup`) | BankItLabBackupPrimary/BackupServiceRole | AWS-documented service-role policies for backup and copy across RDS, EBS, EFS, S3, and DynamoDB. A hand-written equivalent needs snapshot wildcards (IAM5) and drifts from AWS updates. Same reasoning as EX-04 on `aws-remediation-vpc-rds`. | Trust only `backup.amazonaws.com` with `aws:SourceAccount`. 1h sessions. Separate restore role. Vault Lock plus a deny-delete vault policy. CMKs limited by `kms:ViaService`. | Replace with customer-managed policies if the bank IAM standard forbids AWS-managed policies. |
| BKP-EX-02 | AwsSolutions-IAM4 (appliesTo `service-role/AWSBackupServiceRolePolicyForRestores`, `AWSBackupServiceRolePolicyForS3Restore`) | BankItLabBackupPrimary/RestoreServiceRole | AWS-documented restore policies (per-service create APIs, `iam:PassRole`). | Same trust conditions. Used only by restore jobs and restore testing. | As BKP-EX-01. |

The DR stack has no suppressions.
