import { Aws, CfnOutput, Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as backup from 'aws-cdk-lib/aws-backup';
import * as events from 'aws-cdk-lib/aws-events';
import * as iam from 'aws-cdk-lib/aws-iam';
import { NagSuppressions } from 'cdk-nag';
import { Construct } from 'constructs';
import { backupVaultKey } from './backup-key';
import { lockedVault, pinRegion } from './locked-vault';
import { BackupPolicy, RuleCfg } from './policy';

export interface PrimaryBackupStackProps extends StackProps { readonly policy: BackupPolicy }

export const BACKUP_MANAGED_POLICIES = [
  'service-role/AWSBackupServiceRolePolicyForBackup',
  'AWSBackupServiceRolePolicyForS3Backup',
];
export const RESTORE_MANAGED_POLICIES = [
  'service-role/AWSBackupServiceRolePolicyForRestores',
  'AWSBackupServiceRolePolicyForS3Restore',
];

/** Destination vault ARN in the secondary region, built from config (no cross-stack/cross-region reference). */
export function drVaultArn(p: BackupPolicy): string {
  return `arn:${Aws.PARTITION}:backup:${p.regions.secondary}:${Aws.ACCOUNT_ID}:backup-vault:${p.vaults.dr_copy.name}`;
}

function serviceRole(scope: Construct, id: string, roleName: string, managed: string[], description: string): iam.Role {
  return new iam.Role(scope, id, {
    roleName,
    description,
    assumedBy: new iam.ServicePrincipal('backup.amazonaws.com', {
      conditions: { StringEquals: { 'aws:SourceAccount': Aws.ACCOUNT_ID } },
    }),
    managedPolicies: managed.map((m) => iam.ManagedPolicy.fromAwsManagedPolicyName(m)),
    maxSessionDuration: Duration.hours(1),
  });
}

/**
 * Primary-region side: CMK vault (Vault Lock, governance), backup + restore service roles, a backup plan whose every
 * rule copies to the DR vault in the secondary region, a tag-based selection, and a monthly restore-testing plan.
 */
export class PrimaryBackupStack extends Stack {
  public readonly vault: backup.BackupVault;
  public readonly plan: backup.BackupPlan;

  constructor(scope: Construct, id: string, props: PrimaryBackupStackProps) {
    super(scope, id, props);
    const p = props.policy;
    pinRegion(this, p.regions.primary);

    const key = backupVaultKey(this, 'PrimaryVaultKey', {
      description: `CMK for ${p.vaults.primary.name} (fully managed resource types: S3, EFS, DynamoDB advanced)`,
      viaServices: ['backup'],
    });
    this.vault = lockedVault(this, 'PrimaryVault', p.vaults.primary, key, p.break_glass_role_name);
    const drVault = backup.BackupVault.fromBackupVaultArn(this, 'DrCopyVaultRef', drVaultArn(p));

    const backupRole = serviceRole(this, 'BackupServiceRole', `${p.naming_prefix}-backup-role`, BACKUP_MANAGED_POLICIES,
      'Assumed by AWS Backup for backup and copy jobs of the bank-it-lab plan');
    const restoreRole = serviceRole(this, 'RestoreServiceRole', `${p.naming_prefix}-restore-role`, RESTORE_MANAGED_POLICIES,
      'Assumed by AWS Backup for restore jobs and restore testing (separate from the backup role)');

    this.plan = new backup.BackupPlan(this, 'BackupPlan', {
      backupPlanName: `${p.naming_prefix}-standard-plan`,
      backupVault: this.vault,
    });
    for (const r of p.rules) this.plan.addRule(this.rule(r, drVault));

    this.plan.addSelection('TaggedResources', {
      backupSelectionName: `${p.naming_prefix}-tagged`,
      role: backupRole,
      resources: [backup.BackupResource.fromTag(p.selection.tag_key, p.selection.tag_value)],
    });

    const rt = p.restore_testing;
    const rtp = new backup.CfnRestoreTestingPlan(this, 'RestoreTestingPlan', {
      restoreTestingPlanName: rt.name,
      scheduleExpression: rt.schedule_cron_utc,
      scheduleExpressionTimezone: 'Etc/UTC',
      startWindowHours: rt.start_window_hours,
      recoveryPointSelection: {
        algorithm: 'LATEST_WITHIN_WINDOW',
        includeVaults: [this.vault.backupVaultArn],
        recoveryPointTypes: ['SNAPSHOT'],
        selectionWindowDays: rt.recovery_point_window_days,
      },
    });
    const rts = new backup.CfnRestoreTestingSelection(this, 'RestoreTestingSelection', {
      restoreTestingPlanName: rt.name,
      restoreTestingSelectionName: `${rt.name}_rds`,
      protectedResourceType: rt.protected_resource_type,
      iamRoleArn: restoreRole.roleArn,
      protectedResourceConditions: {
        stringEquals: [{ key: `aws:ResourceTag/${p.selection.tag_key}`, value: p.selection.tag_value }],
      },
      validationWindowHours: rt.validation_window_hours,
    });
    rts.node.addDependency(rtp);

    // Registered exceptions BKP-EX-01 / BKP-EX-02 (evidence/backup/aws-backup-dr/SECURITY_EXCEPTIONS.md).
    NagSuppressions.addResourceSuppressions(backupRole, [{
      id: 'AwsSolutions-IAM4',
      reason: 'BKP-EX-01: AWS Backup documented service-role policies for backup/copy (incl. S3); hand-written copies need snapshot wildcards and drift from AWS updates.',
      appliesTo: BACKUP_MANAGED_POLICIES.map((m) => `Policy::arn:<AWS::Partition>:iam::aws:policy/${m}`),
    }]);
    NagSuppressions.addResourceSuppressions(restoreRole, [{
      id: 'AwsSolutions-IAM4',
      reason: 'BKP-EX-02: AWS Backup documented service-role policies for restores (incl. S3); restore needs iam:PassRole and per-service create APIs maintained by AWS.',
      appliesTo: RESTORE_MANAGED_POLICIES.map((m) => `Policy::arn:<AWS::Partition>:iam::aws:policy/${m}`),
    }]);

    new CfnOutput(this, 'PrimaryVaultArn', { value: this.vault.backupVaultArn });
    new CfnOutput(this, 'BackupPlanId', { value: this.plan.backupPlanId });
    new CfnOutput(this, 'RestoreRoleArn', { value: restoreRole.roleArn });
  }

  private rule(r: RuleCfg, drVault: backup.IBackupVault): backup.BackupPlanRule {
    const c = r.schedule_cron_utc;
    const copy = r.copy_to_dr!;
    return new backup.BackupPlanRule({
      ruleName: r.name,
      scheduleExpression: events.Schedule.cron({ minute: c.minute, hour: c.hour, day: c.day, month: c.month, weekDay: c.weekDay }),
      startWindow: Duration.minutes(r.start_window_minutes),
      completionWindow: Duration.minutes(r.completion_window_minutes),
      enableContinuousBackup: r.enable_continuous_backup,
      deleteAfter: Duration.days(r.lifecycle.delete_after_days),
      moveToColdStorageAfter: r.lifecycle.move_to_cold_storage_after_days !== undefined ? Duration.days(r.lifecycle.move_to_cold_storage_after_days) : undefined,
      copyActions: [{
        destinationBackupVault: drVault,
        deleteAfter: Duration.days(copy.lifecycle.delete_after_days),
        moveToColdStorageAfter: copy.lifecycle.move_to_cold_storage_after_days !== undefined ? Duration.days(copy.lifecycle.move_to_cold_storage_after_days) : undefined,
      }],
    });
  }
}
