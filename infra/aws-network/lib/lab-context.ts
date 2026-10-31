export const LAB_CONTEXT: Record<string, unknown> = {
  '@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy': true,
};

export const REQUIRED_TAGS = {
  Owner: 'bank-it-lab',
  DataClass: 'internal',
  CostCenter: 'lab',
} as const;
