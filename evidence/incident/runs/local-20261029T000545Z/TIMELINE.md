# SIMULATION — incident timeline (local-20261029T000545Z)

> **SIMULATION.** Fault injected on purpose into a throwaway local lab. No real bank, customer, vendor or production system was involved. Notifications listed here were **not sent**.

Status: **PASS**  
MTTD **3.590 s** · time to diagnose 0.130 s · detect→restore 5.086 s · **MTTR 8.677 s** (injection → monitor-confirmed HEALTHY) · DB unavailable 3.838 s

Polls: 3 total, 1 UNHEALTHY; cross-check against monitor.tsv: OK

| # | Time (America/New_York) | UTC | Event | Detail |
|---|---|---|---|---|
| 1 | 2026-10-28 20:05:46.806 EDT | 2026-10-29T00:05:46.806219Z | `baseline_healthy` | {"exit_code": 0, "failed_checks": "", "overall": "HEALTHY", "poll_finished_utc": "2026-10-29T00:05:46.657817Z", "poll_seq": 1} |
| 2 | 2026-10-28 20:05:48.311 EDT | 2026-10-29T00:05:48.311390Z | `failure_injected` | {"component": "postgres:55432", "fault": "core-ledger PostgreSQL killed: pg_ctl stop -m immediate"} |
| 3 | 2026-10-28 20:05:51.901 EDT | 2026-10-29T00:05:51.901809Z | `detected` | {"exit_code": 1, "failed_checks": "probe:core-ledger-db-tcp", "overall": "UNHEALTHY", "poll_finished_utc": "2026-10-29T00:05:51.736058Z", "poll_seq": 2} |
| 4 | 2026-10-28 20:05:51.904 EDT | 2026-10-29T00:05:51.904035Z | `escalation_simulated` | {"channel": "SIMULATED - no message sent", "notified": "DB on-call, incident commander, service desk lead", "severity": "SEV1 (core ledger unavailable)"} |
| 5 | 2026-10-28 20:05:52.032 EDT | 2026-10-29T00:05:52.032190Z | `diagnosed` | {"evidence": "diag_* steps in COMMANDS.tsv", "root_cause": "core-ledger PostgreSQL postmaster not running (immediate shutdown); vendor API tier and DNS healthy"} |
| 6 | 2026-10-28 20:05:52.034 EDT | 2026-10-29T00:05:52.034027Z | `restore_started` | runbook: start PostgreSQL, let crash recovery complete, verify data, confirm via monitor |
| 7 | 2026-10-28 20:05:52.149 EDT | 2026-10-29T00:05:52.149039Z | `db_restarted` | pg_ctl start returned 0 |
| 8 | 2026-10-28 20:05:52.247 EDT | 2026-10-29T00:05:52.247864Z | `data_integrity_verified` | lab.accounts, lab.ledger_entries, lab.account_balances row counts and md5 identical to baseline |
| 9 | 2026-10-28 20:05:56.988 EDT | 2026-10-29T00:05:56.988200Z | `service_restored` | {"exit_code": 0, "failed_checks": "", "overall": "HEALTHY", "poll_finished_utc": "2026-10-29T00:05:56.806649Z", "poll_seq": 3} |
| 10 | 2026-10-28 20:06:01.826 EDT | 2026-10-29T00:06:01.826754Z | `monitoring_stopped` | scenario complete; stack torn down |

## Monitor polls (observability `collect`)

| seq | finished (America/New_York) | exit | overall | failed checks |
|---|---|---|---|---|
| 1 | 2026-10-28 20:05:46.657 EDT | 0 | HEALTHY | — |
| 2 | 2026-10-28 20:05:51.736 EDT | 1 | UNHEALTHY | probe:core-ledger-db-tcp |
| 3 | 2026-10-28 20:05:56.806 EDT | 0 | HEALTHY | — |
