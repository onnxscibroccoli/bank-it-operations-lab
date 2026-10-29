import { Stack, Token } from 'aws-cdk-lib';
import { NetworkEdgeStack } from '../lib/network-edge-stack';
import { REQUIRED_TAGS } from '../lib/lab-context';
import { nagErrors, synth } from './helpers';

const { stack, template } = synth((scope) => new NetworkEdgeStack(scope, 'TestEdge'));

describe('NetworkEdgeStack', () => {
  test('is environment-agnostic aside from deploy-time parameters', () => {
    expect(Token.isUnresolved(Stack.of(stack).account)).toBe(true);
    expect(template.findParameters('AmiId')).toBeDefined();
    expect(template.findParameters('CertificateArn')).toBeDefined();
  });

  test('no internet path and no SSH security-group rule', () => {
    template.resourceCountIs('AWS::EC2::InternetGateway', 0);
    template.resourceCountIs('AWS::EC2::NatGateway', 0);
    template.resourceCountIs('AWS::EC2::EIP', 0);
    const groups = template.findResources('AWS::EC2::SecurityGroup');
    const blob = JSON.stringify(groups);
    expect(blob).not.toContain('0.0.0.0/0');
    expect(blob).not.toContain('"FromPort":22');
    expect(blob).not.toContain('"ToPort":22');
    template.hasResourceProperties('AWS::ElasticLoadBalancingV2::LoadBalancer', { Scheme: 'internal' });
  });

  test('IMDSv2 required, detailed monitoring on, private DNS and a documentation-range VPN peer', () => {
    template.hasResourceProperties('AWS::EC2::LaunchTemplate', {
      LaunchTemplateData: {
        MetadataOptions: { HttpTokens: 'required' },
        Monitoring: { Enabled: true },
      },
    });
    template.hasResourceProperties('AWS::Route53::HostedZone', { Name: 'edge.lab.internal.' });
    template.hasResourceProperties('AWS::EC2::CustomerGateway', { IpAddress: '203.0.113.10', Type: 'ipsec.1' });
    template.resourceCountIs('AWS::EC2::VPNConnection', 1);
    template.hasResourceProperties('AWS::Budgets::Budget', { Budget: { BudgetLimit: { Amount: 25, Unit: 'USD' } } });
  });

  test('required tags are on the stack', () => {
    const tags = template.toJSON().Resources;
    const alb = Object.values(tags).find((r) => (r as { Type: string }).Type === 'AWS::ElasticLoadBalancingV2::LoadBalancer') as {
      Properties: { Tags?: Array<{ Key: string; Value: string }> };
    };
    for (const [key, value] of Object.entries(REQUIRED_TAGS)) {
      expect(alb.Properties.Tags).toEqual(expect.arrayContaining([expect.objectContaining({ Key: key, Value: value })]));
    }
  });

  test('cdk-nag AwsSolutions has no unsuppressed errors', () => {
    const errors = nagErrors(stack);
    if (errors.length) {
      // Surface the rule text in the assertion so a failure is actionable.
      expect(errors.map((e) => e.entry.data).join('\n')).toBe('');
    }
    expect(errors).toHaveLength(0);
  });
});
