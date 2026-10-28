"""Structured JSON-lines logging with a privacy allow-list.

Every record is one JSON object per line with sorted keys. Field values are limited to
JSON scalars (and short lists of scalars). Keys that commonly carry personal or host-user
data are refused outright so they can never be emitted by accident.
"""

import json

from .timeutil import format_ts, system_clock

FORBIDDEN_KEYS = frozenset({
    "user", "username", "login", "uid", "gid", "home", "homedir", "cwd", "env",
    "environ", "environment", "argv", "args", "cmdline", "pid", "ppid", "process",
    "processes", "hostname", "fqdn", "email", "password", "token", "secret",
})
_MAX_STR = 300
_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


def _clean(value):
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value if len(value) <= _MAX_STR else value[:_MAX_STR] + "...[truncated]"
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in list(value)[:50]]
    raise TypeError("log field values must be JSON scalars or lists of scalars")


class JsonLineLogger:
    def __init__(self, stream, clock=system_clock, component="healthcheck"):
        self._stream = stream
        self._clock = clock
        self._component = component
        self.records = []

    def log(self, level, event, **fields):
        if level not in _LEVELS:
            raise ValueError("unknown log level %r" % level)
        bad = sorted(k for k in fields if k.lower() in FORBIDDEN_KEYS)
        if bad:
            raise ValueError("refusing to log privacy-sensitive keys: %s" % ", ".join(bad))
        rec = {"ts": format_ts(self._clock()), "level": level, "component": self._component,
               "event": event}
        for k, v in fields.items():
            rec[k] = _clean(v)
        self.records.append(rec)
        if self._stream is not None:
            self._stream.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
            self._stream.flush()
        return rec

    def info(self, event, **f):
        return self.log("INFO", event, **f)

    def warning(self, event, **f):
        return self.log("WARNING", event, **f)

    def error(self, event, **f):
        return self.log("ERROR", event, **f)
