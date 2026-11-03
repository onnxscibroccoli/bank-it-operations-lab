# RESEARCH_EX04: aws:SourceArn / aws:SourceAccount in the AWS Backup service-role trust policy

Research date: 2026-11-03 (America/New_York). Sources were fetched that day from docs.aws.amazon.com (authoritative).
Community material is listed separately and is not relied on. This is a documentation review, not a runtime test.

## Question

Does `backup.amazonaws.com` put `aws:SourceArn` and/or `aws:SourceAccount` into the request context when it calls
`sts:AssumeRole` on a customer-managed service role? If so, which value, and for which operations (backup jobs,
restore jobs, copy jobs)?

## Conclusion

| Key in role trust policy | Backup jobs | Restore jobs / restore testing | Copy jobs | Status |
|---|---|---|---|---|
| `aws:SourceAccount` (StringEquals) | not documented by AWS Backup | not documented | not documented | **UNVERIFIED** (consistent with IAM generic guidance; not contradicted) |
| `aws:SourceArn` = this vault ARN (ArnEquals, current default) | not documented; value unknown | not documented; value unknown | not documented; source vs. destination vault unknown | **UNVERIFIED, deployment-blocking** |
| `aws:SourceArn` like `arn:<p>:backup:<region>:<acct>:*` | not documented | not documented | not documented | **UNVERIFIED** |

No current AWS Backup page documents either key for the service-role trust policy. AWS Backup documents
`aws:SourceArn` only for **resource policies**: SNS topic policies (value must be a backup vault) and a KMS key policy
Deny for `backup-storage.amazonaws.com`. AWS's own CloudFormation examples for the service role use an
**unconditioned** trust. So EX-04 stays **DEPLOYMENT-BLOCKING** until the runtime test in VERIFICATION_PROCEDURE.md
passes. Nothing in this repository is evidence that either key is present at runtime.

## Citations (quoted verbatim)

1. AWS Backup Developer Guide, "Cross-service confused deputy prevention":
   <https://docs.aws.amazon.com/aws-backup/latest/devguide/cross-service-confused-deputy-prevention.html>
   - "We recommend using the `aws:SourceArn` and `aws:SourceAccount` global condition context keys in resource
     policies to limit the permissions that AWS Backup gives another service to the resource."
   - "The value of `aws:SourceArn` must be a AWS Backup vault when using AWS Backup to publish Amazon SNS topics on
     your behalf."
   - Its only example is a KMS key-policy Deny for `backup-storage.amazonaws.com`, which "denies the AWS Backup
     storage service principal from using your KMS key unless the request comes from a backup vault in your
     specified account and Region." (This Deny is implemented on BackupVaultKey.)
   - The page has no role trust-policy example.
2. AWS Backup Developer Guide, "IAM service roles":
   <https://docs.aws.amazon.com/aws-backup/latest/devguide/iam-service-roles.html>
   - "The role must also have AWS Backup listed as a trusted entity, which enables AWS Backup to assume the role."
   - "When you assign resources to a backup plan, or if you perform an on-demand backup, copy, or restore, you must
     pass a service role that has access to perform the underlying operations on the specified resources."
   - "You can use roles to control access to your backups by defining narrowly scoped roles and by specifying who can
     pass that role to AWS Backup."
   - The page mentions no trust-policy conditions.
3. AWS Backup Developer Guide, "CloudFormation templates for backup plans":
   <https://docs.aws.amazon.com/aws-backup/latest/devguide/plan-cfn.html>, and "Assign AWS Backup resources through
   CloudFormation": <https://docs.aws.amazon.com/aws-backup/latest/devguide/assigning-resources-cfn.html>
   - In both, the `BackupRole` / `TestRole` `AssumeRolePolicyDocument` is `Principal: Service: backup.amazonaws.com`,
     `Action: sts:AssumeRole`, with **no Condition**.
4. IAM User Guide, "AWS global condition context keys":
   <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html>
   - aws:SourceArn: "Availability – This key is included in the request context only when the call to your resource
     is being made directly by an AWS service principal on behalf of a resource for which the configuration triggered
     the service-to-service request. The calling service passes the ARN of the original resource to the called
     service."
   - aws:SourceArn and aws:SourceAccount (same note): "However, not all service integrations require the use of this
     global condition key. See the documentation of the AWS services you use for more information about
     service-specific mechanisms for mitigating cross-service confused deputy risks."
   - So IAM defers to the service documentation, and AWS Backup's documentation (1 to 3) does not cover AssumeRole.
5. IAM User Guide, "The confused deputy problem":
   <https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html>. This is generic guidance. It does not
   list AWS Backup.
6. Amazon Aurora DSQL User Guide, "Cross-service confused deputy prevention":
   <https://docs.aws.amazon.com/aurora-dsql/latest/userguide/cross-service-confused-deputy-prevention.html>
   - This is an AWS-documented case where `backup.amazonaws.com` is constrained with `"ArnLike": {"aws:SourceArn":
     "arn:aws:backup:*:123456789012:*"}` and `aws:SourceAccount`, but it is a **resource policy on a DSQL cluster**
     (`dsql:GetCluster`), not a role trust policy. It suggests AWS Backup sends some `arn:aws:backup:...` source ARN
     on direct service calls. It does not say which resource type, and it does not say the key is sent on
     sts:AssumeRole. This is the basis for fallback mode `account-region-backup-arn`.
7. AWS-managed policy reference, AWSBackupServiceRolePolicyForBackup:
   <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSBackupServiceRolePolicyForBackup.html>
   - `"Sid" : "RDSBackupPermissions"`, `"Action" : [ "rds:DeleteDBSnapshot", "rds:ModifyDBSnapshotAttribute" ]`,
     `"Resource" : [ "arn:aws:rds:*:*:snapshot:awsbackup:*" ]`. AWS Backup RDS snapshots are therefore
     `awsbackup:...` (colon), not `awsbackup-...` (finding F-06).
   - `"Sid" : "KMSCreateGrantPermissions"`, `"Action" : "kms:CreateGrant"`, `"Condition" : { "Bool" :
     { "kms:GrantIsForAWSResource" : "true" } }`. This is the AWS pattern for the grant split.
8. Amazon RDS User Guide, AWS Backup:
   <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/AutomatedBackups.AWSBackup.html>
   - "Backups that were created with AWS Backup have names ending in awsbackup: backup-job-number ."
   Aurora User Guide <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Managing.Backups.html>:
   - "Snapshots that were created with AWS Backup have names with awsbackup:job- AWS-Backup-job-number ."

Pages checked with **no** mention of SourceArn, SourceAccount, AssumeRole conditions, or confused deputy for the
service role: security-iam-awsmanpol.html, access-control.html, encryption.html, restoring-rds.html (all under
<https://docs.aws.amazon.com/aws-backup/latest/devguide/>). `restore-testing-iam.html` returned no content at that URL.

### Non-authoritative material (context only, not relied on)

- re:Post <https://repost.aws/questions/QUj5gqLm43SJOhnKk0YapJsQ> shows a `backup.amazonaws.com` trust with
  `aws:SourceAccount` only.
- re:Post <https://repost.aws/knowledge-center/backup-access-denied-cross-copy> shows an unconditioned trust for copy
  jobs.
- A third-party course page shows `aws:SourceArn` `backup-vault:*` in a trust policy. It cites no AWS source.

## Per-operation analysis (why ArnEquals = one vault is the riskiest choice)

- **Scheduled backup jobs (plan + selection):** a passed SourceArn could be the backup plan, the vault, or the job.
  ArnEquals on the vault ARN matches only one of those.
- **On-demand backups** (`StartBackupJob`) have no plan, so the context depends on the job alone.
- **Copy jobs** (not configured in infra/aws-cdk; configured in backup/aws) involve a source and a destination vault,
  possibly in another Region or account. Exact-match to one vault would fail at least one direction if the key carries
  the other vault.
- **Restore jobs / restore testing** (no restore role in infra/aws-cdk; backup/aws has a separate restore role).
  Restore testing also uses the service-linked role `AWSServiceRoleForBackupRestoreTesting`
  (<https://docs.aws.amazon.com/aws-backup/latest/devguide/using-service-linked-roles-AWSServiceRoleForBackupRestoreTesting.html>).
  The context sent when the customer restore role is assumed is undocumented.

Every mode in `lib/backup-trust.ts` **fails closed**: with no `...IfExists` operator, an absent key means AssumeRole
is denied and the job fails. The risk is to availability (backups not taken), not exposure. The danger is that a
failed backup goes unnoticed, so monitoring is a compensating control (RESIDUAL_RISK.md R-1).

## Design decision (implemented, default unchanged)

The restrictive condition was **not removed**. `infra/aws-cdk/lib/backup-trust.ts` adds explicitly selectable,
reviewed alternatives through the CDK context key `bankItLab:backupTrustMode`:

| Mode | Trust condition | When to use |
|---|---|---|
| `vault-arn` (default) | `StringEquals aws:SourceAccount` + `ArnEquals aws:SourceArn = <vault ARN>` | Only if the runtime test shows that SourceArn is present and equal to the vault ARN for every operation that uses the role |
| `account-region-backup-arn` | `StringEquals aws:SourceAccount` + `ArnLike aws:SourceArn = arn:<p>:backup:<region>:<acct>:*` | If SourceArn is present but is a plan/job/other backup ARN |
| `source-account-only` | `StringEquals aws:SourceAccount` | If SourceArn is absent on AssumeRole; same pattern as backup/aws/** and the other service roles here. Owner sign-off required |

An unknown mode fails synthesis (`logs/13-synth-trust-mode-invalid-negative.log`). Tests assert that every mode keeps
`aws:SourceAccount`, uses no `IfExists` operator, and trusts only `backup.amazonaws.com`. Compensating controls that
AWS Backup does document: a narrowly scoped role plus restricting `iam:PassRole` for this role (citation 2), and the
`backup-storage` KMS Deny (citation 1).
