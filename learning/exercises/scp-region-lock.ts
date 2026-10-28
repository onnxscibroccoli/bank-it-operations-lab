// Week 6 exercise. Copy into $PR6/infra/orgs as scratch-scp-exercise.ts, run with
//   npx ts-node --transpile-only scratch-scp-exercise.ts
// then delete it. It imports the delivered SCP source, offline evaluator and linter, and never writes files.
import { SCPS } from './lib/scps';
import { deniedBy } from './lib/scp-evaluator';
import { lintScp } from './lib/policy-lint';

const rl = SCPS.find((s) => s.id === 'region-lock')!;
const cases: [string, any][] = [
  ['ec2:RunInstances in eu-west-1', { action: 'ec2:RunInstances', keys: { 'aws:RequestedRegion': 'eu-west-1', 'aws:PrincipalArn': 'arn:aws:iam::111111111111:role/App' } }],
  ['ec2:RunInstances in us-east-1', { action: 'ec2:RunInstances', keys: { 'aws:RequestedRegion': 'us-east-1', 'aws:PrincipalArn': 'arn:aws:iam::111111111111:role/App' } }],
  ['ec2:RunInstances in eu-west-1 as OrgBreakGlass', { action: 'ec2:RunInstances', keys: { 'aws:RequestedRegion': 'eu-west-1', 'aws:PrincipalArn': 'arn:aws:iam::111111111111:role/OrgBreakGlass' } }],
];
for (const [label, ctx] of cases) console.log(`${label}: ${deniedBy(rl.document, ctx) ?? 'not denied'}`);

// Failure injection: turn the Deny into an Allow (in memory only) and lint it.
const bad = JSON.parse(JSON.stringify(rl));
bad.document.Statement[0].Effect = 'Allow';
console.log('lint findings after Deny->Allow:', JSON.stringify(lintScp(bad)));
