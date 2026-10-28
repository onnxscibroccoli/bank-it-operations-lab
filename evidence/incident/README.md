# evidence/incident — SIMULATION

> **SIMULATION.** Evidence from deliberately injected faults in a throwaway loopback lab. No production system, real customer, real vendor or real person was involved; no notification was sent.

| Item | Path |
|---|---|
| Incident report (findings, business impact, escalation, corrective actions, management update) | [`INCIDENT-REPORT-SIMULATION.md`](INCIDENT-REPORT-SIMULATION.md) |
| Run (executed for real on the lab box, 2026-10-28 14:18 EDT) | [`runs/local-20261028T181818Z/`](runs/local-20261028T181818Z/) — start with `TIMELINE.md` and `SUMMARY.json` |
| Console output of the run and of `selftest.sh` (outside the hashed run dir) | [`runs/local-20261028T181818Z.console/`](runs/local-20261028T181818Z.console/) |
| How to reproduce | [`scenarios/incident/README.md`](../../scenarios/incident/README.md) |

Verify: `python3 scenarios/incident/lib/timeline.py --verify evidence/incident/runs/local-20261028T181818Z` (re-derives
MTTD/MTTR from `events.jsonl` + `monitor.tsv` and checks `SHA256SUMS`).

## Environment notes (honest disclosure)

* Executed on the shared Linux lab box (Debian 13, Python 3.13.5), loopback only.
* PostgreSQL **17.10** server binaries: the box's apt mirror was unreachable (HTTP 500 / TLS EOF), so the
  binaries came from the npm package `@embedded-postgres/linux-x64@17.10.0-beta.17` (unpacked to
  `/opt/pgbin-sim`, passed via `PG_BIN`). No `psql` was available; SQL ran through
  `scenarios/incident/lib/pgclient.py` (ctypes → libpq 17).
* Docker was not available and was not needed.
* Escalation/notifications are recorded as policy decisions only (`escalation_simulated`), never sent.
