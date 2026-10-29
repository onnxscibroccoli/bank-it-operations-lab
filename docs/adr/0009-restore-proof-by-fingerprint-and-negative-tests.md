# 0009: Restore proof by fingerprints and negative tests; failures preserved
- Status: **Proposed; the remediation is delivered.** #2 is an open draft at `e7399fb` (harness v2), integrated in #7, with CI green at both heads.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- `ci-evidence-postgres@e7399fb:tests/integration/postgres/run_restore_scenario.sh`: custom and plain dumps, restore, and a per-table count + md5 fingerprint diff (`fingerprint.sql`)
  against synthetic `seed.sql`. There are 6 negative tests (N01-N06), and their setup runs as separate `S_N*` steps in v2. Every exit code is captured, and the script fails at the end.
- Offline (unix-socket-only `initdb`) and service-container modes. CI uploads evidence with `if: always()` (`.github/workflows/postgres-restore-evidence.yml`).
- Client/server major-version guard added after the pg_dump 18 vs PG 16 failure (first added in v1 `e610015`, and in v2 a gated step `S04_client_server_major_match`; `evidence/postgres/runs/ci-service-40630856041-1/NOTE.md`).
- The shared `postgres-negatives` check asserts the error text (`review/pr1-pr2-evidence-audit@fb36341:evidence/shared/negative-expectations.postgres.json`).

## Harness v2 (delivered at `ci-evidence-postgres@e7399fb`)
- `tests/integration/postgres/expectations.tsv`: every case has a required reason regex. A negative passes only if it fails **for that reason**.
- `lib.sh`: setup runs as separate `S_*` steps with `--needs`. `S04_client_server_major_match` gates a version mismatch as `ERROR/version_mismatch`.
- `verify_evidence.py`: an independent re-derivation of every verdict from the logs and hashes (exit 0 verified, 1 rejected, 3 historical).
- `selftest_harness.sh`: 26 assertions, including a replay of the v1 failing run. CI job `version-mismatch-control` must be REJECTED.
- v1 runs are kept byte-identical, with `STATUS.json` set to `HISTORICAL-KNOWN-INVALID` (`evidence/postgres/runs/INDEX.md`).
- Re-run here: a fresh offline run gave 38/38 and VERIFIED with `--require-artifacts`, a forged log was REJECTED, and the self-test gave 26/26 (learning/execution R01-R02).

## Review status
- `review/pr3-pr6@eb8d259:reports/review-pr3-pr6.md` checkpoint 2 classes the false-PASS finding as **remediated**, with two non-blocking items remaining.
  The first is the verifier trusting the run's own `EXPECTATIONS.tsv`. Reproduced here (learning/execution R21): a weakened regex plus re-hashed SHA256SUMS still gives VERIFIED.
  The second is the `cdk-synth` job going green when skipped.

## Consequences
- v1 (`e610015`): the committed failing CI run contains 4 false PASSes (N01, N04, N05, N06), because negatives chain setup with `&&` (PR #3 §2; E13). v2 remediates this, and the v1 runs are marked historical.
- Dumps are gitignored, so `ARTIFACTS.sha256` cannot be verified from git.
- This covers PostgreSQL logical backup only. There is no RDS or AWS Backup restore and no `backup/aws` module.
