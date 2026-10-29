#!/usr/bin/env bash
# SIMULATION — integrated incident demonstration (bank-it-operations-lab).
#
# Reuses, unmodified, the lab's existing components at pinned commits:
#   * vendor mock  integrations/vendor-mock (branch vendor-mock)        -> "app / vendor API" tier
#   * probes       observability/healthcheck (branch observability)     -> monitoring
#   * PostgreSQL   tests/integration/postgres seed.sql + fingerprint.sql (branch ci-evidence-postgres)
# They are extracted with `git archive` into a throwaway work dir; nothing outside
# scenarios/incident/ and evidence/incident/ is written in the repo.
#
# Fault: the core-ledger PostgreSQL instance is killed with `pg_ctl stop -m immediate`
# (crash-equivalent: no checkpoint, crash recovery on restart). Fully reproducible.
#
# Exit: 0 run PASS, 1 run FAIL, 3 NOT EXECUTED (prerequisite missing; recorded, nothing faked).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
RUN_ID="${RUN_ID:-local-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${OUT:-$REPO/evidence/incident/runs/$RUN_ID}"
VENDOR_REF="${VENDOR_REF:-88a37856da05468ecce86b4c5d1e1ac0b8530bc5}"   # origin/vendor-mock
OBS_REF="${OBS_REF:-3e40e39d73da3f0d20bced68651a54ee6c63846c}"         # origin/observability
PG_REF="${PG_REF:-e7399fbb538504f723d1fb83e32ce50604807b8e}"           # origin/ci-evidence-postgres
VENDOR_PORT="${VENDOR_PORT:-18099}"
PG_PORT="${PG_PORT:-55432}"
POLL_INTERVAL_S="${POLL_INTERVAL_S:-5}"
INJECT_OFFSET_S="${INJECT_OFFSET_S:-1.5}"   # injection delay after a HEALTHY poll completes
WAIT_LIMIT_S="${WAIT_LIMIT_S:-90}"
PY="${PYTHON:-python3}"

mkdir -p "$OUT/logs" "$OUT/polls"
WORK="$(mktemp -d /tmp/incident-sim.XXXXXX)"
SRC="$WORK/src"; PGDATA="$WORK/pgdata"; PGLOG="$WORK/postgres-server.log"
CONN="host=127.0.0.1 port=$PG_PORT dbname=postgres user=labadmin connect_timeout=2"
utc() { date -u +%Y-%m-%dT%H:%M:%S.%6NZ; }
js()  { "$PY" -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }
ev()  { printf '{"simulation":"SIMULATION","ts":"%s","event":"%s","detail":%s}\n' "$(utc)" "$1" "$2" >> "$OUT/events.jsonl"
        echo "[SIMULATION $(date '+%H:%M:%S %Z')] $1"; }

# ---- step runner: every command is logged with its exit code and an expectation ----------------
SEQ=0
printf 'seq\tstep_id\texpected\texit_code\tresult\tstarted_utc\tduration_ms\tlog\tcommand\n' > "$OUT/COMMANDS.tsv"
step() {  # step <id> <zero|nonzero> <regex|-> cmd...
  local id="$1" exp="$2" re="$3"; shift 3
  SEQ=$((SEQ + 1))
  local log; log="logs/$(printf '%02d' "$SEQ")_${id}.log"
  local t0 s rc=0 res; t0=$(date +%s%3N); s=$(utc)
  "$@" > "$OUT/$log" 2>&1 || rc=$?
  res=FAIL
  if { [ "$exp" = zero ] && [ $rc -eq 0 ]; } || { [ "$exp" = nonzero ] && [ $rc -ne 0 ]; }; then
    if [ "$re" = - ] || grep -Eq -- "$re" "$OUT/$log"; then res=PASS; fi
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$SEQ" "$id" "$exp${re:+ /$re/}" "$rc" "$res" "$s" \
    "$(( $(date +%s%3N) - t0 ))" "$log" "$(printf '%q ' "$@" | sed "s#$WORK#\$WORK#g")" >> "$OUT/COMMANDS.tsv"
  printf '  [%s] %-34s exit=%s\n' "$res" "$id" "$rc"
  [ "$res" = PASS ]
}

cleanup() {
  touch "$WORK/monitor.stop" 2>/dev/null || true
  [ -n "${MON_PID:-}" ] && wait "$MON_PID" 2>/dev/null || true
  [ -n "${VENDOR_PID:-}" ] && kill "$VENDOR_PID" 2>/dev/null || true
  [ -x "${PG_BIN:-/nonexistent}/pg_ctl" ] && [ -f "$PGDATA/postmaster.pid" ] && "$PG_BIN/pg_ctl" -D "$PGDATA" -m fast stop >/dev/null 2>&1 || true
  [ -f "$PGLOG" ] && sed "s#$WORK#\$WORK#g" "$PGLOG" > "$OUT/logs/postgres-server.log" || true
  [ "${KEEP_WORK:-0}" = 1 ] || rm -rf "$WORK"
}
finalize() {  # always: tear down, then build + verify the timeline from whatever was recorded
  local rc=$?
  cleanup
  [ -f "$OUT/SUMMARY.json" ] && return $rc   # NOT_EXECUTED path already wrote its summary
  [ -f "$OUT/events.jsonl" ] || return $rc
  local trc=0; "$PY" "$HERE/lib/timeline.py" "$OUT" > "$OUT/logs/timeline-build.log" || trc=$?
  (cd "$OUT" && find . -type f ! -name SHA256SUMS | sed 's#^\./##' | LC_ALL=C sort | xargs sha256sum > SHA256SUMS)
  "$PY" "$HERE/lib/timeline.py" --verify "$OUT" || trc=1
  cat "$OUT/logs/timeline-build.log"
  echo "== SIMULATION run $RUN_ID -> $OUT (script rc=$rc, timeline rc=$trc)"
  [ $rc -ne 0 ] && exit $rc; exit $trc
}
trap finalize EXIT

not_executed() {
  ev not_executed "$(js "$1")"
  printf '# SIMULATION — run NOT EXECUTED\n\nReason: %s\n\nNo timeline or metrics were produced; nothing was fabricated.\n' "$1" > "$OUT/NOT_EXECUTED.md"
  printf '{"simulation":"SIMULATION","status":"NOT_EXECUTED","reason":%s}\n' "$(js "$1")" > "$OUT/SUMMARY.json"
  echo "SIMULATION run NOT EXECUTED: $1" >&2; exit 3
}

# ---- 0. prerequisites ----------------------------------------------------------------------------
if [ -z "${PG_BIN:-}" ]; then
  if command -v pg_config >/dev/null && [ -x "$(pg_config --bindir)/initdb" ]; then PG_BIN="$(pg_config --bindir)"
  else PG_BIN="$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)"; fi
fi
[ -n "$PG_BIN" ] && [ -x "$PG_BIN/initdb" ] && [ -x "$PG_BIN/pg_ctl" ] || not_executed "PostgreSQL server binaries (initdb/pg_ctl) not found; set PG_BIN"
[ -d "$PG_BIN/../lib" ] && export LD_LIBRARY_PATH="$PG_BIN/../lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PG_BIN
for r in "$VENDOR_REF" "$OBS_REF" "$PG_REF"; do
  git -C "$REPO" cat-file -e "$r^{commit}" 2>/dev/null || not_executed "component commit $r not available locally (git fetch origin vendor-mock observability ci-evidence-postgres)"
done
{ echo "SIMULATION run environment"; echo "run_id=$RUN_ID"; echo "os=$(uname -sr)"; echo "python=$("$PY" --version 2>&1)"
  echo "postgres=$("$PG_BIN/postgres" --version)"; echo "vendor_ref=$VENDOR_REF"; echo "observability_ref=$OBS_REF"; echo "postgres_ref=$PG_REF"
  echo "scenario_commit=$(git -C "$REPO" rev-parse HEAD)"; echo "vendor_port=$VENDOR_PORT pg_port=$PG_PORT poll_interval_s=$POLL_INTERVAL_S inject_offset_s=$INJECT_OFFSET_S"
} > "$OUT/ENVIRONMENT.txt"

echo "== SIMULATION incident demo: $RUN_ID"
# ---- 1. bring up the lab stack (reused components, unmodified) -----------------------------------
mkdir -p "$SRC"
step materialize_components zero - bash -c "git -C '$REPO' archive $VENDOR_REF integrations/vendor-mock | tar -x -C '$SRC' &&
  git -C '$REPO' archive $OBS_REF observability | tar -x -C '$SRC' &&
  git -C '$REPO' archive $PG_REF tests/integration/postgres | tar -x -C '$SRC' && find '$SRC' -maxdepth 3 -type d | sed 's#$WORK#\$WORK#'"
step pg_initdb zero - "$PG_BIN/initdb" -D "$PGDATA" -U labadmin -A trust -E UTF8 --no-locale
printf "port = %s\nlisten_addresses = '127.0.0.1'\nunix_socket_directories = '%s'\nlog_line_prefix = '%%m [%%p] '\n" "$PG_PORT" "$WORK" >> "$PGDATA/postgresql.conf"
step pg_start zero - "$PG_BIN/pg_ctl" -D "$PGDATA" -l "$PGLOG" -w -t 30 start
step pg_seed zero - "$PY" "$HERE/lib/pgclient.py" query "$CONN" -f "$SRC/tests/integration/postgres/seed.sql"
step pg_fingerprint_baseline zero 'lab.ledger_entries\|1000\|' "$PY" "$HERE/lib/pgclient.py" query "$CONN" -f "$SRC/tests/integration/postgres/fingerprint.sql"
cp "$OUT/logs/$(printf '%02d' $SEQ)_pg_fingerprint_baseline.log" "$WORK/fp.before"
(cd "$SRC/integrations/vendor-mock" && exec "$PY" -u -m vendor_mock.server --scenario normal --port "$VENDOR_PORT") > "$OUT/logs/vendor-mock-server.log" 2>&1 &
VENDOR_PID=$!
step vendor_health zero '"SIMULATION"' bash -c "for i in \$(seq 50); do curl -fsS --max-time 2 http://127.0.0.1:$VENDOR_PORT/v1/health && exit 0; sleep 0.2; done; exit 1"

cat > "$OUT/probe-config.json" <<JSON
{
  "disk_path": "/",
  "expected_probes": ["vendor-api-http", "core-ledger-db-tcp", "resolver-dns"],
  "policy": {"max_age_s": 300},
  "probes": [
    {"name": "vendor-api-http", "kind": "http", "url": "http://127.0.0.1:$VENDOR_PORT/v1/health",
     "expect_status": [200], "expect_substring": "SIMULATION", "timeout_s": 2, "max_bytes": 4096},
    {"name": "core-ledger-db-tcp", "kind": "tcp", "host": "127.0.0.1", "port": $PG_PORT, "timeout_s": 2},
    {"name": "resolver-dns", "kind": "dns", "hostname": "localhost", "timeout_s": 2}
  ]
}
JSON

# ---- 2. continuous monitor (observability collect every POLL_INTERVAL_S) -------------------------
printf 'seq\tstarted_utc\tfinished_utc\texit_code\toverall\tfailed_checks\n' > "$OUT/monitor.tsv"
monitor() {
  local n=0 s e rc row
  while [ ! -f "$WORK/monitor.stop" ]; do
    n=$((n + 1)); local p; p="$OUT/polls/$(printf '%03d' $n)"; s=$(utc); rc=0
    (cd "$SRC/observability" && "$PY" -m healthcheck collect --config "$OUT/probe-config.json" \
       --payload-out "$p.payload.json" --out "$p.result.json" --log-file "$p.log.jsonl") >/dev/null 2>&1 || rc=$?
    e=$(utc)
    row=$("$PY" -c 'import json,sys; r=json.load(open(sys.argv[1])); print(r["overall"]+"\t"+",".join(c["check"] for c in r["checks"] if c["status"]!="PASS"))' "$p.result.json" 2>/dev/null || printf 'ERROR\tresult-unreadable')
    printf '%s\t%s\t%s\t%s\t%s\n' "$n" "$s" "$e" "$rc" "$row" >> "$OUT/monitor.tsv"
    sleep "$POLL_INTERVAL_S"
  done
}
monitor & MON_PID=$!

wait_poll() {  # wait_poll <HEALTHY|UNHEALTHY> <not-before-utc> -> prints matching monitor.tsv row
  local want="$1" since="$2" deadline=$(( $(date +%s) + WAIT_LIMIT_S ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    local row; row=$(awk -F'\t' -v w="$want" -v s="$since" 'NR>1 && $2>=s && (w=="HEALTHY" ? $5=="HEALTHY" : $5!="HEALTHY") {print; exit}' "$OUT/monitor.tsv")
    [ -n "$row" ] && { echo "$row"; return 0; }
    sleep 0.2
  done
  return 1
}
pollj() { awk -F'\t' '{printf "{\"poll_seq\":%s,\"poll_finished_utc\":\"%s\",\"exit_code\":%s,\"overall\":\"%s\",\"failed_checks\":\"%s\"}", $1,$3,$4,$5,$6}' <<<"$1"; }

ROW=$(wait_poll HEALTHY "$(utc)") || { ev aborted '"baseline never HEALTHY"'; exit 1; }
ev baseline_healthy "$(pollj "$ROW")"

# ---- 3. inject ------------------------------------------------------------------------------------
sleep "$INJECT_OFFSET_S"
INJ=$(utc)
ev failure_injected '{"fault":"core-ledger PostgreSQL killed: pg_ctl stop -m immediate","component":"postgres:'"$PG_PORT"'"}'
step inject_pg_immediate_stop zero - "$PG_BIN/pg_ctl" -D "$PGDATA" -m immediate stop

# ---- 4. detect (first UNHEALTHY poll that started after injection) --------------------------------
ROW=$(wait_poll UNHEALTHY "$INJ") || { ev aborted '"fault not detected within WAIT_LIMIT_S"'; exit 1; }
ev detected "$(pollj "$ROW")"
ev escalation_simulated '{"severity":"SEV1 (core ledger unavailable)","notified":"DB on-call, incident commander, service desk lead","channel":"SIMULATED - no message sent"}'

# ---- 5. diagnose (automated triage; each finding is a logged command) -----------------------------
DPOLL="$OUT/polls/$(printf '%03d' "$(cut -f1 <<<"$ROW")").result.json"
step diag_failed_checks zero 'probe:core-ledger-db-tcp' "$PY" -c 'import json,sys; r=json.load(open(sys.argv[1])); [print(c["check"],c["status"],c["detail"]) for c in r["checks"] if c["status"]!="PASS"]; print("endpoint_decision", r["endpoint_decision"])' "$DPOLL"
step diag_vendor_tier_ok zero '"status": "OK"' curl -fsS --max-time 2 "http://127.0.0.1:$VENDOR_PORT/v1/health"
step diag_db_ping nonzero 'PQPING_NO_RESPONSE' "$PY" "$HERE/lib/pgclient.py" ping "$CONN"
step diag_pg_ctl_status nonzero 'no server running' "$PG_BIN/pg_ctl" -D "$PGDATA" status
step diag_server_log zero 'immediate shutdown request' bash -c "tail -n 15 '$PGLOG' | sed 's#$WORK#\$WORK#g'"
step diag_business_txn_impact nonzero 'connection failed' "$PY" "$HERE/lib/pgclient.py" query "$CONN" -c "SELECT balance_cents FROM lab.account_balances WHERE account_id = 1"
ev diagnosed '{"root_cause":"core-ledger PostgreSQL postmaster not running (immediate shutdown); vendor API tier and DNS healthy","evidence":"diag_* steps in COMMANDS.tsv"}'

# ---- 6. restore -----------------------------------------------------------------------------------
ev restore_started '"runbook: start PostgreSQL, let crash recovery complete, verify data, confirm via monitor"'
step restore_pg_start zero - "$PG_BIN/pg_ctl" -D "$PGDATA" -l "$PGLOG" -w -t 60 start
ev db_restarted '"pg_ctl start returned 0"'
step verify_crash_recovery_logged zero 'not properly shut down|automatic recovery' bash -c "tail -n 20 '$PGLOG' | sed 's#$WORK#\$WORK#g'"
step verify_db_ping zero 'PQPING_OK' "$PY" "$HERE/lib/pgclient.py" ping "$CONN"
step verify_fingerprint_after zero 'lab.ledger_entries\|1000\|' "$PY" "$HERE/lib/pgclient.py" query "$CONN" -f "$SRC/tests/integration/postgres/fingerprint.sql"
cp "$OUT/logs/$(printf '%02d' $SEQ)_verify_fingerprint_after.log" "$WORK/fp.after"
step verify_fingerprint_matches_baseline zero - diff -u "$WORK/fp.before" "$WORK/fp.after"
ev data_integrity_verified '"lab.accounts, lab.ledger_entries, lab.account_balances row counts and md5 identical to baseline"'
step verify_business_txn zero '^[-0-9]+$' "$PY" "$HERE/lib/pgclient.py" query "$CONN" -c "SELECT balance_cents FROM lab.account_balances WHERE account_id = 1"
ROW=$(wait_poll HEALTHY "$(utc)") || { ev aborted '"monitor never returned HEALTHY"'; exit 1; }
ev service_restored "$(pollj "$ROW")"

# ---- 7. close out ---------------------------------------------------------------------------------
touch "$WORK/monitor.stop"; wait "$MON_PID" 2>/dev/null || true; MON_PID=
ev monitoring_stopped '"scenario complete; stack torn down"'
exit 0   # finalize (EXIT trap) builds TIMELINE.md / SUMMARY.json / SHA256SUMS and verifies them
