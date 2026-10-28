# Setup and prerequisites

## Tools
| Tool | Version used by the lab | Needed for | Source of truth |
|---|---|---|---|
| Node.js | 20 (CI `node-version: 20`; `engines.node >=20`) | weeks 1-3, 6, 10-12 | `bank-aws-001@e494bcf:.github/workflows/bank-aws-001-cdk.yml`, `infra/aws-cdk/package.json` |
| npm | any version shipped with Node 20 (`npm ci` with the committed lockfile) | same | `infra/aws-cdk/package-lock.json`, `infra/orgs/package-lock.json` |
| aws-cdk-lib / aws-cdk CLI / cdk-nag | 2.275.0 / 2.1146.1 / 2.38.2 (exact pins) | same | `package.json` on PR #1, #5 and #6 |
| Python 3 (stdlib only) | 3.x | weeks 2, 4-5, 8, 12 | `identity/entra/ca_validator.py`, `evidence/shared/validate_evidence.py` |
| PostgreSQL server and client binaries (`initdb`, `pg_ctl`, `pg_dump`, `pg_restore`, `psql`, `createdb`, `dropdb`, `pg_isready`) | client major must equal server major | weeks 7-8, 12 | `ci-evidence-postgres@e7399fb:tests/integration/postgres/expectations.tsv` (`S00_required_tools`, `S04_client_server_major_match`) |
| parliament (optional) | 1.6.4 with `setuptools<81` | week 6 | `orgs-security-refs@e5e7f46:infra/orgs/scripts/parliament.sh` |

No AWS account, AWS CLI, Entra tenant or credentials are needed. **Do not configure any.**

## Check out every branch side by side
```bash
git clone https://github.com/onnxscibroccoli/bank-it-operations-lab.git lab && cd lab
for b in bank-aws-001 ci-evidence-postgres review/pr1-pr2-evidence-audit entra-ca-offline aws-remediation-vpc-rds orgs-security-refs \
         overnight/integration vendor-mock observability reports/final-report team-management review/pr3-pr6 \
         control-mapping patch-hardening identity-governance hybrid-operations m365-endpoint backup-dr-aws incident-demo; do
  git worktree add --detach "../wt-${b//\//-}" "origin/$b"
done
# optional: make accidental pushes impossible from this clone
git remote set-url --push origin DISABLED
```
The weeks refer to these worktrees as `$PR1` … `$PR22`:
```bash
export LAB=$PWD PR1=$PWD/../wt-bank-aws-001 PR2=$PWD/../wt-ci-evidence-postgres PR3=$PWD/../wt-review-pr1-pr2-evidence-audit \
       PR4=$PWD/../wt-entra-ca-offline PR5=$PWD/../wt-aws-remediation-vpc-rds PR6=$PWD/../wt-orgs-security-refs \
       PR7=$PWD/../wt-overnight-integration PR9=$PWD/../wt-vendor-mock PR10=$PWD/../wt-observability \
       PR11=$PWD/../wt-reports-final-report PR13=$PWD/../wt-team-management PR14=$PWD/../wt-review-pr3-pr6 \
       PR16=$PWD/../wt-control-mapping PR17=$PWD/../wt-patch-hardening PR18=$PWD/../wt-identity-governance \
       PR19=$PWD/../wt-hybrid-operations PR20=$PWD/../wt-m365-endpoint PR21=$PWD/../wt-backup-dr-aws PR22=$PWD/../wt-incident-demo
```
(The paths are absolute, so they keep working after you `cd`. Run this block from the clone root.)

`backup-dr-aws` (#21) needs Node 20 and `npm ci --ignore-scripts` in `backup/aws`. `incident-demo` (#22) needs PostgreSQL server binaries plus `libpq` (see below), `curl`, and free loopback ports 18099 and 55432.

## Credential-free shell
`learning/exercises/no-aws-env.sh <command…>` unsets the common AWS and CDK variables, points the config and
credentials files at `/dev/null`, and disables IMDS before running the command. The same approach is used by
`bank-aws-001@e494bcf:evidence/aws/run-cmd.sh` and `orgs-security-refs@e5e7f46:evidence/orgs/run-cmd.sh`.
The repo's wrappers also write evidence logs, so use the helper for practice runs.

Note (from PR #3, `reports/review-pr1-pr2.md` §2): PR #1's `run-cmd.sh` header claims "AWS_* and CDK_DEFAULT_* unset",
but it unsets only 7 named variables. The helper here also unsets `AWS_ROLE_ARN`, `AWS_WEB_IDENTITY_TOKEN_FILE`
and `AWS_CONTAINER_CREDENTIALS_*`.

## PostgreSQL without a system package (what this guide used)
The Debian mirror returned HTTP 500 on the guide-writing box, so PostgreSQL 16.15 came from conda-forge into a private prefix, without root or credentials:
```bash
mkdir -p ~/pg && cd ~/pg
curl -sSL https://micro.mamba.pm/api/micromamba/linux-64/latest -o mm.tar.bz2
python3 -c "import tarfile; tarfile.open('mm.tar.bz2').extract('bin/micromamba', '.')"   # no bzip2 binary needed
MAMBA_ROOT_PREFIX=$PWD/root ./bin/micromamba create -y -q -p $PWD/env -c conda-forge postgresql=16
export PG_BIN=$PWD/env/bin    # consumed by run_restore_scenario.sh and validate-all.sh
```
The same approach (conda-forge PG 16.15) is recorded for the committed `local-offline-v2-20261028T180208Z` run (`evidence/postgres/runs/INDEX.md` on #2) and in #7's `reports/INTEGRATION.md`.
