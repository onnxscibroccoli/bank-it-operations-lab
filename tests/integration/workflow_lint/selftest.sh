#!/usr/bin/env bash
# Negative self-test for check_workflows.py. Exit 0 only if:
#  T1 the checker FAILS (exit 1) on fixtures/bad, and the (file, rule, count) findings equal fixtures/bad/EXPECTED.tsv
#     exactly (every bad fixture caught, for the intended rule, and nothing else);
#  T2 the checker PASSES (exit 0, 0 findings) on fixtures/good;
#  T3 a lockfile whose entry is marked verified=no makes the good fixture fail with LOCK_MISSING;
#  T4 mutating a copy of the REAL workflows (re-floating one pin to @v5, dropping persist-credentials) is caught;
#  T5 the real repository workflows pass.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
PY="${PYTHON:-python3}"
CHK=("$PY" "$HERE/check_workflows.py" --lock "$ROOT/.github/workflows/ACTIONS_LOCK.tsv" --policy "$ROOT/.github/workflows/WORKFLOW_POLICY.json")
OUT="${SELFTEST_OUT:-$(mktemp -d)}"; mkdir -p "$OUT"
NF=0
res() { local r=PASS; [ "$2" = "$3" ] || { r=FAIL; NF=$((NF+1)); }; printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$r" | tee -a "$OUT/SELFTEST.tsv"; }
printf 'test\texpected\tactual\tresult\n' > "$OUT/SELFTEST.tsv"

"${CHK[@]}" --workflows "$HERE/fixtures/bad" --tsv "$OUT/bad.tsv" > "$OUT/bad.log" 2>&1; rc=$?
res T1.exit_on_bad 1 "$rc"
awk -F'\t' 'NR>1 {c[$1"\t"$2]++} END {for (k in c) print k "\t" c[k]}' "$OUT/bad.tsv" | LC_ALL=C sort > "$OUT/bad.actual"
tail -n +2 "$HERE/fixtures/bad/EXPECTED.tsv" | LC_ALL=C sort > "$OUT/bad.expected"
if diff -u "$OUT/bad.expected" "$OUT/bad.actual" > "$OUT/bad.diff"; then d=match; else d=differ; cat "$OUT/bad.diff"; fi
res T1.findings_equal_expected match "$d"
for f in "$HERE"/fixtures/bad/*.yml; do
  b=$(basename "$f"); n=$(awk -F'\t' -v b="$b" 'NR>1 && $1==b' "$OUT/bad.tsv" | wc -l | tr -d ' ')
  res "T1.caught.$b" yes "$([ "$n" -gt 0 ] && echo yes || echo no)"
done

"${CHK[@]}" --workflows "$HERE/fixtures/good" > "$OUT/good.log" 2>&1; res T2.exit_on_good 0 "$?"

sed -E 's/^(actions\/checkout\tv5\.1\.0\t[0-9a-f]{40}\t[^\t]*\t[^\t]*\t)yes/\1no/' "$ROOT/.github/workflows/ACTIONS_LOCK.tsv" > "$OUT/lock_unverified.tsv"
"$PY" "$HERE/check_workflows.py" --workflows "$HERE/fixtures/good" --lock "$OUT/lock_unverified.tsv" --tsv "$OUT/t3.tsv" > "$OUT/t3.log" 2>&1; rc=$?
res T3.unverified_lock_fails 1 "$rc"
res T3.rule "LOCK_MISSING" "$(awk -F'\t' 'NR>1 {print $2}' "$OUT/t3.tsv" | sort -u | tr '\n' ' ' | sed 's/ $//')"

M="$OUT/mutated"; rm -rf "$M"; cp -r "$ROOT/.github/workflows" "$M"
f="$M/postgres-restore-evidence.yml"
sed -i '0,/actions\/checkout@[0-9a-f]\{40\}/s//actions\/checkout@v5/' "$f"
sed -i '0,/persist-credentials: false/{/persist-credentials: false/d}' "$M/offline-validation.yml"
"${CHK[@]}" --workflows "$M" --tsv "$OUT/t4.tsv" > "$OUT/t4.log" 2>&1; rc=$?
res T4.mutation_fails 1 "$rc"
res T4.rules "PERSIST_CREDS UNPINNED" "$(awk -F'\t' 'NR>1 {print $2}' "$OUT/t4.tsv" | sort -u | tr '\n' ' ' | sed 's/ $//')"

"${CHK[@]}" --tsv "$OUT/real.tsv" > "$OUT/real.log" 2>&1; res T5.real_workflows_pass 0 "$?"

echo "workflow-lint selftest: $(($(wc -l < "$OUT/SELFTEST.tsv") - 1)) assertions, $NF failed (evidence: $OUT)"
[ "$NF" -eq 0 ]
