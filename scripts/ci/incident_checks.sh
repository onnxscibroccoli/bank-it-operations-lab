#!/usr/bin/env bash
# Required SIMULATION incident checks (PR #22 module: scenarios/incident + evidence/incident). Fail closed.
# Usage: scripts/ci/incident_checks.sh committed | fresh | not-executed-negative
#   committed              every committed run: 6 requirements (check_incident_run.py) + selftest.sh negatives
#   fresh                  run a NEW scenario now (needs PostgreSQL server binaries; PG_BIN or auto-detect).
#                          Output goes to $INCIDENT_OUT (default: a temp dir), never over committed runs.
#                          Missing binaries => every requirement NOT_EXECUTED and this check FAILS (never PASS).
#   not-executed-negative  proves the line above: with PG_BIN=/nonexistent, 'fresh' must fail with NOT_EXECUTED
# Loopback-only lab; no cloud calls, no credentials, nothing deployed, no notifications.
set -uo pipefail
cd "$(dirname "$0")/../.."
CHECK="${1:-}"
fail() { echo "::error title=incident ${CHECK}::$1"; echo "INCIDENT CHECK FAILED (${CHECK}): $1"; exit 1; }
for p in scenarios/incident/run_incident_demo.sh scenarios/incident/selftest.sh scenarios/incident/lib/timeline.py evidence/incident/runs; do
  [ -e "$p" ] || fail "required module path missing: $p (incident module, PR #22, is not integrated in this tree)"
done
case "$CHECK" in
  committed)
    n=0
    for r in evidence/incident/runs/*/; do
      r="${r%/}"; case "$r" in *.console) continue ;; esac
      n=$((n+1))
      python3 scripts/ci/check_incident_run.py "$r" || fail "requirements not met: $r"
      bash scenarios/incident/selftest.sh "$r" || fail "selftest negatives failed: $r"
    done
    [ "$n" -gt 0 ] || fail "no committed incident runs"
    ;;
  fresh)
    base="${INCIDENT_OUT:-$(mktemp -d)}"; mkdir -p "$base"
    rid="ci-fresh-$(date -u +%Y%m%dT%H%M%SZ)"
    out="$base/$rid"
    [ ! -e "$out" ] || fail "refusing to overwrite $out"
    RUN_ID="$rid" OUT="$out" bash scenarios/incident/run_incident_demo.sh > "$base/$rid.console.log" 2>&1
    rc=$?
    tail -25 "$base/$rid.console.log"
    python3 scripts/ci/check_incident_run.py "$out" --no-label --json-out "$base/$rid.requirements.json" \
      ${GITHUB_STEP_SUMMARY:+--summary "$GITHUB_STEP_SUMMARY"}
    crc=$?
    [ "$rc" -eq 3 ] && fail "fresh run NOT_EXECUTED (runner exit 3): PostgreSQL binaries or component commits unavailable; acceptance blocked"
    [ "$rc" -eq 0 ] || fail "fresh run failed (runner exit $rc)"
    [ "$crc" -eq 0 ] || fail "fresh run requirements not met"
    ;;
  not-executed-negative)
    t="$(mktemp -d)"
    PG_BIN=/nonexistent INCIDENT_OUT="$t" GITHUB_STEP_SUMMARY= bash "$0" fresh > "$t/neg.log" 2>&1
    rc=$?
    [ "$rc" -ne 0 ] || { cat "$t/neg.log"; fail "missing PostgreSQL binaries did NOT fail the fresh check"; }
    grep -q "INCIDENT REQUIREMENTS NOT_EXECUTED" "$t/neg.log" || { cat "$t/neg.log"; fail "missing binaries not reported as NOT_EXECUTED"; }
    ! grep -Eq "INCIDENT REQUIREMENTS PASS|^[a-z]+ +PASS " "$t/neg.log" || { cat "$t/neg.log"; fail "a requirement reported PASS without execution"; }
    j="$(ls "$t"/*.requirements.json)"
    python3 -c "import json,sys; d=json.load(open(sys.argv[1])); s={v['status'] for v in d['requirements'].values()}; sys.exit(0 if s=={'NOT_EXECUTED'} and d['verdict']=='NOT_EXECUTED' else 1)" "$j" \
      || fail "requirements.json does not mark every requirement NOT_EXECUTED"
    echo "negative OK: missing PostgreSQL binaries => NOT_EXECUTED for all 6 requirements, check failed (exit $rc)"
    rm -rf "$t"
    ;;
  *) echo "usage: $0 committed|fresh|not-executed-negative"; exit 2 ;;
esac
echo "INCIDENT CHECK OK (${CHECK})"
