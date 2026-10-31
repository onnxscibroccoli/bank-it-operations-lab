# Prerequisites: KMS, account, region, resource support

Status: reference checklist. Nothing here was verified against a live account (`NOT_EXECUTED`). Read-only commands are
listed for a future operator. None were run.

## 1. Account
| # | Prerequisite | Why | How to verify (read-only, NOT run) |
|---|---|---|---|
| A1 | One workload account holds both regions' vaults (same-account cross-region copy). | Copy actions use `${AWS::AccountId}` in the DR vault ARN. | `aws sts get-caller-identity` |
| A2 | Role `OrgBreakGlass` exists, MFA-protected, and the orgs SCPs exempt it. | The only principal not denied by the vault access policy (deletion, lifecycle, lock, policy changes). | `aws iam get-role --role-name OrgBreakGlass` |
| A3 | Deploy with a principal that is allowed by `region-lock` and `protect-security-services` SCPs (orgs-security-refs). | AWS Backup is regional. us-east-1 and us-west-2 are the only allowed regions. | Review the SCPs in `evidence/orgs/policies/` |
| A4 | Service opt-in enabled in **both** regions for each in-scope type (Backup console > Settings > Service opt-in). | Tag selection silently skips types that are not opted in. | `aws backup describe-region-settings --region <r>` |
| A5 | DynamoDB: enable "Advanced DynamoDB backup features" if DynamoDB is in scope. | Without it, DynamoDB backups cannot be copied cross-region or moved to cold storage, and they use the table's key. | `aws backup describe-region-settings` (`ResourceTypeManagementPreference`) |
| A6 | S3: buckets in scope must have versioning enabled. | AWS Backup for S3 requires versioning. | `aws s3api get-bucket-versioning --bucket <b>` |
| A7 | Review AWS Backup service quotas in both regions (Service Quotas console). | Concurrency and vault counts limit job throughput (see cost-capacity exercise). | `aws service-quotas list-service-quotas --service-code backup` |
| A8 | CDK bootstrap (v6+) in both regions, with an execution role that may create KMS, IAM, and Backup resources. | Standard CDK deploy. | `aws cloudformation describe-stacks --stack-name CDKToolkit` |

## 2. Regions
- Primary `us-east-1`, secondary `us-west-2`. Both support cross-Region copy, restore testing, Vault Lock, and every in-scope type ([feature availability](https://docs.aws.amazon.com/aws-backup/latest/devguide/backup-feature-availability.html)).
- The stacks pin themselves with CloudFormation Rules (`PinRegion`). Deploy `BankItLabBackupDrVault` to us-west-2 **before** `BankItLabBackupPrimary` to us-east-1.
- Copies of **continuous** (PITR) recovery points become snapshot recovery points in the DR region. PITR is not available there.

## 3. KMS
| # | Prerequisite | Detail |
|---|---|---|
| K1 | Vault CMKs (`PrimaryVaultKey`, `DrVaultKey`) | Created by the stacks: rotation on, RETAIN, 30-day pending window. Crypto and grants only `kms:ViaService` `backup.<region>` (DR key also `rds.<region>`) with `kms:CallerAccount`. |
| K2 | Source resource keys | RDS, EBS, Aurora, and (non-advanced) DynamoDB backups are **not independently encrypted**. They keep the source resource's key. That key must allow the backup role (`bank-it-lab-backup-role`) Decrypt, GenerateDataKey, and CreateGrant via the owning service. `BankItLabNetworkDatabase/DatabaseKey` already allows `rds` and `backup`. |
| K3 | Cross-region copy key | A cross-region copy is encrypted with the **destination vault key**. For not-fully-managed types (RDS, EBS) the destination key must be a CMK or the service key, never `aws/backup`. This design uses a CMK. |
| K4 | Unencrypted sources | Copies of unencrypted Aurora, DocumentDB, and Neptune stay unencrypted. Policy: in-scope sources must be encrypted (the infra/aws-cdk guards already enforce this for RDS). |
| K5 | Key deletion | Never schedule deletion of a vault key or source key while recovery points depend on it. Recovery points become unrecoverable. KMS keys are not protected by Vault Lock. |
| K6 | Restore | The restore role needs the same key access. Restores of RDS and EBS can specify a different CMK. |

References: [Encryption for backups](https://docs.aws.amazon.com/aws-backup/latest/devguide/encryption.html).

## 4. Resource-type support for this design
| Type | Cross-Region copy | Cold storage | Continuous / PITR | Independent encryption | Notes |
|---|---|---|---|---|---|
| RDS DB instance | Yes | **No** (monthly cold setting ignored, stays warm) | Yes (35 days max) | No (source key) | Multi-AZ **clusters** cannot be copied |
| EBS | Yes | Yes | No | No | |
| EFS | Yes | Yes | No | Yes (vault key) | |
| S3 | Yes | **No** | Yes | Yes (vault key) | Versioning required; extra S3 managed policies on the roles |
| DynamoDB (advanced features) | Yes | Yes | No (DynamoDB native PITR is separate) | Yes | Plain DynamoDB: no copy at all |

`validatePolicy` warns about the ignored cold-storage transition for RDS and S3, and rejects non-copyable types such as
Redshift Serverless.
