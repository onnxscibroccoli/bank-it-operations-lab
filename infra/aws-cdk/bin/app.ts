#!/usr/bin/env node
import { App, Aspects } from 'aws-cdk-lib';
import { AwsSolutionsChecks, NIST80053R5Checks } from 'cdk-nag';
import { LAB_CONTEXT } from '../lib/lab-context';
import { NetworkDatabaseStack } from '../lib/network-database-stack';
import { SecureStorageStack } from '../lib/secure-storage-stack';

// Environment-agnostic on purpose: no `env`, no account/region, no lookups. Never deployed from here.
const app = new App({ context: LAB_CONTEXT });
new SecureStorageStack(app, 'BankItLabSecureStorage', {
  description: 'Secure storage (static synthesis lab; not deployed)',
});
new NetworkDatabaseStack(app, 'BankItLabNetworkDatabase', {
  description: 'Private VPC + private PostgreSQL (static synthesis lab; not deployed)',
});
// Two cdk-nag packs: AwsSolutions + NIST 800-53 Rev 5 (no second pack was named in prior repo context).
Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true, reports: true }));
Aspects.of(app).add(new NIST80053R5Checks({ verbose: true, reports: true }));
app.synth();
