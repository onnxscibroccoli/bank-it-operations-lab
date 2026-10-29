# SIMULATION — incident timeline (local-20261028T181818Z)

> **SIMULATION.** Fault injected on purpose into a throwaway local lab. No real bank, customer, vendor or production system was involved. Notifications listed here were **not sent**.

Status: **PASS**  
MTTD **3.584 s** · time to diagnose 0.178 s · detect→restore 5.009 s · **MTTR 8.593 s** (injection → monitor-confirmed HEALTHY) · DB unavailable 3.878 s

Polls: 3 total, 1 UNHEALTHY; cross-check against monitor.tsv: OK

| # | Time (America/New_York) | UTC | Event | Detail |
|---|---|---|---|---|
| 1 | 2026-10-28 14:18:19.221 EDT | 2026-10-28T18:18:19.221170Z | `baseline_healthy` | {"exit_code": 0, "failed_checks": "", "overall": "HEALTHY", "poll_finished_utc": "2026-10-28T18:18:19.070434Z", "poll_seq": 1} |
| 2 | 2026-10-28 14:18:20.726 EDT | 2026-10-28T18:18:20.726332Z | `failure_injected` | {"component": "postgres:55432", "fault": "core-ledger PostgreSQL killed: pg_ctl stop -m immediate"} |
| 3 | 2026-10-28 14:18:24.310 EDT | 2026-10-28T18:18:24.310081Z | `detected` | {"exit_code": 1, "failed_checks": "probe:core-ledger-db-tcp", "overall": "UNHEALTHY", "poll_finished_utc": "2026-10-28T18:18:24.142332Z", "poll_seq": 2} |
| 4 | 2026-10-28 14:18:24.312 EDT | 2026-10-28T18:18:24.312345Z | `escalation_simulated` | {"channel": "SIMULATED - no message sent", "notified": "DB on-call, incident commander, service desk lead", "severity": "SEV1 (core ledger unavailable)"} |
| 5 | 2026-10-28 14:18:24.488 EDT | 2026-10-28T18:18:24.488523Z | `diagnosed` | {"evidence": "diag_* steps in COMMANDS.tsv", "root_cause": "core-ledger PostgreSQL postmaster not running (immediate shutdown); vendor API tier and DNS healthy"} |
| 6 | 2026-10-28 14:18:24.490 EDT | 2026-10-28T18:18:24.490650Z | `restore_started` | runbook: start PostgreSQL, let crash recovery complete, verify data, confirm via monitor |
| 7 | 2026-10-28 14:18:24.604 EDT | 2026-10-28T18:18:24.604725Z | `db_restarted` | pg_ctl start returned 0 |
| 8 | 2026-10-28 14:18:24.757 EDT | 2026-10-28T18:18:24.757508Z | `data_integrity_verified` | lab.accounts, lab.ledger_entries, lab.account_balances row counts and md5 identical to baseline |
| 9 | 2026-10-28 14:18:29.319 EDT | 2026-10-28T18:18:29.319266Z | `service_restored` | {"exit_code": 0, "failed_checks": "", "overall": "HEALTHY", "poll_finished_utc": "2026-10-28T18:18:29.213946Z", "poll_seq": 3} |
| 10 | 2026-10-28 14:18:34.233 EDT | 2026-10-28T18:18:34.233374Z | `monitoring_stopped` | scenario complete; stack torn down |

## Monitor polls (observability `collect`)

| seq | finished (America/New_York) | exit | overall | failed checks |
|---|---|---|---|---|
| 1 | 2026-10-28 14:18:19.070 EDT | 0 | HEALTHY | — |
| 2 | 2026-10-28 14:18:24.142 EDT | 1 | UNHEALTHY | probe:core-ledger-db-tcp |
| 3 | 2026-10-28 14:18:29.213 EDT | 0 | HEALTHY | — |
