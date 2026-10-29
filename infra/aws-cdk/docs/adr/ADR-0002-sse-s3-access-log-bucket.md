# ADR-0002: SSE-S3 (not SSE-KMS) for the server access-log bucket

- Status: Accepted
- Date: 2026-10-28
- Task: BANK-AWS-001

## Context
The data bucket uses SSE-KMS with a customer-managed key (rotation on). Its S3 server access logs need a target
bucket. AWS documents that the target bucket for S3 server access logging must use SSE-S3 (AES256); SSE-KMS
targets are not supported for server access log delivery. In addition, with ACLs disabled (BucketOwnerEnforced)
log delivery must be authorized by a bucket policy rather than the legacy log-delivery ACL (correction pass 2).

## Decision
- `AccessLogsBucket`: `BucketEncryption.S3_MANAGED`, Block Public Access all, `enforceSSL`, versioning,
  BucketOwnerEnforced, RETAIN. ~~Its own access logs under `self-access-logs/`~~ removed: self-logging recursion, see ADR-0004.
- Feature flag `@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy=true` so CDK grants `logging.s3.amazonaws.com`
  `s3:PutObject` via bucket policy, scoped with `aws:SourceArn`/`aws:SourceAccount`.

## Consequences
- Log objects are encrypted at rest with S3-managed keys; key-usage auditing via KMS/CloudTrail does not apply to them.
- If a regulator or policy requires CMK encryption of logs, use a different log path (e.g. CloudTrail data events
  to a KMS-encrypted bucket), not S3 server access logging.
