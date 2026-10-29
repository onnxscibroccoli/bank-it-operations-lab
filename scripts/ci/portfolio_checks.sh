#!/usr/bin/env bash
# Offline checks only. Each suite uses its own process to isolate import paths.
set -uo pipefail
cd "$(dirname "$0")/../.."
failed=0
check() { echo "::group::$*"; "$@" || failed=1; echo '::endgroup::'; }
check python3 -m unittest discover -s observability/tests
check bash -c 'cd integrations/vendor-mock && python3 -m unittest discover -s tests -t .'
check python3 -m unittest discover -s governance/vendor-risk/tests
check python3 governance/vendor-risk/check_governance.py
check python3 -m unittest discover -s identity/governance/tests
check python3 identity/governance/make_fixtures.py --check
check python3 -m unittest discover -s governance/controls/tests
check python3 governance/controls/validate_mapping.py
check python3 -m unittest discover -s operations/patching/tests
check python3 operations/patching/tests/make_fixtures.py --check
check python3 -m unittest discover -s operations/hardening/tests
check python3 -m unittest discover -s operations/hybrid/checks
check python3 operations/hybrid/checks/check_hybrid_runbooks.py
check python3 -m unittest discover -s docs/runbooks/aws-backup/cost-capacity
check bash -c "sha256sum -c evidence/backup/aws-backup-dr/SHA256SUMS --quiet"
check python3 -m unittest discover -s inventory/tests
check python3 inventory/generate.py --check
exit "$failed"
