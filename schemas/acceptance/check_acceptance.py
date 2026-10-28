#!/usr/bin/env python3
"""Acceptance-contract checks for bank-it-operations-lab (stdlib only).

This is NOT a separate validator. It reuses evidence/shared/validate_evidence.py:
  * structure: the shared stdlib schema checker (_check / Report) on
    schemas/acceptance/acceptance-requirements.schema.json, after inlining its $refs
    into evidence/shared/evidence-manifest.schema.json;
  * evidence: each evidence ref must resolve to a bundle MANIFEST.json that passes the
    shared `manifest` subcommand and a hashes file that passes the shared `hashes`
    subcommand, and the artifact must be listed in that hashes file with the same sha256.
On top of that it adds only the contract-level relationship rules (result vs execution vs
evidence, NOT_APPLICABLE rationale, exception dispositions, reviewer independence) and the
aggregate decision.

Usage:
  python3 schemas/acceptance/check_acceptance.py DOC.json [--repo-root DIR] [--json]

Exit codes: 0 = valid and AUTOMATIC_TECHNICAL_ACCEPTANCE, 4 = valid but BLOCKED,
            1 = INVALID document (errors), 2 = usage / unreadable input.
Every error line starts with a stable code in brackets, e.g. [E_RESULT_NEEDS_EVIDENCE].
Automatic technical acceptance is a lab gate only; it is not an audit or sign-off.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "evidence" / "shared"))
import validate_evidence as ve  # noqa: E402  (shared validator; reused, not copied)

SCHEMA = HERE / "acceptance-requirements.schema.json"
HEX40 = "0123456789abcdef"
EXIT_ACCEPT, EXIT_INVALID, EXIT_USAGE, EXIT_BLOCKED = 0, 1, 2, 4


def load_schema(path: Path = SCHEMA) -> dict:
    """Load the schema and inline every {"$ref": "<file>#<json-pointer>"} (the shared
    checker has no $ref support). Unresolvable refs raise, so a broken link fails closed."""
    def resolve(node, base: Path):
        if isinstance(node, dict):
            if "$ref" in node:
                file_part, _, pointer = node["$ref"].partition("#")
                target_file = (base.parent / file_part).resolve() if file_part else base
                target = json.loads(target_file.read_text())
                for tok in [t for t in pointer.split("/") if t]:
                    target = target[tok.replace("~1", "/").replace("~0", "~")]
                return resolve(copy.deepcopy(target), target_file)
            return {k: resolve(v, base) for k, v in node.items()}
        if isinstance(node, list):
            return [resolve(v, base) for v in node]
        return node
    return resolve(json.loads(path.read_text()), path.resolve())


def _shared(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = ve.main(list(argv))
    return rc, out.getvalue()


def _date(s) -> dt.date | None:
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def _blank(s) -> bool:
    return not isinstance(s, str) or not s.strip()


class Checker:
    def __init__(self, repo_root: Path):
        self.root = repo_root.resolve()
        self.r = ve.Report()
        self._bundle_cache: dict[str, tuple[dict | None, dict[str, str]]] = {}

    def err(self, code: str, where: str, msg: str) -> None:
        self.r.err(f"[{code}] {where}: {msg}")

    # ---------- evidence resolution (via the shared validator)
    def _bundle(self, manifest_rel: str, where: str):
        if manifest_rel in self._bundle_cache:
            return self._bundle_cache[manifest_rel]
        result: tuple[dict | None, dict[str, str]] = (None, {})
        mpath = (self.root / manifest_rel).resolve()
        if not mpath.is_file() or self.root not in mpath.parents:
            self.err("E_EVIDENCE_UNRESOLVED", where, f"manifest {manifest_rel} not found under repo root")
        else:
            rc, out = _shared("manifest", str(mpath))
            if rc != 0:
                detail = "; ".join(l for l in out.splitlines() if l.startswith("ERROR"))
                self.err("E_EVIDENCE_MANIFEST_INVALID", where, f"{manifest_rel} rejected by shared validator: {detail}")
            else:
                m = json.loads(mpath.read_text())
                broot = (self.root / m["bundle"]["root"]).resolve()
                if mpath.parent != broot:
                    self.err("E_EVIDENCE_MANIFEST_INVALID", where, f"{manifest_rel} is not in its bundle root {m['bundle']['root']}")
                else:
                    sums = broot / m["hashes"]["file"]
                    base = self.root if m["hashes"]["base"] == "repo" else broot
                    rc, out = _shared("hashes", str(sums), "--base", str(base)) if sums.is_file() else (1, "ERROR hashes file missing")
                    if rc != 0:
                        detail = "; ".join(l for l in out.splitlines() if l.startswith("ERROR")).replace(str(self.root) + "/", "")
                        self.err("E_EVIDENCE_BUNDLE_HASHES", where, f"bundle {m['bundle']['id']} hashes do not verify: {detail}")
                    else:
                        listed = {}
                        for line in sums.read_text().splitlines():
                            mm = ve.SUM_LINE.match(line)
                            if mm:
                                listed[str((base / mm.group(2)).resolve())] = mm.group(1)
                        result = (m, listed)
        self._bundle_cache[manifest_rel] = result
        return result

    def evidence_ref(self, ref: dict, tested: str, where: str) -> None:
        m, listed = self._bundle(ref["manifest"], where)
        if m is None:
            return
        broot = (self.root / m["bundle"]["root"]).resolve()
        art = (self.root / ref["artifact"]).resolve()
        if broot not in art.parents:
            self.err("E_EVIDENCE_UNRESOLVED", where, f"artifact {ref['artifact']} is outside bundle root {m['bundle']['root']}")
            return
        if not art.is_file():
            self.err("E_EVIDENCE_UNRESOLVED", where, f"artifact {ref['artifact']} does not exist")
            return
        if ve.sha256(art) != ref["sha256"]:
            self.err("E_EVIDENCE_HASH_MISMATCH", where, f"artifact {ref['artifact']} sha256 differs from the reference")
        if listed.get(str(art)) != ref["sha256"]:
            self.err("E_EVIDENCE_NOT_COVERED", where, f"artifact {ref['artifact']} is not listed with this sha256 in bundle hashes file {m['hashes']['file']}")
        if not any(a["type"] == "git-commit" and a["ref"] == tested for a in m["anchors"]):
            self.err("E_EVIDENCE_COMMIT_MISMATCH", where, f"bundle {m['bundle']['id']} has no git-commit anchor for tested commit {tested}")

    # ---------- per-requirement relationship rules
    def requirement(self, q: dict, doc: dict, i: int) -> None:
        where = f"$.requirements[{i}]({q.get('id')})"
        tested = doc["document"]["tested_source_commit"]
        author = doc["document"]["recorded_by"]
        res, chk = q["result"], q["check"]
        execution, observed, expected = chk["execution"], chk.get("observed"), chk["expected"]
        if not isinstance(q["required"], bool):
            self.err("E_SCHEMA", where, "required must be a boolean")
        if q["tested_source_commit"] != tested:
            self.err("E_COMMIT_MISMATCH", where, f"tested_source_commit {q['tested_source_commit']} != document {tested}")
        # results vs evidence
        if res in ("PASS", "FAIL") and not q["evidence_refs"]:
            self.err("E_RESULT_NEEDS_EVIDENCE", where, f"{res} without evidence_refs; record UNKNOWN until evidence exists")
        for j, ref in enumerate(q["evidence_refs"]):
            self.evidence_ref(ref, tested, f"{where}.evidence_refs[{j}]")
        # results vs execution
        if execution in ("skipped", "unavailable") and res != "UNKNOWN":
            self.err("E_RESULT_NOT_EXECUTED", where, f"execution={execution} must give UNKNOWN, not {res}")
        if execution == "not_run" and res not in ("UNKNOWN", "NOT_APPLICABLE"):
            self.err("E_RESULT_NOT_EXECUTED", where, f"execution=not_run must give UNKNOWN or NOT_APPLICABLE, not {res}")
        if res == "NOT_APPLICABLE" and execution == "executed":
            self.err("E_RESULT_INCONSISTENT", where, "NOT_APPLICABLE but the check was executed; record its PASS/FAIL result instead")
        if execution == "executed" and observed is None:
            self.err("E_RESULT_NO_OBSERVATION", where, "execution=executed requires check.observed")
        if execution != "executed" and observed is not None:
            self.err("E_RESULT_INCONSISTENT", where, f"check.observed present but execution={execution}")
        if execution == "executed" and observed is not None and res in ("PASS", "FAIL"):
            met = observed["exit_code"] == expected["exit_code"]
            if "output_contains" in expected:
                met = met and observed.get("output_contains_matched") is True
            if (res == "PASS") != met:
                self.err("E_RESULT_INCONSISTENT", where,
                         f"{res} but observed exit {observed['exit_code']} vs expected {expected['exit_code']}"
                         + (f", output matched={observed.get('output_contains_matched')}" if "output_contains" in expected else ""))
        if res in ("NOT_APPLICABLE", "UNKNOWN") and _blank(q.get("result_rationale")):
            self.err("E_RATIONALE_REQUIRED", where, f"{res} requires a non-blank result_rationale")
        # exception disposition
        ex = q.get("exception")
        if ex is not None:
            w = f"{where}.exception"
            if res not in ("FAIL", "UNKNOWN"):
                self.err("E_EXCEPTION_MALFORMED", w, f"exception only allowed on FAIL or UNKNOWN, not {res}")
            a, e = _date(ex["approved_on"]), _date(ex.get("expires_on")) if "expires_on" in ex else None
            if a is None:
                self.err("E_EXCEPTION_MALFORMED", w, f"approved_on {ex['approved_on']!r} is not a valid date")
            if ex["disposition"] != "rejected":
                if "expires_on" not in ex:
                    self.err("E_EXCEPTION_MALFORMED", w, f"{ex['disposition']} requires expires_on")
                elif e is None:
                    self.err("E_EXCEPTION_MALFORMED", w, f"expires_on {ex['expires_on']!r} is not a valid date")
                elif a is not None and e <= a:
                    self.err("E_EXCEPTION_MALFORMED", w, "expires_on must be after approved_on")
            if ex["disposition"] == "compensating_control" and _blank(ex.get("compensating_control")):
                self.err("E_EXCEPTION_MALFORMED", w, "compensating_control disposition requires compensating_control text")
            if ex["approver"].strip() == author.strip():
                self.err("E_EXCEPTION_MALFORMED", w, "approver must not be the recorder (self-approved exception)")
        # independent review
        for j, f in enumerate(q["reviewer_findings"]):
            w = f"{where}.reviewer_findings[{j}]"
            if f["reviewer"].strip() == author.strip():
                self.err("E_REVIEWER_NOT_INDEPENDENT", w, f"reviewer {f['reviewer']!r} is the recorder")
            if f["reviewed_commit"] != tested:
                self.err("E_REVIEW_COMMIT_MISMATCH", w, f"reviewed {f['reviewed_commit']} but tested commit is {tested}")
            if _date(f["date"]) is None:
                self.err("E_SCHEMA", w, f"date {f['date']!r} is not a valid date")

    def check(self, doc) -> None:
        ve._check(load_schema(), doc, "$", self.r)  # shared structural checker
        if self.r.errors:
            self.r.errors[:] = [f"[E_SCHEMA] {e}" for e in self.r.errors]
            return
        if not isinstance(doc["document"].get("synthetic", False), bool):
            self.err("E_SCHEMA", "$.document.synthetic", "must be a boolean")
        seen: set[str] = set()
        for i, q in enumerate(doc["requirements"]):
            if q["id"] in seen:
                self.err("E_DUPLICATE_ID", f"$.requirements[{i}]", f"duplicate id {q['id']}")
            seen.add(q["id"])
            self.requirement(q, doc, i)


def decide(doc: dict) -> dict:
    """Aggregate decision for a VALID document. Fail closed: anything not clearly accepted blocks."""
    blockers = []
    reqs = doc["requirements"]
    if not reqs:
        blockers.append({"id": None, "reason": "no requirements: nothing to accept"})
    for q in reqs:
        res, rid = q["result"], q["id"]
        note = " (exception recorded: human decision, not automatic)" if "exception" in q else ""
        if res == "FAIL":
            blockers.append({"id": rid, "reason": "FAIL" + note})
        elif res == "UNKNOWN" and q["required"]:
            blockers.append({"id": rid, "reason": f"required UNKNOWN (execution={q['check']['execution']})" + note})
        if res == "PASS" and q["required"]:
            v = [f["verdict"] for f in q["reviewer_findings"]]
            if "dispute" in v:
                blockers.append({"id": rid, "reason": "independent reviewer disputes PASS"})
            elif "concur" not in v:
                blockers.append({"id": rid, "reason": "required PASS lacks an independent reviewer concurrence"})
    counts = {k: sum(1 for q in reqs if q["result"] == k) for k in ("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE")}
    return {
        "decision": "BLOCKED" if blockers else "AUTOMATIC_TECHNICAL_ACCEPTANCE",
        "tested_source_commit": doc["document"]["tested_source_commit"],
        "synthetic": doc["document"].get("synthetic", False),
        "counts": counts,
        "blockers": blockers,
    }


def evaluate(doc_path: Path, repo_root: Path) -> dict:
    try:
        doc = json.loads(Path(doc_path).read_text())
    except (OSError, json.JSONDecodeError) as e:
        return {"valid": False, "decision": "INVALID", "errors": [f"[E_UNREADABLE] {doc_path}: {e}"], "exit": EXIT_USAGE}
    c = Checker(repo_root)
    c.check(doc)
    if c.r.errors:
        return {"valid": False, "decision": "INVALID", "errors": c.r.errors, "exit": EXIT_INVALID}
    d = decide(doc)
    d.update(valid=True, errors=[], exit=EXIT_ACCEPT if d["decision"] == "AUTOMATIC_TECHNICAL_ACCEPTANCE" else EXIT_BLOCKED)
    return d


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("doc")
    p.add_argument("--repo-root", default=str(REPO), help="root that evidence paths are relative to (default: this repo)")
    p.add_argument("--json", action="store_true", help="print the full report as JSON")
    a = p.parse_args(argv)
    rep = evaluate(Path(a.doc), Path(a.repo_root))
    if a.json:
        print(json.dumps(rep, indent=2, sort_keys=True))
    else:
        for e in rep["errors"]:
            print(f"ERROR {e}")
        for b in rep.get("blockers", []):
            print(f"BLOCKER {b['id']}: {b['reason']}")
        print(f"DECISION {rep['decision']}" + (" (synthetic fixture)" if rep.get("synthetic") else ""))
    return rep["exit"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
