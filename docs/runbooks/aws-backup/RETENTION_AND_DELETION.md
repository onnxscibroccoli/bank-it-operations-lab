# Retention and deletion implications

Applies to `config/backup-policy.json` as shipped. Static analysis only (`NOT_EXECUTED`).

## Retention matrix
| Rule | Primary vault (us-east-1) | DR copy (us-west-2) | Cold transition | Effective storage |
|---|---|---|---|---|
| `daily-35d-pitr` | 35 days (continuous, where supported) | 35 days (snapshot) | none | warm only |
| `monthly-365d-cold` | 365 days | 365 days | day 90 | EBS, EFS, DynamoDB-adv: 90 days warm then 275 days cold. **RDS, S3: warm for 365 days** (cold setting ignored) |

Both vault locks: **GOVERNANCE**, MinRetentionDays 30, MaxRetentionDays 400. Every rule and copy retention (35, 365) is
inside [30, 400]. `validatePolicy` fails if one leaves that range, because the job would fail at run time.

## Vault Lock
- **Bounds apply to new jobs only.** A backup or copy job whose retention is outside [min, max] **fails**. Recovery points already in the vault keep their own lifecycle.
- **Recovery points cannot be deleted or have their lifecycle shortened** while locked, including by root. They expire only at the end of their lifecycle.
- **GOVERNANCE (shipped):** principals with `backup:DeleteBackupVaultLockConfiguration` can remove the lock. The vault access policy denies that action, and the related delete, lifecycle, and policy actions, to everyone except `OrgBreakGlass`. Consequence: a CloudFormation update that changes the lock or access policy must run as the break-glass role.
- **COMPLIANCE (not shipped, ADR-0001):** set via `ChangeableForDays` (at least 3). After the grace time the lock cannot be changed or removed by anyone, including AWS, and the vault cannot be deleted while it has recovery points. A wrong retention, or "always" retention, then becomes a permanent cost. Use only with an approved change, a retention schedule signed off by records management, and a cost forecast (cost-capacity worksheet).
- If the account is closed, AWS keeps the vault for 90 days, then deletes its contents even when locked.
- Vault Lock governs AWS Backup APIs only. EBS snapshots can still be shared (`ec2:ModifySnapshotAttribute`) or re-tiered (`ec2:ModifySnapshotTier`) through EC2. Deny those in an SCP and exempt the backup roles.

## Cold storage minimum (90 days)
- A recovery point that moves to cold storage must stay there **at least 90 days**. `delete_after_days - move_to_cold_storage_after_days >= 90`. The shipped config uses 365 - 90 = 275.
- Deleting a cold recovery point early (possible only in an unlocked vault) is still billed for the rest of the 90 days. See the cost-capacity worksheet.
- The cold-transition value cannot be changed after a recovery point has moved.
- Ignored for types that do not support cold storage (RDS, S3). Those stay warm for the full retention.
- Continuous backups cannot move to cold storage (rejected by `validatePolicy`).

## Copy retention
- Copy lifecycle is set **per copy action**, independently of the source. Here both match. The DR copy must not expire before the source (`COPY_SHORTER_THAN_SOURCE` warning).
- Every copy action has an explicit `DeleteAfterDays`. The guard `BKP_NO_RETENTION` fails a template whose copy action has no lifecycle, so expiry never depends on a default.
- The copy has to fit the **destination** vault's lock bounds, not the source's.
- A cross-region copy of a continuous recovery point becomes a snapshot. DR RPO is bounded by the daily copy, not by PITR (RTO_RPO.md).

## Deletion behavior
| Action | Effect |
|---|---|
| Lifecycle expiry | AWS Backup deletes the recovery point. Primary and DR copies expire independently. |
| Manual `DeleteRecoveryPoint` | Denied by the vault access policy except for `OrgBreakGlass`. Denied for everyone while the lock covers it. |
| Delete backup plan or selection | Stops new jobs. **Existing recovery points are kept** until their lifecycle ends. |
| Delete source resource | Recovery points are kept until their lifecycle ends. For continuous backups, PITR stops at the deletion time. |
| `cdk destroy` / stack delete | Vaults and KMS keys are `RETAIN` and stay behind. Roles, plan, selection, and restore-testing resources are deleted. The vault can only be deleted after it is empty (and, under COMPLIANCE, never while it holds recovery points). |
| KMS key deletion | Not blocked by Vault Lock. Makes dependent recovery points unrecoverable. Never schedule it while recovery points exist. |
| RDS automated backups | Separate from AWS Backup. `aws-remediation-vpc-rds` keeps 14-day native RDS backups that follow RDS lifecycle rules, not this vault. |
