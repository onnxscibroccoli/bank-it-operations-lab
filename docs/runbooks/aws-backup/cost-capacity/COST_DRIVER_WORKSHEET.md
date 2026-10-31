# Cost-driver worksheet: ESTIMATE

> Every input here is a **placeholder ESTIMATE**. Every unit price is **TO_VERIFY** (null) until copied, with date and region,
> from the AWS pricing pages below. Actual billing: **NOT_OBSERVED** (`evidence/backup/cost-capacity/actual-billing-observation.json`).

Price references (verify for **us-east-1** and **us-west-2** on the day of use):
[AWS Backup pricing](https://aws.amazon.com/backup/pricing/) ·
[AWS KMS pricing](https://aws.amazon.com/kms/pricing/) ·
[EC2 data transfer (inter-region)](https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer) ·
[RDS for PostgreSQL pricing](https://aws.amazon.com/rds/postgresql/pricing/) ·
[AWS Pricing Calculator](https://calculator.aws/)

## Inputs (from `cost-inputs.estimate.json`)
| Symbol | Meaning | Placeholder (ESTIMATE) |
|---|---|---|
| `S` | Source size per resource, GB | RDS 100, EFS 50 |
| `c` | Daily changed fraction | RDS 0.05, EFS 0.02 |
| `u` | Unique fraction per monthly point (1.0 = full, conservative) | 1.0 |
| `L` | PITR transaction-log GB/day (RDS continuous) | RDS 2 |
| `Rd`, `Rm`, `Tc`, `D` | Daily retention 35, monthly retention 365, cold after 90, days/month 30.4 | from `backup-policy.json` |
| `P_*` | Unit prices | **null / TO_VERIFY** |

## Formulas (per resource, steady state)
| # | Driver | Formula | Notes |
|---|---|---|---|
| F1 | Daily chain, warm GB-month (primary) | `S + S*c*(Rd-1) + L*Rd` | Incremental snapshots: one full plus increments, plus PITR logs |
| F2 | Monthly points retained | `Nm = ceil(Rm/D)`. Warm `Nw = ceil(Tc/D)` if cold-capable, else `Nm`. Cold `Nc = Nm - Nw` | RDS and S3 are **not** cold-capable, so all 13 points stay warm |
| F3 | Warm GB-month, primary | `F1 + Nw*S*u` | |
| F4 | Cold GB-month, primary | `Nc*S*u` | Cold tier minimum is 90 days |
| F5 | DR vault GB-month | `F3 - L*Rd` warm, `F4` cold | Copies mirror the lifecycle. PITR logs are not copied. |
| F6 | Cross-region transfer GB/month | `S*c*D + S*u`, plus one-time `S` for the first full copy | Billed as inter-region data transfer out of us-east-1 |
| F7 | Restore GB/month | `S * drill_fraction * drills` warm, plus cold-restore GB | Restore charges vary by type. Some types have none (verify). |
| F8 | Restore-testing runtime | `instance_hours * P_instance_hour` | The restored RDS instance is billed while it exists during the validation window |
| F9 | KMS | `keys * P_key_month + requests/10k * P_10k` | 2 vault CMKs. Source keys (e.g. DatabaseKey) are counted elsewhere. |
| F10 | Early cold deletion | `max(0, 90 - days_in_cold) * cold GB * P_cold/D` | Possible only in an unlocked vault. Shown for completeness. |
| F11 | Cost | `quantity * P` if `P` is known, else **null** | `cost_model.py` never fills prices |

## Quantities from the placeholder inputs (ESTIMATE, from `cost_model.py`)
| Resource | Warm GB-month (primary + DR) | Cold GB-month (primary + DR) | Transfer GB/month | Cost |
|---|---|---|---|---|
| rds-postgres (placeholder) | 1640 + 1570 | 0 + 0 | 252 (+100 one-time) | null (prices TO_VERIFY) |
| efs-shared (placeholder) | 234 + 234 | 500 + 500 | 80.4 (+50 one-time) | null (prices TO_VERIFY) |

KMS: 2 key-months and 2 x 10k requests (placeholder). Restore testing: 24 instance-hours/month (placeholder). Cost: null.

## Vault Lock cost implications
- Locked storage is **committed spend**. With retention `R` and lock bounds [30, 400], each recovery point is billed until its lifecycle ends. Deleting it to cut cost is denied.
- A mistaken long retention in a COMPLIANCE vault cannot be undone after the grace time. Run this worksheet with the proposed retention before any lock change.
- Cold-storage savings do not apply to RDS or S3 (ignored transition). The monthly RDS points cost warm rates for 365 days. This is the largest lever in the placeholder model.
- Max retention 400 days caps the worst case for a single recovery point at about 400 days of storage.

## How to turn this into a real estimate
1. Replace placeholder sizes with measured sizes (mark `placeholder: false`, keep `label: ESTIMATE`).
2. Fill prices from the reference pages. Record the page URL, region, and retrieval date next to each value in a PR comment.
3. Regenerate `estimate-output.json`. It stays `ESTIMATE`. Only Cost Explorer or CUR data can populate `actual-billing-observation.json`.
