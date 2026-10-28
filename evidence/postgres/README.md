# Postgres backup/restore evidence

See `runs/INDEX.md` for the status of every run. Runs marked `HISTORICAL-KNOWN-INVALID` (by `STATUS.json` and `NOTE.md`) were produced by
harness v1 and must not be counted as passing. Their original files are left byte-identical so their hashes still verify.

A harness-v2 run directory contains:

```
evidence/postgres/runs/<RUN_LABEL>/
  ENVIRONMENT.txt     tool versions, mode, git SHA (+ dirty flag), sha256 of each harness file, GitHub run id
  EXPECTATIONS.tsv    the declared cases for this mode (id, kind, expect, modes, fail_class, reason_regex)
  COMMANDS.tsv        seq, step_id, kind, expected, exit_code, result, class, started_utc, duration_ms, log, reason_regex, command
  SUMMARY.json/.md    status CURRENT, overall, expected_cases, passed/failed/errors/not_run
  logs/NN_<step>.log  header, command, "# --- output ---" ... "# --- end output ---", exit code footer
  fingerprints/*.txt  per-table row count + md5 of ordered rows
  ARTIFACTS.sha256    SHA-256 of dumps and corrupted inputs (artifacts/ is gitignored; uploaded by CI)
  SHA256SUMS          SHA-256 of every other file in the run directory
```
Result values are PASS, FAIL, ERROR and NOT_RUN. Only PASS counts.

Verify a run: `python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/<RUN_LABEL> [--require-artifacts]`.
It exits 0 = verified, 1 = rejected, 3 = historical.
