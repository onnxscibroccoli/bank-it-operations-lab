# Terraform reference — not applied

This track demonstrates reading the exported SCPs and a one-way S3 logging relationship. It is not a full Terraform equivalent of the CDK organization, CloudTrail, or security-service stacks. There are no SCP attachments. The bucket relationship alone is not a production logging design: bucket access policy, public-access controls, lifecycle, KMS policy and CloudTrail integration require a deployment-specific implementation/review.

Actions runs Terraform 1.9.8, `terraform init -backend=false -input=false`, and `terraform validate`. Initialization downloads the AWS provider; validation checks its schema without contacting AWS. The selected provider lock file is retained as an artifact. No plan or apply is run.

`bucket_key_enabled` belongs inside an encryption configuration rule, not on an `aws_s3_bucket` resource. The terminal access-log sink uses SSE-S3 and has no logging destination. The CDK reference remains the fuller implementation. B6-3 is a delivered Terraform reference with these stated limits, not owner acceptance of replacing the requested production scope.
