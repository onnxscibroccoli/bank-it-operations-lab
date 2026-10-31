#!/usr/bin/env python3
"""SIMULATION - generate an offline evidence run for the fictional Acme Core Ledger SIMULATION
vendor mock and vendor-risk governance lint. Stdlib only; no network.

    python3 evidence/vendor/generate_evidence.py               # -> evidence/vendor/runs/local-offline-<UTC>/
    python3 evidence/vendor/generate_evidence.py --verify evidence/vendor/runs/<RUN_LABEL>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MOCK = REPO / "integrations" / "vendor-mock"
GOV = REPO / "governance" / "vendor-risk"
RUNS = REPO / "evidence" / "vendor" / "runs"
PY = sys.executable
SCAN = ("import pathlib,sys\n"
        "bad=[str(p) for d in sys.argv[1:] for p in sorted(pathlib.Path(d).rglob('*'))\n"
        "     if p.is_file() and '__pycache__' not in p.parts and p.stat().st_size\n"
        "     and 'SIMULATION' not in p.read_text(encoding='utf-8')]\n"
        "print('files missing SIMULATION label:', bad or 'none'); sys.exit(1 if bad else 0)")


def sh(*cmd, cwd=REPO):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True).stdout.strip()


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def steps(tmp: Path):
    bad_raci = tmp / "raci-two-accountable-SIMULATION.md"
    src = (GOV / "examples" / "acme-core-ledger-SIMULATION-raci.md").read_text(encoding="utf-8")
    bad_raci.write_text(src.replace("| 1 | Business need & data requirements (minimization) | A | R |",
                                    "| 1 | Business need & data requirements (minimization) | A | A |"),
                        encoding="utf-8")
    scen = GOV / "scenarios" / "core-banking-vendor-outage-SIMULATION.md"
    bad_scen = tmp / "scenario-vendor-sla-SIMULATION.md"
    bad_scen.write_text(scen.read_text(encoding="utf-8")
                        + "\n- The vendor will restore service within 4 hours (99.9% uptime SLA).\n",
                        encoding="utf-8")
    jh_scen = tmp / "scenario-real-vendor-outside-context-SIMULATION.md"
    jh_scen.write_text(scen.read_text(encoding="utf-8").replace(
        "The fictional vendor status page", "The Jack Henry status page", 1), encoding="utf-8")
    mut = tmp / "vendor-mock-mutant"
    shutil.copytree(MOCK, mut, ignore=shutil.ignore_patterns("__pycache__"))
    c = mut / "vendor_mock" / "contract.py"
    c.write_text(c.read_text().replace('if schema.get("additionalProperties") is False:', "if False:"))
    mut2 = tmp / "vendor-mock-mutant-retry"
    shutil.copytree(MOCK, mut2, ignore=shutil.ignore_patterns("__pycache__"))
    cl = mut2 / "vendor_mock" / "client.py"
    cl.write_text(cl.read_text().replace("if retry_after > self.max_retry_after:", "if False:"))
    return [
        ("python_version", "env", 0, [PY, "--version"], REPO),
        ("contract_json_parses", "check", 0, [PY, "-m", "json.tool", "contract/openapi.json"], MOCK),
        ("unit_tests", "test", 0, [PY, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"], MOCK),
        ("simulation_label_scan", "check", 0, [PY, "-c", SCAN, str(MOCK), str(GOV)], REPO),
        ("governance_unit_tests", "test", 0,
         [PY, "-m", "unittest", "discover", "-s", "governance/vendor-risk/tests", "-v"], REPO),
        ("governance_lint", "check", 0, [PY, str(GOV / "check_governance.py")], REPO),
        ("neg_scenario_lint_vendor_sla_commitment", "negative", 1,
         [PY, str(GOV / "check_governance.py"), "--scenario", str(bad_scen),
          "--link-base", str(GOV / "scenarios")], REPO),
        ("neg_scenario_lint_real_vendor_outside_context", "negative", 1,
         [PY, str(GOV / "check_governance.py"), "--scenario", str(jh_scen),
          "--link-base", str(GOV / "scenarios")], REPO),
        ("neg_governance_lint_blank_raci_template", "negative", 1,
         [PY, str(GOV / "check_governance.py"), "--raci", str(GOV / "raci-matrix-template.md")], REPO),
        ("neg_governance_lint_two_accountable", "negative", 1,
         [PY, str(GOV / "check_governance.py"), "--raci", str(bad_raci)], REPO),
        ("neg_mutation_validator_ignores_extra_fields", "negative", 1,
         [PY, "-m", "unittest", "discover", "-s", "tests", "-t", "."], mut),
        ("neg_mutation_client_ignores_retry_after_cap", "negative", 1,
         [PY, "-m", "unittest", "discover", "-s", "tests", "-t", "."], mut2),
    ]


def write_sums(run: Path):
    files = sorted(p for p in run.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (run / "SHA256SUMS").write_text("".join(f"{sha256(p)}  {p.relative_to(run).as_posix()}\n" for p in files))


def verify(run: Path) -> int:
    bad = 0
    listed = set()
    for line in (run / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        listed.add(name)
        ok = (run / name).is_file() and sha256(run / name) == digest
        bad += not ok
        print(("OK   " if ok else "FAIL ") + name)
    extra = {p.relative_to(run).as_posix() for p in run.rglob("*") if p.is_file()} - listed - {"SHA256SUMS"}
    for e in sorted(extra):
        print("UNLISTED " + e)
    summary = json.loads((run / "SUMMARY.json").read_text())
    if not summary["allPassed"]:
        print("SUMMARY reports failures"); bad += 1
    print("SIMULATION verify:", "PASS" if not bad and not extra else "FAIL")
    return 0 if not bad and not extra else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", type=Path)
    ap.add_argument("--allow-dirty", action="store_true")
    a = ap.parse_args()
    if a.verify:
        return verify(a.verify)
    dirty = sh("git", "status", "--porcelain", "--", "integrations/vendor-mock", "governance/vendor-risk")
    if dirty and not a.allow_dirty:
        print("refusing: uncommitted changes under owned inputs (use --allow-dirty)\n" + dirty)
        return 2
    started = datetime.now(timezone.utc)
    label = "local-offline-" + started.strftime("%Y%m%dT%H%M%SZ")
    run = RUNS / label
    (run / "logs").mkdir(parents=True)
    rows, results = [], []
    with tempfile.TemporaryDirectory(prefix="vendor-sim-") as td:
        for i, (sid, kind, expect, cmd, cwd) in enumerate(steps(Path(td)), 1):
            t0 = datetime.now(timezone.utc); m0 = time.monotonic()
            p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            ms = int((time.monotonic() - m0) * 1000)
            ok = p.returncode == expect
            log = f"logs/{i:02d}_{sid}.log"
            shown = " ".join(str(x).replace(td, "$TMP").replace(str(REPO), "$REPO") for x in cmd)
            shown_cwd = str(cwd).replace(td, "$TMP").replace(str(REPO), "$REPO")
            (run / log).write_text(
                f"# SIMULATION evidence log\n# step: {sid} ({kind})\n# cwd: {shown_cwd}\n# command: {shown}\n"
                f"# started_utc: {t0.isoformat()}\n\n--- stdout ---\n{p.stdout}\n--- stderr ---\n{p.stderr}\n"
                f"--- exit_code: {p.returncode} (expected {expect}) -> {'PASS' if ok else 'FAIL'} ---\n")
            rows.append([i, sid, kind, expect, p.returncode, "PASS" if ok else "FAIL",
                         t0.isoformat(), ms, log, shown])
            results.append({"seq": i, "step": sid, "kind": kind, "expectedExit": expect,
                            "exitCode": p.returncode, "result": "PASS" if ok else "FAIL",
                            "durationMs": ms, "log": log, "command": shown})
    hdr = ["seq", "step_id", "kind", "expected_exit", "exit_code", "result", "started_utc", "duration_ms", "log", "command"]
    (run / "COMMANDS.tsv").write_text("\t".join(hdr) + "\n" + "".join("\t".join(map(str, r)) + "\n" for r in rows))
    inputs = sorted(p for d in (MOCK, GOV) for p in d.rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts)
    all_ok = all(r["result"] == "PASS" for r in results)
    summary = {
        "simulation": "SIMULATION",
        "disclaimer": "Fictional vendor 'Acme Core Ledger SIMULATION'. Offline; no network, no real vendor, "
                      "no customer data. No authoritative compatibility evidence exists for any real vendor "
                      "or product (including Banno / Jack Henry).",
        "runLabel": label, "commit": sh("git", "rev-parse", "HEAD"),
        "branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD"), "inputsDirty": bool(dirty),
        "startedUtc": started.isoformat(), "finishedUtc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "inputHashes": {p.relative_to(REPO).as_posix(): sha256(p) for p in inputs},
        "steps": results, "allPassed": all_ok,
    }
    (run / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    md = [f"# SIMULATION evidence run `{label}`", "", f"> {summary['disclaimer']}", "",
          f"- commit `{summary['commit']}` on `{summary['branch']}` (inputs dirty: {summary['inputsDirty']})",
          f"- Python {summary['python']}; started {summary['startedUtc']}",
          f"- **Overall: {'PASS' if all_ok else 'FAIL'}**", "",
          "| # | Step | Kind | Expected exit | Exit | Result | Log |", "|---|---|---|---|---|---|---|"]
    md += [f"| {r['seq']} | {r['step']} | {r['kind']} | {r['expectedExit']} | {r['exitCode']} | {r['result']} | `{r['log']}` |"
           for r in results]
    (run / "SUMMARY.md").write_text("\n".join(md) + "\n")
    write_sums(run)
    print(f"SIMULATION evidence run: {run.relative_to(REPO)} -> {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
