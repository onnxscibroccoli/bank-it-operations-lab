# evidence/backup/aws-backup-dr

Static, credential-free evidence for branch `backup-dr-aws` (`backup/aws/`). **Nothing was deployed and no AWS API was
called.** `run-cmd.sh` unsets AWS credential and profile variables and points AWS config and credential files at
`/dev/null`. **Actual AWS recovery: NOT_EXECUTED** (`RECOVERY_EXECUTION_STATUS.json`). Not a certification.

| Path | Content |
|---|---|
| `COMMANDS.tsv` | Every logged command (UTC start, exit code, duration, log, cwd, command), including failures |
| `logs/` | Full output of each command (env versions, credential check, npm ci, JSON lint, config validation, tsc, jest, cdk synth, cdk-nag gate, cost-model tests, estimate generation, evidence-validator tests, account-ID grep) |
| `synth/` | Synthesized templates `BankItLabBackupPrimary`, `BankItLabBackupDrVault`, and the manifest (`cdk synth --no-lookups`, env-agnostic) |
| `cdk-nag/` | AwsSolutions + NIST 800-53 R5 reports. 0 non-compliant. 4 suppressed rows = BKP-EX-01/02 (`SECURITY_EXCEPTIONS.md`). |
| `jest-results.json` | 46 tests (config, stack, negative controls) |
| `RECOVERY_EXECUTION_STATUS.json` | Backup, copy, restore, restore-test, and vault-lock checks: all `NOT_EXECUTED` |
| `rto-rpo-observations.json` | `HYPOTHESIS` targets vs `observed` = `NOT_EXECUTED` / null (docs/runbooks/aws-backup/RTO_RPO.md) |
| `templates/` | Restore test record templates (JSON + Markdown) for future runs under `runs/<label>/` |
| `SHA256SUMS` | Repo-relative hashes of this bundle, `evidence/backup/cost-capacity/`, and the `backup/aws` + runbook sources. Run `sha256sum -c evidence/backup/aws-backup-dr/SHA256SUMS` from the repo root. |

Checks: `python3 evidence/backup/validate_backup_evidence.py` (status/label separation and hashes) and
`python3 -m unittest discover -s evidence/backup/tests -v` (negative tests: invented RTO, billing amount, status flips).
`COMMANDS.tsv` uses the same 6-column layout as `evidence/aws/aws-remediation-vpc-rds/`. The shared manifest schema
(`evidence/shared`, PR #3) only knows `aws-3col` / `postgres-10col`, so no `MANIFEST.json` is claimed here.
