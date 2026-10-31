# Network-edge reference (STATIC_VALIDATED, NOT_DEPLOYED)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Describe cloud storage, networks, databases, and their access controls before deployment. Reviewable definitions make configuration decisions visible and repeatable.

For example: An engineer reviews a template to see whether a database is isolated from public traffic and how its encryption keys are used.

Key terms: **CDK** means a software toolkit used to define infrastructure in programming languages. **CloudFormation** means aWS’s template-based resource provisioning service. **VPC** means a logically isolated cloud network. **RDS** means aWS’s managed relational database service. **S3** means aWS object storage for files and other objects. **KMS** means aWS’s service for managing cryptographic keys. **IAM** means identity and Access Management: controls for who may act on resources.

**Before using this reference:** Cloud deployment is outside this documentation task. Existing exceptions and trust-policy gaps remain unresolved until separately addressed.

Start with the [plain-English learning path](../../docs/knowledge/infrastructure.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


Internal ALB, private application ASG, IMDSv2, private DNS, SSM channels, documentation-range VPN peer, budget and tags. No stack is deployed. Deploy-time inputs include a prepared AMI, certificate and log-delivery configuration. The AMI must contain the application and SSM agent; the template does not install or validate them. VPN routing and live connectivity are not established by synthesis.

The application EBS key grants only the stack's explicitly selected Auto Scaling service-linked role direct key use and resource-grant creation. The grant statement requires `kms:GrantIsForAWSResource`. This is separate from instance-role SSM access. The role's custom suffix must be unique in the deployment account; deployment requires review and appropriate IAM privileges.

Tests assert the synthesized ASG uses that role and that the CMK policy authorizes it. Actions runs npm ci, TypeScript build, Jest and credential-free CDK synthesis. This is configuration evidence, not runtime validation.

NE-01 and NE-02 remain proposed suppressions, not owner-approved exceptions. No production deployment is authorized.

Source: [AWS Auto Scaling CMK policy requirements](https://docs.aws.amazon.com/autoscaling/ec2/userguide/key-policy-requirements-EBS-encryption.html).
