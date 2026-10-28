# Execution log: what was actually run while writing this guide

- **When:** 2026-10-28, about 13:35-14:15 EDT (America/New_York).
- **Where:** a Linux box with Node v20.19.2, npm 11.21.1 and Python 3.13.5. No PostgreSQL binaries. No AWS CLI or credentials.
- **How:** read-only clone of `https://github.com/onnxscibroccoli/bank-it-operations-lab`, with one detached `git worktree` per PR branch at the SHAs in `learning/README.md`.
  CDK commands ran with `AWS_*` and `CDK_DEFAULT_*` unset, config and credentials files set to `/dev/null`, and IMDS disabled.
- **Non-destructive:** nothing was deployed, and no AWS or Graph API was called. All mutations were in `/tmp` copies or an uncommitted
  worktree change that was reverted (`git status` clean afterwards). No PR branch was modified or pushed.
- The box was heavily loaded (load average about 40, shared with other jobs), so the durations below are not representative.

| ID | Exercise | Command (abridged) | Exit | Real output (excerpt) |
|---|---|---|---|---|
| E01 | PR #1 build and test | `npm ci`, `npx tsc --noEmit`, `npm test`, `npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --no-asset-metadata --quiet` in `bank-aws-001@e494bcf:infra/aws-cdk` | 0/0/0/0 | `Test Suites: 2 passed` `Tests: 21 passed, 21 total`. Template `cmp` identical to `evidence/aws/synth/`. NagReport `rows=11 nc=0 sup=0` |
| E01 | PR #5 build and test | same, in `aws-remediation-vpc-rds@099479e:infra/aws-cdk` | 0/0/0/0 | `Test Suites: 3 passed` `Tests: 33 passed, 33 total` (tsc took 1353 s under load). AwsSolutions NetworkDatabase rows=28 nc=0 sup=2; AwsSolutions SecureStorage 11/0/0; NIST NetworkDatabase 53/0/0; NIST SecureStorage 19/0/3. All 4 CSVs identical to committed. SecureStorage template identical. NetworkDatabase template differs only by `"Metadata": {"aws:asset:path": …, "aws:asset:property": "Code"}`, because the committed synth (`logs/09-pass3-cdk-synth.log`) did not pass `--no-asset-metadata` |
| E02 | PR #1 evidence validator | `npm run -s validate:evidence` | 0 | `checked 18 files` `EVIDENCE VALID` |
| E02 | Hash checks | `sha256sum -c` on PR #1 `evidence/aws/SHA256SUMS`, PR #5 bundle `SHA256SUMS`, PR #6 `evidence/orgs/SHA256SUMS` (from repo root) | 0/0/0 | `HASHES OK: 87 entries verified` (PR #1); `HASHES OK: 32 entries verified` (PR #5); PR #6 66 entries OK. Note: running PR #6's file from inside `evidence/orgs/` fails, because its paths are repo-relative |
| E02 | PR #1 command log | `validate_evidence.py commands evidence/aws/logs/COMMANDS.tsv --format aws-3col` | 0 | `COMMANDS OK: 48 rows cross-checked` |
| E03 | PR #3 unit tests | `python3 -m unittest discover -s evidence/shared/tests` | 0 | `Ran 13 tests … OK` |
| E03 | PR #1 self-logging | `validate_evidence.py cfn-s3-selflog bank-aws-001:evidence/aws/synth/BankItLabSecureStorage.template.json` | 1 | `ERROR AccessLogsBucket83982689: server access logs delivered to itself (prefix 'self-access-logs/')` `INVALID (1 errors, 0 warnings)` |
| E04 | PR #5 self-logging (clean, then injected) | `cfn-s3-selflog` on the PR #5 template; then `learning/exercises/inject-s3-selflog.py` → `cfn-s3-selflog` | 0, then 1 | `S3 LOGGING OK: 2 buckets checked, none log to themselves`, then `ERROR AccessLogsBucket83982689 … infinite loop of logs` |
| E05 | Credential guard (CI step logic) | `AWS_ACCESS_KEY_ID=AKIAFAKEFAKEFAKE0000 bash -c '<assert step>'` | 1 | `AWS credentials present; refusing to continue` |
| E06 | Evidence tamper | `/tmp` copy of the PR #5 bundle, `PROPOSED`→`APPROVED` in SECURITY_EXCEPTIONS.md, `sha256sum -c` and `validate_evidence.py hashes` | 1/1 | `./SECURITY_EXCEPTIONS.md: FAILED`; `ERROR …SHA256SUMS:4: sha256 mismatch for ./SECURITY_EXCEPTIONS.md` |
| E07 | Control break (PR #1) | `secure-storage-stack.ts:42` `BLOCK_ALL`→`BLOCK_ACLS`, `npx jest --ci --verbose`, then `git checkout -- lib/` | 1, then clean | `Tests: 4 failed, 17 passed, 21 total`. Failed: `cdk-nag AwsSolutions: zero errors`, `data bucket: SSE-KMS with CMK, BPA, versioning, access logs`, `every bucket has public access fully blocked and versioning`, `committed evidence bundle › validates cleanly` |
| E08 | Entra validator | `python3 -m unittest discover -s tests/entra`; `ca_validator.py`; `make_fixtures.py --check` | 0/0/0 | `Ran 25 tests … OK`; all 13 rules PASS (e.g. `BASE-007 … PASS`) |
| E08 | Entra negatives | `ca_validator.py` on `neg-mfa-or-bypass`, `neg-break-glass-not-excluded`, `malformed-duplicate-key` | 1/1/2 | `BASE-003 … FAIL`; `BASE-001 … FAIL`; `SCHEMA-001 … FAIL` + `BASE-00x … NOT_EVALUATED` |
| E08 | Entra injection | CA002 `state`→`enabledForReportingButNotEnforced` in a `/tmp` copy | 1 | `overall=FAIL exit=1`, `BASE-003 … FAIL` |
| E09 | Entra evidence | `generate_evidence.py --verify evidence/entra/runs/local-offline-20261028T150359Z` | 0 | `verify …: OK` |
| E09 | Risk policy enforced | `ca_validator.py tests/entra/fixtures/neg-risk-enforced.json` | 1 | `BASE-007 … FAIL` |
| E09 | Fixture drift (scratch copy) | edit `neg-missing-mfa.json`, `make_fixtures.py --check`, regenerate, `--check` | 1, then 0 | `fixture drift: ['neg-missing-mfa.json']` |
| E09 | Input changed after evidence (scratch copy) | edit CA001 displayName, `generate_evidence.py --verify …` | 1 | `input changed since evidence run: identity/entra/policies/CA001-Block-Legacy-Authentication-All-Users.json` `FAIL (1)`. Side effect: `make_fixtures.py` `KeyError: 'CA001'` |
| E10 | PR #6 build and test | `npm ci`, `tsc`, `npm test`, synth, `bash scripts/nag-gate.sh` in `orgs-security-refs@e5e7f46:infra/orgs` | 0/0/0/0/0 | `Test Suites: 4 passed` `Tests: 49 passed, 49 total`. 3 templates identical to `evidence/orgs/synth/`. `CloudTrail rows=14 non_compliant=0 suppressed=0`; Governance 0/0/0; SecurityServices 0/0/0; `total_non_compliant_or_suppressed=0` |
| E10 | SCP lint | `npx ts-node scripts/lint-policies.ts` | 0 | `protect-security-services: 1891/5120 chars, 0 findings` … `errors=0 warnings=0` (no tracked file changed) |
| E11 | SCP evaluator and lint injection | `learning/exercises/scp-region-lock.ts` (scratch copy in `infra/orgs`, deleted afterwards) | 0 | `ec2:RunInstances in eu-west-1: DenyOutsideAllowedRegions` / `in us-east-1: not denied` / `as OrgBreakGlass: not denied` / `NOT_DENY … only Effect=Deny statements allowed` |
| E12 | parliament gate | parliament 1.6.4 in a venv (setuptools 80.10.2); `scripts/parliament.sh gated` | 1, then 0 | First run: `json.decoder.JSONDecodeError: Expecting value` (the `pkg_resources` UserWarning entered stdout under `script(1)`). With `PYTHONWARNINGS=ignore`: 2 × `ALLOWLISTED UNKNOWN_CONDITION_FOR_ACTION`, `unallowlisted_findings=0` |
| E13 | Postgres evidence | `verify_evidence.sh runs/local-offline-20261028T041038Z`; `validate_evidence.py hashes` on that run; `postgres-negatives` on both committed runs | 0/0/0/1 | `positive=11 negative=6 failed=0`; `HASHES OK: 39 entries verified`; `NEGATIVES OK: 6 …`; failing CI run: 4 × `ERROR FALSE-PASS` (N01, N04, N05, N06) |
| E13 | Negative-text injection | `/tmp` copy of the offline run, N03 log `does not exist`→`is missing`, `postgres-negatives` | 1 | `ERROR FALSE-PASS N03_restore_missing_database …` |
| E14 | RDS resilience extraction | python over `BankItLabNetworkDatabase.template.json`; `grep -i deletionprotection lib/guards.ts test/*.ts` | 0 | `{'MultiAZ': True, 'DeletionProtection': True, 'BackupRetentionPeriod': 14, 'StorageEncrypted': True, 'PubliclyAccessible': False, 'Port': '5433'} Retain Retain`; BackupPlan `daily-35d` `cron(0 5 * * ? *)` `DeleteAfterDays: 35`; only hit `test/network-database-stack.test.ts:46` |

## Attempted, failed for environment reasons
- `sudo apt-get install postgresql` failed: `apt rc=100`, `Failed to fetch http://deb.debian.org/debian/dists/trixie/InRelease 500 Internal Server Error`.
- `pip install postgresql-wheel` failed: `No matching distribution found` (Python 3.13).
- So `run_restore_scenario.sh offline|service` was **not** run (see PENDING P-W7).
