import { Aws, CfnRule, Duration, Fn, RemovalPolicy } from 'aws-cdk-lib';
import * as backup from 'aws-cdk-lib/aws-backup';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';
import { VaultCfg } from './policy';

/**
 * Actions on recovery points / the lock / the vault policy that only the break-glass role may perform
 * (defence in depth next to Vault Lock). Operational consequence: later CloudFormation updates that change the vault
 * lock or access policy must be executed by the break-glass role (see RETENTION_AND_DELETION.md).
 */
export const PROTECTED_VAULT_ACTIONS = [
  'backup:DeleteRecoveryPoint',
  'backup:UpdateRecoveryPointLifecycle',
  'backup:PutBackupVaultLockConfiguration',
  'backup:DeleteBackupVaultLockConfiguration',
  'backup:DeleteBackupVault',
  'backup:DeleteBackupVaultAccessPolicy',
  'backup:PutBackupVaultAccessPolicy',
];

/**
 * CMK-encrypted, RETAIN, Vault-Lock'd backup vault with an access policy that denies deletion / lifecycle changes to
 * everyone except the break-glass role. GOVERNANCE mode only: `changeableFor` is never set (setting it creates a
 * COMPLIANCE lock that becomes irreversible after the grace time).
 */
export function lockedVault(scope: Construct, id: string, cfg: VaultCfg, key: kms.IKey, breakGlassRoleName: string): backup.BackupVault {
  if (cfg.lock.mode !== 'GOVERNANCE') throw new Error(`${cfg.name}: only GOVERNANCE vault lock is allowed in this lab reference`);
  const breakGlassArn = `arn:${Aws.PARTITION}:iam::${Aws.ACCOUNT_ID}:role/${breakGlassRoleName}`;
  return new backup.BackupVault(scope, id, {
    backupVaultName: cfg.name,
    encryptionKey: key,
    removalPolicy: RemovalPolicy.RETAIN,
    lockConfiguration: {
      minRetention: Duration.days(cfg.lock.min_retention_days),
      maxRetention: Duration.days(cfg.lock.max_retention_days),
    },
    accessPolicy: new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          sid: 'DenyRecoveryPointAndLockChangesExceptBreakGlass',
          effect: iam.Effect.DENY,
          principals: [new iam.AnyPrincipal()],
          actions: PROTECTED_VAULT_ACTIONS,
          resources: ['*'],
          conditions: { ArnNotLike: { 'aws:PrincipalArn': breakGlassArn } },
        }),
      ],
    }),
  });
}

/** Deploy-time guard: the template refuses to create in any region but `region` (synthesis stays env-agnostic). */
export function pinRegion(scope: Construct, region: string) {
  new CfnRule(scope, 'PinRegion', {
    assertions: [{ assert: Fn.conditionEquals(Aws.REGION, region), assertDescription: `This stack may only be deployed in ${region}.` }],
  });
}
