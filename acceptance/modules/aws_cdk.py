"""Acceptance adapter: AWS CDK (infra/aws-cdk, PR #5 via overnight/integration).

Wraps -- does not rebuild -- the existing module:
  * committed evidence bundle  evidence/aws/aws-remediation-vpc-rds/  (SHA256SUMS, jest-results.json,
    4 cdk-nag CSV reports, synthesized templates)
  * PR #3's shared validator   evidence/shared/validate_evidence.py  (`hashes`, `cfn-s3-selflog`)
  * live-offline mode only:    `npx jest --ci` and `npx cdk synth --no-lookups` in infra/aws-cdk,
    with AWS credential variables scrubbed (same list as scripts/validate-all.sh). Nothing is deployed.
"""
from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from . import _util as U
from .contract import ModuleResult, check

VERSION = "0.1.0"
MODULE = "aws-cdk"
EVIDENCE = U.ROOT / "evidence/aws/aws-remediation-vpc-rds"
CDK_DIR = U.ROOT / "infra/aws-cdk"
SHARED_V = U.ROOT / "evidence/shared/validate_evidence.py"
EXPECTED_NAG_REPORTS = 4  # 2 stacks x (AwsSolutions, NIST.800.53.R5); same gate as validate-all.sh
REQUIRED_SUITES = ("negative-controls.test.ts", "secure-storage-stack.test.ts", "network-database-stack.test.ts")


def _nag_checks(res: ModuleResult, nag_dir: Path, prefix: str):
    reports = sorted(nag_dir.glob("*-NagReport.csv")) if nag_dir.is_dir() else []
    res.add(check(f"{prefix}-NAG-001", f"exactly {EXPECTED_NAG_REPORTS} cdk-nag reports", "positive",
                  len(reports) == EXPECTED_NAG_REPORTS, "NAG_REPORT_COUNT",
                  f"found {len(reports)} in {U.rel(nag_dir)}", [U.rel(p) for p in reports]))
    bad = []
    for p in reports:
        with open(p, newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("Compliance") == "Non-Compliant":
                    bad.append(f"{p.name}:{row.get('Rule ID')}:{row.get('Resource ID')}")
    res.add(check(f"{prefix}-NAG-002", "0 Non-Compliant rows across all cdk-nag reports", "positive",
                  bool(reports) and not bad, "NAG_NON_COMPLIANT" if bad else "NAG_REPORT_COUNT",
                  "; ".join(bad[:10]) or f"{len(reports)} reports clean", [U.rel(p) for p in reports]))
    return reports


def _selflog_checks(res: ModuleResult, templates, prefix: str):
    fails = []
    for t in templates:
        rc, out = U.py(str(SHARED_V), "cfn-s3-selflog", str(t))
        if rc != 0:
            fails.append(f"{t.name}: " + " | ".join(l for l in out.splitlines() if l.startswith("ERROR"))[:300])
    res.add(check(f"{prefix}-S3-001", "no S3 bucket delivers access logs to itself (shared cfn-s3-selflog)",
                  "negative", bool(templates) and not fails, "S3_SELF_LOGGING" if fails else "EVIDENCE_MISSING",
                  "; ".join(fails) or f"{len(templates)} templates clean", [U.rel(t) for t in templates]))


def _jest_check(res: ModuleResult, results_json: Path, cid: str, title: str):
    if not results_json.is_file():
        res.add(check(cid, title, "positive", False, "EVIDENCE_MISSING", f"{U.rel(results_json)} missing"))
        return
    d = json.loads(results_json.read_text())
    suites = {Path(t["name"]).name: t["status"] for t in d.get("testResults", [])}
    missing = [s for s in REQUIRED_SUITES if s not in suites]
    failed_suites = [s for s, st in suites.items() if st != "passed"]
    ok = (d.get("success") is True and d.get("numFailedTests", 1) == 0 and d.get("numTotalTests", 0) > 0
          and d.get("numRuntimeErrorTestSuites", 0) == 0 and not missing and not failed_suites)
    detail = (f"{d.get('numPassedTests')}/{d.get('numTotalTests')} passed, suites={sorted(suites)}"
              + (f", missing={missing}" if missing else "") + (f", failed={failed_suites}" if failed_suites else ""))
    res.add(check(cid, title, "positive", ok, "UNIT_TESTS_FAILED", detail, [U.rel(results_json)]))


def run(mode: str = "static-evidence", evidence_dir: Optional[Path] = None) -> ModuleResult:
    ev = Path(evidence_dir or EVIDENCE)
    res = ModuleResult(MODULE, f"acceptance/modules/aws_cdk.py@{VERSION}",
                       {"prs": [5, 1, 3], "paths": ["infra/aws-cdk", U.rel(ev), "evidence/shared/validate_evidence.py"]},
                       mode, git_sha=U.git_sha())
    sums = ev / "SHA256SUMS"
    if not sums.is_file():
        res.add(check("AWS-INT-001", "evidence bundle present with SHA256SUMS", "integrity", False,
                      "EVIDENCE_MISSING", f"{U.rel(sums)} missing"))
        return res
    rc, out = U.py(str(SHARED_V), "hashes", str(sums))
    res.add(check("AWS-INT-001", "evidence bundle matches SHA256SUMS (shared validator `hashes`)", "integrity",
                  rc == 0, "EVIDENCE_HASH_MISMATCH",
                  " | ".join(l for l in out.splitlines() if l.startswith("ERROR"))[:400] or out.strip().splitlines()[-1],
                  [U.rel(sums)]))
    _jest_check(res, ev / "jest-results.json", "AWS-JEST-001",
                "recorded Jest run: all suites incl. negative-controls passed, 0 failures")
    reports = _nag_checks(res, ev / "cdk-nag", "AWS")
    templates = sorted((ev / "synth").glob("*.template.json"))
    _selflog_checks(res, templates, "AWS")
    res.evidence = U.evidence_entries([sums, ev / "jest-results.json", *reports, *templates])

    if mode == "live-offline":
        _live(res, templates)
    return res


def _live(res: ModuleResult, committed_templates):
    if shutil.which("npx") is None or not (CDK_DIR / "node_modules").is_dir():
        res.add(check("AWS-LIVE-000", "Node toolchain + infra/aws-cdk/node_modules available", "positive", False,
                      "TOOL_UNAVAILABLE", "run `npm ci --ignore-scripts` in infra/aws-cdk", status_if_fail="NOT_EXECUTED"))
        return
    with tempfile.TemporaryDirectory(prefix="acc-aws-") as td:
        jr = Path(td) / "jest.json"
        rc, out = U.run(["npx", "jest", "--ci", "--json", f"--outputFile={jr}"], cwd=CDK_DIR)
        _jest_check(res, jr, "AWS-LIVE-001", "fresh Jest run (offline): all suites incl. negative-controls pass")
        outdir = Path(td) / "cdk.out"
        rc, out = U.run(["npx", "cdk", "synth", "--no-lookups", "--no-version-reporting", "--no-path-metadata",
                         "--quiet", "-o", str(outdir)], cwd=CDK_DIR)
        res.add(check("AWS-LIVE-002", "fresh credential-free cdk synth succeeds", "positive", rc == 0,
                      "TOOL_ERROR", out.strip()[-400:]))
        if rc != 0:
            return
        _nag_checks(res, outdir, "AWS-LIVE")
        fresh = sorted(outdir.glob("*.template.json"))
        _selflog_checks(res, fresh, "AWS-LIVE")
        drift = [t.name for t in committed_templates
                 if not (outdir / t.name).is_file() or (outdir / t.name).read_bytes() != t.read_bytes()]
        res.add(check("AWS-LIVE-003", "fresh synth is byte-identical to committed evidence templates", "integrity",
                      bool(committed_templates) and not drift, "SYNTH_DRIFT", f"drift: {drift}" if drift else "no drift"))
