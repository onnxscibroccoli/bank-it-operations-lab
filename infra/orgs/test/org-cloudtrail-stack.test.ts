import { Stack, Token } from 'aws-cdk-lib';
import { Match } from 'aws-cdk-lib/assertions';
import { OrgCloudTrailStack } from '../lib/org-cloudtrail-stack';
import { expectNoNagFindings, synth } from './helpers';

const { stack, template } = synth((s) => new OrgCloudTrailStack(s, 'TestOrgCloudTrail'));

describe('OrgCloudTrailStack', () => {
  test('is environment-agnostic', () => {
    expect(Token.isUnresolved(Stack.of(stack).account)).toBe(true);
    expect(Token.isUnresolved(Stack.of(stack).region)).toBe(true);
  });

  test('organization, multi-region trail with validation, global events and KMS', () => {
    template.resourceCountIs('AWS::CloudTrail::Trail', 1);
    template.hasResourceProperties('AWS::CloudTrail::Trail', {
      IsOrganizationTrail: true,
      IsMultiRegionTrail: true,
      IncludeGlobalServiceEvents: true,
      EnableLogFileValidation: true,
      IsLogging: true,
      KMSKeyId: { 'Fn::GetAtt': [Match.stringLikeRegexp('^TrailKey'), 'Arn'] },
      CloudWatchLogsLogGroupArn: Match.anyValue(),
      EventSelectors: [{ IncludeManagementEvents: true, ReadWriteType: 'All' }],
    });
  });

  test('org id is a validated parameter used in the bucket policy', () => {
    template.hasParameter('OrganizationId', { AllowedPattern: '^o-[a-z0-9]{10,32}$' });
    template.hasResourceProperties('AWS::S3::BucketPolicy', {
      PolicyDocument: {
        Statement: Match.arrayWith([
          Match.objectLike({
            Principal: { Service: 'cloudtrail.amazonaws.com' },
            Action: 's3:PutObject',
            Resource: { 'Fn::Join': ['', Match.arrayWith([{ Ref: 'OrganizationId' }])] },
          }),
        ]),
      },
    });
  });

  test('CMK has rotation and a CloudTrail grant scoped by SourceArn', () => {
    template.hasResourceProperties('AWS::KMS::Key', {
      EnableKeyRotation: true,
      KeyPolicy: {
        Statement: Match.arrayWith([
          Match.objectLike({
            Sid: 'AllowCloudTrailEncrypt',
            Principal: { Service: 'cloudtrail.amazonaws.com' },
            Condition: Match.objectLike({ StringEquals: { 'aws:SourceArn': Match.anyValue() } }),
          }),
        ]),
      },
    });
  });

  test('both buckets: BPA all, versioned, owner-enforced, TLS-only, retained', () => {
    const buckets = template.findResources('AWS::S3::Bucket');
    expect(Object.keys(buckets)).toHaveLength(2);
    for (const b of Object.values(buckets)) {
      expect(b.Properties.PublicAccessBlockConfiguration).toEqual({
        BlockPublicAcls: true, BlockPublicPolicy: true, IgnorePublicAcls: true, RestrictPublicBuckets: true,
      });
      expect(b.Properties.VersioningConfiguration).toEqual({ Status: 'Enabled' });
      expect(b.Properties.OwnershipControls).toEqual({ Rules: [{ ObjectOwnership: 'BucketOwnerEnforced' }] });
      expect(b.DeletionPolicy).toBe('Retain');
    }
    for (const p of Object.values(template.findResources('AWS::S3::BucketPolicy'))) {
      expect(p.Properties.PolicyDocument.Statement).toEqual(expect.arrayContaining([
        expect.objectContaining({ Effect: 'Deny', Condition: { Bool: { 'aws:SecureTransport': 'false' } } }),
      ]));
    }
  });

  test('trail bucket uses SSE-KMS with the CMK', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      BucketEncryption: {
        ServerSideEncryptionConfiguration: [Match.objectLike({
          BucketKeyEnabled: true,
          ServerSideEncryptionByDefault: { SSEAlgorithm: 'aws:kms', KMSMasterKeyID: Match.anyValue() },
        })],
      },
    });
  });

  test('CloudWatch log group has 1-year retention', () => {
    template.hasResourceProperties('AWS::Logs::LogGroup', { RetentionInDays: 365 });
  });

  test('cdk-nag AwsSolutions: no errors or warnings', () => expectNoNagFindings(stack));
});
