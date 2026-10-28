#!/usr/bin/env bash
# Postgres backup/restore exercise (harness v2: every expected failure must fail for its declared reason).
#
# Usage: run_restore_scenario.sh [offline|service]
#   offline : throwaway initdb cluster listening ONLY on a unix socket (no TCP, no cloud)
#   service : existing server from PGHOST/PGPORT/PGUSER/PGPASSWORD (CI service container)
#
# Cases and their expected outcome/reason live in expectations.tsv; see lib.sh for the classification rules.
# Every negative test runs as ONE command after separately-checked setup steps, so a setup error can
# never be mistaken for the injected fault. Exit 0 only if every declared case PASSed exactly once.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
MODE="${1:-${PG_SCENARIO_MODE:-offline}}"
case "$MODE" in offline|service) ;; *) echo "unknown mode: $MODE" >&2; exit 2 ;; esac
RUN_LABEL="${RUN_LABEL:-local-${MODE}-$(date -u +%Y%m%dT%H%M%SZ)}"
EVIDENCE_DIR="${EVIDENCE_DIR:-$REPO_ROOT/evidence/postgres/runs/$RUN_LABEL}"
ARTIFACT_DIR="$EVIDENCE_DIR/artifacts"
FP_DIR="$EVIDENCE_DIR/fingerprints"
mkdir -p "$ARTIFACT_DIR" "$FP_DIR"

# shellcheck source=lib.sh
. "$HERE/lib.sh"
h_init "$EVIDENCE_DIR" "$HERE/expectations.tsv" "$MODE"

# ---------- locate binaries ----------
if [ -z "${PG_BIN:-}" ]; then
  if command -v pg_config >/dev/null 2>&1 && [ -x "$(pg_config --bindir)/initdb" ]; then PG_BIN="$(pg_config --bindir)"
  else PG_BIN="$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)"; fi
fi
[ -n "${PG_BIN:-}" ] && export PATH="$PG_BIN:$PATH"

PSQL=(psql -X -v ON_ERROR_STOP=1 -v VERBOSITY=verbose -q)
DUMP="$ARTIFACT_DIR/lab_source.dump"
PLAIN="$ARTIFACT_DIR/lab_source.sql"
TRUNC="$ARTIFACT_DIR/truncated.dump"
GARBAGE="$ARTIFACT_DIR/garbage.dump"

# ---------- step functions (each is one checked command) ----------
required_tools() {
  local t rc=0
  for t in psql pg_dump pg_restore createdb dropdb pg_isready diff sha256sum awk; do
    if command -v "$t" >/dev/null 2>&1; then echo "found $t: $(command -v "$t")"; else echo "missing $t: not found"; rc=127; fi
  done
  if [ "$MODE" = offline ]; then
    for t in initdb pg_ctl; do
      if command -v "$t" >/dev/null 2>&1; then echo "found $t: $(command -v "$t")"; else echo "missing $t: not found"; rc=127; fi
    done
  fi
  return $rc
}
OFFLINE_DIR=""
cleanup() {
  if [ -n "$OFFLINE_DIR" ] && [ -d "$OFFLINE_DIR" ]; then
    pg_ctl -D "$OFFLINE_DIR/data" -m fast stop >/dev/null 2>&1 || true
    rm -rf "$OFFLINE_DIR"
  fi
}
trap cleanup EXIT
offline_initdb() { initdb -D "$OFFLINE_DIR/data" -U postgres --auth=trust -E UTF8 --locale=C; }
offline_start() {
  pg_ctl -D "$OFFLINE_DIR/data" -w -l "$OFFLINE_DIR/server.log" \
    -o "-c listen_addresses='' -k $OFFLINE_DIR/sock -p 54329" start
}
major_match() {
  local client server_num server
  client="$(pg_dump --version | sed -E 's/^[^0-9]*([0-9]+).*/\1/')" || return 1
  server_num="$(psql -X -d postgres -Atc 'show server_version_num')" || return 1
  server=$(( server_num / 10000 ))
  echo "pg_dump: $(pg_dump --version)"
  echo "server_version_num: $server_num"
  if [ "$client" = "$server" ]; then echo "client_major=$client server_major=$server match"; return 0; fi
  echo "client_major=$client server_major=$server MISMATCH (pg_dump output may use settings the server rejects)"; return 1
}
reset_databases() {
  local db
  for db in lab_source lab_restore_ok lab_restore_plain lab_restore_trunc lab_restore_dup lab_restore_tamper lab_db_does_not_exist; do
    dropdb --if-exists "$db" || return 1
  done
}
fingerprint() { "${PSQL[@]}" -d "$1" -At -f "$HERE/fingerprint.sql" > "$2" && cat "$2"; }
fingerprint_sanity() {
  local f="$FP_DIR/source.txt"
  grep -Eq '^lab\.accounts\|50\|[0-9a-f]{32}$' "$f" &&
  grep -Eq '^lab\.ledger_entries\|1000\|[0-9a-f]{32}$' "$f" &&
  grep -Eq '^lab\.account_balances\|50\|[0-9a-f]{32}$' "$f" &&
  [ "$(wc -l < "$f")" -eq 3 ] && echo "fingerprint ok: 3 tables"
}
toc_list() { pg_restore --list "$DUMP" | tee "$ARTIFACT_DIR/lab_source.toc"; }
make_truncated() {
  local size; size=$(stat -c %s "$DUMP") || return 1
  [ "$size" -gt 1024 ] || { echo "dump too small: $size"; return 1; }
  head -c $((size / 2)) "$DUMP" > "$TRUNC" || return 1
  local tsize; tsize=$(stat -c %s "$TRUNC")
  [ "$tsize" -gt 0 ] && [ "$tsize" -lt "$size" ] && echo "truncated $tsize of $size bytes"
}
make_garbage() { printf 'this is not a postgres archive\n' > "$GARBAGE" && sha256sum "$GARBAGE"; }
assert_db_absent() {
  local n; n="$(psql -X -d postgres -Atc "select count(*) from pg_database where datname='lab_db_does_not_exist'")" || return 1
  [ "$n" = 0 ] && echo absent
}
n04_precondition() {
  local entries orphan
  entries="$(psql -X -d lab_restore_ok -Atc 'select count(*) from lab.ledger_entries')" || return 1
  orphan="$(psql -X -d lab_restore_ok -Atc 'select count(*) = 0 from lab.accounts where account_id = 424242')" || return 1
  [ "$orphan" = t ] && orphan=1 || orphan=0
  echo "ledger_entries=$entries orphan_account_absent=$orphan"
  [ "$entries" = 1000 ] && [ "$orphan" = 1 ]
}
restore() { pg_restore --exit-on-error --no-owner -d "$1" "$2"; }

# ---------- environment record ----------
{
  echo "run_label=$RUN_LABEL"
  echo "mode=$MODE"
  echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uname=$(uname -srm)"
  echo "pg_bin=${PG_BIN:-}"
  echo "pg_dump=$(pg_dump --version 2>&1)"
  echo "git_sha=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "git_tree_dirty=$(git -C "$REPO_ROOT" status --porcelain -- tests/integration 2>/dev/null | grep -q . && echo yes || echo no)"
  for f in lib.sh run_restore_scenario.sh expectations.tsv seed.sql fingerprint.sql; do
    echo "sha256_$f=$(sha256sum "$HERE/$f" | cut -c1-64)"
  done
  echo "github_run_id=${GITHUB_RUN_ID:-}"
  echo "github_run_attempt=${GITHUB_RUN_ATTEMPT:-}"
  echo "github_sha=${GITHUB_SHA:-}"
} > "$EVIDENCE_DIR/ENVIRONMENT.txt"

# ---------- setup ----------
run_case S00_required_tools required_tools
if [ "$MODE" = offline ]; then
  OFFLINE_DIR="$(mktemp -d)"; mkdir -p "$OFFLINE_DIR/sock"
  export PGHOST="$OFFLINE_DIR/sock" PGPORT=54329 PGUSER=postgres; unset PGPASSWORD
  run_case --needs S00_required_tools S01_offline_initdb offline_initdb
  run_case --needs S01_offline_initdb S02_offline_start offline_start
  BASE=S02_offline_start
else
  BASE=S00_required_tools
fi
run_case --needs $BASE S03_server_ready pg_isready -t 30
run_case --needs S03_server_ready S04_client_server_major_match major_match
G=S04_client_server_major_match   # gate: nothing below runs on a version mismatch
run_case --needs $G S05_reset_databases reset_databases
run_case --needs S05_reset_databases S06_create_source createdb lab_source
run_case --needs S06_create_source S07_seed_source "${PSQL[@]}" -d lab_source -f "$HERE/seed.sql"
run_case --needs S07_seed_source S08_fingerprint_source fingerprint lab_source "$FP_DIR/source.txt"
run_case --needs S08_fingerprint_source S09_fingerprint_source_sanity fingerprint_sanity
SRC=S09_fingerprint_source_sanity

# ---------- positive ----------
run_case --needs $SRC P01_pg_dump_custom pg_dump -Fc --no-owner -d lab_source -f "$DUMP"
run_case --needs P01_pg_dump_custom P02_pg_restore_list toc_list
run_case --needs $SRC P03_createdb_target createdb lab_restore_ok
run_case --needs P01_pg_dump_custom,P03_createdb_target P04_pg_restore restore lab_restore_ok "$DUMP"
run_case --needs P04_pg_restore P05_fingerprint_restored fingerprint lab_restore_ok "$FP_DIR/restore_ok.txt"
run_case --needs P05_fingerprint_restored P06_compare_restored diff -u "$FP_DIR/source.txt" "$FP_DIR/restore_ok.txt"
run_case --needs $SRC P07_pg_dump_plain pg_dump -Fp --no-owner -d lab_source -f "$PLAIN"
run_case --needs $SRC P08_createdb_plain createdb lab_restore_plain
run_case --needs P07_pg_dump_plain,P08_createdb_plain P09_psql_restore_plain "${PSQL[@]}" -d lab_restore_plain -f "$PLAIN"
run_case --needs P09_psql_restore_plain P10_fingerprint_plain fingerprint lab_restore_plain "$FP_DIR/restore_plain.txt"
run_case --needs P10_fingerprint_plain P11_compare_plain diff -u "$FP_DIR/source.txt" "$FP_DIR/restore_plain.txt"

# ---------- negative: setup steps are checked separately; the fault step is one command ----------
run_case --needs $SRC S_N01_createdb createdb lab_restore_trunc
run_case --needs P01_pg_dump_custom S_N01_make_truncated_dump make_truncated
run_case --needs S_N01_createdb,S_N01_make_truncated_dump N01_restore_truncated_dump restore lab_restore_trunc "$TRUNC"

run_case --needs $G S_N02_make_garbage_file make_garbage
run_case --needs S_N02_make_garbage_file N02_list_garbage_archive pg_restore --list "$GARBAGE"

run_case --needs $G S_N03_assert_database_absent assert_db_absent
run_case --needs S_N03_assert_database_absent,P01_pg_dump_custom N03_restore_missing_database restore lab_db_does_not_exist "$DUMP"

run_case --needs P06_compare_restored S_N04_precondition n04_precondition
run_case --needs S_N04_precondition N04_fk_enforced_after_restore "${PSQL[@]}" -d lab_restore_ok -c \
  "insert into lab.ledger_entries(entry_id, account_id, amount_cents, memo, posted_on) values (999999, 424242, 1, 'orphan', current_date)"

run_case --needs $SRC S_N05_createdb createdb lab_restore_dup
run_case --needs S_N05_createdb,P01_pg_dump_custom S_N05_first_restore restore lab_restore_dup "$DUMP"
run_case --needs S_N05_first_restore N05_restore_over_existing_objects restore lab_restore_dup "$DUMP"

run_case --needs $SRC S_N06_createdb createdb lab_restore_tamper
run_case --needs S_N06_createdb,P01_pg_dump_custom S_N06_restore restore lab_restore_tamper "$DUMP"
run_case --needs S_N06_restore S_N06_tamper_row psql -X -v ON_ERROR_STOP=1 -d lab_restore_tamper -c \
  "update lab.ledger_entries set amount_cents = amount_cents + 1 where entry_id = 500"
run_case --needs S_N06_tamper_row S_N06_fingerprint_tampered fingerprint lab_restore_tamper "$FP_DIR/restore_tampered.txt"
run_case --needs S_N06_fingerprint_tampered N06_tamper_detected diff -u "$FP_DIR/source.txt" "$FP_DIR/restore_tampered.txt"

h_finalize "$RUN_LABEL" "$ARTIFACT_DIR"
