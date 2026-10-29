# Security exception register: aws-remediation-vpc-rds

Status of every entry: **PROPOSED, pending owner approval.** Nothing here is deployed. Each exception is a scoped
cdk-nag suppression on exactly one rule and one resource (IAM rules also pin `appliesTo`). Tests
(`only registered exceptions are suppressed`) fail if any other suppression appears.

| ID | Rule | Resource | Why | Compensating controls | Exit criteria |
|----|------|----------|-----|-----------------------|---------------|
| EX-01 | NIST.800.53.R5-S3DefaultEncryptionKMS | BankItLabSecureStorage/AccessLogsBucket | S3 server access log delivery only supports SSE-S3 on the target bucket; SSE-KMS breaks delivery (ADR-0002). | SSE-S3 (AES256), BPA all, TLS-only policy, versioning, BucketOwnerEnforced, RETAIN, log delivery via bucket policy scoped by aws:SourceArn/SourceAccount. | If CMK-encrypted logs are mandated, move to CloudTrail S3 data events into a KMS bucket. |
| EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled | AccessLogsBucket, DataBucket | CRR needs a destination bucket in a second region/account; not expressible in an env-agnostic, never-deployed lab stack. | Versioning on, RETAIN on both buckets. | Add a replica stack per target region/account at deployment design time. |
| EX-03 | AwsSolutions-IAM5 (appliesTo `log-group:RDSOSMetrics:log-stream:*`) | BankItLabNetworkDatabase/RdsMonitoringPolicy | RDS enhanced monitoring writes service-named log streams; the wildcard is limited to streams in the single RDSOSMetrics group of this account/region. Chosen instead of the AWS-managed AmazonRDSEnhancedMonitoringRole (broader, IAM4). | Customer-managed policy, role trust limited to monitoring.rds.amazonaws.com with aws:SourceAccount. | None expected (service behavior). |
| EX-04 | AwsSolutions-IAM4 (appliesTo AWSBackupServiceRolePolicyForBackup) | BankItLabNetworkDatabase/BackupPlan/Postgres/Role | AWS Backup's documented service-role policy; a hand-written copy needs snapshot-name wildcards (IAM5) and drifts from AWS updates. Needed for NIST RDSInBackupPlan. | Role trust limited to backup.amazonaws.com; vault encrypted with the DB CMK; vault RETAIN. | Replace with a customer-managed RDS-only backup policy if the bank's IAM standard forbids AWS-managed policies outright. |

Not suppressed (by design): AwsSolutions-S1 / NIST S3BucketLoggingEnabled do not fire on AccessLogsBucket because cdk-nag
treats a server-access-log target as exempt; it is the terminal sink and intentionally has no access logging (ADR-0004).

Noted, not an exception: the CDK `Secret` construct adds two key-policy statements to DatabaseKey granting the account
root Decrypt/Encrypt/ReEncrypt/GenerateDataKey and CreateGrant/DescribeKey **only via secretsmanager.<region>** (kms:ViaService).
No wildcard principal, no kms:*; guarded by `kmsWildcards` tests.
