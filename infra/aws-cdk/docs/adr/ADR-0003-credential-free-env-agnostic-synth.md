# ADR-0003: Credential-free synthesis of an environment-agnostic stack

- Status: Accepted
- Date: 2026-10-28
- Task: BANK-AWS-001

## Context
BANK-AWS-001 is a lab task: produce reviewable static evidence without AWS credentials, deployments or AWS API calls.

## Decision
- The stack sets no `env` (no account/region) and performs no context lookups; the cloud assembly reports
  `aws://unknown-account/unknown-region`.
- All local commands run through `evidence/aws/run-cmd.sh`, which unsets `AWS_*`/`CDK_DEFAULT_*`, points the AWS
  config and credentials files at `/dev/null` and disables IMDS.
- Synth uses `cdk synth --no-lookups --no-version-reporting --no-path-metadata --no-asset-metadata --quiet`.
- CI (`.github/workflows/bank-aws-001-cdk.yml`) mirrors this: `permissions: contents: read`, no secrets, checkout
  without persisted credentials, an explicit step that fails if AWS credential variables are present.

## Consequences
- Output is reproducible anywhere and safe to run on PRs from any branch.
- Account/region-specific constructs (lookups, `Stack.of(this).account` literals, cross-region refs) cannot be used.
- The default synthesizer still emits the `BootstrapVersion` parameter and rule; deployment would require a
  bootstrapped account and is out of scope. Static evidence is not a deployment record or certification.
