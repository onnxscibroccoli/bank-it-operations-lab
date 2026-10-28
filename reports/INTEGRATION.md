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
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | `ci-evidence-postgres` @ `e610015` | **Integrated with review fixes** (4th) | #3's required changes were applied (see below). |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | `orgs-security-refs` @ `e5e7f46` | **Awaiting changes, not integrated** | `TrailAccessLogsBucket` logs to itself (`infra/orgs/lib/org-cloudtrail-stack.ts:50`), which is the same defect #3 blocked in #1. `cfn-s3-selflog` reports an ERROR on `evidence/orgs/synth/BankItLabOrgCloudTrail.template.json`. The PR is also a self-declared draft. A trial merge was clean, and tsc, Jest 49/49 and synth passed. |

No PR has a formal GitHub review, and none of the open PRs has a review comment. The only review is #3's report (`reports/review-pr1-pr2.md`), which covers #1 and #2. Every integrated PR still needs a human review in the draft PR into `main`.

## File overlap and conflicts
- **#1 and #5** share 14 `infra/aws-cdk/**` files. #5's commit 1 imports #1 @ `e494bcf`, minus `lib/evidence-validator.ts`, `scripts/validate-evidence.ts`, `test/evidence-validator.test.ts` and the `validate:evidence` npm script. #5 is used, and #1's copy is dropped.
- Every other pair is disjoint. #2 and #1 both add `.github/workflows/*`, but with different filenames.
- No textual merge conflicts.

## Integration changes (commit `integration fixes: ...`)
1. `.github/workflows/aws-cdk.yml`: #1's workflow adapted to #5. It covers both stacks and both cdk-nag packs, requires exactly 4 reports with 0 Non-Compliant, and uses the evidence path `evidence/aws/aws-remediation-vpc-rds/SHA256SUMS`. It adds the `cfn-s3-selflog` gate, a synth-drift diff against the committed templates, `npm ci --ignore-scripts`, and a wider credential-variable check.
2. `.github/workflows/offline-validation.yml`: runs `scripts/validate-all.sh --python-only`, covering the shared validator tests, Entra tests, validator, fixture drift and evidence verify, and the AWS and Postgres evidence bundles.
3. `.github/workflows/postgres-restore-evidence.yml` (#2):
   - Removed the `cdk-synth` job. It duplicated aws-cdk.yml, set `CDK_DEFAULT_ACCOUNT=000000000000`, and ran unpinned `npx --yes` / `npm install`.
   - Added `persist-credentials: false` and a `postgres-negatives` gate, and the job now fails on it.
   - Paths are scoped to its own workflow and the evidence/test dirs, and PRs are filtered to `main` and `overnight/integration`.
4. `tests/integration/postgres/run_restore_scenario.sh` (#2): each negative is now a single command, and its setup steps are checked separately, so a setup error can no longer count as the expected failure. The server major is now `server_version_num / 10000`.
5. `evidence/postgres/runs/ci-service-40630856041-1/NOTE.md`: corrected the false "negatives behaved as expected" claim. This file is not covered by that run's SHA256SUMS.
6. `infra/aws-cdk/README.md`: fixed the stale pointer to `evidence/aws/README.md`, which does not exist after #5, and the stale CI note.
7. New evidence: `evidence/postgres/runs/integration-offline-20261028T180134Z`. It ran PG 16.15 on a unix socket only and validates `f3a8f17`: 39/39 PASS, and all 6 negatives failed for the intended reason.
8. `scripts/validate-all.sh`, `.gitignore` (`__pycache__`), and this report plus `coordination/tasks.json`.

## Validation result
See the draft PR description for the run on the final HEAD. On the box, with no AWS credentials, Node 20.19.2, Python 3.13.5 and PostgreSQL 16.15 from conda-forge:
- shared validator 13/13, Entra 25/25, baseline exit 0, fixture drift OK, Entra evidence verify OK
- aws-cdk: tsc OK, Jest 33/33, synth OK, 4 nag reports with 0 Non-Compliant, no self-logging, no synth drift, SHA256SUMS OK
- Postgres: committed offline and integration runs verify, a fresh offline run gives 39/39, and negatives pass the intended-reason check
- `ci-service-40630856041-1` is a preserved failing run (4 false PASSes). It is kept on purpose and not gated.

## Open issues / blockers before `main`
- #6 needs the self-logging fix and regenerated evidence. Once that is done it can merge cleanly, because its paths are disjoint.
- #5's security exceptions EX-01..EX-04 need an owner's approval.
- #4's baseline choices need an owner's confirmation: risk policies stay report-only, the device-compliance scope, and the 12 privileged roles.
- #2's PR body is stale, and no passing service-mode run is committed.
- #1 should be closed as superseded by its owner. Integration did not close it.
- No human GitHub review exists on any PR.
- Actions are pinned by tag, not SHA (carried over from #1/#2).
