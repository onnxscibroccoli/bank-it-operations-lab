"""Command-line entry point.

  python3 -m healthcheck evaluate PAYLOAD.json [--now TS] [--policy P.json] [--out R.json] [--log-file L.jsonl]
  python3 -m healthcheck collect  --config C.json [--payload-out P.json] [--out R.json] [--log-file L.jsonl]
  python3 -m healthcheck host     [--disk-path /]

(run with PYTHONPATH=observability from the repo root, or `cd observability` first)

Exit codes: 0 HEALTHY, 1 UNHEALTHY, 2 malformed input / config / internal error (also UNHEALTHY).
Result JSON goes to stdout (or --out); JSON-lines logs go to stderr (or --log-file).
"""

import argparse
import hashlib
import json
import sys

from . import EXIT_HEALTHY, EXIT_MALFORMED, EXIT_UNHEALTHY, MAX_PAYLOAD_BYTES, PAYLOAD_SCHEMA
from .collector import HOST_METRICS, collect_host
from .decision import PolicyError, decide, make_policy, malformed_result
from .jsonlog import JsonLineLogger
from .payload import MalformedPayload, loads, validate
from .probes import ProbeConfigError, probe_from_config, run_probes
from .timeutil import fixed_clock, format_ts, system_clock, system_monotonic

CONFIG_KEYS = {"disk_path", "expected_probes", "probes", "policy"}


def _dump(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def _write(path, text, stdout):
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        stdout.write(text)


def _read_bytes(path):
    with open(path, "rb") as fh:
        data = fh.read(MAX_PAYLOAD_BYTES + 1)
    if len(data) > MAX_PAYLOAD_BYTES:
        raise MalformedPayload("file exceeds %d bytes" % MAX_PAYLOAD_BYTES)
    return data


def _load_policy(path):
    if not path:
        return make_policy()
    doc = loads(_read_bytes(path))
    if not isinstance(doc, dict):
        raise PolicyError("policy file must be a JSON object")
    return make_policy(doc)


def _finish(result, args, stdout, log):
    log.log("INFO" if result["overall"] == "HEALTHY" else "ERROR", "health.decision",
            overall=result["overall"], exit_code=result["exit_code"],
            http_status=result["endpoint_decision"]["http_status"],
            failed_checks=[c["check"] for c in result["checks"] if c["status"] != "PASS"])
    _write(args.out, _dump(result), stdout)
    return result["exit_code"]


def cmd_evaluate(args, stdout, log, clock):
    now = clock()
    try:
        policy = _load_policy(args.policy)
    except (OSError, MalformedPayload, PolicyError) as exc:
        return _finish(malformed_result(now, "policy: %s" % exc), args, stdout, log)
    try:
        raw = _read_bytes(args.payload)
        log.info("payload.loaded", source=args.payload, bytes=len(raw),
                 sha256=hashlib.sha256(raw).hexdigest())
        doc = validate(loads(raw))
    except OSError as exc:
        return _finish(malformed_result(now, "cannot read payload: %s" % type(exc).__name__, policy),
                       args, stdout, log)
    except MalformedPayload as exc:
        log.error("payload.malformed", reason=str(exc))
        return _finish(malformed_result(now, str(exc), policy), args, stdout, log)
    return _finish(decide(doc, now, policy), args, stdout, log)


def _load_config(path, transports):
    cfg = loads(_read_bytes(path))
    if not isinstance(cfg, dict):
        raise ProbeConfigError("config must be a JSON object")
    extra = set(cfg) - CONFIG_KEYS
    if extra:
        raise ProbeConfigError("unknown config keys: %s" % sorted(extra))
    probes_cfg = cfg.get("probes", [])
    if not isinstance(probes_cfg, list):
        raise ProbeConfigError("probes must be a list")
    probes = [probe_from_config(p, transports) for p in probes_cfg]
    expected = cfg.get("expected_probes", [p.name for p in probes])
    disk_path = cfg.get("disk_path", "/")
    if not isinstance(disk_path, str):
        raise ProbeConfigError("disk_path must be a string")
    return probes, expected, disk_path, make_policy(cfg.get("policy"))


def cmd_collect(args, stdout, log, clock, monotonic, transports, host_readers):
    now = clock()
    try:
        probes, expected, disk_path, policy = _load_config(args.config, transports)
        log.info("config.loaded", probes=len(probes), expected=len(expected))
        host = collect_host(readers=host_readers, clock=clock, logger=log, disk_path=disk_path)
        results = run_probes(probes, clock=clock, monotonic=monotonic, logger=log)
    except (OSError, MalformedPayload, ProbeConfigError, PolicyError) as exc:
        log.error("config.invalid", reason=str(exc))
        return _finish(malformed_result(now, "config: %s" % exc), args, stdout, log)
    payload = {"schema": PAYLOAD_SCHEMA, "collected_at": format_ts(clock()),
               "expected_probes": list(expected), "host": host, "probes": results}
    if args.payload_out:
        _write(args.payload_out, _dump(payload), stdout)
    try:  # round-trip through the strict validator so collect and evaluate agree exactly
        doc = validate(loads(json.dumps(payload)))
    except MalformedPayload as exc:
        return _finish(malformed_result(now, str(exc), policy), args, stdout, log)
    return _finish(decide(doc, clock(), policy), args, stdout, log)


def cmd_host(args, stdout, log, clock, host_readers):
    snap = collect_host(readers=host_readers, clock=clock, logger=log, disk_path=args.disk_path)
    stdout.write(_dump(snap))
    ok = all(snap[k] is not None for k in HOST_METRICS) and not snap["errors"]
    return EXIT_HEALTHY if ok else EXIT_UNHEALTHY


def build_parser():
    ap = argparse.ArgumentParser(prog="healthcheck", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    ev = sub.add_parser("evaluate", help="evaluate a recorded payload (offline)")
    ev.add_argument("payload")
    ev.add_argument("--now", help="fixed evaluation time, e.g. 2026-10-28T12:01:00Z")
    ev.add_argument("--policy")
    ev.add_argument("--out")
    ev.add_argument("--log-file")
    co = sub.add_parser("collect", help="collect host metrics + run probes from a config")
    co.add_argument("--config", required=True)
    co.add_argument("--payload-out")
    co.add_argument("--out")
    co.add_argument("--log-file")
    ho = sub.add_parser("host", help="print a host snapshot only (no probes)")
    ho.add_argument("--disk-path", default="/")
    ho.add_argument("--log-file")
    return ap


def main(argv=None, stdout=None, stderr=None, clock=None, monotonic=None, transports=None,
         host_readers=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        return EXIT_MALFORMED if exc.code else EXIT_HEALTHY
    if clock is None:
        try:
            clock = fixed_clock(args.now) if getattr(args, "now", None) else system_clock
        except ValueError as exc:
            stderr.write("invalid --now: %s\n" % exc)
            return EXIT_MALFORMED
    monotonic = monotonic or system_monotonic
    log_fh = open(args.log_file, "w", encoding="utf-8") if getattr(args, "log_file", None) else None
    log = JsonLineLogger(log_fh or stderr, clock=clock)
    try:
        if args.cmd == "evaluate":
            return cmd_evaluate(args, stdout, log, clock)
        if args.cmd == "collect":
            return cmd_collect(args, stdout, log, clock, monotonic, transports, host_readers)
        return cmd_host(args, stdout, log, clock, host_readers)
    except Exception as exc:  # fail closed on anything unexpected
        log.error("internal.error", reason=type(exc).__name__)
        if args.cmd != "host":
            _write(getattr(args, "out", None),
                   _dump(malformed_result(clock(), "internal error: %s" % type(exc).__name__)), stdout)
        return EXIT_MALFORMED
    finally:
        if log_fh:
            log_fh.close()

