# 0009: Restore proof by fingerprints and negative tests; failures preserved
- Status: Proposed (PR #2 open draft; PR #3 recommendations not yet applied)
- Date: 2026-10-28

## Decision (as implemented)
- `ci-evidence-postgres@e610015:tests/integration/postgres/run_restore_scenario.sh`: custom and plain dumps, restore, and a per-table count + md5 fingerprint diff (`fingerprint.sql`)
  against synthetic `seed.sql`. There are 6 negative tests (N01-N06). Every exit code is captured, and the script fails at the end.
- Offline (unix-socket-only `initdb`) and service-container modes. CI uploads evidence with `if: always()` (`.github/workflows/postgres-restore-evidence.yml`).
- Client/server major-version guard added after the pg_dump 18 vs PG 16 failure (`e610015`; `evidence/postgres/runs/ci-service-40630856041-1/NOTE.md`).
- The shared `postgres-negatives` check asserts the error text (`review/pr1-pr2-evidence-audit@fb36341:evidence/shared/negative-expectations.postgres.json`).

## Consequences
- The committed failing CI run contains 4 false PASSes (N01, N04, N05, N06), because negatives chain setup with `&&` (PR #3 §2; re-confirmed in learning/execution E13).
- Dumps are gitignored, so `ARTIFACTS.sha256` cannot be verified from git.
- This covers PostgreSQL logical backup only. There is no RDS or AWS Backup restore and no `backup/aws` module.
