#!/usr/bin/env bash
# Prints whether AWS credential sources are visible (values never printed). Exit 1 if any are present.
rc=0
for v in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE AWS_DEFAULT_PROFILE CDK_DEFAULT_ACCOUNT; do
  if [ -n "${!v:-}" ]; then echo "$v=PRESENT"; rc=1; else echo "$v=unset"; fi
done
echo "AWS_CONFIG_FILE=${AWS_CONFIG_FILE:-<default>} AWS_SHARED_CREDENTIALS_FILE=${AWS_SHARED_CREDENTIALS_FILE:-<default>}"
echo "AWS_EC2_METADATA_DISABLED=${AWS_EC2_METADATA_DISABLED:-unset}"
command -v aws >/dev/null && echo "aws cli: present (not invoked)" || echo "aws cli: not installed"
exit $rc
