import { CfnElement, Stack, Token } from 'aws-cdk-lib';
import { Match } from 'aws-cdk-lib/assertions';
import { kmsWildcards, selfLoggingBuckets } from '../lib/guards';
import { SecureStorageStack } from '../lib/secure-storage-stack';
import { NAG_PACKS, nagFindings, suppressionsIn, synthWithNag } from './helpers';

const { stack, template } = synthWithNag((app) => new SecureStorageStack(app, 'TestStorage'));
const BPA_ALL = { BlockPublicAcls: true, BlockPublicPolicy: true, IgnorePublicAcls: true, RestrictPublicBuckets: true };
const lid = (c: { node: { defaultChild?: unknown } }) => stack.getLogicalId(c.node.defaultChild as CfnElement);
const LOGS = lid(stack.accessLogsBucket);
const DATA = lid(stack.dataBucket);

describe('SecureStorageStack (remediated)', () => {
  test('is environment-agnostic (no account/region)', () => {
    expect(Token.isUnresolved(Stack.of(stack).account)).toBe(true);
    expect(Token.isUnresolved(Stack.of(stack).region)).toBe(true);
  });

  test('AccessLogsBucket has NO server access logging (no self-logging, no self-access-logs/ prefix)', () => {
    const r = template.toJSON().Resources[LOGS];
    expect(r.Properties.LoggingConfiguration).toBeUndefined();
    expect(JSON.stringify(template.toJSON())).not.toContain('self-access-logs');
  });

  test('DataBucket logs one-way to AccessLogsBucket under data-bucket/', () => {
    const r = template.toJSON().Resources[DATA];
    expect(r.Properties.LoggingConfiguration).toEqual({
      DestinationBucketName: { Ref: LOGS },
      LogFilePrefix: 'data-bucket/',
    });
  });

  test('guard: no bucket logs to itself (directly or via a loop)', () => {
    expect(selfLoggingBuckets(template.toJSON())).toEqual([]);
  });

  test('data bucket: SSE-KMS with the CMK, BPA all, versioning', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      BucketEncryption: {
        ServerSideEncryptionConfiguration: [
          Match.objectLike({ BucketKeyEnabled: true, ServerSideEncryptionByDefault: { SSEAlgorithm: 'aws:kms', KMSMasterKeyID: Match.anyValue() } }),
        ],
      },
      PublicAccessBlockConfiguration: BPA_ALL,
      VersioningConfiguration: { Status: 'Enabled' },
    });
  });

  test('every bucket: BPA all, versioning, encryption, ACLs disabled, TLS-only policy, retained', () => {
    for (const b of Object.values(template.findResources('AWS::S3::Bucket'))) {
      expect(b.Properties.PublicAccessBlockConfiguration).toEqual(BPA_ALL);
      expect(b.Properties.VersioningConfiguration).toEqual({ Status: 'Enabled' });
      expect(b.Properties.BucketEncryption).toBeDefined();
      expect(b.Properties.OwnershipControls).toEqual({ Rules: [{ ObjectOwnership: 'BucketOwnerEnforced' }] });
      expect(b.DeletionPolicy).toBe('Retain');
    }
    const policies = Object.values(template.findResources('AWS::S3::BucketPolicy'));
    expect(policies).toHaveLength(2);
    for (const p of policies) {
      expect((p.Properties.PolicyDocument.Statement as any[]).some((s) => s.Effect === 'Deny' && s.Condition?.Bool?.['aws:SecureTransport'] === 'false')).toBe(true);
    }
  });

  test('CMK: rotation on, retained, least-privilege key policy (no wildcard principal, no kms:*)', () => {
    template.resourceCountIs('AWS::KMS::Key', 1);
    template.hasResourceProperties('AWS::KMS::Key', { EnableKeyRotation: true });
    expect(kmsWildcards(template.toJSON())).toEqual([]);
    const key = Object.values(template.findResources('AWS::KMS::Key'))[0];
    const crypto = (key.Properties.KeyPolicy.Statement as any[]).find((s) => s.Sid === 'CryptoViaApprovedServicesOnly');
    expect(JSON.stringify(crypto.Condition.StringEquals['kms:ViaService'])).toContain('"s3."');
    const admin = (key.Properties.KeyPolicy.Statement as any[]).find((s) => s.Sid === 'KeyAdministrationByKeyAdminRoleOnly');
    expect(admin.Action).not.toContain('kms:Decrypt');
    expect(admin.Action).not.toContain('kms:Encrypt');
  });

  test('B5-2: key admin is least-privilege: no Create*/Put* wildcards, no CreateGrant, scoped principal, still manageable', () => {
    const key = Object.values(template.findResources('AWS::KMS::Key'))[0];
    const stmts = key.Properties.KeyPolicy.Statement as any[];
    expect(stmts.find((s) => s.Sid === 'KeyAdministrationByAccountRoot')).toBeUndefined();
    const admin = stmts.find((s) => s.Sid === 'KeyAdministrationByKeyAdminRoleOnly');
    expect(admin.Action).not.toContain('kms:Create*');
    expect(admin.Action).not.toContain('kms:Put*');
    expect(admin.Action).not.toContain('kms:CreateGrant');
    expect((admin.Action as string[]).filter((a) => a.includes('*'))).toEqual([]);
    expect(admin.Action).toEqual(expect.arrayContaining(['kms:PutKeyPolicy', 'kms:ScheduleKeyDeletion', 'kms:CancelKeyDeletion', 'kms:EnableKey']));
    const arns = JSON.stringify(admin.Condition.ArnEquals['aws:PrincipalArn']);
    expect(arns).toContain(':role/BankItLabKmsKeyAdmin');
    expect(arns).toContain(':root');
    expect(admin.Condition.BoolIfExists['kms:BypassPolicyLockoutSafetyCheck']).toBe('false');
    // the only CreateGrant allowed for account principals is the conditioned AWS-resource grant statement
    for (const s of stmts.filter((x) => ([] as string[]).concat(x.Action).includes('kms:CreateGrant'))) {
      expect(s.Condition?.Bool?.['kms:GrantIsForAWSResource'] ?? s.Condition?.StringEquals?.['kms:ViaService']).toBeDefined();
    }
  });

  test.each(NAG_PACKS)('cdk-nag %s: zero unsuppressed errors and warnings', (pack) => {
    expect(nagFindings(stack, 'error', pack)).toHaveLength(0);
    expect(nagFindings(stack, 'warning', pack)).toHaveLength(0);
  });

  test('only registered exceptions are suppressed (EX-01, EX-02)', () => {
    const s = suppressionsIn(template).map((x) => `${x.rule}@${x.logicalId}`).sort();
    expect(s).toEqual(
      [
        `NIST.800.53.R5-S3BucketReplicationEnabled@${LOGS}`,
        `NIST.800.53.R5-S3BucketReplicationEnabled@${DATA}`,
        `NIST.800.53.R5-S3DefaultEncryptionKMS@${LOGS}`,
      ].sort(),
    );
    for (const x of suppressionsIn(template)) expect(x.reason).toMatch(/^EX-0[12]: /);
  });
});
