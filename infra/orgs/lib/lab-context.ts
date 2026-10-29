/** Shared, credential-free constants. No lookups, no account context, no real account IDs. */
export const LAB_CONTEXT: Record<string, unknown> = {
  '@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy': true,
};

/** Regions workloads may use (region-lock SCP). Reference values only. */
export const ALLOWED_REGIONS = ['us-east-1', 'us-west-2'];

/**
 * B6-2 retired the member-account role exemption (OrgSecurityAdmin / OrgBreakGlass).
 * Do not reintroduce an ArnNotLike principal bypass. Break-glass is a management-account
 * operation. SCPs do not apply to the management account.
 */
