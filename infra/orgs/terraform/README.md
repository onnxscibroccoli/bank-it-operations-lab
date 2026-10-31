# Terraform reference — not applied

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize permissions and security administration across multiple cloud accounts. Central guardrails reduce accidental drift, but their scope and exceptions must be understood.

For example: A central team defines a guardrail that member accounts cannot exceed, then reviews where administration is delegated.

Key terms: **SCP** means service Control Policy: an AWS Organizations guardrail that limits available permissions rather than granting them. **Delegated administrator** means an account assigned administration responsibilities for a supported service. **Terraform** means a tool that describes and manages infrastructure through configuration.

**Before using this reference:** No live Organizations changes, Terraform apply, or service enablement is established by these documents.

Start with the [plain-English learning path](../../../docs/knowledge/infrastructure.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


This track demonstrates reading the exported SCPs and a one-way S3 logging relationship. It is not a full Terraform equivalent of the CDK organization, CloudTrail, or security-service stacks. There are no SCP attachments. The bucket relationship alone is not a production logging design: bucket access policy, public-access controls, lifecycle, KMS policy and CloudTrail integration require a deployment-specific implementation/review.

Actions runs Terraform 1.9.8, `terraform init -backend=false -input=false`, and `terraform validate`. Initialization downloads the AWS provider; validation checks its schema without contacting AWS. The selected provider lock file is retained as an artifact. No plan or apply is run.

`bucket_key_enabled` belongs inside an encryption configuration rule, not on an `aws_s3_bucket` resource. The terminal access-log sink uses SSE-S3 and has no logging destination. The CDK reference remains the fuller implementation. B6-3 is a delivered Terraform reference with these stated limits, not owner acceptance of replacing the requested production scope.
