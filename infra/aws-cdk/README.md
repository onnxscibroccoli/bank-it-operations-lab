# infra/aws-cdk: BANK-AWS-001 secure storage stack

AWS CDK v2 (TypeScript) app that synthesizes `BankItLabSecureStorage` **without AWS credentials**. Nothing here is
deployed; outputs are static evidence only (see `evidence/aws/README.md`). Not a certification.

## Stack
- `DataKey`: customer-managed KMS key, rotation enabled, RETAIN.
- `DataBucket`: SSE-KMS (DataKey, S3 Bucket Key), Block Public Access all, TLS-only, versioned, ACLs disabled,
  server access logs to `AccessLogsBucket/data-bucket/`, RETAIN.
- `AccessLogsBucket`: SSE-S3 (see ADR-0002), same controls, self access logs, log delivery via bucket policy.
- cdk-nag `AwsSolutionsChecks` (2.x, see ADR-0001) on the whole app, no suppressions.

## Commands (Node 20)
    npm ci
    npx tsc --noEmit
    npm test                      # stack assertions + evidence validator tests
    npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --no-asset-metadata --quiet
    npm run validate:evidence     # validates evidence/aws against evidence/aws/evidence-schema.json

For logged, credential-free runs use `../../evidence/aws/run-cmd.sh <logname> <command...>`.

## Layout
- `bin/app.ts`: app entry, applies cdk-nag Aspect. `lib/secure-storage-stack.ts`: the stack.
- `lib/lab-context.ts`: feature flags shared with tests. `lib/evidence-validator.ts` + `scripts/validate-evidence.ts`: evidence checks.
- `test/`: Jest tests. `docs/adr/`: decisions (ADR-0001..0003).
- CI: `.github/workflows/bank-aws-001-cdk.yml` (typecheck, tests, synth, cdk-nag gate, SHA256SUMS).

## Known gaps
Default CDK KMS key policy (account root); default `BootstrapVersion` parameter/rule; cdk-nag 2.x pin.
