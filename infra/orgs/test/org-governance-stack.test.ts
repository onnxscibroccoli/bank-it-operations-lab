import { Stack, Token } from 'aws-cdk-lib';
import { Match } from 'aws-cdk-lib/assertions';
import { OrgGovernanceStack } from '../lib/org-governance-stack';
import { OU_LAYOUT } from '../lib/ou-layout';
import { ROOT_SCP_IDS, SCPS } from '../lib/scps';
import { expectNoNagFindings, synth } from './helpers';

const { stack, template } = synth((s) => new OrgGovernanceStack(s, 'TestOrgGovernance'));

describe('OrgGovernanceStack', () => {
  test('is environment-agnostic', () => {
    expect(Token.isUnresolved(Stack.of(stack).account)).toBe(true);
    expect(Token.isUnresolved(Stack.of(stack).region)).toBe(true);
  });

  test('root id and security account are validated parameters (no lookups)', () => {
    template.hasParameter('OrgRootId', { Type: 'String', AllowedPattern: '^r-[0-9a-z]{4,32}$' });
    template.hasParameter('SecurityToolingAccountId', { Type: 'String', AllowedPattern: '^\\d{12}$' });
  });

  test('creates the reference OU layout', () => {
    template.resourceCountIs('AWS::Organizations::OrganizationalUnit', OU_LAYOUT.length);
    for (const ou of OU_LAYOUT.filter((o) => !o.parent)) {
      template.hasResourceProperties('AWS::Organizations::OrganizationalUnit', { Name: ou.name, ParentId: { Ref: 'OrgRootId' } });
    }
    template.hasResourceProperties('AWS::Organizations::OrganizationalUnit', {
      Name: 'Prod', ParentId: { 'Fn::GetAtt': [Match.stringLikeRegexp('^OuWorkloads'), 'Id'] },
    });
  });

  test('one SERVICE_CONTROL_POLICY per definition, content identical to source', () => {
    template.resourceCountIs('AWS::Organizations::Policy', SCPS.length);
    for (const s of SCPS) {
      template.hasResourceProperties('AWS::Organizations::Policy', {
        Name: s.name, Type: 'SERVICE_CONTROL_POLICY', Content: s.document,
      });
    }
  });

  test('every SCP has a target; only root-level SCPs target the root', () => {
    for (const s of SCPS) {
      const p = Object.values(template.findResources('AWS::Organizations::Policy', { Properties: { Name: s.name } }))[0];
      expect(p.Properties.TargetIds.length).toBeGreaterThan(0);
      const onRoot = JSON.stringify(p.Properties.TargetIds).includes('"Ref":"OrgRootId"');
      expect(onRoot).toBe(ROOT_SCP_IDS.includes(s.id));
    }
  });

  test('every target (root and each OU) has at most 4 custom SCPs (+FullAWSAccess = 5)', () => {
    const counts = new Map<string, number>();
    for (const p of Object.values(template.findResources('AWS::Organizations::Policy'))) {
      for (const t of p.Properties.TargetIds) counts.set(JSON.stringify(t), (counts.get(JSON.stringify(t)) ?? 0) + 1);
    }
    for (const n of counts.values()) expect(n).toBeLessThanOrEqual(4);
  });

  test('Suspended OU gets the deny-all quarantine SCP', () => {
    template.hasResourceProperties('AWS::Organizations::Policy', {
      Name: 'BankItLab-DenyAllSuspended',
      TargetIds: [{ 'Fn::GetAtt': [Match.stringLikeRegexp('^OuSuspended'), 'Id'] }],
    });
  });

  test('Security Hub delegated admin points at the parameterised account', () => {
    template.hasResourceProperties('AWS::SecurityHub::DelegatedAdmin', { AdminAccountId: { Ref: 'SecurityToolingAccountId' } });
  });

  test('cdk-nag AwsSolutions: no errors or warnings', () => expectNoNagFindings(stack));
});
