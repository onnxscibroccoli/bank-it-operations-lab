# Postgres backup/restore evidence

Each run of `tests/integration/postgres/run_restore_scenario.sh` writes one directory:

```
evidence/postgres/runs/<RUN_LABEL>/
  ENVIRONMENT.txt     tool versions, mode, git SHA, GitHub run id
  COMMANDS.tsv        seq, step_id, kind, expected, exit_code, result, started_utc, duration_ms, log, command
  SUMMARY.json/.md    totals and per-step table
  logs/NN_<step>.log  full stdout/stderr of each command, with exit code footer
  fingerprints/*.txt  per-table row count + md5 of ordered rows (source vs restored)
  ARTIFACTS.sha256    SHA-256 of dumps/TOC/corrupted inputs (artifacts/ is gitignored; uploaded by CI)
  SHA256SUMS          SHA-256 of every committed file in the run directory
```

CI runs (`.github/workflows/postgres-restore-evidence.yml`) upload the full directory, including
`artifacts/`, as a workflow artifact named `postgres-evidence-<mode>-<run_id>-<attempt>`.
Failures are preserved: evidence is uploaded with `if: always()` before the job is marked failed.

Verify a run: `tests/integration/postgres/verify_evidence.sh evidence/postgres/runs/<RUN_LABEL>`
