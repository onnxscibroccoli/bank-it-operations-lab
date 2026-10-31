import { ALLOWED_REGIONS } from '../lib/lab-context';
import { lintScp, minifiedLength, SCP_MAX_CHARS, SCP_MAX_PER_TARGET } from '../lib/policy-lint';
import { OU_LAYOUT } from '../lib/ou-layout';
import { deniedBy, RequestContext } from '../lib/scp-evaluator';
import { BASELINE_SCP_IDS, ROOT_SCP_IDS, SCPS, scpById } from '../lib/scps';

const ADMIN = 'arn:aws:iam::111122223333:role/OrgSecurityAdmin';
const DEV = 'arn:aws:iam::111122223333:role/Developer';
const ROOT = 'arn:aws:iam::111122223333:root';
const req = (action: string, keys: RequestContext['keys'] = {}): RequestContext => ({
  action,
  keys: { 'aws:PrincipalArn': DEV, 'aws:RequestedRegion': 'us-east-1', 'aws:SecureTransport': 'true', ...keys },
});
const deny = (id: string, r: RequestContext) => deniedBy(scpById(id).document, r);

describe('SCP lint (offline)', () => {
  test.each(SCPS.map((s) => [s.id, s]))('%s has no lint errors and fits the size quota', (_id, s) => {
    const errors = lintScp(s).filter((f) => f.severity === 'ERROR');
    expect(errors).toEqual([]);
    expect(minifiedLength(s.document)).toBeLessThanOrEqual(SCP_MAX_CHARS);
  });

  test('ids and names are unique', () => {
    expect(new Set(SCPS.map((s) => s.id)).size).toBe(SCPS.length);
    expect(new Set(SCPS.map((s) => s.name)).size).toBe(SCPS.length);
  });

  test('linter catches bad policies', () => {
    const bad = lintScp({
      id: 'bad', name: 'bad', description: 'bad',
      document: {
        Version: '2012-10-17',
        Statement: [
          { Sid: 'A', Effect: 'Allow', Action: 's3:*', Resource: '*' },
          { Sid: 'A', Effect: 'Deny', Action: 'not an action', Resource: '*', Condition: { Foo: { 'aws:x': 'y' } } },
        ],
      },
    }).map((f) => f.code);
    expect(bad).toEqual(expect.arrayContaining(['NOT_DENY', 'SID_DUPLICATE', 'ACTION_FORMAT', 'CONDITION_OPERATOR']));
  });

  test('no target exceeds 5 directly attached SCPs (FullAWSAccess counts as one)', () => {
    expect(ROOT_SCP_IDS.length + 1).toBeLessThanOrEqual(SCP_MAX_PER_TARGET);
    for (const ou of OU_LAYOUT) expect(ou.scps.length + 1).toBeLessThanOrEqual(SCP_MAX_PER_TARGET);
  });

  test('root and OU attachments do not overlap', () => {
    for (const ou of OU_LAYOUT) for (const id of ou.scps) expect(ROOT_SCP_IDS).not.toContain(id);
  });
});

describe('SCP behaviour (offline evaluator)', () => {
  test('deny-root-user: root denied, roles allowed', () => {
    expect(deny('deny-root-user', req('s3:ListBucket', { 'aws:PrincipalArn': ROOT }))).toBe('DenyRootUser');
    expect(deny('deny-root-user', req('s3:ListBucket'))).toBeUndefined();
  });

  test('deny-leave-organization', () => {
    expect(deny('deny-leave-organization', req('organizations:LeaveOrganization', { 'aws:PrincipalArn': ADMIN })))
      .toBe('DenyLeaveOrganization');
    expect(deny('deny-leave-organization', req('organizations:DescribeOrganization'))).toBeUndefined();
  });

  test('region-lock: denies other regions for every principal, allows allowed regions and global services', () => {
    expect(deny('region-lock', req('ec2:RunInstances', { 'aws:RequestedRegion': 'eu-west-1' }))).toBe('DenyOutsideAllowedRegions');
    expect(deny('region-lock', req('ec2:RunInstances', { 'aws:RequestedRegion': 'eu-west-1', 'aws:PrincipalArn': ADMIN }))).toBe('DenyOutsideAllowedRegions');
    for (const r of ALLOWED_REGIONS) expect(deny('region-lock', req('ec2:RunInstances', { 'aws:RequestedRegion': r }))).toBeUndefined();
    expect(deny('region-lock', req('iam:CreateRole', { 'aws:RequestedRegion': 'eu-west-1' }))).toBeUndefined();
  });

  test.each([
    ['cloudtrail:StopLogging', 'ProtectCloudTrail'],
    ['cloudtrail:DeleteTrail', 'ProtectCloudTrail'],
    ['guardduty:DeleteDetector', 'ProtectGuardDuty'],
    ['guardduty:DisassociateFromAdministratorAccount', 'ProtectGuardDuty'],
    ['securityhub:DisableSecurityHub', 'ProtectSecurityHub'],
    ['securityhub:BatchDisableStandards', 'ProtectSecurityHub'],
    ['config:StopConfigurationRecorder', 'ProtectConfig'],
  ])('protect-security-services denies %s for every principal, including former break-glass names', (action, sid) => {
    expect(deny('protect-security-services', req(action))).toBe(sid);
    expect(deny('protect-security-services', req(action, { 'aws:PrincipalArn': ADMIN }))).toBe(sid);
  });

  test('protect-security-services leaves read-only calls alone', () => {
    for (const a of ['cloudtrail:LookupEvents', 'guardduty:ListFindings', 'securityhub:GetFindings']) {
      expect(deny('protect-security-services', req(a))).toBeUndefined();
    }
  });

  test('deny-public-s3', () => {
    expect(deny('deny-public-s3', req('s3:PutBucketPublicAccessBlock'))).toBe('DenyBpaChanges');
    expect(deny('deny-public-s3', req('s3:PutAccountPublicAccessBlock', { 'aws:PrincipalArn': ADMIN }))).toBe('DenyBpaChanges');
    expect(deny('deny-public-s3', req('s3:PutObject', { 's3:x-amz-acl': 'public-read' }))).toBe('DenyPublicAcls');
    expect(deny('deny-public-s3', req('s3:PutBucketAcl', { 's3:x-amz-acl': 'public-read', 'aws:PrincipalArn': ADMIN }))).toBe('DenyPublicAcls');
    expect(deny('deny-public-s3', req('s3:PutObject', { 's3:x-amz-acl': 'bucket-owner-full-control' }))).toBeUndefined();
    expect(deny('deny-public-s3', req('s3:PutBucketOwnershipControls', { 's3:x-amz-object-ownership': 'ObjectWriter' })))
      .toBe('DenyDisableOwnershipEnforced');
    expect(deny('deny-public-s3', req('s3:PutBucketOwnershipControls', { 's3:x-amz-object-ownership': 'BucketOwnerEnforced' })))
      .toBeUndefined();
  });

  test('require-encryption', () => {
    expect(deny('require-encryption', req('ec2:CreateVolume', { 'ec2:Encrypted': 'false' }))).toBe('DenyUnencryptedEbs');
    expect(deny('require-encryption', req('ec2:CreateVolume', { 'ec2:Encrypted': 'true' }))).toBeUndefined();
    expect(deny('require-encryption', req('rds:CreateDBInstance', { 'rds:StorageEncrypted': 'false' }))).toBe('DenyUnencryptedRds');
    expect(deny('require-encryption', req('elasticfilesystem:CreateFileSystem', { 'elasticfilesystem:Encrypted': 'false' })))
      .toBe('DenyUnencryptedEfs');
    expect(deny('require-encryption', req('s3:GetObject', { 'aws:SecureTransport': 'false' }))).toBe('DenyS3WithoutTls');
    expect(deny('require-encryption', req('s3:PutObject', { 's3:x-amz-server-side-encryption': 'aws:kms' }))).toBeUndefined();
    expect(deny('require-encryption', req('s3:PutObject'))).toBeUndefined(); // default SSE-S3 applies
    expect(deny('require-encryption', req('s3:PutObject', { 's3:x-amz-server-side-encryption': 'bogus' }))).toBe('DenyUnsupportedS3Sse');
    expect(deny('require-encryption', req('ec2:DisableEbsEncryptionByDefault'))).toBe('DenyDisableEbsDefaultEncryption');
  });

  test('deny-all-suspended: everything denied, including former break-glass role names', () => {
    expect(deny('deny-all-suspended', req('s3:ListAllMyBuckets'))).toBe('DenyAll');
    expect(deny('deny-all-suspended', req('s3:ListAllMyBuckets', { 'aws:PrincipalArn': ADMIN }))).toBe('DenyAll');
    expect(deny('deny-all-suspended', req('ec2:DisableEbsEncryptionByDefault', { 'aws:PrincipalArn': ADMIN }))).toBe('DenyAll');
  });

  test('no statement exempts a principal ARN (B6-2 regression)', () => {
    const blob = JSON.stringify(SCPS);
    expect(blob).not.toContain('ArnNotLike');
    expect(blob).not.toContain('OrgBreakGlass');
    expect(blob).not.toContain('OrgSecurityAdmin');
  });

  test('baseline references only defined SCPs', () => {
    for (const id of [...ROOT_SCP_IDS, ...BASELINE_SCP_IDS]) expect(() => scpById(id)).not.toThrow();
  });
});
