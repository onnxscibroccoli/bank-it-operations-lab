set -e
total=0
for f in cdk.out/*-NagReport.csv; do
  rows=$(tail -n +2 "$f" | grep -c . || true)
  nc=$(grep -c '"Non-Compliant"' "$f" || true)
  sup=$(grep -c '"Suppressed"' "$f" || true)
  echo "$(basename "$f"): rows=$rows non_compliant=$nc suppressed=$sup"
  total=$((total+nc+sup))
done
echo "NagSuppressions in source: $(grep -rc NagSuppressions lib bin | awk -F: '{s+=$2} END {print s}')"
echo "total_non_compliant_or_suppressed=$total"; test "$total" -eq 0
