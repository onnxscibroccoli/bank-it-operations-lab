"""Host health snapshot (stdlib only, no personal data).

Collected: 1-minute load average, CPU count, disk total/free bytes for ONE configured
mount path, available-memory ratio and uptime seconds. Deliberately NOT collected:
usernames, environment variables, process lists or arguments, home directories,
hostnames, IP addresses, or file contents other than /proc/meminfo and /proc/uptime.

Every reader is injectable so tests never touch the real host. A reader that fails
yields a null metric plus an error string; the decision layer treats null as UNHEALTHY.
"""

import os
import shutil

from .timeutil import format_ts, system_clock

HOST_METRICS = ("load_avg_1m", "cpu_count", "disk_total_bytes", "disk_free_bytes",
                "mem_available_ratio", "uptime_s")


def _read_text(path, max_bytes=16384):
    with open(path, "r", encoding="ascii", errors="replace") as fh:
        return fh.read(max_bytes)


def read_meminfo_ratio(read_text=_read_text):
    fields = {}
    for line in read_text("/proc/meminfo").splitlines():
        name, _, rest = line.partition(":")
        parts = rest.split()
        if parts and parts[0].isdigit():
            fields[name.strip()] = int(parts[0])
    total, avail = fields.get("MemTotal"), fields.get("MemAvailable")
    if not total or avail is None:
        raise ValueError("MemTotal/MemAvailable not found")
    return round(avail / total, 4)


def read_uptime(read_text=_read_text):
    return round(float(read_text("/proc/uptime").split()[0]), 1)


def default_readers(disk_path="/"):
    return {
        "load_avg_1m": lambda: round(os.getloadavg()[0], 2),
        "cpu_count": lambda: os.cpu_count(),
        "disk": lambda: shutil.disk_usage(disk_path),
        "mem_available_ratio": read_meminfo_ratio,
        "uptime_s": read_uptime,
    }


def collect_host(readers=None, clock=system_clock, logger=None, disk_path="/"):
    """Return a host snapshot dict matching the payload `host` schema."""
    readers = readers if readers is not None else default_readers(disk_path)
    snap = {"collected_at": format_ts(clock()), "disk_path": disk_path, "errors": []}
    for key in HOST_METRICS:
        snap[key] = None

    def _try(name, fn):
        try:
            return fn(), None
        except Exception as exc:  # fail closed: record, never raise
            return None, "%s: %s" % (name, type(exc).__name__)

    for key in ("load_avg_1m", "cpu_count", "mem_available_ratio", "uptime_s"):
        fn = readers.get(key)
        if fn is None:
            snap["errors"].append("%s: reader missing" % key)
            continue
        val, err = _try(key, fn)
        snap[key] = val
        if err:
            snap["errors"].append(err)

    disk_fn = readers.get("disk")
    if disk_fn is None:
        snap["errors"].append("disk: reader missing")
    else:
        usage, err = _try("disk", disk_fn)
        if err:
            snap["errors"].append(err)
        else:
            snap["disk_total_bytes"] = int(usage[0])
            snap["disk_free_bytes"] = int(usage[2])

    if logger is not None:
        logger.info("host.collected", metrics_ok=sum(snap[k] is not None for k in HOST_METRICS),
                    metrics_total=len(HOST_METRICS), errors=snap["errors"])
    return snap
