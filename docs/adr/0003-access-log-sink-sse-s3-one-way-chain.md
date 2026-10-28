# 0003: SSE-S3 access-log sink and a one-way logging chain
- Status: Proposed. PR #1 introduced self-logging (a defect). PR #5 removes it. Both are unmerged.
- Date: 2026-10-28

## Context
S3 server access logs cannot be delivered to an SSE-KMS target bucket (`bank-aws-001@e494bcf:infra/aws-cdk/docs/adr/ADR-0002-sse-s3-access-log-bucket.md`).
PR #1 also made `AccessLogsBucket` log to itself to satisfy AwsSolutions-S1. PR #3 found that this creates an infinite log loop
(`review/pr1-pr2-evidence-audit@fb36341:reports/review-pr1-pr2.md` §3; `validate_evidence.py cfn-s3-selflog` → ERROR).

## Decision (as implemented on PR #5)
- `AccessLogsBucket`: SSE-S3, BPA all, TLS-only, versioned, BucketOwnerEnforced, RETAIN, and **no** access logging (terminal sink).
  `DataBucket` → `AccessLogsBucket` under `data-bucket/` is the only edge. Log delivery uses a bucket policy (`@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy`).
  `aws-remediation-vpc-rds@099479e:infra/aws-cdk/lib/secure-storage-stack.ts`, `lib/lab-context.ts`.
- Guard `selfLoggingBuckets` (direct and multi-bucket loops) with negative tests: `lib/guards.ts`, `test/negative-controls.test.ts`.
- NIST `S3DefaultEncryptionKMS` on the sink is exception EX-01 (`evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md`).
- Module ADR: `aws-remediation-vpc-rds@099479e:infra/aws-cdk/docs/adr/ADR-0004-no-self-logging-log-sink.md`.

## Consequences
- The sink itself is not access-logged. ADR-0004 proposes CloudTrail S3 data events to a separate trail bucket if that is needed. That is not built.
- Neither bucket has lifecycle rules (PR #3 §4).
