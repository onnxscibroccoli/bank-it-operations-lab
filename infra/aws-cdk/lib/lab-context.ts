/** Feature flags / context shared by the app entrypoint and tests (no lookups, no account context). */
export const LAB_CONTEXT: Record<string, unknown> = {
  '@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy': true,
};
