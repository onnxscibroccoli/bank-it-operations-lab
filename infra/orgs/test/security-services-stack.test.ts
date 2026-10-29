import { Stack, Token } from 'aws-cdk-lib';
import { GUARDDUTY_FEATURES, SECURITY_HUB_STANDARDS, SecurityServicesStack } from '../lib/security-services-stack';
import { expectNoNagFindings, synth } from './helpers';

const { stack, template } = synth((s) => new SecurityServicesStack(s, 'TestSecurityServices'));

describe('SecurityServicesStack', () => {
  test('is environment-agnostic', () => {
    expect(Token.isUnresolved(Stack.of(stack).account)).toBe(true);
    expect(Token.isUnresolved(Stack.of(stack).region)).toBe(true);
  });

  test('GuardDuty detector enabled with all reference protection plans', () => {
    template.resourceCountIs('AWS::GuardDuty::Detector', 1);
    template.hasResourceProperties('AWS::GuardDuty::Detector', {
      Enable: true,
      FindingPublishingFrequency: 'FIFTEEN_MINUTES',
      Features: GUARDDUTY_FEATURES.map((Name) => ({ Name, Status: 'ENABLED' })),
    });
  });

  test('Security Hub: no default standards, consolidated control findings', () => {
    template.hasResourceProperties('AWS::SecurityHub::Hub', {
      EnableDefaultStandards: false, ControlFindingGenerator: 'SECURITY_CONTROL', AutoEnableControls: true,
    });
  });

  test('FSBP and CIS 3.0 standards enabled, region/partition-agnostic, after the hub', () => {
    const stds = template.findResources('AWS::SecurityHub::Standard');
    expect(Object.keys(stds)).toHaveLength(Object.keys(SECURITY_HUB_STANDARDS).length);
    const arns = Object.values(stds).map((s) => JSON.stringify(s.Properties.StandardsArn));
    for (const path of Object.values(SECURITY_HUB_STANDARDS)) {
      expect(arns.some((a) => a.includes(path) && a.includes('AWS::Region') && a.includes('AWS::Partition'))).toBe(true);
    }
    for (const s of Object.values(stds)) expect(s.DependsOn).toEqual([expect.stringMatching(/^SecurityHub/)]);
  });

  test('central configuration with an all-regions finding aggregator', () => {
    template.hasResourceProperties('AWS::SecurityHub::FindingAggregator', { RegionLinkingMode: 'ALL_REGIONS' });
    template.hasResourceProperties('AWS::SecurityHub::OrganizationConfiguration', {
      ConfigurationType: 'CENTRAL', AutoEnable: false, AutoEnableStandards: 'NONE',
    });
    const org = Object.values(template.findResources('AWS::SecurityHub::OrganizationConfiguration'))[0];
    expect(org.DependsOn).toEqual([expect.stringMatching(/^FindingAggregator/)]);
  });

  test('cdk-nag AwsSolutions: no errors or warnings', () => expectNoNagFindings(stack));
});
