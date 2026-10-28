# Correction pass 2
Failure (logs 12/13 pass2): `MustBeObjectownershipAccesscontrol` - without feature flag
`@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy`, CDK grants log delivery via the legacy `LogDeliveryWrite` ACL,
which conflicts with ObjectOwnership=BucketOwnerEnforced (ACLs disabled).
Fix: enable the flag (lib/lab-context.ts, applied in bin/app.ts and tests; mirrored in cdk.json) so CDK grants
`logging.s3.amazonaws.com` s3:PutObject via bucket policy with aws:SourceArn/aws:SourceAccount conditions. ACLs stay disabled.
