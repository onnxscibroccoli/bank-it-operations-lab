/**
 * aws-remediation-backup-kms: static policy tests + negative tests for the backup vault key, the backup role's KMS
 * permissions and the backup role trust (EX-04).
 *
 * These assert what the SYNTHESIZED TEMPLATE says. They do not (and cannot) prove how AWS IAM/KMS evaluate the
 * policies at runtime, nor that AWS Backup sends aws:SourceArn on sts:AssumeRole. See VERIFICATION_PROCEDURE.md.
 */
import { App, CfnElement, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import { BACKUP_TRUST_MODES, BACKUP_TRUST_MODE_CONTEXT_KEY, DEFAULT_BACKUP_TRUST_MODE } from '../lib/backup-trust';
import { allViolations, backupRoleTrust, classifyKmsAction, iamKmsPermissions, kmsSeparation, kmsWildcards } from '../lib/guards';
import { LAB_CONTEXT } from '../lib/lab-context';
import { NetworkDatabaseStack } from '../lib/network-database-stack';

const synth = (extra: Record<string, unknown> = {}) => {
  const app = new App({ context: { ...LAB_CONTEXT, ...extra } });
  const stack = new NetworkDatabaseStack(app, 'BkmsNetDb');
  return { stack, json: JSON.parse(JSON.stringify(Template.fromStack(stack).toJSON())) as any };
};
const { stack, json } = synth();
const lid = (c: { node: { defaultChild?: unknown } }) => stack.getLogicalId(c.node.defaultChild as CfnElement);
const res = (id: string) => json.Resources[id];
const backupRoleId = () => Object.keys(json.Resources).find((k) => k.startsWith('DbBackupRole') && json.Resources[k].Type === 'AWS::IAM::Role')!;
const backupPolicyId = () => Object.keys(json.Resources).find((k) => k.startsWith('DbBackupPolicy'))!;
const clone = () => JSON.parse(JSON.stringify(json));

describe('positive: backup vault key and backup role (static template)', () => {
  test('the vault uses a dedicated BackupVaultKey, not DatabaseKey', () => {
    const vault = Object.values<any>(json.Resources).find((r) => r.Type === 'AWS::Backup::BackupVault');
    expect(vault.Properties.EncryptionKeyArn).toEqual({ 'Fn::GetAtt': [lid(stack.backupVaultKey), 'Arn'] });
    expect(lid(stack.backupVaultKey)).not.toEqual(lid(stack.dbKey));
  });

  test('BackupVaultKey: admin statement separate from crypto/grant statements; crypto only via backup.<region>', () => {
    const st: any[] = res(lid(stack.backupVaultKey)).Properties.KeyPolicy.Statement;
    const admin = st.find((s) => s.Sid === 'KeyAdministrationByKeyAdminRoleOnly');
    const crypto = st.find((s) => s.Sid === 'CryptoViaApprovedServicesOnly');
    const grants = st.find((s) => s.Sid === 'GrantsForAwsResourcesViaApprovedServicesOnly');
    expect(admin.Action.map(classifyKmsAction).filter((c: string) => c !== 'admin' && c !== 'neutral')).toEqual([]);
    expect(admin.Condition.ArnEquals['aws:PrincipalArn']).toHaveLength(2);
    expect(admin.Condition.BoolIfExists['kms:BypassPolicyLockoutSafetyCheck']).toBe('false');
    expect(crypto.Action.map(classifyKmsAction).every((c: string) => c === 'crypto' || c === 'neutral')).toBe(true);
    expect(JSON.stringify(crypto.Condition.StringEquals['kms:ViaService'])).toContain('backup.');
    expect(JSON.stringify(crypto.Condition.StringEquals['kms:ViaService'])).not.toMatch(/rds\.|secretsmanager\./);
    expect(crypto.Condition.StringEquals['kms:CallerAccount']).toEqual({ Ref: 'AWS::AccountId' });
    expect(grants.Condition.Bool['kms:GrantIsForAWSResource']).toBe('true');
    expect(grants.Condition.StringEquals['kms:CallerAccount']).toEqual({ Ref: 'AWS::AccountId' });
  });

  test('BackupVaultKey carries the AWS-documented backup-storage confused-deputy Deny', () => {
    const st: any[] = res(lid(stack.backupVaultKey)).Properties.KeyPolicy.Statement;
    const d = st.find((s) => s.Sid === 'DenyBackupStorageConfusedDeputy');
    expect(d.Effect).toBe('Deny');
    expect(d.Principal).toEqual({ Service: 'backup-storage.amazonaws.com' });
    expect(d.Action.sort()).toEqual(['kms:Decrypt', 'kms:GenerateDataKey', 'kms:RetireGrant']);
    expect(d.Condition.StringNotEquals['aws:SourceAccount']).toEqual({ Ref: 'AWS::AccountId' });
    expect(JSON.stringify(d.Condition.ArnNotLike['aws:SourceArn'])).toContain(':backup-vault:*');
  });

  test('backup role KMS: crypto and CreateGrant in separate statements; CreateGrant requires GrantIsForAWSResource; no admin, no "*"', () => {
    const st: any[] = res(backupPolicyId()).Properties.PolicyDocument.Statement;
    const kmsSt = st.filter((s) => [].concat(s.Action).some((a: string) => a.startsWith('kms:')));
    expect(kmsSt.map((s) => s.Sid).sort()).toEqual(['CryptoDbAndVaultKeysViaRdsAndBackupOnly', 'GrantsForAwsResourcesViaRdsAndBackupOnly']);
    const grant = kmsSt.find((s) => s.Sid === 'GrantsForAwsResourcesViaRdsAndBackupOnly');
    expect(grant.Action).toEqual('kms:CreateGrant');
    expect(grant.Condition.Bool['kms:GrantIsForAWSResource']).toBe('true');
    for (const s of kmsSt) {
      expect(s.Resource).not.toContain('*');
      expect(s.Condition.StringEquals['kms:ViaService']).toHaveLength(2);
    }
    expect(iamKmsPermissions(json)).toEqual([]);
  });

  test('backup role RDS snapshot scope matches the AWS Backup snapshot name awsbackup:job-<id> (F-06)', () => {
    const s = JSON.stringify(res(backupPolicyId()).Properties.PolicyDocument);
    expect(s).toContain(':snapshot:awsbackup:*');
    expect(s).not.toContain(':snapshot:awsbackup-*');
  });

  test(`default trust mode is ${DEFAULT_BACKUP_TRUST_MODE}: SourceAccount AND SourceArn = this vault (restriction kept)`, () => {
    const c = res(backupRoleId()).Properties.AssumeRolePolicyDocument.Statement[0].Condition;
    expect(c.StringEquals['aws:SourceAccount']).toEqual({ Ref: 'AWS::AccountId' });
    expect(c.ArnEquals['aws:SourceArn']).toEqual({ 'Fn::GetAtt': [expect.stringMatching(/^BackupVault/), 'BackupVaultArn'] });
    expect(backupRoleTrust(json)).toEqual([]);
  });

  test.each(BACKUP_TRUST_MODES)('trust mode %s keeps StringEquals aws:SourceAccount, no IfExists, only backup.amazonaws.com', (mode) => {
    const { json: j } = synth({ [BACKUP_TRUST_MODE_CONTEXT_KEY]: mode });
    expect(backupRoleTrust(j)).toEqual([]);
    const role = Object.values<any>(j.Resources).find((r) => r.Type === 'AWS::IAM::Role' && JSON.stringify(r).includes('backup.amazonaws.com'));
    const s = role.Properties.AssumeRolePolicyDocument.Statement;
    expect(s).toHaveLength(1);
    expect(s[0].Principal).toEqual({ Service: 'backup.amazonaws.com' });
    expect(Object.keys(s[0].Condition).some((o) => o.endsWith('IfExists'))).toBe(false);
  });

  test('an unknown trust mode is rejected at synth time (no silent fallback)', () => {
    expect(() => synth({ [BACKUP_TRUST_MODE_CONTEXT_KEY]: 'none' })).toThrow(/backupTrustMode must be one of/);
  });

  test('all key policies and identity policies pass every static guard', () => {
    expect(kmsSeparation(json)).toEqual([]);
    expect(allViolations(json)).toEqual([]);
  });
});

describe('classifyKmsAction', () => {
  test.each([
    ['kms:Decrypt', 'crypto'], ['kms:ReEncrypt*', 'crypto'], ['kms:GenerateDataKeyWithoutPlaintext', 'crypto'], ['kms:Encrypt*', 'crypto'],
    ['kms:CreateGrant', 'grant'], ['kms:RevokeGrant', 'grant-lifecycle'], ['kms:DescribeKey', 'neutral'],
    ['kms:PutKeyPolicy', 'admin'], ['kms:ScheduleKeyDeletion', 'admin'], ['kms:Create*', 'admin'], ['kms:*', 'wildcard'], ['*', 'wildcard'],
  ])('%s -> %s', (a, c) => expect(classifyKmsAction(a)).toBe(c));
});

function keyFixture(statements: iam.PolicyStatement[]) {
  const app = new App({ context: LAB_CONTEXT });
  const s = new Stack(app, 'BadKey');
  new kms.Key(s, 'K', { enableKeyRotation: true, policy: new iam.PolicyDocument({ statements }) });
  return Template.fromStack(s).toJSON() as any;
}
const root = () => [new iam.AccountRootPrincipal()];

describe('negative: the pre-remediation backup/aws backup-key.ts pattern is caught', () => {
  // Exact admin list from backup/aws/lib/backup-key.ts @ main 8e2df97 (owned by another worker; reproduced, not edited).
  const OLD_ADMIN = ['kms:Create*', 'kms:Describe*', 'kms:Enable*', 'kms:List*', 'kms:Put*', 'kms:Update*', 'kms:Revoke*',
    'kms:Disable*', 'kms:Get*', 'kms:Delete*', 'kms:TagResource', 'kms:UntagResource', 'kms:ScheduleKeyDeletion', 'kms:CancelKeyDeletion'];
  const j = keyFixture([new iam.PolicyStatement({ sid: 'KeyAdministrationByAccountRoot', principals: root(), actions: OLD_ADMIN, resources: ['*'] })]);
  test('flags wildcard admin verbs, unscoped admin principal, lockout bypass and unconditioned Create*/Put*', () => {
    const rules = [...kmsWildcards(j), ...kmsSeparation(j)].map((v) => v.rule);
    expect(rules).toEqual(expect.arrayContaining([
      'KMS_ADMIN_VERB_WILDCARD', 'KMS_ADMIN_UNSCOPED_PRINCIPAL', 'KMS_PUTKEYPOLICY_LOCKOUT_BYPASS_ALLOWED',
      'KMS_UNCONDITIONED_ADMIN', 'KMS_ADMIN_WILDCARD',
    ]));
  });
});

describe('negative: KMS admin/operational mixing and unscoped operational use are caught', () => {
  test('admin + crypto in one statement -> KMS_ADMIN_OPERATIONAL_MIX', () => {
    const j = keyFixture([new iam.PolicyStatement({ principals: root(), actions: ['kms:PutKeyPolicy', 'kms:Decrypt'], resources: ['*'],
      conditions: { ArnEquals: { 'aws:PrincipalArn': 'arn:aws:iam::111111111111:role/x' }, StringEquals: { 'kms:ViaService': 'backup.us-east-1.amazonaws.com' }, BoolIfExists: { 'kms:BypassPolicyLockoutSafetyCheck': 'false' } } })]);
    expect(kmsSeparation(j).map((v) => v.rule)).toEqual(['KMS_ADMIN_OPERATIONAL_MIX']);
  });
  test('admin + CreateGrant in one statement -> KMS_ADMIN_OPERATIONAL_MIX', () => {
    const j = keyFixture([new iam.PolicyStatement({ principals: root(), actions: ['kms:CreateAlias', 'kms:CreateGrant'], resources: ['*'],
      conditions: { ArnEquals: { 'aws:PrincipalArn': 'arn:aws:iam::111111111111:role/x' }, Bool: { 'kms:GrantIsForAWSResource': 'true' } } })]);
    expect(kmsSeparation(j).map((v) => v.rule)).toContain('KMS_ADMIN_OPERATIONAL_MIX');
  });
  test('account-root crypto without kms:ViaService -> KMS_CRYPTO_NOT_VIA_SERVICE', () => {
    const j = keyFixture([new iam.PolicyStatement({ principals: root(), actions: ['kms:Decrypt', 'kms:GenerateDataKey*'], resources: ['*'] })]);
    expect(kmsSeparation(j).map((v) => v.rule)).toEqual(['KMS_CRYPTO_NOT_VIA_SERVICE']);
  });
  test('CreateGrant without GrantIsForAWSResource and without ViaService -> KMS_GRANT_UNSCOPED', () => {
    const j = keyFixture([new iam.PolicyStatement({ principals: root(), actions: ['kms:CreateGrant'], resources: ['*'],
      conditions: { StringEquals: { 'kms:CallerAccount': '111111111111' } } })]);
    expect(kmsSeparation(j).map((v) => v.rule)).toEqual(['KMS_GRANT_UNSCOPED']);
  });
  test('admin for the account root without aws:PrincipalArn -> KMS_ADMIN_UNSCOPED_PRINCIPAL', () => {
    const j = keyFixture([new iam.PolicyStatement({ principals: root(), actions: ['kms:ScheduleKeyDeletion'], resources: ['*'] })]);
    expect(kmsSeparation(j).map((v) => v.rule)).toEqual(['KMS_ADMIN_UNSCOPED_PRINCIPAL']);
  });
  test('service principal with no condition -> KMS_SERVICE_PRINCIPAL_UNCONDITIONED', () => {
    const j = keyFixture([new iam.PolicyStatement({ principals: [new iam.ServicePrincipal('backup.amazonaws.com')], actions: ['kms:Decrypt'], resources: ['*'] })]);
    expect(kmsSeparation(j).map((v) => v.rule)).toEqual(['KMS_SERVICE_PRINCIPAL_UNCONDITIONED']);
  });
});

describe('negative: mutating the real template is caught', () => {
  test('restoring the pre-remediation mixed CreateGrant+crypto statement (no GrantIsForAWSResource) is caught', () => {
    const j = clone();
    const st: any[] = j.Resources[backupPolicyId()].Properties.PolicyDocument.Statement;
    const crypto = st.find((s) => s.Sid === 'CryptoDbAndVaultKeysViaRdsAndBackupOnly');
    crypto.Action = ['kms:CreateGrant', ...crypto.Action];
    expect(iamKmsPermissions(j).map((v) => v.rule).sort()).toEqual(['IAM_KMS_GRANT_MIXED_WITH_CRYPTO', 'IAM_KMS_GRANT_NOT_FOR_AWS_RESOURCE']);
  });
  test('kms:* / Resource "*" / an admin action in the backup role policy is caught', () => {
    const j = clone();
    j.Resources[backupPolicyId()].Properties.PolicyDocument.Statement.push(
      { Effect: 'Allow', Action: ['kms:*'], Resource: '*' },
      { Effect: 'Allow', Action: 'kms:PutKeyPolicy', Resource: { 'Fn::GetAtt': ['X', 'Arn'] } },
    );
    expect(iamKmsPermissions(j).map((v) => v.rule)).toEqual(expect.arrayContaining(['IAM_KMS_WILDCARD', 'IAM_KMS_RESOURCE_WILDCARD', 'IAM_KMS_ADMIN_IN_WORKLOAD_POLICY']));
  });
  test('dropping CreateGrant\'s GrantIsForAWSResource condition is caught', () => {
    const j = clone();
    const g = j.Resources[backupPolicyId()].Properties.PolicyDocument.Statement.find((s: any) => s.Sid === 'GrantsForAwsResourcesViaRdsAndBackupOnly');
    delete g.Condition.Bool;
    expect(iamKmsPermissions(j).map((v) => v.rule)).toEqual(['IAM_KMS_GRANT_NOT_FOR_AWS_RESOURCE']);
  });
  test('adding a crypto action to the real vault-key admin statement is caught', () => {
    const j = clone();
    const admin = j.Resources[lid(stack.backupVaultKey)].Properties.KeyPolicy.Statement.find((s: any) => s.Sid === 'KeyAdministrationByKeyAdminRoleOnly');
    admin.Action.push('kms:Decrypt');
    // Caught twice: admin+crypto mixing, and crypto for an account principal without kms:ViaService.
    expect(kmsSeparation(j).map((v) => v.rule).sort()).toEqual(['KMS_ADMIN_OPERATIONAL_MIX', 'KMS_CRYPTO_NOT_VIA_SERVICE']);
  });
  test('removing kms:ViaService from the real vault-key crypto statement is caught', () => {
    const j = clone();
    const c = j.Resources[lid(stack.backupVaultKey)].Properties.KeyPolicy.Statement.find((s: any) => s.Sid === 'CryptoViaApprovedServicesOnly');
    delete c.Condition.StringEquals['kms:ViaService'];
    expect(kmsSeparation(j).map((v) => v.rule)).toEqual(['KMS_CRYPTO_NOT_VIA_SERVICE']);
  });
  test('restoring Delete*/Get* admin wildcards on the real vault key is caught', () => {
    const j = clone();
    const admin = j.Resources[lid(stack.backupVaultKey)].Properties.KeyPolicy.Statement.find((s: any) => s.Sid === 'KeyAdministrationByKeyAdminRoleOnly');
    admin.Action.push('kms:Delete*', 'kms:Get*');
    expect(kmsSeparation(j).map((v) => v.rule)).toEqual(['KMS_ADMIN_VERB_WILDCARD']);
  });
  test('removing aws:SourceAccount from the backup role trust is caught', () => {
    const j = clone();
    delete j.Resources[backupRoleId()].Properties.AssumeRolePolicyDocument.Statement[0].Condition.StringEquals;
    expect(backupRoleTrust(j).map((v) => v.rule)).toEqual(['BACKUP_TRUST_NO_SOURCE_ACCOUNT']);
  });
  test('weakening the trust to ArnEqualsIfExists / StringEqualsIfExists is caught', () => {
    const j = clone();
    const c = j.Resources[backupRoleId()].Properties.AssumeRolePolicyDocument.Statement[0].Condition;
    c.ArnEqualsIfExists = c.ArnEquals; delete c.ArnEquals;
    c.StringEqualsIfExists = c.StringEquals; delete c.StringEquals;
    expect(backupRoleTrust(j).map((v) => v.rule).sort()).toEqual(['BACKUP_TRUST_IFEXISTS', 'BACKUP_TRUST_IFEXISTS', 'BACKUP_TRUST_NO_SOURCE_ACCOUNT']);
  });
  test('adding a second principal to the backup trust statement is caught', () => {
    const j = clone();
    j.Resources[backupRoleId()].Properties.AssumeRolePolicyDocument.Statement[0].Principal = { Service: 'backup.amazonaws.com', AWS: '*' };
    expect(backupRoleTrust(j).map((v) => v.rule)).toEqual(['BACKUP_TRUST_EXTRA_PRINCIPAL']);
  });
  test('an unconditioned backup trust (the AWS docs CloudFormation example) is caught', () => {
    const j = clone();
    delete j.Resources[backupRoleId()].Properties.AssumeRolePolicyDocument.Statement[0].Condition;
    expect(backupRoleTrust(j).map((v) => v.rule)).toEqual(['BACKUP_TRUST_NO_SOURCE_ACCOUNT']);
  });
});
