# Inventory: what the lab actually delivers

Snapshot: 2026-10-28, PR heads re-fetched at 14:24 EDT (R15). Repo: https://github.com/onnxscibroccoli/bank-it-operations-lab (public, default `main`).
Nothing is merged. `main` is `7f50348` (README only). Heads and merge state for every PR are in `README.md`.

## Not delivered (absent from every pushed branch)
- **Any executed recovery.** Backup/DR code now exists (#21, below), but every backup, copy, restore and restore-testing item is `NOT_EXECUTED`,
  and billing is `NOT_OBSERVED` (`backup-dr-aws@10da54f:evidence/backup/aws-backup-dr/RECOVERY_EXECUTION_STATUS.json`, `evidence/backup/cost-capacity/actual-billing-observation.json`).
- Any executed hybrid (Windows Server, AD DS, DNS, GPO, Entra Connect) work. The runbooks are plans marked `NOT_EXECUTED` (`hybrid-operations@3397dac:operations/hybrid/EXECUTION_STATUS.md`).
- Any deployment, CDK bootstrap, account or tenant state. No Access Analyzer, policy simulator, Entra What-If or live Graph calls.
- Terraform. #14 (`review/pr3-pr6@eb8d259:reports/review-pr3-pr6.md` B6-3) reports that Ian's plan asked for Terraform for the Organizations work, but CDK was delivered.
  That plan is not in the repo, so this guide treats it as a reported requirement, not a fact it can verify.

## Real: code plus offline tests that pass (re-executed; see `execution/EXECUTION_LOG.md`)
| Capability | Files | Result here |
|---|---|---|
| S3 + KMS storage stack (original) | `bank-aws-001@e494bcf:infra/aws-cdk/**` | Jest 21/21, synth byte-identical (E01). **Superseded by #5** per #7 |
| Remediated storage, private VPC, private RDS, AWS Backup resources, guards | `aws-remediation-vpc-rds@099479e:infra/aws-cdk/**` | Jest 33/33, 0 non-compliant, 5 registered suppressions (E01). The KMS key-admin escalation is open (R07) |
| Organizations OU, SCPs, org trail, GuardDuty, Security Hub | `orgs-security-refs@e5e7f46:infra/orgs/**` | Jest 49/49, lint 0, parliament gated 0 (E10-E12). **`TrailAccessLogsBucket` logs to itself** (R06) |
| Entra CA validator | `entra-ca-offline@d302c99:identity/entra/**`, `tests/entra/**` | 25/25, exits 0/1/2 (E08). CA007 has no baseline rule (R08) |
| Shared evidence checks | `review/pr1-pr2-evidence-audit@fb36341:evidence/shared/**` | 13/13 (E03). On a harness-v2 run it reports `NEGATIVES OK: 0` (R03), which is fixed on #7 |
| Postgres backup/restore, harness v2 | `ci-evidence-postgres@e7399fb:tests/integration/postgres/{run_restore_scenario.sh,lib.sh,expectations.tsv,verify_evidence.py,selftest_harness.sh}` | **Fresh offline run 38/38 PASS, VERIFIED with `--require-artifacts`** (R01). Self-test 26/26 (R02). A forged log is REJECTED (R01) |
| Integration branch + `validate-all.sh` | `overnight/integration@49122f2:scripts/validate-all.sh`, `.github/workflows/{aws-cdk,offline-validation,postgres-restore-evidence}.yml`, `reports/INTEGRATION.md`, `coordination/tasks.json` | `--python-only`: PASS (20 steps) (R04). Full run: see R05 |
| Host health collector, fail-closed endpoint decision | `observability@3e40e39:observability/**` | 64/64; healthy → 0/200, stale → 1/503, NaN → 2/503 (R09) |
| SSM patch rings and systemd hardening (offline inspectors) | `patch-hardening@5605b78:operations/{patching,hardening}/**` | 9/9 + 18/18 tests, fixture drift OK, `--plan` overall PASS, evidence verify PASS (113 inputs) (R10) |
| Identity governance: Graph fixture client, privileged-role inventory, access review | `identity-governance@f48e7e3:identity/governance/**` | 65/65, fixture drift OK, evidence verify OK (R11) |
| Vendor API mock (SIMULATION) and vendor-risk lint | `vendor-mock@d6efb82:integrations/vendor-mock/**`, `governance/vendor-risk/**` | 45/45 (with the documented `-t .`), 25/25 governance tests, lint PASS, evidence verify PASS for `local-offline-20261028T181549Z` (R12 re-run at `d6efb82`) |
| AWS Backup DR reference: CMK vaults, GOVERNANCE Vault Lock, plan with cross-region copy to us-west-2, restore testing plan, cost model | `backup-dr-aws@10da54f:backup/aws/**`, `docs/runbooks/aws-backup/**`, `evidence/backup/**` | tsc 0, Jest 46/46, validate-config 0 errors / 2 warnings, synth with no drift from the committed templates, 4 nag reports 0 non-compliant, evidence validator ok, 8 + 8 tests. **The same unconditioned key-admin statement as B5-2** on `DrVaultKey` and `PrimaryVaultKey` (R17) |
| Integrated incident demo (SIMULATION): crash the DB, detect via #10 probes, diagnose, restore, verify, MTTD/MTTR timeline | `incident-demo@3f13622:scenarios/incident/**`, `evidence/incident/**` | Fresh local run PASS, 19 steps, MTTD 3.596 s, MTTR 8.52 s; selftest 0 failures; `--verify` PASS; a tampered SUMMARY is rejected, exit 1 (R18) |
| M365 / endpoint ops scenarios (synthetic tenant, plan-only engine) | `m365-endpoint@1b3c240:identity/m365/**`, `evidence/m365/**` | 13/13 scenarios, `mutationsExecuted=0`, 29 tests; a real domain gives exit 2, a missing approval gives exit 1; evidence verify OK (R19) |
| Hybrid runbook validator | `hybrid-operations@3397dac:operations/hybrid/checks/**` | 12 files, 0 findings; 10 tests; an injected "EXECUTED" claim is caught, exit 1 (R20). The runbooks themselves are NOT_EXECUTED plans |
| FFIEC AIO lab control mapping validator | `control-mapping@3f82697:governance/controls/**` | 10/10, `MAPPING VALID` (17 rows, 97 artifacts; 0 OBSERVED, 14 SIMULATION, 2 STATIC, 1 NOT_EXECUTED) (R13) |

## Documents only (reference material, no executable checks of their own)
- Federation walkthrough (Entra → AWS IAM Identity Center, SAML + SCIM): `identity-governance@f48e7e3:docs/federation/*.md`. Not executed.
- Team model, on-call, escalation matrix, P1-P4 triage, CAB change review: `team-management@9dc8f1f:operations/team/*`, `docs/management/*`. All synthetic.
- Hybrid runbooks: `hybrid-operations@3397dac:docs/runbooks/hybrid/*.md` (NOT_EXECUTED, two-person change gates in `operations/hybrid/change-gates.md`).
- Backup runbooks: `backup-dr-aws@10da54f:docs/runbooks/aws-backup/{RESTORE_VALIDATION_RUNBOOK,RETENTION_AND_DELETION,RTO_RPO,PREREQUISITES}.md`. The RTO/RPO values are HYPOTHESES with no observations.
- Vendor outage tabletop: `vendor-mock@d6efb82:governance/vendor-risk/scenarios/core-banking-vendor-outage-SIMULATION.md` (linted, SIMULATION).
- Reviews and reports: `review/pr1-pr2-evidence-audit@fb36341:reports/review-pr1-pr2.md`, `review/pr3-pr6@eb8d259:reports/review-pr3-pr6.md`,
  `overnight/integration@49122f2:reports/INTEGRATION.md`, `reports/final-report@54d6fbd:reports/{FINAL_REPORT,USER_ACTIONS_REQUIRED,EVIDENCE_MANIFEST}.md`.
- Not used by this guide: `portfolio-cases@7010d05:portfolio/*` and `job-requirements-matrix@31b69db:docs/JOB_REQUIREMENTS_MATRIX.md`.

## Open findings that affect the curriculum (each re-verified here)
| ID | Finding | Source | Re-check |
|---|---|---|---|
| B5-2 | All 3 CMKs in #5 (and both CMKs in #21) have an unconditioned `KeyAdministrationByAccountRoot` with `kms:Create*` (includes CreateGrant) and `kms:Put*` (includes PutKeyPolicy). The "least-privilege CMK" claim is not proven | #14 | R07: present on `LogsKey`, `DatabaseKey`, `DataKey`, no Condition. R17: also on `DrVaultKey` and `PrimaryVaultKey` |
| B6-1 | `TrailAccessLogsBucket` in #6 logs to itself | #14, #7 | R06: `cfn-s3-selflog` ERROR `TrailAccessLogsBucket30C0D746` |
| B6-2 | No SCP protects the exempt role names (`OrgSecurityAdmin`, `OrgBreakGlass`) from being created or modified in member accounts | #14 | R06: the only `iam:` reference in `scps.ts` is the region-lock NotAction and the root-ARN condition |
| CA007 | Disabling CA007 still passes the baseline | #14 | R08: exit 0 |
| v1 false PASS | The PR #2 v1 harness recorded 4 false PASSes | #3 | Remediated by harness v2 (`2aac93c`, `e7399fb`), confirmed by #14 checkpoint 2. v1 runs are now `HISTORICAL-KNOWN-INVALID` (R01) |
| V2-self-attest | `verify_evidence.py` trusts the run's own `EXPECTATIONS.tsv`, so a run with weakened regexes still verifies (non-blocking) | #14 checkpoint 2 | R21: N01 regex set to `.` and SHA256SUMS re-hashed gives VERIFIED, exit 0. The only tell is the `sha256_expectations.tsv` mismatch in `ENVIRONMENT.txt` |
| EX-01..EX-04 | All 5 suppressions applied while the register says PROPOSED (B5-1). #11 records decisions "relayed" from a security review, **not recorded in #5** | #14, #11 | Register at `099479e` still says PROPOSED |
