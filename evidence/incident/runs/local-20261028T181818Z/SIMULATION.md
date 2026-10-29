# SIMULATION — label for this run directory

> **SIMULATION.** Every file in `evidence/incident/runs/local-20261028T181818Z/` (including all of
> `logs/`, `polls/`, `COMMANDS.tsv`, `events.jsonl`, `monitor.tsv`, `probe-config.json`,
> `ENVIRONMENT.txt`, `SUMMARY.json`, `TIMELINE.md` and `SHA256SUMS`) is evidence from a deliberately
> injected fault in a throwaway, loopback-only lab on 2026-10-28 (14:18 EDT). No production system,
> real bank, customer, vendor or person was involved, and no notification was sent.

Raw logs and poll payloads are byte-for-byte tool output and are hash-pinned in `SHA256SUMS`, so they
deliberately carry no inline SIMULATION marker; this file supplies the label for the whole directory.
This file is added after the run and is intentionally **not** listed in `SHA256SUMS`
(`timeline.py --verify` checks only the listed files, so verification is unaffected).

Claim classification (PR #27 plan vocabulary): **EXECUTED_LOCAL** + **SIMULATION**.
