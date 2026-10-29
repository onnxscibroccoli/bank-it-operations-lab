# Network-edge reference (STATIC_VALIDATED, NOT_DEPLOYED)

Internal ALB, private application ASG, IMDSv2, private DNS, SSM channels, documentation-range VPN peer, budget and tags. No stack is deployed. Deploy-time inputs include a prepared AMI, certificate and log-delivery configuration. The AMI must contain the application and SSM agent; the template does not install or validate them. VPN routing and live connectivity are not established by synthesis.

The application EBS key grants only the stack's explicitly selected Auto Scaling service-linked role direct key use and resource-grant creation. The grant statement requires `kms:GrantIsForAWSResource`. This is separate from instance-role SSM access. The role's custom suffix must be unique in the deployment account; deployment requires review and appropriate IAM privileges.

Tests assert the synthesized ASG uses that role and that the CMK policy authorizes it. Actions runs npm ci, TypeScript build, Jest and credential-free CDK synthesis. This is configuration evidence, not runtime validation.

NE-01 and NE-02 remain proposed suppressions, not owner-approved exceptions. No production deployment is authorized.

Source: [AWS Auto Scaling CMK policy requirements](https://docs.aws.amazon.com/autoscaling/ec2/userguide/key-policy-requirements-EBS-encryption.html).
