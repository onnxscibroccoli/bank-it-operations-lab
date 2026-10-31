#!/usr/bin/env python3
"""Generate an OFFLINE evidence run for host operations (patching + systemd hardening).

Writes evidence/host-operations/runs/<RUN_LABEL>/:
  SUMMARY.json   commit SHA, branch, UTC timestamps, SHA-256 of every input file, each command
                 with expected + actual exit code, tool versions, systemd-analyze comparison
  SUMMARY.md     human-readable rendering
  COMMANDS.tsv   seq, step_id, kind, expected_exit, exit_code, result, started_utc, duration_ms, log, command
  logs/NN_<step>.log   stdout/stderr of each command with an exit-code footer
  SHA256SUMS     SHA-256 of every other file in the run directory

Usage:
  python3 evidence/host-operations/generate_evidence.py [--label LABEL]
  python3 evidence/host-operations/generate_evidence.py --verify evidence/host-operations/runs/<LABEL>

No AWS call, no `systemctl`, no host change. Optional analyzers (cfn-lint, yamllint, shellcheck,
systemd-analyze) are run only if present on PATH; a missing analyzer is recorded as SKIPPED, never
as PASS. systemd-analyze runs in --user mode against copies staged in a temporary directory.
Python stdlib only.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RUNS = os.path.join(HERE, "runs")
HASHED_TREES = ("operations/patching", "operations/hardening", "evidence/host-operations/examples")
HASHED_EXTRA = ("evidence/host-operations/generate_evidence.py", "evidence/host-operations/check_examples.py")
DISCLAIMER = ("OFFLINE EVIDENCE. Generated from files in this repository only. No AWS API was called, no "
              "host was patched, and no systemd unit was installed, reloaded or started. Example data is "
              "marked EXAMPLE DATA. Nothing here describes the state of any account or host.")
PY = sys.executable or "python3"
sys.dont_write_bytecode = True
PF = "operations/patching/tests/fixtures"
HF = "operations/hardening/tests/fixtures"
UNITS = "operations/hardening/systemd/units"
DROP = "operations/hardening/systemd/dropins"


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


def input_files():
    files = []
    for tree in HASHED_TREES:
        for dp, dns, fns in os.walk(os.path.join(ROOT, tree)):
            dns[:] = sorted(d for d in dns if d not in ("__pycache__", ".pytest_cache"))
            files += [os.path.join(dp, f) for f in sorted(fns) if not f.endswith(".pyc")]
    files += [os.path.join(ROOT, p) for p in HASHED_EXTRA]
    return sorted(files)


def input_hashes():
    return [{"path": os.path.relpath(f, ROOT), "sha256": sha256(f), "bytes": os.path.getsize(f)}
            for f in input_files()]


class Runner:
    def __init__(self, run_dir):
        self.run_dir, self.steps, self.seq = run_dir, [], 0

    def run(self, step_id, kind, argv, expected, env_extra=None, cwd=None, display=None):
        self.seq += 1
        log_rel = "logs/%02d_%s.log" % (self.seq, step_id)
        started = utc_now()
        t0 = time.monotonic()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", **(env_extra or {}))
        r = subprocess.run(argv, cwd=cwd or ROOT, capture_output=True, text=True, env=env)
        ms = int((time.monotonic() - t0) * 1000)
        cmd = display or " ".join(shlex.quote(a if a != PY else "python3") for a in argv)
        with open(os.path.join(self.run_dir, log_rel), "w", encoding="utf-8") as fh:
            fh.write("$ %s\n--- stdout ---\n%s--- stderr ---\n%s" % (cmd, r.stdout, r.stderr))
            fh.write("--- exit_code=%d expected=%d started_utc=%s duration_ms=%d ---\n"
                     % (r.returncode, expected, started, ms))
        step = {"seq": self.seq, "stepId": step_id, "kind": kind, "command": cmd, "expectedExitCode": expected,
                "exitCode": r.returncode, "result": "PASS" if r.returncode == expected else "FAIL",
                "startedUtc": started, "durationMs": ms, "log": log_rel}
        self.steps.append(step)
        return step, r

    def skip(self, step_id, kind, why):
        self.seq += 1
        self.steps.append({"seq": self.seq, "stepId": step_id, "kind": kind, "command": "-", "expectedExitCode": None,
                           "exitCode": None, "result": "SKIPPED", "startedUtc": utc_now(), "durationMs": 0,
                           "log": "-", "note": why})


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


def tool_version(argv):
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        lines = (r.stdout or r.stderr).strip().splitlines()
        return next((l.strip() for l in lines if l.lower().startswith("version:")), lines[0])
    except (OSError, subprocess.TimeoutExpired, IndexError):
        return None


def stage_units(tmp, dropins):
    cfg = os.path.join(tmp, "config", "systemd", "user")
    os.makedirs(os.path.join(cfg, "bank-lab-app.service.d"))
    os.makedirs(os.path.join(tmp, "runtime"), mode=0o700)
    for u in sorted(os.listdir(os.path.join(ROOT, UNITS))):
        shutil.copy(os.path.join(ROOT, UNITS, u), cfg)
    for d in dropins:
        shutil.copy(os.path.join(ROOT, DROP, d), os.path.join(cfg, "bank-lab-app.service.d"))
    return cfg, {"XDG_CONFIG_HOME": os.path.join(tmp, "config"), "XDG_RUNTIME_DIR": os.path.join(tmp, "runtime")}


def generate(label):
    run_dir = os.path.join(RUNS, label)
    if os.path.exists(run_dir):
        raise SystemExit("run dir exists: %s" % run_dir)
    os.makedirs(os.path.join(run_dir, "logs"))
    started = utc_now()
    status = git("status", "--porcelain", "--", *HASHED_TREES, *HASHED_EXTRA)
    R = Runner(run_dir)
    R.run("python_version", "env", [PY, "--version"], 0)
    R.run("patching_fixture_drift", "drift", [PY, "operations/patching/tests/make_fixtures.py", "--check"], 0)
    R.run("patching_unit_tests", "test", [PY, "-m", "unittest", "discover", "-s", "operations/patching/tests", "-v"], 0)
    R.run("hardening_unit_tests", "test", [PY, "-m", "unittest", "discover", "-s", "operations/hardening/tests", "-v"], 0)
    R.run("examples_marked", "check", [PY, "evidence/host-operations/check_examples.py"], 0)
    R.run("inspect_example_manifest", "inspect",
          [PY, "operations/patching/tools/inspect_patch_manifest.py",
           "operations/patching/manifests/patch-manifest.example.json", "--plan"], 0)
    R.run("print_cli_commands", "dry-run", ["bash", "operations/patching/tools/print-cli-commands.sh"], 0)
    with open(os.path.join(ROOT, PF, "INDEX.json"), encoding="utf-8") as fh:
        for f in json.load(fh)["fixtures"]:
            R.run("patch_fixture_" + f["file"][:-5].replace("-", "_"), "fixture",
                  [PY, "operations/patching/tools/inspect_patch_manifest.py", os.path.join(PF, f["file"]), "--json"],
                  f["expectedExit"])
    with open(os.path.join(ROOT, HF, "INDEX.json"), encoding="utf-8") as fh:
        for c in json.load(fh)["cases"]:
            R.run("unit_fixture_" + c["id"].replace("-", "_"), "fixture",
                  [PY, os.path.join(ROOT, "operations/hardening/tools/score_units.py")] + c["args"] + ["--json"],
                  c["expectedExit"], cwd=os.path.join(ROOT, HF),
                  display="(cd %s && python3 ../../tools/score_units.py %s --json)"
                          % (HF, " ".join(shlex.quote(a) for a in c["args"])))
    scorer = [PY, "operations/hardening/tools/score_units.py"]
    app = os.path.join(UNITS, "bank-lab-app.service")
    layers = {
        "root_agent": ([os.path.join(UNITS, "bank-lab-root-agent.service")], [], 1),
        "app_unhardened": ([app], [], 1),
        "app_baseline": ([app], ["10-hardening-baseline.conf"], 1),
        "app_strict": ([app], ["10-hardening-baseline.conf", "20-hardening-strict.conf"], 0),
    }
    ours = {}
    for name, (unit, dropins, exp) in layers.items():
        argv = scorer + unit + sum((["--dropin", os.path.join(DROP, d)] for d in dropins), []) + ["--json"]
        _, r = R.run("score_" + name, "score", argv, exp)
        try:
            ours[name] = json.loads(r.stdout)["declaredExposure"]
        except ValueError:
            ours[name] = None
    for distro, exp in (("rhel7", 1), ("rhel8", 1), ("ubuntu2004", 1), ("rhel9", 0), ("al2023", 0), ("ubuntu2404", 0)):
        R.run("score_app_strict_" + distro, "score",
              scorer + [app, "--dropin", os.path.join(DROP, "10-hardening-baseline.conf"),
                        "--dropin", os.path.join(DROP, "20-hardening-strict.conf"),
                        "--dropin", os.path.join(DROP, "30-net-bind-service.conf"), "--distro", distro], exp)
    R.run("score_app_legacy_rhel7_threshold6", "score",
          scorer + [app, "--dropin", os.path.join(DROP, "05-hardening-legacy-219.conf"), "--distro", "rhel7",
                    "--threshold", "6.0"], 0)
    R.run("compat_matrix_render", "render", scorer + ["--render-matrix"], 0)

    versions = {"python": platform.python_version()}
    for tool, argv, step in (
            ("cfn-lint", ["cfn-lint", "operations/patching/ssm/patch-baselines-and-windows.cfn.yaml"], "cfn_lint"),
            ("yamllint", ["yamllint", "-d", "{extends: default, rules: {line-length: {max: 120}}}",
                          "operations/patching/ssm/patch-baselines-and-windows.cfn.yaml"], "yamllint"),
            ("shellcheck", ["shellcheck", "operations/patching/tools/print-cli-commands.sh"], "shellcheck")):
        if shutil.which(tool):
            versions[tool] = tool_version([tool, "--version"])
            R.run(step, "analyzer", argv, 0)
        else:
            versions[tool] = None
            R.skip(step, "analyzer", "%s not on PATH" % tool)

    systemd_cmp = {}
    if shutil.which("systemd-analyze"):
        versions["systemd-analyze"] = tool_version(["systemd-analyze", "--version"])
        for name, (unit, dropins, _) in layers.items():
            with tempfile.TemporaryDirectory() as tmp:
                cfg, env = stage_units(tmp, dropins)
                uname = os.path.basename(unit[0])
                disp_env = "XDG_CONFIG_HOME=<tmp>/config XDG_RUNTIME_DIR=<tmp>/runtime"
                staged = "<tmp>/config/systemd/user/%s (+ %s)" % (uname, ", ".join(dropins) or "no drop-ins")
                R.run("sd_verify_" + name, "analyzer", ["systemd-analyze", "--user", "verify", os.path.join(cfg, uname)],
                      0, env_extra=env, display="%s systemd-analyze --user verify %s" % (disp_env, staged))
                _, r = R.run("sd_security_" + name, "analyzer",
                             ["systemd-analyze", "--user", "security", "--offline=true", "--no-pager",
                              os.path.join(cfg, uname)], 0, env_extra=env,
                             display="%s systemd-analyze --user security --offline=true --no-pager %s" % (disp_env, staged))
                m = re.search(r"Overall exposure level for \S+: ([0-9.]+) (\w+)", r.stdout + r.stderr)
                systemd_cmp[name] = {"scoreUnits": ours.get(name),
                                     "systemdAnalyze": float(m.group(1)) if m else None,
                                     "systemdRating": m.group(2) if m else None}
    else:
        versions["systemd-analyze"] = None
        R.skip("systemd_analyze", "analyzer", "systemd-analyze not on PATH")

    failed = [s for s in R.steps if s["result"] == "FAIL"]
    summary = {
        "schemaVersion": "1.0.0", "runLabel": label, "mode": "offline", "disclaimer": DISCLAIMER,
        "awsCallsMade": False, "hostsModified": False,
        "git": {"commitSha": git("rev-parse", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "scopedTreeClean": status == ""},
        "startedUtc": started, "finishedUtc": utc_now(),
        "environment": {"platform": platform.platform(), "versions": versions},
        "inputHashes": input_hashes(),
        "steps": R.steps,
        "counts": {k: sum(1 for s in R.steps if s["result"] == k) for k in ("PASS", "FAIL", "SKIPPED")},
        "exposureComparison": systemd_cmp,
        "overall": "FAIL" if failed else "PASS",
    }
    with open(os.path.join(run_dir, "SUMMARY.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(run_dir, "COMMANDS.tsv"), "w", encoding="utf-8") as fh:
        fh.write("seq\tstep_id\tkind\texpected_exit\texit_code\tresult\tstarted_utc\tduration_ms\tlog\tcommand\n")
        for s in R.steps:
            fh.write("\t".join(str(x) if x is not None else "-" for x in (
                s["seq"], s["stepId"], s["kind"], s["expectedExitCode"], s["exitCode"], s["result"],
                s["startedUtc"], s["durationMs"], s["log"], s["command"])) + "\n")
    with open(os.path.join(run_dir, "SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(summary))
    write_sums(run_dir)
    return run_dir, summary


def render_md(s):
    L = ["# Host operations -- offline evidence run `%s`" % s["runLabel"], "", "> **%s**" % s["disclaimer"], "",
         "| Field | Value |", "|---|---|",
         "| Validated commit | `%s` |" % s["git"]["commitSha"], "| Branch | `%s` |" % s["git"]["branch"],
         "| Scoped tree clean at run | `%s` |" % str(s["git"]["scopedTreeClean"]).lower(),
         "| Started (UTC) | %s |" % s["startedUtc"], "| Finished (UTC) | %s |" % s["finishedUtc"],
         "| AWS calls made | `false` |", "| Hosts modified | `false` |",
         "| Steps | %d PASS / %d FAIL / %d SKIPPED |" % (s["counts"]["PASS"], s["counts"]["FAIL"], s["counts"]["SKIPPED"]),
         "| Overall | **%s** |" % s["overall"], "", "## Tool versions", ""]
    for k, v in sorted(s["environment"]["versions"].items()):
        L.append("- `%s`: %s" % (k, v if v else "not installed (step SKIPPED)"))
    if s["exposureComparison"]:
        L += ["", "## Exposure: score_units.py vs systemd-analyze security --offline", "",
              "| Layer | score_units.py | systemd-analyze | systemd rating |", "|---|---|---|---|"]
        for k, v in s["exposureComparison"].items():
            L.append("| %s | %s | %s | %s |" % (k, v["scoreUnits"], v["systemdAnalyze"], v["systemdRating"]))
        L += ["", "Both are offline estimates on staged copies (systemd-analyze in `--user` mode); the ordering "
              "is what matters. Run `systemd-analyze security` on the real host as the authority."]
    L += ["", "## Commands", "", "| # | Step | Kind | Expected | Exit | Result | Log |", "|---|---|---|---|---|---|---|"]
    for st in s["steps"]:
        L.append("| %d | `%s` | %s | %s | %s | %s | %s |" % (st["seq"], st["stepId"], st["kind"],
                 "-" if st["expectedExitCode"] is None else st["expectedExitCode"],
                 "-" if st["exitCode"] is None else st["exitCode"], st["result"],
                 "`%s`" % st["log"] if st["log"] != "-" else st.get("note", "-")))
    return "\n".join(L) + "\n"


def verify(run_dir):
    bad = []
    with open(os.path.join(run_dir, "SHA256SUMS"), encoding="utf-8") as fh:
        for line in fh:
            h, rel = line.rstrip("\n").split("  ", 1)
            p = os.path.join(run_dir, rel)
            if not os.path.isfile(p) or sha256(p) != h:
                bad.append("run file changed: %s" % rel)
    with open(os.path.join(run_dir, "SUMMARY.json"), encoding="utf-8") as fh:
        s = json.load(fh)
    for ih in s["inputHashes"]:
        p = os.path.join(ROOT, ih["path"])
        if not os.path.isfile(p) or sha256(p) != ih["sha256"]:
            bad.append("input changed since run: %s" % ih["path"])
    for b in bad:
        print("VERIFY: %s" % b)
    print("verify %s: %s (%d inputs)" % (os.path.relpath(run_dir, ROOT), "FAIL" if bad else "PASS", len(s["inputHashes"])))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label")
    ap.add_argument("--verify")
    a = ap.parse_args()
    if a.verify:
        return verify(os.path.abspath(a.verify))
    label = a.label or "local-offline-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir, s = generate(label)
    print("wrote %s: %s (%d PASS / %d FAIL / %d SKIPPED)" % (os.path.relpath(run_dir, ROOT), s["overall"],
          s["counts"]["PASS"], s["counts"]["FAIL"], s["counts"]["SKIPPED"]))
    return 0 if s["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
