#!/usr/bin/env bash
# First executable acceptance command for bank-it-operations-lab (Worker D, vertical slice).
#
#   scripts/acceptance/run.sh <TARGET_SHA> [--out DIR] [--inject-defect NAME]
#
# 1. Checks out exactly <TARGET_SHA> (full 40-hex commit) into a detached git worktree and asserts HEAD == SHA.
# 2. Runs, against that checkout, using the target's own tooling:
#      AWS static checks (npm ci, tsc, jest, credential-free cdk synth, cdk-nag gate, S3 self-logging, synth drift)
#      PostgreSQL recovery (fresh offline pg_dump/pg_restore exercise + independent verifier + harness self-test)
#      Entra offline validation (unit tests, validator on baseline, fixture drift, committed evidence re-verify)
#      Reports/hashes (every committed SHA256SUMS bundle; this run's own results are hashed and re-verified)
#      Defect controls (deliberately broken copies MUST be rejected by the target's checkers)
# 3. Writes results.tsv / results.json / SUMMARY.md / SHA256SUMS to --out (default ./acceptance-out).
# 4. Exit codes: 0 = every required check PASS; 1 = at least one FAIL; 2 = no FAIL but a required check UNKNOWN.
#
# --inject-defect entra-mfa-report-only   flips CA002 (Require MFA, all users) to report-only INSIDE the
#   checked-out worktree before the checks run. The run MUST then exit nonzero with ENTRA-02 = FAIL.
#   Used by the CI defect-control job to prove the gate itself fails closed end to end.
#
# No AWS, Entra or Graph calls. AWS credential variables are unset. Nothing is deployed. No verdict is
# ever written without the command that produced it; a check that cannot run is UNKNOWN, never PASS.
set -uo pipefail

usage() { sed -n '2,20p' "$0" >&2; exit 64; }
SHA=""; OUT="acceptance-out"; DEFECT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --inject-defect) DEFECT="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) [ -z "$SHA" ] && SHA="$1" || usage; shift ;;
  esac
done
[[ "$SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "TARGET_SHA must be a full 40-hex commit SHA (got '$SHA')" >&2; exit 64; }
case "$DEFECT" in ""|entra-mfa-report-only) ;; *) echo "unknown --inject-defect $DEFECT" >&2; exit 64 ;; esac

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"; LOGS="$OUT/logs"; mkdir -p "$LOGS"
RESULTS="$OUT/results.tsv"; printf 'check_id\trequired\tverdict\texit_code\tdetail\tlog\n' > "$RESULTS"

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE AWS_ROLE_ARN AWS_WEB_IDENTITY_TOKEN_FILE \
      AWS_CONTAINER_CREDENTIALS_FULL_URI AWS_CONTAINER_CREDENTIALS_RELATIVE_URI CDK_DEFAULT_ACCOUNT CDK_DEFAULT_REGION
export AWS_EC2_METADATA_DISABLED=true AWS_CONFIG_FILE=/dev/null AWS_SHARED_CREDENTIALS_FILE=/dev/null CDK_DISABLE_CLI_TELEMETRY=true

record() { # id required verdict exit detail log
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$(printf '%s' "$5" | tr '\t\n' '  ')" "$6" >> "$RESULTS"
  printf '[%-7s] %-10s req=%s exit=%s %s\n' "$3" "$1" "$2" "$4" "$5"
}
# check ID REQUIRED DESCRIPTION -- cmd...   : PASS iff cmd exits 0
check() {
  local id="$1" req="$2" desc="$3"; shift 4
  local log="logs/$id.log" rc
  { echo "# check: $id - $desc"; echo "# cwd: $(pwd)"; printf '# cmd:'; printf ' %q' "$@"; echo; } > "$OUT/$log"
  "$@" >> "$OUT/$log" 2>&1; rc=$?
  echo "# exit_code: $rc" >> "$OUT/$log"
  if [ $rc -eq 0 ]; then record "$id" "$req" PASS $rc "$desc" "$log"; else record "$id" "$req" FAIL $rc "$desc" "$log"; fi
  return $rc
}
# expect_reject ID REASON_REGEX DESCRIPTION -- cmd...
#   defect control: PASS iff cmd exits NONZERO *and* its output matches REASON_REGEX (rejected for the
#   intended reason). Exit 0 = FAIL (defect not detected). Nonzero for another reason (crash, traceback,
#   missing tool) = UNKNOWN, never PASS.
expect_reject() {
  local id="$1" why="$2" desc="$3"; shift 4
  local log="logs/$id.log" rc
  { echo "# defect-control: $id - $desc"; echo "# reason_regex: $why"; printf '# cmd:'; printf ' %q' "$@"; echo; } > "$OUT/$log"
  "$@" >> "$OUT/$log" 2>&1; rc=$?
  echo "# exit_code: $rc" >> "$OUT/$log"
  if [ $rc -eq 0 ]; then record "$id" yes FAIL $rc "defect NOT detected (checker accepted a broken input): $desc" "$log"
  elif grep -v '^# ' "$OUT/$log" | grep -qE "$why"; then record "$id" yes PASS $rc "defect detected for intended reason: $desc" "$log"
  else record "$id" yes UNKNOWN $rc "checker exited $rc but output lacks intended reason /$why/: $desc" "$log"; fi
}
unknown() { record "$1" "$2" UNKNOWN - "$3" -; }

# ---------------------------------------------------------------- 1. exact checkout
WT="$(mktemp -d)/target"
cleanup() { git -C "$REPO" worktree remove --force "$WT" >/dev/null 2>&1 || true; }
trap cleanup EXIT
git -C "$REPO" cat-file -e "$SHA^{commit}" 2>/dev/null || git -C "$REPO" fetch --quiet origin "$SHA" || true
if ! git -C "$REPO" worktree add --detach --quiet "$WT" "$SHA" 2>"$LOGS/CHECKOUT.log"; then
  echo "# exit_code: 1" >> "$LOGS/CHECKOUT.log"; record CHECKOUT yes FAIL 1 "could not check out $SHA" logs/CHECKOUT.log
else
  HEAD="$(git -C "$WT" rev-parse HEAD)"; echo "HEAD=$HEAD" >> "$LOGS/CHECKOUT.log"
  [ "$HEAD" = "$SHA" ]; echo "# exit_code: $?" >> "$LOGS/CHECKOUT.log"
  if [ "$HEAD" = "$SHA" ]; then record CHECKOUT yes PASS 0 "worktree HEAD == $SHA" logs/CHECKOUT.log
  else record CHECKOUT yes FAIL 1 "worktree HEAD $HEAD != $SHA" logs/CHECKOUT.log; fi
fi

if [ -d "$WT" ] && [ "$(git -C "$WT" rev-parse HEAD 2>/dev/null)" = "$SHA" ]; then
cd "$WT"
V=evidence/shared/validate_evidence.py

if [ "$DEFECT" = entra-mfa-report-only ]; then
  f=identity/entra/policies/CA002-Require-MFA-All-Users.json
  python3 - "$f" <<'PY' && echo "INJECTED DEFECT: $f state -> enabledForReportingButNotEnforced"
import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["state"]="enabledForReportingButNotEnforced"; json.dump(d,open(p,"w"),indent=2)
PY
  record DEFECT-INJECTED no INFO - "worktree deliberately modified: $f state=enabledForReportingButNotEnforced (this run MUST exit nonzero)" -
fi

# ---------------------------------------------------------------- 2a. AWS static checks
if env | grep -qE '^(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|AWS_PROFILE)='; then
  record AWS-00 yes FAIL 1 "AWS credentials present in environment; refusing" -
else record AWS-00 yes PASS 0 "no AWS credential variables in environment" -; fi
if [ ! -f infra/aws-cdk/package-lock.json ]; then
  unknown AWS-01 yes "infra/aws-cdk/package-lock.json not present at target"
elif ! command -v npm >/dev/null; then
  unknown AWS-01 yes "npm not installed; AWS static checks could not run"
else
  if check AWS-01 yes "npm ci (lockfile, --ignore-scripts)" -- bash -c 'cd infra/aws-cdk && npm ci --no-audit --no-fund --ignore-scripts'; then
    check AWS-02 yes "tsc --noEmit" -- bash -c 'cd infra/aws-cdk && npx --no-install tsc --noEmit'
    check AWS-03 yes "jest unit + negative-control tests" -- bash -c 'cd infra/aws-cdk && npx --no-install jest --ci'
    if check AWS-04 yes "credential-free cdk synth --no-lookups" -- bash -c 'cd infra/aws-cdk && rm -rf cdk.out && npx --no-install cdk synth --no-lookups --no-version-reporting --no-path-metadata --quiet'; then
      check AWS-05 yes "cdk-nag gate: 4 reports, each non-empty, 0 Non-Compliant" -- bash -c '
        cd infra/aws-cdk; c=0
        for f in cdk.out/*-NagReport.csv; do [ -f "$f" ] || continue; c=$((c+1))
          rows=$(tail -n +2 "$f" | grep -c . || true); n=$(grep -c "\"Non-Compliant\"" "$f" || true)
          echo "$f rows=$rows non_compliant=$n"; [ "$rows" -gt 0 ] && [ "$n" -eq 0 ] || exit 1; done
        echo "reports=$c"; [ "$c" -eq 4 ]'
      check AWS-06 yes "no S3 bucket logs to itself (fresh synth)" -- bash -c 'set -e; n=0; for t in infra/aws-cdk/cdk.out/*.template.json; do n=$((n+1)); python3 '"$V"' cfn-s3-selflog "$t"; done; [ $n -gt 0 ]'
      check AWS-07 yes "fresh synth == committed evidence templates (no drift)" -- bash -c 'set -e; n=0; for t in evidence/aws/aws-remediation-vpc-rds/synth/*.template.json; do n=$((n+1)); diff -u "$t" "infra/aws-cdk/cdk.out/$(basename "$t")"; done; [ $n -gt 0 ]'
      t1="$(ls infra/aws-cdk/cdk.out/BankItLabSecureStorage.template.json 2>/dev/null)"
      if [ -n "$t1" ]; then
        python3 - "$t1" "$OUT/defect-selflog.template.json" <<'PY' > "$LOGS/DEFECT-AWS-prep.log" 2>&1
import json,sys
d=json.load(open(sys.argv[1])); n=0
for lid,r in d.get("Resources",{}).items():
    if r.get("Type")=="AWS::S3::Bucket":
        r.setdefault("Properties",{})["LoggingConfiguration"]={"DestinationBucketName":{"Ref":lid},"LogFilePrefix":"self/"}; n+=1; break
json.dump(d,open(sys.argv[2],"w")); print("buckets mutated:",n); sys.exit(0 if n else 1)
PY
        if [ $? -eq 0 ]; then expect_reject DEFECT-AWS "delivered to itself" "S3 bucket made to log to itself must be rejected by cfn-s3-selflog" -- python3 "$V" cfn-s3-selflog "$OUT/defect-selflog.template.json"
        else unknown DEFECT-AWS yes "could not build self-logging defect template (no S3 bucket found)"; fi
      else unknown DEFECT-AWS yes "BankItLabSecureStorage.template.json not synthesized"; fi
    else
      for i in AWS-05 AWS-06 AWS-07 DEFECT-AWS; do unknown $i yes "not run: synth failed"; done
    fi
  else
    for i in AWS-02 AWS-03 AWS-04 AWS-05 AWS-06 AWS-07 DEFECT-AWS; do unknown $i yes "not run: npm ci failed"; done
  fi
fi

# ---------------------------------------------------------------- 2b. PostgreSQL recovery
PGS=tests/integration/postgres
if [ ! -f $PGS/run_restore_scenario.sh ]; then
  unknown PG-01 yes "$PGS/run_restore_scenario.sh not present at target"
else
  PGBIN="${PG_BIN:-}"; [ -z "$PGBIN" ] && command -v pg_config >/dev/null && [ -x "$(pg_config --bindir)/initdb" ] && PGBIN="$(pg_config --bindir)"
  [ -z "$PGBIN" ] && PGBIN="$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)"
  if [ -z "$PGBIN" ] || [ ! -x "$PGBIN/initdb" ]; then
    unknown PG-01 yes "no PostgreSQL server binaries (initdb) found; recovery exercise could not run (set PG_BIN)"
    unknown PG-02 yes "not run: PG-01 could not run"
  else
    PGEV="$OUT/postgres-run"
    check PG-01 yes "offline pg_dump/pg_restore recovery exercise (harness v2, $PGBIN)" -- env PG_BIN="$PGBIN" RUN_LABEL=acceptance-$SHA EVIDENCE_DIR="$PGEV" bash $PGS/run_restore_scenario.sh offline
    check PG-02 yes "independent verifier re-derives every verdict + artifact hashes" -- python3 $PGS/verify_evidence.py "$PGEV" --require-artifacts
  fi
  check PG-03 yes "harness self-test: deliberate wrong-reason/unexpected-success/forged cases must FAIL" -- bash -c 'd=$(mktemp -d); EVIDENCE_DIR="$d" bash '"$PGS"'/selftest_harness.sh; rc=$?; rm -rf "$d"; exit $rc'
fi

# ---------------------------------------------------------------- 2c. Entra offline validation
if [ ! -f identity/entra/ca_validator.py ]; then
  unknown ENTRA-01 yes "identity/entra/ca_validator.py not present at target"
else
  check ENTRA-01 yes "Entra CA validator unit tests" -- python3 -m unittest discover -s tests/entra
  check ENTRA-02 yes "Entra CA validator on committed baseline policies" -- python3 identity/entra/ca_validator.py --quiet
  check ENTRA-03 yes "Entra fixtures regenerate with no drift" -- python3 tests/entra/make_fixtures.py --check
  n=0; for r in evidence/entra/runs/*/; do [ -d "$r" ] || continue; n=$((n+1))
    check "ENTRA-04.$n" yes "re-verify committed Entra evidence ${r%/}" -- python3 evidence/entra/generate_evidence.py --verify "${r%/}"; done
  [ $n -eq 0 ] && unknown ENTRA-04 yes "no committed Entra evidence runs"
  # defect control on a COPY (never the worktree baseline): same policy flipped to report-only must be rejected
  D="$(mktemp -d)"; cp identity/entra/policies/*.json "$D/"
  python3 -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["state"]="enabledForReportingButNotEnforced"; json.dump(d,open(p,"w"))' "$D/CA002-Require-MFA-All-Users.json" \
    && expect_reject DEFECT-ENTRA "CA002-Require-MFA-All-Users: state=enabledForReportingButNotEnforced" "CA002 Require-MFA flipped to report-only must be rejected by ca_validator" -- python3 identity/entra/ca_validator.py "$D" \
    || unknown DEFECT-ENTRA yes "could not build Entra defect copy"
  rm -rf "$D"
fi

# ---------------------------------------------------------------- 2e. integrated workers A (contract) and B (runner)
if [ -f schemas/acceptance/check_acceptance.py ]; then
  check ACC-A-01 yes "acceptance-contract (A) unit tests" -- python3 -m unittest discover -s tests/acceptance-contract
  check ACC-A-02 yes "acceptance-contract (A) fixtures regenerate with no drift" -- python3 tests/acceptance-contract/make_fixtures.py --check
else unknown ACC-A-01 yes "schemas/acceptance/check_acceptance.py (worker A) not present at target"; fi
if [ -f tools/acceptance/runner.py ]; then
  check ACC-B-01 yes "acceptance-runner (B) unit tests" -- python3 -m unittest discover -s tools/acceptance/tests
  check ACC-B-02 yes "acceptance-runner (B) allowlisted checks.json run + shared-validator bundle check" -- python3 tools/acceptance/runner.py --label "acceptance-$SHA"
else unknown ACC-B-01 yes "tools/acceptance/runner.py (worker B) not present at target"; fi

# ---------------------------------------------------------------- 2d. reports and hashes
n=0; while IFS= read -r s; do n=$((n+1))
  check "HASH-$n" yes "committed bundle $s verifies (no missing file, no mismatch, no self-listing)" -- python3 "$V" hashes "$s"
done < <(git ls-files | grep -E '(^|/)SHA256SUMS$' | sort)
[ $n -eq 0 ] && unknown HASH-1 yes "no committed SHA256SUMS bundles found"
f="$(git ls-files 'evidence/aws/*/SHA256SUMS' | head -1)"
if [ -n "$f" ]; then
  D="$(mktemp -d)"; cp -r "$(dirname "$f")/." "$D/"
  victim="$(awk 'NR==1{print $2}' "$D/SHA256SUMS" | sed 's/^\*//')"; printf ' ' >> "$D/$victim"
  expect_reject DEFECT-HASH "sha256 mismatch for (\\./)?$victim" "one byte appended to $(dirname "$f")/$victim must break its SHA256SUMS" -- python3 "$V" hashes "$D/SHA256SUMS"
  rm -rf "$D"
else unknown DEFECT-HASH yes "no AWS evidence bundle to tamper"; fi
for r in reports/INTEGRATION.md reports/ACCEPTANCE.md; do
  if [ -s "$r" ]; then record "REPORT-$(basename "$r" .md)" no PASS 0 "$r present and non-empty at target (content not certified)" -
  else unknown "REPORT-$(basename "$r" .md)" no "$r absent at target"; fi
done
cd "$REPO"
fi  # checkout ok

# ---------------------------------------------------------------- 3. gate + own report integrity
python3 - "$RESULTS" "$OUT" "$SHA" "$DEFECT" <<'PY'
import csv,json,sys,os,datetime
res,out,sha,defect=sys.argv[1:5]
rows=list(csv.DictReader(open(res),delimiter="\t"))
req=[r for r in rows if r["required"]=="yes"]
fail=[r["check_id"] for r in req if r["verdict"]=="FAIL"]
unk=[r["check_id"] for r in req if r["verdict"]=="UNKNOWN"]
bad=[r for r in rows if r["verdict"] not in ("PASS","FAIL","UNKNOWN","INFO")]
overall="FAIL" if (fail or bad or not req) else ("UNKNOWN" if unk else "PASS")
s={"target_sha":sha,"injected_defect":defect or None,"overall":overall,"required":len(req),
   "pass":sum(r["verdict"]=="PASS" for r in req),"fail":fail,"unknown":unk,
   "generated_utc":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),"checks":rows}
json.dump(s,open(os.path.join(out,"results.json"),"w"),indent=2)
with open(os.path.join(out,"SUMMARY.md"),"w") as f:
    f.write(f"# Acceptance run for `{sha}`\n\nOverall: **{overall}** (required {len(req)}, pass {s['pass']}, fail {len(fail)}, unknown {len(unk)})\n")
    if defect: f.write(f"\nInjected defect: `{defect}` (this run is expected to FAIL)\n")
    f.write("\n| check | required | verdict | exit | detail |\n|---|---|---|---|---|\n")
    for r in rows: f.write(f"| {r['check_id']} | {r['required']} | {r['verdict']} | {r['exit_code']} | {r['detail'].replace('|','/')} |\n")
print(f"OVERALL={overall} required={len(req)} fail={fail} unknown={unk}")
PY
( cd "$OUT" && find . -type f ! -name SHA256SUMS ! -path './postgres-run/*' | sort | sed 's|^\./||' | xargs sha256sum > SHA256SUMS )
if ! python3 "$REPO/scripts/acceptance/verify_results.py" "$OUT"; then echo "acceptance output failed self-verification" >&2; exit 1; fi
overall="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["overall"])' "$OUT/results.json")"
echo "acceptance: $overall for $SHA (out: $OUT)"
case "$overall" in PASS) exit 0 ;; UNKNOWN) exit 2 ;; *) exit 1 ;; esac
