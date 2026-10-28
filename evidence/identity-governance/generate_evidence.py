#!/usr/bin/env python3
"""Generate an OFFLINE / SYNTHETIC evidence run for identity governance.

Writes evidence/identity-governance/runs/<RUN_LABEL>/:
  SUMMARY.json      commit SHA, UTC timestamps, SHA-256 of every input file, every command with
                    expected + actual exit code, per-scenario inventory summary
  SUMMARY.md        human-readable rendering of SUMMARY.json
  reports/          inventory-<scenario>.{json,md,csv} for every fixture scenario,
                    access-review-baseline.{json,md}
  COMMANDS.tsv      seq, step_id, kind, expected_exit, exit_code, result, started_utc, duration_ms, log, command
  logs/NN_<step>.log stdout/stderr of each command with an exit-code footer
  SHA256SUMS        SHA-256 of every other file in the run directory

Usage:
  python3 evidence/identity-governance/generate_evidence.py [--label LABEL]
  python3 evidence/identity-governance/generate_evidence.py --verify evidence/identity-governance/runs/<LABEL>

No network, tenant, Microsoft Graph call, AWS call or credential is involved. Python stdlib only.
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
HASHED_TREES = ("identity/governance", "docs/federation")
HASHED_EXTRA = ("evidence/identity-governance/generate_evidence.py", "evidence/identity-governance/README.md")
GOV = os.path.join("identity", "governance")
DISCLAIMER = (
    "OFFLINE / SYNTHETIC EVIDENCE. Generated from local Microsoft Graph-shaped JSON fixtures in this "
    "repository. No Microsoft Entra ID tenant, Microsoft Graph API, AWS account or credential was used. "
    "Nothing here describes or claims the configuration or state of any tenant or account."
)
# scenario -> expected inventory exit code (0 pass, 1 findings, 2 fail-closed)
SCENARIOS = {"baseline": 0, "findings": 1, "missing-fields": 1, "auth-401": 2, "auth-403": 2,
             "throttled-recover": 0, "throttled-exhausted": 2, "paging-loop": 2, "malformed-page": 2,
             "free-tier": 0}
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


def classify(rel):
    if rel.startswith("identity/governance/fixtures/"):
        return "fixture"
    if rel.startswith("identity/governance/tests/"):
        return "test"
    if rel.startswith("evidence/"):
        return "evidence-generator"
    if rel.endswith(".py") or rel.endswith("baseline.json"):
        return "tool"
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
    out = []
    for f in input_files():
        rel = os.path.relpath(f, ROOT)
        out.append({"path": rel, "kind": classify(rel), "sha256": sha256(f), "bytes": os.path.getsize(f)})
    return out


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


def render_md(s):
    L = ["# Identity governance -- offline evidence run `%s`" % s["runLabel"], "",
         "> **%s**" % s["disclaimer"], "",
         "| Field | Value |", "|---|---|",
         "| Mode | `%s` |" % s["mode"],
         "| Tenant state claimed | `%s` |" % str(s["tenantStateClaimed"]).lower(),
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
    L += ["", "## Inventory scenarios", "",
          "| Scenario | Overall | Exit | Rows | Findings (H/M/L/I) | Graph pages | Retries | Error |",
          "|---|---|---|---|---|---|---|---|"]
    for sc in s["scenarios"]:
        f = sc.get("findingsBySeverity") or {}
        L.append("| `%s` | %s | %d | %s | %s | %s | %s | %s |" % (
            sc["scenario"], sc["overall"], sc["exitCode"], sc.get("inventoryRows", "-"),
            "/".join(str(f.get(k, 0)) for k in ("HIGH", "MEDIUM", "LOW", "INFO")) if f else "-",
            sc.get("pages", "-"), sc.get("retries", "-"), sc.get("error") or ""))
    ar = s["accessReview"]
    L += ["", "## Access review (baseline fixture)", "",
          "Overall **%s** (exit %d); decisions %s; findings %s" % (
              ar["overall"], ar["exitCode"], json.dumps(ar.get("decisions")), ", ".join(ar.get("rules", [])))]
    L += ["", "## Input hashes (SHA-256)", "", "| Kind | Path | SHA-256 |", "|---|---|---|"]
    for h in s["inputHashes"]:
        L.append("| %s | `%s` | `%s` |" % (h["kind"], h["path"], h["sha256"]))
    L += ["", "Verify: `python3 evidence/identity-governance/generate_evidence.py --verify "
              "evidence/identity-governance/runs/%s`" % s["runLabel"]]
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
    os.makedirs(os.path.join(run_dir, "reports"))
    started = utc_now()
    rel_run = os.path.relpath(run_dir, ROOT)
    rep_rel = os.path.join(rel_run, "reports")
    steps = [
        ("python_version", "env", [PY, "--version"], 0),
        ("fixtures_drift_check", "test", [PY, os.path.join(GOV, "make_fixtures.py"), "--check"], 0),
        ("unit_tests", "test", [PY, "-m", "unittest", "discover", "-s", os.path.join(GOV, "tests"), "-v"], 0),
    ]
    for name, exp in SCENARIOS.items():
        base = os.path.join(rep_rel, "inventory-%s" % name)
        steps.append(("inventory_" + name.replace("-", "_"), "inventory",
                      [PY, os.path.join(GOV, "inventory.py"), "--scenario", name, "--json-out", base + ".json",
                       "--md-out", base + ".md", "--csv-out", base + ".csv", "--quiet"], exp))
    ar_base = os.path.join(rep_rel, "access-review-baseline")
    steps.append(("access_review_baseline", "access-review",
                  [PY, os.path.join(GOV, "access_review.py"), "--scenario", "baseline", "--json-out",
                   ar_base + ".json", "--md-out", ar_base + ".md", "--quiet"], 1))
    cmds = [run_step(run_dir, i, sid, kind, argv, exp) for i, (sid, kind, argv, exp) in enumerate(steps, 1)]

    scen = []
    for name in SCENARIOS:
        with open(os.path.join(run_dir, "reports", "inventory-%s.json" % name), encoding="utf-8") as fh:
            r = json.load(fh)
        row = {"scenario": name, "overall": r["overall"], "exitCode": r["exitCode"], "mode": r.get("mode"),
               "pages": (r.get("graph") or {}).get("pages"), "retries": len((r.get("graph") or {}).get("retries", [])),
               "report": "reports/inventory-%s.json" % name}
        if r["overall"] == "ERROR":
            row["error"] = "%s %s" % (r["error"].get("kind"), r["error"].get("status") or "")
        else:
            row["inventoryRows"] = r["summary"]["inventoryRows"]
            row["findingsBySeverity"] = r["summary"]["findingsBySeverity"]
            row["rules"] = sorted({f["rule"] for f in r["findings"]})
        scen.append(row)
    with open(os.path.join(run_dir, "reports", "access-review-baseline.json"), encoding="utf-8") as fh:
        ar = json.load(fh)
    overall = "PASS" if all(c["result"] == "PASS" for c in cmds) else "FAIL"
    summary = {
        "schema": "bank-it-lab/identity-governance-offline-evidence/v1",
        "runLabel": label,
        "mode": "offline-synthetic",
        "tenantStateClaimed": False,
        "disclaimer": DISCLAIMER,
        "git": {"commitSha": commit, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "scopedTreeClean": not dirty,
                "note": "commitSha is the commit whose identity/governance and docs/federation content was "
                        "exercised; the evidence itself is committed on top of it. inputHashes pin the exact bytes."},
        "startedUtc": started,
        "finishedUtc": utc_now(),
        "environment": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                        "network": "not used", "credentials": "not used"},
        "overall": overall,
        "totals": {"commands": len(cmds), "passed": sum(c["result"] == "PASS" for c in cmds),
                   "failed": sum(c["result"] != "PASS" for c in cmds)},
        "scenarios": scen,
        "accessReview": {"overall": ar["overall"], "exitCode": ar["exitCode"], "decisions": ar.get("decisions"),
                         "rules": [f["rule"] for f in ar.get("findings", [])],
                         "report": "reports/access-review-baseline.json"},
        "commands": cmds,
        "inputHashes": input_hashes(),
        "hashes": "SHA256SUMS",
    }
    with open(os.path.join(run_dir, "SUMMARY.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(summary, indent=2) + "\n")
    with open(os.path.join(run_dir, "SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(summary))
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
    if s.get("mode") != "offline-synthetic" or s.get("tenantStateClaimed") is not False:
        problems.append("SUMMARY.json is not labelled offline-synthetic / tenantStateClaimed=false")
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
