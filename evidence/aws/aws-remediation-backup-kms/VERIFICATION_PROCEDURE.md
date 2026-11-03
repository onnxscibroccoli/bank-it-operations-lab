# VERIFICATION_PROCEDURE: EX-04 and backup KMS runtime checks (NOT EXECUTED)

Status: **NOT_EXECUTED.** These steps are for a later, separately approved test in a **non-production, disposable**
AWS account. They are not to be run from this lab. They need owner approval, a sandbox account with no production
data, and a named operator. Until V-2 and V-3 pass, EX-04 stays **DEPLOYMENT-BLOCKING**.

## Preconditions

- P-1: A sandbox account and Region are approved in writing. The test role is limited to that account. A budget alarm
  is set.
- P-2: `BankItLabKmsKeyAdmin` exists. The operator role can pass `DbBackupRole` only with
  `iam:PassedToService=backup.amazonaws.com`.
- P-3: CloudTrail management events are enabled for STS, KMS, RDS, and Backup (a trail or event data store), and
  logs are kept for the test window.
- P-4: Synthesize from a clean checkout of this branch:
  `cd infra/aws-cdk && npm ci && npx jest --ci && npx cdk synth --no-lookups`. Record the template SHA-256 next to
  `synth/` in this directory.

## Steps

1. **V-1 (deploy, sandbox only):** deploy `BankItLabNetworkDatabase` with the default mode `vault-arn`. Record the
   stack ARN.
2. **V-2 (trust, per operation):** start an on-demand backup of the instance with `DbBackupRole` (StartBackupJob),
   and let one scheduled plan run happen.
   - Expect: the job reaches COMPLETED. In CloudTrail, `sts:AssumeRole` by `backup.amazonaws.com` on DbBackupRole
     succeeds.
   - If the job FAILS with an IAM/STS error: record the CloudTrail `AssumeRole` event in full, including any
     `errorCode`, and keep it as failure evidence. Do not edit the trust in place. Redeploy with
     `-c bankItLab:backupTrustMode=account-region-backup-arn` and repeat. If that also fails, redeploy with
     `source-account-only` and repeat. Each mode change is a recorded change, and `source-account-only` needs owner
     sign-off.
   - CloudTrail does not show which condition keys were evaluated. The success or failure of each mode is the
     evidence. Optionally, add a temporary **second** statement with `Null` checks to tell absent keys from wrong
     values. Remove it after the test.
   - Repeat V-2 for every operation that will use this role. Copy jobs and restore jobs are not configured in
     infra/aws-cdk today. If they are added, test them separately with their own roles.
3. **V-3 (permissions and naming):** confirm the RDS snapshot identifier starts with `awsbackup:job-` and that there
   are no AccessDenied events for `rds:*` or `kms:*` from the role. List the KMS calls on DatabaseKey and
   BackupVaultKey, with their `kms:ViaService` / `sourceIPAddress = *.amazonaws.com`, to decide on R-6.
4. **V-4 (negative):** pass `DbBackupRole` from a job in a different sandbox account, or point a second vault in the
   same account at it if testing `vault-arn`, and confirm AssumeRole is denied.
5. **V-5 (KMS separation):** as a principal with no key-admin role, call `kms:PutKeyPolicy`, `kms:CreateGrant`
   (without GrantIsForAWSResource), and `kms:Decrypt` (directly, not via a service) on BackupVaultKey, and confirm
   AccessDenied each time. As `BankItLabKmsKeyAdmin`, confirm `DescribeKey` and `GetKeyPolicy` succeed and
   `kms:Decrypt` is denied.
6. **V-6 (restore drill, separate role):** restore the recovery point to a new instance with a **separate** restore
   role (not DbBackupRole), then delete the restored instance. Record the RTO and confirm the backup role cannot
   restore.
7. **V-7 (monitoring):** confirm an EventBridge rule or Backup notification on `BACKUP_JOB_FAILED` / `EXPIRED`
   reaches an owner. This is required for R-1.
8. **Teardown:** remove the stack. Retained KMS keys, the vault, and log groups need manual cleanup through a
   recorded change. Schedule KMS key deletion with the 30-day window.

## Evidence to keep (per step)

The command or console action, a UTC timestamp, the CloudTrail event IDs, the job IDs, and the status. Never keep
credentials, account IDs in public artifacts, or snapshot data. Record the results in a new evidence directory. Do
not edit this one.

## Pass criteria for lifting EX-04 "deployment-blocking"

V-2 is COMPLETED in the chosen mode for every operation that uses the role, V-3 has no AccessDenied, V-4 is denied,
V-5 matches, V-7 alerts, and the owner approves the mode in writing.
