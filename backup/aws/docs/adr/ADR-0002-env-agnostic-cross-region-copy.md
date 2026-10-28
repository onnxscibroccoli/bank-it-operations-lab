# ADR-0002: Cross-region copy target by deterministic ARN, regions pinned by CloudFormation Rules

Status: accepted for the lab reference.

Context: the repo synthesizes without credentials or `env` (infra/aws-cdk ADR-0003). A copy action needs the destination
vault ARN in another region, and CDK cross-region references need concrete environments.

Decision: the DR vault has a fixed name from config; the primary stack builds
`arn:${AWS::Partition}:backup:us-west-2:${AWS::AccountId}:backup-vault:bank-it-lab-dr-copy-vault`. Each stack carries a
CloudFormation Rule asserting `AWS::Region` equals its intended region, so a template deployed to the wrong region fails
before creating anything. Same account only; cross-account copy (to a separate backup/log-archive account) is a gap.

Consequences: deploy order is DR stack first, then primary. If the DR vault is missing, copy jobs fail at run time (not at
deploy time). The Rule behavior is untested against CloudFormation because nothing is deployed.
