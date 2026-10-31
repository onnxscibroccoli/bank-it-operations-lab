/**
 * Negative tests: deliberately weakened templates MUST be caught by the static guards. If one starts passing,
 * a control has been weakened.
 */
import { App, Duration, RemovalPolicy, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as backup from 'aws-cdk-lib/aws-backup';
import { copyRegionViolations, retentionViolations, vaultViolations } from '../lib/guards';
import { POLICY } from '../lib/lab-context';
import { lockedVault } from '../lib/locked-vault';
import { PrimaryBackupStack } from '../lib/primary-backup-stack';
import { clone } from './helpers';

function fixture(build: (s: Stack) => void) {
  const app = new App();
  const stack = new Stack(app, 'BadFixture');
  build(stack);
  return Template.fromStack(stack).toJSON();
}
const rules = (v: { rule: string }[]) => v.map((x) => x.rule);

test('unlocked vault on the default aws/backup key, not retained, no deny policy', () => {
  const json = fixture((s) => { new backup.BackupVault(s, 'V', { removalPolicy: RemovalPolicy.DESTROY }); });
  expect(rules(vaultViolations(json))).toEqual(expect.arrayContaining(['BKP_VAULT_UNLOCKED', 'BKP_VAULT_DEFAULT_KEY', 'BKP_VAULT_NOT_RETAINED', 'BKP_VAULT_DELETE_ALLOWED']));
});

test('compliance-mode lock (changeableFor) is flagged', () => {
  const json = fixture((s) => {
    new backup.BackupVault(s, 'V', { lockConfiguration: { minRetention: Duration.days(30), changeableFor: Duration.days(3) } });
  });
  expect(rules(vaultViolations(json))).toContain('BKP_VAULT_COMPLIANCE_LOCK');
});

test('lockedVault() refuses COMPLIANCE mode', () => {
  const s = new Stack(new App(), 'X');
  const cfg = clone(POLICY.vaults.primary);
  cfg.lock.mode = 'COMPLIANCE';
  expect(() => lockedVault(s, 'V', cfg, undefined as any, 'OrgBreakGlass')).toThrow(/GOVERNANCE/);
});

test('rule without copy, without retention, and with cold storage under 90 days', () => {
  const json = fixture((s) => {
    const plan = new backup.BackupPlan(s, 'P', { backupVault: new backup.BackupVault(s, 'V') });
    plan.addRule(new backup.BackupPlanRule({ ruleName: 'noRetention' }));
    plan.addRule(new backup.BackupPlanRule({ ruleName: 'cold', moveToColdStorageAfter: Duration.days(30), deleteAfter: Duration.days(200) }));
    // CDK rejects cold+<90 itself, so inject the bad lifecycle at L1 (what a hand-edited template could contain).
    (plan.node.defaultChild as backup.CfnBackupPlan).addPropertyOverride('BackupPlan.BackupPlanRule.1.Lifecycle', { MoveToColdStorageAfterDays: 30, DeleteAfterDays: 60 });
  });
  expect(rules(retentionViolations(json))).toEqual(expect.arrayContaining(['BKP_NO_RETENTION', 'BKP_NO_CROSS_REGION_COPY', 'BKP_COLD_UNDER_90D']));
});

test('copy action with no lifecycle (no explicit expiry) is flagged', () => {
  const json = fixture((s) => {
    const plan = new backup.BackupPlan(s, 'P', { backupVault: new backup.BackupVault(s, 'V') });
    plan.addRule(new backup.BackupPlanRule({
      ruleName: 'r', deleteAfter: Duration.days(35),
      copyActions: [{ destinationBackupVault: backup.BackupVault.fromBackupVaultArn(s, 'D', 'arn:aws:backup:us-west-2:111111111111:backup-vault:x') }],
    }));
  });
  expect(rules(retentionViolations(json))).toContain('BKP_NO_RETENTION');
});

test('"DR" copy into the same region is flagged', () => {
  const p = clone(POLICY);
  p.regions.secondary = 'us-east-1';
  const json = Template.fromStack(new PrimaryBackupStack(new App(), 'Same', { policy: p })).toJSON();
  expect(rules(copyRegionViolations(json, 'us-west-2'))).toContain('BKP_COPY_WRONG_REGION');
});
