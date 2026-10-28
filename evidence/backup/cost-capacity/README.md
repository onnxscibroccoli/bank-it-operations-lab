# evidence/backup/cost-capacity

| File | Label | Status |
|---|---|---|
| `estimate-output.json` | `ESTIMATE` | Generated offline by `docs/runbooks/aws-backup/cost-capacity/cost_model.py` from **placeholder** inputs. Every price is null, so every cost is null. |
| `actual-billing-observation.json` | `ACTUAL_BILLING_OBSERVATION` | **NOT_OBSERVED.** Nothing deployed, no billing data read. |
| `capacity-observation.template.json` | `CAPACITY_OBSERVATION` | Template. Every check is **NOT_OBSERVED**. |

`evidence/backup/validate_backup_evidence.py` checks these labels and statuses, and checks that NOT_OBSERVED entries carry no
values. Hashes: `evidence/backup/aws-backup-dr/SHA256SUMS` (repo-relative paths, covers this directory).
