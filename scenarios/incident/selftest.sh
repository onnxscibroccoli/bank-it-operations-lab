#!/usr/bin/env bash
# SIMULATION — negative checks for the incident evidence tooling. Usage: selftest.sh <run_dir>
# 1. a pristine run must VERIFY PASS; 2. a run with a forged MTTD must VERIFY FAIL;
# 3. a run with a deleted `detected` event must VERIFY FAIL; 4. missing PG binaries -> NOT_EXECUTED (exit 3).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; RUN="$1"; T="$(mktemp -d)"; fails=0
check() { local name="$1" want="$2"; shift 2; "$@" >"$T/out" 2>&1; local rc=$?
  if [ "$rc" = "$want" ]; then echo "PASS $name (exit $rc)"; else echo "FAIL $name (exit $rc, wanted $want)"; cat "$T/out"; fails=$((fails+1)); fi; }
check pristine_run_verifies 0 python3 "$HERE/lib/timeline.py" --verify "$RUN"
cp -r "$RUN" "$T/forged"; sed -i 's/"mttd_s": [0-9.]*/"mttd_s": 0.5/' "$T/forged/SUMMARY.json"
check forged_mttd_rejected 1 python3 "$HERE/lib/timeline.py" --verify "$T/forged"
cp -r "$RUN" "$T/nodetect"; sed -i '/"event":"detected"/d' "$T/nodetect/events.jsonl"
check missing_detection_event_rejected 1 python3 "$HERE/lib/timeline.py" --verify "$T/nodetect"
check missing_pg_binaries_not_executed 3 env PG_BIN=/nonexistent OUT="$T/ne" "$HERE/run_incident_demo.sh"
rm -rf "$T"; echo "SIMULATION selftest: $fails failure(s)"; exit $((fails > 0))
