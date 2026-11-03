# ADR status on main

The seventeen ADRs in this directory are preserved records, written on 2026-10-28 while every source pull request was an open draft. Their bytes are locked by [preserved-records.json](../metadata/preserved-records.json), so this page records their current position instead of editing them. Checked 2026-11-03 against main `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6`, and re-checked after main moved to `8e2df97b558e69032e52a50ed0adfd311ad04578`. PR #40 adds the acceptance gate but no ADR source code.

## Status rule

Every ADR still says **Proposed**, and that is still correct. The [ADR index](README.md) said they stay Proposed "until its source PR merges". Several source PRs have now merged, but merging code is not the same as accepting a decision. [The integration policy](../knowledge/integration-policy.md) records that independent review was deferred, and final human acceptance (AC6) has not been given. Changing an ADR to Accepted needs the repository owner's decision. No ADR has been superseded or rejected.

## Per-decision position

"Code on main" means the implementing module is INTEGRATED in [coordination/modules.json](../../coordination/modules.json) and its path exists at `30e0a83`.

| ADR | Source PRs (state on 2026-11-03) | Code on main | Notes |
|---|---|---|---|
| [0001](0001-credential-free-static-evidence.md) credential-free static evidence | #1 closed, #5 merged, #6 open | `infra/aws-cdk`, `infra/orgs` | PR #1 paths `evidence/aws/run-cmd.sh` and `.github/workflows/bank-aws-001-cdk.yml` are not on main |
| [0002](0002-pin-cdk-nag-2x-aspects.md) pin cdk-nag 2.x Aspects | #1 closed, #5 merged, #6 open | `infra/aws-cdk`, `infra/orgs` | cited `evidence/aws/logs/CORRECTION-PASS-1.md` is PR #1 only |
| [0003](0003-access-log-sink-sse-s3-one-way-chain.md) access-log sink | #1 closed, #3 merged, #5 merged | `infra/aws-cdk` | B6-1 (Organizations trail bucket) is still recorded as blocking in `coordination/tasks.json` |
| [0004](0004-private-isolated-vpc-and-rds.md) private VPC and RDS | #5 merged | `infra/aws-cdk` | B5-2 is recorded as fixed in `80f01d6`, an ancestor of main. The registry `aws-cdk` limitation still says B5-1/B5-2 open |
| [0005](0005-scoped-security-exception-register.md) exception register | #5 merged | `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` | Exceptions EX-01..EX-04 are unapproved (registry, owner action UA-1) |
| [0006](0006-scps-as-typed-source-offline-validation.md) typed SCPs | #6 open | `infra/orgs` | B6-2 (exempt-role bypass) and B6-3 are still recorded as blocking |
| [0007](0007-delegated-admin-coverage-and-gaps.md) delegated admin | #6 open | `infra/orgs` | GuardDuty org enablement gap as recorded |
| [0008](0008-offline-fail-closed-ca-validator.md) CA validator | #4 merged | `identity/entra`, `tests/entra` | 25 tests OK on 2026-11-03. CA007 baseline gap not re-checked |
| [0009](0009-restore-proof-by-fingerprint-and-negative-tests.md) restore proof | #2, #3, #7 merged | `tests/integration`, `evidence/postgres` | Verifier output `VERIFIED` for the committed bundle (local, 2026-11-03). Live restore not re-run |
| [0010](0010-evidence-bundle-integrity.md) evidence integrity | mixed | `evidence/shared` | `validate-all.sh --python-only` PASS (34 steps) on 2026-11-03. Three cited PR #1/#6 paths are not on main |
| [0011](0011-integration-branch-and-sha-pinned-merge-gates.md) merge gates | #7 merged, #11 open | `.github/workflows`, `scripts/ci`, `tools/acceptance/gate` | Main was integrated before independent review by owner direction. The PR #40 gate reports EXECUTION_PASS / REVIEW_PENDING, never ACCEPTED. The `merge-eligibility` job fails on main `8e2df97` (trusted-manifest drift on `scripts/ci/tests/test_module_coverage.py`), `main` has no branch protection, and no PR has a review, as recorded in the open draft [PR #39](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/39) |
| [0012](0012-fail-closed-health-endpoint.md) fail-closed health | #10 open | `observability` | Offline evaluate HEALTHY on 2026-11-03 |
| [0013](0013-patch-rings-with-gated-scan-waves.md) patch rings | #17 open | `operations/patching` | EXAMPLE data. Nothing applied |
| [0014](0014-fixture-only-graph-client.md) fixture-only Graph client | #18 open | `identity/governance` | Baseline exit 0 and findings exit 1 on 2026-11-03 |
| [0015](0015-simulation-labelled-offline-vendor-mock.md) vendor mock | #9 open | `integrations/vendor-mock` | 45 tests OK on 2026-11-03 |
| [0016](0016-aws-backup-governance-lock-cross-region-copy.md) AWS Backup lock and copy | #21 open | `backup/aws` | `backup/aws/lib/backup-key.ts` still grants `kms:Create*`/`kms:Put*` to the account root; not re-reviewed |
| [0017](0017-simulation-incident-demo-from-pinned-components.md) incident demo | #22 merged | `scenarios/incident` | Both recorded timelines verify. The live crash demo was not re-run |

"Open" PRs above are still open on GitHub, but their content reached main through PR #35. The commands behind each "on 2026-11-03" note are in [Tutorials](../knowledge/tutorials.md).

## What would change a status

- **Accepted** needs an owner decision recorded against a specific commit.
- **Superseded** needs a newer ADR that replaces the decision.
- A blocking finding being fixed does not change ADR status. It changes the Notes column after someone re-checks it.
