#!/usr/bin/env python3
"""Generate the SYNTHETIC acceptance-contract fixtures (stdlib only).

  python3 tests/acceptance-contract/make_fixtures.py          # (re)write fixtures/
  python3 tests/acceptance-contract/make_fixtures.py --check  # exit 1 if committed fixtures drifted

fixtures/repo/ is a miniature repo root (pass it as --repo-root) holding evidence bundles
described by evidence/shared/evidence-manifest.schema.json. fixtures/docs/{valid,invalid}/ hold
acceptance documents; fixtures/INDEX.json records the expected decision or error codes for each.
Nothing here is a real test result: every document sets "synthetic": true and every log says SYNTHETIC.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = HERE / "fixtures"
TESTED = "49122f2457aff41f14a3f3dec4ae378ac0147cff"  # overnight/integration head this slice was built on
OTHER = "7f50348" + "0" * 33  # deliberately different commit (40 hex) for mismatch fixtures
RECORDER, REVIEWER, APPROVER = "worker-a (recorder)", "reviewer-b (independent)", "owner (approver)"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def j(o) -> str:
    return json.dumps(o, indent=2, sort_keys=False) + "\n"


def bundle(files: dict, bid: str, anchor_commit: str, *, tamper: str | None = None, uncovered=(), bad_manifest=False):
    """Return {repo-relative path: text} for one bundle under evidence/<bid>/."""
    root = f"evidence/{bid}"
    out = {f"{root}/{k}": v for k, v in files.items()}
    sums = []
    for k, v in files.items():
        if k in uncovered:
            continue
        h = sha(v.encode())
        if k == tamper:
            h = sha(b"tampered")
        sums.append(f"{h}  {k}")
    out[f"{root}/SHA256SUMS"] = "\n".join(sums) + "\n"
    excl = [{"path": "SHA256SUMS", "reason": "self-reference"}, {"path": "MANIFEST.json", "reason": "added-after-run"}]
    excl += [{"path": u, "reason": "added-after-run", "note": "SYNTHETIC: deliberately not hashed"} for u in uncovered]
    m = {
        "schema_version": "1.0.0",
        "bundle": {"id": bid, "root": root, "kind": "static-synth"},
        "producer": {"script": "tests/acceptance-contract/make_fixtures.py", "source_commit": TESTED},
        "hashes": {"file": "SHA256SUMS", "base": "bundle", "algorithm": "sha256"},
        "commands": {"file": "logs/COMMANDS.tsv", "format": "aws-3col", "rows_written_by": "producer-script"},
        "exclusions": excl,
        "anchors": [{"type": "git-commit", "ref": anchor_commit}],
    }
    if bad_manifest:
        m["bundle"]["kind"] = "not-a-kind"
    out[f"{root}/MANIFEST.json"] = j(m)
    return out


def log(name: str, rc: int) -> str:
    return f"SYNTHETIC fixture log for {name}; not a real run.\nresult text: {'all checks ok' if rc == 0 else 'check failed'}\n# exit_code: {rc}\n"


DEMO_FILES = {
    "logs/ACC-DEMO-001.log": log("ACC-DEMO-001", 0),
    "logs/ACC-DEMO-002.log": log("ACC-DEMO-002", 0),
    "logs/ACC-DEMO-FAIL.log": log("ACC-DEMO-FAIL", 1),
    "logs/UNCOVERED.log": log("UNCOVERED", 0),
    "logs/COMMANDS.tsv": "ACC-DEMO-001.log\t0\tpython3 -m unittest discover -s evidence/shared/tests\n"
                         "ACC-DEMO-002.log\t0\tbash scripts/validate-all.sh --python-only\n"
                         "ACC-DEMO-FAIL.log\t1\tpython3 synthetic_failing_check.py\n"
                         "UNCOVERED.log\t0\ttrue\n",
}
REPO_FILES: dict[str, str] = {}
REPO_FILES.update(bundle(DEMO_FILES, "acceptance-demo", TESTED, uncovered=("logs/UNCOVERED.log",)))
REPO_FILES.update(bundle({"logs/ACC-DEMO-001.log": log("ACC-DEMO-001 at other commit", 0)}, "acceptance-other-commit", OTHER))
REPO_FILES.update(bundle({"logs/ACC-DEMO-001.log": log("ACC-DEMO-001", 0), "logs/OTHER.log": log("OTHER", 0)},
                         "acceptance-tampered", TESTED, tamper="logs/OTHER.log"))
REPO_FILES.update(bundle({"logs/ACC-DEMO-001.log": log("ACC-DEMO-001", 0)}, "acceptance-bad-manifest", TESTED, bad_manifest=True))


def ref(bid: str, name: str) -> dict:
    return {"manifest": f"evidence/{bid}/MANIFEST.json", "artifact": f"evidence/{bid}/{name}",
            "sha256": sha(REPO_FILES[f"evidence/{bid}/{name}"].encode())}


def review(verdict="concur", reviewer=REVIEWER, commit=TESTED):
    return {"reviewer": reviewer, "reviewed_commit": commit, "verdict": verdict,
            "finding": "SYNTHETIC: re-ran the command at the tested commit and compared with the evidence log.", "date": "2026-10-28"}


def req(rid, result, *, required=True, execution="executed", exit_obs=0, refs=None, reviews=None, **extra):
    q = {
        "id": rid,
        "scope": "SYNTHETIC fixture scope",
        "rationale": "SYNTHETIC fixture rationale",
        "required": required,
        "source": {"type": "project_decision", "reference": "coordination/tasks.json#acceptance_conditions_for_main"},
        "tested_source_commit": TESTED,
        "check": {"command": "python3 -m unittest discover -s evidence/shared/tests", "expected": {"exit_code": 0}, "execution": execution},
        "evidence_refs": refs if refs is not None else [],
        "assumptions": ["SYNTHETIC: stdlib Python 3.12+ on a clean checkout"],
        "exclusions": ["No production systems, tenants or cloud accounts are touched"],
        "verification_method": "automated_test",
        "result": result,
        "reviewer_findings": reviews if reviews is not None else [],
    }
    if execution == "executed":
        q["check"]["observed"] = {"exit_code": exit_obs}
    q.update(extra)
    return q


def doc(reqs, doc_id="acceptance-fixture"):
    return {"schema_version": "1.0.0",
            "document": {"id": doc_id, "title": "SYNTHETIC acceptance fixture", "repository": "onnxscibroccoli/bank-it-operations-lab",
                         "tested_source_commit": TESTED, "recorded_by": RECORDER, "synthetic": True},
            "requirements": reqs}


P1 = lambda **kw: req("ACC-DEMO-001", "PASS", refs=[ref("acceptance-demo", "logs/ACC-DEMO-001.log")], reviews=[review()], **kw)
P2 = lambda: req("ACC-DEMO-002", "PASS", refs=[ref("acceptance-demo", "logs/ACC-DEMO-002.log")], reviews=[review()],
                 verification_method="demonstration")
NA = lambda: req("ACC-DEMO-003", "NOT_APPLICABLE", execution="not_run",
                 result_rationale="SYNTHETIC: control applies to Windows hosts; none are in scope for this lab.",
                 source={"type": "standard", "reference": "SYNTHETIC: FFIEC IT Handbook, Architecture, Infrastructure, and Operations (June 2021)"})
ADV = lambda: req("ACC-DEMO-004", "UNKNOWN", required=False, execution="skipped",
                  result_rationale="SYNTHETIC: optional Node toolchain not installed; check skipped.",
                  source={"type": "vendor_guidance", "reference": "SYNTHETIC: vendor doc URL"})
FAIL_EX = lambda **ex: req("ACC-DEMO-005", "FAIL", exit_obs=1, refs=[ref("acceptance-demo", "logs/ACC-DEMO-FAIL.log")], reviews=[review()],
                           source={"type": "job_description", "reference": "SYNTHETIC: posting section 'Responsibilities'"},
                           exception=dict({"disposition": "compensating_control", "approver": APPROVER, "approved_on": "2026-10-28",
                                           "expires_on": "2026-11-28", "rationale": "SYNTHETIC", "reference": "SYNTHETIC-TICKET-1",
                                           "compensating_control": "SYNTHETIC: manual weekly review"}, **ex))
UNK_REQ = lambda: req("ACC-DEMO-006", "UNKNOWN", execution="unavailable",
                      result_rationale="SYNTHETIC: PostgreSQL binaries unavailable on the runner.")


def mutate(base_reqs, i, fn):
    reqs = copy.deepcopy(base_reqs)
    fn(reqs[i])
    return doc(reqs)


BASE = [P1(), P2(), NA(), ADV()]
VALID = {
    "accept": (doc(BASE), "AUTOMATIC_TECHNICAL_ACCEPTANCE"),
    "blocked-fail-with-exception": (doc(BASE + [FAIL_EX()]), "BLOCKED"),
    "blocked-required-unknown": (doc(BASE + [UNK_REQ()]), "BLOCKED"),
    "blocked-pass-without-review": (mutate(BASE, 0, lambda q: q.update(reviewer_findings=[])), "BLOCKED"),
    "blocked-pass-disputed": (mutate(BASE, 0, lambda q: q["reviewer_findings"].append(review("dispute", "reviewer-c"))), "BLOCKED"),
    "blocked-empty": (doc([]), "BLOCKED"),
}


def _set(path, value):
    def f(q):
        node = q
        for k in path[:-1]:
            node = node[k]
        if value is DELETE:
            del node[path[-1]]
        else:
            node[path[-1]] = value
    return f


DELETE = object()
B5 = BASE + [FAIL_EX()]
INVALID = {
    # rule: PASS/FAIL need evidence
    "pass-without-evidence": (mutate(BASE, 0, _set(["evidence_refs"], [])), ["E_RESULT_NEEDS_EVIDENCE"]),
    "fail-without-evidence": (mutate(B5, 4, _set(["evidence_refs"], [])), ["E_RESULT_NEEDS_EVIDENCE"]),
    # rule: evidence refs must resolve to evidence records
    "evidence-missing-artifact": (mutate(BASE, 0, lambda q: q["evidence_refs"][0].update(artifact="evidence/acceptance-demo/logs/NOPE.log")), ["E_EVIDENCE_UNRESOLVED"]),
    "evidence-missing-manifest": (mutate(BASE, 0, lambda q: q["evidence_refs"][0].update(manifest="evidence/nope/MANIFEST.json")), ["E_EVIDENCE_UNRESOLVED"]),
    "evidence-outside-bundle": (mutate(BASE, 0, lambda q: q["evidence_refs"][0].update(artifact="evidence/acceptance-other-commit/logs/ACC-DEMO-001.log")), ["E_EVIDENCE_UNRESOLVED"]),
    "evidence-hash-mismatch": (mutate(BASE, 0, lambda q: q["evidence_refs"][0].update(sha256="0" * 64)), ["E_EVIDENCE_HASH_MISMATCH", "E_EVIDENCE_NOT_COVERED"]),
    "evidence-not-covered": (mutate(BASE, 0, _set(["evidence_refs"], [ref("acceptance-demo", "logs/UNCOVERED.log")])), ["E_EVIDENCE_NOT_COVERED"]),
    "evidence-manifest-invalid": (mutate(BASE, 0, _set(["evidence_refs"], [ref("acceptance-bad-manifest", "logs/ACC-DEMO-001.log")])), ["E_EVIDENCE_MANIFEST_INVALID"]),
    "evidence-bundle-tampered": (mutate(BASE, 0, _set(["evidence_refs"], [ref("acceptance-tampered", "logs/ACC-DEMO-001.log")])), ["E_EVIDENCE_BUNDLE_HASHES"]),
    "evidence-other-commit": (mutate(BASE, 0, _set(["evidence_refs"], [ref("acceptance-other-commit", "logs/ACC-DEMO-001.log")])), ["E_EVIDENCE_COMMIT_MISMATCH"]),
    "evidence-bad-sha256-format": (mutate(BASE, 0, lambda q: q["evidence_refs"][0].update(sha256="xyz")), ["E_SCHEMA"]),
    # rule: skipped / unavailable / not run stay UNKNOWN
    "skipped-but-pass": (mutate(BASE, 0, lambda q: (q["check"].update(execution="skipped"), q["check"].pop("observed"))), ["E_RESULT_NOT_EXECUTED"]),
    "unavailable-but-fail": (mutate(B5, 4, lambda q: (q["check"].update(execution="unavailable"), q["check"].pop("observed"))), ["E_RESULT_NOT_EXECUTED"]),
    "not-run-but-pass": (mutate(BASE, 0, lambda q: (q["check"].update(execution="not_run"), q["check"].pop("observed"))), ["E_RESULT_NOT_EXECUTED"]),
    "skipped-but-not-applicable": (mutate(BASE, 2, _set(["check", "execution"], "skipped")), ["E_RESULT_NOT_EXECUTED"]),
    "executed-without-observation": (mutate(BASE, 0, lambda q: q["check"].pop("observed")), ["E_RESULT_NO_OBSERVATION"]),
    "observation-without-execution": (mutate(BASE, 3, _set(["check", "observed"], {"exit_code": 0})), ["E_RESULT_INCONSISTENT"]),
    # rule: result consistent with expected vs observed
    "pass-but-exit-mismatch": (mutate(BASE, 0, _set(["check", "observed", "exit_code"], 1)), ["E_RESULT_INCONSISTENT"]),
    "pass-but-output-unmatched": (mutate(BASE, 0, lambda q: (q["check"]["expected"].update(output_contains="OK"), q["check"]["observed"].update(output_contains_matched=False))), ["E_RESULT_INCONSISTENT"]),
    "fail-but-expectation-met": (mutate(B5, 4, _set(["check", "observed", "exit_code"], 0)), ["E_RESULT_INCONSISTENT"]),
    "not-applicable-but-executed": (mutate(BASE, 2, _set(["check"], {"command": "true", "expected": {"exit_code": 0}, "execution": "executed", "observed": {"exit_code": 0}})), ["E_RESULT_INCONSISTENT"]),
    # rule: NOT_APPLICABLE / UNKNOWN need rationale
    "not-applicable-without-rationale": (mutate(BASE, 2, _set(["result_rationale"], DELETE)), ["E_RATIONALE_REQUIRED"]),
    "not-applicable-blank-rationale": (mutate(BASE, 2, _set(["result_rationale"], "   ")), ["E_RATIONALE_REQUIRED"]),
    "unknown-without-rationale": (mutate(BASE, 3, _set(["result_rationale"], DELETE)), ["E_RATIONALE_REQUIRED"]),
    # rule: exception dispositions well-formed
    "exception-on-pass": (mutate(B5, 0, _set(["exception"], copy.deepcopy(B5[4]["exception"]))), ["E_EXCEPTION_MALFORMED"]),
    "exception-unknown-disposition": (mutate(B5, 4, lambda q: q["exception"].update(disposition="waived")), ["E_SCHEMA"]),
    "exception-missing-approver": (mutate(B5, 4, lambda q: q["exception"].pop("approver")), ["E_SCHEMA"]),
    "exception-missing-expiry": (mutate(B5, 4, lambda q: q["exception"].pop("expires_on")), ["E_EXCEPTION_MALFORMED"]),
    "exception-expiry-before-approval": (mutate(B5, 4, lambda q: q["exception"].update(expires_on="2026-10-01")), ["E_EXCEPTION_MALFORMED"]),
    "exception-impossible-date": (mutate(B5, 4, lambda q: q["exception"].update(approved_on="2026-02-30")), ["E_EXCEPTION_MALFORMED"]),
    "exception-self-approved": (mutate(B5, 4, lambda q: q["exception"].update(approver=RECORDER)), ["E_EXCEPTION_MALFORMED"]),
    "exception-compensating-without-control": (mutate(B5, 4, lambda q: q["exception"].pop("compensating_control")), ["E_EXCEPTION_MALFORMED"]),
    "exception-extra-key": (mutate(B5, 4, lambda q: q["exception"].update(auto_accept=True)), ["E_SCHEMA"]),
    # rule: independent reviewer findings
    "reviewer-is-recorder": (mutate(BASE, 0, _set(["reviewer_findings"], [review(reviewer=RECORDER)])), ["E_REVIEWER_NOT_INDEPENDENT"]),
    "review-of-other-commit": (mutate(BASE, 0, _set(["reviewer_findings"], [review(commit=OTHER)])), ["E_REVIEW_COMMIT_MISMATCH"]),
    "review-bad-verdict": (mutate(BASE, 0, _set(["reviewer_findings"], [review(verdict="lgtm")])), ["E_SCHEMA"]),
    # rule: exact tested commit, stable IDs, required fields, enums
    "short-commit-sha": (mutate(BASE, 0, _set(["tested_source_commit"], TESTED[:7])), ["E_SCHEMA"]),
    "branch-name-as-commit": (mutate(BASE, 0, _set(["tested_source_commit"], "main")), ["E_SCHEMA"]),
    "commit-differs-from-document": (mutate(BASE, 0, _set(["tested_source_commit"], OTHER)), ["E_COMMIT_MISMATCH"]),
    "duplicate-id": (mutate(BASE, 1, _set(["id"], "ACC-DEMO-001")), ["E_DUPLICATE_ID"]),
    "bad-id-format": (mutate(BASE, 0, _set(["id"], "req-1")), ["E_SCHEMA"]),
    "bad-source-type": (mutate(BASE, 0, lambda q: q["source"].update(type="blog_post")), ["E_SCHEMA"]),
    "missing-source-reference": (mutate(BASE, 0, lambda q: q["source"].pop("reference")), ["E_SCHEMA"]),
    "missing-check-command": (mutate(BASE, 0, lambda q: q["check"].pop("command")), ["E_SCHEMA"]),
    "missing-assumptions": (mutate(BASE, 0, _set(["assumptions"], DELETE)), ["E_SCHEMA"]),
    "missing-verification-method": (mutate(BASE, 0, _set(["verification_method"], DELETE)), ["E_SCHEMA"]),
    "bad-result-value": (mutate(BASE, 0, _set(["result"], "PARTIAL")), ["E_SCHEMA"]),
    "required-not-boolean": (mutate(BASE, 0, _set(["required"], "yes")), ["E_SCHEMA"]),
}


def render() -> dict[Path, str]:
    files = {FX / "repo" / k: v for k, v in REPO_FILES.items()}
    index = {"tested_source_commit": TESTED, "repo_root": "repo", "valid": {}, "invalid": {}}
    for name, (d, decision) in VALID.items():
        files[FX / "docs" / "valid" / f"{name}.json"] = j(d)
        index["valid"][name] = {"decision": decision}
    for name, (d, codes) in INVALID.items():
        files[FX / "docs" / "invalid" / f"{name}.json"] = j(d)
        index["invalid"][name] = {"errors": codes}
    files[FX / "INDEX.json"] = j(index)
    return files


def main(argv) -> int:
    files = render()
    if "--check" in argv:
        on_disk = {p for p in FX.rglob("*") if p.is_file()}
        bad = sorted(str(p.relative_to(HERE)) for p in files if not p.is_file() or p.read_text() != files[p])
        extra = sorted(str(p.relative_to(HERE)) for p in on_disk - set(files))
        for b in bad:
            print(f"DRIFT {b}")
        for e in extra:
            print(f"EXTRA {e}")
        print("FIXTURES OK" if not (bad or extra) else "FIXTURES DRIFTED: run make_fixtures.py")
        return 0 if not (bad or extra) else 1
    for p, text in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    print(f"wrote {len(files)} files under {FX.relative_to(HERE.parents[1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
