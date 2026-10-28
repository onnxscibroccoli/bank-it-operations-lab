/**
 * Negative tests: deliberately insecure fixtures MUST be caught by the static guards and/or cdk-nag.
 * If any of these start passing, a control has been weakened.
 */
import { App, Aspects, RemovalPolicy, Stack } from 'aws-cdk-lib';
import { Annotations, Match, Template } from 'aws-cdk-lib/assertions';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { AwsSolutionsChecks, NIST80053R5Checks } from 'cdk-nag';
import { kmsWildcards, openSecurityGroupRules, rdsPublicOrUnencrypted, selfLoggingBuckets } from '../lib/guards';
import { LAB_CONTEXT } from '../lib/lab-context';
import { NetworkDatabaseStack } from '../lib/network-database-stack';
import { SecureStorageStack } from '../lib/secure-storage-stack';

function fixture(build: (s: Stack) => void) {
  const app = new App({ context: LAB_CONTEXT });
  const stack = new Stack(app, 'BadFixture');
  build(stack);
  Aspects.of(stack).add(new AwsSolutionsChecks({ reports: false }));
  Aspects.of(stack).add(new NIST80053R5Checks({ reports: false }));
  app.synth();
  return { stack, json: Template.fromStack(stack).toJSON() };
}
const errorIds = (stack: Stack) =>
  Annotations.fromStack(stack).findError('*', Match.anyValue()).map((m) => String(m.entry.data).split(':')[0]);

describe('negative: public RDS is caught', () => {
  const { stack, json } = fixture((s) => {
    const vpc = new ec2.Vpc(s, 'Vpc', { maxAzs: 2, natGateways: 0 });
    new rds.DatabaseInstance(s, 'PublicDb', {
      engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_17_9 }),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      publiclyAccessible: true,
      storageEncrypted: false,
      removalPolicy: RemovalPolicy.DESTROY,
    });
  });
  test('guard flags RDS_PUBLIC and RDS_UNENCRYPTED', () => {
    const rules = rdsPublicOrUnencrypted(json).map((v) => v.rule);
    expect(rules).toEqual(expect.arrayContaining(['RDS_PUBLIC', 'RDS_UNENCRYPTED']));
  });
  test('cdk-nag flags it (NIST RDSInstancePublicAccess, AwsSolutions-RDS2)', () => {
    expect(errorIds(stack)).toEqual(expect.arrayContaining(['NIST.800.53.R5-RDSInstancePublicAccess', 'AwsSolutions-RDS2']));
  });
  test('guard flags an RDS instance with PubliclyAccessible omitted (CloudFormation default is not "private")', () => {
    expect(rdsPublicOrUnencrypted({ Resources: { Db: { Type: 'AWS::RDS::DBInstance', Properties: { StorageEncrypted: true, KmsKeyId: 'k' } } } }).map((v) => v.rule)).toEqual(['RDS_PUBLIC']);
  });
});

describe('negative: a bucket that logs to itself is caught', () => {
  // The original defect: serverAccessLogsPrefix with no target bucket => the bucket logs to itself.
  const { json } = fixture((s) => {
    new s3.Bucket(s, 'SelfLogging', { enforceSSL: true, versioned: true, serverAccessLogsPrefix: 'self-access-logs/' });
  });
  test('guard flags the self-logging bucket', () => {
    const flagged = selfLoggingBuckets(json).map((v) => v.resource);
    expect(flagged).toHaveLength(1);
    expect(flagged[0].startsWith('SelfLogging')).toBe(true);
  });
  test('guard flags both members of a two-bucket loop A -> B -> A (raw template; CDK refuses to synth the cycle)', () => {
    const loop = {
      Resources: {
        A: { Type: 'AWS::S3::Bucket', Properties: { LoggingConfiguration: { DestinationBucketName: { Ref: 'B' } } } },
        B: { Type: 'AWS::S3::Bucket', Properties: { LoggingConfiguration: { DestinationBucketName: { Ref: 'A' } } } },
        C: { Type: 'AWS::S3::Bucket', Properties: { LoggingConfiguration: { DestinationBucketName: { Ref: 'A' } } } },
      },
    };
    expect(selfLoggingBuckets(loop).map((v) => v.resource).sort()).toEqual(['A', 'B']);
  });
  test('cdk-nag alone does NOT catch self-logging (AwsSolutions-S1 is satisfied) - which is why the guard exists', () => {
    const app = new App({ context: LAB_CONTEXT });
    const st = new Stack(app, 'S1Only');
    new s3.Bucket(st, 'SelfLogging', { serverAccessLogsPrefix: 'self-access-logs/' });
    Aspects.of(st).add(new AwsSolutionsChecks({ reports: false }));
    app.synth();
    const ids = Annotations.fromStack(st).findError('*', Match.anyValue()).map((m) => String(m.entry.data).split(':')[0]);
    expect(ids).not.toContain('AwsSolutions-S1');
  });
});

describe('negative: KMS key policy with wildcard principal / kms:* is caught', () => {
  const { json } = fixture((s) => {
    const k = new kms.Key(s, 'OpenKey', { enableKeyRotation: true });
    k.addToResourcePolicy(new iam.PolicyStatement({ principals: [new iam.AnyPrincipal()], actions: ['kms:Decrypt'], resources: ['*'] }));
    k.addToResourcePolicy(new iam.PolicyStatement({ principals: [new iam.ArnPrincipal('*')], actions: ['kms:Encrypt'], resources: ['*'] }));
  });
  test('guard flags wildcard principals', () => {
    expect(kmsWildcards(json).filter((v) => v.rule === 'KMS_WILDCARD_PRINCIPAL')).toHaveLength(2);
  });
  test('guard flags the CDK default key policy (account root kms:*) as not least-privilege', () => {
    expect(kmsWildcards(json).map((v) => v.rule)).toContain('KMS_WILDCARD_ACTION');
  });
});

describe('negative: SG open to the internet is caught', () => {
  const { json } = fixture((s) => {
    const vpc = new ec2.Vpc(s, 'Vpc', { maxAzs: 1, natGateways: 0 });
    const sg = new ec2.SecurityGroup(s, 'Open', { vpc, allowAllOutbound: true });
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(5432));
  });
  test('guard flags 0.0.0.0/0 ingress and egress', () => {
    const rules = openSecurityGroupRules(json).map((v) => v.rule);
    expect(rules).toEqual(expect.arrayContaining(['SG_OPEN_INGRESS', 'SG_OPEN_EGRESS']));
  });
});

describe('negative: mutating the real templates is caught', () => {
  test('flipping PubliclyAccessible=true on the real DB is caught', () => {
    const app = new App({ context: LAB_CONTEXT });
    const st = new NetworkDatabaseStack(app, 'MutDb');
    const json = JSON.parse(JSON.stringify(Template.fromStack(st).toJSON()));
    expect(rdsPublicOrUnencrypted(json)).toEqual([]);
    for (const r of Object.values<any>(json.Resources)) if (r.Type === 'AWS::RDS::DBInstance') r.Properties.PubliclyAccessible = true;
    expect(rdsPublicOrUnencrypted(json).map((v) => v.rule)).toEqual(['RDS_PUBLIC']);
  });
  test('re-adding self-logging to the real AccessLogsBucket is caught', () => {
    const app = new App({ context: LAB_CONTEXT });
    const st = new SecureStorageStack(app, 'MutS3');
    const json = JSON.parse(JSON.stringify(Template.fromStack(st).toJSON()));
    expect(selfLoggingBuckets(json)).toEqual([]);
    const id = st.getLogicalId(st.accessLogsBucket.node.defaultChild as s3.CfnBucket);
    json.Resources[id].Properties.LoggingConfiguration = { LogFilePrefix: 'self-access-logs/' };
    expect(selfLoggingBuckets(json).map((v) => v.resource)).toEqual([id]);
  });
  test('adding a wildcard principal to a real key policy is caught', () => {
    const app = new App({ context: LAB_CONTEXT });
    const st = new NetworkDatabaseStack(app, 'MutKms');
    const json = JSON.parse(JSON.stringify(Template.fromStack(st).toJSON()));
    const key = Object.values<any>(json.Resources).find((r) => r.Type === 'AWS::KMS::Key');
    key.Properties.KeyPolicy.Statement.push({ Effect: 'Allow', Principal: { AWS: '*' }, Action: 'kms:Decrypt', Resource: '*' });
    expect(kmsWildcards(json).map((v) => v.rule)).toEqual(['KMS_WILDCARD_PRINCIPAL']);
  });
});
