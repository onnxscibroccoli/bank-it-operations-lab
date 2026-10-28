# Cost and capacity module (AWS Backup DR reference)

Two strictly separated kinds of number:

| Label | Meaning | Where |
|---|---|---|
| `ESTIMATE` | Planning quantities from **placeholder** inputs. Costs only where an operator filled a unit price from an AWS public pricing page. | `cost-inputs.estimate.json`, `cost_model.py`, `COST_DRIVER_WORKSHEET.md`, `evidence/backup/cost-capacity/estimate-output.json` |
| `ACTUAL_BILLING_OBSERVATION` | Values read from Cost Explorer or CUR for a real deployment. | `evidence/backup/cost-capacity/actual-billing-observation.json`: **`NOT_OBSERVED`** (nothing deployed, no billing data read) |

Capacity: `CAPACITY_TROUBLESHOOTING_EXERCISE.md` (tabletop scenarios with expected checks). Observations go in
`evidence/backup/cost-capacity/capacity-observation.template.json`. All are `NOT_OBSERVED`.

No AWS API was called, no paid resource was created, and no price was invented. Shipped unit prices are `null` and
`test_shipped_inputs_have_no_prices` enforces that.

    python3 docs/runbooks/aws-backup/cost-capacity/cost_model.py > evidence/backup/cost-capacity/estimate-output.json
    python3 -m unittest discover -s docs/runbooks/aws-backup/cost-capacity -p 'test_*.py' -v
