"""Map adapter results onto the shared acceptance contract from PR #23 (schemas/acceptance, Worker A).

For each module result it writes, under OUT_ROOT (a repo-root-shaped directory, never this repo's tree by default):
  OUT_ROOT/evidence/acceptance-modules/<label>/
      logs/<module>.log            runner-style log with an `# exit_code: N` trailer (aws-3col convention)
      logs/<module>.result.json    the full adapter result (provisional module contract)
      logs/COMMANDS.tsv            aws-3col rows: <log> <exit> <command>
      SHA256SUMS                   bundle-relative sha256 of every log
      MANIFEST.json                evidence/shared/evidence-manifest.schema.json, with a git-commit anchor = tested commit
  OUT_ROOT/acceptance-modules-<label>.json   acceptance-requirements document (schema_version 1.0.0)

Mapping (module result -> requirement):
  id ACC-MOD-<AWS|PG|ENTRA>-001 · required true · verification_method automated_test
  check.command   python3 acceptance/modules/run.py <module> --mode <mode>
  check.expected  exit_code 0 (run.py exit codes: 0 PASS, 1 FAIL, 2 ERROR, 4 NOT_EXECUTED)
  check.execution executed, or `unavailable` when the adapter reports NOT_EXECUTED (-> result UNKNOWN + rationale)
  result          PASS iff the adapter status is PASS; otherwise FAIL (or UNKNOWN for NOT_EXECUTED)
  evidence_refs   the <module>.result.json and <module>.log artifacts in the bundle
  reviewer_findings [] -- left for an independent human reviewer; the aggregate decision is therefore BLOCKED
                      by design until someone other than `recorded_by` records a `concur`.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from . import _util as U
from .contract import EXIT

REPO = "onnxscibroccoli/bank-it-operations-lab"
SHORT = {"aws-cdk": "AWS", "postgres": "PG", "entra-offline": "ENTRA"}
SOURCES = {
    "aws-cdk": ("project_decision", "PR #5 aws-remediation-vpc-rds; reports/INTEGRATION.md AC3/AC5",
                "cdk-nag AwsSolutions + NIST 800-53 R5 with 0 Non-Compliant; no S3 self-logging (PR #3 finding)"),
    "postgres": ("project_decision", "PR #2 harness v2 @ e7399fb; evidence/postgres/runs/INDEX.md",
                 "backup/restore negatives must fail for their declared reason (PR #3 false-PASS finding)"),
    "entra-offline": ("project_decision", "PR #4 entra-ca-offline; identity/entra/baseline.json",
                      "offline CA baseline; every negative/malformed fixture rejected for its declared rule"),
}
EXCLUSIONS = {
    "aws-cdk": ["No deployment, no AWS API calls; synth/nag only"],
    "postgres": ["Throwaway local cluster only; no managed RDS restore"],
    "entra-offline": ["No Entra ID tenant or Graph; synthetic fixtures only; no tenant state claimed"],
}


def _log_text(r: Dict) -> str:
    lines = [f"acceptance/modules adapter {r['adapter']} module={r['module']} mode={r['mode']}",
             f"status={r['status']} reason_code={r['reason_code']} checks={len(r['checks'])}"]
    lines += [f"{c['status']:12} {c['reason_code']:28} {c['id']}: {c['detail'][:200]}".rstrip() for c in r["checks"]]
    lines.append(f"# exit_code: {EXIT[r['status']]}")
    return "\n".join(l.replace("\n", " ") for l in lines) + "\n"


def emit(results: List[Dict], out_root: Path, label: str, tested_commit: str,
         recorded_by: str = "acceptance/modules (automation)", producer_commit: Optional[str] = None) -> Path:
    if not re.fullmatch(r"[0-9a-f]{40}", tested_commit or ""):
        raise ValueError("tested_commit must be a full 40-hex SHA")
    rel_root = f"evidence/acceptance-modules/{label}"
    broot = Path(out_root) / rel_root
    (broot / "logs").mkdir(parents=True, exist_ok=True)
    rows, sums, reqs = [], [], []
    for r in results:
        m = r["module"]
        log, res = f"{m}.log", f"{m}.result.json"
        (broot / "logs" / log).write_text(_log_text(r))
        (broot / "logs" / res).write_text(json.dumps(r, indent=2) + "\n")
        cmd = f"python3 acceptance/modules/run.py {m} --mode {r['mode']}"
        rows.append(f"{log}\t{EXIT[r['status']]}\t{cmd}")
        not_exec = r["status"] == "NOT_EXECUTED"
        req = {
            "id": f"ACC-MOD-{SHORT[m]}-001",
            "scope": f"{m} module acceptance via existing checks ({', '.join(r['source']['paths'])})",
            "rationale": SOURCES[m][2],
            "required": True,
            "source": {"type": SOURCES[m][0], "reference": SOURCES[m][1]},
            "tested_source_commit": tested_commit,
            "check": {"command": cmd, "expected": {"exit_code": 0},
                      "execution": "unavailable" if not_exec else "executed"},
            "evidence_refs": [{"manifest": f"{rel_root}/MANIFEST.json", "artifact": f"{rel_root}/logs/{f}",
                               "sha256": U.sha256(broot / "logs" / f)} for f in (res, log)],
            "assumptions": ["Adapter wraps the module's own validator/verifier/tests; it does not reimplement them",
                            "Credential variables scrubbed; offline only"],
            "exclusions": EXCLUSIONS[m],
            "verification_method": "automated_test",
            "result": "UNKNOWN" if not_exec else ("PASS" if r["status"] == "PASS" else "FAIL"),
            "reviewer_findings": [],
        }
        if not_exec:
            req["result_rationale"] = f"adapter reported NOT_EXECUTED ({r['reason_code']})"
        else:
            req["check"]["observed"] = {"exit_code": EXIT[r["status"]]}
            if r["status"] != "PASS":
                req["result_rationale"] = f"adapter {r['status']}: {', '.join(r['reason_codes'])}"
        reqs.append(req)
    (broot / "logs" / "COMMANDS.tsv").write_text("\n".join(rows) + "\n")
    for f in sorted((broot / "logs").iterdir()):
        sums.append(f"{U.sha256(f)}  logs/{f.name}")
    (broot / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    script = Path(__file__).resolve()
    producer = {"script": "acceptance/modules/emit_shared.py", "source_commit": producer_commit or "uncommitted"}
    if producer["source_commit"] == "uncommitted":
        producer["script_sha256"] = U.sha256(script)
    manifest = {
        "schema_version": "1.0.0",
        "bundle": {"id": f"acceptance-modules-{label}", "root": rel_root, "kind": "integration-run"},
        "producer": producer,
        "hashes": {"file": "SHA256SUMS", "base": "bundle", "algorithm": "sha256"},
        "commands": {"file": "logs/COMMANDS.tsv", "format": "aws-3col", "rows_written_by": "producer-script"},
        "exclusions": [{"path": "SHA256SUMS", "reason": "self-reference"},
                       {"path": "MANIFEST.json", "reason": "added-after-run"}],
        "anchors": [{"type": "git-commit", "ref": tested_commit}],
    }
    (broot / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    doc = {"schema_version": "1.0.0",
           "document": {"id": f"acceptance-modules-{label}", "title": "Existing-module acceptance (aws-cdk, postgres, entra-offline)",
                        "repository": REPO, "tested_source_commit": tested_commit, "recorded_by": recorded_by,
                        "synthetic": False},
           "requirements": reqs}
    dp = Path(out_root) / f"acceptance-modules-{label}.json"
    dp.write_text(json.dumps(doc, indent=2) + "\n")
    return dp


def contract_checker() -> Optional[Path]:
    """PR #23's checker: in this checkout once merged, or a checkout named by ACCEPTANCE_CONTRACT_ROOT."""
    import os
    for root in (U.ROOT, os.environ.get("ACCEPTANCE_CONTRACT_ROOT")):
        if root and (Path(root) / "schemas/acceptance/check_acceptance.py").is_file():
            return Path(root) / "schemas/acceptance/check_acceptance.py"
    return None


def check_with_shared(doc: Path, out_root: Path):
    """Evaluate with PR #23's checker if it is present in this checkout; returns (exit, json) or None."""
    ca = contract_checker()
    if ca is None:
        return None
    rc, out = U.py(str(ca), str(doc), "--repo-root", str(out_root), "--json")
    try:
        return rc, json.loads(out)
    except ValueError:
        return rc, {"raw": out}
