# Inventory: what the lab actually delivers

Snapshot taken 2026-10-28 (America/New_York). Repo: https://github.com/onnxscibroccoli/bank-it-operations-lab (public, default branch `main`).

## Branches and PRs
- `main` @ `7f50348`: `README.md` only (2 lines). **No PR has been merged.**
- PRs #1-#6 are all **open drafts** targeting `main`. Branch heads are listed in `README.md`.
- No `learning/**` or top-level `docs/adr/**` content existed before this guide. Module ADRs exist inside
  `infra/aws-cdk/docs/adr/` (PR #1: ADR-0001..0003; PR #5 adds ADR-0004) and `infra/orgs/docs/adr/` (PR #6: ADR-0001..0003).

## Not delivered (absent on every branch at the SHAs above)
You might expect these from the lab's name or from earlier plans. They **do not exist** on any pushed branch:
- `backup/aws/**`: no AWS Backup module directory. AWS Backup exists only as resources inside
  `aws-remediation-vpc-rds@099479e:infra/aws-cdk/lib/network-database-stack.ts` (BackupVault, BackupPlan, BackupSelection).
- `docs/runbooks/**`: no runbooks.
- `evidence/backup/**`: no backup evidence bundle.
- No deployment, no CDK bootstrap, no AWS account or tenant state. No IAM Access Analyzer, policy simulator or Graph runs.
- No CI workflow for `infra/orgs` (PR #6) or for `identity/entra` (PR #4). Both state this themselves.

## Real (code plus tests that run offline and pass; re-executed for this guide)
| Capability | Files | Re-run result here |
|---|---|---|
| Credential-free CDK synth of an S3 + KMS secure storage stack | `bank-aws-001@e494bcf:infra/aws-cdk/{bin/app.ts,lib/secure-storage-stack.ts}` | tsc 0, Jest 21/21, synth 0, template byte-identical to `evidence/aws/synth/`, nag 11 rows / 0 non-compliant |
| Evidence-bundle validator (TypeScript) | `bank-aws-001@e494bcf:infra/aws-cdk/{lib/evidence-validator.ts,scripts/validate-evidence.ts}`, `evidence/aws/evidence-schema.json` | `checked 18 files / EVIDENCE VALID` |
| Remediated storage stack with no self-logging + private VPC + private RDS PostgreSQL 17.9, CMKs, rotation through a VPC endpoint, AWS Backup | `aws-remediation-vpc-rds@099479e:infra/aws-cdk/lib/{secure-storage-stack.ts,network-database-stack.ts,least-privilege-key.ts}` | tsc 0, Jest 33/33, synth 0; nag AwsSolutions + NIST R5: 0 non-compliant; 5 suppressions in total, all registered (EX-01..EX-04) |
| Static template guards (public/unencrypted RDS, S3 self-logging loops, KMS wildcards, 0.0.0.0/0 SG rules) | `aws-remediation-vpc-rds@099479e:infra/aws-cdk/lib/guards.ts`, `test/negative-controls.test.ts` | part of the Jest 33/33 |
| Organizations reference: OU tree, 7 SCPs, org CloudTrail, GuardDuty detector, Security Hub (FSBP + CIS, aggregator, CENTRAL config) | `orgs-security-refs@e5e7f46:infra/orgs/lib/*.ts` | tsc 0, Jest 49/49, synth 0 (3 templates byte-identical), nag gate 0/0 |
| Offline SCP linter and evaluator, parliament gate | `infra/orgs/lib/{policy-lint.ts,scp-evaluator.ts}`, `scripts/{lint-policies.ts,parliament.sh}`, `parliament-allowlist.json` | lint `errors=0 warnings=0`; parliament gated `unallowlisted_findings=0` (needed `PYTHONWARNINGS=ignore`, see EXECUTION_LOG) |
| Entra Conditional Access baseline validator (fail-closed, exit codes 0/1/2) | `entra-ca-offline@d302c99:identity/entra/{ca_validator.py,baseline.json,policies/*.json}`, `tests/entra/*` | 25/25 unit tests OK, baseline exit 0, fixture drift check exit 0 |
| Shared evidence checks (`hashes`, `commands`, `postgres-negatives`, `cfn-s3-selflog`, `manifest`) | `review/pr1-pr2-evidence-audit@fb36341:evidence/shared/validate_evidence.py` | 13/13 unit tests OK; results match `reports/review-pr1-pr2.md` |
| Evidence hash integrity | `evidence/aws/SHA256SUMS` (PR #1), `evidence/aws/aws-remediation-vpc-rds/SHA256SUMS` (PR #5), `evidence/orgs/SHA256SUMS` (PR #6), Postgres run `SHA256SUMS` (PR #2) | all `sha256sum -c` OK: 87, 32, 66 and 39 entries |

## Partial (real code, but not runnable here, or with known defects)
| Capability | Files | Status |
|---|---|---|
| PostgreSQL backup/restore exercise | `ci-evidence-postgres@e610015:tests/integration/postgres/run_restore_scenario.sh`, `seed.sql`, `fingerprint.sql`, `verify_evidence.sh` | **Not re-executed here**: no PostgreSQL binaries, and the apt mirror returned HTTP 500. The committed offline run (`runs/local-offline-20261028T041038Z`) verifies: 11 positive, 6 negative, 0 failed. The committed failing CI run has **4 false PASSes** (N01, N04, N05, N06), confirmed with `postgres-negatives`. Root cause: negatives chained with `&&` (PR #3 §2). |
| PR #1 CI workflow | `bank-aws-001@e494bcf:.github/workflows/bank-aws-001-cdk.yml` | Runs 1-3 succeeded per `evidence/aws/ci/RUNS.md`. Not re-run here. |
| PR #2 CI workflow | `ci-evidence-postgres@e610015:.github/workflows/postgres-restore-evidence.yml` | Passing runs exist only as 30-day artifacts. Its `cdk-synth` job sets `CDK_DEFAULT_ACCOUNT=000000000000` and uses `npx --yes` (PR #3 §5). |
| PR #1 self-logging access-log bucket | `bank-aws-001@e494bcf:infra/aws-cdk/lib/secure-storage-stack.ts` | Defect, found by PR #3: `cfn-s3-selflog` reports `ERROR AccessLogsBucket83982689`. Fixed on PR #5. |
| GuardDuty org-wide enablement, Security Hub configuration policies | `orgs-security-refs@e5e7f46:infra/orgs/docs/adr/ADR-0002-delegated-admin-coverage.md` | Documented gap. No code. |
| Security exception register | `aws-remediation-vpc-rds@099479e:evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` | All entries **PROPOSED, pending owner approval**. |

## Stubs
None of the delivered modules is an empty stub. The gaps are absences (listed above) or documented "not modelled" items.
