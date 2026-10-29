#!/usr/bin/env node
import { App, Aspects } from 'aws-cdk-lib';
import { AwsSolutionsChecks, NIST80053R5Checks } from 'cdk-nag';
import { DrVaultStack } from '../lib/dr-vault-stack';
import { LAB_CONTEXT, POLICY } from '../lib/lab-context';
import { PrimaryBackupStack } from '../lib/primary-backup-stack';
import { validatePolicy } from '../lib/policy';

// Fail synthesis on any config error (retention, cold storage, vault lock bounds, regions).
const errors = validatePolicy(POLICY).filter((f) => f.level === 'error');
if (errors.length) throw new Error(`config/backup-policy.json invalid:\n${errors.map((e) => `${e.code} ${e.where}: ${e.detail}`).join('\n')}`);

// Environment-agnostic on purpose: no `env`, no account, no lookups. Region intent is enforced at deploy time by a
// CloudFormation Rule in each stack (PinRegion). Never deployed from here.
const app = new App({ context: LAB_CONTEXT });
new DrVaultStack(app, 'BankItLabBackupDrVault', {
  policy: POLICY,
  description: `AWS Backup DR copy vault, intended region ${POLICY.regions.secondary} (static synthesis lab; not deployed)`,
});
new PrimaryBackupStack(app, 'BankItLabBackupPrimary', {
  policy: POLICY,
  description: `AWS Backup vault, plan, cross-region copy and restore testing, intended region ${POLICY.regions.primary} (static synthesis lab; not deployed)`,
});
Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true, reports: true }));
Aspects.of(app).add(new NIST80053R5Checks({ verbose: true, reports: true }));
app.synth();
