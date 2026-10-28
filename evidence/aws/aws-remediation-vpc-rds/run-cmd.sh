#!/usr/bin/env bash
# Credential-free command logger. Usage: run-cmd.sh <log-name> <command...>  (run from infra/aws-cdk)
# Appends one row to COMMANDS.tsv: started_utc, exit_code, duration_s, log, cwd, command. Output (incl. failures) kept in logs/.
set -uo pipefail
EV="$(cd "$(dirname "$0")" && pwd)"
name="$1"; shift
# Hard guarantee: no AWS credentials or profiles reach the command.
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE AWS_DEFAULT_PROFILE
export AWS_EC2_METADATA_DISABLED=true AWS_CONFIG_FILE=/dev/null AWS_SHARED_CREDENTIALS_FILE=/dev/null CDK_DISABLE_VERSION_CHECK=1
start=$(date -u +%Y-%m-%dT%H:%M:%SZ); t0=$(date +%s)
"$@" > "$EV/logs/$name.log" 2>&1; rc=$?
dt=$(( $(date +%s) - t0 ))
sed -i -E 's/\x1b\[[0-9;]*m//g' "$EV/logs/$name.log"
[ -f "$EV/COMMANDS.tsv" ] || printf 'started_utc\texit_code\tduration_s\tlog\tcwd\tcommand\n' > "$EV/COMMANDS.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$start" "$rc" "$dt" "logs/$name.log" "${PWD#*/bank-it-ops-remediation/}" "$*" >> "$EV/COMMANDS.tsv"
echo "[$name] exit=$rc (${dt}s)"
exit $rc
