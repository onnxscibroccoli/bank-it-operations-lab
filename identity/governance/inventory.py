#!/usr/bin/env python3
"""Privileged role assignment inventory + report (OFFLINE / SYNTHETIC).

Reads synthetic Microsoft Graph responses through ``graph_client.FixtureTransport`` and produces an
inventory of who holds which privileged Microsoft Entra directory role, how (permanent / activated /
eligible), and a list of governance findings.

Modes
  pim   (default) PIM schedule-instance APIs -- needs Entra ID P2 or Entra ID Governance in a real
        tenant: roleAssignmentScheduleInstances (active) + roleEligibilityScheduleInstances (eligible).
  free  Free-tier fallback: roleAssignments only (active assignments; no eligibility, no end dates).

Usage
  python3 identity/governance/inventory.py --scenario baseline
  python3 identity/governance/inventory.py --scenario findings --json-out r.json --md-out r.md --csv-out r.csv
  python3 identity/governance/inventory.py --scenario-dir path/to/scenario --mode free --quiet

Exit codes: 0 no HIGH/MEDIUM findings, 1 HIGH/MEDIUM findings present, 2 fetch or input failure
(401/403, throttling budget exhausted, malformed fixture) -- fail-closed, no partial inventory.

No network, tenant, credential or real Graph call is involved. Python 3 stdlib only.
"""
import argparse
import csv
import datetime as dt
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import graph_client as gc  # noqa: E402

SCENARIOS = os.path.join(HERE, "fixtures", "graph", "scenarios")
BASELINE = os.path.join(HERE, "baseline.json")
EXIT_OK, EXIT_FINDINGS, EXIT_ERROR = 0, 1, 2
SCHEMA = "bank-it-lab/identity-governance-inventory/v1"
DISCLAIMER = ("OFFLINE / SYNTHETIC. Generated from local Microsoft Graph-shaped JSON fixtures. No tenant, "
              "Microsoft Graph API call or credential was used; nothing here describes any real tenant.")

P_ROLEDEFS = "/roleManagement/directory/roleDefinitions?$select=id,displayName,templateId,isBuiltIn"
P_ACTIVE = "/roleManagement/directory/roleAssignmentScheduleInstances"
P_ELIGIBLE = "/roleManagement/directory/roleEligibilityScheduleInstances"
P_ASSIGNMENTS = "/roleManagement/directory/roleAssignments"
P_USERS = "/users?$select=id,displayName,userPrincipalName,userType,accountEnabled"
P_SPS = "/servicePrincipals?$select=id,displayName,appId,servicePrincipalType"
P_GROUPS = "/groups?$filter=isAssignableToRole%20eq%20true&$select=id,displayName,isAssignableToRole"

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
RULES = {
    "INV-001": ("HIGH", "Permanent active privileged assignment outside the break-glass allow-list"),
    "INV-002": ("HIGH", "Global Administrator count above baseline maximum"),
    "INV-003": ("MEDIUM", "Expired assignment/eligibility still returned; excluded from effective inventory"),
    "INV-004": ("HIGH", "Privileged role held by a guest (userType=Guest)"),
    "INV-005": ("HIGH", "Tier-0 role held by a service principal"),
    "INV-006": ("MEDIUM", "Activation window longer than baseline maxActivationHours"),
    "INV-007": ("HIGH", "Break-glass account lacks a permanent active Global Administrator assignment"),
    "INV-008": ("MEDIUM", "Assignment principal not resolvable (orphaned or deleted object)"),
    "INV-009": ("LOW", "Privileged assignment on a disabled account"),
    "INV-010": ("INFO", "Free-tier mode: no PIM data; permanence and eligibility unknown"),
    "DQ-001": ("MEDIUM", "Record missing a required field; skipped"),
    "DQ-002": ("LOW", "Record has an unparseable or missing timestamp; treated conservatively"),
    "DQ-003": ("MEDIUM", "roleDefinitionId not present in roleDefinitions"),
}


class InputError(Exception):
    pass


def parse_ts(value):
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("timestamp is not a string")
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    t = dt.datetime.fromisoformat(v)
    if t.tzinfo is None:
        raise ValueError("timestamp without timezone")
    return t.astimezone(dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ") if t else None


def load_baseline(path):
    with open(path, encoding="utf-8") as fh:
        b = json.load(fh)
    for k in ("breakGlass", "globalAdministratorTemplateId", "maxGlobalAdministrators", "maxActivationHours",
              "tierZeroRoleTemplateIds", "privilegedRoleTemplateIds"):
        if k not in b:
            raise InputError("baseline missing %s" % k)
    return b


def fetch(client, mode):
    data = {"roleDefinitions": client.list_all(P_ROLEDEFS), "users": client.list_all(P_USERS),
            "servicePrincipals": client.list_all(P_SPS), "groups": client.list_all(P_GROUPS)}
    if mode == "pim":
        data["active"] = client.list_all(P_ACTIVE)
        data["eligible"] = client.list_all(P_ELIGIBLE)
    else:
        data["assignments"] = client.list_all(P_ASSIGNMENTS)
    return data


def _principals(data):
    out = {}
    for u in data["users"]:
        if isinstance(u, dict) and u.get("id"):
            out[u["id"]] = {"type": "user", "displayName": u.get("displayName"),
                            "userPrincipalName": u.get("userPrincipalName"),
                            "userType": u.get("userType") or "Unknown",
                            "accountEnabled": u.get("accountEnabled")}
    for s in data["servicePrincipals"]:
        if isinstance(s, dict) and s.get("id"):
            out[s["id"]] = {"type": "servicePrincipal", "displayName": s.get("displayName"),
                            "appId": s.get("appId"), "userType": None, "accountEnabled": None}
    for g in data["groups"]:
        if isinstance(g, dict) and g.get("id"):
            out[g["id"]] = {"type": "group", "displayName": g.get("displayName"), "userType": None,
                            "accountEnabled": None}
    return out


def build(data, baseline, as_of, mode):
    """Pure function: Graph-shaped data -> (inventory rows, findings)."""
    findings = []

    def find(rule, subject, detail, record_id=None):
        sev, title = RULES[rule]
        findings.append({"rule": rule, "severity": sev, "title": title, "subject": subject,
                         "recordId": record_id, "detail": detail})

    priv = baseline["privilegedRoleTemplateIds"]
    tier0 = set(baseline["tierZeroRoleTemplateIds"])
    ga = baseline["globalAdministratorTemplateId"]
    bg = set(baseline["breakGlass"]["userIds"])
    roles = {}
    for r in data["roleDefinitions"]:
        if isinstance(r, dict) and r.get("id"):
            roles[r["id"]] = {"displayName": r.get("displayName"), "templateId": r.get("templateId") or r["id"]}
    principals = _principals(data)

    records = []
    if mode == "pim":
        records += [("active", r) for r in data["active"]] + [("eligible", r) for r in data["eligible"]]
    else:
        records += [("active", r) for r in data["assignments"]]
        find("INV-010", "tenant", "roleAssignments has no schedule data; run in 'pim' mode where licensed")

    rows = []
    for state, rec in records:
        if not isinstance(rec, dict):
            find("DQ-001", "record", "non-object record in %s collection" % state)
            continue
        rid = rec.get("id")
        missing = [k for k in ("id", "principalId", "roleDefinitionId") if not rec.get(k)]
        if missing:
            find("DQ-001", "record", "%s record missing %s" % (state, ", ".join(missing)), rid)
            continue
        role = roles.get(rec["roleDefinitionId"])
        if role is None:
            find("DQ-003", rec["roleDefinitionId"], "unknown role definition; treated as privileged", rid)
            role = {"displayName": "UNKNOWN", "templateId": rec["roleDefinitionId"]}
            is_priv = True
        else:
            is_priv = role["templateId"] in priv
        start = end = None
        if mode == "pim":
            try:
                start = parse_ts(rec.get("startDateTime"))
                end = parse_ts(rec.get("endDateTime"))
            except ValueError as e:
                find("DQ-002", rid, "bad timestamp (%s); treated as permanent" % e, rid)
                start, end = None, None
            if rec.get("startDateTime") in (None, ""):
                find("DQ-002", rid, "startDateTime missing", rid)
        if end is not None and end <= as_of:
            find("INV-003", rid, "%s %s ended %s (asOf %s)" % (state, role["displayName"], iso(end), iso(as_of)), rid)
            continue
        if start is not None and start > as_of:
            continue  # future-dated schedule instance: not yet effective
        if mode == "pim":
            a_type = rec.get("assignmentType") if state == "active" else "Eligible"
            if state == "active" and a_type not in ("Assigned", "Activated"):
                find("DQ-002", rid, "assignmentType %r unknown; treated as Assigned" % a_type, rid)
                a_type = "Assigned"
        else:
            a_type = "Unknown (free tier)"
        p = principals.get(rec["principalId"])
        if p is None:
            find("INV-008", rec["principalId"], "%s on %s" % (state, role["displayName"]), rid)
            p = {"type": "unresolved", "displayName": None, "userType": None, "accountEnabled": None}
        permanent = (end is None) if mode == "pim" else None
        rows.append({
            "recordId": rid, "state": state, "assignmentType": a_type,
            "memberType": rec.get("memberType") or ("Direct" if mode == "free" else "Unknown"),
            "principalId": rec["principalId"], "principalType": p["type"],
            "principalDisplayName": p.get("displayName"), "userPrincipalName": p.get("userPrincipalName"),
            "userType": p.get("userType"), "accountEnabled": p.get("accountEnabled"),
            "roleTemplateId": role["templateId"], "roleDisplayName": role["displayName"],
            "privileged": is_priv, "tierZero": role["templateId"] in tier0,
            "directoryScopeId": rec.get("directoryScopeId", "/"),
            "startDateTime": iso(start), "endDateTime": iso(end), "permanent": permanent,
            "breakGlass": rec["principalId"] in bg,
        })

    for r in rows:
        if not r["privileged"]:
            continue
        subj = r["principalDisplayName"] or r["principalId"]
        if r["state"] == "active" and r["permanent"] and not r["breakGlass"]:
            find("INV-001", subj, "permanent %s %s" % (r["assignmentType"], r["roleDisplayName"]), r["recordId"])
        if r["userType"] == "Guest":
            find("INV-004", subj, "%s %s" % (r["state"], r["roleDisplayName"]), r["recordId"])
        if r["principalType"] == "servicePrincipal" and r["tierZero"]:
            find("INV-005", subj, "%s %s" % (r["state"], r["roleDisplayName"]), r["recordId"])
        if r["accountEnabled"] is False:
            find("INV-009", subj, "%s %s on disabled account" % (r["state"], r["roleDisplayName"]), r["recordId"])
        if r["assignmentType"] == "Activated" and r["startDateTime"] and r["endDateTime"]:
            hours = (parse_ts(r["endDateTime"]) - parse_ts(r["startDateTime"])).total_seconds() / 3600.0
            if hours > baseline["maxActivationHours"]:
                find("INV-006", subj, "%s activation %.1fh > %dh" % (r["roleDisplayName"], hours,
                                                                     baseline["maxActivationHours"]), r["recordId"])

    ga_active = sorted({r["principalId"] for r in rows if r["state"] == "active" and r["roleTemplateId"] == ga})
    if len(ga_active) > baseline["maxGlobalAdministrators"]:
        find("INV-002", "Global Administrator", "%d active principals > %d"
             % (len(ga_active), baseline["maxGlobalAdministrators"]))
    if mode == "pim":
        for uid in sorted(bg):
            ok = any(r["principalId"] == uid and r["roleTemplateId"] == ga and r["state"] == "active"
                     and r["permanent"] for r in rows)
            if not ok:
                find("INV-007", uid, "no permanent active Global Administrator assignment found")

    rows.sort(key=lambda r: (not r["tierZero"], r["roleDisplayName"] or "", r["state"],
                             r["principalDisplayName"] or "", r["recordId"]))
    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["rule"], str(f["subject"]), str(f["recordId"])))
    return rows, findings


def run(scenario_dir, baseline_path=BASELINE, mode=None, as_of=None, sleep=None, max_retries=4):
    """Returns the report dict. Never raises for Graph/fixture failures: they become exitCode 2."""
    report = {"schema": SCHEMA, "mode": None, "offline": True, "tenantStateClaimed": False,
              "disclaimer": DISCLAIMER, "scenario": os.path.basename(os.path.normpath(scenario_dir))}
    try:
        baseline = load_baseline(baseline_path)
        transport = gc.FixtureTransport(scenario_dir)
        mode = mode or transport.meta.get("mode", "pim")
        if mode not in ("pim", "free"):
            raise InputError("unknown mode %r" % mode)
        report["mode"] = mode
        as_of_t = parse_ts(as_of or transport.meta.get("asOfUtc"))
        if as_of_t is None:
            raise InputError("asOfUtc not set (scenario routes.json or --as-of)")
        report["asOfUtc"] = iso(as_of_t)
        client = gc.GraphClient(transport, max_retries=max_retries, sleep=sleep or (lambda s: None))
        try:
            data = fetch(client, mode)
        finally:
            report["graph"] = {"requests": len(transport.calls), "pages": client.pages_fetched,
                               "retries": client.retry_log}
        rows, findings = build(data, baseline, as_of_t, mode)
    except gc.GraphError as e:
        report.update(exitCode=EXIT_ERROR, overall="ERROR", error=e.as_dict(), inventory=[], findings=[])
        return report
    except (InputError, ValueError, OSError, KeyError, TypeError) as e:
        report.update(exitCode=EXIT_ERROR, overall="ERROR",
                      error={"kind": "input", "message": "%s: %s" % (type(e).__name__, e)}, inventory=[], findings=[])
        return report
    bad = [f for f in findings if f["severity"] in ("HIGH", "MEDIUM")]
    counts = {s: sum(f["severity"] == s for f in findings) for s in SEVERITY_ORDER}
    report.update(
        exitCode=EXIT_FINDINGS if bad else EXIT_OK, overall="FINDINGS" if bad else "PASS",
        summary={"inventoryRows": len(rows), "privilegedRows": sum(r["privileged"] for r in rows),
                 "activePrivileged": sum(r["privileged"] and r["state"] == "active" for r in rows),
                 "eligiblePrivileged": sum(r["privileged"] and r["state"] == "eligible" for r in rows),
                 "permanentActivePrivileged": sum(bool(r["privileged"] and r["state"] == "active" and r["permanent"])
                                                  for r in rows),
                 "findingsBySeverity": counts},
        inventory=rows, findings=findings)
    return report


CSV_FIELDS = ["roleDisplayName", "roleTemplateId", "tierZero", "state", "assignmentType", "memberType",
              "principalType", "principalDisplayName", "userPrincipalName", "userType", "principalId",
              "breakGlass", "permanent", "startDateTime", "endDateTime", "directoryScopeId", "recordId"]


def render_csv(report):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_FIELDS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in report.get("inventory", []):
        if r["privileged"]:
            w.writerow(r)
    return buf.getvalue()


def _md(v):
    return "" if v is None else str(v).replace("|", "\\|")


def render_markdown(report, extra=None):
    L = ["# Privileged role assignment inventory -- scenario `%s`" % report["scenario"], "",
         "> **%s**" % report["disclaimer"], "", "| Field | Value |", "|---|---|",
         "| Mode | `%s` |" % report.get("mode"), "| As of (UTC) | %s |" % report.get("asOfUtc"),
         "| Overall | **%s** (exit %d) |" % (report["overall"], report["exitCode"])]
    for k, v in (extra or {}).items():
        L.append("| %s | `%s` |" % (k, v))
    g = report.get("graph")
    if g:
        L.append("| Graph requests (fixture) | %d requests, %d pages, %d retries |"
                 % (g["requests"], g["pages"], len(g["retries"])))
    if report["overall"] == "ERROR":
        e = report["error"]
        L += ["", "## Error (fail-closed, no inventory produced)", "", "```", json.dumps(e, indent=2), "```"]
        return "\n".join(L) + "\n"
    s = report["summary"]
    L += ["", "## Summary", "", "| Metric | Value |", "|---|---|"]
    for k in ("inventoryRows", "privilegedRows", "activePrivileged", "eligiblePrivileged", "permanentActivePrivileged"):
        L.append("| %s | %d |" % (k, s[k]))
    L.append("| findings | %s |" % ", ".join("%s=%d" % kv for kv in s["findingsBySeverity"].items()))
    L += ["", "## Findings", "", "| Severity | Rule | Subject | Detail | Record |", "|---|---|---|---|---|"]
    for f in report["findings"]:
        L.append("| %s | %s | %s | %s | `%s` |" % (f["severity"], f["rule"], _md(f["subject"]), _md(f["detail"]),
                                                  _md(f["recordId"])))
    if not report["findings"]:
        L.append("| - | - | - | none | - |")
    L += ["", "## Privileged inventory", "",
          "| Role | Tier0 | State | Type | Principal | Kind | Permanent | Ends (UTC) |", "|---|---|---|---|---|---|---|---|"]
    for r in report["inventory"]:
        if r["privileged"]:
            L.append("| %s | %s | %s | %s | %s%s | %s | %s | %s |" % (
                _md(r["roleDisplayName"]), "yes" if r["tierZero"] else "", r["state"], _md(r["assignmentType"]),
                _md(r["principalDisplayName"] or r["principalId"]), " (break-glass)" if r["breakGlass"] else "",
                r["principalType"], {True: "yes", False: "no", None: "unknown"}[r["permanent"]],
                r["endDateTime"] or ""))
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--scenario", help="name under fixtures/graph/scenarios/")
    g.add_argument("--scenario-dir")
    ap.add_argument("--baseline", default=BASELINE)
    ap.add_argument("--mode", choices=("pim", "free"))
    ap.add_argument("--as-of", help="evaluation time (ISO-8601 with zone); default from scenario")
    ap.add_argument("--json-out")
    ap.add_argument("--md-out")
    ap.add_argument("--csv-out")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    sdir = a.scenario_dir or os.path.join(SCENARIOS, a.scenario)
    rep = run(sdir, a.baseline, a.mode, a.as_of)
    for path, text in ((a.json_out, json.dumps(rep, indent=2) + "\n"), (a.md_out, render_markdown(rep)),
                       (a.csv_out, render_csv(rep))):
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
    if rep["overall"] == "ERROR":
        print("ERROR scenario=%s %s" % (rep["scenario"], json.dumps(rep["error"])), file=sys.stderr)
    if not a.quiet:
        sys.stdout.write(render_markdown(rep))
    else:
        print("%s scenario=%s mode=%s exit=%d" % (rep["overall"], rep["scenario"], rep.get("mode"), rep["exitCode"]))
    return rep["exitCode"]


if __name__ == "__main__":
    sys.exit(main())
