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

# Run 2: reconciliation (2026-10-28, about 14:15-14:35 EDT)
- **Where:** the same box. PostgreSQL 16.15 server and client came from conda-forge via micromamba into a private prefix (`learning/SETUP.md`). No credentials, and `AWS_*`/`CDK_*`/`GH_*` were unset per command.
- **Heads:** as in `learning/README.md` (re-fetched at 14:24 EDT, R15).
  R04 and R05 ran on `overnight/integration@afb4127`. `49122f2` changes only `coordination/tasks.json` and `reports/INTEGRATION.md` (checked with `git diff --stat`), so the results carry over.
- **Non-destructive:** all mutations were in `/tmp` copies. Local runs written inside a worktree (the Postgres self-test, the incident demo) were moved out afterwards. No PR branch was modified.

| ID | Exercise | Command (abridged) | Exit | Real output (excerpt) |
|---|---|---|---|---|
| R01 | #2 harness v2, fresh offline run + verifier | `EVIDENCE_DIR=/tmp/r2-pg bash tests/integration/postgres/run_restore_scenario.sh offline`; `verify_evidence.py --require-artifacts /tmp/r2-pg` at `e7399fb` | 0, 0 | `overall=PASS passed=38/38 failed=0 errors=0 not_run=0`; `cases=38 positive=11 negative=6 rows=38 problems=0 -> VERIFIED` |
| R01b | Forged log (first line of `01_S00` log) | `verify_evidence.py /tmp/r2-pg-forged` | 1 | `ERROR hash: mismatch: logs/01_S00_required_tools.log`; `problems=1 -> REJECTED` |
| R01c | Forged N04 reason | `23503` and fkey name replaced in `30_N04_…log`; verify | 1 | `ERROR hash: mismatch …`, `ERROR N04_fk_enforced_after_restore: reason_regex not found …`, `problems=2 -> REJECTED` |
| R02 | #2 harness self-test | `selftest_harness.sh` | 0 | `assertions=26 failed=0`, including `C.verifier_rejects_forged_pass expected=1 actual=1` |
| R03 | Shared checker on a v2 run: #3 versus #7 | `validate_evidence.py postgres-negatives /tmp/r2-pg` from `fb36341`, then from #7 | 0, 0 | #3: `NEGATIVES OK: 0 negative steps …` (vacuous); #7: `NEGATIVES OK: 6 negative steps failed for the intended reason` |
| R04 | #7 integration, Python subset | `scripts/validate-all.sh --python-only` | 0 | `validate-all: PASS (20 steps)` |
| R05 | #7 integration, full | `PG_BIN=… scripts/validate-all.sh` | 0 | `validate-all: PASS (32 steps)`; includes `ci-offline-40741329107-1: cases=38 … VERIFIED`, `ci-service-40741329107-1: cases=36 … VERIFIED`, shared tests `Ran 15 tests` |
| R06 | #6 self-logging and exempt roles | `cfn-s3-selflog evidence/orgs/synth/BankItLabOrgCloudTrail.template.json`; `sed -n 50p org-cloudtrail-stack.ts`; `grep iam: scps.ts` | 1 (selflog) | `ERROR TrailAccessLogsBucket30C0D746: server access logs delivered to itself (prefix 'self-access-logs/')`, `INVALID (1 errors, 0 warnings)`; line 50 `serverAccessLogsPrefix: 'self-access-logs/'`; `EXEMPT_ROLE_ARNS` in `lab-context.ts:13`; `iam:` appears only in the line-32 NotAction and the line-47 root condition |
| R07 | #5 key-admin statements | Python over both `synth/*.template.json` | 0 | `LogsKeyA6AB43B2`, `DatabaseKey7576F140`, `DataKey17AFBB84`: `KeyAdministrationByAccountRoot ['kms:Create*', 'kms:Put*'] False` (no Condition) |
| R08 | CA007 disabled (copy in `/tmp`) | `ca_validator.py policies --quiet` | 0 | `overall=PASS exit=0` (the gap) |
| R09 | #10 observability | unit tests; `run_healthcheck.py evaluate` on 3 fixtures; evidence `--verify` | 0; 0/1/2; 0 | `Ran 64 tests … OK`; `healthy rc=0 {'http_status': 200, 'serve': True}`, `stale rc=1 {503, False}` (`stale: age 3660s > max_age_s 300`), `malformed-nan rc=2 {503, False}` (`non-finite number NaN not allowed`); `VERIFY PASS` |
| R10 | #17 patching and hardening | `inspect_patch_manifest.py … --plan`; 2 test suites; `make_fixtures.py --check`; evidence verify | 0 | `canary Install … concurrency=1 errors=0 soak=48h`, `wave1 … 10% errors=5% … approvers=service-owner,change-advisory-board`, `wave2 … 25% … soak=24h`, `overall: PASS`; `Ran 9 tests` OK, `Ran 18 tests` OK; `fixture drift: none`; `PASS (113 inputs)` |
| R11 | #18 identity governance | unit tests; `make_fixtures.py --check`; evidence verify | 0 | `Ran 65 tests … OK`; `fixtures OK (37 files)`; `verify …local-offline-20261028T181435Z: OK` |
| R12 | #9 vendor mock (at `88a3785`, then re-run at `d6efb82`) | plain `discover`; documented `-s tests -t .`; governance tests and lint; evidence verify | 1; 0; 0 | plain: `ModuleNotFoundError: No module named 'tests'`; documented: `Ran 45 tests … OK`; at `d6efb82`: `Ran 25 tests` OK, `SIMULATION governance lint: PASS (0 findings)`, `SIMULATION verify: PASS` (`local-offline-20261028T181549Z`) |
| R13 | #16 control mapping | `validate_mapping.py`; unit tests | 0 | `rows=17 artifacts=97 NOT_EXECUTED=1 OBSERVED=0 SIMULATION=14 STATIC=2`, `MAPPING VALID`; `Ran 10 tests` OK |
| R14 | CI status at heads | `gh api …/commits/<sha>/check-runs` | n/a | #2 `e7399fb` success=10; #7 `49122f2` success=8; #15, #19-#22: no check runs |
| R15 | PR re-fetch | `gh pr list --state all` at 14:24 EDT | n/a | 22 PRs, all OPEN drafts, `mergedAt` null; `main` = `7f50348` |
| R16 | Citation re-verification | see "Citation check" below | 0 | see below |
| R17 | #21 backup-dr-aws | `npm ci --ignore-scripts`, `tsc`, `npm test`, `validate-config`, `cdk synth --no-lookups`; drift diff; nag CSVs; `sha256sum -c` from the repo root; `validate_backup_evidence.py`; 2 cost/evidence test suites; config injections in `/tmp` | 0 (all); injections 1, 1 | `Tests: 46 passed, 46 total`; `errors: 0, warnings: 2`; both templates `drift=none`; 4 NagReports `noncompliant=0`; `S3 LOGGING OK: 0 buckets`; `{"ok": true}`; `Ran 8 tests` OK twice. COMPLIANCE gives `LOCK_GRACE`, `LOCK_COMPLIANCE_IN_LAB`; same region gives `SAME_REGION_COPY`. `DrVaultKeyE3D6C377` and `PrimaryVaultKey22F77B03`: `KeyAdministrationByAccountRoot ['kms:Create*', 'kms:Put*'] False` |
| R18 | #22 incident demo (SIMULATION) | `PG_BIN=… run_incident_demo.sh`; `selftest.sh`; `timeline.py --verify`; tampered `mttr_s` | 0; 0; 0; 1 | `status: PASS`, `steps_total: 19`, `mttd_s: 3.596`, `mttr_s: 8.52`, `polls_unhealthy: 1`; `SIMULATION selftest: 0 failure(s)`; `VERIFY PASS`; tampered: `VERIFY FAIL: SUMMARY.json metrics do not match values re-derived …`, `hash mismatch: SUMMARY.json` |
| R19 | #20 M365 / endpoint | `m365_ops.py --quiet`; unit tests; 2 negative fixtures; evidence verify | 0; 0; 2, 1; 0 | `overall=PASS scenarios=13 passed=13 failed=0 plannedSteps=43 mutationsExecuted=0`; `Ran 29 tests` OK; `MALFORMED SYN-002 … 'contoso.com' is not a synthetic tenant domain`; `overall=FAIL scenarios=1 … failed=1`; `verify …: OK` |
| R20 | #19 hybrid runbook validator | `check_hybrid_runbooks.py`; unit tests; `EXECUTED` banner injected into a `/tmp` copy | 0; 0; 1 | `checked 12 files, 0 findings`; `Ran 10 tests` OK; `FAIL: …dns.md: missing 'Execution status: NOT_EXECUTED' banner …`, `claims execution status EXECUTED outside code`, `2 findings` |
| R21 | #2 verifier trusts run-local expectations | N01 regex set to `.` in the `/tmp` copy's `EXPECTATIONS.tsv`; SHA256SUMS re-hashed; verify | 0 (the gap) | `problems=0 -> VERIFIED`; `ENVIRONMENT.txt sha256_expectations.tsv=70ec3354…` versus the run copy `66c06325…` |

## Citation check (R16)
`LAB_REPO=<clone with every origin/* branch fetched> python3 learning/exercises/check-citations.py`, run at 14:33 EDT after all Run 2 edits and before this section was written:
`pinned=98 bare=238 stale=0 bad=10`. A re-run now reports `bad=18`, because this section quotes the same 8 distinct tokens.
- All 98 `branch@sha:path` citations point at the **current** head of their branch, and each path exists at that SHA.
- The 10 flagged backtick spans were checked by hand. None is a missing file:
  - status labels and URL fragments: `ERROR/version_mismatch` ×2, `NOT_RUN/missing_test`, `unknown-account/unknown-region`
  - ranges or prefixes: `infra/orgs/docs/adr/ADR-0001..0003` ×2, `infra/aws-cdk/docs/adr/ADR-0002`, `docs/adr/0003`, `docs/adr/0006`
  - one module-relative ADR path: `docs/adr/ADR-0004-no-self-logging-log-sink.md`, which is `infra/aws-cdk/docs/adr/ADR-0004-no-self-logging-log-sink.md` on `aws-remediation-vpc-rds`
- Every bare 7-character SHA in the guide (29 distinct) resolves to a commit (`git cat-file -e <sha>^{commit}`).
- Historical `e610015` references remain only where they are explicitly labelled v1 or historical (week 7 header, week 8 timeline, ADR-0001, ADR-0009).
