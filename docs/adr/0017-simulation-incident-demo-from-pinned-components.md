# 0017: Incident demo composed from pinned, unmodified components, with metrics re-derived on verify
- Status: **Proposed.** #22 is an open draft, not integrated in #7, with no CI. SIMULATION, loopback only.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- `incident-demo@3f13622:scenarios/incident/run_incident_demo.sh` extracts the vendor mock (`88a3785`), observability (`3e40e39`) and the Postgres seed and fingerprint (`e7399fb`) with `git archive` and leaves them unmodified (`scenarios/incident/README.md`).
- Each phase (inject, detect, escalate (simulated), diagnose, restore, verify) is a logged command with an expected exit code and output regex. Any mismatch fails the run.
- `scenarios/incident/lib/timeline.py --verify` re-derives MTTD and MTTR from `events.jsonl` and `monitor.tsv` and re-checks hashes. Missing PG binaries give exit 3 and `NOT_EXECUTED.md`, never invented metrics.

## Consequences
- The demo tests the real fail-closed probe (ADR-0012) and fingerprint restore proof (ADR-0009) together, but against pinned, older component SHAs. If #9 moves (it is now at `d6efb82`), the pin has to be re-validated.
- Verified here (R18): a fresh run PASSed with 19 steps, MTTD 3.596 s and MTTR 8.52 s. Selftest gave 0 failures and verify PASSed. A tampered SUMMARY gives VERIFY FAIL, exit 1.
