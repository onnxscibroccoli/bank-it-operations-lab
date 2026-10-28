/** Shared, credential-free constants. No lookups, no account context, no real account IDs. */
export const LAB_CONTEXT: Record<string, unknown> = {
  '@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy': true,
};

/** Regions workloads may use (region-lock SCP). Reference values only. */
export const ALLOWED_REGIONS = ['us-east-1', 'us-west-2'];

/**
 * Role-name patterns exempt from guard-rail SCPs (break-glass / security automation).
 * `*` wildcard account; role names are lab placeholders.
 */
export const EXEMPT_ROLE_ARNS = [
  'arn:aws:iam::*:role/OrgSecurityAdmin',
  'arn:aws:iam::*:role/OrgBreakGlass',
];
