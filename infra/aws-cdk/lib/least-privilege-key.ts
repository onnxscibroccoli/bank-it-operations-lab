import { Duration, RemovalPolicy, Stack } from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';

/** Key administration only. Deliberately excludes Encrypt/Decrypt/GenerateDataKey/ReEncrypt and `kms:*`. */
export const KEY_ADMIN_ACTIONS = [
  'kms:Create*',
  'kms:Describe*',
  'kms:Enable*',
  'kms:List*',
  'kms:Put*',
  'kms:Update*',
  'kms:Revoke*',
  'kms:Disable*',
  'kms:Get*',
  'kms:Delete*',
  'kms:TagResource',
  'kms:UntagResource',
  'kms:ScheduleKeyDeletion',
  'kms:CancelKeyDeletion',
];

export const KEY_USAGE_ACTIONS = [
  'kms:Encrypt',
  'kms:Decrypt',
  'kms:ReEncrypt*',
  'kms:GenerateDataKey*',
  'kms:DescribeKey',
];

export interface LeastPrivilegeKeyProps {
  readonly description: string;
  /** Service prefixes (e.g. 's3', 'rds', 'secretsmanager') allowed to use the key on behalf of account principals via kms:ViaService. */
  readonly viaServices: string[];
  /** Allow the CloudWatch Logs service principal to use the key, scoped to log groups in this account/region. */
  readonly allowCloudWatchLogs?: boolean;
}

/**
 * Customer-managed KMS key with an explicit, least-privilege key policy:
 *  - account root may administer the key (no cryptographic use, no kms:*), so the key can never become unmanageable;
 *  - account principals may use the key for crypto only through the named AWS services (kms:ViaService) in this
 *    account (kms:CallerAccount);
 *  - optionally, logs.<region>.amazonaws.com may use it only for log groups in this account/region.
 * No statement uses a wildcard principal.
 */
export function leastPrivilegeKey(scope: Construct, id: string, props: LeastPrivilegeKeyProps): kms.Key {
  const stack = Stack.of(scope);
  const statements: iam.PolicyStatement[] = [
    new iam.PolicyStatement({
      sid: 'KeyAdministrationByAccountRoot',
      principals: [new iam.AccountRootPrincipal()],
      actions: KEY_ADMIN_ACTIONS,
      resources: ['*'],
    }),
    new iam.PolicyStatement({
      sid: 'CryptoViaApprovedServicesOnly',
      principals: [new iam.AccountRootPrincipal()],
      actions: KEY_USAGE_ACTIONS,
      resources: ['*'],
      conditions: {
        StringEquals: {
          'kms:CallerAccount': stack.account,
          'kms:ViaService': props.viaServices.map((s) => `${s}.${stack.region}.amazonaws.com`),
        },
      },
    }),
    new iam.PolicyStatement({
      sid: 'GrantsForAwsResourcesViaApprovedServicesOnly',
      principals: [new iam.AccountRootPrincipal()],
      actions: ['kms:CreateGrant', 'kms:ListGrants', 'kms:RevokeGrant'],
      resources: ['*'],
      conditions: {
        Bool: { 'kms:GrantIsForAWSResource': 'true' },
        StringEquals: {
          'kms:CallerAccount': stack.account,
          'kms:ViaService': props.viaServices.map((s) => `${s}.${stack.region}.amazonaws.com`),
        },
      },
    }),
  ];
  if (props.allowCloudWatchLogs) {
    statements.push(
      new iam.PolicyStatement({
        sid: 'CloudWatchLogsForThisAccountOnly',
        principals: [new iam.ServicePrincipal(`logs.${stack.region}.amazonaws.com`)],
        actions: ['kms:Encrypt*', 'kms:Decrypt*', 'kms:ReEncrypt*', 'kms:GenerateDataKey*', 'kms:Describe*'],
        resources: ['*'],
        conditions: {
          ArnLike: {
            'kms:EncryptionContext:aws:logs:arn': `arn:${stack.partition}:logs:${stack.region}:${stack.account}:log-group:*`,
          },
        },
      }),
    );
  }
  return new kms.Key(scope, id, {
    description: props.description,
    enableKeyRotation: true,
    pendingWindow: Duration.days(30),
    removalPolicy: RemovalPolicy.RETAIN,
    policy: new iam.PolicyDocument({ statements }),
  });
}
