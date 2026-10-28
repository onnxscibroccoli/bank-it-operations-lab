#!/usr/bin/env bash
# Offline third-party lint of exported SCPs with parliament (pip install parliament==1.6.4 'setuptools<81').
# Usage: scripts/parliament.sh [raw|gated]
#   raw   = print every finding; exit 1 if any.
#   gated = fail only on findings not in parliament-allowlist.json (parliament 1.6.4's own
#           ignore_locations config is broken for YAML input, so the allowlist is applied here).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PARLIAMENT="${PARLIAMENT:-parliament}"
cd "$HERE/../../evidence/orgs/policies"
# parliament treats a non-tty stdin as policy input; run it under script(1) to give it a tty.
out="$(script -qec "$PARLIAMENT --directory . --json" /dev/null | tr -d '\r' || true)"
if [ "${1:-gated}" = raw ]; then
  printf '%s\n' "$out"; [ -z "$out" ]; exit $?
fi
printf '%s\n' "$out" | python3 -c '
import json, os, sys
allow = json.load(open(sys.argv[1]))["allow"]
bad = 0
for line in filter(None, (l.strip() for l in sys.stdin)):
    f = json.loads(line); fp = os.path.basename(f["location"].get("filepath", ""))
    ok = any(a["issue"] == f["issue"] and a["file"] == fp and a["detail"] == f.get("detail") for a in allow)
    print(("ALLOWLISTED " if ok else "FAIL ") + f["issue"] + " " + fp + ": " + f.get("detail", ""))
    bad += 0 if ok else 1
print(f"unallowlisted_findings={bad}"); sys.exit(1 if bad else 0)
' "$HERE/parliament-allowlist.json"
