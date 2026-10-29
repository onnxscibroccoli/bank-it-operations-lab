# 0004: Private isolated VPC and private RDS PostgreSQL with CMKs
- Status: **Proposed, with an open blocking finding** (B5-2). #5 is an open draft, integrated in #7, and #14 says request changes.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
`aws-remediation-vpc-rds@099479e:infra/aws-cdk/lib/network-database-stack.ts`:
- VPC with `PRIVATE_ISOLATED` subnets only (`app`, `db`). There is no IGW, no NAT and no public subnet. Flow logs (ALL) go to a KMS-encrypted log group with 1-year retention.
- RDS PostgreSQL `VER_17_9`: `publiclyAccessible: false`, Multi-AZ, deletion protection, 14-day backups, IAM auth, log exports to pre-created KMS log groups,
  enhanced monitoring, port `5433`, and storage, Performance Insights and the secret encrypted with a CMK (`lib/least-privilege-key.ts`).
- SGs: DB ingress only from the app SG on 5433, with no egress. Rotation and endpoint SGs have no 0.0.0.0/0. Secret rotation goes through a Secrets Manager interface endpoint.
- AWS Backup plan `daily-35d` into a vault encrypted with the DB CMK (synth: `evidence/aws/aws-remediation-vpc-rds/synth/BankItLabNetworkDatabase.template.json`).
- Guards: `rdsPublicOrUnencrypted`, `openSecurityGroupRules`, `kmsWildcards` (`lib/guards.ts`). Tests: `test/network-database-stack.test.ts`, `test/negative-controls.test.ts`.

## Consequences
- **Open: key-admin escalation (B5-2).** `lib/least-privilege-key.ts` emits `KeyAdministrationByAccountRoot` with `kms:Create*` (which covers CreateGrant) and `kms:Put*` (which covers PutKeyPolicy), with no condition (learning/execution R07;
  `review/pr3-pr6@eb8d259:reports/review-pr3-pr6.md` B5-2). Until it is fixed, "least-privilege CMK" is not an accurate description.
- The same unconditioned statement appears on `backup-dr-aws@10da54f` `DrVaultKey` and `PrimaryVaultKey` (R17). A fix belongs in a shared key construct.
- Scanner blind spots: the default-SG custom-resource Lambda, the SAR rotation nested stack, the Backup resources, the endpoint, the flow log and the standalone egress rules appear in no NagReport row (#14).
- There is no internet egress, so every AWS dependency needs an endpoint. Correction pass 3 added the missing rotation→endpoint 443 rule (`CORRECTION_PASSES.md`).
- No cross-region replica (EX-02). No restore has been exercised. Deletion protection is not covered by a static guard (learning/execution E14).
