"""Fail-closed health decision.

The endpoint is HEALTHY only when every single check below passes. Everything else,
including anything we did not anticipate, is UNHEALTHY:

  * payload missing, unparseable or structurally invalid           -> UNHEALTHY (exit 2)
  * no expected probes declared                                    -> UNHEALTHY
  * an expected probe has no result (missing probe)                -> UNHEALTHY
  * a probe result that was not expected, or a duplicate result    -> UNHEALTHY
  * probe status anything other than OK (FAIL/TIMEOUT/ERROR/UNKNOWN)-> UNHEALTHY
  * probe latency above policy                                     -> UNHEALTHY
  * any timestamp older than max_age_s, or in the future > skew    -> UNHEALTHY (stale)
  * any host metric null / host collection errors                  -> UNHEALTHY
  * disk free, load per CPU or available memory outside policy     -> UNHEALTHY
"""

import copy

from . import EXIT_HEALTHY, EXIT_MALFORMED, EXIT_UNHEALTHY, RESULT_SCHEMA
from .collector import HOST_METRICS
from .timeutil import format_ts, parse_ts

DEFAULT_POLICY = {
    "max_age_s": 300,
    "max_future_skew_s": 30,
    "min_disk_free_ratio": 0.10,
    "max_load_per_cpu": 2.0,
    "min_mem_available_ratio": 0.10,
    "max_probe_latency_ms": 5000,
}


class PolicyError(ValueError):
    pass


def make_policy(overrides=None):
    pol = copy.deepcopy(DEFAULT_POLICY)
    for k, v in (overrides or {}).items():
        if k not in DEFAULT_POLICY:
            raise PolicyError("unknown policy key %r" % k)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
            raise PolicyError("policy %s must be a non-negative number" % k)
        pol[k] = v
    return pol


def _check(checks, name, ok, detail):
    checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    return ok


def _fresh(checks, name, ts, now, pol):
    age = (now - parse_ts(ts)).total_seconds()
    if age < -pol["max_future_skew_s"]:
        return _check(checks, name, False, "timestamp %s is %.0fs in the future" % (ts, -age))
    if age > pol["max_age_s"]:
        return _check(checks, name, False, "stale: age %.0fs > max_age_s %s" % (age, pol["max_age_s"]))
    return _check(checks, name, True, "age %.0fs" % age)


def decide(doc, now, policy=None):
    """Evaluate a VALIDATED payload. Returns a result dict (never raises on bad health)."""
    pol = policy or make_policy()
    checks = []

    _fresh(checks, "freshness:payload", doc["collected_at"], now, pol)
    _fresh(checks, "freshness:host", doc["host"]["collected_at"], now, pol)

    # --- host ---
    host = doc["host"]
    nulls = [k for k in HOST_METRICS if host[k] is None]
    _check(checks, "host:metrics_present", not nulls,
           "all metrics present" if not nulls else "missing: %s" % ", ".join(nulls))
    _check(checks, "host:collection_errors", not host["errors"],
           "none" if not host["errors"] else "; ".join(host["errors"]))
    total, free = host["disk_total_bytes"], host["disk_free_bytes"]
    if total is not None and free is not None:
        if total <= 0 or free < 0 or free > total:
            _check(checks, "host:disk_free_ratio", False, "inconsistent disk figures")
        else:
            r = free / total
            _check(checks, "host:disk_free_ratio", r >= pol["min_disk_free_ratio"],
                   "%.4f (min %s)" % (r, pol["min_disk_free_ratio"]))
    load, cpus = host["load_avg_1m"], host["cpu_count"]
    if load is not None and cpus is not None:
        if cpus < 1 or load < 0:
            _check(checks, "host:load_per_cpu", False, "inconsistent load/cpu figures")
        else:
            lpc = load / cpus
            _check(checks, "host:load_per_cpu", lpc <= pol["max_load_per_cpu"],
                   "%.3f (max %s)" % (lpc, pol["max_load_per_cpu"]))
    mem = host["mem_available_ratio"]
    if mem is not None:
        _check(checks, "host:mem_available_ratio",
               0 <= mem <= 1 and mem >= pol["min_mem_available_ratio"],
               "%.4f (min %s)" % (mem, pol["min_mem_available_ratio"]))

    # --- probes ---
    expected = doc["expected_probes"]
    _check(checks, "probes:expected_declared", bool(expected),
           "%d expected" % len(expected) if expected else "no expected probes declared")
    if len(set(expected)) != len(expected):
        _check(checks, "probes:expected_unique", False, "duplicate names in expected_probes")
    seen = {}
    for p in doc["probes"]:
        if p["name"] in seen:
            _check(checks, "probe:%s" % p["name"], False, "duplicate result")
            continue
        seen[p["name"]] = p
    for name in sorted(set(seen) - set(expected)):
        _check(checks, "probe:%s" % name, False, "unexpected probe result")
    for name in expected:
        p = seen.get(name)
        if p is None:
            _check(checks, "probe:%s" % name, False, "missing: no result for expected probe")
            continue
        _check(checks, "probe:%s" % name, p["status"] == "OK",
               "%s (%s) %s" % (p["status"], p["kind"], p["detail"]))
        _check(checks, "probe:%s:latency" % name, p["latency_ms"] <= pol["max_probe_latency_ms"],
               "%.1fms (max %s)" % (p["latency_ms"], pol["max_probe_latency_ms"]))
        _fresh(checks, "freshness:probe:%s" % name, p["observed_at"], now, pol)

    failed = [c for c in checks if c["status"] != "PASS"]
    healthy = bool(checks) and not failed
    return _result(now, healthy, checks, [c["check"] + ": " + c["detail"] for c in failed], pol)


def _result(now, healthy, checks, reasons, pol, malformed=False):
    if malformed:
        code = EXIT_MALFORMED
    else:
        code = EXIT_HEALTHY if healthy else EXIT_UNHEALTHY
    return {
        "schema": RESULT_SCHEMA,
        "evaluated_at": format_ts(now),
        "overall": "HEALTHY" if healthy else "UNHEALTHY",
        "endpoint_decision": {"serve": healthy, "http_status": 200 if healthy else 503},
        "exit_code": code,
        "reasons": reasons,
        "checks": checks,
        "policy": pol,
    }


def malformed_result(now, reason, policy=None):
    pol = policy or make_policy()
    chk = [{"check": "payload:valid", "status": "FAIL", "detail": reason}]
    return _result(now, False, chk, ["payload:valid: " + reason], pol, malformed=True)
