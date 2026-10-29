# SIMULATION — integrated incident demonstration

> **SIMULATION.** Every fault here is injected on purpose into a throwaway, loopback-only lab stack.
> No real bank, customer, vendor, production system or person is involved, and no notification is sent.

One script brings up the lab's **existing** components, injects a reproducible failure, lets the
existing probes detect it, runs automated triage, restores service, verifies data integrity and writes
a timeline with MTTD/MTTR (America/New_York).

## Components reused (unmodified, pinned commits, extracted with `git archive` into a temp dir)

| Tier | Component | Source |
|---|---|---|
| App / vendor API | `integrations/vendor-mock` loopback server (`vendor_mock.server`, scenario `normal`) | `vendor-mock` @ `88a3785` |
| Monitoring | `observability/healthcheck collect` (HTTP + TCP + DNS probes, fail-closed decision) | `observability` @ `3e40e39` |
| Core-ledger DB | PostgreSQL with `tests/integration/postgres/seed.sql` (50 accounts / 1000 ledger rows) and `fingerprint.sql` | `ci-evidence-postgres` @ `e7399fb` |

Nothing outside `scenarios/incident/` and `evidence/incident/` is changed.

## The incident

| Phase | What happens | Evidence |
|---|---|---|
| Baseline | monitor polls every `POLL_INTERVAL_S` (5 s) until HEALTHY | `monitor.tsv`, `polls/` |
| Inject | `pg_ctl stop -m immediate` on the core-ledger DB (crash-equivalent, no checkpoint) `INJECT_OFFSET_S` (1.5 s) after a healthy poll | `failure_injected` event |
| Detect | first UNHEALTHY poll that **started after** injection (`probe:core-ledger-db-tcp` → 503) | `detected` event |
| Escalate | SEV1 rule recorded — **simulated, nothing sent** | `escalation_simulated` |
| Diagnose | failed checks; vendor tier healthy; `PQping` = NO_RESPONSE; `pg_ctl status` = no server; server log shows `immediate shutdown request`; business balance query fails | `diag_*` in `COMMANDS.tsv` |
| Restore | `pg_ctl start`; crash recovery (`not properly shut down; automatic recovery`) | `restore_*`, `verify_crash_recovery_logged` |
| Verify | `PQping` OK; fingerprint (row counts + md5 of all rows) identical to baseline; balance query OK; monitor HEALTHY | `verify_*`, `service_restored` |

Metrics: **MTTD** = injection → detecting poll finished; **MTTR** = injection → monitor-confirmed HEALTHY.
Every step is a logged command with an expected exit code (and output regex); any mismatch makes the run FAIL.

## Run

```bash
git fetch origin vendor-mock observability ci-evidence-postgres   # pinned component commits
PG_BIN=/path/to/postgresql/bin scenarios/incident/run_incident_demo.sh   # auto-detects pg_config / /usr/lib/postgresql/*/bin
scenarios/incident/selftest.sh evidence/incident/runs/<run_id>          # negative checks of the evidence tooling
python3 scenarios/incident/lib/timeline.py --verify evidence/incident/runs/<run_id>
```

Requirements: bash, git, curl, Python ≥ 3.9 (stdlib only), PostgreSQL server binaries (`initdb`, `pg_ctl`,
`postgres`) and `libpq`. No `psql` needed: `lib/pgclient.py` talks to libpq via `ctypes`. Ports 18099
(vendor mock) and 55432 (PostgreSQL) on 127.0.0.1, overridable with `VENDOR_PORT` / `PG_PORT`.
If PostgreSQL binaries are missing the run stops with exit 3 and writes `NOT_EXECUTED.md` — no metrics are invented.

Outputs in `evidence/incident/runs/<run_id>/`: `TIMELINE.md`, `SUMMARY.json`, `events.jsonl`, `monitor.tsv`,
`COMMANDS.tsv`, `logs/`, `polls/`, `probe-config.json`, `ENVIRONMENT.txt`, `SHA256SUMS`.
`timeline.py --verify` re-derives every metric from the raw events/polls and re-checks hashes, so an
edited summary fails verification.
