# Week 7: Backup and restore you can prove (resilience and incidents 1 of 3)

**Branch:** `$PR2` = `ci-evidence-postgres@e610015` (PR #2), plus `$PR3` for checks.
**Prerequisites:** PostgreSQL server and client binaries with the **same major version** (`initdb`, `pg_ctl`, `pg_dump`, `pg_restore`, `psql`, `createdb`, `dropdb`, `pg_isready`). No network or cloud.
**Delivered files used:** `tests/integration/postgres/{run_restore_scenario.sh,seed.sql,fingerprint.sql,verify_evidence.sh}`, `tests/integration/README.md`,
`evidence/postgres/README.md`, `evidence/postgres/runs/local-offline-20261028T041038Z/`, `.github/workflows/postgres-restore-evidence.yml`.

## Daily exercises
**Day 1: Read the scenario.** `seed.sql` creates synthetic `lab.accounts` (50 rows) and `lab.ledger_entries` with an FK and a CHECK constraint.
`fingerprint.sql` computes per-table row counts plus an md5 of the ordered rows. List P01-P11 and N01-N06 from `run_restore_scenario.sh` (lines 124-146 at `e610015`).

**Day 2: Verify committed evidence.**
```bash
cd $PR2 && bash tests/integration/postgres/verify_evidence.sh evidence/postgres/runs/local-offline-20261028T041038Z; echo rc=$?
python3 $PR3/evidence/shared/validate_evidence.py postgres-negatives evidence/postgres/runs/local-offline-20261028T041038Z
```
- *Expected:* `positive=11 negative=6 failed=0`, rc 0, and `NEGATIVES OK: 6 negative steps failed for the intended reason`. (Executed: E13.)

**Day 3: Run the offline scenario.** `RUN_LABEL=practice-$(date -u +%Y%m%dT%H%M%SZ) bash tests/integration/postgres/run_restore_scenario.sh offline`
- *Expected* (per the committed run's `SUMMARY.md`): `Overall: PASS`. The current script has 31 steps, one more than the committed run, because it adds `client_server_major_match`.
  **UNEXECUTED here** (P-W7): no PostgreSQL binaries on the guide-writing machine, and `apt-get` failed with HTTP 500 from the Debian mirror.

**Day 4: Fingerprints.** Compare `fingerprints/source.txt`, `restore_ok.txt`, `restore_plain.txt` and `restore_tampered.txt` in the committed offline run.
Explain why a row count alone is not a restore proof.

**Day 5: Restore-time and RPO.** Read `COMMANDS.tsv` `duration_ms` for P01 and P04. These are lab-sized numbers. Discuss what they do *not* tell you about production RTO.

## Failure injection and recovery
The scenario *is* a failure-injection suite: a truncated dump (N01), a garbage archive (N02), a missing DB (N03), an FK violation after restore (N04),
a duplicate restore (N05), and tampering (N06). Each must fail **for the right reason**. `negative-expectations.postgres.json` (PR #3) holds the required error text.
Recovery is built in: the script captures every exit code and fails at the end, never at the first error.

## Answer notes
- A backup is not proven until a restore is compared against the source (P06 and P11 use `diff -u` on fingerprints).
- Custom format (`-Fc`) supports `--list` (P02) and selective restore. Plain SQL is portable but all-or-nothing.

## Architecture tradeoffs
- Offline unix-socket cluster (no network) versus service container (closer to CI reality). The repo runs both in CI.
- Committing evidence but gitignoring dumps (`evidence/postgres/.gitignore`) keeps the repo small, but `ARTIFACTS.sha256` then cannot be checked from git (PR #3 §1).

## Fifteen-minute walkthrough
Seed → dump → restore → fingerprint diff → six negatives → `verify_evidence.sh`.

## Interview questions
1. How do you prove a restore is complete and correct?
2. Why must negative tests assert the error text?
3. What would you add to measure RTO credibly?

## PENDING / UNEXECUTED
- P-W7: live offline and service-mode scenario runs. These need PostgreSQL binaries. Not executed in this guide.
- RDS-native backup and restore (snapshots, PITR, AWS Backup jobs): only declared in `aws-remediation-vpc-rds@099479e:infra/aws-cdk/lib/network-database-stack.ts`, never executed. There is no `backup/aws` module.
