#!/usr/bin/env python3
"""Fail-closed PLAN_ONLY assertions for plan and evidence records (M365 module and any other PLAN_ONLY producer).

  check_plan_only.py report FILE [--min-plan-steps N]   one engine report (e.g. m365_ops.py --json-out)
  check_plan_only.py run DIR                            one evidence run (validation-report.json + SUMMARY.json)

Rules (all must hold; exit 1 otherwise, exit 2 on unreadable input):
  R1 the top-level object has mutationsExecuted == 0 (an int, not a bool, not missing)
  R2 every "mutationsExecuted" key anywhere is int 0
  R3 every "executed" key anywhere is exactly false (not "false", not 0, not null)
  R4 every element of every "plan" list is an object with mode == "PLAN_ONLY" and executed == false
  R5 at least N plan steps exist (a report with no plan steps cannot demonstrate the property; default N=1 for reports)
Standard library only. Values are data; nothing is executed.
"""
import argparse, json, sys
from pathlib import Path


def _walk(o, path, errs, steps):
    if isinstance(o, dict):
        for k, v in o.items():
            p = f"{path}.{k}"
            if k == "mutationsExecuted" and not (type(v) is int and v == 0):
                errs.append(f"R2 {p} = {v!r} (must be integer 0)")
            if k == "executed" and v is not False:
                errs.append(f"R3 {p} = {v!r} (must be false)")
            if k == "plan":
                if not isinstance(v, list):
                    errs.append(f"R4 {p} is not a list")
                else:
                    for i, s in enumerate(v):
                        sp = f"{p}[{i}]"
                        steps.append(sp)
                        if not isinstance(s, dict):
                            errs.append(f"R4 {sp} is not an object")
                            continue
                        if s.get("mode") != "PLAN_ONLY":
                            errs.append(f"R4 {sp}.mode = {s.get('mode')!r} (must be PLAN_ONLY)")
                        if "executed" not in s:
                            errs.append(f"R4 {sp}.executed missing (must be false)")
            _walk(v, p, errs, steps)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            _walk(v, f"{path}[{i}]", errs, steps)


def check_obj(obj, name, min_steps):
    errs, steps = [], []
    if not isinstance(obj, dict):
        return [f"{name}: top level is not an object"], 0
    if "mutationsExecuted" not in obj:
        errs.append(f"{name}: R1 top-level mutationsExecuted missing")
    _walk(obj, "$", errs, steps)
    if len(steps) < min_steps:
        errs.append(f"{name}: R5 {len(steps)} plan step(s), need at least {min_steps}")
    return [e if e.startswith(name) else f"{name}: {e}" for e in errs], len(steps)


def load(path):
    def no_dupes(pairs):
        keys = [k for k, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate key")
        return dict(pairs)
    return json.loads(Path(path).read_text(), object_pairs_hook=no_dupes,
                      parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("file")
    r.add_argument("--min-plan-steps", type=int, default=1)
    d = sub.add_parser("run")
    d.add_argument("dir")
    a = ap.parse_args(argv)
    targets = []
    if a.cmd == "report":
        targets = [(a.file, a.min_plan_steps)]
    else:
        run = Path(a.dir)
        targets = [(str(run / "validation-report.json"), 1), (str(run / "SUMMARY.json"), 0)]
    errs, total = [], 0
    for f, n in targets:
        try:
            obj = load(f)
        except (OSError, ValueError) as e:
            print(f"PLAN_ONLY CHECK ERROR: {f}: {e}")
            return 2
        e, steps = check_obj(obj, f, n)
        errs += e
        total += steps
    for e in errs:
        print("VIOLATION " + e)
    if errs:
        print(f"PLAN_ONLY CHECK FAILED: {len(errs)} violation(s)")
        return 1
    print(f"PLAN_ONLY OK: {total} plan step(s), all PLAN_ONLY/executed=false, mutationsExecuted=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
