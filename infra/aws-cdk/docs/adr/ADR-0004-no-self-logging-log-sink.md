# ADR-0004: One-way access-log chain; the log sink never logs to itself

- Status: Proposed (supersedes the `self-access-logs/` part of ADR-0002)
- Date: 2026-10-28

## Context
`AccessLogsBucket` had `serverAccessLogsPrefix: 'self-access-logs/'` and no target bucket, so S3 delivered its access
logs into itself. Every delivered log object is itself an access that produces more log records: a feedback loop that
grows storage and cost, and buries real events. It existed only to satisfy AwsSolutions-S1 without a suppression.

## Decision
- `DataBucket` -> `AccessLogsBucket` (prefix `data-bucket/`) is the only logging edge. `AccessLogsBucket` is the
  terminal sink with no server access logging. cdk-nag exempts log-target buckets from S1, so no suppression is needed.
- VPC flow logs and RDS logs go to KMS-encrypted CloudWatch Logs groups, not S3, so they cannot recurse into the sink.
- `lib/guards.ts#selfLoggingBuckets` detects direct self-logging and multi-bucket loops; Jest negative tests prove it.
- Access to the sink itself, if required, should be audited with CloudTrail S3 data events to a separate trail bucket
  that is excluded from its own trail's data-event selectors.
