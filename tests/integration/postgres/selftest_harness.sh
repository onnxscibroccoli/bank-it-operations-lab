#!/usr/bin/env bash
# Self-test for lib.sh. Needs no database. Proves the harness reports FAIL/ERROR/NOT_RUN (never PASS) for:
# unexpected success, wrong failure reason, version-mismatch errors, missing executables, setup failures,
# dependants of failed setup, pipeline failures masked by a later command, wrong positive output,
# declared-but-unexecuted cases, duplicates, undeclared cases; and that the overall run is FAIL with exit!=0.
# Part B replays the real outputs of the preserved run ci-service-40630856041-1 through the production
# expectations: N01/N04/N05/N06 (false PASS under harness v1) must NOT pass; N02/N03 must pass.
# Part C checks verify_evidence.py rejects a forged COMMANDS.tsv that claims PASS for a wrong-reason failure.
# Exit 0 only if every assertion holds.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
RUN_LABEL="${RUN_LABEL:-local-selftest-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${EVIDENCE_DIR:-$REPO_ROOT/evidence/postgres/runs/$RUN_LABEL}"
mkdir -p "$OUT"
ASSERT="$OUT/SELFTEST_ASSERTIONS.tsv"
printf 'assertion\texpected\tactual\tresult\n' > "$ASSERT"
NFAIL=0
check() {  # check <name> <expected> <actual>
  local r=PASS; [ "$2" = "$3" ] || { r=FAIL; NFAIL=$((NFAIL + 1)); }
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$r" >> "$ASSERT"
  printf '[%s] %-48s expected=%-40s actual=%s\n' "$r" "$1" "$2" "$3"
}
row() { awk -F'\t' -v id="$2" 'NR>1 && $2==id {print $6 "/" $7; exit}' "$1/COMMANDS.tsv"; }

# ---------------- Part A: synthetic cases ----------------
A="$OUT/A_synthetic"
(
  . "$HERE/lib.sh"
  h_init "$A" "$HERE/expectations.selftest.tsv" selftest
  fault()      { echo "injected fault: disk full" >&2; return 3; }
  ok()         { echo "all good"; }
  unrelated()  { echo 'ERROR:  syntax error at or near "SELEC"' >&2; return 1; }
  versionerr() { echo 'pg_restore: error: could not execute query: ERROR:  unrecognized configuration parameter "transaction_timeout"' >&2
                 echo "injected fault: disk ful" >&2; return 1; }
  masked_pipe() { false | tail -n 1; }      # rc must be 1 under pipefail, not tail's 0
  wrong_rows() { echo "rows=999"; }
  mismatch()   { echo "client_major=18 server_major=16 MISMATCH"; return 1; }
  run_case ST01_control_expected_fault fault
  run_case ST02_unexpected_success ok
  run_case ST03_wrong_reason unrelated
  run_case ST04_version_mismatch_masquerade versionerr
  run_case ST05_missing_executable definitely-not-installed-pg-tool --version
  run_case ST06_setup_failure false
  run_case --needs ST06_setup_failure ST07_dependent_on_failed_setup fault
  run_case ST08_pipeline_failure_hidden_by_tail masked_pipe
  run_case ST09_positive_wrong_output wrong_rows
  # ST10 is declared but deliberately never executed
  run_case ST11_run_twice ok
  run_case ST11_run_twice ok
  run_case ST12_version_gate mismatch
  run_case ST99_undeclared ok
  h_finalize "$RUN_LABEL-A"
)
rcA=$?
check "A.overall_exit_nonzero" 1 "$rcA"
check "A.summary_overall" '"overall": "FAIL",' "$(grep '"overall"' "$A/SUMMARY.json" | tr -s ' ' | sed 's/^ //')"
check "A.ST01_control_expected_fault" PASS/expected_fault_detected "$(row "$A" ST01_control_expected_fault)"
check "A.ST02_unexpected_success" FAIL/unexpected_success "$(row "$A" ST02_unexpected_success)"
check "A.ST03_wrong_reason" FAIL/wrong_reason "$(row "$A" ST03_wrong_reason)"
check "A.ST04_version_mismatch_masquerade" ERROR/version_mismatch "$(row "$A" ST04_version_mismatch_masquerade)"
check "A.ST05_missing_executable" ERROR/missing_executable "$(row "$A" ST05_missing_executable)"
check "A.ST06_setup_failure" ERROR/setup_failure "$(row "$A" ST06_setup_failure)"
check "A.ST07_dependent_on_failed_setup" NOT_RUN/dependency_failed:ST06_setup_failure "$(row "$A" ST07_dependent_on_failed_setup)"
check "A.ST08_pipeline_failure_hidden_by_tail" FAIL/positive_failed "$(row "$A" ST08_pipeline_failure_hidden_by_tail)"
check "A.ST09_positive_wrong_output" FAIL/output_mismatch "$(row "$A" ST09_positive_wrong_output)"
check "A.ST10_declared_but_never_run" NOT_RUN/missing_test "$(row "$A" ST10_declared_but_never_run)"
check "A.ST11_duplicate_row" FAIL/duplicate_test "$(awk -F'\t' 'NR>1 && $2=="ST11_run_twice" {r=$6 "/" $7} END {print r}' "$A/COMMANDS.tsv")"
check "A.ST12_version_gate" ERROR/version_mismatch "$(row "$A" ST12_version_gate)"
check "A.ST99_undeclared" ERROR/undeclared_test "$(row "$A" ST99_undeclared)"
check "A.passed_count_only_control" 2 "$(awk -F'\t' 'NR>1 && $6=="PASS"' "$A/COMMANDS.tsv" | wc -l | tr -d ' ')"
python3 "$HERE/verify_evidence.py" "$A" > "$OUT/A_verify.log" 2>&1; check "A.verifier_rejects" 1 "$?"

# ---------------- Part B: replay of preserved run 40630856041 through production expectations ----------------
B="$OUT/B_replay_40630856041"
HIST="$REPO_ROOT/evidence/postgres/runs/ci-service-40630856041-1/logs"
(
  . "$HERE/lib.sh"
  h_init "$B" "$HERE/expectations.tsv" service
  replay() { grep -v '^#' "$1" >&2; return "$2"; }   # re-emit the historic output with its historic exit code
  for n in 23_N01_restore_truncated_dump 24_N02_list_garbage_archive 25_N03_restore_missing_database \
           26_N04_fk_enforced_after_restore 27_N05_restore_over_existing_objects 28_N06_tamper_detected; do
    rc=$(sed -nE 's/^# exit_code=([0-9]+).*/\1/p' "$HIST/$n.log")
    run_case "${n#*_}" replay "$HIST/$n.log" "$rc"
  done
  h_finalize "$RUN_LABEL-B"
)
rcB=$?
check "B.overall_exit_nonzero" 1 "$rcB"
check "B.N01_was_false_pass" ERROR/version_mismatch "$(row "$B" N01_restore_truncated_dump)"
check "B.N02_genuine" PASS/expected_fault_detected "$(row "$B" N02_list_garbage_archive)"
check "B.N03_genuine" PASS/expected_fault_detected "$(row "$B" N03_restore_missing_database)"
check "B.N04_was_false_pass" ERROR/environment_error "$(row "$B" N04_fk_enforced_after_restore)"
check "B.N05_was_false_pass" ERROR/version_mismatch "$(row "$B" N05_restore_over_existing_objects)"
check "B.N06_was_false_pass" ERROR/version_mismatch "$(row "$B" N06_tamper_detected)"

# ---------------- Part C: verifier rejects a forged PASS ----------------
C="$OUT/C_forged"
rm -rf "$C"; cp -r "$A" "$C"
awk -F'\t' 'BEGIN{OFS="\t"} NR>1 && $2=="ST03_wrong_reason" {$6="PASS"; $7="expected_fault_detected"} {print}' "$A/COMMANDS.tsv" > "$C/COMMANDS.tsv"
(cd "$C" && find . -type f ! -name SHA256SUMS -printf '%P\n' | LC_ALL=C sort | xargs -d '\n' sha256sum > SHA256SUMS)
python3 "$HERE/verify_evidence.py" "$C" > "$OUT/C_verify.log" 2>&1; check "C.verifier_rejects_forged_pass" 1 "$?"
check "C.verifier_names_reason" yes "$(grep -q 'ST03_wrong_reason.*reason_regex not found' "$OUT/C_verify.log" && echo yes || echo no)"

TOTAL=$(awk 'NR>1' "$ASSERT" | wc -l | tr -d ' ')
cat > "$OUT/SELFTEST_SUMMARY.json" <<JSON
{
  "status": "CURRENT",
  "run_label": "$RUN_LABEL",
  "assertions": $TOTAL,
  "failed_assertions": $NFAIL,
  "overall": "$([ "$NFAIL" -eq 0 ] && echo PASS || echo FAIL)",
  "note": "PASS means the harness correctly reported FAIL/ERROR/NOT_RUN for every deliberately bad case."
}
JSON
(cd "$OUT" && find . -type f ! -name SHA256SUMS -printf '%P\n' | LC_ALL=C sort | xargs -d '\n' sha256sum > SHA256SUMS)
echo "selftest: $OUT assertions=$TOTAL failed=$NFAIL"
[ "$NFAIL" -eq 0 ]
