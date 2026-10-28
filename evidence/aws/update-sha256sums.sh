#!/usr/bin/env bash
# Regenerate evidence/aws/SHA256SUMS over all git-tracked + staged files in the BANK-AWS-001 owned paths
# (excluding SHA256SUMS itself). Run from anywhere; stage files first.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
git ls-files -- infra/aws-cdk evidence/aws .github/workflows/bank-aws-001-cdk.yml reports/MORNING_REPORT.md \
  | grep -vx 'evidence/aws/SHA256SUMS' | LC_ALL=C sort | xargs -d '\n' sha256sum > evidence/aws/SHA256SUMS
echo "SHA256SUMS: $(wc -l < evidence/aws/SHA256SUMS) entries"
