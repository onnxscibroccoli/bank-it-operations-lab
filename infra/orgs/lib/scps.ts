import { ALLOWED_REGIONS } from './lab-context';

/** Minimal IAM policy document types (SCP subset). */
export type Condition = Record<string, Record<string, string | string[] | boolean>>;
export interface Statement {
  Sid: string;
  Effect: 'Allow' | 'Deny';
  Action?: string | string[];
  NotAction?: string | string[];
  Resource?: string | string[];
  NotResource?: string | string[];
  Condition?: Condition;
}
export interface PolicyDocument {
  Version: '2012-10-17';
  Statement: Statement[];
}
export interface ScpDefinition {
  /** Stable kebab-case id; also the exported file name. */
  id: string;
  name: string;
  description: string;
  document: PolicyDocument;
}

const doc = (Statement: Statement[]): PolicyDocument => ({ Version: '2012-10-17', Statement });

/**
 * B6-2: no IAM-role exemption. A role-name ArnNotLike condition is a standing bypass:
 * anyone who can create a role with that name steps around the guard rail.
 * SCPs do not apply to the management account (AWS Organizations). Break-glass is an
 * operation from the management account, or an OU move, not a member-account role exemption.
 * Service-linked roles are outside SCP evaluation for the actions those roles perform.
 */

/** Global / control-plane services that must stay callable from us-east-1 regardless of region lock. */
export const REGION_LOCK_EXEMPT_ACTIONS = [
  'account:*', 'acm:*', 'aws-portal:*', 'budgets:*', 'ce:*', 'cloudfront:*', 'cur:*', 'globalaccelerator:*',
  'health:*', 'iam:*', 'kms:*', 'organizations:*', 'route53:*', 'route53domains:*', 's3:GetAccountPublicAccessBlock',
  's3:ListAllMyBuckets', 'shield:*', 'sso:*', 'sts:*', 'support:*', 'trustedadvisor:*', 'waf:*', 'wafv2:*',
];

export const SCPS: ScpDefinition[] = [
  {
    id: 'deny-root-user',
    name: 'BankItLab-DenyRootUser',
    description: 'Deny all actions by member-account root users.',
    document: doc([
      {
        Sid: 'DenyRootUser',
        Effect: 'Deny',
        Action: '*',
        Resource: '*',
        Condition: { ArnLike: { 'aws:PrincipalArn': 'arn:aws:iam::*:root' } },
      },
    ]),
  },
  {
    id: 'deny-leave-organization',
    name: 'BankItLab-DenyLeaveOrganization',
    description: 'Prevent member accounts from leaving the organization.',
    document: doc([
      { Sid: 'DenyLeaveOrganization', Effect: 'Deny', Action: 'organizations:LeaveOrganization', Resource: '*' },
    ]),
  },
  {
    id: 'region-lock',
    name: 'BankItLab-RegionLock',
    description: `Deny regional actions outside ${ALLOWED_REGIONS.join(', ')}. Global services are excepted by action, not by principal. No role exemption.`,
    document: doc([
      {
        Sid: 'DenyOutsideAllowedRegions',
        Effect: 'Deny',
        NotAction: REGION_LOCK_EXEMPT_ACTIONS,
        Resource: '*',
        Condition: {
          StringNotEquals: { 'aws:RequestedRegion': ALLOWED_REGIONS },
        },
      },
    ]),
  },
  {
    id: 'protect-security-services',
    name: 'BankItLab-ProtectSecurityServices',
    description: 'Deny disabling or tampering with CloudTrail, GuardDuty, Security Hub and AWS Config.',
    document: doc([
      {
        Sid: 'ProtectCloudTrail',
        Effect: 'Deny',
        Action: [
          'cloudtrail:DeleteTrail', 'cloudtrail:StopLogging', 'cloudtrail:UpdateTrail',
          'cloudtrail:PutEventSelectors', 'cloudtrail:PutInsightSelectors', 'cloudtrail:DeleteEventDataStore',
        ],
        Resource: '*',
      },
      {
        Sid: 'ProtectGuardDuty',
        Effect: 'Deny',
        Action: [
          'guardduty:DeleteDetector', 'guardduty:UpdateDetector', 'guardduty:DisassociateFromAdministratorAccount',
          'guardduty:DisassociateFromMasterAccount', 'guardduty:DisassociateMembers', 'guardduty:DeleteMembers',
          'guardduty:StopMonitoringMembers', 'guardduty:DeletePublishingDestination',
          'guardduty:UpdatePublishingDestination', 'guardduty:CreateFilter', 'guardduty:UpdateFilter',
          'guardduty:CreateIPSet', 'guardduty:UpdateIPSet',
        ],
        Resource: '*',
      },
      {
        Sid: 'ProtectSecurityHub',
        Effect: 'Deny',
        Action: [
          'securityhub:DisableSecurityHub', 'securityhub:DisassociateFromAdministratorAccount',
          'securityhub:DisassociateFromMasterAccount', 'securityhub:DisassociateMembers', 'securityhub:DeleteMembers',
          'securityhub:BatchDisableStandards', 'securityhub:UpdateStandardsControl',
          'securityhub:DisableImportFindingsForProduct', 'securityhub:DeleteFindingAggregator',
        ],
        Resource: '*',
      },
      {
        Sid: 'ProtectConfig',
        Effect: 'Deny',
        Action: [
          'config:DeleteConfigurationRecorder', 'config:StopConfigurationRecorder',
          'config:DeleteDeliveryChannel', 'config:DeleteConfigurationAggregator',
        ],
        Resource: '*',
      },
    ]),
  },
  {
    id: 'deny-public-s3',
    name: 'BankItLab-DenyPublicS3',
    description: 'Deny weakening S3 Block Public Access and granting public ACLs.',
    document: doc([
      {
        Sid: 'DenyBpaChanges',
        Effect: 'Deny',
        Action: ['s3:PutAccountPublicAccessBlock', 's3:PutBucketPublicAccessBlock'], // also authorises Delete*PublicAccessBlock APIs
        Resource: '*',
      },
      {
        Sid: 'DenyPublicAcls',
        Effect: 'Deny',
        Action: ['s3:CreateBucket', 's3:PutBucketAcl', 's3:PutObject', 's3:PutObjectAcl'],
        Resource: '*',
        Condition: {
          StringEquals: { 's3:x-amz-acl': ['public-read', 'public-read-write', 'authenticated-read'] },
        },
      },
      {
        Sid: 'DenyDisableOwnershipEnforced',
        Effect: 'Deny',
        Action: 's3:PutBucketOwnershipControls',
        Resource: '*',
        Condition: { StringNotEquals: { 's3:x-amz-object-ownership': 'BucketOwnerEnforced' } },
      },
    ]),
  },
  {
    id: 'require-encryption',
    name: 'BankItLab-RequireEncryption',
    description: 'Deny unencrypted EBS/RDS/EFS creation, non-TLS S3 access and unsupported S3 SSE values.',
    document: doc([
      {
        Sid: 'DenyUnencryptedEbs',
        Effect: 'Deny',
        Action: 'ec2:CreateVolume',
        Resource: '*',
        Condition: { Bool: { 'ec2:Encrypted': 'false' } },
      },
      {
        Sid: 'DenyDisableEbsDefaultEncryption',
        Effect: 'Deny',
        Action: 'ec2:DisableEbsEncryptionByDefault',
        Resource: '*',
      },
      {
        Sid: 'DenyUnencryptedRds',
        Effect: 'Deny',
        Action: ['rds:CreateDBInstance', 'rds:CreateDBCluster'],
        Resource: '*',
        Condition: { Bool: { 'rds:StorageEncrypted': 'false' } },
      },
      {
        Sid: 'DenyUnencryptedEfs',
        Effect: 'Deny',
        Action: 'elasticfilesystem:CreateFileSystem',
        Resource: '*',
        Condition: { Bool: { 'elasticfilesystem:Encrypted': 'false' } },
      },
      {
        Sid: 'DenyS3WithoutTls',
        Effect: 'Deny',
        Action: 's3:*',
        Resource: '*',
        Condition: { Bool: { 'aws:SecureTransport': 'false' } },
      },
      {
        Sid: 'DenyUnsupportedS3Sse',
        Effect: 'Deny',
        Action: 's3:PutObject',
        Resource: '*',
        Condition: {
          // Only when the header is sent: StringNotEqualsIfExists alone would also deny header-less PutObject
          // (absent key => true), which breaks S3 default encryption. Caught by test/scps.test.ts.
          StringNotEquals: { 's3:x-amz-server-side-encryption': ['aws:kms', 'aws:kms:dsse', 'AES256'] },
          Null: { 's3:x-amz-server-side-encryption': 'false' },
        },
      },
    ]),
  },
  {
    id: 'deny-all-suspended',
    name: 'BankItLab-DenyAllSuspended',
    description: 'Quarantine: deny every action in the Suspended OU. No role exemption. Recovery is a management-account OU move.',
    document: doc([{ Sid: 'DenyAll', Effect: 'Deny', Action: '*', Resource: '*' }]),
  },
];

export function scpById(id: string): ScpDefinition {
  const s = SCPS.find((p) => p.id === id);
  if (!s) throw new Error(`unknown SCP ${id}`);
  return s;
}

/**
 * Attached at the organization root: applies to every member account (never the management account).
 * Kept small because each target allows at most 5 directly attached SCPs, including FullAWSAccess.
 */
export const ROOT_SCP_IDS = ['deny-root-user', 'deny-leave-organization'];

/** Baseline guard rails attached to every active top-level OU (4 + FullAWSAccess = 5, the quota). */
export const BASELINE_SCP_IDS = ['region-lock', 'protect-security-services', 'deny-public-s3', 'require-encryption'];
