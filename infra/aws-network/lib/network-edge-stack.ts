import { CfnParameter, Duration, RemovalPolicy, Stack, StackProps, Tags } from 'aws-cdk-lib';
import * as autoscaling from 'aws-cdk-lib/aws-autoscaling';
import * as budgets from 'aws-cdk-lib/aws-budgets';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as route53 from 'aws-cdk-lib/aws-route53';
import * as targets from 'aws-cdk-lib/aws-route53-targets';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import { NagSuppressions } from 'cdk-nag';
import { Construct } from 'constructs';
import { REQUIRED_TAGS } from './lab-context';
import { leastPrivilegeKey } from './least-privilege-key';

const APP_PORT = 8080;

/**
 * Credential-free network edge. Synthesis does not look up AMIs, certificates, or accounts.
 * AmiId and CertificateArn are parameters supplied at a real deploy, which this lab does not perform.
 *
 * Controls aligned to FFIEC Architecture, Infrastructure, and Operations (access paths, logging)
 * and to the GLBA expectation that customer-data paths are not exposed to the public internet:
 * internal ALB, no IGW, no NAT, no SSH, SSM only through interface endpoints.
 */
export class NetworkEdgeStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);
    for (const [key, value] of Object.entries(REQUIRED_TAGS)) Tags.of(this).add(key, value);

    const amiId = new CfnParameter(this, 'AmiId', {
      type: 'AWS::EC2::Image::Id',
      description: 'Amazon Linux 2023 AMI. Supplied at deploy time; synthesis does not look it up.',
    });
    const certificateArn = new CfnParameter(this, 'CertificateArn', {
      type: 'String',
      allowedPattern: '^arn:aws[a-zA-Z0-9-]*:acm:[a-z0-9-]+:[0-9]{12}:certificate/[A-Za-z0-9-]+$',
      description: 'ACM certificate ARN in this region. Supplied at deploy time; not looked up.',
    });

    const logsKey = leastPrivilegeKey(this, 'LogsKey', {
      description: 'CMK for VPC flow logs',
      viaServices: ['logs'],
      allowCloudWatchLogs: true,
    });
    const snsKey = leastPrivilegeKey(this, 'SnsKey', {
      description: 'CMK for the ASG notification topic',
      viaServices: ['sns'],
    });

    const vpc = new ec2.Vpc(this, 'Vpc', {
      ipAddresses: ec2.IpAddresses.cidr('10.42.0.0/16'),
      maxAzs: 2,
      natGateways: 0,
      createInternetGateway: false,
      restrictDefaultSecurityGroup: true,
      subnetConfiguration: [{ name: 'app', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, cidrMask: 24 }],
    });

    const flowLogGroup = new logs.LogGroup(this, 'FlowLogGroup', {
      encryptionKey: logsKey,
      retention: logs.RetentionDays.ONE_YEAR,
      removalPolicy: RemovalPolicy.RETAIN,
    });
    const flowLogRole = new iam.Role(this, 'FlowLogRole', {
      assumedBy: new iam.ServicePrincipal('vpc-flow-logs.amazonaws.com', {
        conditions: { StringEquals: { 'aws:SourceAccount': this.account } },
      }),
    });
    flowLogRole.addManagedPolicy(new iam.ManagedPolicy(this, 'FlowLogPolicy', {
      statements: [new iam.PolicyStatement({
        actions: ['logs:CreateLogStream', 'logs:PutLogEvents', 'logs:DescribeLogStreams'],
        resources: [flowLogGroup.logGroupArn],
      })],
    }));
    vpc.addFlowLog('FlowLog', {
      destination: ec2.FlowLogDestination.toCloudWatchLogs(
        flowLogGroup,
        iam.Role.fromRoleArn(this, 'FlowLogRoleRef', flowLogRole.roleArn, { mutable: false }),
      ),
      trafficType: ec2.FlowLogTrafficType.ALL,
    });

    const endpointSg = new ec2.SecurityGroup(this, 'EndpointSg', {
      vpc, allowAllOutbound: false, description: 'SSM interface endpoints',
    });
    const appSg = new ec2.SecurityGroup(this, 'AppSg', {
      vpc, allowAllOutbound: false, description: 'App instances. No SSH. Egress only to SSM endpoints.',
    });
    const albSg = new ec2.SecurityGroup(this, 'AlbSg', {
      vpc, allowAllOutbound: false, description: 'Internal ALB. Ingress from the VPC CIDR on 443 only.',
    });
    endpointSg.addIngressRule(appSg, ec2.Port.tcp(443), 'instances to SSM endpoints');
    appSg.addEgressRule(endpointSg, ec2.Port.tcp(443), 'instances to SSM endpoints');
    albSg.addIngressRule(ec2.Peer.ipv4(vpc.vpcCidrBlock), ec2.Port.tcp(443), 'VPC clients to the internal listener');
    albSg.addEgressRule(appSg, ec2.Port.tcp(APP_PORT), 'ALB to the app port');
    appSg.addIngressRule(albSg, ec2.Port.tcp(APP_PORT), 'ALB to the app port');

    for (const service of [
      ec2.InterfaceVpcEndpointAwsService.SSM,
      ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
      ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
    ]) {
      vpc.addInterfaceEndpoint(service.shortName, {
        service,
        subnets: { subnetGroupName: 'app' },
        privateDnsEnabled: true,
        open: false,
        securityGroups: [endpointSg],
      });
    }

    const accessLogs = new s3.Bucket(this, 'AccessLogs', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      versioned: true,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    const elbLogAccount = new CfnParameter(this, 'ElbLogDeliveryAccount', {
      type: 'String',
      allowedPattern: '^[0-9]{12}$',
      description: 'Regional ELB access-log delivery account from AWS documentation. Supplied at deploy time; not looked up, because that lookup needs a region.',
    });
    accessLogs.addToResourcePolicy(new iam.PolicyStatement({
      sid: 'ElbWriteLogs',
      principals: [new iam.AccountPrincipal(elbLogAccount.valueAsString)],
      actions: ['s3:PutObject'],
      resources: [accessLogs.arnForObjects('alb/*')],
      conditions: { StringEquals: { 's3:x-amz-acl': 'bucket-owner-full-control' } },
    }));

    const alb = new elbv2.ApplicationLoadBalancer(this, 'Alb', {
      vpc,
      internetFacing: false,
      vpcSubnets: { subnetGroupName: 'app' },
      securityGroup: albSg,
      dropInvalidHeaderFields: true,
    });
    const cfnAlb = alb.node.defaultChild as elbv2.CfnLoadBalancer;
    cfnAlb.loadBalancerAttributes = [
      { key: 'access_logs.s3.enabled', value: 'true' },
      { key: 'access_logs.s3.bucket', value: accessLogs.bucketName },
      { key: 'access_logs.s3.prefix', value: 'alb' },
      { key: 'routing.http.drop_invalid_header_fields.enabled', value: 'true' },
    ];
    NagSuppressions.addResourceSuppressions(accessLogs, [{
      id: 'AwsSolutions-S1',
      reason:
        'NE-02: This bucket is the terminal destination for internal ALB access logs. S3 server access log delivery cannot use a KMS target, and logging the sink to itself loops. Proposed, not approved.',
    }]);
    const listener = alb.addListener('Https', {
      port: 443,
      open: false,
      protocol: elbv2.ApplicationProtocol.HTTPS,
      certificates: [elbv2.ListenerCertificate.fromArn(certificateArn.valueAsString)],
    });
    const targetGroup = new elbv2.ApplicationTargetGroup(this, 'AppTargets', {
      vpc,
      port: APP_PORT,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.INSTANCE,
      healthCheck: { path: '/health', healthyHttpCodes: '200' },
    });
    listener.addTargetGroups('App', { targetGroups: [targetGroup] });

    const instanceRole = new iam.Role(this, 'InstanceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      description: 'SSM session channel only. No SSH. No AWS-managed SSM policy.',
    });
    const ssmPolicy = new iam.ManagedPolicy(this, 'SsmChannelPolicy', {
      statements: [new iam.PolicyStatement({
        sid: 'SsmAgentChannel',
        actions: [
          'ssmmessages:CreateControlChannel',
          'ssmmessages:CreateDataChannel',
          'ssmmessages:OpenControlChannel',
          'ssmmessages:OpenDataChannel',
          'ec2messages:AcknowledgeMessage',
          'ec2messages:DeleteMessage',
          'ec2messages:FailMessage',
          'ec2messages:GetEndpoint',
          'ec2messages:GetMessages',
          'ec2messages:SendReply',
          'ssm:UpdateInstanceInformation',
        ],
        resources: ['*'],
      })],
    });
    instanceRole.addManagedPolicy(ssmPolicy);
    NagSuppressions.addResourceSuppressions(ssmPolicy, [{
      id: 'AwsSolutions-IAM5',
      reason:
        'NE-01: The SSM agent message channels (ssmmessages, ec2messages) and ssm:UpdateInstanceInformation have no resource-level ARN. ' +
        'The instance has no SSH key, no port 22, and no path to the internet. Proposed, not an approved exception.',
      appliesTo: ['Resource::*'],
    }]);
    const profile = new iam.CfnInstanceProfile(this, 'InstanceProfile', { roles: [instanceRole.roleName] });

    const ebsKey = leastPrivilegeKey(this, 'EbsKey', {
      description: 'CMK for application volumes',
      viaServices: ['ec2'],
    });
    // The Auto Scaling service-linked role needs direct CMK permissions;
    // kms:ViaService=ec2 alone does not authorize its encrypted-volume launches.
    const autoScalingRole = new iam.CfnServiceLinkedRole(this, 'AutoScalingServiceRole', {
      awsServiceName: 'autoscaling.amazonaws.com',
      customSuffix: 'BankItLabEdge',
    });
    const autoScalingRoleArn = this.formatArn({
      service: 'iam', region: '', resource: 'role',
      resourceName: `aws-service-role/autoscaling.amazonaws.com/${autoScalingRole.ref}`,
    });
    const scalingPrincipal = new iam.ArnPrincipal(autoScalingRoleArn);
    ebsKey.addToResourcePolicy(new iam.PolicyStatement({
      sid: 'AutoScalingEbsCrypto',
      principals: [scalingPrincipal],
      actions: ['kms:Encrypt', 'kms:Decrypt', 'kms:ReEncrypt*', 'kms:GenerateDataKey*', 'kms:DescribeKey'],
      resources: ['*'],
    }));
    ebsKey.addToResourcePolicy(new iam.PolicyStatement({
      sid: 'AutoScalingEbsGrants',
      principals: [scalingPrincipal],
      actions: ['kms:CreateGrant'],
      resources: ['*'],
      conditions: { Bool: { 'kms:GrantIsForAWSResource': 'true' } },
    }));
    const launchTemplate = new ec2.CfnLaunchTemplate(this, 'LaunchTemplate', {
      launchTemplateData: {
        imageId: amiId.valueAsString,
        instanceType: 't3.micro',
        iamInstanceProfile: { arn: profile.attrArn },
        securityGroupIds: [appSg.securityGroupId],
        monitoring: { enabled: true },
        metadataOptions: { httpTokens: 'required', httpPutResponseHopLimit: 1, httpEndpoint: 'enabled' },
        blockDeviceMappings: [{
          deviceName: '/dev/xvda',
          ebs: { encrypted: true, kmsKeyId: ebsKey.keyArn, volumeSize: 20, volumeType: 'gp3' },
        }],
      },
    });

    const topic = new sns.Topic(this, 'AsgTopic', { masterKey: snsKey });
    const asg = new autoscaling.CfnAutoScalingGroup(this, 'AppAsg', {
      serviceLinkedRoleArn: autoScalingRoleArn,
      minSize: '1',
      maxSize: '2',
      desiredCapacity: '1',
      vpcZoneIdentifier: vpc.selectSubnets({ subnetGroupName: 'app' }).subnetIds,
      healthCheckType: 'ELB',
      healthCheckGracePeriod: Duration.minutes(5).toSeconds(),
      targetGroupArns: [targetGroup.targetGroupArn],
      launchTemplate: {
        launchTemplateId: launchTemplate.ref,
        version: launchTemplate.attrLatestVersionNumber,
      },
      notificationConfigurations: [{
        topicArn: topic.topicArn,
        notificationTypes: [
          'autoscaling:EC2_INSTANCE_LAUNCH',
          'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
          'autoscaling:EC2_INSTANCE_TERMINATE',
          'autoscaling:EC2_INSTANCE_TERMINATE_ERROR',
        ],
      }],
    });
    asg.node.addDependency(profile);

    const zone = new route53.PrivateHostedZone(this, 'PrivateZone', { zoneName: 'edge.lab.internal', vpc });
    new route53.ARecord(this, 'AppAlias', {
      zone,
      recordName: 'app',
      target: route53.RecordTarget.fromAlias(new targets.LoadBalancerTarget(alb)),
    });

    const customerGateway = new ec2.CfnCustomerGateway(this, 'DocumentationPeer', {
      bgpAsn: 65000,
      ipAddress: '203.0.113.10',
      type: 'ipsec.1',
    });
    const vpnGateway = new ec2.CfnVPNGateway(this, 'VpnGateway', { type: 'ipsec.1', amazonSideAsn: 64512 });
    const attachment = new ec2.CfnVPCGatewayAttachment(this, 'VpnAttachment', {
      vpcId: vpc.vpcId,
      vpnGatewayId: vpnGateway.ref,
    });
    const vpn = new ec2.CfnVPNConnection(this, 'SiteToSite', {
      customerGatewayId: customerGateway.ref,
      vpnGatewayId: vpnGateway.ref,
      type: 'ipsec.1',
      staticRoutesOnly: true,
    });
    vpn.addDependency(attachment);
    new ec2.CfnVPNConnectionRoute(this, 'PeerRoute', {
      vpnConnectionId: vpn.ref,
      destinationCidrBlock: '192.0.2.0/24',
    });

    new budgets.CfnBudget(this, 'MonthlyBudget', {
      budget: {
        budgetType: 'COST',
        timeUnit: 'MONTHLY',
        budgetName: 'bank-it-lab-network-edge',
        budgetLimit: { amount: 25, unit: 'USD' },
      },
      notificationsWithSubscribers: [{
        notification: {
          comparisonOperator: 'GREATER_THAN',
          notificationType: 'ACTUAL',
          threshold: 80,
          thresholdType: 'PERCENTAGE',
        },
        subscribers: [{ address: 'budgets@example.com', subscriptionType: 'EMAIL' }],
      }],
    });
  }
}
