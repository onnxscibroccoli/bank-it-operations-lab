# evidence/aws/aws-remediation-backup-kms

Static, credential-free evidence for branch `aws-remediation-backup-kms` (based on `main@8e2df97`). Nothing was
deployed. No AWS credentials were present: `run-cmd.sh` unsets them and points the AWS config and credential files
at /dev/null. This is not a certification, and static checks do not prove runtime AWS behavior.

## Findings

| ID | Where | Finding | Action |
|---|---|---|---|
| F-01 | `backup/aws/lib/backup-key.ts` (PrimaryVaultKey, DrVaultKey) | `KeyAdministrationByAccountRoot` grants the **account root principal** (so any IAM principal in the account that its own policy allows) `kms:Create*`, `kms:Put*`, `kms:Update*`, `kms:Enable*`, `kms:Disable*`, `kms:Delete*`, `kms:Get*`, `kms:List*`, `kms:Revoke*`, `kms:Describe*`, Tag/Untag, Schedule/CancelKeyDeletion, with **no aws:PrincipalArn** condition and no `BypassPolicyLockoutSafetyCheck` guard. No wildcard principal and no `kms:*`. | Proposed patch only (owner: backup/aws). `proposed-backup-aws/backup-key.ts.patch` |
| F-02 | same | `kms:Create*` includes **kms:CreateGrant**, which bypasses the conditioned grant statement (no GrantIsForAWSResource, no ViaService), so an admin-path grant can hand out Decrypt. `kms:Put*` includes PutKeyPolicy. This mixes administration with operational delegation. | same |
| F-03 | `infra/aws-cdk` DbBackupPolicy | `kms:CreateGrant` sat in the same statement as Decrypt/GenerateDataKey, conditioned only on kms:ViaService (no `kms:GrantIsForAWSResource`). | **Fixed**: separate crypto and grant statements, CreateGrant requires GrantIsForAWSResource=true |
| F-04 | `infra/aws-cdk` BackupVault | The vault used **DatabaseKey**, shared with RDS storage, Performance Insights, and Secrets Manager. | **Fixed**: dedicated `BackupVaultKey` (via backup.<region> only) |
| F-05 | `infra/aws-cdk` DbBackupRole trust | `aws:SourceArn` = vault on sts:AssumeRole is undocumented by AWS Backup (RESEARCH_EX04.md). | **Kept** (not removed). Reviewed fallbacks added. EX-04 is **DEPLOYMENT-BLOCKING** |
| F-06 | `infra/aws-cdk` DbBackupPolicy | The snapshot scope was `snapshot:awsbackup-*`. AWS Backup names RDS snapshots `awsbackup:job-<id>`, and the AWS-managed policy uses `snapshot:awsbackup:*`. The old scope would likely have failed delete/modify at runtime. | **Fixed** to `snapshot:awsbackup:*` (EX-04 appliesTo updated) |
| F-07 | Vault keys (infra and backup/aws) | The AWS-documented `backup-storage.amazonaws.com` confused-deputy Deny was missing. | **Added** in infra, and included in the backup/aws proposal |
| F-08 | `infra/aws-cdk/lib/guards.ts` | The guard caught only `kms:Create*`/`kms:Put*`, so Delete*/Get*/Update*/... wildcards, admin/operational mixing, and identity-policy CreateGrant passed. | **Extended**: `kmsSeparation`, `iamKmsPermissions`, `backupRoleTrust` |
| F-09 | `backup/aws` service roles | Use AWS-managed backup/restore policies (BKP-EX-01/02). Trust has aws:SourceAccount only. | Not changed (owner: backup/aws). Noted in RESIDUAL_RISK R-2/R-5 |

## Layout

- `COMMANDS.tsv`: every logged command (UTC start, exit code, duration, log, cwd, command), including failures.
  `logs/`: full output of each command.
- `synth/`: final templates and manifest. `cdk-nag/`: AwsSolutions and NIST 800-53 R5 reports (0 Non-Compliant;
  only the registered EX-01 to EX-04 are suppressed). `jest-results.json`: 77/77.
- `synth-trust-modes/`: NetworkDatabase templates for the fallback trust modes (for the later runtime test).
- `proposed-backup-aws/`: the patch for `backup/aws/lib/backup-key.ts`, plus the templates and nag reports
  synthesized from a scratch copy with it applied. Not applied to the repo.
- `RESEARCH_EX04.md`, `RESIDUAL_RISK.md`, `VERIFICATION_PROCEDURE.md` (NOT_EXECUTED), `CORRECTION_PASSES.md`,
  `SECURITY_EXCEPTIONS_EX04_UPDATE.md`.
- Refreshed: `../aws-remediation-vpc-rds/{synth,cdk-nag,jest-results.json}`, so the CI synth-drift step tracks the
  new code. The previous outputs were moved unmodified to
  `../aws-remediation-vpc-rds/superseded/pre-backup-kms-8e2df97/`.
- `SHA256SUMS`: run `sha256sum -c SHA256SUMS` from this directory.
