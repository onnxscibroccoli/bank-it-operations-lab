Preserved failing run: https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041
Service job used pg_dump 18.6 (ubuntu-latest, now Ubuntu 26.04) against a postgres:16 service container.
pg_dump 18 emits `SET transaction_timeout = 0;`, which PostgreSQL 16 rejects, so P04 and P09 restores failed
(and P05/P06/P10/P11 failed as a consequence). Negative tests behaved as expected.
Fix (correction pass 1): service image -> postgres:18, plus a `client_server_major_match` setup check.
This NOTE.md was added after the run and is not covered by SHA256SUMS.

**Correction (integration, 2026-10-28):** the sentence "Negative tests behaved as expected" above is **not accurate**.
N01, N04, N05 and N06 were recorded as PASS but failed for an unrelated reason (`transaction_timeout` rejected by the
PG16 server, or `lab.ledger_entries` missing), so they are FALSE PASSES. See `reports/review-pr1-pr2.md` section 2 and
`python3 evidence/shared/validate_evidence.py postgres-negatives evidence/postgres/runs/ci-service-40630856041-1`.
The negatives were hardened on `overnight/integration` (setup split into separately-checked steps; expected error text checked in CI).
This run stays as a preserved failing run and is not gated.
