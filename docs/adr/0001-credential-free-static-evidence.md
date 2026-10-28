# 0001: Credential-free, environment-agnostic synthesis; static evidence only
- Status: **Proposed**. Source PRs #1, #5 and #6 are open drafts, none merged. #5 is integrated in #7 (open draft); #1 is superseded; #6 is not integrated.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Context
The lab must produce reviewable infrastructure evidence without AWS credentials, deployments or API calls.

## Decision (as implemented)
- Stacks set no `env`, and synth uses `--no-lookups`. The manifest reports `aws://unknown-account/unknown-region`.
  `bank-aws-001@e494bcf:infra/aws-cdk/bin/app.ts`; `aws-remediation-vpc-rds@099479e:infra/aws-cdk/bin/app.ts`; `orgs-security-refs@e5e7f46:infra/orgs/bin/app.ts`.
- Org IDs and account IDs are `CfnParameter`s with `AllowedPattern` (`orgs-security-refs@e5e7f46:infra/orgs/docs/adr/ADR-0001-credential-free-org-reference.md`).
- Wrappers unset credentials and disable IMDS: `bank-aws-001@e494bcf:evidence/aws/run-cmd.sh`, `orgs-security-refs@e5e7f46:evidence/orgs/run-cmd.sh`.
- CI: `permissions: contents: read`, `persist-credentials: false`, and a step that fails if credentials are present (`bank-aws-001@e494bcf:.github/workflows/bank-aws-001-cdk.yml`).

## Consequences
- Reproducible anywhere. This guide re-synthesized byte-identical templates (learning/execution E01, E10).
- No lookups or account literals. The `BootstrapVersion` parameter remains. Deployment is out of scope.
- Known weakness: PR #1's `run-cmd.sh` unsets only 7 variables while its header claims all `AWS_*` (`review/pr1-pr2-evidence-audit@fb36341:reports/review-pr1-pr2.md` §2).
- Conflict (historical): at `e610015`, #2's `postgres-restore-evidence.yml` set `CDK_DEFAULT_ACCOUNT=000000000000` in its cdk-synth job (PR #3 §5). This is resolved at `ci-evidence-postgres@e7399fb:.github/workflows/postgres-restore-evidence.yml`: its `cdk-synth` job has no `CDK_DEFAULT_*` (re-checked by grep).
