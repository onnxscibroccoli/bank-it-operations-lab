import { App, Aspects, Stack, Token } from 'aws-cdk-lib';
import { Annotations, Match, Template } from 'aws-cdk-lib/assertions';
import { AwsSolutionsChecks } from 'cdk-nag';
import { LAB_CONTEXT } from '../lib/lab-context';
import { SecureStorageStack } from '../lib/secure-storage-stack';

function build(): { stack: Stack; template: Template } {
  const app = new App({ context: LAB_CONTEXT });
  const stack = new SecureStorageStack(app, 'TestStack');
  Aspects.of(stack).add(new AwsSolutionsChecks({ verbose: true, reports: false }));
  app.synth();
  return { stack, template: Template.fromStack(stack) };
}

const { stack, template } = build();

const BPA_ALL = {
  BlockPublicAcls: true,
  BlockPublicPolicy: true,
  IgnorePublicAcls: true,
  RestrictPublicBuckets: true,
};

describe('SecureStorageStack', () => {
  test('is environment-agnostic (no account/region)', () => {
    expect(Token.isUnresolved(Stack.of(stack).account)).toBe(true);
    expect(Token.isUnresolved(Stack.of(stack).region)).toBe(true);
  });

  test('creates exactly one KMS key with rotation enabled', () => {
    template.resourceCountIs('AWS::KMS::Key', 1);
    template.hasResourceProperties('AWS::KMS::Key', { EnableKeyRotation: true });
  });

  test('creates exactly two buckets', () => {
    template.resourceCountIs('AWS::S3::Bucket', 2);
  });

  test('data bucket: SSE-KMS with CMK, BPA, versioning, access logs', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      BucketEncryption: {
        ServerSideEncryptionConfiguration: [
          Match.objectLike({
            BucketKeyEnabled: true,
            ServerSideEncryptionByDefault: {
              SSEAlgorithm: 'aws:kms',
              KMSMasterKeyID: Match.anyValue(),
            },
          }),
        ],
      },
      PublicAccessBlockConfiguration: BPA_ALL,
      VersioningConfiguration: { Status: 'Enabled' },
      LoggingConfiguration: {
        DestinationBucketName: Match.anyValue(),
        LogFilePrefix: 'data-bucket/',
      },
    });
  });

  test('access logs bucket: SSE-S3, BPA, versioning', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      BucketEncryption: {
        ServerSideEncryptionConfiguration: [
          { ServerSideEncryptionByDefault: { SSEAlgorithm: 'AES256' } },
        ],
      },
      PublicAccessBlockConfiguration: BPA_ALL,
      VersioningConfiguration: { Status: 'Enabled' },
    });
  });

  test('every bucket has public access fully blocked and versioning', () => {
    const buckets = template.findResources('AWS::S3::Bucket');
    for (const b of Object.values(buckets)) {
      expect(b.Properties.PublicAccessBlockConfiguration).toEqual(BPA_ALL);
      expect(b.Properties.VersioningConfiguration).toEqual({ Status: 'Enabled' });
      expect(b.Properties.BucketEncryption).toBeDefined();
    }
  });

  test('every bucket policy denies non-TLS access (enforceSSL)', () => {
    const policies = template.findResources('AWS::S3::BucketPolicy');
    expect(Object.keys(policies)).toHaveLength(2);
    for (const p of Object.values(policies)) {
      const stmts = p.Properties.PolicyDocument.Statement as any[];
      const deny = stmts.find(
        (s) =>
          s.Effect === 'Deny' &&
          s.Condition?.Bool?.['aws:SecureTransport'] === 'false',
      );
      expect(deny).toBeDefined();
    }
  });

  test('ACLs disabled; log delivery granted via bucket policy, not ACL', () => {
    for (const b of Object.values(template.findResources('AWS::S3::Bucket'))) {
      expect(b.Properties.OwnershipControls).toEqual({
        Rules: [{ ObjectOwnership: 'BucketOwnerEnforced' }],
      });
      expect(b.Properties.AccessControl).toBeUndefined();
    }
    template.hasResourceProperties('AWS::S3::BucketPolicy', {
      PolicyDocument: {
        Statement: Match.arrayWith([
          Match.objectLike({
            Effect: 'Allow',
            Action: 's3:PutObject',
            Principal: { Service: 'logging.s3.amazonaws.com' },
          }),
        ]),
      },
    });
  });

  test('buckets and key are retained', () => {
    for (const type of ['AWS::S3::Bucket', 'AWS::KMS::Key']) {
      for (const r of Object.values(template.findResources(type))) {
        expect(r.DeletionPolicy).toBe('Retain');
      }
    }
  });

  test('cdk-nag AwsSolutions: zero errors', () => {
    const errors = Annotations.fromStack(stack).findError(
      '*',
      Match.stringLikeRegexp('AwsSolutions-.*'),
    );
    expect(errors).toHaveLength(0);
  });

  test('cdk-nag AwsSolutions: zero warnings', () => {
    const warnings = Annotations.fromStack(stack).findWarning(
      '*',
      Match.stringLikeRegexp('AwsSolutions-.*'),
    );
    expect(warnings).toHaveLength(0);
  });

  test('no NagSuppressions are applied', () => {
    const json = JSON.stringify(template.toJSON());
    expect(json).not.toContain('cdk_nag');
  });
});
