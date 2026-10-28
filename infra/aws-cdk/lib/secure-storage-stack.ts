import { RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { NagSuppressions } from 'cdk-nag';
import { Construct } from 'constructs';
import { leastPrivilegeKey } from './least-privilege-key';

/**
 * Secure storage stack (remediated).
 * Environment-agnostic: no account/region, no context lookups.
 *
 * Logging topology is a one-way chain with no recursion:
 *   DataBucket --(S3 server access logs, prefix data-bucket/)--> AccessLogsBucket (terminal sink, logs nowhere)
 * The terminal sink deliberately has NO server access logging: logging a log bucket to itself creates a
 * feedback loop (every delivered log object generates a further log record). See ADR-0004 and the
 * security exception register (evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md).
 */
export class SecureStorageStack extends Stack {
  public readonly dataKey: kms.Key;
  public readonly accessLogsBucket: s3.Bucket;
  public readonly dataBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    this.dataKey = leastPrivilegeKey(this, 'DataKey', {
      description: 'CMK for the data bucket (S3 use only, via kms:ViaService)',
      viaServices: ['s3'],
    });

    // Terminal server-access-log sink. SSE-S3 because S3 server access log delivery does not support SSE-KMS targets
    // (ADR-0002). No serverAccessLogsBucket / serverAccessLogsPrefix: it must never log to itself.
    this.accessLogsBucket = new s3.Bucket(this, 'AccessLogsBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      versioned: true,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    this.dataBucket = new s3.Bucket(this, 'DataBucket', {
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: this.dataKey,
      bucketKeyEnabled: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      versioned: true,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      serverAccessLogsBucket: this.accessLogsBucket,
      serverAccessLogsPrefix: 'data-bucket/',
      removalPolicy: RemovalPolicy.RETAIN,
    });
  
    // Registered exceptions (evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md). Proposed, pending approval.
    NagSuppressions.addResourceSuppressions(this.accessLogsBucket, [
      {
        id: 'NIST.800.53.R5-S3DefaultEncryptionKMS',
        reason:
          'EX-01: S3 server access log delivery only supports SSE-S3 (AES256) on the target bucket; SSE-KMS would break log delivery (ADR-0002).',
      },
      {
        id: 'NIST.800.53.R5-S3BucketReplicationEnabled',
        reason:
          'EX-02: Cross-region replication needs a destination bucket in a second region/account; out of scope for an env-agnostic, never-deployed lab stack.',
      },
    ]);
    NagSuppressions.addResourceSuppressions(this.dataBucket, [
      {
        id: 'NIST.800.53.R5-S3BucketReplicationEnabled',
        reason:
          'EX-02: Cross-region replication needs a destination bucket in a second region/account; out of scope for an env-agnostic, never-deployed lab stack.',
      },
    ]);
  }
}
