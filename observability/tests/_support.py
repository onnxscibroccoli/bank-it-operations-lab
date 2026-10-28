"""Shared offline test helpers: fixed clock, fake host readers, fake transports."""

import io
import json
import os
import sys

OBS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if OBS_DIR not in sys.path:
    sys.path.insert(0, OBS_DIR)

from healthcheck import cli  # noqa: E402
from healthcheck.timeutil import StepMonotonic, fixed_clock  # noqa: E402

FIXTURES = os.path.join(OBS_DIR, "fixtures")
CONFIG_EXAMPLE = os.path.join(OBS_DIR, "config.example.json")
NOW = "2026-10-28T12:01:00Z"


def fake_readers(**overrides):
    r = {
        "load_avg_1m": lambda: 0.5,
        "cpu_count": lambda: 4,
        "disk": lambda: (100_000, 40_000, 60_000),
        "mem_available_ratio": lambda: 0.5,
        "uptime_s": lambda: 1234.5,
    }
    r.update(overrides)
    return r


def ok_transports():
    return {
        "http": lambda url, t, mb: (200, b"ok"),
        "tcp": lambda host, port, t: None,
        "dns": lambda name: ["192.0.2.10", "192.0.2.11"],
    }


def run_cli(argv, clock_ts=NOW, transports=None, host_readers=None):
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(argv, stdout=out, stderr=err, clock=fixed_clock(clock_ts),
                    monotonic=StepMonotonic(0.002), transports=transports,
                    host_readers=host_readers)
    result = json.loads(out.getvalue()) if out.getvalue().strip() else None
    logs = [json.loads(line) for line in err.getvalue().splitlines() if line.strip()]
    return code, result, logs, out.getvalue() + err.getvalue()
