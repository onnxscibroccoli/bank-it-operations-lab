#!/usr/bin/env bash
# Prove the false-acceptance regression tests are real: run the SAME test file against an older gate.
#   tools/acceptance/gate/tests/prove_regressions.sh [OLD_SHA] [OUT_TSV]
# OLD_SHA defaults to eb42b23747d5b686d9540c93e445a713b4e56c5d (acceptance/vertical-slice, PR #26), whose gate lives in
# scripts/acceptance/. Prints one line per test: <test id> <old result> <new result>. Every FA-* regression must be
# FAIL/ERROR on the old gate and ok on the new one (tests named *_control / *_hardening are excluded: they guard new
# rules whose inputs the old gate rejects for an interface reason). C1-C4/I1/I2 were closed at eb42b23 (PR #29); a few
# show FAIL on old only because old A-contract export rejects the new requirement_ids review field (old exit 1 = INVALID).
# Offline: uses a local git worktree only.
set -uo pipefail
export LC_ALL=C
OLD="${1:-eb42b23747d5b686d9540c93e445a713b4e56c5d}"; OUTF="${2:-/dev/stdout}"
case "$OUTF" in /*) ;; *) OUTF="$(pwd)/$OUTF" ;; esac  # absolute: the script cds below
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
WT="$(mktemp -d)/old"; trap 'git -C "$ROOT" worktree remove --force "$WT" >/dev/null 2>&1' EXIT
git -C "$ROOT" worktree add --detach --quiet "$WT" "$OLD" || { echo "cannot check out $OLD" >&2; exit 2; }
res() { python3 -m unittest -v "$@" 2>&1 | sed -nE 's/^(test_[a-z0-9_]+) \(test_invariants\.([A-Za-z0-9]+)\.[a-z0-9_]+\) \.\.\. (ok|FAIL|ERROR)$/\2.\1\t\3/p' | sort; }
cd "$HERE"
new="$(PYTHONDONTWRITEBYTECODE=1 res test_invariants)"
old="$(ACC_GATE_SRC="$WT/scripts/acceptance" ACC_GATE_REL=scripts/acceptance PYTHONDONTWRITEBYTECODE=1 res test_invariants)"
join -t $'\t' <(echo "$old") <(echo "$new") | awk -F'\t' -v old="$OLD" 'BEGIN{print "test\told(" substr(old,1,12) ")\tnew"} {print}' > "$OUTF"
bad=$(join -t $'\t' <(echo "$old") <(echo "$new") | awk -F'\t' '$1 ~ /^FA[0-9]/ && $1 !~ /control|hardening/ && ($2=="ok" || $3!="ok")' | wc -l)
echo "regressions not proven (FA-* ok on old, or not ok on new): $bad" >&2
[ "$bad" -eq 0 ]
