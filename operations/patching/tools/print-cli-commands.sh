#!/usr/bin/env bash
# Print (never run) the AWS CLI commands that would register the example SSM patch resources,
# in dependency order, for review in a change record. This script makes no AWS calls: it only
# echoes text. Placeholders like <CANARY_WINDOW_ID> must be filled from real command output by
# the operator, under an approved change.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cli="${here}/ssm/cli"
region="${AWS_REGION_FOR_REVIEW:-<REGION>}"

emit() {
  printf '%s\n' "$*"
}

emit "# DRY RUN - commands for review only; nothing below has been executed."
emit "# region: ${region}"
for os_name in al2023 rhel; do
  emit "aws ssm create-patch-baseline --region ${region} --cli-input-json file://${cli#"${here}/"}/create-patch-baseline.${os_name}.json"
done
for f in "${cli}"/register-patch-group.*.json; do
  emit "aws ssm register-patch-baseline-for-patch-group --region ${region} --cli-input-json file://${f#"${here}/"}"
done
for ring in canary wave1 wave2; do
  emit "aws ssm create-maintenance-window --region ${region} --cli-input-json file://ssm/cli/create-maintenance-window.${ring}.json"
  emit "aws ssm register-target-with-maintenance-window --region ${region} --cli-input-json file://ssm/cli/register-target.${ring}.json"
  emit "aws ssm register-task-with-maintenance-window --region ${region} --cli-input-json file://ssm/cli/register-task.${ring}.json"
done
