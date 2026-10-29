#!/usr/bin/env python3
"""Generate an OFFLINE / SYNTHETIC evidence run for the M365 / endpoint operations scenario engine.

Writes evidence/m365/runs/<RUN_LABEL>/:
  SUMMARY.json            structured evidence: commit SHA, timestamps, input SHA-256 hashes,
                          every command with expected + actual exit code, per-rule results
  SUMMARY.md              human-readable rendering of SUMMARY.json
  validation-report.json  scenario engine JSON report for identity/m365/scenarios (per-scenario PASS/FAIL)
  validation-report.md    markdown rendering of the same
  COMMANDS.tsv            seq, step_id, kind, expected_exit, exit_code, result, started_utc, duration_ms, log, command
  logs/NN_<step>.log      stdout/stderr of each command with an exit-code footer
  SHA256SUMS              SHA-256 of every other file in the run directory

Usage:
  python3 evidence/m365/generate_evidence.py [--label LABEL]
  python3 evidence/m365/generate_evidence.py --verify evidence/m365/runs/<LABEL>

No network, tenant, Microsoft Graph call or credential is involved. Python stdlib only.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RUNS = os.path.join(HERE, "runs")
HASHED_TREES = ("identity/m365",)
HASHED_EXTRA = ("evidence/m365/generate_evidence.py",)
DISCLAIMER = (
    "OFFLINE / SYNTHETIC EVIDENCE. Generated from local JSON scenarios in this repository. No Microsoft 365, "
    "Entra ID, Intune or Exchange Online tenant, Microsoft Graph API or credential was used, no change was "
    "executed anywhere, and nothing here describes or claims the configuration or state of any tenant."
)
PY = sys.executable or "python3"
sys.dont_write_bytecode = True


def utc_now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def classify(path):
    rel = os.path.relpath(path, ROOT)
    if rel.endswith("m365_ops.py"):
        return "engine"
    if rel.startswith("identity/m365/tenant/"):
        return "tenant-fixture"
    if rel.startswith("identity/m365/scenarios/"):
        return "scenario"
    if rel.startswith("identity/m365/tests/fixtures/"):
        return "test-fixture"
    if rel.startswith("identity/m365/tests/") and rel.endswith(".py"):
        return "test"
    if rel.startswith("evidence/m365/"):
        return "evidence-generator"
    return "doc"


def input_files():
    files = []
    for tree in HASHED_TREES:
        for dp, dns, fns in os.walk(os.path.join(ROOT, tree)):
            dns[:] = sorted(d for d in dns if d != "__pycache__")
            for fn in sorted(fns):
                if not fn.endswith(".pyc"):
                    files.append(os.path.join(dp, fn))
    files += [os.path.join(ROOT, p) for p in HASHED_EXTRA]
    return sorted(files)


def input_hashes():
    return [{"path": os.path.relpath(f, ROOT), "kind": classify(f), "sha256": sha256(f),
             "bytes": os.path.getsize(f)} for f in input_files()]


def run_step(run_dir, seq, step_id, kind, argv, expected):
    log_rel = "logs/%02d_%s.log" % (seq, step_id)
    started = utc_now()
    t0 = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, env=env)
    ms = int((time.monotonic() - t0) * 1000)
    cmd = " ".join(shlex.quote(a if a != PY else "python3") for a in argv)
    with open(os.path.join(run_dir, log_rel), "w", encoding="utf-8") as fh:
        fh.write("$ %s\n" % cmd)
        fh.write("--- stdout ---\n%s" % r.stdout)
        fh.write("--- stderr ---\n%s" % r.stderr)
        fh.write("--- exit_code=%d expected=%d started_utc=%s duration_ms=%d ---\n"
                 % (r.returncode, expected, started, ms))
    return {"seq": seq, "stepId": step_id, "kind": kind, "command": cmd, "expectedExitCode": expected,
            "exitCode": r.returncode, "result": "PASS" if r.returncode == expected else "FAIL",
            "startedUtc": started, "durationMs": ms, "log": log_rel}


def expected_for_fixture(name):
    if name.startswith("mismatch-"):
        return 1
    if name.startswith("malformed-"):
        return 2
    raise SystemExit("unclassified fixture %s" % name)


def write_sums(run_dir):
    lines = []
    for dp, dns, fns in os.walk(run_dir):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, run_dir)
            if rel != "SHA256SUMS":
                lines.append("%s  %s" % (sha256(p), rel))
    with open(os.path.join(run_dir, "SHA256SUMS"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(sorted(lines, key=lambda l: l.split("  ", 1)[1])) + "\n")


def render_md(s, report):
    L = ["# M365 / endpoint operations -- offline evidence run `%s`" % s["runLabel"], "",
         "> **%s**" % s["disclaimer"], "",
         "| Field | Value |", "|---|---|",
         "| Mode | `%s` |" % s["mode"],
         "| Tenant state claimed | `%s` |" % str(s["tenantStateClaimed"]).lower(),
         "| Mutations executed | `%d` |" % s["mutationsExecuted"],
         "| Validated commit | `%s` |" % s["git"]["commitSha"],
         "| Branch | `%s` |" % s["git"]["branch"],
         "| Scoped source tree clean at run | `%s` |" % str(s["git"]["scopedTreeClean"]).lower(),
         "| Started (UTC) | %s |" % s["startedUtc"],
         "| Finished (UTC) | %s |" % s["finishedUtc"],
         "| Python | %s |" % s["environment"]["python"],
         "| Overall | **%s** |" % s["overall"], "",
         "## Commands", "", "| # | Step | Expected exit | Exit | Result | Log |", "|---|---|---|---|---|---|"]
    for c in s["commands"]:
        L.append("| %d | `%s` | %d | %d | %s | `%s` |" % (c["seq"], c["stepId"], c["expectedExitCode"],
                                                          c["exitCode"], c["result"], c["log"]))
    L += ["", "## Scenario results (identity/m365/scenarios)", "",
          "| Scenario | Type | Verdict | Findings | Result |", "|---|---|---|---|---|"]
    for r in report["scenarios"]:
        L.append("| %s | %s | %s | %s | %s |" % (r["id"], r["type"], r["verdict"], ", ".join(r["findingCodes"]) or "-", r["result"]))
    L += ["", "## Input hashes (SHA-256)", "", "| Kind | Path | SHA-256 |", "|---|---|---|"]
    for h in s["inputHashes"]:
        L.append("| %s | `%s` | `%s` |" % (h["kind"], h["path"], h["sha256"]))
    L += ["", "Verify: `python3 evidence/m365/generate_evidence.py --verify evidence/m365/runs/%s`" % s["runLabel"]]
    return "\n".join(L) + "\n"


def generate(label):
    commit = git("rev-parse", "HEAD")
    if not commit:
        raise SystemExit("not a git checkout; refusing to generate evidence without a commit SHA")
    dirty = git("status", "--porcelain", "--", *HASHED_TREES, *HASHED_EXTRA)
    run_dir = os.path.join(RUNS, label)
    if os.path.exists(run_dir):
        raise SystemExit("run directory exists: %s" % run_dir)
    os.makedirs(os.path.join(run_dir, "logs"))
    started = utc_now()
    v = os.path.join("identity", "m365", "m365_ops.py")
    rel_run = os.path.relpath(run_dir, ROOT)
    steps = [
        ("python_version", "env", [PY, "--version"], 0),
        ("unit_tests", "test", [PY, "-m", "unittest", "discover", "-s", "identity/m365/tests", "-v"], 0),
        ("evaluate_scenarios", "engine",
         [PY, v, "--json-out", os.path.join(rel_run, "validation-report.json")], 0),
    ]
    fx = os.path.join("identity", "m365", "tests", "fixtures")
    for name in sorted(f for f in os.listdir(os.path.join(ROOT, fx)) if f.endswith(".json")):
        steps.append(("fixture_" + name[:-5].replace("-", "_"), "engine-fixture",
                      [PY, v, os.path.join(fx, name), "--quiet"], expected_for_fixture(name)))
    cmds = [run_step(run_dir, i, sid, kind, argv, exp) for i, (sid, kind, argv, exp) in enumerate(steps, 1)]
    with open(os.path.join(run_dir, "validation-report.json"), encoding="utf-8") as fh:
        report = json.load(fh)
    # Stamp provenance into the validator report (JSON + markdown) so it stands alone.
    report["provenance"] = {"commitSha": commit, "runLabel": label, "generatedUtc": utc_now(),
                            "evidence": "SUMMARY.json"}
    with open(os.path.join(run_dir, "validation-report.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(report, indent=2) + "\n")
    sys.path.insert(0, os.path.join(ROOT, "identity", "m365"))
    import m365_ops  # noqa: E402  (stdlib-only, offline)
    with open(os.path.join(run_dir, "validation-report.md"), "w", encoding="utf-8") as fh:
        fh.write(m365_ops.render_markdown(report, {
            "Validated commit": commit, "Run": label, "Generated (UTC)": report["provenance"]["generatedUtc"]}))
    overall = "PASS" if all(c["result"] == "PASS" for c in cmds) and report["overall"] == "PASS" else "FAIL"
    summary = {
        "schema": "bank-it-lab/m365-ops-offline-evidence/v1",
        "runLabel": label,
        "mode": "offline-synthetic",
        "tenantStateClaimed": False,
        "mutationsExecuted": report["mutationsExecuted"],
        "disclaimer": DISCLAIMER,
        "git": {"commitSha": commit, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "scopedTreeClean": not dirty,
                "note": "commitSha is the commit whose identity/m365 content was validated; "
                        "the evidence itself is committed on top of it. inputHashes pin the exact bytes."},
        "startedUtc": started,
        "finishedUtc": utc_now(),
        "environment": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                        "network": "not used", "credentials": "not used"},
        "overall": overall,
        "totals": {"commands": len(cmds), "passed": sum(c["result"] == "PASS" for c in cmds),
                   "failed": sum(c["result"] != "PASS" for c in cmds)},
        "validation": {"report": "validation-report.json", "reportMarkdown": "validation-report.md",
                       "overall": report["overall"], "exitCode": report["exitCode"],
                       "scenarios": [{"id": r["id"], "type": r["type"], "verdict": r["verdict"],
                                      "findingCodes": r["findingCodes"], "result": r["result"]}
                                     for r in report["scenarios"]]},
        "commands": cmds,
        "inputHashes": input_hashes(),
        "hashes": "SHA256SUMS",
    }
    with open(os.path.join(run_dir, "SUMMARY.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(summary, indent=2) + "\n")
    with open(os.path.join(run_dir, "SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(summary, report))
    with open(os.path.join(run_dir, "COMMANDS.tsv"), "w", encoding="utf-8") as fh:
        fh.write("seq\tstep_id\tkind\texpected_exit\texit_code\tresult\tstarted_utc\tduration_ms\tlog\tcommand\n")
        for c in cmds:
            fh.write("%d\t%s\t%s\t%d\t%d\t%s\t%s\t%d\t%s\t%s\n" % (
                c["seq"], c["stepId"], c["kind"], c["expectedExitCode"], c["exitCode"], c["result"],
                c["startedUtc"], c["durationMs"], c["log"], c["command"]))
    write_sums(run_dir)
    print("%s overall=%s commands=%d failed=%d commit=%s scopedTreeClean=%s"
          % (rel_run, overall, len(cmds), summary["totals"]["failed"], commit, not dirty))
    return 0 if overall == "PASS" else 1


def verify(run_dir):
    problems = []
    with open(os.path.join(run_dir, "SHA256SUMS"), encoding="utf-8") as fh:
        for line in fh:
            digest, rel = line.rstrip("\n").split("  ", 1)
            p = os.path.join(run_dir, rel)
            if not os.path.isfile(p) or sha256(p) != digest:
                problems.append("run file mismatch: %s" % rel)
    with open(os.path.join(run_dir, "SUMMARY.json"), encoding="utf-8") as fh:
        s = json.load(fh)
    if s.get("mode") != "offline-synthetic" or s.get("tenantStateClaimed") is not False or s.get("mutationsExecuted") != 0:
        problems.append("SUMMARY.json is not labelled offline-synthetic / tenantStateClaimed=false / mutationsExecuted=0")
    for h in s["inputHashes"]:
        p = os.path.join(ROOT, h["path"])
        if not os.path.isfile(p):
            problems.append("input missing: %s" % h["path"])
        elif sha256(p) != h["sha256"]:
            problems.append("input changed since evidence run: %s" % h["path"])
    current = {os.path.relpath(f, ROOT) for f in input_files()}
    recorded = {h["path"] for h in s["inputHashes"]}
    problems += ["input added since evidence run: %s" % p for p in sorted(current - recorded)]
    for p in problems:
        print(p, file=sys.stderr)
    print("verify %s: %s" % (run_dir, "OK" if not problems else "FAIL (%d)" % len(problems)))
    return 0 if not problems else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="local-offline-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    ap.add_argument("--verify", metavar="RUN_DIR")
    a = ap.parse_args()
    return verify(a.verify) if a.verify else generate(a.label)


if __name__ == "__main__":
    sys.exit(main())
