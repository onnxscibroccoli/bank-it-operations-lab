#!/usr/bin/env bash
# Compatibility shim: the acceptance gate moved to tools/acceptance/gate/ (acceptance/INTEGRATION-V2.md, decision D-1).
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/tools/acceptance/gate/run.sh" "$@"
