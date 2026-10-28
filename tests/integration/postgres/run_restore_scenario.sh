#!/usr/bin/env bash
# Postgres backup/restore exercise with positive and negative tests.
#
# Usage: run_restore_scenario.sh [service|offline]
#   service : use an existing server from PGHOST/PGPORT/PGUSER/PGPASSWORD (e.g. a CI service container)
#   offline : start a throwaway local cluster (initdb) listening ONLY on a unix socket; no network, no cloud
#
# Every command's exit code is captured in $EVIDENCE_DIR/COMMANDS.tsv and its output in logs/.
# Negative tests are expected to FAIL (non-zero exit); a negative test "passes" when the failure is observed.
# Failures are never hidden: the script records everything, then exits 1 if any expectation was not met.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
MODE="${1:-${PG_SCENARIO_MODE:-offline}}"
RUN_LABEL="${RUN_LABEL:-local-${MODE}-$(date -u +%Y%m%dT%H%M%SZ)}"
EVIDENCE_DIR="${EVIDENCE_DIR:-$REPO_ROOT/evidence/postgres/runs/$RUN_LABEL}"
ARTIFACT_DIR="${ARTIFACT_DIR:-$EVIDENCE_DIR/artifacts}"
LOG_DIR="$EVIDENCE_DIR/logs"
FP_DIR="$EVIDENCE_DIR/fingerprints"
TSV="$EVIDENCE_DIR/COMMANDS.tsv"

mkdir -p "$LOG_DIR" "$FP_DIR" "$ARTIFACT_DIR"
printf 'seq\tstep_id\tkind\texpected\texit_code\tresult\tstarted_utc\tduration_ms\tlog\tcommand\n' > "$TSV"

SEQ=0; PASS=0; FAIL=0
now_ms() { date +%s%3N; }

# run_step <step_id> <kind: setup|positive|negative> <expect: zero|nonzero> <command...>
run_step() {
  local id="$1" kind="$2" expect="$3"; shift 3
  SEQ=$((SEQ + 1))
  local log="logs/$(printf '%02d' "$SEQ")_${id}.log"
  local cmd; cmd="$(printf '%q ' "$@")"
  local started; started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local t0; t0="$(now_ms)"
  { echo "# step=$id kind=$kind expect=$expect started=$started"; echo "# cmd: $cmd"; } > "$EVIDENCE_DIR/$log"
  "$@" >> "$EVIDENCE_DIR/$log" 2>&1
  local rc=$?
  local dur=$(( $(now_ms) - t0 ))
  echo "# exit_code=$rc duration_ms=$dur" >> "$EVIDENCE_DIR/$log"
  local result
  if { [ "$expect" = zero ] && [ "$rc" -eq 0 ]; } || { [ "$expect" = nonzero ] && [ "$rc" -ne 0 ]; }; then
    result=PASS; PASS=$((PASS + 1))
  else
    result=FAIL; FAIL=$((FAIL + 1))
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$SEQ" "$id" "$kind" "$expect" "$rc" "$result" "$started" "$dur" "$log" "${cmd% }" >> "$TSV"
  printf '[%s] %-28s %-8s expect=%-7s exit=%-3s %s\n' "$result" "$id" "$kind" "$expect" "$rc" "$log"
  return 0
}

# ---------- locate binaries ----------
if [ -z "${PG_BIN:-}" ]; then
  if command -v pg_config >/dev/null 2>&1 && [ -x "$(pg_config --bindir)/initdb" ]; then
    PG_BIN="$(pg_config --bindir)"
  else
    PG_BIN="$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)"
    [ -n "$PG_BIN" ] || PG_BIN="$(dirname "$(command -v pg_dump)")"
  fi
fi
export PATH="$PG_BIN:$PATH"

# ---------- server setup ----------
OFFLINE_DIR=""
cleanup() {
  if [ -n "$OFFLINE_DIR" ] && [ -d "$OFFLINE_DIR" ]; then
    pg_ctl -D "$OFFLINE_DIR/data" -m fast stop >/dev/null 2>&1 || true
    rm -rf "$OFFLINE_DIR"
  fi
}
trap cleanup EXIT

if [ "$MODE" = offline ]; then
  OFFLINE_DIR="$(mktemp -d)"
  mkdir -p "$OFFLINE_DIR/sock"
  export PGHOST="$OFFLINE_DIR/sock" PGPORT=54329 PGUSER=postgres
  unset PGPASSWORD
  run_step offline_initdb setup zero initdb -D "$OFFLINE_DIR/data" -U postgres --auth=trust -E UTF8 --locale=C
  run_step offline_start setup zero pg_ctl -D "$OFFLINE_DIR/data" -w -l "$OFFLINE_DIR/server.log" \
    -o "-c listen_addresses='' -k $OFFLINE_DIR/sock -p 54329" start
elif [ "$MODE" != service ]; then
  echo "unknown mode: $MODE" >&2; exit 2
fi

PSQL=(psql -X -v ON_ERROR_STOP=1 -q)

{
  echo "run_label=$RUN_LABEL"
  echo "mode=$MODE"
  echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uname=$(uname -srm)"
  echo "pg_bin=$PG_BIN"
  echo "pg_dump=$(pg_dump --version)"
  echo "pg_restore=$(pg_restore --version)"
  echo "psql=$(psql --version)"
  echo "git_sha=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "github_run_id=${GITHUB_RUN_ID:-}"
  echo "github_run_attempt=${GITHUB_RUN_ATTEMPT:-}"
  echo "pghost_kind=$([ "$MODE" = offline ] && echo unix-socket-only || echo "${PGHOST:-default}")"
} > "$EVIDENCE_DIR/ENVIRONMENT.txt"

run_step server_ready setup zero pg_isready -t 30
run_step server_version setup zero "${PSQL[@]}" -d postgres -Atc "select version()"

DUMP="$ARTIFACT_DIR/lab_source.dump"
PLAIN="$ARTIFACT_DIR/lab_source.sql"

for db in lab_source lab_restore_ok lab_restore_plain lab_restore_trunc lab_restore_dup lab_restore_tamper; do
  run_step "reset_$db" setup zero dropdb --if-exists "$db"
done
run_step create_source setup zero createdb lab_source
run_step seed_source setup zero "${PSQL[@]}" -d lab_source -f "$HERE/seed.sql"
run_step fingerprint_source setup zero bash -c "\"\$@\" -d lab_source -At -f '$HERE/fingerprint.sql' > '$FP_DIR/source.txt'" _ "${PSQL[@]}"

# ---------- positive tests ----------
run_step P01_pg_dump_custom positive zero pg_dump -Fc --no-owner -d lab_source -f "$DUMP"
run_step P02_pg_restore_list positive zero bash -c "pg_restore --list '$DUMP' > '$ARTIFACT_DIR/lab_source.toc'"
run_step P03_createdb_target positive zero createdb lab_restore_ok
run_step P04_pg_restore positive zero pg_restore --exit-on-error --no-owner -d lab_restore_ok "$DUMP"
run_step P05_fingerprint_restored positive zero bash -c "\"\$@\" -d lab_restore_ok -At -f '$HERE/fingerprint.sql' > '$FP_DIR/restore_ok.txt'" _ "${PSQL[@]}"
run_step P06_compare_restored positive zero diff -u "$FP_DIR/source.txt" "$FP_DIR/restore_ok.txt"
run_step P07_pg_dump_plain positive zero pg_dump -Fp --no-owner -d lab_source -f "$PLAIN"
run_step P08_createdb_plain positive zero createdb lab_restore_plain
run_step P09_psql_restore_plain positive zero "${PSQL[@]}" -d lab_restore_plain -f "$PLAIN"
run_step P10_fingerprint_plain positive zero bash -c "\"\$@\" -d lab_restore_plain -At -f '$HERE/fingerprint.sql' > '$FP_DIR/restore_plain.txt'" _ "${PSQL[@]}"
run_step P11_compare_plain positive zero diff -u "$FP_DIR/source.txt" "$FP_DIR/restore_plain.txt"

# ---------- negative tests (must fail) ----------
SIZE=$(stat -c %s "$DUMP" 2>/dev/null || echo 0)
head -c $((SIZE / 2)) "$DUMP" > "$ARTIFACT_DIR/truncated.dump" 2>/dev/null || true
printf 'this is not a postgres archive\n' > "$ARTIFACT_DIR/garbage.dump"
run_step N01_restore_truncated_dump negative nonzero bash -c "createdb lab_restore_trunc && pg_restore --exit-on-error --no-owner -d lab_restore_trunc '$ARTIFACT_DIR/truncated.dump'"
run_step N02_list_garbage_archive negative nonzero pg_restore --list "$ARTIFACT_DIR/garbage.dump"
run_step N03_restore_missing_database negative nonzero pg_restore --exit-on-error --no-owner -d lab_db_does_not_exist "$DUMP"
run_step N04_fk_enforced_after_restore negative nonzero "${PSQL[@]}" -d lab_restore_ok -c \
  "insert into lab.ledger_entries(entry_id, account_id, amount_cents, memo, posted_on) values (999999, 424242, 1, 'orphan', current_date)"
run_step N05_restore_over_existing_objects negative nonzero bash -c "createdb lab_restore_dup && pg_restore --exit-on-error --no-owner -d lab_restore_dup '$DUMP' && pg_restore --exit-on-error --no-owner -d lab_restore_dup '$DUMP'"
run_step N06_tamper_detected negative nonzero bash -c "createdb lab_restore_tamper && pg_restore --exit-on-error --no-owner -d lab_restore_tamper '$DUMP' && \"\$@\" -d lab_restore_tamper -c \"update lab.ledger_entries set amount_cents = amount_cents + 1 where entry_id = 500\" && \"\$@\" -d lab_restore_tamper -At -f '$HERE/fingerprint.sql' > '$FP_DIR/restore_tampered.txt' && diff -u '$FP_DIR/source.txt' '$FP_DIR/restore_tampered.txt'" _ "${PSQL[@]}"

# ---------- summary + hashes ----------
(cd "$ARTIFACT_DIR" && sha256sum -- * > "$EVIDENCE_DIR/ARTIFACTS.sha256")
OVERALL=$([ "$FAIL" -eq 0 ] && echo PASS || echo FAIL)
cat > "$EVIDENCE_DIR/SUMMARY.json" <<JSON
{
  "run_label": "$RUN_LABEL",
  "mode": "$MODE",
  "overall": "$OVERALL",
  "steps": $SEQ,
  "passed": $PASS,
  "failed": $FAIL,
  "finished_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commands_tsv": "COMMANDS.tsv",
  "hashes": "SHA256SUMS",
  "artifact_hashes": "ARTIFACTS.sha256"
}
JSON
{
  echo "# Postgres restore exercise: $RUN_LABEL"
  echo
  echo "Mode: \`$MODE\`. Overall: **$OVERALL** ($PASS passed, $FAIL failed, $SEQ steps)."
  echo
  echo "| # | step | kind | expected | exit | result |"
  echo "|---|------|------|----------|------|--------|"
  tail -n +2 "$TSV" | awk -F'\t' '{printf "| %s | %s | %s | %s | %s | %s |\n", $1, $2, $3, $4, $5, $6}'
} > "$EVIDENCE_DIR/SUMMARY.md"
(cd "$EVIDENCE_DIR" && find . -type f ! -name SHA256SUMS ! -path './artifacts/*' -printf '%P\n' | LC_ALL=C sort | xargs -d '\n' sha256sum > SHA256SUMS)

echo "evidence: $EVIDENCE_DIR  overall=$OVERALL passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]
