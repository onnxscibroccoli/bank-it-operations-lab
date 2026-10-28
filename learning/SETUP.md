# Setup and prerequisites

## Tools
| Tool | Version used by the lab | Needed for | Source of truth |
|---|---|---|---|
| Node.js | 20 (CI `node-version: 20`; `engines.node >=20`) | weeks 1-3, 6, 10-12 | `bank-aws-001@e494bcf:.github/workflows/bank-aws-001-cdk.yml`, `infra/aws-cdk/package.json` |
| npm | any version shipped with Node 20 (`npm ci` with the committed lockfile) | same | `infra/aws-cdk/package-lock.json`, `infra/orgs/package-lock.json` |
| aws-cdk-lib / aws-cdk CLI / cdk-nag | 2.275.0 / 2.1146.1 / 2.38.2 (exact pins) | same | `package.json` on PR #1, #5 and #6 |
| Python 3 (stdlib only) | 3.x | weeks 2, 4-5, 8, 12 | `identity/entra/ca_validator.py`, `evidence/shared/validate_evidence.py` |
| PostgreSQL server and client binaries (`initdb`, `pg_ctl`, `pg_dump`, `pg_restore`, `psql`) | client major must equal server major | week 7 | `ci-evidence-postgres@e610015:tests/integration/postgres/run_restore_scenario.sh` (`client_server_major_match`) |
| parliament (optional) | 1.6.4 with `setuptools<81` | week 6 | `orgs-security-refs@e5e7f46:infra/orgs/scripts/parliament.sh` |

No AWS account, AWS CLI, Entra tenant or credentials are needed. **Do not configure any.**

## Check out every branch side by side
```bash
git clone https://github.com/onnxscibroccoli/bank-it-operations-lab.git lab && cd lab
for b in bank-aws-001 ci-evidence-postgres review/pr1-pr2-evidence-audit entra-ca-offline aws-remediation-vpc-rds orgs-security-refs; do
  git worktree add --detach "../wt-${b//\//-}" "origin/$b"
done
# optional: make accidental pushes impossible from this clone
git remote set-url --push origin DISABLED
```
The weeks refer to these worktrees as `$PR1` … `$PR6`:
```bash
export LAB=$PWD PR1=$PWD/../wt-bank-aws-001 PR2=$PWD/../wt-ci-evidence-postgres PR3=$PWD/../wt-review-pr1-pr2-evidence-audit \
       PR4=$PWD/../wt-entra-ca-offline PR5=$PWD/../wt-aws-remediation-vpc-rds PR6=$PWD/../wt-orgs-security-refs
```
(The paths are absolute, so they keep working after you `cd`. Run this block from the clone root.)

## Credential-free shell
`learning/exercises/no-aws-env.sh <command…>` unsets the common AWS and CDK variables, points the config and
credentials files at `/dev/null`, and disables IMDS before running the command. The same approach is used by
`bank-aws-001@e494bcf:evidence/aws/run-cmd.sh` and `orgs-security-refs@e5e7f46:evidence/orgs/run-cmd.sh`.
The repo's wrappers also write evidence logs, so use the helper for practice runs.

Note (from PR #3, `reports/review-pr1-pr2.md` §2): PR #1's `run-cmd.sh` header claims "AWS_* and CDK_DEFAULT_* unset",
but it unsets only 7 named variables. The helper here also unsets `AWS_ROLE_ARN`, `AWS_WEB_IDENTITY_TOKEN_FILE`
and `AWS_CONTAINER_CREDENTIALS_*`.
