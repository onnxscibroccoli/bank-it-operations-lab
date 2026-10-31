# Integration tests

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Check that a database backup can be restored and that the result contains the expected information. A command that exits successfully can still produce the wrong data; verification must examine the recovered result.

For example: A saved ledger is restored in a disposable database and compared with the original synthetic records.

Key terms: **PostgreSQL** means database software that organizes related information in tables. **Transaction** means a group of database changes treated as a unit. **Fingerprint** means a calculated summary used here to compare the lab data before and after restoration. **Negative test** means a check that intentionally invalid behavior is rejected for the expected reason.

**Before using this reference:** Historical run records prove only their stated revision and environment. Full restore execution needs compatible PostgreSQL tools and an isolated non-root lab.

Start with the [plain-English learning path](../../docs/knowledge/recovery.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


## `postgres/`: backup/restore exercise (harness v2)

| File | Purpose |
|------|---------|
| `run_restore_scenario.sh [offline\|service]` | pg_dump / pg_restore exercise on synthetic data (`seed.sql`) |
| `expectations.tsv` | every case that must run: kind, expected exit, and **required reason regex** |
| `lib.sh` | harness: runs each case once, captures exit codes (`pipefail`), classifies the outcome, writes evidence |
| `verify_evidence.py` | independent verifier: re-derives every verdict from the logs and the hashes |
| `selftest_harness.sh` + `expectations.selftest.tsv` | harness self-test (no DB needed) |

### Rules (v2)
- **Negative tests pass only when the command fails *and* its own output matches the declared reason**:
  - N01 `could not read from input file|unexpected end of file`
  - N02 `does not appear to be a valid archive`
  - N03 `database "lab_db_does_not_exist" does not exist`
  - N04 SQLSTATE `23503` + `ledger_entries_account_id_fkey`
  - N05 `ERROR: … "…" already exists`
  - N06 the diff shows `-lab.ledger_entries|1000|<md5>`
- **Unexpected success** is a FAIL (`unexpected_success`). A failure for another reason is a FAIL (`wrong_reason`), or an ERROR
  (`version_mismatch` / `environment_error`) when the output matches known environment errors such as `unrecognized configuration parameter`.
- **Setup is checked separately**:
  - Every precondition is its own `setup` step, for example `S_N05_first_restore` or `S_N04_precondition` (1000 rows, no account 424242).
  - The fault step runs as one command, with `--needs` on its setup steps.
  - A failed setup step is `ERROR setup_failure`, and its dependants are `NOT_RUN`.
- **Version mismatch** is gated by `S04_client_server_major_match`: on a mismatch it reports `ERROR/version_mismatch`, and everything after it is `NOT_RUN`.
- **Missing executables** are reported as `ERROR/missing_executable` (`S00_required_tools`, plus a 126/127 check on every step).
- **Skipped means not passed.** Any declared case that never runs gets a `NOT_RUN/missing_test` row. Duplicates and undeclared cases fail.
  Overall PASS requires exactly one PASS row per declared case: 38 offline, 36 service.
- **Exit codes** are captured with `set -o pipefail` inside each step, and with `${PIPESTATUS[0]}` in CI where output is `tee`d.

### Self-test (`selftest_harness.sh`)
- **Part A:** deliberately bad cases must not pass:
  - unexpected success
  - wrong reason
  - a version error disguised as a fault
  - missing executable
  - setup failure and its dependant
  - `false | tail` pipeline
  - wrong positive output
  - declared-but-unrun case
  - duplicate and undeclared cases
- **Part B:** replays the preserved logs of run 40630856041 through the production expectations. N01, N04, N05 and N06 (false PASS under v1) must
  come out ERROR, and N02 and N03 must come out PASS.
- **Part C:** the verifier must reject a forged COMMANDS.tsv that claims PASS for a wrong-reason failure.

In CI, job `version-mismatch-control` runs the real scenario against `postgres:16` with pg_dump 18 and asserts that the harness reports
`version_mismatch`, zero negative PASSes, overall FAIL, and that the verifier rejects the run.

No cloud credentials or network are used. The binaries are auto-detected from `pg_config`, `/usr/lib/postgresql/*/bin`, or `PG_BIN`.
