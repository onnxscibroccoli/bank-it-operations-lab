import { Stack } from 'aws-cdk-lib';
import { Construct } from 'constructs';

/**
 * Trust-policy designs for the AWS Backup service role (EX-04). Selected with the CDK context key
 * `bankItLab:backupTrustMode`; the default is the most restrictive design that was already in place ('vault-arn').
 * Nothing here is removed silently: every mode keeps StringEquals aws:SourceAccount, and no mode uses an ...IfExists
 * operator (IfExists would let the condition pass when AWS omits the key, i.e. silently drop the restriction).
 *
 *  - 'vault-arn' (DEFAULT, unchanged): SourceAccount + ArnEquals aws:SourceArn = this backup vault ARN.
 *     Most restrictive. RUNTIME-UNVERIFIED: AWS Backup does not document sending aws:SourceArn (or which ARN: vault,
 *     plan, job, recovery point) on sts:AssumeRole of a customer service role. If the key is absent or carries a
 *     different ARN, AssumeRole is denied and backup jobs fail (fail-closed: availability risk, not exposure).
 *  - 'account-region-backup-arn' (FALLBACK 1): SourceAccount + ArnLike aws:SourceArn = arn:<p>:backup:<region>:<acct>:*
 *     Same shape as AWS's own backup.amazonaws.com example in the Aurora DSQL confused-deputy page. Still fails closed
 *     if the key is absent. Wider: any AWS Backup resource of this account/region.
 *  - 'source-account-only' (FALLBACK 2): StringEquals aws:SourceAccount only. Pattern already used by backup/aws/**
 *     and the other service roles in this stack. Least restrictive design still allowed; requires owner sign-off.
 */
export const BACKUP_TRUST_MODES = ['vault-arn', 'account-region-backup-arn', 'source-account-only'] as const;
export type BackupTrustMode = (typeof BACKUP_TRUST_MODES)[number];
export const BACKUP_TRUST_MODE_CONTEXT_KEY = 'bankItLab:backupTrustMode';
export const DEFAULT_BACKUP_TRUST_MODE: BackupTrustMode = 'vault-arn';

export function resolveBackupTrustMode(scope: Construct): BackupTrustMode {
  const raw = scope.node.tryGetContext(BACKUP_TRUST_MODE_CONTEXT_KEY) ?? DEFAULT_BACKUP_TRUST_MODE;
  if (!(BACKUP_TRUST_MODES as readonly string[]).includes(raw)) {
    throw new Error(`${BACKUP_TRUST_MODE_CONTEXT_KEY} must be one of ${BACKUP_TRUST_MODES.join(', ')} (got ${JSON.stringify(raw)})`);
  }
  return raw as BackupTrustMode;
}

export function backupTrustConditions(stack: Stack, mode: BackupTrustMode, vaultArn: string): Record<string, Record<string, unknown>> {
  const base = { StringEquals: { 'aws:SourceAccount': stack.account } };
  switch (mode) {
    case 'vault-arn':
      return { ...base, ArnEquals: { 'aws:SourceArn': vaultArn } };
    case 'account-region-backup-arn':
      return { ...base, ArnLike: { 'aws:SourceArn': `arn:${stack.partition}:backup:${stack.region}:${stack.account}:*` } };
    case 'source-account-only':
      return base;
  }
}
