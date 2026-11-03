#!/usr/bin/env python3
"""Final acceptance decision for one run.sh output (finding C4).

  decide.py OUT --sha SHA [--reviews FILE] [--stage DIR] [--decision-out FILE] [--contract-out FILE]

1. verify_results.verify(OUT, expect_sha=SHA)   (C1 inventory, C2 gate, C3 complete records, binding to SHA)
2. Export the run into worker A's shared contract (schemas/acceptance/acceptance-requirements.schema.json):
   one requirement per inventory entry, evidence = this run's logs staged as an evidence bundle with a
   MANIFEST.json anchored to SHA; reviewer_findings come ONLY from --reviews (never invented).
3. Evaluate it with schemas/acceptance/check_acceptance.py (A's code, unmodified) and combine:

   state               exit  meaning
   ACCEPTED              0   execution PASS and A's contract = AUTOMATIC_TECHNICAL_ACCEPTANCE (needs concur reviews)
   EXECUTION_FAIL        1   a required check FAILed (or a defect-injection run)
   INVALID               1   output inconsistent/unbound, or the exported contract is INVALID
   EXECUTION_UNKNOWN     2   no FAIL, but a required check UNKNOWN
   REVIEW_PENDING        5   EXECUTION_PASS; only blocker is missing independent concurrence (technically eligible)
   REVIEW_BLOCKED        6   EXECUTION_PASS; a reviewer disputes, or another contract blocker remains

The gate never reports ACCEPTED while review is pending. Reviewer strings are not authenticated: a --reviews
file is a claim to be bound to GitHub review provenance by a human (see the assurance note, limitations).
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify_results as vr  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CHECKER = os.path.join(REPO, "schemas", "acceptance", "check_acceptance.py")
RECORDER = "worker-d scripts/acceptance/run.sh (recorder)"
EXIT = {"ACCEPTED": 0, "EXECUTION_FAIL": 1, "INVALID": 1, "EXECUTION_UNKNOWN": 2, "REVIEW_PENDING": 5, "REVIEW_BLOCKED": 6}
PENDING = "required PASS lacks an independent reviewer concurrence"


def stage_bundle(out, sha, stage):
    rel = f"evidence/acceptance/runs/{sha}"
    root = os.path.join(stage, rel)
    shutil.copytree(out, root, ignore=shutil.ignore_patterns("postgres-run", "SHA256SUMS"))
    rows = vr.verify(out, quiet=True)[1]["checks"]
    with open(os.path.join(root, "logs", "COMMANDS.tsv"), "w") as f:  # aws-3col: log, exit_code, description
        for r in rows:
            if r["log"] not in ("", "-"):
                f.write(f"{os.path.basename(r['log'])}\t{r['exit_code']}\t{r['check_id']}: {r['detail'].replace(chr(9), ' ')}\n")
    files = sorted(os.path.relpath(os.path.join(d, n), root) for d, _, ns in os.walk(root) for n in ns)
    with open(os.path.join(root, "SHA256SUMS"), "w") as f:
        for p in files:
            f.write(f"{vr.sha256_file(os.path.join(root, p))}  {p}\n")
    manifest = {"schema_version": "1.0.0",
                "bundle": {"id": f"acceptance-{sha[:12]}", "root": rel, "kind": "integration-run"},
                "producer": {"script": "scripts/acceptance/run.sh", "source_commit": sha},
                "hashes": {"file": "SHA256SUMS", "base": "bundle", "algorithm": "sha256"},
                "commands": {"file": "logs/COMMANDS.tsv", "format": "aws-3col", "rows_written_by": "producer-script"},
                "exclusions": [{"path": "SHA256SUMS", "reason": "self-reference"}, {"path": "MANIFEST.json", "reason": "added-after-run"}],
                "anchors": [{"type": "git-commit", "ref": sha}]}
    json.dump(manifest, open(os.path.join(root, "MANIFEST.json"), "w"), indent=2)
    return rel


def requirement(entry, members, sha, rel, stage, reviews, kind):
    def ref(r):
        p = f"{rel}/{r['log']}"
        return {"manifest": f"{rel}/MANIFEST.json", "artifact": p, "sha256": vr.sha256_file(os.path.join(stage, p))}
    verdicts = [m["verdict"] for m in members]
    result = "FAIL" if "FAIL" in verdicts else ("UNKNOWN" if (not members or "UNKNOWN" in verdicts) else "PASS")
    executed = [m for m in members if re.fullmatch(r"-?\d+", m["exit_code"]) and m["log"] not in ("", "-")]
    expected = {"exit_code": 1 if kind == "defect" else 0}
    if "expect_output" in entry: expected["output_contains"] = entry["expect_output"]
    chk = {"command": f"bash scripts/acceptance/run.sh {sha}  # check(s) {', '.join(m['check_id'] for m in members) or entry.get('id', entry.get('name'))}",
           "expected": expected}
    if executed and len(executed) == len(members):
        codes = [int(m["exit_code"]) for m in executed]
        obs = {"exit_code": (max(codes, key=abs) if kind != "defect" else codes[0])}
        if "expect_output" in entry:
            body = open(os.path.join(stage, rel, executed[0]["log"]), errors="replace").read()
            obs["output_contains_matched"] = entry["expect_output"] in "\n".join(l for l in body.splitlines() if not l.startswith("# "))
        chk.update(execution="executed", observed=obs)
    else:
        chk["execution"] = "unavailable" if any(m["exit_code"] in ("4", "126", "127") for m in members) else "not_run"
    q = {"id": entry["contract_id"], "scope": entry["title"],
         "rationale": "Mandatory check in the reviewed acceptance inventory (C1).",
         "required": True, "source": {"type": "project_decision", "reference": vr.INVENTORY_REL, "locator": entry.get("id", entry.get("name"))},
         "tested_source_commit": sha, "check": chk,
         "evidence_refs": [ref(m) for m in members if m["log"] not in ("", "-")] if chk["execution"] == "executed" else [],
         "assumptions": ["Offline, credential-free GitHub-hosted or local runner; results describe the lab repo only"],
         "exclusions": ["No AWS, Entra/Graph or production system is contacted or changed"],
         "verification_method": "automated_test", "result": result if chk["execution"] == "executed" else "UNKNOWN",
         "reviewer_findings": list(reviews)}
    if q["result"] == "UNKNOWN":
        q["result_rationale"] = "; ".join(f"{m['check_id']}: {m['detail']}" for m in members) or "no rows recorded"
    return q


def export(out, sha, stage, reviews):
    inv = vr.load_inventory()
    rows = vr.verify(out, quiet=True)[1]["checks"]
    by = {r["check_id"]: r for r in rows}
    rel = stage_bundle(out, sha, stage)
    reqs = []
    for c in inv["checks"]:
        reqs.append(requirement(c, [by[c["id"]]] if c["id"] in by else [], sha, rel, stage, reviews, c["kind"]))
    for g in inv["groups"]:
        rx = re.compile(g["pattern"])
        reqs.append(requirement(g, [r for r in rows if rx.match(r["check_id"])], sha, rel, stage, reviews, g["kind"]))
    return {"schema_version": "1.0.0",
            "document": {"id": f"acceptance-{sha[:12]}", "title": f"Acceptance run.sh results for {sha} (inventory v{inv['version']})",
                         "repository": "onnxscibroccoli/bank-it-operations-lab", "tested_source_commit": sha,
                         "recorded_by": RECORDER, "synthetic": False},
            "requirements": reqs}


def decide(out, sha, reviews=(), stage=None):
    rc, j = vr.verify(out, expect_sha=sha, quiet=True)
    if rc != 0:
        vr.verify(out, expect_sha=sha)
        return {"state": "INVALID", "reason": "run output inconsistent, incomplete or not bound to SHA", "target_sha": sha}
    own = stage is None
    stage = stage or tempfile.mkdtemp(prefix="acceptance-contract-")
    try:
        doc = export(out, sha, stage, reviews)
        dp = os.path.join(stage, "ACCEPTANCE.contract.json")
        json.dump(doc, open(dp, "w"), indent=2)
        p = subprocess.run([sys.executable, CHECKER, dp, "--repo-root", stage, "--json"], capture_output=True, text=True)
        try:
            rep = json.loads(p.stdout)
        except json.JSONDecodeError:
            rep = {"valid": False, "decision": "INVALID", "errors": [p.stdout[-500:], p.stderr[-500:]]}
    finally:
        if own: shutil.rmtree(stage, ignore_errors=True)
    exe = j["execution_state"] if j.get("execution_state") else {"PASS": "EXECUTION_PASS", "FAIL": "EXECUTION_FAIL"}.get(j["overall"], "EXECUTION_UNKNOWN")
    if j.get("injected_defect"): exe = "EXECUTION_FAIL"
    blockers = rep.get("blockers", [])
    if not rep.get("valid"):
        state = "INVALID"
    elif exe == "EXECUTION_FAIL":
        state = "EXECUTION_FAIL"
    elif exe == "EXECUTION_UNKNOWN":
        state = "EXECUTION_UNKNOWN"
    elif rep["decision"] == "AUTOMATIC_TECHNICAL_ACCEPTANCE":
        state = "ACCEPTED"
    elif blockers and all(b["reason"] == PENDING for b in blockers):
        state = "REVIEW_PENDING"
    else:
        state = "REVIEW_BLOCKED"
    if state == "ACCEPTED" and (exe != "EXECUTION_PASS" or rep["decision"] != "AUTOMATIC_TECHNICAL_ACCEPTANCE"):
        state = "INVALID"  # defence in depth; unreachable by construction
    return {"state": state, "execution_state": exe, "technically_eligible": exe == "EXECUTION_PASS" and rep.get("valid", False),
            "contract_decision": rep.get("decision"), "contract_valid": rep.get("valid"), "contract_errors": rep.get("errors", []),
            "blockers": blockers, "target_sha": sha, "inventory_version": j.get("inventory_version"),
            "reviews_supplied": len(reviews), "contract_document": doc, "note": "Lab gate only; not an audit, certification or production sign-off."}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out"); ap.add_argument("--sha", required=True)
    ap.add_argument("--reviews", help="JSON list of reviewer_findings (A's schema) applied to every requirement")
    ap.add_argument("--stage"); ap.add_argument("--decision-out"); ap.add_argument("--contract-out")
    a = ap.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{40}", a.sha): print("--sha must be a full 40-hex SHA"); return 64
    reviews = json.load(open(a.reviews)) if a.reviews else []
    d = decide(a.out, a.sha, reviews, a.stage)
    doc = d.pop("contract_document", None)
    if a.contract_out and doc: json.dump(doc, open(a.contract_out, "w"), indent=2)
    if a.decision_out: json.dump(d, open(a.decision_out, "w"), indent=2)
    for e in d.get("contract_errors", []): print("CONTRACT ERROR", e)
    for b in d.get("blockers", [])[:5]: print("BLOCKER", b["id"], b["reason"])
    if len(d.get("blockers", [])) > 5: print(f"... {len(d['blockers'])} blockers in total")
    print(f"decision: {d['state']} (execution={d.get('execution_state')}, contract={d.get('contract_decision')}, "
          f"reviews={d.get('reviews_supplied')}) for {a.sha}")
    return EXIT[d["state"]]


if __name__ == "__main__":
    sys.exit(main())
