import { Duration, RemovalPolicy, Stack, StackProps, Token } from 'aws-cdk-lib';
import * as backup from 'aws-cdk-lib/aws-backup';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as events from 'aws-cdk-lib/aws-events';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as rds from 'aws-cdk-lib/aws-rds';
import { NagSuppressions } from 'cdk-nag';
import { Construct } from 'constructs';
import { leastPrivilegeKey } from './least-privilege-key';

export const DB_PORT = 5433; // non-default port (AwsSolutions-RDS11)
export const DB_INSTANCE_ID = 'bank-it-lab-postgres';

/**
 * Private network + private PostgreSQL (remediation of the VPC/RDS gap).
 * Environment-agnostic: no account/region, no lookups; synthesizes without AWS credentials.
 *
 * - VPC with PRIVATE_ISOLATED subnets only: no IGW, no NAT, no public subnets, no route to the internet.
 * - Default security group restricted (no rules).
 * - VPC flow logs (ALL traffic) to a KMS-encrypted CloudWatch Logs group (not S3, so no log-bucket recursion).
 * - RDS PostgreSQL: publiclyAccessible=false, isolated subnets, storage + Performance Insights + secret encrypted
 *   with a customer-managed key, Multi-AZ, deletion protection, backups, IAM auth, CloudWatch log exports,
 *   enhanced monitoring, non-default port.
 * - Security groups: DB SG allows ingress only from the app SG on DB_PORT; no egress. App SG egress only to the DB SG.
 */
export class NetworkDatabaseStack extends Stack {
  public readonly vpc: ec2.Vpc;
  public readonly dbKey: kms.Key;
  public readonly logsKey: kms.Key;
  public readonly appSecurityGroup: ec2.SecurityGroup;
  public readonly dbSecurityGroup: ec2.SecurityGroup;
  public readonly database: rds.DatabaseInstance;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    this.logsKey = leastPrivilegeKey(this, 'LogsKey', {
      description: 'CMK for VPC flow log and RDS log groups (CloudWatch Logs only)',
      viaServices: ['logs'],
      allowCloudWatchLogs: true,
    });
    this.dbKey = leastPrivilegeKey(this, 'DatabaseKey', {
      description: 'CMK for RDS storage, Performance Insights and the DB credentials secret',
      viaServices: ['rds', 'secretsmanager', 'backup'],
    });

    this.vpc = new ec2.Vpc(this, 'Vpc', {
      ipAddresses: ec2.IpAddresses.cidr('10.40.0.0/16'),
      maxAzs: 2,
      natGateways: 0,
      createInternetGateway: false,
      restrictDefaultSecurityGroup: true,
      subnetConfiguration: [
        { name: 'app', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, cidrMask: 24 },
        { name: 'db', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, cidrMask: 24 },
      ],
    });

    // Flow logs -> CloudWatch Logs (KMS). Role uses a customer-managed policy (no inline policy, no AWS-managed policy)
    // and is handed to the flow log as immutable so CDK does not attach an inline DefaultPolicy.
    const flowLogGroup = new logs.LogGroup(this, 'FlowLogGroup', {
      encryptionKey: this.logsKey,
      retention: logs.RetentionDays.ONE_YEAR,
      removalPolicy: RemovalPolicy.RETAIN,
    });
    const flowLogRole = new iam.Role(this, 'FlowLogRole', {
      assumedBy: new iam.ServicePrincipal('vpc-flow-logs.amazonaws.com', {
        conditions: { StringEquals: { 'aws:SourceAccount': this.account } },
      }),
    });
    const flowLogPolicy = new iam.ManagedPolicy(this, 'FlowLogPolicy', {
      statements: [
        new iam.PolicyStatement({
          actions: ['logs:CreateLogStream', 'logs:PutLogEvents', 'logs:DescribeLogStreams'],
          resources: [flowLogGroup.logGroupArn],
        }),
      ],
    });
    flowLogRole.addManagedPolicy(flowLogPolicy);
    this.vpc.addFlowLog('FlowLog', {
      destination: ec2.FlowLogDestination.toCloudWatchLogs(
        flowLogGroup,
        iam.Role.fromRoleArn(this, 'FlowLogRoleRef', flowLogRole.roleArn, { mutable: false }),
      ),
      trafficType: ec2.FlowLogTrafficType.ALL,
    });

    this.appSecurityGroup = new ec2.SecurityGroup(this, 'AppSecurityGroup', {
      vpc: this.vpc,
      description: 'Application tier: egress only to the database SG on the DB port',
      allowAllOutbound: false,
    });
    this.dbSecurityGroup = new ec2.SecurityGroup(this, 'DatabaseSecurityGroup', {
      vpc: this.vpc,
      description: 'PostgreSQL: ingress only from the application SG on the DB port; no egress',
      allowAllOutbound: false,
    });
    this.dbSecurityGroup.addIngressRule(this.appSecurityGroup, ec2.Port.tcp(DB_PORT), 'app tier to PostgreSQL');
    this.appSecurityGroup.addEgressRule(this.dbSecurityGroup, ec2.Port.tcp(DB_PORT), 'app tier to PostgreSQL');

    const monitoringRole = new iam.Role(this, 'RdsMonitoringRole', {
      assumedBy: new iam.ServicePrincipal('monitoring.rds.amazonaws.com', {
        conditions: { StringEquals: { 'aws:SourceAccount': this.account } },
      }),
    });
    const monitoringPolicy = new iam.ManagedPolicy(this, 'RdsMonitoringPolicy', {
      statements: [
          new iam.PolicyStatement({
            actions: ['logs:CreateLogGroup', 'logs:PutRetentionPolicy'],
            resources: [`arn:${this.partition}:logs:${this.region}:${this.account}:log-group:RDSOSMetrics`],
          }),
          new iam.PolicyStatement({
            actions: ['logs:CreateLogStream', 'logs:PutLogEvents', 'logs:DescribeLogStreams', 'logs:GetLogEvents'],
            resources: [`arn:${this.partition}:logs:${this.region}:${this.account}:log-group:RDSOSMetrics:log-stream:*`],
          }),
        ],
    });
    monitoringRole.addManagedPolicy(monitoringPolicy);

    // RDS log export groups are pre-created (KMS-encrypted, 1y retention) instead of `cloudwatchLogsRetention`,
    // which would add a LogRetention Lambda with an AWS-managed policy, an inline policy and Resource::*.
    const dbLogGroups = ['postgresql', 'upgrade'].map(
      (t) =>
        new logs.LogGroup(this, `PostgresLogGroup-${t}`, {
          logGroupName: `/aws/rds/instance/${DB_INSTANCE_ID}/${t}`,
          encryptionKey: this.logsKey,
          retention: logs.RetentionDays.ONE_YEAR,
          removalPolicy: RemovalPolicy.RETAIN,
        }),
    );

    this.database = new rds.DatabaseInstance(this, 'Postgres', {
      instanceIdentifier: DB_INSTANCE_ID,
      engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_17_9 }),
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE4_GRAVITON, ec2.InstanceSize.MEDIUM),
      vpc: this.vpc,
      vpcSubnets: { subnetGroupName: 'db' },
      publiclyAccessible: false,
      securityGroups: [this.dbSecurityGroup],
      port: DB_PORT,
      credentials: rds.Credentials.fromGeneratedSecret('bankadmin', { encryptionKey: this.dbKey }),
      storageEncrypted: true,
      storageEncryptionKey: this.dbKey,
      multiAz: true,
      allocatedStorage: 50,
      maxAllocatedStorage: 200,
      storageType: rds.StorageType.GP3,
      deletionProtection: true,
      removalPolicy: RemovalPolicy.RETAIN,
      backupRetention: Duration.days(14),
      copyTagsToSnapshot: true,
      iamAuthentication: true,
      autoMinorVersionUpgrade: true,
      cloudwatchLogsExports: ['postgresql', 'upgrade'],
      monitoringInterval: Duration.seconds(60),
      monitoringRole,
      enablePerformanceInsights: true,
      performanceInsightEncryptionKey: this.dbKey,
      parameterGroup: new rds.ParameterGroup(this, 'PostgresParams', {
        engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_17_9 }),
        parameters: { 'rds.force_ssl': '1', log_connections: '1', log_disconnections: '1' },
      }),
    });
  
    dbLogGroups.forEach((g) => this.database.node.addDependency(g));

    // Secret rotation (AwsSolutions-SMG4 / NIST SecretsManagerRotationEnabled). The hosted rotation function runs in
    // the isolated app subnets and reaches Secrets Manager through a private interface endpoint (no internet path).
    // Least-privilege SGs: no 0.0.0.0/0 egress anywhere. CDK wires rotation->endpoint (443) and rotation->DB rules.
    const endpointSg = new ec2.SecurityGroup(this, 'SecretsManagerEndpointSecurityGroup', {
      vpc: this.vpc,
      description: 'Secrets Manager interface endpoint: ingress 443 only from the rotation function; no egress',
      allowAllOutbound: false,
    });
    const rotationSg = new ec2.SecurityGroup(this, 'RotationSecurityGroup', {
      vpc: this.vpc,
      description: 'Secret rotation function: egress only to the Secrets Manager endpoint (443) and the DB port',
      allowAllOutbound: false,
    });
    const smEndpoint = this.vpc.addInterfaceEndpoint('SecretsManagerEndpoint', {
      service: ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
      subnets: { subnetGroupName: 'app' },
      privateDnsEnabled: true,
      open: false,
      securityGroups: [endpointSg],
    });
    this.database.addRotationSingleUser({
      automaticallyAfter: Duration.days(30),
      vpcSubnets: { subnetGroupName: 'app' },
      endpoint: smEndpoint,
      securityGroup: rotationSg,
    });
    // The hosted rotation construct does not add the rotation->endpoint rule itself; add exactly 443 SG-to-SG.
    smEndpoint.connections.allowDefaultPortFrom(rotationSg, 'rotation function to Secrets Manager endpoint');
    // CDK expresses the rotation->DB rule with the instance's Endpoint.Port token; pin it to the literal DB_PORT
    // (same port, no widening) so the rule is statically checkable by cdk-nag and tests.
    for (const sg of [this.dbSecurityGroup, rotationSg]) {
      for (const child of sg.node.children) {
        if (child instanceof ec2.CfnSecurityGroupIngress || child instanceof ec2.CfnSecurityGroupEgress) {
          if (Token.isUnresolved(child.fromPort) || Token.isUnresolved(child.toPort)) {
            child.fromPort = DB_PORT;
            child.toPort = DB_PORT;
          }
        }
      }
    }

    // AWS Backup (NIST RDSInBackupPlan): CMK-encrypted vault, daily backups kept 35 days.
    const vault = new backup.BackupVault(this, 'BackupVault', {
      encryptionKey: this.dbKey,
      removalPolicy: RemovalPolicy.RETAIN,
    });
    const plan = new backup.BackupPlan(this, 'BackupPlan', { backupVault: vault });
    plan.addRule(
      new backup.BackupPlanRule({
        ruleName: 'daily-35d',
        scheduleExpression: events.Schedule.cron({ hour: '5', minute: '0' }),
        deleteAfter: Duration.days(35),
      }),
    );
    const selection = plan.addSelection('Postgres', {
      resources: [backup.BackupResource.fromRdsDatabaseInstance(this.database)],
    });
    // Registered exception EX-04.
    // Scoped to the selection's role resource only (not applied to children or the selection itself).
    NagSuppressions.addResourceSuppressions(
      selection.node.findChild('Role'),
      [
        {
          id: 'AwsSolutions-IAM4',
          reason:
            'EX-04: AWS Backup selection role uses the AWS-documented service-role policy AWSBackupServiceRolePolicyForBackup; ' +
            'a hand-written copy would need snapshot-name wildcards (IAM5) and drift from AWS updates.',
          appliesTo: ['Policy::arn:<AWS::Partition>:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup'],
        },
      ],
    );

    // Registered exception EX-03 (see evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md).
    NagSuppressions.addResourceSuppressions(monitoringPolicy, [
      {
        id: 'AwsSolutions-IAM5',
        reason:
          'EX-03: RDS enhanced monitoring creates log streams with service-chosen names inside the single ' +
          'RDSOSMetrics log group of this account/region; the wildcard is limited to that group\'s log streams.',
        appliesTo: ['Resource::arn:<AWS::Partition>:logs:<AWS::Region>:<AWS::AccountId>:log-group:RDSOSMetrics:log-stream:*'],
      },
    ]);
  }
}
