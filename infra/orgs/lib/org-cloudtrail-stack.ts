import { CfnParameter, Duration, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import * as cloudtrail from 'aws-cdk-lib/aws-cloudtrail';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

/**
 * Organization CloudTrail skeleton (management account or CloudTrail delegated admin).
 * Multi-region, global events, log-file validation, SSE-KMS (CMK), CloudWatch Logs, hardened S3.
 */
export class OrgCloudTrailStack extends Stack {
  public readonly trail: cloudtrail.Trail;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const orgId = new CfnParameter(this, 'OrganizationId', {
      type: 'String',
      description: 'AWS Organizations id (o-xxxxxxxxxx). Supplied at deploy time; never looked up.',
      allowedPattern: '^o-[a-z0-9]{10,32}$',
    });

    const trailName = 'bank-it-lab-org-trail';
    const trailArn = Stack.of(this).formatArn({ service: 'cloudtrail', resource: 'trail', resourceName: trailName });

    const key = new kms.Key(this, 'TrailKey', {
      description: 'CMK for organization CloudTrail logs',
      enableKeyRotation: true,
      removalPolicy: RemovalPolicy.RETAIN,
    });
    key.addToResourcePolicy(new iam.PolicyStatement({
      sid: 'AllowCloudTrailEncrypt',
      principals: [new iam.ServicePrincipal('cloudtrail.amazonaws.com')],
      actions: ['kms:GenerateDataKey*', 'kms:DescribeKey'],
      resources: ['*'],
      conditions: {
        StringEquals: { 'aws:SourceArn': trailArn },
        StringLike: { 'kms:EncryptionContext:aws:cloudtrail:arn': `arn:${Stack.of(this).partition}:cloudtrail:*:${Stack.of(this).account}:trail/*` },
      },
    }));

    const accessLogs = new s3.Bucket(this, 'TrailAccessLogsBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      enforceSSL: true,
      versioned: true,
      // B6-1: no serverAccessLogsPrefix. A prefix without a destination bucket logs this bucket to itself.
      removalPolicy: RemovalPolicy.RETAIN,
    });

    const bucket = new s3.Bucket(this, 'TrailBucket', {
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: key,
      bucketKeyEnabled: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      enforceSSL: true,
      versioned: true,
      serverAccessLogsBucket: accessLogs,
      serverAccessLogsPrefix: 'trail-bucket/',
      lifecycleRules: [{ noncurrentVersionExpiration: Duration.days(365) }],
      removalPolicy: RemovalPolicy.RETAIN,
    });

    const logGroup = new logs.LogGroup(this, 'TrailLogGroup', {
      retention: logs.RetentionDays.ONE_YEAR,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    this.trail = new cloudtrail.Trail(this, 'OrgTrail', {
      trailName,
      bucket,
      encryptionKey: key,
      isOrganizationTrail: true,
      orgId: orgId.valueAsString,
      isMultiRegionTrail: true,
      includeGlobalServiceEvents: true,
      enableFileValidation: true,
      sendToCloudWatchLogs: true,
      cloudWatchLogGroup: logGroup,
      managementEvents: cloudtrail.ReadWriteType.ALL,
    });
  }
}
