# 0005: Scoped, registered, test-enforced cdk-nag suppressions
- Status: Proposed (PR #5 open draft; every entry is "PROPOSED, pending owner approval")
- Date: 2026-10-28

## Decision (as implemented)
- Every suppression covers exactly one rule on one resource (IAM rules also pin `appliesTo`), and is listed in
  `aws-remediation-vpc-rds@099479e:evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` (EX-01..EX-04) with its compensating controls and exit criteria.
- Tests named `only registered exceptions are suppressed` fail on any other suppression (`infra/aws-cdk/test/secure-storage-stack.test.ts`, `test/network-database-stack.test.ts`).
- Contrast: PR #1 and PR #6 use **zero** suppressions (`bank-aws-001@e494bcf:infra/aws-cdk/test/secure-storage-stack.test.ts` "no NagSuppressions are applied"; `orgs-security-refs@e5e7f46:infra/orgs/scripts/nag-gate.sh`).

## Consequences
- Re-run here: the nag reports show 5 Suppressed rows in total (AwsSolutions NetworkDatabase 2, NIST SecureStorage 3) and 0 Non-Compliant (learning/execution E01).
- Exceptions still need an owner's sign-off. The register records that this has not happened.
