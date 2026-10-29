import { CfnOutput, Stack, StackProps } from 'aws-cdk-lib';
import * as backup from 'aws-cdk-lib/aws-backup';
import { Construct } from 'constructs';
import { backupVaultKey } from './backup-key';
import { lockedVault, pinRegion } from './locked-vault';
import { BackupPolicy } from './policy';

export interface DrVaultStackProps extends StackProps { readonly policy: BackupPolicy }

/**
 * Secondary-region (DR) side: the destination vault for cross-region copies. Deployed (never, in this lab) to
 * policy.regions.secondary, before the primary stack, because copy actions reference this vault by ARN.
 */
export class DrVaultStack extends Stack {
  public readonly vault: backup.BackupVault;

  constructor(scope: Construct, id: string, props: DrVaultStackProps) {
    super(scope, id, props);
    const p = props.policy;
    pinRegion(this, p.regions.secondary);
    // 'rds' is included because RDS (not fully managed by AWS Backup) re-encrypts cross-region snapshot copies
    // with the destination vault key through the RDS service in this region.
    const key = backupVaultKey(this, 'DrVaultKey', {
      description: `CMK for ${p.vaults.dr_copy.name} (cross-region copy destination)`,
      viaServices: ['backup', 'rds'],
    });
    this.vault = lockedVault(this, 'DrCopyVault', p.vaults.dr_copy, key, p.break_glass_role_name);
    new CfnOutput(this, 'DrCopyVaultArn', { value: this.vault.backupVaultArn });
  }
}
