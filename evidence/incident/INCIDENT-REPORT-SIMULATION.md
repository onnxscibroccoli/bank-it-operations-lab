# SIMULATION — Incident report SIM-INC-2026-10-28-01: core-ledger database outage

> **SIMULATION — NOT A REAL INCIDENT.** Fault injected on purpose into a loopback lab stack
> (fictional "Acme Core Ledger SIMULATION" vendor mock + synthetic PostgreSQL ledger). Times are real
> measurements from run `local-20261028T181818Z`; people, paging and business figures are illustrative. No message was sent.

| Field | Value |
|---|---|
| Severity | SEV1 (simulated): core ledger unavailable → balance/posting lookups fail |
| Status | Resolved (service restored, data verified) |
| Window | 2026-10-28 14:18:20.726 → 14:18:29.319 EDT (America/New_York) |
| **MTTD** | **3.584 s** (injection → detecting poll finished; poll interval 5 s) |
| Time to diagnose | 0.178 s (automated triage) |
| Detect → restored | 5.009 s |
| **MTTR** | **8.593 s** (injection → monitor-confirmed HEALTHY) |
| DB unavailable | 3.878 s (injection → `pg_ctl start` returned) |
| Data loss | None: row counts and md5 of `lab.accounts`, `lab.ledger_entries`, `lab.account_balances` identical to baseline |
| Evidence | [`runs/local-20261028T181818Z/TIMELINE.md`](runs/local-20261028T181818Z/TIMELINE.md), `COMMANDS.tsv` (19 steps, all PASS), `SHA256SUMS`, selftest 4/4 PASS |

## Timeline (America/New_York, EDT)

| Time | Event |
|---|---|
| 14:18:19.070 | Monitor poll 1 HEALTHY (vendor-api-http, core-ledger-db-tcp, resolver-dns, host metrics) |
| 14:18:20.726 | **Fault injected**: `pg_ctl stop -m immediate` on core-ledger PostgreSQL (127.0.0.1:55432) |
| 14:18:24.142 | **Detected**: poll 2 UNHEALTHY, `probe:core-ledger-db-tcp` FAIL (ConnectionRefusedError), endpoint decision 503 |
| 14:18:24.312 | Escalation rule fired: SEV1 → DB on-call, incident commander, service-desk lead (**simulated, not sent**) |
| 14:18:24.488 | **Diagnosed**: postmaster not running; vendor API and DNS healthy |
| 14:18:24.490 | Restore started (runbook: start DB → crash recovery → verify data → confirm via monitor) |
| 14:18:24.604 | PostgreSQL started; log shows `database system was not properly shut down; automatic recovery in progress` → redo done |
| 14:18:24.757 | Data integrity verified against baseline fingerprint; balance query OK |
| 14:18:29.213 | **Service restored**: poll 3 HEALTHY |

## Technical findings

1. **Root cause (injected):** the core-ledger PostgreSQL postmaster was terminated without a checkpoint
   (`received immediate shutdown request` in the server log). Simulates a DB process crash / OOM kill / host reboot.
2. **Detection worked as designed.** The existing observability `collect` probes failed closed: only
   `probe:core-ledger-db-tcp` failed, and the endpoint decision flipped to `serve:false / 503`.
   MTTD was bounded by the 5 s poll interval (fault landed 1.5 s after a healthy poll).
3. **Triage isolated the tier in < 0.2 s:** vendor API `/v1/health` 200, `PQping` = `PQPING_NO_RESPONSE`,
   `pg_ctl status` = no server running (exit 3), business query `account_balances` → connection refused.
4. **Recovery was clean:** WAL crash recovery replayed to a consistent state; the fingerprint (1000 ledger
   rows, 50 accounts, balances view) matched the pre-incident baseline exactly.
5. **Gaps observed:**
   * The TCP probe proves the port is open, not that the DB answers queries; a query-level probe
     (e.g. `SELECT 1` / balance lookup) would also catch hung-but-listening states.
   * Nothing restarted the DB automatically; restore was a scripted runbook step. Without automation,
     MTTR is dominated by human response (page → acknowledge → act), which this lab does not measure.
   * Single DB instance: no replica/failover, so any crash is a full outage of ledger reads.

## Business impact (illustrative, SIMULATION)

* **Measured in the lab:** 3.9 s of core-ledger unavailability; 8.6 s until monitoring confirmed full service;
  balance lookups failed during the outage (`diag_business_txn_impact`); no data lost or corrupted.
* **What this outage class would mean for a bank:** balance inquiries, transaction history and posting would
  fail for online/mobile banking, branch tellers and the contact centre; card authorisations relying on
  real-time balances would fall back to stand-in limits; payments may queue. Regulatory exposure arises if
  the outage breaches published service levels or incident-reporting thresholds. No monetary or customer
  counts are given because none were measured — any figure would be invented.

## Escalation (policy applied; SIMULATED — nothing sent)

| Time from detection | Action | Owner (role) |
|---|---|---|
| 0 min | Auto-page DB on-call + incident commander; open SEV1 bridge; service-desk lead informed | Monitoring / IC |
| 15 min unresolved | Notify Head of IT Operations; status-page / customer-comms draft prepared | IC |
| 30 min unresolved | Executive + business-line notification; assess vendor (Acme Core Ledger SIMULATION) involvement per vendor-risk escalation runbook | Head of IT Ops |
| Regulatory threshold met | Compliance/risk evaluate regulator and customer notification obligations | CRO delegate |

In this run the incident resolved before the first time-based step, so only the initial page would have occurred.

## Corrective and preventive actions

| # | Action | Type | Owner (role) | Priority |
|---|---|---|---|---|
| 1 | Add a query-level DB probe (`SELECT 1` and a read-only balance lookup) beside the TCP probe | Detective | Observability | High |
| 2 | Run the DB under a supervisor (systemd `Restart=on-failure` / managed service) so crash restarts are automatic | Corrective | Platform | High |
| 3 | Shorten the core-ledger poll interval to ≤ 15 s in production with 2-of-3 confirmation to avoid flapping | Detective | Observability | Medium |
| 4 | Add a streaming replica with tested failover; rehearse quarterly with this scenario | Preventive | DBA | Medium |
| 5 | Keep post-restore verification (fingerprint/reconciliation) mandatory before declaring service restored | Process | Ops | High |
| 6 | Run this scenario in CI on each change to probes or runbook (`run_incident_demo.sh` + `selftest.sh`) | Preventive | Ops engineering | Medium |

## Management update (concise)

> **SIMULATION drill — core-ledger database outage — resolved.**
> At 14:18:20 EDT we deliberately crashed the lab's core-ledger database. Monitoring caught it in 3.6 seconds,
> automated checks pinpointed the database (not the vendor API) within 0.2 seconds, and service was restored and
> confirmed in 8.6 seconds with no data loss. The drill shows detection and recovery tooling work; the main risks
> are that a real crash today would not restart itself and that our database check confirms the port only, not
> real queries. We are adding a query-level health check and automatic restart (high priority), then a standby
> replica with rehearsed failover. No customer, production system or vendor was affected.
