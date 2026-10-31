# 0005: Scoped, registered, test-enforced cdk-nag suppressions
- Status: **Proposed.** #5 is an open draft. Its register says PROPOSED. Relayed decisions exist only in #11 (open draft).
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- Every suppression covers exactly one rule on one resource (IAM rules also pin `appliesTo`), and is listed in
  `aws-remediation-vpc-rds@099479e:evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` (EX-01..EX-04) with its compensating controls and exit criteria.
- Tests named `only registered exceptions are suppressed` fail on any other suppression (`infra/aws-cdk/test/secure-storage-stack.test.ts`, `test/network-database-stack.test.ts`).
- Contrast: PR #1 and PR #6 use **zero** suppressions (`bank-aws-001@e494bcf:infra/aws-cdk/test/secure-storage-stack.test.ts` "no NagSuppressions are applied"; `orgs-security-refs@e5e7f46:infra/orgs/scripts/nag-gate.sh`).

## Consequences
- **B5-1** (#14): all 5 suppressions are already applied, so "0 unsuppressed" depends on exceptions nobody has approved. EX-02 covers two resources, which contradicts "one rule on one resource".
- Relayed decisions: `reports/final-report@54d6fbd:reports/USER_ACTIONS_REQUIRED.md` says EX-01 is ACCEPTED for the lab, EX-02 is ACCEPTED as a limitation (rationale rejected), EX-03 is OPEN and EX-04 is CONDITIONALLY ACCEPTABLE. Those decisions are **not recorded in #5**.
- Test gap: the allowlist tests read only resource-level `Metadata.cdk_nag`, so `addStackSuppressions` would bypass them (#14).
- Re-run here: the nag reports show 5 Suppressed rows in total (AwsSolutions NetworkDatabase 2, NIST SecureStorage 3) and 0 Non-Compliant (learning/execution E01).
- Exceptions still need an owner's sign-off. The register records that this has not happened.
