#!/usr/bin/env bash
# Usage: run-cmd.sh <logname> <command...>  (runs in infra/aws-cdk, credential-free env)
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="$ROOT/evidence/aws/logs/$1.log"; shift
cd "$ROOT/infra/aws-cdk"
{
  echo "# cwd: $(pwd)"
  echo "# started: $(date -Iseconds)"
  echo "# command: $*"
  echo "# env: AWS_* and CDK_DEFAULT_* unset; AWS_EC2_METADATA_DISABLED=true"
} > "$LOG"
env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN -u AWS_PROFILE \
    -u AWS_DEFAULT_PROFILE -u CDK_DEFAULT_ACCOUNT -u CDK_DEFAULT_REGION \
    AWS_EC2_METADATA_DISABLED=true AWS_CONFIG_FILE=/dev/null AWS_SHARED_CREDENTIALS_FILE=/dev/null \
    CDK_DISABLE_CLI_TELEMETRY=true \
    "$@" >> "$LOG" 2>&1
rc=$?
{ echo "# finished: $(date -Iseconds)"; echo "# exit_code: $rc"; } >> "$LOG"
echo "$(basename "$LOG") exit_code=$rc"
exit $rc
