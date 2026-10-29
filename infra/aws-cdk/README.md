# infra/aws-cdk: BANK-AWS-001 secure storage stack

AWS CDK v2 (TypeScript) app that synthesizes `BankItLabSecureStorage` **without AWS credentials**. Nothing here is
deployed; outputs are static evidence only (see `evidence/aws/aws-remediation-vpc-rds/`). Not a certification.

## Stacks
`BankItLabSecureStorage`
- `DataKey`: customer-managed KMS key, rotation, RETAIN, least-privilege key policy (root = admin only; crypto only via S3).
- `DataBucket`: SSE-KMS (DataKey, Bucket Key), BPA all, TLS-only, versioned, ACLs disabled, access logs -> `AccessLogsBucket/data-bucket/`.
- `AccessLogsBucket`: SSE-S3 (ADR-0002), same controls, terminal log sink with **no** self-logging (ADR-0004).

`BankItLabNetworkDatabase`
- VPC 10.40.0.0/16, 2 AZs, PRIVATE_ISOLATED `app` + `db` subnets only (no IGW/NAT/routes), default SG restricted, flow logs (ALL) to a KMS log group.
- RDS PostgreSQL 17: `publiclyAccessible: false`, `db` isolated subnets, storage/PI/secret encrypted with `DatabaseKey` (CMK), Multi-AZ,
  deletion protection, 14-day backups + AWS Backup plan (CMK vault), IAM auth, `rds.force_ssl=1`, log exports, enhanced monitoring, port 5433,
  secret rotation every 30 days via a Secrets Manager interface endpoint.
- SGs: DB ingress only from app SG and rotation SG on 5433; no 0.0.0.0/0 anywhere.

cdk-nag: `AwsSolutionsChecks` + `NIST80053R5Checks` on the whole app. Suppressions only for registered exceptions
EX-01..EX-04 (`evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md`). Static guards in `lib/guards.ts`.

## Commands (Node 20)
    npm ci
    npx tsc --noEmit
    npm test                      # stack assertions + negative controls
    npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --no-asset-metadata --quiet

For logged, credential-free runs use `../../evidence/aws/aws-remediation-vpc-rds/run-cmd.sh <logname> <command...>`.

## Layout
- `bin/app.ts`: app entry, applies both cdk-nag packs. `lib/secure-storage-stack.ts`, `lib/network-database-stack.ts`: the stacks.
- `lib/least-privilege-key.ts`: CMK factory with explicit key policy. `lib/guards.ts`: static template guards.
- `lib/lab-context.ts`: feature flags shared with tests. `test/`: Jest tests incl. `negative-controls.test.ts`. `docs/adr/`: ADR-0001..0004.
- CI: `.github/workflows/aws-cdk.yml` (added at integration; adapted from PR #1's `bank-aws-001-cdk.yml`).
- PR #1 (`bank-aws-001`) is **superseded** by PR #5. Its S3 self-logging design was removed (ADR-0004), and only its CI workflow was carried over. PR #1 is still open; closing it is user action UA-4.

## Known gaps
Default `BootstrapVersion` parameter/rule; cdk-nag 2.x pin; proposed exceptions EX-01..EX-04; hosted rotation uses a SAR application.

## Deployment blocker: Backup trust context (EX-04)

The narrowed DbBackupRole/DbBackupPolicy is statically checked only. The configured vault `aws:SourceArn` and account context during `backup.amazonaws.com` service-role AssumeRole have not been established by service-role-specific documentation or a sandbox run. AWS's Backup confused-deputy page describes vault context for SNS publishing and storage KMS policies; it is not evidence that this exact role assumption supplies those keys. Retain the restrictive draft and mark deployment blocked pending that evidence, rather than presenting a passing template assertion as proof it can run. No owner exception approval or live backup success is claimed.

Source: https://docs.aws.amazon.com/aws-backup/latest/devguide/cross-service-confused-deputy-prevention.html
