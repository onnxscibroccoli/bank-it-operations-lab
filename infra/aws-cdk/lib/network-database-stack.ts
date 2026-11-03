import { ArnFormat, Duration, RemovalPolicy, Stack, StackProps, Token } from 'aws-cdk-lib';
import * as backup from 'aws-cdk-lib/aws-backup';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as events from 'aws-cdk-lib/aws-events';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as rds from 'aws-cdk-lib/aws-rds';
import { NagSuppressions } from 'cdk-nag';
import { Construct } from 'constructs';
import { backupTrustConditions, resolveBackupTrustMode } from './backup-trust';
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
  /** Dedicated CMK for the AWS Backup vault (not shared with RDS storage / Secrets Manager). */
  public readonly backupVaultKey: kms.Key;
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

    // AWS Backup (NIST RDSInBackupPlan): vault encrypted with its own CMK, daily backups kept 35 days.
    // aws-remediation-backup-kms: the vault no longer shares DatabaseKey. RDS snapshots taken by AWS Backup stay
    // encrypted with the source DB key (RDS is not a "fully managed" AWS Backup resource type); the vault key covers
    // vault-level encryption only, is usable only via backup.<region> in this account, and carries the AWS-documented
    // backup-storage confused-deputy Deny.
    this.backupVaultKey = leastPrivilegeKey(this, 'BackupVaultKey', {
      description: 'CMK for the lab AWS Backup vault only (via backup.<region>; no RDS / Secrets Manager use)',
      viaServices: ['backup'],
      denyBackupStorageConfusedDeputy: true,
    });
    const vault = new backup.BackupVault(this, 'BackupVault', {
      encryptionKey: this.backupVaultKey,
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
    const role = backupRole(this, vault, this.database, this.dbKey, this.backupVaultKey);
    new backup.CfnBackupSelection(this, 'PostgresSelection', {
      backupPlanId: plan.backupPlanId,
      backupSelection: {
        selectionName: 'postgres',
        iamRoleArn: role.roleArn,
        resources: [this.database.instanceArn],
      },
    });

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

/**
 * Customer-managed AWS Backup role for the lab PostgreSQL instance (backup jobs only; no restore permissions).
 *
 * Trust: backup.amazonaws.com with aws:SourceAccount = this account (StringEquals) AND, in the default mode, aws:SourceArn
 * = this vault (ArnEquals). See lib/backup-trust.ts and evidence/aws/aws-remediation-backup-kms/RESEARCH_EX04.md:
 * AWS Backup does not document which aws:SourceArn value (if any) it sends when it assumes a customer service role,
 * so EX-04 is DEPLOYMENT-BLOCKING until the non-prod runtime test in VERIFICATION_PROCEDURE.md passes.
 *
 * Permissions (customer-managed, replaces AWSBackupServiceRolePolicyForBackup):
 *  - RDS snapshot actions on this instance and on AWS Backup-named snapshots. AWS Backup names RDS snapshots
 *    `awsbackup:job-<id>`; the AWS-managed policy scopes them as `snapshot:awsbackup:*`. The pre-remediation
 *    `snapshot:awsbackup-*` (hyphen) did not match that documented name (finding F-06).
 *  - KMS split into crypto (Decrypt/GenerateDataKey/DescribeKey via rds|backup) and grant delegation (CreateGrant only
 *    with kms:GrantIsForAWSResource=true via rds|backup). No admin KMS actions, no Resource "*".
 */
function backupRole(
  scope: NetworkDatabaseStack,
  vault: backup.BackupVault,
  database: rds.DatabaseInstance,
  dbKey: kms.Key,
  vaultKey: kms.Key,
): iam.Role {
  const stack = Stack.of(scope);
  const snapshotArn = stack.formatArn({
    service: 'rds',
    resource: 'snapshot',
    arnFormat: ArnFormat.COLON_RESOURCE_NAME,
    resourceName: 'awsbackup:*',
  });
  const via = [`rds.${stack.region}.amazonaws.com`, `backup.${stack.region}.amazonaws.com`];
  const mode = resolveBackupTrustMode(scope);
  const role = new iam.Role(scope, 'DbBackupRole', {
    assumedBy: new iam.ServicePrincipal('backup.amazonaws.com', {
      conditions: backupTrustConditions(stack, mode, vault.backupVaultArn),
    }),
    description: `Lab PostgreSQL backup jobs only. Trust mode ${mode} (EX-04, deployment-blocking until runtime-verified).`,
  });
  const policy = new iam.ManagedPolicy(scope, 'DbBackupPolicy', {
    document: new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          sid: 'SnapshotThisInstance',
          actions: [
            'rds:AddTagsToResource',
            'rds:CopyDBSnapshot',
            'rds:CreateDBSnapshot',
            'rds:DeleteDBSnapshot',
            'rds:DescribeDBInstances',
            'rds:DescribeDBSnapshotAttributes',
            'rds:DescribeDBSnapshots',
            'rds:ListTagsForResource',
            'rds:ModifyDBSnapshotAttribute',
          ],
          resources: [database.instanceArn, snapshotArn],
        }),
        new iam.PolicyStatement({
          sid: 'UseThisVault',
          actions: ['backup:CopyIntoBackupVault', 'backup:DescribeBackupVault'],
          resources: [vault.backupVaultArn],
        }),
        new iam.PolicyStatement({
          sid: 'CryptoDbAndVaultKeysViaRdsAndBackupOnly',
          actions: ['kms:Decrypt', 'kms:DescribeKey', 'kms:GenerateDataKey'],
          resources: [dbKey.keyArn, vaultKey.keyArn],
          conditions: { StringEquals: { 'kms:ViaService': via } },
        }),
        new iam.PolicyStatement({
          sid: 'GrantsForAwsResourcesViaRdsAndBackupOnly',
          actions: ['kms:CreateGrant'],
          resources: [dbKey.keyArn, vaultKey.keyArn],
          conditions: {
            Bool: { 'kms:GrantIsForAWSResource': 'true' },
            StringEquals: { 'kms:ViaService': via },
          },
        }),
      ],
    }),
  });
  role.addManagedPolicy(policy);
  NagSuppressions.addResourceSuppressions(policy, [
    {
      id: 'AwsSolutions-IAM5',
      reason:
        'EX-04: AWS Backup names RDS snapshots awsbackup:job-<id> at runtime (AWS-managed policy scope snapshot:awsbackup:*). ' +
        'The wildcard is only that prefix in this account/region. Trust: aws:SourceAccount + trust mode per backup-trust.ts. ' +
        'DEPLOYMENT-BLOCKING until runtime-verified. Replaces the AWS-managed backup policy.',
      appliesTo: [
        'Resource::arn:<AWS::Partition>:rds:<AWS::Region>:<AWS::AccountId>:snapshot:awsbackup:*',
      ],
    },
  ]);
  return role;
}
