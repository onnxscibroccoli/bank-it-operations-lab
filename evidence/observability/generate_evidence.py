#!/usr/bin/env python3
"""Generate (or --verify) an offline evidence run for observability/.

  python3 evidence/observability/generate_evidence.py
  python3 evidence/observability/generate_evidence.py --verify evidence/observability/runs/<RUN_LABEL>

Local only: runs the unittest suite and evaluates every fixture with the fixed clock recorded in
observability/fixtures/EXPECTED.json. No network, no cloud, no production endpoints.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OBS = os.path.join(ROOT, "observability")
RUNS = os.path.join(ROOT, "evidence", "observability", "runs")
PY = "python3"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utc(dt=None):
    return (dt or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def input_files():
    out = []
    for base, _, files in os.walk(OBS):
        if "__pycache__" in base:
            continue
        out += [os.path.relpath(os.path.join(base, f), ROOT) for f in files if not f.endswith(".pyc")]
    out.append("evidence/observability/generate_evidence.py")
    return sorted(out)


def write_sums(run_dir):
    rows = []
    for base, _, files in os.walk(run_dir):
        for f in files:
            rel = os.path.relpath(os.path.join(base, f), run_dir)
            if rel != "SHA256SUMS":
                rows.append("%s  %s" % (sha256(os.path.join(run_dir, rel)), rel))
    with open(os.path.join(run_dir, "SHA256SUMS"), "w") as fh:
        fh.write("\n".join(sorted(rows, key=lambda r: r[66:])) + "\n")


def verify(run_dir):
    ok = True
    with open(os.path.join(run_dir, "SHA256SUMS")) as fh:
        for line in fh:
            digest, rel = line.rstrip("\n").split("  ", 1)
            p = os.path.join(run_dir, rel)
            good = os.path.exists(p) and sha256(p) == digest
            ok &= good
            print("%s  %s" % ("OK  " if good else "FAIL", rel))
    with open(os.path.join(run_dir, "SUMMARY.json")) as fh:
        summary = json.load(fh)
    for rel, digest in sorted(summary["inputHashes"].items()):
        p = os.path.join(ROOT, rel)
        good = os.path.exists(p) and sha256(p) == digest
        ok &= good
        print("%s  input %s" % ("OK  " if good else "DRIFT", rel))
    print("VERIFY", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify")
    ap.add_argument("--allow-dirty", action="store_true")
    args = ap.parse_args()
    if args.verify:
        return verify(args.verify)

    dirty = git("status", "--porcelain", "--", "observability", "evidence/observability/generate_evidence.py")
    if dirty and not args.allow_dirty:
        print("refusing: observability/ has uncommitted changes:\n" + dirty, file=sys.stderr)
        return 2

    started = datetime.now(timezone.utc)
    label = "local-offline-" + started.strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join(RUNS, label)
    rel_run = os.path.relpath(run_dir, ROOT)
    os.makedirs(os.path.join(run_dir, "logs"))
    os.makedirs(os.path.join(run_dir, "results"))
    with open(os.path.join(OBS, "fixtures", "EXPECTED.json")) as fh:
        expected = json.load(fh)

    steps = [("python_version", "env", 0, [PY, "--version"]),
             ("unit_tests", "test", 0, [PY, "-m", "unittest", "discover", "-s", "observability/tests", "-v"])]
    for name in sorted(expected["cases"]):
        stem = name[:-5]
        steps.append(("fixture_" + stem.replace("-", "_"), "fixture", expected["cases"][name]["exit"],
                      [PY, "observability/run_healthcheck.py", "evaluate", "observability/fixtures/" + name,
                       "--now", expected["now"], "--out", "%s/results/%s.result.json" % (rel_run, stem),
                       "--log-file", "%s/results/%s.log.jsonl" % (rel_run, stem)]))

    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1",
           "LC_ALL": "C.UTF-8"}  # minimal env: nothing personal is passed to child processes
    records = []
    for i, (step, kind, exp, cmd) in enumerate(steps, 1):
        log_rel = "logs/%02d_%s.log" % (i, step)
        t0, st = time.monotonic(), utc()
        p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
        ms = int((time.monotonic() - t0) * 1000)
        with open(os.path.join(run_dir, log_rel), "w") as fh:
            fh.write("$ %s\n%s%s\n[exit_code=%d expected=%d]\n" % (" ".join(cmd), p.stdout, p.stderr,
                                                                  p.returncode, exp))
        records.append({"seq": i, "step": step, "kind": kind, "expectedExit": exp,
                        "exitCode": p.returncode, "result": "PASS" if p.returncode == exp else "FAIL",
                        "startedUtc": st, "durationMs": ms, "log": log_rel, "command": " ".join(cmd)})

    fixture_results = {}
    for name, case in sorted(expected["cases"].items()):
        with open(os.path.join(run_dir, "results", name[:-5] + ".result.json")) as fh:
            r = json.load(fh)
        failed = sorted(c["check"] for c in r["checks"] if c["status"] != "PASS")
        match = (r["overall"] == case["overall"] and r["exit_code"] == case["exit"]
                 and failed == sorted(case["failed_checks"]))
        fixture_results[name] = {"overall": r["overall"], "exitCode": r["exit_code"],
                                 "httpStatus": r["endpoint_decision"]["http_status"],
                                 "failedChecks": failed, "matchesExpected": match}

    all_pass = all(r["result"] == "PASS" for r in records) and all(
        v["matchesExpected"] for v in fixture_results.values())
    summary = {
        "schema": "bank-it-lab/observability/evidence-summary/v1",
        "runLabel": label, "offline": True, "productionChanges": False, "network": False,
        "git": {"branch": git("rev-parse", "--abbrev-ref", "HEAD"), "commitSha": git("rev-parse", "HEAD"),
                "dirty": bool(dirty)},
        "startedUtc": utc(started), "finishedUtc": utc(), "fixedEvaluationClock": expected["now"],
        "python": sys.version.split()[0],
        "inputHashes": {f: sha256(os.path.join(ROOT, f)) for f in input_files()},
        "commands": records, "fixtures": fixture_results,
        "overall": "PASS" if all_pass else "FAIL",
    }
    with open(os.path.join(run_dir, "SUMMARY.json"), "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(run_dir, "COMMANDS.tsv"), "w") as fh:
        fh.write("seq\tstep_id\tkind\texpected_exit\texit_code\tresult\tstarted_utc\tduration_ms\tlog\tcommand\n")
        for r in records:
            fh.write("%(seq)d\t%(step)s\t%(kind)s\t%(expectedExit)d\t%(exitCode)d\t%(result)s\t"
                     "%(startedUtc)s\t%(durationMs)d\t%(log)s\t%(command)s\n" % r)
    md = ["# Observability evidence: %s" % label, "",
          "Offline/local only. No network, no cloud calls, no production endpoint or routing changes.", "",
          "- commit: `%s` (branch `%s`)" % (summary["git"]["commitSha"], summary["git"]["branch"]),
          "- started: %s, fixed evaluation clock: %s" % (summary["startedUtc"], expected["now"]),
          "- overall: **%s**" % summary["overall"], "",
          "| fixture | overall | exit | HTTP | failed checks | matches expected |",
          "|---|---|---|---|---|---|"]
    for n, v in fixture_results.items():
        md.append("| %s | %s | %d | %d | %s | %s |" % (n, v["overall"], v["exitCode"], v["httpStatus"],
                                                      ", ".join(v["failedChecks"]) or "-",
                                                      "yes" if v["matchesExpected"] else "NO"))
    md += ["", "| # | step | expected | exit | result |", "|---|---|---|---|---|"]
    md += ["| %(seq)d | %(step)s | %(expectedExit)d | %(exitCode)d | %(result)s |" % r for r in records]
    with open(os.path.join(run_dir, "SUMMARY.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")
    write_sums(run_dir)
    print("%s %s" % (summary["overall"], rel_run))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
