#!/usr/bin/env bash
# Thin wrapper kept for compatibility; the checks live in verify_evidence.py.
exec python3 "$(dirname "${BASH_SOURCE[0]}")/verify_evidence.py" "$@"
