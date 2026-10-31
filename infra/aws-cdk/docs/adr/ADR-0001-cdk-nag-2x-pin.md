# ADR-0001: Pin cdk-nag to the 2.x line (2.38.2)

- Status: Accepted
- Date: 2026-10-28
- Task: BANK-AWS-001

## Context
The BANK-AWS-001 brief requires cdk-nag `AwsSolutionsChecks` applied with
`Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true, reports: true }))`. In correction pass 1
(`evidence/aws/logs/CORRECTION-PASS-1.md`, logs 05/06/08) the latest cdk-nag 3.x was installed, which no longer
supports registration as an Aspect (3.x moved to `Validations.of(...).addPlugins`), so typecheck, tests and synth failed.

## Decision
Pin `cdk-nag` to exactly `2.38.2` (`--save-exact`), the latest 2.x at implementation time, and keep the Aspects API
named in the brief. `package-lock.json` is committed and CI uses `npm ci`.

## Consequences
- Matches the specified API; reports are written as `AwsSolutions-<stack>-NagReport.csv` in `cdk.out/`.
- 2.x will stop receiving new rules at some point. Moving to 3.x is a separate, reviewed change: new registration API,
  different report format, and the CI nag gate and evidence schema (`nag-zero-noncompliant`) must be updated together.
