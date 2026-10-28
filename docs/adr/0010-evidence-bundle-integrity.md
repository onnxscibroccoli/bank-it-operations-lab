# 0010: Evidence bundles: SHA256SUMS, command logs with exit trailers, shared validator
- Status: Proposed (all source PRs are open drafts)
- Date: 2026-10-28

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
- The shared checks are not wired into any CI workflow (`evidence/shared/README.md`).
