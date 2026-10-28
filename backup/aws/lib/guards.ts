/**
 * Static guards over synthesized CloudFormation templates for the AWS Backup reference. Used by Jest (positive and
 * negative tests) so a regression (unlocked vault, copy without retention, compliance-mode lock, cold storage under
 * 90 days, same-region "DR" copy, AWS-managed vault key) fails the build without AWS credentials.
 */
type Resources = Record<string, { Type: string; Properties?: any }>;
export interface TemplateJson { Resources?: Resources; Rules?: Record<string, any> }
export interface Violation { rule: string; resource: string; detail: string }

const COLD_MIN = 90;

function lifecycleIssues(id: string, where: string, l: any, out: Violation[]) {
  if (!l || l.DeleteAfterDays === undefined) {
    out.push({ rule: 'BKP_NO_RETENTION', resource: id, detail: `${where}: no DeleteAfterDays (recovery points never expire)` });
    return;
  }
  if (l.DeleteAfterDays === -1) out.push({ rule: 'BKP_RETAIN_FOREVER', resource: id, detail: `${where}: DeleteAfterDays=-1` });
  if (l.MoveToColdStorageAfterDays !== undefined && l.DeleteAfterDays - l.MoveToColdStorageAfterDays < COLD_MIN) {
    out.push({ rule: 'BKP_COLD_UNDER_90D', resource: id, detail: `${where}: delete ${l.DeleteAfterDays} - cold ${l.MoveToColdStorageAfterDays} < ${COLD_MIN}` });
  }
}

/** Every plan rule and copy action has explicit, finite retention that satisfies the 90-day cold-storage minimum. */
export function retentionViolations(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type !== 'AWS::Backup::BackupPlan') continue;
    for (const rule of r.Properties?.BackupPlan?.BackupPlanRule ?? []) {
      lifecycleIssues(id, `rule ${rule.RuleName}`, rule.Lifecycle, out);
      const copies = rule.CopyActions ?? [];
      if (copies.length === 0) out.push({ rule: 'BKP_NO_CROSS_REGION_COPY', resource: id, detail: `rule ${rule.RuleName} has no CopyActions` });
      for (const c of copies) lifecycleIssues(id, `rule ${rule.RuleName} copy`, c.Lifecycle, out);
    }
  }
  return out;
}

/** Vaults without a lock, in compliance mode (ChangeableForDays set), without a CMK, not retained, or deletable. */
export function vaultViolations(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type !== 'AWS::Backup::BackupVault') continue;
    const p = r.Properties ?? {};
    if (!p.LockConfiguration) out.push({ rule: 'BKP_VAULT_UNLOCKED', resource: id, detail: 'no LockConfiguration' });
    else {
      if (p.LockConfiguration.ChangeableForDays !== undefined) out.push({ rule: 'BKP_VAULT_COMPLIANCE_LOCK', resource: id, detail: 'ChangeableForDays set => COMPLIANCE mode (irreversible after grace time)' });
      if (p.LockConfiguration.MinRetentionDays === undefined) out.push({ rule: 'BKP_VAULT_LOCK_NO_MIN', resource: id, detail: 'MinRetentionDays required' });
    }
    if (p.EncryptionKeyArn === undefined) out.push({ rule: 'BKP_VAULT_DEFAULT_KEY', resource: id, detail: 'no customer-managed EncryptionKeyArn (falls back to aws/backup)' });
    if ((r as any).DeletionPolicy !== 'Retain') out.push({ rule: 'BKP_VAULT_NOT_RETAINED', resource: id, detail: `DeletionPolicy=${(r as any).DeletionPolicy}` });
    const denies = (p.AccessPolicy?.Statement ?? []).filter((s: any) => s.Effect === 'Deny');
    const acts = denies.flatMap((s: any) => (Array.isArray(s.Action) ? s.Action : [s.Action]));
    if (!acts.includes('backup:DeleteRecoveryPoint')) out.push({ rule: 'BKP_VAULT_DELETE_ALLOWED', resource: id, detail: 'access policy does not deny backup:DeleteRecoveryPoint' });
  }
  return out;
}

const flat = (v: any): string => (typeof v === 'string' ? v : JSON.stringify(v));

/** Copy destinations must name the expected secondary region and must not be the stack's own region. */
export function copyRegionViolations(t: TemplateJson, secondaryRegion: string): Violation[] {
  const out: Violation[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type !== 'AWS::Backup::BackupPlan') continue;
    for (const rule of r.Properties?.BackupPlan?.BackupPlanRule ?? []) {
      for (const c of rule.CopyActions ?? []) {
        const arn = flat(c.DestinationBackupVaultArn);
        if (arn.includes('AWS::Region')) out.push({ rule: 'BKP_COPY_SAME_REGION', resource: id, detail: `rule ${rule.RuleName}: destination uses the stack region` });
        if (!arn.includes(`:backup:${secondaryRegion}:`)) out.push({ rule: 'BKP_COPY_WRONG_REGION', resource: id, detail: `rule ${rule.RuleName}: destination ${arn}` });
      }
    }
  }
  return out;
}

/** Each stack must carry a CloudFormation Rule pinning AWS::Region to `region`. */
export function regionPinViolations(t: TemplateJson, region: string): Violation[] {
  const want = JSON.stringify({ 'Fn::Equals': [{ Ref: 'AWS::Region' }, region] });
  const pinned = Object.values(t.Rules ?? {}).some((rule: any) => (rule.Assertions ?? []).some((a: any) => flat(a.Assert) === want));
  return pinned ? [] : [{ rule: 'BKP_REGION_NOT_PINNED', resource: 'Rules', detail: `no Rule asserting AWS::Region == ${region}` }];
}

export function allViolations(t: TemplateJson): Violation[] {
  return [...retentionViolations(t), ...vaultViolations(t)];
}
