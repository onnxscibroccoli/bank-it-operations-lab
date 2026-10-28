#!/usr/bin/env python3
"""Shared, read-only evidence checks for bank-it-operations-lab (stdlib only).

Subcommands (exit 0 = no errors, 1 = errors, 2 = usage):
  hashes <sums-file> [--base DIR] [--cover DIR ...]
      Recompute every sha256sum(1) line. Errors: malformed line, missing file, mismatch,
      the sums file listing itself (a file cannot hash itself). With --cover, files under
      those directories that are not listed are reported as UNCOVERED (warning), so a
      reviewer can see what the hashes do not vouch for.
  commands <tsv> --format aws-3col|postgres-10col
      Cross-check every COMMANDS.tsv row against its log's exit-code trailer, flag logs
      with no row (orphans), and for postgres-10col check expected/result consistency.
  postgres-negatives <run-dir> [--expectations FILE]
      For every negative step recorded as PASS, require the log to contain the error text
      that proves the intended failure. Otherwise: FALSE-PASS (error).
  cfn-s3-selflog <template.json>
      Error if any AWS::S3::Bucket sends server access logs to itself (LoggingConfiguration
      with no DestinationBucketName, or a DestinationBucketName that refers to the same
      logical id). AWS: delivering logs to the source bucket causes an infinite loop of logs.
  manifest <MANIFEST.json> [--schema FILE]
      Minimal structural check of a bundle manifest against evidence-manifest.schema.json
      (required keys, enums, patterns, additionalProperties). Use a full JSON Schema
      validator in CI if one is available; this keeps the check dependency-free.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def finish(self, ok_msg: str) -> int:
        for w in self.warnings:
            print(f"WARN  {w}")
        for e in self.errors:
            print(f"ERROR {e}")
        print(ok_msg if not self.errors else f"INVALID ({len(self.errors)} errors, {len(self.warnings)} warnings)")
        return 0 if not self.errors else 1


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


SUM_LINE = re.compile(r"^([0-9a-f]{64}) [ *](.+)$")


def cmd_hashes(a: argparse.Namespace) -> int:
    r = Report()
    sums = Path(a.sums).resolve()
    base = Path(a.base).resolve() if a.base else sums.parent
    listed: set[Path] = set()
    lines = [l for l in sums.read_text().splitlines() if l.strip()]
    if not lines:
        r.err(f"{a.sums}: empty")
    for n, line in enumerate(lines, 1):
        m = SUM_LINE.match(line)
        if not m:
            r.err(f"{a.sums}:{n}: malformed line")
            continue
        target = (base / m.group(2)).resolve()
        listed.add(target)
        if target == sums:
            r.err(f"{a.sums}:{n}: lists itself (self-hash is impossible to keep valid)")
        elif not target.is_file():
            r.err(f"{a.sums}:{n}: missing file {m.group(2)}")
        elif sha256(target) != m.group(1):
            r.err(f"{a.sums}:{n}: sha256 mismatch for {m.group(2)}")
    for cover in a.cover or []:
        for root, _dirs, files in os.walk(cover):
            for name in files:
                p = Path(root, name).resolve()
                if p != sums and p not in listed:
                    r.warn(f"UNCOVERED {os.path.relpath(p)} (not vouched for by {a.sums})")
    return r.finish(f"HASHES OK: {len(lines)} entries verified")


AWS_TRAILER = re.compile(r"^# exit_code: (-?\d+)$", re.M)
PG_TRAILER = re.compile(r"^# exit_code=(-?\d+) ", re.M)


def cmd_commands(a: argparse.Namespace) -> int:
    r = Report()
    tsv = Path(a.tsv)
    rows = [l for l in tsv.read_text().split("\n") if l]
    seen: set[str] = set()
    if a.format == "aws-3col":
        log_dir, trailer, ncol, start = tsv.parent, AWS_TRAILER, 3, 0
    else:
        log_dir, trailer, ncol, start = tsv.parent, PG_TRAILER, 10, 1
        if not rows or not rows[0].startswith("seq\tstep_id"):
            r.err(f"{tsv}: missing header row")
    for n, row in enumerate(rows[start:], start + 1):
        cols = row.split("\t")
        if len(cols) != ncol:
            r.err(f"{tsv}:{n}: expected {ncol} fields, got {len(cols)}")
            continue
        if a.format == "aws-3col":
            log, code = cols[0], cols[1]
        else:
            log, code = cols[8], cols[4]
            expect, result = cols[3], cols[5]
            ok = (expect == "zero" and code == "0") or (expect == "nonzero" and code not in ("0", ""))
            if (result == "PASS") != ok:
                r.err(f"{tsv}:{n}: result {result} inconsistent with expect={expect} exit={code}")
        seen.add(log)
        lp = log_dir / log
        if not lp.is_file():
            r.err(f"{tsv}:{n}: log {log} missing")
            continue
        found = trailer.findall(lp.read_text(errors="replace"))
        if not found:
            r.err(f"{log}: no exit-code trailer")
        elif found[-1] != code:
            r.err(f"{log}: trailer exit {found[-1]} != TSV exit {code}")
    log_root = log_dir
    pattern = "*.log" if a.format == "aws-3col" else "logs/*.log"
    for p in sorted(log_root.glob(pattern)):
        rel = p.name if a.format == "aws-3col" else f"logs/{p.name}"
        if rel not in seen:
            r.warn(f"ORPHAN log {rel} has no COMMANDS.tsv row")
    return r.finish(f"COMMANDS OK: {len(rows) - start} rows cross-checked")


def cmd_pg_neg(a: argparse.Namespace) -> int:
    # Columns are located by header name so both harness v1 (10 columns) and harness v2 (12 columns:
    # adds `class` and `reason_regex`) COMMANDS.tsv layouts are understood. A run with zero negative
    # steps is an ERROR, never "OK": an unrecognised layout must not pass silently.
    r = Report()
    run = Path(a.run_dir)
    exp = json.loads(Path(a.expectations).read_text())["steps"]
    lines = (run / "COMMANDS.tsv").read_text().splitlines()
    hdr = lines[0].split("\t") if lines else []
    try:
        i_step, i_kind, i_res, i_log = (hdr.index(k) for k in ("step_id", "kind", "result", "log"))
    except ValueError:
        r.err(f"COMMANDS.tsv header lacks step_id/kind/result/log: {hdr}")
        return r.finish("")
    checked = 0
    for row in lines[1:]:
        c = row.split("\t")
        if len(c) != len(hdr) or c[i_kind] != "negative":
            continue
        step, result, log = c[i_step], c[i_res], c[i_log]
        if step not in exp:
            r.warn(f"{step}: no expectation defined")
            continue
        text = (run / log).read_text(errors="replace")
        body = "\n".join(l for l in text.splitlines() if not l.startswith("# "))
        checked += 1
        if result == "PASS" and not re.search(exp[step], body, re.M):
            first = next((l for l in body.splitlines() if "error" in l.lower()), body.strip()[:120])
            r.err(f"FALSE-PASS {step}: non-zero exit but not for the intended reason; log says: {first.strip()}")
    if checked == 0:
        r.err("no negative steps found in COMMANDS.tsv (unrecognised layout or empty run)")
    return r.finish(f"NEGATIVES OK: {checked} negative steps failed for the intended reason")


def _refs(node) -> set[str]:
    out: set[str] = set()
    if isinstance(node, dict):
        if "Ref" in node and isinstance(node["Ref"], str):
            out.add(node["Ref"])
        ga = node.get("Fn::GetAtt")
        if isinstance(ga, list) and ga:
            out.add(ga[0])
        for v in node.values():
            out |= _refs(v)
    elif isinstance(node, list):
        for v in node:
            out |= _refs(v)
    return out


def cmd_cfn(a: argparse.Namespace) -> int:
    r = Report()
    t = json.loads(Path(a.template).read_text())
    n = 0
    for lid, res in (t.get("Resources") or {}).items():
        if res.get("Type") != "AWS::S3::Bucket":
            continue
        n += 1
        lc = (res.get("Properties") or {}).get("LoggingConfiguration")
        if lc is None:
            continue
        dest = lc.get("DestinationBucketName")
        if dest is None or lid in _refs(dest):
            r.err(f"{lid}: server access logs delivered to itself (prefix {lc.get('LogFilePrefix', '')!r}); "
                  "AWS: logging to the source bucket causes an infinite loop of logs")
    return r.finish(f"S3 LOGGING OK: {n} buckets checked, none log to themselves")


def _check(schema: dict, value, path: str, r: Report) -> None:
    t = schema.get("type")
    if "const" in schema and value != schema["const"]:
        r.err(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        r.err(f"{path}: {value!r} not in {schema['enum']}")
    if t == "object":
        if not isinstance(value, dict):
            r.err(f"{path}: expected object"); return
        for k in schema.get("required", []):
            if k not in value:
                r.err(f"{path}: missing required key {k}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for k in value:
                if k not in props:
                    r.err(f"{path}: unexpected key {k}")
        for k, v in value.items():
            if k in props:
                _check(props[k], v, f"{path}.{k}", r)
        cond = schema.get("if")
        if cond and all(value.get(k) == s.get("const") for k, s in cond.get("properties", {}).items()):
            for k in schema.get("then", {}).get("required", []):
                if k not in value:
                    r.err(f"{path}: missing {k} (required by conditional)")
    elif t == "array":
        if not isinstance(value, list):
            r.err(f"{path}: expected array"); return
        for i, v in enumerate(value):
            _check(schema.get("items", {}), v, f"{path}[{i}]", r)
    elif t == "string":
        if not isinstance(value, str):
            r.err(f"{path}: expected string"); return
        if "pattern" in schema and not re.search(schema["pattern"], value):
            r.err(f"{path}: {value!r} does not match {schema['pattern']}")
    elif t == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            r.err(f"{path}: expected integer")
        elif "minimum" in schema and value < schema["minimum"]:
            r.err(f"{path}: below minimum {schema['minimum']}")


def cmd_manifest(a: argparse.Namespace) -> int:
    r = Report()
    schema = json.loads(Path(a.schema).read_text())
    m = json.loads(Path(a.manifest).read_text())
    _check(schema, m, "$", r)
    if not r.errors:
        hashes_file = m["hashes"]["file"]
        if not any(e["path"] == hashes_file and e["reason"] == "self-reference" for e in m["exclusions"]):
            r.err(f"$.exclusions: hashes file {hashes_file} must be excluded with reason self-reference")
        if not m["anchors"]:
            r.warn("$.anchors: empty; bundle is self-attesting (no independent check)")
    return r.finish("MANIFEST OK")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("hashes"); s.add_argument("sums"); s.add_argument("--base"); s.add_argument("--cover", action="append")
    s.set_defaults(fn=cmd_hashes)
    s = sub.add_parser("commands"); s.add_argument("tsv"); s.add_argument("--format", required=True, choices=["aws-3col", "postgres-10col"])
    s.set_defaults(fn=cmd_commands)
    s = sub.add_parser("postgres-negatives"); s.add_argument("run_dir")
    s.add_argument("--expectations", default=str(HERE / "negative-expectations.postgres.json")); s.set_defaults(fn=cmd_pg_neg)
    s = sub.add_parser("cfn-s3-selflog"); s.add_argument("template"); s.set_defaults(fn=cmd_cfn)
    s = sub.add_parser("manifest"); s.add_argument("manifest")
    s.add_argument("--schema", default=str(HERE / "evidence-manifest.schema.json")); s.set_defaults(fn=cmd_manifest)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
