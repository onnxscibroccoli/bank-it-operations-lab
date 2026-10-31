# Capacity troubleshooting exercise (tabletop)

Status: **NOT_OBSERVED.** A tabletop or game-day script for the `backup/aws` design. Commands are read-only
diagnostics for a future, deployed environment. **None were run.** Record findings in
`evidence/backup/cost-capacity/capacity-observation.template.json` (copy it per run). Do not change limits, plans, or
quotas during the exercise without a change ticket.

Plan facts used below: `daily-35d-pitr` starts 05:00 UTC (start window 60 min, completion window 480 min).
`monthly-365d-cold` starts on the 1st at 06:00 UTC (60 / 720 min). Copies go to `bank-it-lab-dr-copy-vault` (us-west-2).
Restore test: 15th at 08:00 UTC.

## C1. Backup window overrun
**Symptom:** daily jobs end `EXPIRED` (did not start within 60 min) or `ABORTED`/`PARTIAL` after the 480-min completion window.
On the 1st of the month the daily (05:00) and monthly (06:00) rules overlap.

| Step | Check (NOT run) | Expected / healthy |
|---|---|---|
| 1 | `aws backup list-backup-jobs --by-backup-vault-name bank-it-lab-primary-vault --by-created-after <date> --region us-east-1` | All `COMPLETED`. Count by `State`. |
| 2 | For each non-completed job: `aws backup describe-backup-job --backup-job-id <id>` | `StatusMessage` explains it (window, quota, resource busy) |
| 3 | Compare `CreationDate`, `StartBy`, `CompletionDate` | Duration well under 480 min. Trend over 30 days not rising. |
| 4 | RDS only: overlap with the native RDS backup window or maintenance window (`aws rds describe-db-instances` `PreferredBackupWindow`) | No overlap with 05:00-06:00 UTC |
| 5 | Day-1 overlap: AWS Backup takes one job per resource per window. Check whether the monthly job was skipped or merged. | Documented behavior verified. No missing monthly point. |

**Decision points:** widen the completion window, move the schedule, split resources across rules, or reduce change rate. Each is a plan change and needs a PR.

## C2. Job concurrency and quotas
**Symptom:** jobs queue or fail with throttling or limit messages when many resources share one schedule.

| Step | Check (NOT run) | Expected |
|---|---|---|
| 1 | `aws service-quotas list-service-quotas --service-code backup --region us-east-1` (and us-west-2) | Record the current values. Do not assume defaults. |
| 2 | Count tagged resources: `aws resourcegroupstaggingapi get-resources --tag-filters Key=backup-plan,Values=bank-it-lab-standard` | Below the concurrent-job quota with headroom |
| 3 | Peak concurrent jobs at 05:00 UTC: `list-backup-jobs --by-state RUNNING` sampled during the window | Peak below quota |
| 4 | Copy jobs: `aws backup list-copy-jobs --by-destination-vault-arn <dr-arn>`. Also check service-side limits on concurrent cross-region snapshot copies (e.g. RDS). | No `FAILED` copy jobs for limit reasons |
| 5 | CloudWatch `AWS/Backup` metrics: `NumberOfBackupJobsRunning`, `NumberOfBackupJobsFailed`, `NumberOfCopyJobsFailed` | Failed = 0 |

**Decision points:** stagger schedules (second selection or rule), request a quota increase (change ticket).

## C3. Vault and storage growth
**Symptom:** storage grows faster than the ESTIMATE model (`COST_DRIVER_WORKSHEET.md` F1-F5).

| Step | Check (NOT run) | Expected |
|---|---|---|
| 1 | `aws backup describe-backup-vault --backup-vault-name <vault>` | `NumberOfRecoveryPoints` near the steady state (~35 daily + 13 monthly per resource, plus continuous points) |
| 2 | `aws backup list-recovery-points-by-backup-vault ... --query 'RecoveryPoints[].{a:RecoveryPointArn,s:BackupSizeInBytes,c:CreationDate,l:CalculatedLifecycle}'` | Every point has a `DeleteAt`. None is retained indefinitely. |
| 3 | Compare the measured GB-month with the ESTIMATE quantities | Within the tolerance agreed in the change. Re-run `cost_model.py` with measured inputs. |
| 4 | Look for points from outside the plan (manual on-demand backups) | Only plan-created points |
| 5 | Vault Lock check: points cannot be deleted. Remediation is only prospective (shorter lifecycle on **new** points). | Team understands committed spend |

## C4. Restore throughput (RTO capacity)
**Symptom:** a restore drill misses the RTO hypothesis (RTO_RPO.md).

| Step | Check (NOT run) | Expected |
|---|---|---|
| 1 | `aws backup describe-restore-job --restore-job-id <id>`: `CreationDate` to `CompletionDate`, `ExpectedCompletionTimeMinutes` | Restore job time recorded |
| 2 | Post-restore warm-up: EBS and RDS restored volumes load blocks lazily. First reads are slow until hydrated. | Validation time (V3) recorded separately from job time |
| 3 | Instance class and storage of the restored DB vs production | Same or documented difference |
| 4 | DR region: time to make the network ready (subnet group, SGs) if not pre-provisioned | Pre-provisioned, otherwise counted in RTO |
| 5 | Cold recovery points: restore from cold takes longer than warm | Measured separately (scenario S5) |

**Decision points:** pre-provision DR networking, larger restore instance class, Fast Snapshot Restore for EBS (cost line), shorter validation suite.

## C5. Copy lag (DR RPO capacity)
| Step | Check (NOT run) | Expected |
|---|---|---|
| 1 | For each daily backup job, find its copy job and compute `copy.CompletionDate - backup.CompletionDate` | Lag recorded. DR RPO hypothesis = 24 h + lag. |
| 2 | Inter-region transfer volume vs ESTIMATE F6 | Within tolerance |

## Exercise record
Fill `capacity-observation.template.json`. For every check: `status` (`NOT_OBSERVED | OBSERVED_OK | OBSERVED_ISSUE`),
the command log path, and the raw value. Never enter a value without its log.
