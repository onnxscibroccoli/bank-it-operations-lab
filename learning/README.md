# Bank IT operations lab: twelve-week learning guide

This guide teaches from what the repository **actually delivers**. Every capability it uses is cited to a file
on a branch, at an exact commit. Nothing here deploys anything, calls an AWS or Microsoft Graph API, or uses
credentials.

> **Important: almost nothing is on `main` yet.** At the time of writing, `main` (`7f50348`) contains only
> `README.md`. All delivered work lives on six **open, draft, unmerged** pull requests. Each week below tells you
> which branch to check out. If a PR is later changed or merged, re-check the cited paths against the SHA listed here.

| PR | Branch | Head SHA | What it delivers |
|---|---|---|---|
| [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) | `bank-aws-001` | `e494bcf` | `infra/aws-cdk`: S3 + KMS secure storage stack, Jest, cdk-nag AwsSolutions, evidence validator, CI workflow `bank-aws-001-cdk.yml`, ADR-0001..0003 |
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | `ci-evidence-postgres` | `e610015` | `tests/integration/postgres`: pg_dump/pg_restore exercise with 11 positive and 6 negative steps, evidence runs, CI workflow `postgres-restore-evidence.yml` |
| [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) | `review/pr1-pr2-evidence-audit` | `fb36341` | `reports/review-pr1-pr2.md` audit, `evidence/shared/validate_evidence.py` (5 subcommands) and 13 unit tests |
| [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) | `entra-ca-offline` | `d302c99` | `identity/entra`: 7 synthetic Conditional Access policies, a fail-closed validator (13 rules), 37 fixtures, 25 unit tests, evidence generator |
| [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) | `aws-remediation-vpc-rds` | `099479e` | `infra/aws-cdk` remediated: S3 self-logging removed, private VPC + private RDS PostgreSQL, NIST 800-53 R5 pack, static guards, 33 Jest tests, exception register, ADR-0004 |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | `orgs-security-refs` | `e5e7f46` | `infra/orgs`: OU layout, 7 SCPs, org CloudTrail, GuardDuty, Security Hub, an offline SCP linter and evaluator, parliament gate, 49 Jest tests, ADR-0001..0003 |

Citation format used throughout: `` `<branch>@<sha7>:<path>` ``.

## Layout
- `INVENTORY.md`: what is real, what is partial, and what is absent (including things you might expect but that do not exist).
- `SETUP.md`: prerequisites and how to check out every branch side by side with `git worktree`.
- `weeks/week-01.md` … `weeks/week-12.md`: the curriculum.
  - Weeks 1-3: AWS and IaC.
  - Weeks 4-6: identity and governance.
  - Weeks 7-9: resilience and incidents.
  - Weeks 10-12: architecture defense.
- `execution/EXECUTION_LOG.md`: what was **actually run** while writing this guide, with real output and exit codes.
- `execution/PENDING.md`: every exercise that was **not** executed, and why.
- `exercises/`: small scratch helpers used by the exercises. They never modify committed evidence.
- Architecture decision records (ADRs) are in `../docs/adr/`. Each one indexes a real decision in the delivered code.

## Each week has
Daily exercises (about 30-60 min), exact commands and prerequisites, expected observations, failure injection and
recovery, answer notes, architecture tradeoffs, a fifteen-minute walkthrough script, interview questions, and an
explicit **PENDING / UNEXECUTED** section.

## Ground rules for learners
1. Run everything credential-free. Use the repo's own wrappers (`evidence/aws/run-cmd.sh`, `evidence/orgs/run-cmd.sh`)
   or `exercises/no-aws-env.sh`.
2. Do failure injection only in a scratch copy (`/tmp/...`) or in an uncommitted working tree that you reset with
   `git checkout -- .`. Never commit a mutated evidence bundle.
3. If a cited file is missing on your checkout, that is a finding. Do not invent the content.
