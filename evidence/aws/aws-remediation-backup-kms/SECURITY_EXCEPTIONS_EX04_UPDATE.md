# Proposed update to EX-04 (register row is a frozen record; not edited in place)

The authoritative register is `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md`. It is hash-pinned in
`docs/metadata/preserved-records.json`, so it was not edited. The rule it registers is unchanged
(`AwsSolutions-IAM5` on `BankItLabNetworkDatabase/DbBackupPolicy`), so `scripts/ci/check_exceptions.py` still
matches. The proposed replacement text follows. Status: **PROPOSED, DEPLOYMENT-BLOCKING, pending owner approval.**

- **Rule / resource:** AwsSolutions-IAM5, appliesTo
  `Resource::arn:<AWS::Partition>:rds:<AWS::Region>:<AWS::AccountId>:snapshot:awsbackup:*`, on
  BankItLabNetworkDatabase/DbBackupPolicy.
- **Why:** AWS Backup names RDS snapshots `awsbackup:job-<id>` at job time. The AWS-managed policy uses
  `snapshot:awsbackup:*`. The earlier `snapshot:awsbackup-*` (hyphen) did not match (F-06) and has been corrected.
- **Compensating controls:** a customer-managed policy limited to this instance, `awsbackup:*` snapshots, and this
  vault. KMS crypto and CreateGrant are in separate statements (CreateGrant requires
  `kms:GrantIsForAWSResource=true`), both with `kms:ViaService` rds|backup, on DatabaseKey and the dedicated
  BackupVaultKey only. The trust allows `backup.amazonaws.com` with `aws:SourceAccount` and, by default,
  `aws:SourceArn` = this vault. Fallback modes keep SourceAccount and never use IfExists.
- **Exit criteria:** VERIFICATION_PROCEDURE.md V-2 to V-7 pass in a non-prod account, and the owner approves.
  Until then, **DEPLOYMENT-BLOCKING** (RESEARCH_EX04.md: AWS Backup does not document SourceArn or SourceAccount on
  sts:AssumeRole).
