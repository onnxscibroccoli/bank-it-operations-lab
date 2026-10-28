# 0016: AWS Backup DR with GOVERNANCE Vault Lock, cross-region copy and explicit NOT_EXECUTED status
- Status: **Proposed.** #21 is an open draft, not integrated in #7, with no CI. The module's own ADRs say "accepted for the lab reference".
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- `backup-dr-aws@10da54f:backup/aws/config/backup-policy.json` is the single source of truth. `lib/policy.ts#validatePolicy` enforces AWS Backup job-time constraints, and `bin/app.ts` refuses to synthesize if there are errors.
- Two stacks: `BankItLabBackupDrVault` (us-west-2) and `BankItLabBackupPrimary` (us-east-1), each pinned to its region by a CloudFormation Rule. Each has a CMK vault and GOVERNANCE Vault Lock (30-400 days).
  The plan has rules `daily-35d-pitr` and `monthly-365d-cold`, both copied cross-region, plus a monthly restore testing plan.
- COMPLIANCE mode is refused in code, so an accidental deployment can never create an irreversible lock (`backup/aws/docs/adr/ADR-0001-governance-mode-vault-lock.md`).
  The DR vault ARN is built from config rather than a cross-stack reference (`ADR-0002-env-agnostic-cross-region-copy.md`).
- Recovery status is a separate artifact: `evidence/backup/aws-backup-dr/RECOVERY_EXECUTION_STATUS.json` (all `NOT_EXECUTED`). RTO/RPO values are HYPOTHESES (`docs/runbooks/aws-backup/RTO_RPO.md`).

## Consequences
- Verified here (R17): tsc 0, Jest 46/46, validate-config 0 errors / 2 warnings, no synth drift, 4 nag reports 0 non-compliant, evidence validator ok.
  Injecting COMPLIANCE gives exit 1 (`LOCK_COMPLIANCE_IN_LAB`), and a same-region copy gives exit 1 (`SAME_REGION_COPY`).
- Open: B5-2's key-admin pattern on both vault keys; same-account copy only; no alerting; duplicates #5's backup plan; no restore ever executed (`docs/runbooks/aws-backup/README.md#gaps`).
