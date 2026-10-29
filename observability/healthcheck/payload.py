"""Strict parsing/validation of health payloads. Anything unexpected is MALFORMED."""

import json
import math

from . import MAX_PAYLOAD_BYTES, MAX_PROBES, PAYLOAD_SCHEMA
from .collector import HOST_METRICS
from .probes import KINDS, STATUSES
from .timeutil import parse_ts


class MalformedPayload(ValueError):
    pass


TOP_KEYS = {"schema", "collected_at", "expected_probes", "host", "probes"}
HOST_KEYS = {"collected_at", "disk_path", "errors"} | set(HOST_METRICS)
PROBE_KEYS = {"name", "kind", "target", "status", "detail", "latency_ms", "observed_at"}


def _no_dupes(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise MalformedPayload("duplicate key %r" % k)
        seen[k] = v
    return seen


def _reject_constant(name):
    raise MalformedPayload("non-finite number %s not allowed" % name)


def loads(raw):
    """Parse JSON bytes/str strictly (size cap, no duplicate keys, no NaN/Infinity)."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if len(raw) > MAX_PAYLOAD_BYTES:
        raise MalformedPayload("payload exceeds %d bytes" % MAX_PAYLOAD_BYTES)
    try:
        text = raw.decode("utf-8")
        return json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_reject_constant)
    except MalformedPayload:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MalformedPayload("invalid JSON: %s" % exc) from None


def _is_num(v):
    return not isinstance(v, bool) and isinstance(v, (int, float)) and math.isfinite(v)


def _keys(obj, allowed, where):
    if not isinstance(obj, dict):
        raise MalformedPayload("%s must be an object" % where)
    missing = allowed - set(obj)
    extra = set(obj) - allowed
    if missing:
        raise MalformedPayload("%s missing keys: %s" % (where, sorted(missing)))
    if extra:
        raise MalformedPayload("%s has unknown keys: %s" % (where, sorted(extra)))


def _ts(v, where):
    try:
        parse_ts(v)
    except ValueError as exc:
        raise MalformedPayload("%s: %s" % (where, exc)) from None


def validate(doc):
    """Validate structure/types only (health semantics live in decision.py)."""
    _keys(doc, TOP_KEYS, "payload")
    if doc["schema"] != PAYLOAD_SCHEMA:
        raise MalformedPayload("schema must be %r" % PAYLOAD_SCHEMA)
    _ts(doc["collected_at"], "collected_at")

    exp = doc["expected_probes"]
    if not isinstance(exp, list) or not all(isinstance(x, str) and x for x in exp):
        raise MalformedPayload("expected_probes must be a list of non-empty strings")
    if len(exp) > MAX_PROBES:
        raise MalformedPayload("expected_probes exceeds max %d" % MAX_PROBES)

    host = doc["host"]
    _keys(host, HOST_KEYS, "host")
    _ts(host["collected_at"], "host.collected_at")
    if not isinstance(host["disk_path"], str):
        raise MalformedPayload("host.disk_path must be a string")
    if not isinstance(host["errors"], list) or not all(isinstance(e, str) for e in host["errors"]):
        raise MalformedPayload("host.errors must be a list of strings")
    for k in HOST_METRICS:
        if host[k] is not None and not _is_num(host[k]):
            raise MalformedPayload("host.%s must be a finite number or null" % k)

    probes = doc["probes"]
    if not isinstance(probes, list):
        raise MalformedPayload("probes must be a list")
    if len(probes) > MAX_PROBES:
        raise MalformedPayload("probes exceeds max %d" % MAX_PROBES)
    for i, p in enumerate(probes):
        where = "probes[%d]" % i
        _keys(p, PROBE_KEYS, where)
        for k in ("name", "target", "detail"):
            if not isinstance(p[k], str):
                raise MalformedPayload("%s.%s must be a string" % (where, k))
        if p["kind"] not in KINDS:
            raise MalformedPayload("%s.kind must be one of %s" % (where, list(KINDS)))
        if p["status"] not in STATUSES:
            raise MalformedPayload("%s.status must be one of %s" % (where, list(STATUSES)))
        if not _is_num(p["latency_ms"]) or p["latency_ms"] < 0:
            raise MalformedPayload("%s.latency_ms must be a non-negative number" % where)
        _ts(p["observed_at"], "%s.observed_at" % where)
    return doc
