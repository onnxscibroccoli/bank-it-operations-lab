# ADR-0001: Credential-free, parameterised Organizations reference stacks

- Status: Accepted
- Date: 2026-10-28

## Context
The lab needs organization-level security guard rails as reviewable code and evidence. It must never deploy, never use
AWS credentials, and only touch `infra/orgs/**` and `evidence/orgs/**`.

## Decision
- TypeScript CDK in its own package (`infra/orgs`), with the same pins and conventions as `infra/aws-cdk`
  (Jest + `aws-cdk-lib/assertions`, cdk-nag 2.x `AwsSolutionsChecks` via Aspects, env-agnostic stacks).
- SCPs are plain typed JSON documents (`lib/scps.ts`), so the same source feeds the CDK `AWS::Organizations::Policy`
  resources, the exported JSON in `evidence/orgs/policies/`, and the linters. Tests assert that the synthesized `Content`
  matches the source exactly.
- Org root id, organization id and the Security Tooling account id are `CfnParameter`s with `AllowedPattern`.
  No lookups, no hard-coded account ids (checked by evidence log 15).
- Evidence commands run through `evidence/orgs/run-cmd.sh`, which unsets `AWS_*`/`CDK_DEFAULT_*`, points the AWS config
  and credentials files at `/dev/null` and disables IMDS.

## Consequences
- Reproducible anywhere. No CI workflow was added, because `.github/**` is outside this change's allowed paths.
  The evidence README lists the commands a workflow would run.
- The default synthesizer still emits the BootstrapVersion parameter and rule. Deploying is out of scope.
