# Repository-level architecture decision records

These ADRs record decisions that the delivered code **already makes**. Each one cites the files that implement it, at the
branch and SHA where the code lives. All source PRs are open drafts (none merged; `main` is `7f50348`, re-checked 2026-10-28 at 14:24 EDT), so every ADR here has status **Proposed** until its source PR merges.
Status lines also record whether the source is integrated in #7 and any open #14 finding.
Module-level ADRs remain authoritative for their module, and these records index and connect them. They do not override them.

| ADR | Decision | Source PR(s) | Module ADR(s) |
|---|---|---|---|
| [0001](0001-credential-free-static-evidence.md) | Credential-free, environment-agnostic synthesis; static evidence only | #1, #5, #6 | aws-cdk ADR-0003, orgs ADR-0001 |
| [0002](0002-pin-cdk-nag-2x-aspects.md) | Pin cdk-nag 2.38.2 and use the Aspects API; exact toolchain pins | #1, #5, #6 | aws-cdk ADR-0001 |
| [0003](0003-access-log-sink-sse-s3-one-way-chain.md) | SSE-S3 access-log sink and a one-way logging chain | #1, #3, #5 | aws-cdk ADR-0002, ADR-0004 |
| [0004](0004-private-isolated-vpc-and-rds.md) | Private isolated VPC and private RDS PostgreSQL with CMKs (open: B5-2) | #5 | (none; stack doc comment) |
| [0005](0005-scoped-security-exception-register.md) | Scoped, registered, test-enforced cdk-nag suppressions | #5 | (none) |
| [0006](0006-scps-as-typed-source-offline-validation.md) | SCPs as typed source with three offline validation layers and quota-driven attachment | #6 | orgs ADR-0003 |
| [0007](0007-delegated-admin-coverage-and-gaps.md) | Delegated-admin coverage; GuardDuty org enablement left as a gap | #6 | orgs ADR-0002 |
| [0008](0008-offline-fail-closed-ca-validator.md) | Offline fail-closed Conditional Access validator with exit-code contract and staged risk rollout | #4 | (none) |
| [0009](0009-restore-proof-by-fingerprint-and-negative-tests.md) | Restore proof by fingerprints and negative tests; harness v2; failures preserved | #2, #3, #7 | (none) |
| [0010](0010-evidence-bundle-integrity.md) | Evidence bundles: SHA256SUMS, command logs with exit trailers, shared validator | #1-#7, #9, #10, #17, #18, #20-#22 | (none) |
| [0011](0011-integration-branch-and-sha-pinned-merge-gates.md) | Integration branch plus SHA-pinned merge gates G1-G9 | #7, #11 | (none) |
| [0012](0012-fail-closed-health-endpoint.md) | Fail-closed health endpoint (anything not HEALTHY is 503) | #10 | (none) |
| [0013](0013-patch-rings-with-gated-scan-waves.md) | Patch rings; gated waves ship as Scan | #17 | (none) |
| [0014](0014-fixture-only-graph-client.md) | Fixture-only Graph client; federation documentation only | #18 | (none) |
| [0015](0015-simulation-labelled-offline-vendor-mock.md) | SIMULATION-labelled, socket-blocked vendor mock | #9 | (none) |
| [0016](0016-aws-backup-governance-lock-cross-region-copy.md) | AWS Backup: GOVERNANCE Vault Lock, cross-region copy, NOT_EXECUTED status artifact | #21 | backup/aws ADR-0001, ADR-0002 |
| [0017](0017-simulation-incident-demo-from-pinned-components.md) | SIMULATION incident demo from pinned components, with metrics re-derived on verify | #22 | (none) |
