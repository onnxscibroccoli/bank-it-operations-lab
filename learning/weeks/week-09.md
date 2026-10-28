# Week 9: Resilience in the infrastructure design (resilience and incidents 3 of 3)

**Branches:** `$PR5` (`aws-remediation-vpc-rds@099479e`), `$PR6` (`orgs-security-refs@e5e7f46`), `$PR21` (`backup-dr-aws@10da54f`), plus `$PR10` and `$PR17` for the operations extension.
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

**Day 5: The DR module (#21) and the gaps register.**
```bash
cd $PR21/backup/aws && npm ci --ignore-scripts && npx tsc --noEmit && npm test && npm run -s validate-config
npx cdk synth --no-lookups --no-version-reporting --path-metadata false --quiet -o /tmp/backup-cdkout
for t in BankItLabBackupDrVault BankItLabBackupPrimary; do diff -q <(python3 -m json.tool --sort-keys ../../evidence/backup/aws-backup-dr/synth/$t.template.json) <(python3 -m json.tool --sort-keys /tmp/backup-cdkout/$t.template.json) && echo "$t no drift"; done
cd $PR21 && sha256sum -c --quiet evidence/backup/aws-backup-dr/SHA256SUMS && python3 evidence/backup/validate_backup_evidence.py
```
- *Observed (R17):* tsc exit 0, `Tests: 46 passed, 46 total`, validate-config `errors: 0, warnings: 2`
  (`COLD_IGNORED_FOR_TYPES`: RDS and S3 ignore the cold transition; `DYNAMODB_ADVANCED_REQUIRED`). Synth succeeded with no drift for either stack, and all 4 nag reports have 0 Non-Compliant.
  SHA256SUMS passes **from the repo root** (the paths are repo-relative), and the evidence validator gives `"ok": true`.
- Read the design: `config/backup-policy.json` is the single source of truth. There are two rules, `daily-35d-pitr` and `monthly-365d-cold` (cold after 90 days, deleted at 365), each copied to `bank-it-lab-dr-copy-vault` in us-west-2.
  Both vaults use GOVERNANCE Vault Lock (30-400 days), and a monthly restore testing plan runs on the 15th (`backup/aws/README.md`; module ADRs `backup/aws/docs/adr/ADR-0001-governance-mode-vault-lock.md`, `ADR-0002-env-agnostic-cross-region-copy.md`).
- Then the gaps register. What still blocks a real DR claim:
  - every row of `evidence/backup/aws-backup-dr/RECOVERY_EXECUTION_STATUS.json` is `NOT_EXECUTED`
  - the RTO/RPO targets in `docs/runbooks/aws-backup/RTO_RPO.md` are HYPOTHESES (for example S1 PITR: RPO ≤ 15 min, RTO ≤ 4 h) with no observations
  - copies are same-account only, and there is no job-failure alerting
  - the restore test has no `RestoreMetadataOverrides` for #5's isolated VPC
  - #21 duplicates #5's own 35-day plan (`docs/runbooks/aws-backup/README.md#gaps` items 2-5)
  - EX-02 (#5 has no cross-region S3 replication)
  - GuardDuty org enablement is not built (ADR-0002)

## Operations extension (new modules #10 and #17, offline)
**Ext A: Fail-closed health endpoint** (`$PR10` = `observability@3e40e39`):
```bash
cd $PR10 && python3 -m unittest discover -s observability/tests
for f in healthy stale malformed-nan; do python3 observability/run_healthcheck.py evaluate observability/fixtures/$f.json --now 2026-10-28T12:01:00Z >/tmp/$f.json 2>/dev/null; echo "$f rc=$?"; done
python3 evidence/observability/generate_evidence.py --verify evidence/observability/runs/local-offline-20261028T180832Z
```
- *Observed (R09):* `Ran 64 tests … OK`. `healthy` gives exit 0 with `endpoint_decision {serve: true, http_status: 200}`. `stale` gives exit 1 with `freshness:payload … stale: age 3660s > max_age_s 300` and HTTP 503.
  `malformed-nan` gives exit 2 with `payload:valid … non-finite number NaN not allowed` and HTTP 503. `--verify` prints `VERIFY PASS`.
  The design choice: anything unanticipated means UNHEALTHY (`observability/README.md`, "Fail-closed decision").

**Ext B: Patch rings and rollback** (`$PR17` = `patch-hardening@5605b78`):
```bash
cd $PR17 && python3 operations/patching/tools/inspect_patch_manifest.py operations/patching/manifests/patch-manifest.example.json --plan
python3 -m unittest discover -s operations/patching/tests && python3 -m unittest discover -s operations/hardening/tests
python3 operations/patching/tests/make_fixtures.py --check
python3 evidence/host-operations/generate_evidence.py --verify evidence/host-operations/runs/local-offline-20261028T181252Z
```
- *Observed (R10):* the plan is canary (concurrency 1, errors 0, soak 48h), then wave1 (10%/5%, approvers service-owner and change-advisory-board), then wave2 (25%/5%), with `overall: PASS`.
  9/9 and 18/18 tests OK, no fixture drift, and `PASS (113 inputs)`. Read `operations/patching/procedures/ROLLBACK.md` as the delivered rollback runbook. It is for patching, not DR.
- Everything here is EXAMPLE data. Nothing was applied to an account or host (`operations/patching/README.md`).

## Failure injection and recovery
- **COMPLIANCE lock and a same-region "DR" copy** (on `/tmp` copies of `config/backup-policy.json`, run with `npx ts-node scripts/validate-config.ts <copy>`):
  - *Observed (R17):* setting `vaults.dr_copy.lock.mode=COMPLIANCE` gives exit 1 with `LOCK_GRACE` and `LOCK_COMPLIANCE_IN_LAB`.
    Setting `regions.secondary=us-east-1` gives exit 1 with `SAME_REGION_COPY`. The committed config is untouched.
- **Inherited key-admin pattern:** run the week-3 B5-2 one-liner on `/tmp/backup-cdkout/*.template.json`.
  *Observed (R17):* `DrVaultKeyE3D6C377` and `PrimaryVaultKey22F77B03` both have `KeyAdministrationByAccountRoot` with `kms:Create*`/`kms:Put*` and no Condition. #21 inherits B5-2, and the static guards do not flag it.
- **Deletion protection off** (in memory): mutate a copy of the template (`DeletionProtection: false`) and ask which delivered check catches it.
  *Answer (verified with `grep -i deletionprotection lib/guards.ts test/*.ts`, E14):* no static guard checks `DeletionProtection`. Only the positive assertion at
  `test/network-database-stack.test.ts:46` covers it, and only against the CDK construct, not a mutated JSON. That is a real coverage gap. Running a mutated template through Jest is **UNEXECUTED** (P-W9).

## Answer notes
- Multi-AZ is high availability within a region. It is not DR. Backups need a restore test before they count, and #21 ships the test **plan** but no executed test.
- GOVERNANCE versus COMPLIANCE: GOVERNANCE can be removed by sufficiently privileged IAM principals. COMPLIANCE becomes irreversible after the grace period, so the lab deliberately refuses it (module ADR-0001).
- 14-day automated backups plus an AWS Backup plan give two recovery paths, but neither has been exercised.

## Architecture tradeoffs
- RETAIN everywhere prevents accidental data loss but leaves orphaned resources and cost on stack deletion.
- A CMK-encrypted backup vault means key loss equals backup loss. Key policy and key deletion protection become DR-critical.

## Fifteen-minute walkthrough
Template extraction, then the Backup trio in #5, then #21's plan, copy and lock design with its two injected config errors, then org detection controls, then the gaps register (`NOT_EXECUTED` everywhere, hypothesis RTO/RPO only).

## Interview questions
1. Multi-AZ versus cross-region replication versus backups: what does each protect against?
2. What would your first RDS restore drill look like, and what evidence would it produce?
3. Why protect security services with an SCP?
4. Why are #21's RTO/RPO values labelled HYPOTHESIS, and what measurement does `RTO_RPO.md` define to replace them?
5. Who can remove a GOVERNANCE-mode lock, and how would you constrain that principal?

## PENDING / UNEXECUTED
- P-W9 (above). No RDS or AWS Backup restore drill has run. `RESTORE_VALIDATION_RUNBOOK.md` (#21) is unexecuted, and all 7 recovery items and all OBSERVED RTO/RPO cells are `NOT_EXECUTED`. Billing is `NOT_OBSERVED`. #21 has no CI workflow.
- #10 live `collect` mode (real HTTP/TCP/DNS probes) and #17 `cfn-lint` / AWS CLI commands were not executed. Only offline fixtures were used.
