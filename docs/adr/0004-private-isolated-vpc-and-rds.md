# 0004: Private isolated VPC and private RDS PostgreSQL with CMKs
- Status: Proposed (PR #5 open draft)
- Date: 2026-10-28

## Decision (as implemented)
`aws-remediation-vpc-rds@099479e:infra/aws-cdk/lib/network-database-stack.ts`:
- VPC with `PRIVATE_ISOLATED` subnets only (`app`, `db`). There is no IGW, no NAT and no public subnet. Flow logs (ALL) go to a KMS-encrypted log group with 1-year retention.
- RDS PostgreSQL `VER_17_9`: `publiclyAccessible: false`, Multi-AZ, deletion protection, 14-day backups, IAM auth, log exports to pre-created KMS log groups,
  enhanced monitoring, port `5433`, and storage, Performance Insights and the secret encrypted with a CMK (`lib/least-privilege-key.ts`).
- SGs: DB ingress only from the app SG on 5433, with no egress. Rotation and endpoint SGs have no 0.0.0.0/0. Secret rotation goes through a Secrets Manager interface endpoint.
- AWS Backup plan `daily-35d` into a vault encrypted with the DB CMK (synth: `evidence/aws/aws-remediation-vpc-rds/synth/BankItLabNetworkDatabase.template.json`).
- Guards: `rdsPublicOrUnencrypted`, `openSecurityGroupRules`, `kmsWildcards` (`lib/guards.ts`). Tests: `test/network-database-stack.test.ts`, `test/negative-controls.test.ts`.

## Consequences
- There is no internet egress, so every AWS dependency needs an endpoint. Correction pass 3 added the missing rotation→endpoint 443 rule (`CORRECTION_PASSES.md`).
- No cross-region replica (EX-02). No restore has been exercised. Deletion protection is not covered by a static guard (learning/execution E14).
