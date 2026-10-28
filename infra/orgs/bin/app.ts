#!/usr/bin/env node
import { App, Aspects } from 'aws-cdk-lib';
import { AwsSolutionsChecks } from 'cdk-nag';
import { LAB_CONTEXT } from '../lib/lab-context';
import { OrgCloudTrailStack } from '../lib/org-cloudtrail-stack';
import { OrgGovernanceStack } from '../lib/org-governance-stack';
import { SecurityServicesStack } from '../lib/security-services-stack';

// Environment-agnostic on purpose: no `env`, no account/region, no lookups. Never deployed by this repo.
const app = new App({ context: LAB_CONTEXT });
new OrgGovernanceStack(app, 'BankItLabOrgGovernance', {
  description: 'Reference: OU layout, SCPs, Security Hub delegated admin (static synthesis lab; not deployed)',
});
new OrgCloudTrailStack(app, 'BankItLabOrgCloudTrail', {
  description: 'Reference: organization CloudTrail (static synthesis lab; not deployed)',
});
new SecurityServicesStack(app, 'BankItLabSecurityServices', {
  description: 'Reference: GuardDuty + Security Hub in delegated admin (static synthesis lab; not deployed)',
});
Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true, reports: true }));
app.synth();
