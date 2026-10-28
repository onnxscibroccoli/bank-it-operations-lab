import { Duration, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

/**
 * BANK-AWS-001 secure storage stack.
 * Environment-agnostic: no account/region, no context lookups.
 */
export class SecureStorageStack extends Stack {
  public readonly dataKey: kms.Key;
  public readonly accessLogsBucket: s3.Bucket;
  public readonly dataBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    this.dataKey = new kms.Key(this, 'DataKey', {
      description: 'BANK-AWS-001 CMK for the data bucket',
      enableKeyRotation: true,
      pendingWindow: Duration.days(30),
      removalPolicy: RemovalPolicy.RETAIN,
    });

    // Server access log target. S3 server access logging only supports SSE-S3 on the target bucket.
    this.accessLogsBucket = new s3.Bucket(this, 'AccessLogsBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      versioned: true,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      removalPolicy: RemovalPolicy.RETAIN,
      // Logs bucket writes its own access logs under a separate prefix (satisfies AwsSolutions-S1
      // without a NagSuppression and without an extra bucket).
      serverAccessLogsPrefix: 'self-access-logs/',
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
  }
}
