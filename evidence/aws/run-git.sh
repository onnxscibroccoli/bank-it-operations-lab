#!/usr/bin/env bash
# Usage: run-git.sh <logname> <command...>  (runs at repo root; logs output + exit code; appends COMMANDS.tsv)
# Never used for commands that print credentials.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NAME="$1"; shift
LOG="$ROOT/evidence/aws/logs/$NAME.log"
cd "$ROOT"
{ echo "# cwd: $(pwd)"; echo "# started: $(date -Iseconds)"; echo "# command: $*"; } > "$LOG"
env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN -u AWS_PROFILE \
    AWS_EC2_METADATA_DISABLED=true AWS_CONFIG_FILE=/dev/null AWS_SHARED_CREDENTIALS_FILE=/dev/null \
    "$@" >> "$LOG" 2>&1
rc=$?
# scrub anything token-like defensively
sed -i -E 's/(gh[pousr]_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|ya29\.[A-Za-z0-9._-]+|"access_token":"[^"]+"|"refresh_token":"[^"]+")/[REDACTED]/g' "$LOG"
{ echo "# finished: $(date -Iseconds)"; echo "# exit_code: $rc"; } >> "$LOG"
printf '%s\t%s\t%s\n' "$NAME.log" "$rc" "$*" >> "$ROOT/evidence/aws/logs/COMMANDS.tsv"
echo "$NAME.log exit_code=$rc"
exit $rc
