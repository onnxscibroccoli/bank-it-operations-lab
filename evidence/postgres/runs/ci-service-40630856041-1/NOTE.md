Preserved failing run: https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041
Service job used pg_dump 18.6 (ubuntu-latest, now Ubuntu 26.04) against a postgres:16 service container.
pg_dump 18 emits `SET transaction_timeout = 0;`, which PostgreSQL 16 rejects, so P04 and P09 restores failed
(and P05/P06/P10/P11 failed as a consequence). Negative tests behaved as expected.
Fix (correction pass 1): service image -> postgres:18, plus a `client_server_major_match` setup check.
This NOTE.md was added after the run and is not covered by SHA256SUMS.

---
## CORRECTION (2026-10-28, harness v2): this run is HISTORICAL / KNOWN-INVALID

The sentence above, "Negative tests behaved as expected", is **wrong**. It is kept as originally written so the record isn't rewritten.
The independent review in PR #3 (`reports/review-pr1-pr2.md` §2) found that four negative tests were recorded as PASS even though they failed for an
unrelated reason. Harness v1 counted any non-zero exit as the expected failure, and it chained setup and fault into one `bash -c ... && ...`.

| Step | Recorded | Actual cause (log) | Harness v2 verdict on replay |
|---|---|---|---|
| N01_restore_truncated_dump | PASS | `unrecognized configuration parameter "transaction_timeout"` in createdb/restore, not truncation | ERROR/version_mismatch |
| N04_fk_enforced_after_restore | PASS | `relation "lab.ledger_entries" does not exist`; the FK was never exercised | ERROR/environment_error (setup never happened) |
| N05_restore_over_existing_objects | PASS | first restore failed on `transaction_timeout`; the duplicate-object path never ran | ERROR/version_mismatch |
| N06_tamper_detected | PASS | restore failed on `transaction_timeout`; no tamper or diff ran | ERROR/version_mismatch |
| N02_list_garbage_archive | PASS | `input file does not appear to be a valid archive` (genuine) | PASS/expected_fault_detected |
| N03_restore_missing_database | PASS | `database "lab_db_does_not_exist" does not exist` (genuine) | PASS/expected_fault_detected |

Replay evidence: `tests/integration/postgres/selftest_harness.sh` Part B feeds these exact logs through the v2 expectations; see the
`*-selftest*/B_replay_40630856041/` directories. `SUMMARY.json`, `SUMMARY.md` and `COMMANDS.tsv` are left byte-identical, so `SHA256SUMS` still
matches what CI produced. Their PASS values for N01, N04, N05 and N06 are superseded by `STATUS.json` in this directory.
