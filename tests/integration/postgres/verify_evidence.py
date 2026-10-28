#!/usr/bin/env python3
"""Independently verify a harness-v2 evidence run directory (stdlib only).

Usage: verify_evidence.py <run_dir> [--require-artifacts]

Exit 0 only if:
  * the run is not marked HISTORICAL in STATUS.json,
  * SHA256SUMS matches and covers every file (artifacts/ excluded; checked via ARTIFACTS.sha256),
  * every case in EXPECTATIONS.tsv has exactly one COMMANDS.tsv row, and no undeclared rows exist,
  * every row is PASS, and PASS is re-derived from the log itself: exit code agrees with `expect`
    and the declared reason_regex is found in the command's own output (never the command line),
  * SUMMARY.json says PASS with the same case count.
Exit 3 for historical runs, 1 for any other problem.
"""
import hashlib, json, os, re, sys

HEADER = ["seq", "step_id", "kind", "expected", "exit_code", "result", "class", "started_utc",
          "duration_ms", "log", "reason_regex", "command"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def log_output(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"^# --- output ---\n(.*?)^# --- end output ---$", text, re.S | re.M)
    rc = re.search(r"^# exit_code=(\d+)", text, re.M)
    return (m.group(1) if m else None), (int(rc.group(1)) if rc else None)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    require_artifacts = "--require-artifacts" in sys.argv
    if len(args) != 1:
        print(__doc__); return 2
    d = args[0]
    errs = []
    st = os.path.join(d, "STATUS.json")
    if os.path.exists(st):
        s = json.load(open(st))
        if str(s.get("status", "")).startswith("HISTORICAL"):
            print(f"{d}: {s['status']} - not counted as a passing run: {s.get('reason', '')}")
            return 3

    # hashes
    sums = os.path.join(d, "SHA256SUMS")
    listed = {}
    if not os.path.exists(sums):
        errs.append("SHA256SUMS missing")
    else:
        for line in open(sums):
            h, _, name = line.rstrip("\n").partition("  ")
            listed[name] = h
        for name, h in listed.items():
            p = os.path.join(d, name)
            if not os.path.exists(p):
                errs.append(f"hash: listed file missing: {name}")
            elif sha256(p) != h:
                errs.append(f"hash: mismatch: {name}")
        for root, _, files in os.walk(d):
            for fn in files:
                rel = os.path.relpath(os.path.join(root, fn), d)
                if rel == "SHA256SUMS" or rel.startswith("artifacts" + os.sep):
                    continue
                if rel not in listed:
                    errs.append(f"hash: file not covered by SHA256SUMS: {rel}")
    adir = os.path.join(d, "artifacts")
    asums = os.path.join(d, "ARTIFACTS.sha256")
    if os.path.isdir(adir) and os.path.exists(asums):
        for line in open(asums):
            h, _, name = line.rstrip("\n").partition("  ")
            p = os.path.join(adir, name)
            if not os.path.exists(p) or sha256(p) != h:
                errs.append(f"artifact hash mismatch or missing: {name}")
        print("artifacts: checked against ARTIFACTS.sha256")
    elif require_artifacts:
        errs.append("artifacts/ or ARTIFACTS.sha256 missing but --require-artifacts given")
    else:
        print("artifacts: NOT CHECKED (artifacts/ not present; dumps live in the CI artifact)")

    # expectations vs commands
    exp = {}
    try:
        for i, line in enumerate(open(os.path.join(d, "EXPECTATIONS.tsv"))):
            if i == 0 or not line.strip():
                continue
            c = line.rstrip("\n").split("\t")
            exp[c[0]] = {"kind": c[1], "expect": c[2], "regex": "" if c[5] == "-" else c[5]}
    except FileNotFoundError:
        errs.append("EXPECTATIONS.tsv missing")
    rows = []
    try:
        lines = open(os.path.join(d, "COMMANDS.tsv")).read().splitlines()
        if lines[0].split("\t") != HEADER:
            errs.append("COMMANDS.tsv header mismatch")
        for ln in lines[1:]:
            c = ln.split("\t")
            if len(c) != len(HEADER):
                errs.append(f"COMMANDS.tsv malformed row: {ln[:80]}")
                continue
            rows.append(dict(zip(HEADER, c)))
    except FileNotFoundError:
        errs.append("COMMANDS.tsv missing")
    seen = {}
    for r in rows:
        seen.setdefault(r["step_id"], []).append(r)
    for sid in seen:
        if sid not in exp:
            errs.append(f"{sid}: row for undeclared case")
    for sid, e in exp.items():
        rs = seen.get(sid, [])
        if len(rs) != 1:
            errs.append(f"{sid}: expected exactly 1 row, found {len(rs)}")
            continue
        r = rs[0]
        if r["result"] != "PASS":
            errs.append(f"{sid}: result {r['result']}/{r['class']}")
            continue
        lp = os.path.join(d, r["log"])
        if not os.path.exists(lp):
            errs.append(f"{sid}: log missing {r['log']}"); continue
        out, rc = log_output(lp)
        if out is None or rc is None:
            errs.append(f"{sid}: log has no output section or exit code"); continue
        if str(rc) != r["exit_code"]:
            errs.append(f"{sid}: TSV exit_code {r['exit_code']} != log exit_code {rc}")
        if e["expect"] == "zero" and rc != 0:
            errs.append(f"{sid}: expected exit 0, log shows {rc}")
        if e["expect"] == "nonzero" and rc == 0:
            errs.append(f"{sid}: expected failure but command SUCCEEDED (unexpected success)")
        if e["kind"] == "negative" and not e["regex"]:
            errs.append(f"{sid}: negative case without declared reason")
        if e["regex"] and not re.search(e["regex"], out, re.M):
            errs.append(f"{sid}: reason_regex not found in log output: {e['regex']}")
    try:
        s = json.load(open(os.path.join(d, "SUMMARY.json")))
        if s.get("overall") != "PASS":
            errs.append(f"SUMMARY.json overall={s.get('overall')}")
        if s.get("expected_cases") != len(exp):
            errs.append(f"SUMMARY.json expected_cases={s.get('expected_cases')} != {len(exp)}")
    except FileNotFoundError:
        errs.append("SUMMARY.json missing")

    neg = sum(1 for e in exp.values() if e["kind"] == "negative")
    pos = sum(1 for e in exp.values() if e["kind"] == "positive")
    for e in errs:
        print("ERROR", e)
    print(f"{d}: cases={len(exp)} positive={pos} negative={neg} rows={len(rows)} problems={len(errs)} -> "
          + ("VERIFIED" if not errs else "REJECTED"))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
