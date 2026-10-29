import { Duration, RemovalPolicy, Stack } from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';

/**
 * Key administration only (B5-2). Explicit actions, no `kms:Create*` / `kms:Put*` wildcards:
 *  - no kms:CreateGrant here (grants are only possible through the conditioned GrantsForAwsResources... statement),
 *  - no kms:Encrypt/Decrypt/GenerateDataKey/ReEncrypt and no `kms:*`,
 *  - kms:PutKeyPolicy stays (so the key remains manageable) but only without BypassPolicyLockoutSafetyCheck.
 */
export const KEY_ADMIN_ACTIONS = [
  'kms:CreateAlias',
  'kms:DescribeKey',
  'kms:GetKeyPolicy',
  'kms:GetKeyRotationStatus',
  'kms:ListAliases',
  'kms:ListKeyPolicies',
  'kms:ListResourceTags',
  'kms:PutKeyPolicy',
  'kms:UpdateAlias',
  'kms:UpdateKeyDescription',
  'kms:EnableKey',
  'kms:EnableKeyRotation',
  'kms:DisableKey',
  'kms:DisableKeyRotation',
  'kms:DeleteAlias',
  'kms:TagResource',
  'kms:UntagResource',
  'kms:ScheduleKeyDeletion',
  'kms:CancelKeyDeletion',
];

/** Default IAM role name of the key administrator (a dedicated role; created outside this lab, never by the stack). */
export const DEFAULT_KEY_ADMIN_ROLE_NAME = 'BankItLabKmsKeyAdmin';

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
  /** IAM role name allowed to administer the key (in addition to the account root user as break-glass). */
  readonly keyAdminRoleName?: string;
}

/**
 * Customer-managed KMS key with an explicit, least-privilege key policy:
 *  - only the dedicated key-admin role (and the account root user as break-glass) may administer the key, using an
 *    explicit action list with no CreateGrant and no lockout-safety bypass (aws:PrincipalArn condition), so the key
 *    stays manageable without giving every account principal wildcard Create or Put actions;
 *  - account principals may use the key for crypto only through the named AWS services (kms:ViaService) in this
 *    account (kms:CallerAccount);
 *  - optionally, logs.<region>.amazonaws.com may use it only for log groups in this account/region.
 * No statement uses a wildcard principal.
 */
export function leastPrivilegeKey(scope: Construct, id: string, props: LeastPrivilegeKeyProps): kms.Key {
  const stack = Stack.of(scope);
  const statements: iam.PolicyStatement[] = [
    new iam.PolicyStatement({
      sid: 'KeyAdministrationByKeyAdminRoleOnly',
      principals: [new iam.AccountRootPrincipal()],
      actions: KEY_ADMIN_ACTIONS,
      resources: ['*'],
      conditions: {
        ArnEquals: {
          'aws:PrincipalArn': [
            `arn:${stack.partition}:iam::${stack.account}:role/${props.keyAdminRoleName ?? DEFAULT_KEY_ADMIN_ROLE_NAME}`,
            `arn:${stack.partition}:iam::${stack.account}:root`,
          ],
        },
        BoolIfExists: { 'kms:BypassPolicyLockoutSafetyCheck': 'false' },
      },
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
