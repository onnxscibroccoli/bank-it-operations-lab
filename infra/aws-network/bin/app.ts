#!/usr/bin/env node
import { App, Aspects } from 'aws-cdk-lib';
import { AwsSolutionsChecks } from 'cdk-nag';
import { LAB_CONTEXT } from '../lib/lab-context';
import { NetworkEdgeStack } from '../lib/network-edge-stack';

const app = new App({ context: LAB_CONTEXT });
new NetworkEdgeStack(app, 'BankItLabNetworkEdge', {
  description: 'Internal edge reference (static synthesis; not deployed)',
});
Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true, reports: true }));
app.synth();
