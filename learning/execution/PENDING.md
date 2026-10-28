# PENDING / UNEXECUTED

Everything below is either **not executed** while writing this guide, or **not delivered** by the repository. Do not cite these as working.

## Not executed (the capability exists in the repo)
| ID | Week | What | Why not | How to run |
|---|---|---|---|---|
| P-W2 | 2 | `validate_evidence.py manifest` on a real bundle | No bundle ships a `MANIFEST.json` | Write one against `evidence/shared/evidence-manifest.schema.json` |
| P-W5 | 5 | Fresh `generate_evidence.py` run | It writes a new committed-evidence directory and needs a clean committed tree | In a throwaway clone of `entra-ca-offline` |
| P-W6 | 6 | Reproduce the `StringNotEqualsIfExists` defect from orgs ADR-0003 | Would need edits to `scps.ts` and a full Jest run | Scratch tree, then `npm test` |
| P-W7 | 7 | `tests/integration/postgres/run_restore_scenario.sh offline` and `service` | No PostgreSQL binaries. apt mirror HTTP 500. No pip wheel for Python 3.13 | Machine with matching PG client/server majors |
| P-W9 | 9 | Mutated `DeletionProtection: false` template through tests | No guard reads it, so the run would only confirm the gap | Add a guard first |
| CI | 1, 7 | Re-running `bank-aws-001-cdk` and `postgres-restore-evidence` | This guide records the existing runs only | `workflow_dispatch` on the PR branches |

## Not delivered (absent from every branch)
- `backup/aws/**`, `docs/runbooks/**`, `evidence/backup/**`.
- Any deployment, CDK bootstrap, `cdk diff`, or account/tenant state.
- IAM Access Analyzer `ValidatePolicy`, the IAM policy simulator, the Entra What-If tool, and Microsoft Graph reads.
- GuardDuty org admin and auto-enable, Security Hub configuration policies (orgs ADR-0002).
- Cross-region replication (EX-02), S3 lifecycle rules, RDS or AWS Backup restore drills.
- CI for `infra/orgs` and `identity/entra`. The `evidence/shared` checks are not wired into CI.
- Entra ↔ AWS federation or SSO. Break-glass monitoring.
- Owner approval of exceptions EX-01..EX-04 (all PROPOSED).
