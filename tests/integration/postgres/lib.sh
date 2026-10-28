# shellcheck shell=bash
# Test harness for evidence-producing integration scenarios.
#
# Every case is declared in an expectations file (TSV):
#   id  kind(setup|positive|negative)  expect(zero|nonzero)  modes(all|offline|service|selftest)  fail_class  reason_regex
# Classification (column `class` in COMMANDS.tsv):
#   setup     rc=0 (+regex if set)           -> PASS  setup_ok
#             otherwise                      -> ERROR <fail_class|setup_failure>
#   positive  rc=0 (+regex if set)           -> PASS  positive_ok
#             rc=0, regex not matched        -> FAIL  output_mismatch
#             rc!=0                          -> FAIL  positive_failed
#   negative  rc!=0 and output ~ reason_regex-> PASS  expected_fault_detected
#             rc=0                           -> FAIL  unexpected_success
#             rc!=0, output ~ known env error-> ERROR version_mismatch | environment_error
#             rc!=0, any other reason        -> FAIL  wrong_reason
#   any       executable not found (126/127) -> ERROR missing_executable
#   any       a --needs dependency not PASS  -> NOT_RUN dependency_failed
#   declared but never executed              -> NOT_RUN missing_test
#   executed but not declared / run twice    -> ERROR undeclared_test / FAIL duplicate_test
# Overall PASS requires every declared case to have exactly one PASS row and nothing else.
# Only the command's own output is matched (never the logged command line).
set -o pipefail

H_SEQ=0
declare -gA X_KIND=() X_EXPECT=() X_FAILCLASS=() X_REGEX=() RESULT=()
declare -ga X_IDS=()
H_ENV_ERROR_RE='unrecognized configuration parameter|unsupported version|server version mismatch|aborting because of server version|could not connect to server|Connection refused|role "[^"]+" does not exist|relation "[^"]+" does not exist|No such file or directory|Permission denied'
H_VERSION_RE='unrecognized configuration parameter|unsupported version|server version mismatch|aborting because of server version'

h_init() {  # h_init <evidence_dir> <expectations.tsv> <mode>
  H_DIR="$1"; H_EXPECTATIONS_SRC="$2"; H_MODE="$3"
  H_TSV="$H_DIR/COMMANDS.tsv"
  mkdir -p "$H_DIR/logs"
  printf 'seq\tstep_id\tkind\texpected\texit_code\tresult\tclass\tstarted_utc\tduration_ms\tlog\treason_regex\tcommand\n' > "$H_TSV"
  # Copy only the expectations that apply to this mode, so the run directory is self-describing.
  printf 'id\tkind\texpect\tmodes\tfail_class\treason_regex\n' > "$H_DIR/EXPECTATIONS.tsv"
  local id kind expect modes failclass regex
  while IFS=$'\t' read -r id kind expect modes failclass regex || [ -n "$id" ]; do
    case "$id" in ''|'#'*|id) continue ;; esac
    case ",$modes," in *",all,"*|*",$H_MODE,"*) ;; *) continue ;; esac
    [ "$failclass" = "-" ] && failclass=""
    [ "$regex" = "-" ] && regex=""
    X_IDS+=("$id"); X_KIND[$id]="$kind"; X_EXPECT[$id]="$expect"; X_FAILCLASS[$id]="$failclass"; X_REGEX[$id]="$regex"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$kind" "$expect" "$modes" "${failclass:--}" "${regex:--}" >> "$H_DIR/EXPECTATIONS.tsv"
  done < "$H_EXPECTATIONS_SRC"
}

_h_row() {  # _h_row id kind expect rc result class started dur log regex cmd
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$H_SEQ" "$@" >> "$H_TSV"
  printf '[%-7s] %-40s %-8s expect=%-7s exit=%-3s %s\n' "$5" "$1" "$2" "$3" "$4" "$6"
}

# run_case [--needs id1,id2] <id> <command> [args...]
run_case() {
  local needs=""
  if [ "${1:-}" = --needs ]; then needs="$2"; shift 2; fi
  local id="$1"; shift
  H_SEQ=$((H_SEQ + 1))
  local log; log="logs/$(printf '%02d' "$H_SEQ")_${id}.log"
  local cmd; cmd="$(printf '%q ' "$@")"; cmd="${cmd% }"
  local started; started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local kind="${X_KIND[$id]:-undeclared}" expect="${X_EXPECT[$id]:--}" regex="${X_REGEX[$id]:-}"
  local regex_col="${regex:--}"

  if [ "$kind" = undeclared ]; then
    echo "# step=$id is not declared in EXPECTATIONS.tsv" > "$H_DIR/$log"
    _h_row "$id" "$kind" "-" "-" ERROR undeclared_test "$started" 0 "$log" "-" "$cmd"; return 0
  fi
  if [ -n "${RESULT[$id]+x}" ]; then
    echo "# step=$id executed more than once" > "$H_DIR/$log"
    _h_row "$id" "$kind" "$expect" "-" FAIL duplicate_test "$started" 0 "$log" "$regex_col" "$cmd"
    RESULT[$id]=FAIL; return 0
  fi
  local dep
  for dep in ${needs//,/ }; do
    if [ "${RESULT[$dep]:-}" != PASS ]; then
      echo "# step=$id NOT RUN: dependency $dep is ${RESULT[$dep]:-missing}" > "$H_DIR/$log"
      _h_row "$id" "$kind" "$expect" "-" NOT_RUN "dependency_failed:$dep" "$started" 0 "$log" "$regex_col" "$cmd"
      RESULT[$id]=NOT_RUN; return 0
    fi
  done

  local out; out="$(mktemp)"
  {
    echo "# step=$id kind=$kind expect=$expect started=$started"
    echo "# reason_regex: ${regex:-<none>}"
    echo "# cmd: $cmd"
    echo "# --- output ---"
  } > "$H_DIR/$log"
  local t0 rc; t0="$(date +%s%3N)"
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "harness: executable or function not found: $1" > "$out"; rc=127
  else
    ( set -o pipefail; "$@" ) > "$out" 2>&1; rc=$?
  fi
  local dur=$(( $(date +%s%3N) - t0 ))
  cat "$out" >> "$H_DIR/$log"
  { echo "# --- end output ---"; echo "# exit_code=$rc duration_ms=$dur"; } >> "$H_DIR/$log"

  local matched=no
  if [ -n "$regex" ] && grep -Eq -- "$regex" "$out"; then matched=yes; fi
  local result class
  if { [ "$rc" -eq 127 ] || [ "$rc" -eq 126 ]; } && grep -Eq 'not found|No such file|Permission denied' "$out"; then
    result=ERROR; class=missing_executable
  else
    case "$kind" in
      setup)
        if [ "$rc" -eq 0 ] && { [ -z "$regex" ] || [ "$matched" = yes ]; }; then result=PASS; class=setup_ok
        else result=ERROR; class="${X_FAILCLASS[$id]:-setup_failure}"; fi ;;
      positive)
        if [ "$rc" -ne 0 ]; then result=FAIL; class=positive_failed
        elif [ -n "$regex" ] && [ "$matched" = no ]; then result=FAIL; class=output_mismatch
        else result=PASS; class=positive_ok; fi ;;
      negative)
        if [ "$rc" -eq 0 ]; then result=FAIL; class=unexpected_success
        elif [ -z "$regex" ]; then result=ERROR; class=no_reason_declared
        elif [ "$matched" = yes ]; then result=PASS; class=expected_fault_detected
        elif grep -Eq -- "$H_VERSION_RE" "$out"; then result=ERROR; class=version_mismatch
        elif grep -Eq -- "$H_ENV_ERROR_RE" "$out"; then result=ERROR; class=environment_error
        else result=FAIL; class=wrong_reason; fi ;;
      *) result=ERROR; class=bad_kind ;;
    esac
  fi
  rm -f "$out"
  RESULT[$id]="$result"
  _h_row "$id" "$kind" "$expect" "$rc" "$result" "$class" "$started" "$dur" "$log" "$regex_col" "$cmd"
  return 0
}

# h_finalize <run_label> [artifact_dir]   -> writes SUMMARY.*, hashes; returns 0 only if overall PASS
h_finalize() {
  local label="$1" adir="${2:-}" id
  for id in "${X_IDS[@]}"; do
    if [ -z "${RESULT[$id]+x}" ]; then
      H_SEQ=$((H_SEQ + 1))
      _h_row "$id" "${X_KIND[$id]}" "${X_EXPECT[$id]}" "-" NOT_RUN missing_test "$(date -u +%Y-%m-%dT%H:%M:%SZ)" 0 "-" "${X_REGEX[$id]:--}" "-"
      RESULT[$id]=NOT_RUN
    fi
  done
  local expected=${#X_IDS[@]}
  local rows pass fail err notrun neg_pass
  rows=$(awk -F'\t' 'NR>1' "$H_TSV" | wc -l)
  pass=$(awk -F'\t' 'NR>1 && $6=="PASS"' "$H_TSV" | wc -l)
  fail=$(awk -F'\t' 'NR>1 && $6=="FAIL"' "$H_TSV" | wc -l)
  err=$(awk -F'\t' 'NR>1 && $6=="ERROR"' "$H_TSV" | wc -l)
  notrun=$(awk -F'\t' 'NR>1 && $6=="NOT_RUN"' "$H_TSV" | wc -l)
  neg_pass=$(awk -F'\t' 'NR>1 && $3=="negative" && $6=="PASS"' "$H_TSV" | wc -l)
  local overall=FAIL
  if [ "$pass" -eq "$expected" ] && [ "$rows" -eq "$expected" ]; then overall=PASS; fi
  if [ -n "$adir" ] && [ -d "$adir" ] && [ -n "$(ls -A "$adir")" ]; then
    (cd "$adir" && sha256sum -- * > "$H_DIR/ARTIFACTS.sha256")
  fi
  cat > "$H_DIR/SUMMARY.json" <<JSON
{
  "status": "CURRENT",
  "harness": "tests/integration/postgres/lib.sh (reason-asserting, v2)",
  "run_label": "$label",
  "mode": "$H_MODE",
  "overall": "$overall",
  "expected_cases": $expected,
  "rows": $rows,
  "passed": $pass,
  "failed": $fail,
  "errors": $err,
  "not_run": $notrun,
  "negative_faults_detected": $neg_pass,
  "finished_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON
  {
    echo "# $label"
    echo
    echo "Status: CURRENT (harness v2). Mode: \`$H_MODE\`. Overall: **$overall**"
    echo "($pass/$expected passed; $fail failed, $err errors, $notrun not run)."
    echo
    echo "| # | step | kind | expected | exit | result | class |"
    echo "|---|------|------|----------|------|--------|-------|"
    awk -F'\t' 'NR>1 {printf "| %s | %s | %s | %s | %s | %s | %s |\n", $1, $2, $3, $4, $5, $6, $7}' "$H_TSV"
  } > "$H_DIR/SUMMARY.md"
  (cd "$H_DIR" && find . -type f ! -name SHA256SUMS ! -path './artifacts/*' -printf '%P\n' | LC_ALL=C sort | xargs -d '\n' sha256sum > SHA256SUMS)
  echo "evidence: $H_DIR overall=$overall passed=$pass/$expected failed=$fail errors=$err not_run=$notrun"
  [ "$overall" = PASS ]
}
