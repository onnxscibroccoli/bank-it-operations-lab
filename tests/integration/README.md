# Integration tests

## `postgres/` — backup/restore exercise

`run_restore_scenario.sh [offline|service]` runs a pg_dump / pg_restore exercise against synthetic data
(`seed.sql`) and writes structured evidence to `evidence/postgres/runs/<RUN_LABEL>/`.

| Mode | Server | Network |
|------|--------|---------|
| `offline` (default) | throwaway `initdb` cluster, unix socket only (`listen_addresses=''`) | none |
| `service` | existing server from `PGHOST`/`PGPORT`/`PGUSER`/`PGPASSWORD` (CI service container) | localhost |

Positive tests (must exit 0): custom-format dump, TOC listing, restore, row-count + content
fingerprint match (`fingerprint.sql`), plain-SQL dump and `psql` restore with fingerprint match.

Negative tests (must exit non-zero, and are recorded as PASS when they do):

| id | scenario |
|----|----------|
| N01 | restore a truncated custom dump |
| N02 | list a file that is not a Postgres archive |
| N03 | restore into a database that does not exist |
| N04 | insert an orphan row into the restored DB (FK constraint must survive restore) |
| N05 | restore twice into the same DB with `--exit-on-error` (duplicate objects) |
| N06 | tamper with a restored row; fingerprint diff must detect it |

The script never stops on the first failure: every exit code is captured in `COMMANDS.tsv`, then it
exits 1 if any expectation was not met. `verify_evidence.sh <run dir>` re-checks hashes and results.

No cloud credentials or network access are used. Requires PostgreSQL client/server binaries
(auto-detected from `pg_config`, `/usr/lib/postgresql/*/bin`, or `PG_BIN`).
