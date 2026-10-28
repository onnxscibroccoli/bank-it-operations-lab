import { CfnElement, Stack, Token } from 'aws-cdk-lib';
import { Match } from 'aws-cdk-lib/assertions';
import { allViolations, kmsWildcards, openSecurityGroupRules, rdsPublicOrUnencrypted } from '../lib/guards';
import { DB_PORT, NetworkDatabaseStack } from '../lib/network-database-stack';
import { NAG_PACKS, nagFindings, suppressionsIn, synthWithNag } from './helpers';

const { stack, template } = synthWithNag((app) => new NetworkDatabaseStack(app, 'TestNetDb'));
const json = template.toJSON();
const lid = (c: { node: { defaultChild?: unknown } }) => stack.getLogicalId(c.node.defaultChild as CfnElement);

describe('NetworkDatabaseStack', () => {
  test('is environment-agnostic (no account/region)', () => {
    expect(Token.isUnresolved(Stack.of(stack).account)).toBe(true);
    expect(Token.isUnresolved(Stack.of(stack).region)).toBe(true);
  });

  test('VPC: isolated subnets only, no IGW, no NAT, no routes, no public IP mapping', () => {
    template.resourceCountIs('AWS::EC2::VPC', 1);
    template.resourceCountIs('AWS::EC2::InternetGateway', 0);
    template.resourceCountIs('AWS::EC2::NatGateway', 0);
    template.resourceCountIs('AWS::EC2::Route', 0);
    template.resourceCountIs('AWS::EC2::EIP', 0);
    for (const s of Object.values(template.findResources('AWS::EC2::Subnet'))) {
      expect(s.Properties.MapPublicIpOnLaunch).toBe(false);
      expect(JSON.stringify(s.Properties.Tags)).toContain('Isolated');
    }
  });

  test('VPC flow logs (ALL) to a KMS-encrypted log group; default SG restricted', () => {
    template.hasResourceProperties('AWS::EC2::FlowLog', { TrafficType: 'ALL', LogDestinationType: 'cloud-watch-logs' });
    for (const g of Object.values(template.findResources('AWS::Logs::LogGroup'))) {
      expect(g.Properties.KmsKeyId).toBeDefined();
      expect(g.Properties.RetentionInDays).toBe(365);
    }
    template.resourceCountIs('Custom::VpcRestrictDefaultSG', 1);
  });

  test('RDS PostgreSQL is private, in the isolated db subnets, encrypted with the CMK', () => {
    template.hasResourceProperties('AWS::RDS::DBInstance', {
      Engine: 'postgres',
      PubliclyAccessible: false,
      StorageEncrypted: true,
      KmsKeyId: { 'Fn::GetAtt': [lid(stack.dbKey), 'Arn'] },
      PerformanceInsightsKMSKeyId: { 'Fn::GetAtt': [lid(stack.dbKey), 'Arn'] },
      MultiAZ: true,
      DeletionProtection: true,
      EnableIAMDatabaseAuthentication: true,
      Port: String(DB_PORT),
      EnableCloudwatchLogsExports: ['postgresql', 'upgrade'],
    });
    const dbSubnetIds = stack.vpc.selectSubnets({ subnetGroupName: 'db' }).subnets.map((s) => ({ Ref: lid(s) }));
    template.hasResourceProperties('AWS::RDS::DBSubnetGroup', { SubnetIds: dbSubnetIds });
    template.hasResourceProperties('AWS::RDS::DBParameterGroup', { Parameters: Match.objectLike({ 'rds.force_ssl': '1' }) });
    template.hasResourceProperties('AWS::SecretsManager::Secret', { KmsKeyId: { 'Fn::GetAtt': [lid(stack.dbKey), 'Arn'] } });
    template.resourceCountIs('AWS::SecretsManager::RotationSchedule', 1);
    template.resourceCountIs('AWS::Backup::BackupSelection', 1);
    expect(rdsPublicOrUnencrypted(json)).toEqual([]);
  });

  test('security groups: no 0.0.0.0/0, DB reachable only SG-to-SG on the DB port', () => {
    expect(openSecurityGroupRules(json)).toEqual([]);
    const ingress = Object.values(template.findResources('AWS::EC2::SecurityGroupIngress'));
    const dbIngress = ingress.filter((r) => JSON.stringify(r.Properties.GroupId).includes(lid(stack.dbSecurityGroup)));
    expect(dbIngress.length).toBeGreaterThan(0);
    for (const r of dbIngress) {
      expect(r.Properties.FromPort).toBe(DB_PORT);
      expect(r.Properties.ToPort).toBe(DB_PORT);
      expect(r.Properties.SourceSecurityGroupId).toBeDefined();
      expect(r.Properties.CidrIp).toBeUndefined();
    }
    for (const r of ingress) expect(r.Properties.SourceSecurityGroupId).toBeDefined();
    for (const r of Object.values(template.findResources('AWS::EC2::SecurityGroupEgress'))) {
      expect(r.Properties.DestinationSecurityGroupId).toBeDefined();
    }
  });

  test('CMKs: rotation on, no wildcard principals, no kms:* (least-privilege key policies)', () => {
    template.resourceCountIs('AWS::KMS::Key', 2);
    for (const k of Object.values(template.findResources('AWS::KMS::Key'))) {
      expect(k.Properties.EnableKeyRotation).toBe(true);
      expect(k.DeletionPolicy).toBe('Retain');
    }
    expect(kmsWildcards(json)).toEqual([]);
  });

  test('IAM: no inline policies attached to roles defined here', () => {
    template.resourceCountIs('AWS::IAM::Policy', 0);
  });

  test('all static guards pass on the real template', () => {
    expect(allViolations(json)).toEqual([]);
  });

  test.each(NAG_PACKS)('cdk-nag %s: zero unsuppressed errors and warnings', (pack) => {
    expect(nagFindings(stack, 'error', pack)).toHaveLength(0);
    expect(nagFindings(stack, 'warning', pack)).toHaveLength(0);
  });

  test('only registered exceptions are suppressed (EX-03, EX-04)', () => {
    const s = suppressionsIn(template);
    expect(s.map((x) => `${x.rule}@${x.logicalId}`).sort()).toEqual(
      [
        `AwsSolutions-IAM4@${stack.getLogicalId(stack.node.findChild('BackupPlan').node.findChild('Postgres').node.findChild('Role').node.defaultChild as CfnElement)}`,
        `AwsSolutions-IAM5@${stack.getLogicalId(stack.node.findChild('RdsMonitoringPolicy').node.defaultChild as CfnElement)}`,
      ].sort(),
    );
    for (const x of s) expect(x.reason).toMatch(/^EX-0[34]: /);
  });
});
