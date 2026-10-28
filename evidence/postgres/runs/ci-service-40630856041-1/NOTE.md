Preserved failing run: https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041
Service job used pg_dump 18.6 (ubuntu-latest, now Ubuntu 26.04) against a postgres:16 service container.
pg_dump 18 emits `SET transaction_timeout = 0;`, which PostgreSQL 16 rejects, so P04 and P09 restores failed
(and P05/P06/P10/P11 failed as a consequence). Negative tests behaved as expected.
Fix (correction pass 1): service image -> postgres:18, plus a `client_server_major_match` setup check.
This NOTE.md was added after the run and is not covered by SHA256SUMS.
