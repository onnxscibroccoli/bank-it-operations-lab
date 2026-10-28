"""Acceptance adapter: Entra Conditional Access, offline/synthetic (identity/entra, PR #4 via overnight/integration).

Wraps -- does not rebuild -- the existing module:
  * identity/entra/ca_validator.py   (exit 0 PASS / 1 baseline FAIL / 2 malformed, fail-closed; JSON report)
  * tests/entra/test_ca_validator.py the PR's own fixture->expected-rule map (BASELINE_NEGATIVES, MALFORMED)
                                      is imported, not copied, so the adapter tracks the module's declared reasons
  * tests/entra unittest suite and fixture drift check (make_fixtures.py --check)
  * evidence/entra/generate_evidence.py --verify on every committed run
Never contacts Entra ID / Graph; reads no credentials; claims nothing about any tenant.
"""
from __future__ import annotations

import importlib.util
import json
import re
import tempfile
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple

from . import _util as U
from .contract import ModuleResult, check

VERSION = "0.1.0"
MODULE = "entra-offline"
ENTRA = U.ROOT / "identity/entra"
VALIDATOR = ENTRA / "ca_validator.py"
TESTS = U.ROOT / "tests/entra"
FIXTURES = TESTS / "fixtures"
EVIDENCE_RUNS = U.ROOT / "evidence/entra/runs"
GEN = U.ROOT / "evidence/entra/generate_evidence.py"
EXIT_PASS, EXIT_BASELINE_FAIL, EXIT_MALFORMED = 0, 1, 2


def module_expectations() -> Tuple[Dict[str, Set[str]], Dict[str, str]]:
    """Load the fixture expectations declared by PR #4's own test module."""
    spec = importlib.util.spec_from_file_location("_entra_tests", TESTS / "test_ca_validator.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return {k: set(v) for k, v in m.BASELINE_NEGATIVES.items()}, dict(m.MALFORMED)


def validate(policies: Path, baseline: Optional[Path] = None) -> Tuple[int, dict]:
    with tempfile.TemporaryDirectory(prefix="acc-entra-") as td:
        jp = Path(td) / "r.json"
        rc, out = U.py(str(VALIDATOR), str(policies), "--baseline", str(baseline or ENTRA / "baseline.json"),
                       "--json-out", str(jp), "--quiet")
        rep = json.loads(jp.read_text()) if jp.is_file() else {"rules": [], "_stdout": out}
    return rc, rep


def failing(rep: dict) -> Set[str]:
    return {r["id"] for r in rep.get("rules", []) if r.get("status") == "FAIL"}


def judge_negative(rc: int, rep: dict, expect_rules: Iterable[str], expect_rc: int) -> Tuple[bool, str, str]:
    """A negative fixture passes only if rejected with the expected exit code AND the expected rule ids FAIL."""
    want = set(expect_rules)
    got = failing(rep)
    if rc == EXIT_PASS:
        return False, "NEGATIVE_UNEXPECTED_SUCCESS", "validator accepted a known-bad fixture (exit 0)"
    if rc != expect_rc or not want <= got:
        return False, "NEGATIVE_WRONG_REASON", f"exit {rc} (want {expect_rc}); failing={sorted(got)} want>={sorted(want)}"
    return True, "OK", f"exit {rc}; failing={sorted(got)}"


def run(mode: str = "static-evidence", policies: Optional[Path] = None,
        expectations: Optional[Tuple[Dict[str, Set[str]], Dict[str, str]]] = None,
        evidence_runs: Optional[Path] = None, fixtures: Optional[Path] = None) -> ModuleResult:
    pol = Path(policies or ENTRA / "policies")
    fx = Path(fixtures or FIXTURES)
    ev_runs = Path(evidence_runs or EVIDENCE_RUNS)
    res = ModuleResult(MODULE, f"acceptance/modules/entra_offline.py@{VERSION}",
                       {"prs": [4], "paths": ["identity/entra", "tests/entra", U.rel(ev_runs)]},
                       mode, git_sha=U.git_sha())

    # 1. baseline policies must pass schema + baseline (the module's own positive case)
    rc, rep = validate(pol)
    code = {EXIT_BASELINE_FAIL: "BASELINE_RULE_FAILED", EXIT_MALFORMED: "INPUT_MALFORMED"}.get(rc, "TOOL_ERROR")
    res.add(check("ENTRA-BASE-001", "baseline CA policies pass all SCHEMA-* and BASE-* rules", "positive",
                  rc == EXIT_PASS and rep.get("overall") == "PASS", code,
                  f"exit {rc}; failing={sorted(failing(rep))}", [U.rel(pol)]))
    res.add(check("ENTRA-CLAIM-001", "validator report is offline-synthetic and claims no tenant state", "integrity",
                  rep.get("mode") == "offline-synthetic" and rep.get("tenantStateClaimed") is False,
                  "CLAIM_VIOLATION", f"mode={rep.get('mode')} tenantStateClaimed={rep.get('tenantStateClaimed')}"))

    # 2. every declared negative / malformed fixture is rejected for its declared rule
    base_neg, malformed = expectations or module_expectations()
    for name, rules in sorted(base_neg.items()):
        rc, rep = validate(fx / name)
        ok, code, det = judge_negative(rc, rep, rules, EXIT_BASELINE_FAIL)
        res.add(check(f"ENTRA-NEG-{name[:-5]}", f"{name} rejected by {sorted(rules)}", "negative", ok, code, det,
                      [U.rel(fx / name)]))
    for name, rule in sorted(malformed.items()):
        rc, rep = validate(fx / name)
        ok, code, det = judge_negative(rc, rep, {rule}, EXIT_MALFORMED)
        res.add(check(f"ENTRA-MAL-{name[:-5]}", f"{name} fails closed with {rule}", "negative", ok, code, det,
                      [U.rel(fx / name)]))
    res.add(check("ENTRA-NEG-COUNT", "module declares >=1 baseline negative and >=1 malformed fixture", "negative",
                  bool(base_neg) and bool(malformed), "NEGATIVE_COUNT",
                  f"baseline_negatives={len(base_neg)} malformed={len(malformed)}"))

    # 3. committed evidence runs still verify against current inputs
    runs = sorted(p for p in ev_runs.glob("*") if (p / "SHA256SUMS").is_file()) if ev_runs.is_dir() else []
    if not runs:
        res.add(check("ENTRA-EV-000", "committed Entra evidence run present", "integrity", False, "EVIDENCE_MISSING",
                      f"none under {U.rel(ev_runs)}"))
    for r in runs:
        rc, out = U.py(str(GEN), "--verify", str(r))
        code = ("EVIDENCE_INPUT_DRIFT" if re.search(r"input (changed|missing|added)", out) else
                "CLAIM_VIOLATION" if "tenantStateClaimed" in out else "EVIDENCE_HASH_MISMATCH")
        res.add(check(f"ENTRA-EV-{r.name}", f"evidence run {r.name} verifies (hashes + input hashes + claims)",
                      "integrity", rc == 0, code, out.strip().replace("\n", " | ")[:400], [U.rel(r)]))
    res.evidence = U.evidence_entries([f for r in runs for f in (r / "SHA256SUMS", r / "SUMMARY.json",
                                                                  r / "validation-report.json")])

    # 4. live-offline: also run the module's own unit tests and fixture drift check
    if mode == "live-offline":
        rc, out = U.py("-m", "unittest", "discover", "-s", str(TESTS))
        m = re.search(r"Ran (\d+) test", out)
        res.add(check("ENTRA-LIVE-001", "tests/entra unittest suite passes", "positive",
                      rc == 0 and bool(m) and int(m.group(1)) > 0, "UNIT_TESTS_FAILED",
                      (m.group(0) if m else "") + " " + out.strip().splitlines()[-1]))
        rc, out = U.py(str(TESTS / "make_fixtures.py"), "--check")
        res.add(check("ENTRA-LIVE-002", "fixtures match their generator (no drift)", "integrity", rc == 0,
                      "EVIDENCE_INPUT_DRIFT", out.strip()[-200:]))
    return res
