#!/usr/bin/env python3
"""Access-review decision summary (OFFLINE / SYNTHETIC).

Reads synthetic ``accessReviewInstanceDecisionItem`` pages for one review instance through the
fixture transport and reports decision counts plus governance findings. Access reviews require
Microsoft Entra ID Governance (some capabilities Entra ID P2) in a real tenant; see
identity/governance/docs/licensing-prerequisites.md for the free-tier manual fallback.

  python3 identity/governance/access_review.py --scenario baseline
  python3 identity/governance/access_review.py --scenario baseline --json-out ar.json --quiet

Exit codes: 0 no HIGH/MEDIUM findings, 1 findings, 2 fetch/input failure (fail-closed).
No network, tenant or credential is involved. Python 3 stdlib only.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import graph_client as gc  # noqa: E402

SCENARIOS = os.path.join(HERE, "fixtures", "graph", "scenarios")
DEFINITION_ID = "b9a5e000-0000-4000-8000-000000000500"
INSTANCE_ID = "b9a5e000-0000-4000-8000-000000000501"
DECISIONS = ("Approve", "Deny", "NotReviewed", "DontKnow")
RULES = {
    "AR-001": ("MEDIUM", "Decision still NotReviewed (apply default-decision / escalate before instance end)"),
    "AR-002": ("HIGH", "Deny decision not applied (applyResult is not AppliedSuccessfully*)"),
    "AR-003": ("HIGH", "Self-review: reviewer approved their own access"),
    "AR-004": ("MEDIUM", "Approve with empty justification"),
    "DQ-001": ("MEDIUM", "Decision item missing id, decision or principal; skipped"),
}


def decisions_path(definition_id=DEFINITION_ID, instance_id=INSTANCE_ID):
    return "/identityGovernance/accessReviews/definitions/%s/instances/%s/decisions" % (definition_id, instance_id)


def summarize(items):
    counts = {d: 0 for d in DECISIONS}
    findings = []

    def find(rule, item_id, detail):
        sev, title = RULES[rule]
        findings.append({"rule": rule, "severity": sev, "title": title, "decisionId": item_id, "detail": detail})

    for it in items:
        principal = it.get("principal") if isinstance(it, dict) else None
        if not isinstance(it, dict) or not it.get("id") or it.get("decision") not in DECISIONS \
                or not isinstance(principal, dict) or not principal.get("id"):
            find("DQ-001", it.get("id") if isinstance(it, dict) else None, "malformed decision item")
            continue
        d = it["decision"]
        counts[d] += 1
        who = principal.get("displayName") or principal["id"]
        reviewer = it.get("reviewedBy") or {}
        if d == "NotReviewed":
            find("AR-001", it["id"], "%s not reviewed (recommendation %s)" % (who, it.get("recommendation")))
        if d == "Deny" and not str(it.get("applyResult") or "").startswith("AppliedSuccessfully"):
            find("AR-002", it["id"], "%s denied but applyResult=%s" % (who, it.get("applyResult")))
        if d == "Approve" and reviewer.get("id") == principal["id"]:
            find("AR-003", it["id"], "%s approved own access" % who)
        if d == "Approve" and not (it.get("justification") or "").strip():
            find("AR-004", it["id"], "%s approved without justification" % who)
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
    findings.sort(key=lambda f: (order[f["severity"]], f["rule"], str(f["decisionId"])))
    return counts, findings


def run(scenario_dir, path=None, sleep=None):
    rep = {"schema": "bank-it-lab/identity-governance-access-review/v1", "offline": True,
           "tenantStateClaimed": False, "scenario": os.path.basename(os.path.normpath(scenario_dir))}
    try:
        client = gc.GraphClient(gc.FixtureTransport(scenario_dir), sleep=sleep or (lambda s: None))
        items = client.list_all(path or decisions_path())
    except gc.GraphError as e:
        rep.update(exitCode=2, overall="ERROR", error=e.as_dict())
        return rep
    except (OSError, ValueError) as e:
        rep.update(exitCode=2, overall="ERROR", error={"kind": "input", "message": str(e)})
        return rep
    counts, findings = summarize(items)
    bad = any(f["severity"] in ("HIGH", "MEDIUM") for f in findings)
    rep.update(exitCode=1 if bad else 0, overall="FINDINGS" if bad else "PASS", pages=client.pages_fetched,
               total=len(items), decisions=counts, findings=findings)
    return rep


def render_markdown(rep):
    L = ["# Access review decisions -- scenario `%s` (offline, synthetic)" % rep["scenario"], "",
         "Overall: **%s** (exit %d)" % (rep["overall"], rep["exitCode"]), ""]
    if rep["overall"] == "ERROR":
        return "\n".join(L + ["```", json.dumps(rep["error"], indent=2), "```"]) + "\n"
    L += ["| Decision | Count |", "|---|---|"] + ["| %s | %d |" % kv for kv in rep["decisions"].items()]
    L += ["", "| Severity | Rule | Decision item | Detail |", "|---|---|---|---|"]
    L += ["| %s | %s | `%s` | %s |" % (f["severity"], f["rule"], f["decisionId"], f["detail"]) for f in rep["findings"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scenario", default="baseline")
    ap.add_argument("--json-out")
    ap.add_argument("--md-out")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    rep = run(os.path.join(SCENARIOS, a.scenario))
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(rep, indent=2) + "\n")
    if a.md_out:
        with open(a.md_out, "w", encoding="utf-8") as fh:
            fh.write(render_markdown(rep))
    if a.quiet:
        print("%s scenario=%s exit=%d" % (rep["overall"], rep["scenario"], rep["exitCode"]))
    else:
        sys.stdout.write(render_markdown(rep))
    return rep["exitCode"]


if __name__ == "__main__":
    sys.exit(main())
