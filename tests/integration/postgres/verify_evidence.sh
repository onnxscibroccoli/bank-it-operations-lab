#!/usr/bin/env bash
# Verify an evidence run directory: hashes match, COMMANDS.tsv well-formed, all expectations met.
# Usage: verify_evidence.sh <evidence/postgres/runs/RUN_LABEL>
set -euo pipefail
dir="${1:?evidence run dir required}"
cd "$dir"
sha256sum --quiet -c SHA256SUMS
if [ -d artifacts ]; then (cd artifacts && sha256sum --quiet -c ../ARTIFACTS.sha256); fi
cols=$(awk -F'\t' 'NR>1 && NF!=10 {bad++} END {print bad+0}' COMMANDS.tsv)
[ "$cols" -eq 0 ] || { echo "COMMANDS.tsv has $cols malformed rows" >&2; exit 1; }
fails=$(awk -F'\t' 'NR>1 && $6!="PASS" {n++} END {print n+0}' COMMANDS.tsv)
neg=$(awk -F'\t' 'NR>1 && $3=="negative" {n++} END {print n+0}' COMMANDS.tsv)
pos=$(awk -F'\t' 'NR>1 && $3=="positive" {n++} END {print n+0}' COMMANDS.tsv)
echo "verified $dir: positive=$pos negative=$neg failed=$fails"
[ "$pos" -gt 0 ] && [ "$neg" -gt 0 ] && [ "$fails" -eq 0 ]
