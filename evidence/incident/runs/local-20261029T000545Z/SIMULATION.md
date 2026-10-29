# SIMULATION — label for this run directory

> **SIMULATION.** Every file in `evidence/incident/runs/local-20261029T000545Z/` (including all of `logs/`, `polls/`,
> `COMMANDS.tsv`, `events.jsonl`, `monitor.tsv`, `probe-config.json`, `ENVIRONMENT.txt`, `SUMMARY.json`,
> `TIMELINE.md` and `SHA256SUMS`) is evidence from a deliberately injected fault in a throwaway, loopback-only lab
> on 2026-10-28 (20:05 EDT, run by the integrator on the integration box with PostgreSQL 16.15). No production system,
> real bank, customer, vendor or person was involved, and no notification was sent.

This run was added alongside `local-20261028T181818Z`. Nothing earlier was overwritten. This label was added after
the run and is intentionally **not** listed in `SHA256SUMS`, the same convention as the earlier run.

Claim classification (PR #27 plan vocabulary): **EXECUTED_LOCAL** + **SIMULATION**.
