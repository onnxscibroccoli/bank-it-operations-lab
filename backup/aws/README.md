# backup/aws: AWS Backup DR reference (vault, plan, cross-region copy, Vault Lock, restore testing)

AWS CDK v2 (TypeScript) app that synthesizes two stacks **without AWS credentials**. Nothing here is deployed, no
backup/copy/restore job has ever run from it, and no AWS API was called to build it. Static evidence only
(`evidence/backup/aws-backup-dr/`). Not a certification.

Conventions follow `infra/aws-cdk` (branches `bank-aws-001` / `aws-remediation-vpc-rds`): CDK 2.275.0, cdk-nag 2.38.2
(AwsSolutions + NIST 800-53 R5 on the whole app), env-agnostic synth (`--no-lookups`, no `env`), customer-managed KMS keys
with explicit least-privilege key policies, `RETAIN` on stateful resources, suppressions only for registered exceptions.
Regions follow the orgs region-lock SCP reference: **us-east-1 primary, us-west-2 secondary**.

## Single source of truth
`config/backup-policy.json` holds names, regions, tag selection, vault-lock bounds, rules and copy retention.
`lib/policy.ts#validatePolicy` checks it against AWS Backup job-time constraints (cold storage >= 90 days before deletion,
continuous backup <= 35 days, retention inside the target vault's lock bounds, every rule copies cross-region, no
COMPLIANCE lock, naming). `bin/app.ts` refuses to synthesize if it has errors.

## Stacks
`BankItLabBackupDrVault` (intended region us-west-2; deploy first)
- `DrVaultKey`: CMK, rotation, RETAIN; crypto only via `backup` and `rds` in this account/region (RDS re-encrypts cross-region snapshot copies with the destination vault key).
- `DrCopyVault` `bank-it-lab-dr-copy-vault`: CMK, Vault Lock **GOVERNANCE** (min 30 / max 400 days), access policy denying recovery-point deletion, lifecycle changes, lock and policy changes to all but `OrgBreakGlass`.
- CloudFormation Rule `PinRegion`: deployment fails outside us-west-2.

`BankItLabBackupPrimary` (intended region us-east-1)
- `PrimaryVaultKey` + `PrimaryVault` `bank-it-lab-primary-vault`: same controls as the DR vault (crypto via `backup`).
- `bank-it-lab-backup-role` / `bank-it-lab-restore-role`: separate AWS Backup service roles, trust limited to `backup.amazonaws.com` with `aws:SourceAccount`, 1h sessions (exceptions BKP-EX-01/02).
- `bank-it-lab-standard-plan`:
  - `daily-35d-pitr`: 05:00 UTC, continuous backup (PITR) where supported, 35 days; copy to DR vault, 35 days.
  - `monthly-365d-cold`: 1st of month 06:00 UTC, cold after 90 days, delete at 365; copy to DR vault with the same lifecycle.
  - Selection `bank-it-lab-tagged`: every resource tagged `backup-plan=bank-it-lab-standard`.
- `bank_it_lab_monthly_restore_test`: AWS Backup restore testing plan (15th, 08:00 UTC, latest snapshot within 30 days) + RDS selection by the same tag, 24h validation window.
- CloudFormation Rule `PinRegion`: deployment fails outside us-east-1.

The DR vault ARN in copy actions is built from config (`arn:<partition>:backup:us-west-2:<account>:backup-vault:bank-it-lab-dr-copy-vault`),
so the primary stack has no cross-region stack reference (ADR-0002).

## Commands (Node 20)
    npm ci
    npx tsc --noEmit
    npm test                      # config, stack, and negative-control tests
    npm run validate-config       # JSON findings for config/backup-policy.json
    npx cdk synth --no-lookups --no-version-reporting --path-metadata false --quiet

For logged, credential-free runs use `../../evidence/backup/aws-backup-dr/run-cmd.sh <logname> <command...>` from this directory.

## Docs
Runbooks and design notes: `docs/runbooks/aws-backup/` (prerequisites, retention/deletion, restore validation, RTO/RPO,
cost & capacity). ADRs: `docs/adr/`.

## Known gaps
See `docs/runbooks/aws-backup/README.md#gaps`.
