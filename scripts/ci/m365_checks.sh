#!/usr/bin/env bash
# Required M365 scenario checks (PR #20 module: identity/m365 + evidence/m365). Fail closed:
# if the module is not present in this tree, every check FAILS (a clean merge without these checks is not acceptance).
# Usage: scripts/ci/m365_checks.sh evaluate|unit|evidence|plan-only-negatives
# Offline only: no Microsoft 365 / Entra / Graph calls, no credentials, nothing executed against any tenant.
set -euo pipefail
cd "$(dirname "$0")/../.."
CHECK="${1:-}"
fail() { echo "::error title=m365 ${CHECK}::$1"; echo "M365 CHECK FAILED (${CHECK}): $1"; exit 1; }
require_module() {
  local p
  for p in identity/m365/m365_ops.py identity/m365/scenarios identity/m365/tests evidence/m365/generate_evidence.py; do
    [ -e "$p" ] || fail "required module path missing: $p (M365 module, PR #20, is not integrated in this tree)"
  done
}
case "$CHECK" in
  evaluate)
    require_module
    out="$(mktemp -d)"
    python3 identity/m365/m365_ops.py --json-out "$out/report.json" --md-out "$out/report.md" --quiet \
      || fail "scenario evaluation did not match expectations (exit $?)"
    python3 scripts/ci/check_plan_only.py report "$out/report.json" --min-plan-steps 1 || fail "PLAN_ONLY assertion failed on the fresh engine report"
    python3 - "$out/report.json" <<'PY' || fail "scenario coverage check failed"
import json, sys
from pathlib import Path
rep = json.load(open(sys.argv[1]))
files = sorted(Path("identity/m365/scenarios").glob("*.json"))
n = len(rep.get("scenarios") or [])
if not files or n != len(files):
    sys.exit(f"report has {n} scenarios, scenarios/ has {len(files)}")
print(f"scenario coverage OK: {n}/{len(files)}")
PY
    ;;
  unit)
    require_module
    python3 -m unittest discover -s identity/m365/tests || fail "unit tests failed"
    ;;
  evidence)
    require_module
    shopt -s nullglob
    runs=(evidence/m365/runs/*/)
    [ "${#runs[@]}" -gt 0 ] || fail "no evidence runs under evidence/m365/runs"
    for r in "${runs[@]}"; do
      python3 evidence/m365/generate_evidence.py --verify "${r%/}" || fail "evidence verify failed: $r"
      python3 scripts/ci/check_plan_only.py run "${r%/}" || fail "PLAN_ONLY assertion failed: $r"
    done
    ;;
  plan-only-negatives)
    python3 -m unittest discover -s scripts/ci/tests -p 'test_*.py' || fail "PLAN_ONLY / required-check negative tests failed"
    ;;
  *) echo "usage: $0 evaluate|unit|evidence|plan-only-negatives"; exit 2 ;;
esac
echo "M365 CHECK OK (${CHECK})"
