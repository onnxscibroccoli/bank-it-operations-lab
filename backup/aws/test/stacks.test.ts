import { Match } from 'aws-cdk-lib/assertions';
import { DrVaultStack } from '../lib/dr-vault-stack';
import { allViolations, copyRegionViolations, regionPinViolations } from '../lib/guards';
import { POLICY } from '../lib/lab-context';
import { BACKUP_MANAGED_POLICIES, PrimaryBackupStack, RESTORE_MANAGED_POLICIES } from '../lib/primary-backup-stack';
import { NAG_PACKS, nagFindings, suppressionsIn, synthWithNag } from './helpers';

const primary = synthWithNag((app) => new PrimaryBackupStack(app, 'BankItLabBackupPrimary', { policy: POLICY }));
const dr = synthWithNag((app) => new DrVaultStack(app, 'BankItLabBackupDrVault', { policy: POLICY }));

describe.each([['primary', primary], ['dr', dr]] as const)('%s stack', (_n, s) => {
  test.each(NAG_PACKS)('no unsuppressed cdk-nag %s errors', (pack) => {
    expect(nagFindings(s.stack, 'error', pack).map((m) => m.entry.data)).toEqual([]);
  });
  test('static guards report no violations', () => expect(allViolations(s.template.toJSON())).toEqual([]));
  test('vault: CMK, governance lock bounds from config, RETAIN', () => {
    s.template.hasResource('AWS::Backup::BackupVault', {
      DeletionPolicy: 'Retain',
      Properties: Match.objectLike({
        EncryptionKeyArn: Match.anyValue(),
        LockConfiguration: Match.objectEquals({ MinRetentionDays: 30, MaxRetentionDays: 400 }),
      }),
    });
  });
  test('vault keys rotate, are retained, and have no wildcard principal or kms:*', () => {
    const keys = s.template.findResources('AWS::KMS::Key');
    expect(Object.keys(keys).length).toBe(1);
    for (const k of Object.values<any>(keys)) {
      expect(k.Properties.EnableKeyRotation).toBe(true);
      expect(k.DeletionPolicy).toBe('Retain');
      for (const st of k.Properties.KeyPolicy.Statement) {
        expect(JSON.stringify(st.Principal)).not.toContain('"*"');
        expect([].concat(st.Action)).not.toContain('kms:*');
      }
    }
  });
});

describe('region pinning (deploy-time CloudFormation Rules)', () => {
  test('primary pinned to us-east-1', () => expect(regionPinViolations(primary.template.toJSON(), 'us-east-1')).toEqual([]));
  test('dr pinned to us-west-2', () => expect(regionPinViolations(dr.template.toJSON(), 'us-west-2')).toEqual([]));
  test('negative: pin check fails for the wrong region', () => expect(regionPinViolations(primary.template.toJSON(), 'us-west-2')).toHaveLength(1));
});

describe('primary backup plan', () => {
  const plan = Object.values<any>(primary.template.findResources('AWS::Backup::BackupPlan'))[0].Properties.BackupPlan;
  test('rules match config (names, retention, cold storage, continuous)', () => {
    expect(plan.BackupPlanRule.map((r: any) => r.RuleName)).toEqual(POLICY.rules.map((r) => r.name));
    const daily = plan.BackupPlanRule[0];
    expect(daily).toMatchObject({ EnableContinuousBackup: true, Lifecycle: { DeleteAfterDays: 35 }, StartWindowMinutes: 60, CompletionWindowMinutes: 480 });
    const monthly = plan.BackupPlanRule[1];
    expect(monthly.Lifecycle).toEqual({ MoveToColdStorageAfterDays: 90, DeleteAfterDays: 365 });
    expect(monthly.CopyActions[0].Lifecycle).toEqual({ MoveToColdStorageAfterDays: 90, DeleteAfterDays: 365 });
  });
  test('every rule copies cross-region to the DR vault in us-west-2 with explicit retention', () => {
    expect(copyRegionViolations(primary.template.toJSON(), 'us-west-2')).toEqual([]);
    for (const r of plan.BackupPlanRule) {
      expect(r.CopyActions).toHaveLength(1);
      expect(JSON.stringify(r.CopyActions[0].DestinationBackupVaultArn)).toContain(`:backup-vault:${POLICY.vaults.dr_copy.name}`);
    }
  });
  test('tag-based selection', () => {
    primary.template.hasResourceProperties('AWS::Backup::BackupSelection', {
      BackupSelection: Match.objectLike({
        SelectionName: 'bank-it-lab-tagged',
        ListOfTags: [{ ConditionKey: POLICY.selection.tag_key, ConditionValue: POLICY.selection.tag_value, ConditionType: 'STRINGEQUALS' }],
      }),
    });
  });
  test('backup and restore roles are separate, trusted only by backup.amazonaws.com in this account', () => {
    const roles = Object.values<any>(primary.template.findResources('AWS::IAM::Role'));
    expect(roles.map((r) => r.Properties.RoleName).sort()).toEqual(['bank-it-lab-backup-role', 'bank-it-lab-restore-role']);
    for (const r of roles) {
      const st = r.Properties.AssumeRolePolicyDocument.Statement;
      expect(st).toHaveLength(1);
      expect(st[0].Principal).toEqual({ Service: 'backup.amazonaws.com' });
      expect(st[0].Condition.StringEquals['aws:SourceAccount']).toEqual({ Ref: 'AWS::AccountId' });
    }
  });
  test('restore testing plan + RDS selection exist', () => {
    primary.template.hasResourceProperties('AWS::Backup::RestoreTestingPlan', { RestoreTestingPlanName: POLICY.restore_testing.name, ScheduleExpression: POLICY.restore_testing.schedule_cron_utc });
    primary.template.hasResourceProperties('AWS::Backup::RestoreTestingSelection', { ProtectedResourceType: 'RDS', ValidationWindowHours: 24 });
  });
});

describe('only registered exceptions are suppressed', () => {
  test('primary: exactly BKP-EX-01 / BKP-EX-02 (AwsSolutions-IAM4 on the two roles, pinned appliesTo)', () => {
    const sup = suppressionsIn(primary.template);
    expect(sup.map((s) => s.rule)).toEqual(['AwsSolutions-IAM4', 'AwsSolutions-IAM4']);
    expect(sup.map((s) => s.reason.split(':')[0]).sort()).toEqual(['BKP-EX-01', 'BKP-EX-02']);
    const applies = sup.flatMap((s) => s.appliesTo ?? []).sort();
    expect(applies).toEqual([...BACKUP_MANAGED_POLICIES, ...RESTORE_MANAGED_POLICIES].map((m) => `Policy::arn:<AWS::Partition>:iam::aws:policy/${m}`).sort());
  });
  test('dr: none', () => expect(suppressionsIn(dr.template)).toEqual([]));
});
