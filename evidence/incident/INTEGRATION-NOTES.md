# SIMULATION — Integration notes for the Lane C integrator (incident module, PR #22)

> **SIMULATION.** Everything referenced here is a deliberately injected fault in a throwaway,
> loopback-only lab. No production system, real bank, customer, vendor or person was involved and no
> notification was sent. Timings are lab measurements, **not** a bank SLA.

Context: PR #27 accelerated completion plan, lane **C — module closure** (incident). Owner paths:
`scenarios/incident/**`, `evidence/incident/**` only. Nothing outside those paths is changed by PR #22.
Claim classification: **EXECUTED_LOCAL + SIMULATION** (run executed for real on the lab box, 2026-10-28
14:18 EDT; not EXECUTED_CI). Run id: `local-20261028T181818Z`. Scenario commit recorded in the run:
`43e607ec31ad7e62b54e66ebb9abc5ca69d9ac52`.

## Coverage matrix

`R` = `evidence/incident/runs/local-20261028T181818Z`

| Requirement | Status | Where (file paths) |
|---|---|---|
| Reuse app/vendor mock, PostgreSQL, probes | Covered | `scenarios/incident/run_incident_demo.sh` (pinned refs, `git archive`), `scenarios/incident/README.md` §Components, `R/ENVIRONMENT.txt`, `R/logs/01_materialize_components.log`, `R/probe-config.json` |
| Failure injection (reproducible) | Covered | `run_incident_demo.sh` step `inject_pg_immediate_stop` (`pg_ctl stop -m immediate`), `R/logs/07_inject_pg_immediate_stop.log`, `R/events.jsonl` (`failure_injected`), `R/COMMANDS.tsv` |
| Detection (existing probes) | Covered | `R/monitor.tsv`, `R/polls/002.*` (`probe:core-ledger-db-tcp` UNHEALTHY), `R/events.jsonl` (`detected`), MTTD 3.584 s in `R/SUMMARY.json` |
| Diagnosis | Covered | `R/logs/08_diag_failed_checks.log` … `13_diag_business_txn_impact.log`, `R/logs/postgres-server.log`, `R/events.jsonl` (`diagnosed`) |
| Recovery / restore + integrity | Covered | `R/logs/14_restore_pg_start.log` … `19_verify_business_txn.log` (crash recovery logged, fingerprint identical to baseline `05_…`), `R/polls/003.*` HEALTHY, `R/events.jsonl` (`db_restarted`, `data_integrity_verified`, `service_restored`) |
| Timeline (America/New_York) | Covered | `R/TIMELINE.md`, `R/SUMMARY.json`, generator `scenarios/incident/lib/timeline.py` |
| Technical findings, business impact, escalation, corrective actions, management update | Covered | `evidence/incident/INCIDENT-REPORT-SIMULATION.md` (sections: Technical findings, Business impact, Escalation, Corrective and preventive actions, Management update). Escalation is policy-only (`escalation_simulated` event), nothing sent; business impact is qualitative, no invented figures |
| SIMULATION label | Covered | Headers of every authored file (`README.md`s, report, `TIMELINE.md`, this file); `"simulation": "SIMULATION"` in `R/SUMMARY.json` and every `R/events.jsonl` record (enforced by `--verify`); directory labels `R/SIMULATION.md` and `R.console/SIMULATION.md` cover raw `logs/`, `polls/`, `monitor.tsv` and console logs, which are hash-pinned tool output and are intentionally not edited |
| Tamper / negative checks | Covered | `scenarios/incident/selftest.sh` → `evidence/incident/runs/local-20261028T181818Z.console/selftest.log` |

## Verify (no PostgreSQL needed)

```bash
python3 scenarios/incident/lib/timeline.py --verify evidence/incident/runs/local-20261028T181818Z
# expected: "VERIFY PASS (SIMULATION run local-20261028T181818Z)", exit 0
scenarios/incident/selftest.sh evidence/incident/runs/local-20261028T181818Z
# expected: 4 PASS lines, "SIMULATION selftest: 0 failure(s)", exit 0
```

`--verify` re-derives every metric from `events.jsonl` + `monitor.tsv`, compares against `SUMMARY.json`,
requires the SIMULATION label in the summary and every event, and re-checks every file listed in
`SHA256SUMS`. Expected negative reasons (first three exercised by `selftest.sh`; last two checked by hand on a temp copy on 2026-10-28, 18:10 EDT):

| Negative case | Expected result |
|---|---|
| forged `mttd_s` in `SUMMARY.json` | exit 1, `VERIFY FAIL: SUMMARY.json metrics do not match values re-derived …` |
| `detected` event deleted | exit 1, `VERIFY FAIL: missing events: …` |
| PostgreSQL binaries missing (`PG_BIN=/nonexistent`) | exit 3, writes `NOT_EXECUTED.md`, no metrics invented |
| any hashed log/summary file edited | exit 1, `VERIFY FAIL: hash mismatch: <file>` |
| SIMULATION label removed from summary/events | exit 1, `VERIFY FAIL: SIMULATION label missing` |

Re-verified on 2026-10-28 at 18:09 EDT against head `3f13622` plus this notes commit: `--verify` PASS,
`selftest.sh` 4/4 PASS.

## Re-run the scenario (needs PostgreSQL server binaries)

```bash
git fetch origin vendor-mock observability ci-evidence-postgres   # pinned component commits must exist locally
PG_BIN=/path/to/postgresql/bin scenarios/incident/run_incident_demo.sh
# writes evidence/incident/runs/<new_run_id>/ ; then run --verify and selftest.sh on it
```

Bash, git, curl, Python ≥ 3.9 (stdlib only), PostgreSQL `initdb`/`pg_ctl`/`postgres` + `libpq`. Loopback
ports 18099 (vendor mock) and 55432 (PostgreSQL), overridable with `VENDOR_PORT` / `PG_PORT`. Docker not used.

## Dependencies on unmerged branches

The script extracts these components unchanged from fixed commits (overridable via `VENDOR_REF`,
`OBS_REF`, `PG_REF`). None is on `main` yet; if the integrator merges different heads, re-run and
re-verify, or keep these pins.

| Component | Branch @ commit | Used for |
|---|---|---|
| `integrations/vendor-mock` | `vendor-mock` @ `88a37856da05468ecce86b4c5d1e1ac0b8530bc5` | app / vendor API tier (`vendor_mock.server`, scenario `normal`) |
| `observability/healthcheck` | `observability` @ `3e40e39d73da3f0d20bced68651a54ee6c63846c` | probes (`collect`: HTTP + TCP + DNS, fail-closed) |
| `tests/integration/postgres/seed.sql`, `fingerprint.sql` | `ci-evidence-postgres` @ `e7399fbb538504f723d1fb83e32ce50604807b8e` | core-ledger seed (50 accounts / 1000 ledger rows) and integrity fingerprint |

## Adapter notes

* **PostgreSQL source.** The recorded run used PostgreSQL **17.10** server binaries from the npm package
  `@embedded-postgres/linux-x64@17.10.0-beta.17` (unpacked to `/opt/pgbin-sim`, passed via `PG_BIN`),
  because the box's apt mirror was unreachable. Any PostgreSQL ≥ 14 build with `initdb`/`pg_ctl` should
  work; the script auto-detects `pg_config --bindir` or `/usr/lib/postgresql/*/bin`, and adds
  `$PG_BIN/../lib` to `LD_LIBRARY_PATH`. For CI, the `ci-evidence-postgres` workflow's PostgreSQL or
  the distro `postgresql` package is the expected substitute.
* **`scenarios/incident/lib/pgclient.py`.** Stdlib-only libpq client over `ctypes` (`ping` → `PQping`,
  `query -c/-f`) because no `psql`/`pg_isready` was available. libpq lookup order: `$PG_LIBPQ`,
  `$PG_BIN/../lib/libpq.so.5`, `ctypes.util.find_library("pq")`. Local trust auth, no secrets. It can be
  swapped for `psql` without changing the evidence format.

## Known limits

* **MTTR is scripted.** 8.593 s is injection → monitor-confirmed HEALTHY with an automated runbook; it
  excludes human paging/response time and is not a bank SLA. MTTD is bounded by the 5 s poll interval.
* Malformed `monitor.tsv` (e.g. an appended junk line) makes `--verify` exit 1 with a Python traceback rather than a `VERIFY FAIL:` line: still fail-closed, but the message is not clean.
* Single run, single fault type (DB immediate stop). The DB probe is TCP-level only (see corrective action 1).
* EXECUTED_LOCAL, not EXECUTED_CI: no Actions workflow runs this scenario yet (corrective action 6; workflow
  wiring belongs to lane B, outside these paths).
* Escalation and business impact are illustrative; nothing was sent and no figures are invented.
* `/opt/pgbin-sim` from the recorded run is no longer present on the lab box; a fresh re-run needs
  PostgreSQL binaries supplied again. Verification of the existing run does not need them.
