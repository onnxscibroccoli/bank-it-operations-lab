import { Duration, RemovalPolicy, Stack } from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';

/**
 * Same pattern as infra/aws-cdk/lib/least-privilege-key.ts (branch aws-remediation-vpc-rds), copied rather than
 * imported because infra/aws-cdk/** belongs to another worker. Key admin for account root (no crypto, no kms:*);
 * crypto and grants only via the named services in this account. No wildcard principal.
 */
export const KEY_ADMIN_ACTIONS = [
  'kms:Create*', 'kms:Describe*', 'kms:Enable*', 'kms:List*', 'kms:Put*', 'kms:Update*', 'kms:Revoke*',
  'kms:Disable*', 'kms:Get*', 'kms:Delete*', 'kms:TagResource', 'kms:UntagResource', 'kms:ScheduleKeyDeletion',
  'kms:CancelKeyDeletion',
];
export const KEY_USAGE_ACTIONS = ['kms:Encrypt', 'kms:Decrypt', 'kms:ReEncrypt*', 'kms:GenerateDataKey*', 'kms:DescribeKey'];

export interface BackupKeyProps {
  readonly description: string;
  /** Service prefixes allowed to use the key via kms:ViaService, e.g. ['backup'] or ['backup', 'rds']. */
  readonly viaServices: string[];
}

export function backupVaultKey(scope: Construct, id: string, props: BackupKeyProps): kms.Key {
  const stack = Stack.of(scope);
  const via = props.viaServices.map((s) => `${s}.${stack.region}.amazonaws.com`);
  return new kms.Key(scope, id, {
    description: props.description,
    enableKeyRotation: true,
    pendingWindow: Duration.days(30),
    removalPolicy: RemovalPolicy.RETAIN,
    policy: new iam.PolicyDocument({
      statements: [
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
          conditions: { StringEquals: { 'kms:CallerAccount': stack.account, 'kms:ViaService': via } },
        }),
        new iam.PolicyStatement({
          sid: 'GrantsForAwsResourcesViaApprovedServicesOnly',
          principals: [new iam.AccountRootPrincipal()],
          actions: ['kms:CreateGrant', 'kms:ListGrants', 'kms:RevokeGrant'],
          resources: ['*'],
          conditions: {
            Bool: { 'kms:GrantIsForAWSResource': 'true' },
            StringEquals: { 'kms:CallerAccount': stack.account, 'kms:ViaService': via },
          },
        }),
      ],
    }),
  });
}
