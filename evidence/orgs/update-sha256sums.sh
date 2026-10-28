#!/usr/bin/env bash
# Regenerate evidence/orgs/SHA256SUMS over git-tracked + staged files in infra/orgs and evidence/orgs
# (excluding SHA256SUMS itself). Stage files first. Verify from repo root: sha256sum -c evidence/orgs/SHA256SUMS
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
git ls-files -- infra/orgs evidence/orgs | grep -vx 'evidence/orgs/SHA256SUMS' | LC_ALL=C sort \
  | xargs -d '\n' sha256sum > evidence/orgs/SHA256SUMS
echo "SHA256SUMS: $(wc -l < evidence/orgs/SHA256SUMS) entries"
