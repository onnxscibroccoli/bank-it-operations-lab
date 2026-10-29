# RTO / RPO: hypothesis targets vs observed lab measurements

> **No recovery has been executed.** Every OBSERVED value is `NOT_EXECUTED` and `null`. The HYPOTHESIS targets come from the
> design (schedules, windows, AWS-documented behavior). They are not measurements and must not be reported as achieved.

Machine-readable copy: `evidence/backup/aws-backup-dr/rto-rpo-observations.json` (checked by `evidence/backup/validate_backup_evidence.py`).

## Definitions
- **RPO observed** = restore-target data timestamp minus the incident timestamp (data loss window), measured from the restored data (fingerprint row with the latest commit time), not from job metadata alone.
- **RTO observed** = time the restored resource passes validation (runbook step V6) minus the time the restore was declared (step R0).

## Scenarios
| ID | Scenario | HYPOTHESIS RPO target | Basis | HYPOTHESIS RTO target | Basis | OBSERVED RPO | OBSERVED RTO |
|---|---|---|---|---|---|---|---|
| S1 | RDS PITR restore, primary region (logical corruption) | <= 15 min | Continuous backup in `daily-35d-pitr`. AWS documents a ~5 min restore window for PITR. Margin added. | <= 4 h | Restore of a new instance from PITR plus validation, untested | `NOT_EXECUTED` | `NOT_EXECUTED` |
| S2 | RDS snapshot restore, primary region | <= 24 h | Daily 05:00 UTC snapshot | <= 4 h | as S1 | `NOT_EXECUTED` | `NOT_EXECUTED` |
| S3 | RDS restore in DR region (us-east-1 unavailable) | <= 24 h + copy duration | Daily copy only. Continuous points arrive as snapshots. | <= 8 h | New instance in us-west-2. Network/DB subnet group must exist there first (gap) | `NOT_EXECUTED` | `NOT_EXECUTED` |
| S4 | EFS / EBS restore in DR region | <= 24 h + copy duration | Daily copy | <= 8 h | Untested | `NOT_EXECUTED` | `NOT_EXECUTED` |
| S5 | Restore of a monthly cold recovery point (EBS/EFS) | <= 1 month | Monthly rule | Hypothesis requires measurement. Cold restores are slower than warm. | No basis until measured | `NOT_EXECUTED` | `NOT_EXECUTED` |

Copy duration and lag for S3/S4 are unknown until measured (`copy_job.completion - backup_job.completion`).

## How an observation gets recorded
1. Run the restore validation runbook. Fill `evidence/backup/aws-backup-dr/templates/restore-test-record.template.json` as a new file under `evidence/backup/aws-backup-dr/runs/<label>/`.
2. Set `status: EXECUTED` only with job IDs, timestamps, and validation output attached. Otherwise keep `NOT_EXECUTED` or record `FAILED` with logs.
3. Compare to the hypothesis. A miss is a finding to fix, not something to restate.
