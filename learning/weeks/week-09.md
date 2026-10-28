# Week 9: Resilience in the infrastructure design (resilience and incidents 3 of 3)

**Branches:** `$PR5` (`aws-remediation-vpc-rds@099479e`), `$PR6` (`orgs-security-refs@e5e7f46`).
**Delivered files used:** `infra/aws-cdk/lib/network-database-stack.ts`, `evidence/aws/aws-remediation-vpc-rds/{synth/BankItLabNetworkDatabase.template.json,SECURITY_EXCEPTIONS.md}`,
`infra/aws-cdk/lib/secure-storage-stack.ts`, `infra/orgs/lib/{org-cloudtrail-stack.ts,scps.ts}`, `infra/orgs/docs/adr/ADR-0002-delegated-admin-coverage.md`.

## Daily exercises
**Day 1: RDS resilience settings.** From the synthesized template, extract `MultiAZ`, `DeletionProtection`, `BackupRetentionPeriod`, `StorageEncrypted`, `KmsKeyId`, and the deletion and update-replace policies:
```bash
python3 -c "import json;t=json.load(open('$PR5/evidence/aws/aws-remediation-vpc-rds/synth/BankItLabNetworkDatabase.template.json'));
[print(k,{x:v['Properties'].get(x) for x in ['MultiAZ','DeletionProtection','BackupRetentionPeriod','StorageEncrypted','PubliclyAccessible','Port']},v.get('DeletionPolicy'),v.get('UpdateReplacePolicy')) for k,v in t['Resources'].items() if v['Type']=='AWS::RDS::DBInstance']"
```
- *Observed (E14):* `Postgres9DC8BB04 {'MultiAZ': True, 'DeletionProtection': True, 'BackupRetentionPeriod': 14, 'StorageEncrypted': True, 'PubliclyAccessible': False, 'Port': '5433'} Retain Retain`.

**Day 2: AWS Backup.** Find `AWS::Backup::BackupVault`, `BackupPlan` and `BackupSelection` in the same template. *Observed (E14):* one rule `daily-35d`, `cron(0 5 * * ? *)`, `DeleteAfterDays: 35`. The vault is encrypted with `DatabaseKey` (the same CMK as the DB).
Map them to EX-04 (backup role) and to NIST `RDSInBackupPlan`.

**Day 3: Data retention.** S3 `RETAIN` and versioning on both buckets. PR #3 §4 notes **no lifecycle rules**. Discuss the cost and retention tradeoff.

**Day 4: Detection plumbing.** Org CloudTrail: multi-region, log-file validation, CMK, 1-year CloudWatch retention (`infra/orgs/README.md`).
`protect-security-services` SCP stops member accounts from disabling CloudTrail, GuardDuty, Security Hub or Config.

**Day 5: The gaps register.** List what would block a real DR claim: EX-02 (no cross-region replication), no restore test for RDS or AWS Backup, no runbooks (`docs/runbooks` is absent),
and GuardDuty org enablement not built (ADR-0002).

## Failure injection and recovery
- **Deletion protection off** (in memory): mutate a copy of the template (`DeletionProtection: false`) and ask which delivered check catches it.
  *Answer (verified with `grep -i deletionprotection lib/guards.ts test/*.ts`, E14):* no static guard checks `DeletionProtection`. Only the positive assertion at
  `test/network-database-stack.test.ts:46` covers it, and only against the CDK construct, not a mutated JSON. That is a real coverage gap. Running a mutated template through Jest is **UNEXECUTED** (P-W9).

## Answer notes
- Multi-AZ is high availability within a region. It is not DR. Backups need a restore test before they count.
- 14-day automated backups plus an AWS Backup plan give two recovery paths, but neither has been exercised.

## Architecture tradeoffs
- RETAIN everywhere prevents accidental data loss but leaves orphaned resources and cost on stack deletion.
- A CMK-encrypted backup vault means key loss equals backup loss. Key policy and key deletion protection become DR-critical.

## Fifteen-minute walkthrough
Template extraction → Backup trio → retention → org detection controls → the gaps register (be explicit about what is *not* proven).

## Interview questions
1. Multi-AZ versus cross-region replication versus backups: what does each protect against?
2. What would your first RDS restore drill look like, and what evidence would it produce?
3. Why protect security services with an SCP?

## PENDING / UNEXECUTED
- P-W9 (above). No runbooks, no RDS or AWS Backup restore drill, no replica stack. None of these exist in the repo.
