/** Config-level checks: the shipped policy is valid, and each class of bad value is rejected (negative controls). */
import { BackupPolicy, loadPolicy, validatePolicy } from '../lib/policy';
import { clone } from './helpers';

const base = loadPolicy();
const codes = (p: BackupPolicy) => validatePolicy(p).filter((f) => f.level === 'error').map((f) => f.code);

describe('shipped config/backup-policy.json', () => {
  test('has no error-level findings', () => expect(codes(base)).toEqual([]));
  test('regions match the orgs region-lock allow-list (us-east-1 primary, us-west-2 secondary)', () => {
    expect(base.regions).toMatchObject({ primary: 'us-east-1', secondary: 'us-west-2' });
  });
  test('every rule copies to DR and both vaults use GOVERNANCE lock', () => {
    expect(base.rules.every((r) => r.copy_to_dr)).toBe(true);
    expect([base.vaults.primary.lock.mode, base.vaults.dr_copy.lock.mode]).toEqual(['GOVERNANCE', 'GOVERNANCE']);
  });
  test('warns that RDS/S3 ignore cold-storage transition (cost implication documented)', () => {
    const w = validatePolicy(base).filter((f) => f.code === 'COLD_IGNORED_FOR_TYPES');
    expect(w.length).toBeGreaterThan(0);
    expect(w[0].detail).toMatch(/RDS/);
  });
});

describe('negative: invalid policies are rejected', () => {
  const cases: [string, (p: BackupPolicy) => void, string][] = [
    ['cold storage < 90 days before deletion', (p) => { p.rules[1].lifecycle = { move_to_cold_storage_after_days: 90, delete_after_days: 150 }; }, 'COLD_STORAGE_UNDER_90D'],
    ['copy cold storage < 90 days', (p) => { p.rules[1].copy_to_dr!.lifecycle = { move_to_cold_storage_after_days: 30, delete_after_days: 100 }; }, 'COLD_STORAGE_UNDER_90D'],
    ['rule without DR copy', (p) => { delete p.rules[0].copy_to_dr; }, 'NO_DR_COPY'],
    ['same-region "DR"', (p) => { p.regions.secondary = p.regions.primary; }, 'SAME_REGION_COPY'],
    ['retention below vault-lock minimum', (p) => { p.rules[0].lifecycle.delete_after_days = 7; p.rules[0].copy_to_dr!.lifecycle.delete_after_days = 7; }, 'OUTSIDE_VAULT_LOCK'],
    ['copy retention above DR vault-lock maximum', (p) => { p.rules[1].copy_to_dr!.lifecycle.delete_after_days = 2557; }, 'OUTSIDE_VAULT_LOCK'],
    ['continuous backup over 35 days', (p) => { p.rules[0].lifecycle.delete_after_days = 60; }, 'CONTINUOUS_RETENTION'],
    ['continuous backup to cold storage', (p) => { p.rules[0].lifecycle.move_to_cold_storage_after_days = 1; }, 'CONTINUOUS_COLD'],
    ['compliance-mode lock', (p) => { p.vaults.dr_copy.lock.mode = 'COMPLIANCE'; p.vaults.dr_copy.lock.changeable_for_days = 3; }, 'LOCK_COMPLIANCE_IN_LAB'],
    ['compliance grace < 3 days', (p) => { p.vaults.dr_copy.lock.mode = 'COMPLIANCE'; p.vaults.dr_copy.lock.changeable_for_days = 1; }, 'LOCK_GRACE'],
    ['governance with changeable_for_days', (p) => { p.vaults.primary.lock.changeable_for_days = 3; }, 'LOCK_MODE_AMBIGUOUS'],
    ['lock min > max', (p) => { p.vaults.primary.lock.min_retention_days = 500; }, 'LOCK_BOUNDS'],
    ['missing retention', (p) => { (p.rules[0].lifecycle as any).delete_after_days = undefined; }, 'RETENTION_MISSING'],
    ['vault outside naming convention', (p) => { p.vaults.primary.name = 'prod-vault'; }, 'NAMING'],
    ['non-copyable resource type', (p) => { p.selection.in_scope_resource_types.push('RedshiftServerless'); }, 'TYPE_NOT_COPYABLE'],
    ['start window under 60 minutes', (p) => { p.rules[0].start_window_minutes = 30; }, 'START_WINDOW'],
  ];
  test.each(cases)('%s', (_name, mutate, code) => {
    const p = clone(base);
    mutate(p);
    expect(codes(p)).toContain(code);
  });
});
