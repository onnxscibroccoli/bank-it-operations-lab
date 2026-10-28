"""UTC timestamp helpers and injectable clocks."""

import re
import time
from datetime import datetime, timezone

_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$")


def parse_ts(value):
    """Parse a strict RFC 3339 UTC timestamp ending in 'Z'. Raises ValueError."""
    if not isinstance(value, str) or not _TS_RE.match(value):
        raise ValueError("timestamp must look like YYYY-MM-DDTHH:MM:SS[.ffffff]Z")
    fmt = "%Y-%m-%dT%H:%M:%S.%fZ" if "." in value else "%Y-%m-%dT%H:%M:%SZ"
    return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)


def format_ts(dt):
    dt = dt.astimezone(timezone.utc)
    if dt.microsecond:
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def system_clock():
    return datetime.now(timezone.utc)


def fixed_clock(ts):
    """Return a clock that always reports the given timestamp (str or datetime)."""
    dt = parse_ts(ts) if isinstance(ts, str) else ts
    return lambda: dt


class StepMonotonic:
    """Deterministic monotonic clock: each call advances by `step` seconds."""

    def __init__(self, step=0.001, start=0.0):
        self._t = start
        self._step = step

    def __call__(self):
        self._t += self._step
        return self._t


system_monotonic = time.monotonic
