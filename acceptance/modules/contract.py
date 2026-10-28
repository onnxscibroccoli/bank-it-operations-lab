"""Acceptance module result contract (PROVISIONAL shim, owned by acceptance/modules/).

No shared acceptance contract existed on any branch of bank-it-operations-lab when these
adapters were written (2026-10-28 ~14:40 EDT). This module defines the smallest result
shape the adapters need, so the adapters are complete and testable now. When the shared
contract lands, only `to_shared()` / this file should need to change; adapters build
results exclusively through `ModuleResult` and `Check`.

Contract id: bank-it-lab/acceptance-module-result/v0-provisional

Result object (JSON):
  contract        str   contract id above
  module          str   "aws-cdk" | "postgres" | "entra-offline"
  adapter         str   "acceptance/modules/<file>.py@<version>"
  source          obj   {"prs": [int], "paths": [str]}  -- the existing module this wraps
  mode            str   "static-evidence" | "live-offline"
  status          str   PASS | FAIL | ERROR | NOT_EXECUTED
  reason_code     str   OK when PASS, otherwise the first failing check's reason code
  reason_codes    [str] every distinct non-OK reason code, in check order
  checks          [Check]
  evidence        [{"path": str, "sha256": str}]  -- existing evidence files the result relies on
  claims          {"network_used": false, "credentials_used": false,
                   "cloud_mutated": false, "tenant_state_claimed": false}
  started_utc / finished_utc  ISO-8601 Z
  git_sha         str | null

Check object:
  id           str   stable, e.g. "AWS-NAG-001"
  title        str
  kind         str   "positive" (must succeed) | "negative" (a known-bad input must be rejected
                     for its declared reason) | "integrity" (evidence hashes/provenance)
  status       str   PASS | FAIL | ERROR | NOT_EXECUTED
  reason_code  str   OK or one of REASON_CODES
  detail       str
  evidence     [str] repo-relative paths

Exit codes of acceptance/modules/run.py: 0 PASS, 1 FAIL, 2 ERROR/usage, 4 NOT_EXECUTED.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

CONTRACT_ID = "bank-it-lab/acceptance-module-result/v0-provisional"
STATUSES = ("PASS", "FAIL", "ERROR", "NOT_EXECUTED")
KINDS = ("positive", "negative", "integrity")
MODES = ("static-evidence", "live-offline")
EXIT = {"PASS": 0, "FAIL": 1, "ERROR": 2, "NOT_EXECUTED": 4}

REASON_CODES = {
    "OK": "check passed",
    "EVIDENCE_MISSING": "an expected evidence file or directory is absent",
    "EVIDENCE_HASH_MISMATCH": "a file does not match its recorded SHA256 (tampered or stale evidence)",
    "EVIDENCE_HISTORICAL": "the evidence run is marked HISTORICAL and cannot count as a pass",
    "EVIDENCE_INPUT_DRIFT": "inputs changed since the evidence run was recorded",
    "UNIT_TESTS_FAILED": "the module's own test suite reports failures or ran zero tests",
    "NAG_NON_COMPLIANT": "a cdk-nag report contains Non-Compliant rows",
    "NAG_REPORT_COUNT": "the number of cdk-nag reports is not the expected count",
    "S3_SELF_LOGGING": "an S3 bucket logs to itself (PR #3 blocking finding)",
    "SYNTH_DRIFT": "a fresh synth differs from the committed template",
    "RUN_FAILED": "the run's own summary reports a failure",
    "CASE_FAILED": "a declared case in the run did not PASS",
    "NEGATIVE_UNEXPECTED_SUCCESS": "a known-bad input was accepted",
    "NEGATIVE_WRONG_REASON": "a known-bad input was rejected, but not for its declared reason",
    "NEGATIVE_COUNT": "fewer negative cases than required",
    "CONTROL_NOT_REJECTED": "a negative-control run was not rejected",
    "BASELINE_RULE_FAILED": "well-formed input violates one or more baseline rules",
    "INPUT_MALFORMED": "input is malformed / unknown (fail closed)",
    "CLAIM_VIOLATION": "evidence claims tenant/cloud state or credential use",
    "TOOL_UNAVAILABLE": "a required local tool is missing (live mode only)",
    "TOOL_ERROR": "the wrapped tool exited unexpectedly",
}


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Check:
    id: str
    title: str
    kind: str
    status: str
    reason_code: str = "OK"
    detail: str = ""
    evidence: List[str] = field(default_factory=list)

    def __post_init__(self):
        assert self.kind in KINDS, self.kind
        assert self.status in STATUSES, self.status
        assert self.reason_code in REASON_CODES, self.reason_code
        if self.status == "PASS":
            assert self.reason_code == "OK", (self.id, self.reason_code)
        else:
            assert self.reason_code != "OK", (self.id, "non-PASS check needs a reason code")


def check(id, title, kind, ok, reason_if_fail, detail="", evidence=None, status_if_fail="FAIL"):
    return Check(id, title, kind, "PASS" if ok else status_if_fail,
                 "OK" if ok else reason_if_fail, detail, list(evidence or []))


@dataclass
class ModuleResult:
    module: str
    adapter: str
    source: Dict
    mode: str
    checks: List[Check] = field(default_factory=list)
    evidence: List[Dict] = field(default_factory=list)
    claims: Dict = field(default_factory=lambda: {"network_used": False, "credentials_used": False,
                                                  "cloud_mutated": False, "tenant_state_claimed": False})
    started_utc: str = field(default_factory=utc_now)
    finished_utc: Optional[str] = None
    git_sha: Optional[str] = None

    def add(self, c: Check) -> Check:
        self.checks.append(c)
        return c

    @property
    def status(self) -> str:
        sts = [c.status for c in self.checks]
        if not sts:
            return "NOT_EXECUTED"
        if "ERROR" in sts:
            return "ERROR"
        if "FAIL" in sts:
            return "FAIL"
        # Worker D integration fix: any NOT_EXECUTED check makes the module NOT_EXECUTED. Previously a mix of
        # PASS + NOT_EXECUTED aggregated to PASS (exit 0), e.g. live-offline postgres with no PG binaries.
        if "NOT_EXECUTED" in sts:
            return "NOT_EXECUTED"
        return "PASS" if all(s == "PASS" for s in sts) else "FAIL"

    @property
    def reason_codes(self) -> List[str]:
        out: List[str] = []
        for c in self.checks:
            if c.reason_code != "OK" and c.reason_code not in out:
                out.append(c.reason_code)
        return out

    def to_dict(self) -> Dict:
        if self.finished_utc is None:
            self.finished_utc = utc_now()
        rc = self.reason_codes
        d = {
            "contract": CONTRACT_ID, "module": self.module, "adapter": self.adapter,
            "source": self.source, "mode": self.mode, "status": self.status,
            "reason_code": "OK" if self.status == "PASS" else (rc[0] if rc else "TOOL_ERROR"),
            "reason_codes": rc, "checks": [asdict(c) for c in self.checks],
            "evidence": self.evidence, "claims": self.claims,
            "started_utc": self.started_utc, "finished_utc": self.finished_utc, "git_sha": self.git_sha,
        }
        validate(d)
        return d


REQUIRED = {"contract", "module", "adapter", "source", "mode", "status", "reason_code", "reason_codes",
            "checks", "evidence", "claims", "started_utc", "finished_utc", "git_sha"}


def validate(d: Dict) -> None:
    """Raise ValueError if `d` does not satisfy the provisional contract."""
    missing = REQUIRED - set(d)
    if missing:
        raise ValueError("result missing fields: %s" % sorted(missing))
    if d["contract"] != CONTRACT_ID:
        raise ValueError("wrong contract id")
    if d["status"] not in STATUSES or d["mode"] not in MODES:
        raise ValueError("bad status/mode")
    if d["status"] == "PASS" and d["reason_code"] != "OK":
        raise ValueError("PASS must carry reason_code OK")
    if d["status"] != "PASS" and d["reason_code"] not in REASON_CODES:
        raise ValueError("unknown reason_code")
    if any(v is not False for v in d["claims"].values()):
        raise ValueError("adapters must never claim network/credential/cloud/tenant use")
    for c in d["checks"]:
        if c["kind"] not in KINDS or c["status"] not in STATUSES or c["reason_code"] not in REASON_CODES:
            raise ValueError("bad check %r" % c.get("id"))
