#!/usr/bin/env python3
"""Convenience wrapper: python3 observability/run_healthcheck.py <evaluate|collect|host> ..."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from healthcheck.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
