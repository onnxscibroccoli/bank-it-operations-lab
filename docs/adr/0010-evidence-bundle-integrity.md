# 0010: Evidence bundles: SHA256SUMS, command logs with exit trailers, shared validator
- Status: **Proposed.** All source PRs are open drafts. #7 wires the shared checks into CI (`offline-validation.yml`).
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- Each bundle has a `SHA256SUMS` that excludes itself: `bank-aws-001@e494bcf:evidence/aws/SHA256SUMS` (87 entries, including infra source),
  `aws-remediation-vpc-rds@099479e:evidence/aws/aws-remediation-vpc-rds/SHA256SUMS` (32, bundle-relative), `orgs-security-refs@e5e7f46:evidence/orgs/SHA256SUMS` (66, repo-relative),
  and per-run sums in PR #2 and PR #4.
- Command logs: `COMMANDS.tsv` rows plus a `# exit_code:` trailer per log (`evidence/aws/run-cmd.sh`, `run-git.sh`, `evidence/orgs/run-cmd.sh`).
- Validators: `bank-aws-001@e494bcf:infra/aws-cdk/lib/evidence-validator.ts` (schema descriptor `evidence/aws/evidence-schema.json`) and
  `review/pr1-pr2-evidence-audit@fb36341:evidence/shared/validate_evidence.py` (`hashes`, `commands`, `postgres-negatives`, `cfn-s3-selflog`, `manifest`) with `evidence-manifest.schema.json`.

## Consequences
- Hashes prove integrity, not provenance. PR #1's `run-cmd.sh` does not write COMMANDS.tsv rows (PR #3 §2).
- Path roots differ between bundles (bundle-relative vs repo-relative), which is a consistency gap.
- At `fb36341` the shared checks are not wired into CI, and `postgres-negatives` passes vacuously on v2's 12-column COMMANDS.tsv (`NEGATIVES OK: 0`; R03).
  `overnight/integration@49122f2` (`05941a9`) reads the columns by header, fails on zero negatives, and runs everything via `scripts/validate-all.sh` and `.github/workflows/offline-validation.yml`.
- The newer bundles follow the same pattern (`SUMMARY.json` input hashes, `--verify`): `observability@3e40e39:evidence/observability/generate_evidence.py`, `identity-governance@f48e7e3:evidence/identity-governance/generate_evidence.py`,
  `patch-hardening@5605b78:evidence/host-operations/generate_evidence.py` and `vendor-mock@d6efb82:evidence/vendor/generate_evidence.py`. All four verified here (R09-R12). Also `m365-endpoint@1b3c240:evidence/m365/generate_evidence.py` (R19), `incident-demo@3f13622:scenarios/incident/lib/timeline.py` (`--verify`), which re-derives MTTD/MTTR and rejects an edited SUMMARY (R18),
  and `backup-dr-aws@10da54f:evidence/backup/validate_backup_evidence.py`, which keeps status labels separate: NOT_EXECUTED and NOT_OBSERVED entries may carry no values (R17).
