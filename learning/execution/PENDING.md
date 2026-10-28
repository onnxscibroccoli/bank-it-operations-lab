# PENDING / UNEXECUTED

Everything below is either **not executed** while writing this guide, or **not delivered** by the repository. Do not cite these as working.

## Not executed (the capability exists in the repo)
| ID | Week | What | Why not | How to run |
|---|---|---|---|---|
| P-W2 | 2 | `validate_evidence.py manifest` on a real bundle | No bundle ships a `MANIFEST.json` | Write one against `evidence/shared/evidence-manifest.schema.json` |
| P-W5 | 5 | Fresh `generate_evidence.py` run | It writes a new committed-evidence directory and needs a clean committed tree | In a throwaway clone of `entra-ca-offline` |
| P-W6 | 6 | Reproduce the `StringNotEqualsIfExists` defect from orgs ADR-0003 | Would need edits to `scps.ts` and a full Jest run | Scratch tree, then `npm test` |
| P-W7 | 7 | Local version-mismatch control (pg_dump 18 against PG 16) and `service` mode | Offline mode **was** run in Run 2 (R01). These need two PG majors or a service container | CI job `version-mismatch-control`, or a machine with both majors |
| P-W9 | 9 | Mutated `DeletionProtection: false` template through tests | No guard reads it, so the run would only confirm the gap | Add a guard first |
| CI | 1, 7 | Re-running `bank-aws-001-cdk` and `postgres-restore-evidence` | This guide records the existing runs only (R14) | `workflow_dispatch` on the PR branches |
| P-W8 | 8 | Committing an incident-demo run | Local run R18 was kept out of every branch | It is the owner's choice on #22 |
| P-W9b | 9 | #10 live `collect` mode, #17 `cfn-lint`/AWS CLI, #21 `run-cmd.sh` logged runs | Offline fixtures only, by design | Lab host or sandbox account |

## Not delivered (absent from every branch)
- Any **executed** recovery. #21 delivers `backup/aws/**` and `docs/runbooks/aws-backup/**`, but all 7 recovery items and all OBSERVED RTO/RPO values are `NOT_EXECUTED`, and billing is `NOT_OBSERVED`.
- Any executed hybrid work. All of #19's runbooks are `NOT_EXECUTED`.
- Terraform (B6-3, reported by #14; no `.tf` on any branch).
- Any deployment, CDK bootstrap, `cdk diff`, or account/tenant state.
- IAM Access Analyzer `ValidatePolicy`, the IAM policy simulator, the Entra What-If tool, and Microsoft Graph reads.
- GuardDuty org admin and auto-enable, Security Hub configuration policies (orgs ADR-0002).
- Cross-region replication (EX-02), S3 lifecycle rules, RDS or AWS Backup restore drills.
- CI for `infra/orgs`, `backup/aws` and #9/#10/#16-#22. The `evidence/shared` checks run in CI only on #7 (`offline-validation.yml`).
- Entra ↔ AWS federation or SSO configuration (#18 has documents only). Break-glass monitoring.
- Owner approval of exceptions EX-01..EX-04. #11 relays decisions, but #5's register still says PROPOSED. #21's BKP-EX-* are not adjudicated.

## Open findings, with no fix on any branch (re-verified in Run 2)
- B5-2: key-admin escalation on all 3 CMKs of #5 and both of #21 (R07, R17).
- B6-1: self-logging `TrailAccessLogsBucket` in #6 (R06). B6-2: exempt-role bypass (R06).
- CA007: no baseline rule (R08).
- #2 verifier trusts run-local expectations (R21; non-blocking per #14).
- The #3 checker's vacuous `NEGATIVES OK: 0` is fixed only on #7 (`05941a9`), not on #3 (R03).

## Process (needs Ian)
- No human GitHub review on any PR (gate G1, #7 AC1 unmet). Nothing is merged. #14 review notes are agent notes, not sign-offs.
- #11 A11: decide what ships as-is and what slips before midnight ET.
