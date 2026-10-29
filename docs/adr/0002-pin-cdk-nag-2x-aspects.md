# 0002: Pin cdk-nag 2.38.2 with the Aspects API; exact toolchain pins
- Status: **Proposed**. Source PRs #1, #5 and #6 are open drafts, none merged. The pins carried into #7 via #5.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Context
cdk-nag 3.x removed Aspect registration. Installing it broke typecheck, tests and synth (`bank-aws-001@e494bcf:evidence/aws/logs/CORRECTION-PASS-1.md`).

## Decision (as implemented)
- `cdk-nag 2.38.2`, `aws-cdk-lib 2.275.0`, `aws-cdk 2.1146.1`, `jest 30.5.2` and `typescript 5.9.3`, all exact, in
  `infra/aws-cdk/package.json` (PR #1, PR #5) and `infra/orgs/package.json` (PR #6). Lockfiles are committed, and CI uses `npm ci`.
- `Aspects.of(app).add(new AwsSolutionsChecks(...))`. PR #5 adds `NIST80053R5Checks` the same way (`aws-remediation-vpc-rds@099479e:infra/aws-cdk/bin/app.ts`).
- Module ADR: `bank-aws-001@e494bcf:infra/aws-cdk/docs/adr/ADR-0001-cdk-nag-2x-pin.md`.

## Consequences
- 2.x will stop receiving rules. Migrating to 3.x changes the registration API, the report format, the CI gate and the evidence schema together.
