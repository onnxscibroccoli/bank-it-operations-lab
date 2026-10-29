/**
 * Typed view of config/backup-policy.json plus pure, credential-free validation of the retention rules that AWS
 * Backup enforces at job time (so a bad value fails here, in review, instead of as a failed backup/copy job).
 */
import * as fs from 'fs';
import * as path from 'path';

export interface Lifecycle { move_to_cold_storage_after_days?: number; delete_after_days: number }
export interface VaultLock { mode: 'GOVERNANCE' | 'COMPLIANCE'; min_retention_days: number; max_retention_days: number; changeable_for_days?: number }
export interface VaultCfg { name: string; lock: VaultLock }
export interface RuleCfg {
  name: string;
  schedule_cron_utc: { minute: string; hour: string; day?: string; month?: string; weekDay?: string };
  start_window_minutes: number;
  completion_window_minutes: number;
  enable_continuous_backup: boolean;
  lifecycle: Lifecycle;
  copy_to_dr?: { lifecycle: Lifecycle };
}
export interface BackupPolicy {
  schema_version: string;
  naming_prefix: string;
  regions: { primary: string; secondary: string };
  selection: { tag_key: string; tag_value: string; in_scope_resource_types: string[] };
  vaults: { primary: VaultCfg; dr_copy: VaultCfg };
  break_glass_role_name: string;
  rules: RuleCfg[];
  restore_testing: {
    name: string; schedule_cron_utc: string; start_window_hours: number; recovery_point_window_days: number;
    validation_window_hours: number; protected_resource_type: string;
  };
}

export const POLICY_PATH = path.join(__dirname, '..', 'config', 'backup-policy.json');

export function loadPolicy(file: string = POLICY_PATH): BackupPolicy {
  return JSON.parse(fs.readFileSync(file, 'utf8')) as BackupPolicy;
}

/** AWS Backup: a recovery point moved to cold storage must stay there >= 90 days. */
export const COLD_STORAGE_MIN_DAYS = 90;
/** AWS Backup: continuous backup (PITR) retention is 1..35 days. */
export const CONTINUOUS_MAX_DAYS = 35;
/** AWS Backup Vault Lock bounds (days). */
export const LOCK_MIN_RETENTION_FLOOR = 1;
export const LOCK_MAX_RETENTION_CEILING = 36500;
export const COMPLIANCE_GRACE_MIN_DAYS = 3;
/** Resource types for which AWS Backup supports lifecycle to cold storage (feature-availability table). */
export const COLD_STORAGE_TYPES = new Set(['EBS', 'EFS', 'DynamoDB', 'Timestream', 'VirtualMachine', 'CloudFormation', 'SAPHANA', 'AuroraDSQL']);
/** Resource types whose recovery points AWS Backup can copy cross-Region (DynamoDB only with advanced features). */
export const CROSS_REGION_COPY_TYPES = new Set(['RDS', 'EBS', 'EFS', 'S3', 'DynamoDB', 'EC2', 'Aurora', 'FSx']);

export interface Finding { level: 'error' | 'warning'; code: string; where: string; detail: string }

function checkLifecycle(where: string, l: Lifecycle, out: Finding[]) {
  if (!Number.isInteger(l.delete_after_days) || l.delete_after_days < 1) {
    out.push({ level: 'error', code: 'RETENTION_MISSING', where, detail: 'delete_after_days must be a positive integer (never "keep forever" in a locked vault)' });
  }
  if (l.move_to_cold_storage_after_days !== undefined && l.delete_after_days - l.move_to_cold_storage_after_days < COLD_STORAGE_MIN_DAYS) {
    out.push({
      level: 'error', code: 'COLD_STORAGE_UNDER_90D', where,
      detail: `delete_after_days (${l.delete_after_days}) must be >= move_to_cold_storage_after_days (${l.move_to_cold_storage_after_days}) + ${COLD_STORAGE_MIN_DAYS}`,
    });
  }
}

function checkWithinLock(where: string, days: number, v: VaultCfg, out: Finding[]) {
  if (days < v.lock.min_retention_days || days > v.lock.max_retention_days) {
    out.push({
      level: 'error', code: 'OUTSIDE_VAULT_LOCK', where,
      detail: `retention ${days}d is outside vault lock [${v.lock.min_retention_days}, ${v.lock.max_retention_days}] of ${v.name}; jobs into this vault would fail`,
    });
  }
}

function checkLock(v: VaultCfg, out: Finding[]) {
  const l = v.lock;
  if (l.min_retention_days < LOCK_MIN_RETENTION_FLOOR || l.max_retention_days > LOCK_MAX_RETENTION_CEILING || l.min_retention_days > l.max_retention_days) {
    out.push({ level: 'error', code: 'LOCK_BOUNDS', where: v.name, detail: `invalid lock bounds ${JSON.stringify(l)}` });
  }
  if (l.mode === 'COMPLIANCE') {
    if (l.changeable_for_days === undefined || l.changeable_for_days < COMPLIANCE_GRACE_MIN_DAYS) {
      out.push({ level: 'error', code: 'LOCK_GRACE', where: v.name, detail: `compliance mode needs changeable_for_days >= ${COMPLIANCE_GRACE_MIN_DAYS}` });
    }
    // Lab rule: compliance mode becomes irreversible after the grace time; this reference must never ship it by default.
    out.push({ level: 'error', code: 'LOCK_COMPLIANCE_IN_LAB', where: v.name, detail: 'COMPLIANCE mode is irreversible after grace time; requires a separate approved change, not this lab config' });
  } else if (l.changeable_for_days !== undefined) {
    out.push({ level: 'error', code: 'LOCK_MODE_AMBIGUOUS', where: v.name, detail: 'changeable_for_days makes the lock COMPLIANCE mode; remove it for GOVERNANCE' });
  }
}

export function validatePolicy(p: BackupPolicy): Finding[] {
  const out: Finding[] = [];
  if (p.schema_version !== '1.0.0') out.push({ level: 'error', code: 'SCHEMA_VERSION', where: 'schema_version', detail: String(p.schema_version) });
  if (!p.regions?.primary || p.regions.primary === p.regions.secondary) {
    out.push({ level: 'error', code: 'SAME_REGION_COPY', where: 'regions', detail: 'secondary region must differ from primary for a cross-region copy' });
  }
  for (const v of [p.vaults.primary, p.vaults.dr_copy]) {
    if (!/^[a-zA-Z0-9\-_]{2,50}$/.test(v.name)) out.push({ level: 'error', code: 'VAULT_NAME', where: v.name, detail: 'vault name must match ^[a-zA-Z0-9-_]{2,50}$' });
    if (!v.name.startsWith(p.naming_prefix)) out.push({ level: 'error', code: 'NAMING', where: v.name, detail: `must start with ${p.naming_prefix}` });
    checkLock(v, out);
  }
  const names = new Set<string>();
  for (const r of p.rules) {
    const where = `rule:${r.name}`;
    if (names.has(r.name)) out.push({ level: 'error', code: 'DUPLICATE_RULE', where, detail: 'rule names must be unique' });
    names.add(r.name);
    if (r.start_window_minutes < 60) out.push({ level: 'error', code: 'START_WINDOW', where, detail: 'start window must be >= 60 minutes' });
    if (r.completion_window_minutes < r.start_window_minutes) out.push({ level: 'error', code: 'COMPLETION_WINDOW', where, detail: 'completion window shorter than start window' });
    checkLifecycle(where, r.lifecycle, out);
    checkWithinLock(where, r.lifecycle.delete_after_days, p.vaults.primary, out);
    if (r.enable_continuous_backup) {
      if (r.lifecycle.delete_after_days > CONTINUOUS_MAX_DAYS) out.push({ level: 'error', code: 'CONTINUOUS_RETENTION', where, detail: `continuous backup retention must be <= ${CONTINUOUS_MAX_DAYS} days` });
      if (r.lifecycle.move_to_cold_storage_after_days !== undefined) out.push({ level: 'error', code: 'CONTINUOUS_COLD', where, detail: 'continuous backups cannot transition to cold storage' });
    }
    if (!r.copy_to_dr) {
      out.push({ level: 'error', code: 'NO_DR_COPY', where, detail: 'every rule must copy to the DR vault in the secondary region' });
    } else {
      checkLifecycle(`${where}:copy`, r.copy_to_dr.lifecycle, out);
      checkWithinLock(`${where}:copy`, r.copy_to_dr.lifecycle.delete_after_days, p.vaults.dr_copy, out);
      if (r.copy_to_dr.lifecycle.delete_after_days < r.lifecycle.delete_after_days) {
        out.push({ level: 'warning', code: 'COPY_SHORTER_THAN_SOURCE', where, detail: 'DR copy expires before the primary recovery point' });
      }
    }
    if (r.lifecycle.move_to_cold_storage_after_days !== undefined) {
      const ignored = p.selection.in_scope_resource_types.filter((t) => !COLD_STORAGE_TYPES.has(t));
      if (ignored.length) out.push({ level: 'warning', code: 'COLD_IGNORED_FOR_TYPES', where, detail: `AWS Backup ignores cold-storage transition for: ${ignored.join(', ')} (warm storage billed for full retention)` });
    }
  }
  const noCopy = p.selection.in_scope_resource_types.filter((t) => !CROSS_REGION_COPY_TYPES.has(t));
  if (noCopy.length) out.push({ level: 'error', code: 'TYPE_NOT_COPYABLE', where: 'selection', detail: `no cross-region copy support for: ${noCopy.join(', ')}` });
  if (p.selection.in_scope_resource_types.includes('DynamoDB')) {
    out.push({ level: 'warning', code: 'DYNAMODB_ADVANCED_REQUIRED', where: 'selection', detail: 'DynamoDB cross-region copy and cold storage require AWS Backup advanced DynamoDB features (account opt-in)' });
  }
  if (!/^[a-zA-Z0-9_]{1,50}$/.test(p.restore_testing.name)) out.push({ level: 'error', code: 'RESTORE_TEST_NAME', where: 'restore_testing', detail: 'name must match ^[a-zA-Z0-9_]{1,50}$' });
  return out;
}
