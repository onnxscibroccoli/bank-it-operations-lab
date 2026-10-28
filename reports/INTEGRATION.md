# Overnight integration: `overnight/integration`

- Base: `main` @ `7f50348` (contains only `README.md`; verified it was not broken). Nothing was merged into `main`, no PR was closed, nothing was deployed, and no AWS, Entra or Graph calls were made.
- Machine-readable status: [`coordination/tasks.json`](../coordination/tasks.json).
- Full validation: `scripts/validate-all.sh` (Node 20, npm, and PostgreSQL binaries via `PG_BIN` or PATH). For the Python-only subset, run `scripts/validate-all.sh --python-only`.

## Per-PR disposition

| PR | Branch @ head | Disposition | Why |
|---|---|---|---|
| [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) | `review/pr1-pr2-evidence-audit` @ `fb36341` | **Integrated** (1st) | Shared, dependency-free tooling (`evidence/shared/`) that later checks rely on. It is the review of #1/#2. |
| [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) | `aws-remediation-vpc-rds` @ `099479e` | **Integrated** (2nd) | Newer `infra/aws-cdk` that includes #1's app and fixes #3's blocking self-logging finding. |
| [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) | `bank-aws-001` @ `e494bcf` | **Superseded by #5** | 14 duplicate `infra/aws-cdk` files. Its top-level `evidence/aws/**` is for the self-logging template, which fails `cfn-s3-selflog`. Only its CI workflow was carried forward, adapted as `.github/workflows/aws-cdk.yml`. |
| [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) | `entra-ca-offline` @ `d302c99` | **Integrated** (3rd) | Disjoint paths, stdlib only, all checks pass. |
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | `ci-evidence-postgres` @ `e7399fb` | **Integrated, harness v2** (4th; re-merged in `e76d8a4`) | The owner's harness v2 (`2aac93c`, `e7399fb`) fixes #3's false-PASS finding. It replaces the interim integration hardening from `f3a8f17`. GitHub CI at `e7399fb`: 5/5 jobs green. |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | `orgs-security-refs` @ `e5e7f46` | **Awaiting changes, not integrated** | `TrailAccessLogsBucket` logs to itself (`infra/orgs/lib/org-cloudtrail-stack.ts:50`), which is the same defect #3 blocked in #1. `cfn-s3-selflog` reports an ERROR on `evidence/orgs/synth/BankItLabOrgCloudTrail.template.json`. The PR is also a self-declared draft. A trial merge was clean, and tsc, Jest 49/49 and synth passed. |

No PR has a formal GitHub review, and none of the open PRs has a review comment. The only review is #3's report (`reports/review-pr1-pr2.md`), which covers #1 and #2. Every integrated PR still needs a human review in the draft PR into `main`.

## File overlap and conflicts
- **#1 and #5** share 14 `infra/aws-cdk/**` files. #5's commit 1 imports #1 @ `e494bcf`, minus `lib/evidence-validator.ts`, `scripts/validate-evidence.ts`, `test/evidence-validator.test.ts` and the `validate:evidence` npm script. #5 is used, and #1's copy is dropped.
- Every other pair is disjoint. #2 and #1 both add `.github/workflows/*`, but with different filenames.
- No textual merge conflicts.

## Integration changes
1. `.github/workflows/aws-cdk.yml`: PR #1's workflow adapted to PR #5.
   - covers both stacks and both cdk-nag packs; requires exactly 4 reports with 0 Non-Compliant
   - uses the evidence path `evidence/aws/aws-remediation-vpc-rds/SHA256SUMS`
   - adds the `cfn-s3-selflog` gate, a synth-drift diff, `npm ci --ignore-scripts`, and a wider credential-variable check
2. `.github/workflows/offline-validation.yml`: runs `scripts/validate-all.sh --python-only`.
3. PR #2 re-merge (`e76d8a4`, merging `e7399fb`):
   - My interim changes to `run_restore_scenario.sh`, `postgres-restore-evidence.yml` and `ci-service-40630856041-1/NOTE.md` (from `f3a8f17`) conflicted with the owner's v2. I resolved all three to the **owner's version**.
   - The interim evidence run `integration-offline-20261028T180134Z` was removed, because the script that produced it no longer exists.
   - The v2 workflow has its own pinned `cdk-synth` job with no `CDK_DEFAULT_*`, so it overlaps `aws-cdk.yml`. That is harmless.
4. Interface fix between #3 and #2 (`05941a9`): on v2's 12-column `COMMANDS.tsv`, `evidence/shared/validate_evidence.py postgres-negatives` silently reported `NEGATIVES OK: 0 negative steps`.
   - It now finds columns by header name, so it handles v1 and v2.
   - It errors when it finds zero negatives.
   - 2 new unit tests (15/15).
   - It agrees with v2's `verify_evidence.py` on every committed run: 6/6 on the current runs, and 4 false PASSes on the v1 CI run.
5. `infra/aws-cdk/README.md` and `evidence/shared/README.md`: fixed stale paths and stale "not wired into CI" text.
6. `scripts/validate-all.sh`, `.gitignore`, this report, and `coordination/tasks.json`.

## Validation result
I ran `PG_BIN=<conda-forge PG 16.15>/bin scripts/validate-all.sh` on the box with no AWS credentials (Node 20.19.2, Python 3.13.5). Result: **PASS, all steps**. The full step list is in the draft PR description.
- Shared validator: 15/15.
- Entra:
  - 25/25 tests
  - baseline exit 0
  - fixture drift OK
  - evidence verify OK
- aws-cdk:
  - tsc OK, Jest 33/33, synth OK
  - 4 nag reports with 0 Non-Compliant
  - no S3 self-logging
  - no synth drift
  - SHA256SUMS OK
- Postgres v2:
  - The committed CURRENT runs `ci-service-40741329107-1`, `ci-offline-40741329107-1` and `local-offline-v2-20261028T180208Z` are VERIFIED.
  - `ci-mismatch-control-40741329107-1` is REJECTED, as intended.
  - The v1 runs report HISTORICAL (exit 3).
  - The self-test passes.
  - A fresh offline v2 run passes 38/38 and is verified with `--require-artifacts`.
  - The shared validator cross-check agrees.

## Acceptance conditions for merging PR #7 into `main`
These are evaluated at the PR #7 head pushed with this report. The machine-readable copy is in `coordination/tasks.json` under `acceptance_conditions_for_main`.

| # | Condition | Status | Detail |
|---|---|---|---|
| AC1 | An independent human review approves the **exact** PR #7 head SHA. The reviewer must not be the author or this automation. | **UNMET** | There are no GitHub reviews on #1–#7. #3 reviewed only #1 @ `e494bcf` and #2 @ `e6100154`, and both have since been superseded or changed. |
| AC2 | Security exceptions are recorded **and approved**. | **PARTIAL** | EX-01..EX-04 are recorded in `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` and enforced by tests. No approval is recorded. |
| AC3 | All checks pass on that SHA: PR #7 GitHub CI plus `scripts/validate-all.sh`. | **MET locally, CI pending for the new HEAD** | Local: PASS. PR #7 CI was green at `876f7b7`. |
| AC4 | The docs match the code. | **PARTIAL** | Repo docs and the PR #2 body are fixed or current. PR #1 is still open with the superseded design. The PR #4 baseline choices are unconfirmed. |
| AC5 | No unresolved blocking findings remain in integrated code. | **MET** | `cfn-s3-selflog` is clean, and the false PASSes are fixed by v2. PR #6 is excluded. |

## Open issues / blockers before `main`
- #6 needs the self-logging fix and regenerated evidence. Once that is done it can merge cleanly, because its paths are disjoint.
- #5's security exceptions EX-01..EX-04 need an owner's approval.
- #4's baseline choices need an owner's confirmation: risk policies stay report-only, the device-compliance scope, and the 12 privileged roles.
- #2's v2 `cdk-synth` job duplicates `aws-cdk.yml`. It is not a blocker.
- #1 should be closed as superseded by its owner. Integration did not close it.
- No human GitHub review exists on any PR.
- Actions are pinned by tag, not SHA (carried over from #1/#2).
