# 0007: Delegated-admin coverage; GuardDuty org enablement left as a gap
- Status: Proposed (PR #6 open draft)
- Date: 2026-10-28

## Decision (as implemented)
- Security Hub: `AWS::SecurityHub::DelegatedAdmin` (management account), Hub, FSBP v1.0.0 + CIS v3.0.0, an `ALL_REGIONS` aggregator, and `CENTRAL` org configuration.
  `orgs-security-refs@e5e7f46:infra/orgs/lib/{org-governance-stack.ts,security-services-stack.ts}`.
- GuardDuty: detector with protection plans only. Org admin and auto-enable have no CloudFormation resource and are **intentionally not built**.
- CloudTrail: an organization trail in the management account (`lib/org-cloudtrail-stack.ts`).
- Module ADR: `infra/orgs/docs/adr/ADR-0002-delegated-admin-coverage.md`.

## Consequences
- GuardDuty org-wide enablement and Security Hub configuration policies are gaps.
- AwsSolutions has no rules for these resource types (0 nag rows), so unit tests are the only coverage (`evidence/orgs/README.md`).
