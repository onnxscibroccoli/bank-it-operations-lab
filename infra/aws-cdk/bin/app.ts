#!/usr/bin/env node
import { App, Aspects } from 'aws-cdk-lib';
import { AwsSolutionsChecks } from 'cdk-nag';
import { LAB_CONTEXT } from '../lib/lab-context';
import { SecureStorageStack } from '../lib/secure-storage-stack';

// Environment-agnostic on purpose: no `env`, no account/region, no lookups.
const app = new App({ context: LAB_CONTEXT });
new SecureStorageStack(app, 'BankItLabSecureStorage', {
  description: 'BANK-AWS-001 secure storage (static synthesis lab; not deployed)',
});
Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true, reports: true }));
app.synth();
