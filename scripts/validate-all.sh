#!/usr/bin/env bash
# Full offline, credential-free validation for overnight/integration. Run from anywhere.
#   scripts/validate-all.sh                 # everything (needs Node 20 + npm, and PostgreSQL binaries for the restore exercise)
#   scripts/validate-all.sh --python-only   # stdlib Python checks only (shared evidence validator, Entra, evidence bundles)
#   PG_BIN=/path/to/pg/bin scripts/validate-all.sh   # point the Postgres exercise at specific binaries
# Nothing is deployed; no AWS, Entra or Graph calls; AWS credential variables are unset for every step.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY_ONLY=0; [ "${1:-}" = "--python-only" ] && PY_ONLY=1
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE AWS_ROLE_ARN AWS_WEB_IDENTITY_TOKEN_FILE \
      AWS_CONTAINER_CREDENTIALS_FULL_URI AWS_CONTAINER_CREDENTIALS_RELATIVE_URI CDK_DEFAULT_ACCOUNT CDK_DEFAULT_REGION
export AWS_EC2_METADATA_DISABLED=true AWS_CONFIG_FILE=/dev/null AWS_SHARED_CREDENTIALS_FILE=/dev/null CDK_DISABLE_CLI_TELEMETRY=true
V=evidence/shared/validate_evidence.py
FAILED=(); N=0
step() { local name="$1"; shift; N=$((N+1)); echo "::: [$N] $name"; if "$@"; then echo "    ok"; else echo "    FAILED: $name"; FAILED+=("$name"); fi; }

# --- PR #3 shared evidence tooling
step "shared validator unit tests" python3 -m unittest discover -s evidence/shared/tests
# --- PR #4 Entra CA (offline, synthetic)
step "entra unit tests"            python3 -m unittest discover -s tests/entra
step "entra validator on baseline" python3 identity/entra/ca_validator.py --quiet
step "entra fixture drift"         python3 tests/entra/make_fixtures.py --check
for r in evidence/entra/runs/*/; do step "entra evidence verify $r" python3 evidence/entra/generate_evidence.py --verify "${r%/}"; done
# --- PR #5 AWS evidence bundle (static)
step "aws evidence SHA256SUMS" bash -c 'cd evidence/aws/aws-remediation-vpc-rds && sha256sum -c SHA256SUMS --quiet'
for t in evidence/aws/aws-remediation-vpc-rds/synth/*.template.json; do step "s3 self-logging $t" python3 "$V" cfn-s3-selflog "$t"; done
# --- PR #2 Postgres evidence (harness v2, committed runs; see evidence/postgres/runs/INDEX.md)
PV=tests/integration/postgres/verify_evidence.py
for r in ci-service-40741329107-1 ci-offline-40741329107-1 local-offline-v2-20261028T180208Z; do
  step "postgres v2 verify $r" python3 "$PV" "evidence/postgres/runs/$r"
done
step "postgres mismatch control is REJECTED" bash -c '! python3 '"$PV"' evidence/postgres/runs/ci-mismatch-control-40741329107-1 >/dev/null'
for r in ci-service-40630856041-1 local-offline-20261028T041038Z integration-offline-20261028T180134Z; do
  step "postgres v1 run $r reported HISTORICAL (exit 3)" bash -c 'python3 '"$PV"' "evidence/postgres/runs/'"$r"'" >/dev/null; [ $? -eq 3 ]'
done
step "postgres harness self-test (no DB)" bash -c 'd=$(mktemp -d); EVIDENCE_DIR="$d" bash tests/integration/postgres/selftest_harness.sh >/dev/null; rc=$?; rm -rf "$d"; exit $rc'
# cross-check: PR #3's shared validator must agree with PR #2's v2 verifier on the current runs
for r in ci-service-40741329107-1 ci-offline-40741329107-1 local-offline-v2-20261028T180208Z; do
  step "shared postgres-negatives $r" python3 "$V" postgres-negatives "evidence/postgres/runs/$r"
done
step "shared postgres-negatives flags v1 false PASSes" bash -c '! python3 '"$V"' postgres-negatives evidence/postgres/runs/ci-service-40630856041-1 >/dev/null'
step "shared postgres-negatives rejects all-NOT_RUN mismatch control" bash -c '! python3 '"$V"' postgres-negatives evidence/postgres/runs/ci-mismatch-control-40741329107-1 >/dev/null'

if [ "$PY_ONLY" -eq 0 ]; then
  # --- PR #5 infra/aws-cdk
  step "aws-cdk npm ci"  bash -c 'cd infra/aws-cdk && npm ci --no-audit --no-fund --ignore-scripts >/dev/null'
  step "aws-cdk tsc"     bash -c 'cd infra/aws-cdk && npx tsc --noEmit'
  step "aws-cdk jest"    bash -c 'cd infra/aws-cdk && npx jest --ci'
  step "aws-cdk synth"   bash -c 'cd infra/aws-cdk && rm -rf cdk.out && npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --quiet >/dev/null'
  step "aws-cdk nag gate" bash -c 'cd infra/aws-cdk && c=0; for f in cdk.out/*-NagReport.csv; do c=$((c+1)); [ "$(grep -c "\"Non-Compliant\"" "$f")" -eq 0 ] || exit 1; done; [ "$c" -eq 4 ]'
  for t in infra/aws-cdk/cdk.out/*.template.json; do step "s3 self-logging (fresh) $t" python3 "$V" cfn-s3-selflog "$t"; done
  for t in evidence/aws/aws-remediation-vpc-rds/synth/*.template.json; do step "synth drift $(basename "$t")" diff -q "$t" "infra/aws-cdk/cdk.out/$(basename "$t")"; done
  # --- PR #2 Postgres restore exercise (fresh, offline unix-socket cluster)
  if [ -n "${PG_BIN:-}" ] || command -v initdb >/dev/null 2>&1 || ls -d /usr/lib/postgresql/*/bin >/dev/null 2>&1; then
    TMP_EV="$(mktemp -d)"
    step "postgres restore exercise v2 (offline)" env RUN_LABEL=validate-all EVIDENCE_DIR="$TMP_EV" bash tests/integration/postgres/run_restore_scenario.sh offline
    step "postgres fresh-run v2 verifier" python3 "$PV" "$TMP_EV" --require-artifacts
    step "postgres fresh-run shared negatives" python3 "$V" postgres-negatives "$TMP_EV"
    rm -rf "$TMP_EV"
  else
    echo "::: SKIP postgres restore exercise: no PostgreSQL binaries (set PG_BIN)"; FAILED+=("postgres exercise skipped (no binaries)")
  fi
fi

echo
if [ "${#FAILED[@]}" -eq 0 ]; then echo "validate-all: PASS ($N steps)"; exit 0; fi
echo "validate-all: FAIL (${#FAILED[@]} of $N): ${FAILED[*]}"; exit 1
