#!/usr/bin/env python3
"""Offline M365 / endpoint operations scenario engine (SYNTHETIC lab data only).

Evaluates onboarding, offboarding, access-troubleshooting, service-health triage and
break-glass (emergency access) scenarios against a synthetic tenant snapshot and checks the
result against each scenario's recorded expectation.

Nothing here authenticates to Microsoft 365, Entra ID, Intune, Exchange Online or Microsoft
Graph, and nothing is ever executed against a tenant: every remediation step is emitted as a
PLAN_ONLY record with executed=false. Python 3 standard library only; no network access.

Usage:
  python3 identity/m365/m365_ops.py                         # tenant/tenant.json + scenarios/
  python3 identity/m365/m365_ops.py scenarios/x.json ...    # specific scenario files or dirs
  python3 identity/m365/m365_ops.py --tenant other.json --json-out r.json --md-out r.md --quiet

Exit codes: 0 every scenario matched its expectation, 1 at least one mismatch,
2 malformed / unsafe / non-synthetic input (fail-closed; nothing is evaluated).
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TENANT = os.path.join(HERE, "tenant", "tenant.json")
DEFAULT_SCENARIOS = os.path.join(HERE, "scenarios")
TOOL = "bank-it-lab/m365-ops/v1"
DISCLAIMER = ("OFFLINE / SYNTHETIC. Evaluated from local JSON in this repository. No Microsoft 365 / "
              "Entra ID / Intune tenant, Microsoft Graph call or credential was used, and no change was "
              "made anywhere. Every remediation step is PLAN_ONLY (executed=false).")

LAB_GUID = re.compile(r"^[0-9a-f]{8}-0000-4000-8000-[0-9a-f]{12}$")
ANY_GUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
EMAILISH = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+)")
URLISH = re.compile(r"https?://", re.I)
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
VER_RE = re.compile(r"^\d+(\.\d+)*$")
REF_RE = re.compile(r"^(HR|CHG|INC|AUD|SR)-LAB-\d{4,}$")
SCEN_ID = re.compile(r"^M365-(ONB|OFF|ACC|SH|BG)-\d{3}$")
FORBIDDEN_KEYS = {"password", "clientsecret", "client_secret", "secret", "accesstoken", "access_token",
                  "refreshtoken", "refresh_token", "privatekey", "private_key", "certificatepem",
                  "execute", "apply", "commit"}

SCENARIO_TYPES = ("onboarding", "offboarding", "access-troubleshooting", "service-health",
                  "break-glass-review", "break-glass-usage")
REQUIRED_EVIDENCE = {
    "onboarding": ["approval", "identity-change", "license-assignment", "mfa-registration"],
    "offboarding": ["approval", "identity-change", "session-revocation", "device-action",
                    "mailbox-retention", "license-removal"],
    "access-troubleshooting": ["sign-in-log", "diagnosis", "resolution"],
    "service-health": ["service-health-snapshot", "user-communication"],
    "break-glass-review": ["break-glass-review", "alert-config", "test-record"],
    "break-glass-usage": ["sign-in-log", "incident-ticket", "credential-rotation", "audit-review"],
}
APPROVAL_TYPES = ("onboarding", "offboarding")

# AADSTS sign-in error codes -> lab diagnosis code
SIGNIN_ERRORS = {
    0: None,
    50053: ("AUTH-LOCKED", "Account locked (smart lockout) or sign-in from a blocked IP",
            "Confirm it was the user (not a spray attack) before unlocking; review risky sign-ins."),
    50057: ("AUTH-ACCOUNT-DISABLED", "User account is disabled",
            "Confirm with HR whether the account was disabled by an offboarding; never re-enable on a user's request alone."),
    50076: ("AUTH-MFA-REQUIRED", "MFA required by Conditional Access and not completed",
            "User completes MFA with a registered method; check CA002 sign-in details."),
    50079: ("AUTH-MFA-REGISTRATION-REQUIRED", "User must register for MFA but has no usable method",
            "Verify identity out of band (call back on HR-record number), issue a one-time Temporary Access Pass, have the user register a phishing-resistant method."),
    50126: ("AUTH-BAD-CREDENTIALS", "Invalid username or password",
            "Self-service password reset; check for a spray pattern across users first."),
    53000: ("CA-DEVICE-NOT-COMPLIANT", "Conditional Access requires a compliant device (CA004) and the device is not",
            "Remediate the device compliance settings below, then sync the device in Company Portal."),
    53003: ("CA-BLOCKED", "Access blocked by a Conditional Access policy",
            "Read the CA policy result in the sign-in log entry; do not add exclusions to fix a single user."),
}

STEP_REFERENCE = {
    "DISABLE_ONPREM_AD": "AD DS: Disable-ADAccount <samAccountName>, then wait for (or trigger) Entra Connect delta sync",
    "DISABLE_SIGNIN": "Graph: PATCH /v1.0/users/{id} {\"accountEnabled\": false}",
    "REVOKE_SESSIONS": "Graph: POST /v1.0/users/{id}/revokeSignInSessions",
    "REMOVE_AUTH_METHODS": "Graph: DELETE /v1.0/users/{id}/authentication/<method>Methods/{methodId}",
    "REMOVE_PRIV_ROLES": "Graph: DELETE /v1.0/roleManagement/directory/roleAssignments/{assignmentId}",
    "RETIRE_DEVICE": "Graph: POST /v1.0/deviceManagement/managedDevices/{deviceId}/retire (selective wipe)",
    "WIPE_DEVICE": "Graph: POST /v1.0/deviceManagement/managedDevices/{deviceId}/wipe (factory reset)",
    "SET_LITIGATION_HOLD": "Exchange Online PowerShell: Set-Mailbox <upn> -LitigationHoldEnabled $true",
    "CONVERT_MAILBOX_SHARED": "Exchange Online PowerShell: Set-Mailbox <upn> -Type Shared; grant manager FullAccess",
    "TRANSFER_ONEDRIVE": "SharePoint admin: grant the manager site-collection admin on the user's OneDrive",
    "REMOVE_FROM_GROUPS": "Graph: DELETE /v1.0/groups/{groupId}/members/{id}/$ref",
    "REMOVE_LICENSES": "Group-based: remove from GRP-LIC-* groups; direct: POST /v1.0/users/{id}/assignLicense removeLicenses",
    "EXPORT_AUDIT_EVIDENCE": "Purview audit search + Entra audit/sign-in log export for the user, hashed into the ticket",
}
OFFBOARD_STEPS = set(STEP_REFERENCE)
DEVICE_STEPS = {"RETIRE_DEVICE", "WIPE_DEVICE"}
DISABLE_STEPS = {"DISABLE_ONPREM_AD", "DISABLE_SIGNIN"}
RETENTION_STEPS = {"SET_LITIGATION_HOLD", "CONVERT_MAILBOX_SHARED", "TRANSFER_ONEDRIVE"}

VERDICTS = {
    "onboarding": ("READY", "READY_WITH_WARNINGS", "BLOCKED"),
    "offboarding": ("APPROVED", "APPROVED_WITH_WARNINGS", "REJECTED"),
    "access-troubleshooting": ("ROOT_CAUSE_IDENTIFIED", "ESCALATE"),
    "service-health": ("KNOWN_SERVICE_INCIDENT", "ESCALATE_TO_MICROSOFT", "LOCAL_ISSUE"),
    "break-glass-review": ("COMPLIANT", "COMPLIANT_WITH_WARNINGS", "NONCOMPLIANT"),
    "break-glass-usage": ("POST_USE_COMPLETE", "POST_USE_COMPLETE_WITH_WARNINGS", "POST_USE_INCOMPLETE"),
}


class Malformed(Exception):
    def __init__(self, rule, msg):
        Exception.__init__(self, "%s: %s" % (rule, msg))
        self.rule = rule
        self.msg = msg


# ---------------------------------------------------------------- loading / schema

def strict_load(path):
    def hook(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise Malformed("SCHEMA-001", "%s: duplicate key %r" % (path, k))
            d[k] = v
        return d

    def bad_const(x):
        raise Malformed("SCHEMA-001", "%s: non-finite number %s" % (path, x))

    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh, object_pairs_hook=hook, parse_constant=bad_const)
    except Malformed:
        raise
    except (ValueError, OSError) as e:
        raise Malformed("SCHEMA-001", "%s: %s" % (path, e))


def safety_scan(obj, where, allowed_domains):
    """SAFE-001 no secret/execution keys; SYN-001 lab GUIDs only; SYN-002 .example domains only;
    SYN-003 no URLs in data."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in FORBIDDEN_KEYS:
                raise Malformed("SAFE-001", "%s: forbidden key %r (no secrets, no execution flags)" % (where, k))
            safety_scan(v, "%s.%s" % (where, k), allowed_domains)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            safety_scan(v, "%s[%d]" % (where, i), allowed_domains)
    elif isinstance(obj, str):
        for g in ANY_GUID.findall(obj):
            if not LAB_GUID.match(g):
                raise Malformed("SYN-001", "%s: %r is not a synthetic lab GUID" % (where, g))
        for dom in EMAILISH.findall(obj):
            d = dom.lower().rstrip(".")
            if not d.endswith(".example") or (allowed_domains and d not in allowed_domains):
                raise Malformed("SYN-002", "%s: domain %r is not a synthetic tenant domain" % (where, d))
        if URLISH.search(obj):
            raise Malformed("SYN-003", "%s: URLs are not allowed in lab data" % where)
    elif isinstance(obj, float) and obj != obj:
        raise Malformed("SCHEMA-001", "%s: NaN" % where)


def need(obj, key, types, where, allow_none=False):
    if not isinstance(obj, dict):
        raise Malformed("SCHEMA-002", "%s: expected an object" % where)
    if key not in obj:
        raise Malformed("SCHEMA-002", "%s: missing key %r" % (where, key))
    v = obj[key]
    if v is None and allow_none:
        return v
    if isinstance(v, bool) and types is not object and bool not in (types if isinstance(types, tuple) else (types,)):
        raise Malformed("SCHEMA-002", "%s.%s: wrong type bool" % (where, key))
    if not isinstance(v, types):
        raise Malformed("SCHEMA-002", "%s.%s: wrong type %s" % (where, key, type(v).__name__))
    return v


def only_keys(obj, allowed, where):
    extra = sorted(set(obj) - set(allowed) - {"_comment"})
    if extra:
        raise Malformed("SCHEMA-002", "%s: unknown key(s) %s" % (where, ", ".join(extra)))


def utc(s, where):
    if not isinstance(s, str) or not UTC_RE.match(s):
        raise Malformed("SCHEMA-003", "%s: %r is not a UTC timestamp YYYY-MM-DDTHH:MM:SSZ" % (where, s))
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def ver(s, where):
    if not isinstance(s, str) or not VER_RE.match(s):
        raise Malformed("SCHEMA-003", "%s: %r is not a dotted version" % (where, s))
    return tuple(int(p) for p in s.split("."))


def lab_id(v, where):
    if not isinstance(v, str) or not LAB_GUID.match(v):
        raise Malformed("SYN-001", "%s: %r is not a synthetic lab GUID" % (where, v))
    return v


TENANT_KEYS = ("schemaVersion", "synthetic", "asOfUtc", "tenant", "servicePlans", "workloads", "skus", "groups",
               "users", "devices", "complianceSettings", "compliancePolicies", "conditionalAccess", "breakGlass",
               "serviceHealth")


def check_tenant(t):
    if not isinstance(t, dict):
        raise Malformed("SCHEMA-002", "tenant: expected an object")
    only_keys(t, TENANT_KEYS, "tenant")
    for k in TENANT_KEYS:
        need(t, k, object, "tenant")
    if t["schemaVersion"] != 1:
        raise Malformed("SCHEMA-002", "tenant.schemaVersion must be 1")
    if t["synthetic"] is not True:
        raise Malformed("SYN-000", "tenant.synthetic must be true; this tool only accepts synthetic lab data")
    utc(t["asOfUtc"], "tenant.asOfUtc")
    ten = t["tenant"]
    lab_id(need(ten, "id", str, "tenant.tenant"), "tenant.tenant.id")
    doms = {need(ten, "primaryDomain", str, "tenant.tenant").lower(), need(ten, "initialDomain", str, "tenant.tenant").lower()}
    for d in doms:
        if not d.endswith(".example"):
            raise Malformed("SYN-002", "tenant domain %r must end in .example" % d)
    safety_scan(t, "tenant", doms)
    plans = need(t, "servicePlans", dict, "tenant")
    for p, spec in plans.items():
        only_keys(spec, ("displayName", "requires"), "servicePlans.%s" % p)
        for grp in need(spec, "requires", list, "servicePlans.%s" % p):
            if not isinstance(grp, list) or not grp or any(x not in plans for x in grp):
                raise Malformed("SCHEMA-004", "servicePlans.%s.requires: unknown plan or empty group" % p)
    for w, spec in need(t, "workloads", dict, "tenant").items():
        only_keys(spec, ("displayName", "requires"), "workloads.%s" % w)
        for grp in need(spec, "requires", list, "workloads.%s" % w):
            if not isinstance(grp, list) or not grp or any(x not in plans for x in grp):
                raise Malformed("SCHEMA-004", "workloads.%s.requires: unknown plan or empty group" % w)
    skus = {}
    for i, s in enumerate(need(t, "skus", list, "tenant")):
        where = "skus[%d]" % i
        only_keys(s, ("id", "skuPartNumber", "prepaid", "consumed", "servicePlans"), where)
        lab_id(need(s, "id", str, where), where + ".id")
        name = need(s, "skuPartNumber", str, where)
        if not name.startswith("LAB_"):
            raise Malformed("SYN-004", "%s: skuPartNumber must start with LAB_" % where)
        pre, con = need(s, "prepaid", int, where), need(s, "consumed", int, where)
        if pre < 0 or con < 0 or con > pre:
            raise Malformed("SCHEMA-004", "%s: seat counts invalid" % where)
        if any(p not in plans for p in need(s, "servicePlans", list, where)):
            raise Malformed("SCHEMA-004", "%s: unknown service plan" % where)
        skus[name] = s
    groups = {}
    for i, g in enumerate(need(t, "groups", list, "tenant")):
        where = "groups[%d]" % i
        only_keys(g, ("id", "displayName", "license"), where)
        lab_id(need(g, "id", str, where), where + ".id")
        lic = need(g, "license", dict, where)
        sku = need(lic, "skuPartNumber", str, where + ".license")
        if sku not in skus:
            raise Malformed("SCHEMA-004", "%s: unknown sku %s" % (where, sku))
        if any(p not in skus[sku]["servicePlans"] for p in need(lic, "disabledPlans", list, where + ".license")):
            raise Malformed("SCHEMA-004", "%s: disabledPlans not in sku" % where)
        groups[need(g, "displayName", str, where)] = g
    users = {}
    ukeys = ("id", "upn", "displayName", "department", "accountEnabled", "onPremisesSynced", "usageLocation",
             "licenseGroups", "directLicenses", "mfaMethods", "roles")
    for i, u in enumerate(need(t, "users", list, "tenant")):
        where = "users[%d]" % i
        only_keys(u, ukeys, where)
        uid = lab_id(need(u, "id", str, where), where + ".id")
        if uid in users:
            raise Malformed("SCHEMA-005", "duplicate user id %s" % uid)
        upn = need(u, "upn", str, where)
        if "@" not in upn or upn.split("@", 1)[1].lower() not in doms:
            raise Malformed("SYN-002", "%s: upn must be on a tenant .example domain" % where)
        need(u, "accountEnabled", bool, where)
        need(u, "onPremisesSynced", bool, where)
        need(u, "usageLocation", str, where, allow_none=True)
        for g in need(u, "licenseGroups", list, where):
            if g not in groups:
                raise Malformed("SCHEMA-004", "%s: unknown license group %s" % (where, g))
        for lic in need(u, "directLicenses", list, where):
            if need(lic, "skuPartNumber", str, where) not in skus:
                raise Malformed("SCHEMA-004", "%s: unknown direct sku" % where)
        need(u, "mfaMethods", list, where)
        for r in need(u, "roles", list, where):
            if need(r, "assignment", str, where + ".roles") not in ("permanent", "eligible"):
                raise Malformed("SCHEMA-004", "%s: role assignment must be permanent|eligible" % where)
            need(r, "role", str, where + ".roles")
        users[uid] = u
    devices = {}
    for i, d in enumerate(need(t, "devices", list, "tenant")):
        where = "devices[%d]" % i
        did = lab_id(need(d, "id", str, where), where + ".id")
        if need(d, "ownerId", str, where) not in users:
            raise Malformed("SCHEMA-004", "%s: unknown owner" % where)
        if need(d, "platform", str, where) not in ("windows", "ios", "android", "macos"):
            raise Malformed("SCHEMA-004", "%s: unknown platform" % where)
        if need(d, "ownership", str, where) not in ("corporate", "personal"):
            raise Malformed("SCHEMA-004", "%s: ownership must be corporate|personal" % where)
        need(d, "managed", bool, where)
        ver(need(d, "osVersion", str, where), where + ".osVersion")
        for k in ("lastCheckInUtc", "firstNoncompliantUtc"):
            if need(d, k, str, where, allow_none=True) is not None:
                utc(d[k], "%s.%s" % (where, k))
        devices[did] = d
    cs = need(t, "complianceSettings", dict, "tenant")
    need(cs, "validityPeriodDays", int, "complianceSettings")
    need(cs, "markNoPolicyAsNoncompliant", bool, "complianceSettings")
    known_settings = {"minOsVersion", "requireBitLocker", "requireSecureBoot", "requireDefender", "requireFirewall",
                      "blockJailbroken", "requirePasscode", "blockRooted", "requireEncryption"}
    for i, p in enumerate(need(t, "compliancePolicies", list, "tenant")):
        where = "compliancePolicies[%d]" % i
        need(p, "id", str, where)
        need(p, "platform", str, where)
        need(p, "gracePeriodHours", int, where)
        st = need(p, "settings", dict, where)
        if set(st) - known_settings:
            raise Malformed("SCHEMA-004", "%s: unknown compliance setting(s) %s" % (where, sorted(set(st) - known_settings)))
        if "minOsVersion" in st:
            ver(st["minOsVersion"], where + ".minOsVersion")
    for i, p in enumerate(need(need(t, "conditionalAccess", dict, "tenant"), "policies", list, "conditionalAccess")):
        where = "conditionalAccess.policies[%d]" % i
        need(p, "policyRef", str, where)
        if need(p, "state", str, where) not in ("enabled", "disabled", "enabledForReportingButNotEnforced"):
            raise Malformed("SCHEMA-004", "%s: invalid state" % where)
        need(p, "excludeUsers", list, where)
        need(p, "requiresCompliantDevice", bool, where)
    bg = need(t, "breakGlass", dict, "tenant")
    for i, a in enumerate(need(bg, "accounts", list, "breakGlass")):
        where = "breakGlass.accounts[%d]" % i
        if need(a, "userId", str, where) not in users:
            raise Malformed("SCHEMA-004", "%s: unknown user" % where)
        if need(a, "lastTestedUtc", str, where, allow_none=True) is not None:
            utc(a["lastTestedUtc"], where + ".lastTestedUtc")
        need(a, "custodyLocations", list, where)
    for i, r in enumerate(need(bg, "alertRules", list, "breakGlass")):
        where = "breakGlass.alertRules[%d]" % i
        need(r, "enabled", bool, where)
        need(r, "targetsUserIds", list, where)
    need(bg, "testIntervalDays", int, "breakGlass")
    need(bg, "rotationDeadlineHours", int, "breakGlass")
    for i, s in enumerate(need(t, "serviceHealth", list, "tenant")):
        where = "serviceHealth[%d]" % i
        need(s, "id", str, where)
        if any(w not in t["workloads"] for w in need(s, "workloads", list, where)):
            raise Malformed("SCHEMA-004", "%s: unknown workload" % where)
        if need(s, "classification", str, where) not in ("incident", "advisory"):
            raise Malformed("SCHEMA-004", "%s: classification must be incident|advisory" % where)
        need(s, "status", str, where)
        utc(need(s, "startUtc", str, where), where + ".startUtc")
        if need(s, "endUtc", str, where, allow_none=True) is not None:
            utc(s["endUtc"], where + ".endUtc")
    return {"users": users, "devices": devices, "skus": skus, "groups": groups, "domains": doms}


SCEN_KEYS = ("schemaVersion", "id", "type", "title", "narrative", "input", "auditEvidence", "expected")


def check_scenario(s, path, idx):
    if not isinstance(s, dict):
        raise Malformed("SCHEMA-002", "%s: scenario must be an object" % path)
    only_keys(s, SCEN_KEYS, path)
    for k in SCEN_KEYS:
        need(s, k, object, path)
    if s["schemaVersion"] != 1:
        raise Malformed("SCHEMA-002", "%s: schemaVersion must be 1" % path)
    if not isinstance(s["id"], str) or not SCEN_ID.match(s["id"]):
        raise Malformed("SCHEMA-002", "%s: id must match M365-(ONB|OFF|ACC|SH|BG)-NNN" % path)
    if s["type"] not in SCENARIO_TYPES:
        raise Malformed("SCHEMA-002", "%s: unknown type %r" % (path, s["type"]))
    safety_scan(s, path, idx["domains"])
    need(s, "input", dict, path)
    for i, e in enumerate(need(s, "auditEvidence", list, path)):
        where = "%s.auditEvidence[%d]" % (path, i)
        need(e, "category", str, where)
        if not REF_RE.match(need(e, "ref", str, where)):
            raise Malformed("SCHEMA-002", "%s.ref must look like AUD-LAB-0001" % where)
        need(e, "source", str, where)
    exp = need(s, "expected", dict, path)
    only_keys(exp, ("verdict", "findings"), path + ".expected")
    if need(exp, "verdict", str, path + ".expected") not in VERDICTS[s["type"]]:
        raise Malformed("SCHEMA-002", "%s.expected.verdict %r not valid for %s" % (path, exp["verdict"], s["type"]))
    if not all(isinstance(c, str) for c in need(exp, "findings", list, path + ".expected")):
        raise Malformed("SCHEMA-002", "%s.expected.findings must be strings" % path)
    inp = s["input"]
    for k in ("userId",):
        if k in inp and inp[k] not in idx["users"]:
            raise Malformed("SCHEMA-004", "%s: unknown userId %s" % (path, inp[k]))
    for k in ("approvalRef", "incidentRef"):
        if inp.get(k) is not None and not REF_RE.match(str(inp[k])):
            raise Malformed("SCHEMA-002", "%s.input.%s must look like CHG-LAB-0001" % (path, k))
    return s


# ---------------------------------------------------------------- evaluation helpers

def finding(code, severity, detail, remediation="", root=False):
    return {"code": code, "severity": severity, "rootCause": bool(root), "detail": detail, "remediation": remediation}


def plan_step(action, reference, target=""):
    return {"action": action, "target": target, "reference": reference, "mode": "PLAN_ONLY", "executed": False}


def assignments(t, idx, user, extra_groups=()):
    out = []
    for g in list(user["licenseGroups"]) + [g for g in extra_groups if g not in user["licenseGroups"]]:
        lic = idx["groups"][g]["license"]
        out.append({"source": "group:" + g, "sku": lic["skuPartNumber"], "disabled": list(lic["disabledPlans"])})
    for lic in user["directLicenses"]:
        out.append({"source": "direct", "sku": lic["skuPartNumber"], "disabled": list(lic.get("disabledPlans", []))})
    return out


def effective_plans(idx, assigns):
    plans, disabled_by = {}, {}
    for a in assigns:
        for p in idx["skus"][a["sku"]]["servicePlans"]:
            if p in a["disabled"]:
                disabled_by.setdefault(p, []).append(a["source"])
            else:
                plans.setdefault(p, []).append(a["source"])
    return plans, disabled_by


def license_findings(t, idx, user, workloads, extra_groups=(), severity="error", root=False):
    out = []
    plans, disabled_by = effective_plans(idx, assignments(t, idx, user, extra_groups))
    for w in workloads:
        for alt in t["workloads"][w]["requires"]:
            if not any(p in plans for p in alt):
                why = [p + " disabled in " + ",".join(disabled_by[p]) for p in alt if p in disabled_by]
                out.append(finding(
                    "LIC-WORKLOAD-MISSING", severity,
                    "%s: workload '%s' needs one of %s; %s" % (user["upn"], w, alt,
                                                             "; ".join(why) if why else "no assigned SKU includes it"),
                    "Assign a license group whose SKU includes the plan (or re-enable the disabled plan); never hand out ad-hoc direct licenses.",
                    root))
    for p in sorted(plans):
        for alt in t["servicePlans"][p]["requires"]:
            if not any(x in plans for x in alt):
                out.append(finding(
                    "LIC-PREREQ", severity,
                    "%s: plan %s is enabled but its prerequisite %s is not (group-based licensing reports a dependency violation)"
                    % (user["upn"], p, alt),
                    "Fix the license group's disabledPlans so prerequisites stay enabled.", root))
    return out


def device_eval(t, dev, as_of):
    """Lab model of Intune compliance evaluation. Returns (state, findings)."""
    out = []
    if not dev["managed"]:
        return "unmanaged", [finding("DEV-UNMANAGED", "error", "%s is not enrolled in Intune" % dev["name"],
                                     "Enroll via Company Portal (corporate: Autopilot) before granting access.")]
    pol = next((p for p in t["compliancePolicies"] if p["platform"] == dev["platform"]), None)
    if pol is None:
        if t["complianceSettings"]["markNoPolicyAsNoncompliant"]:
            return "noncompliant", [finding("DEV-NO-POLICY", "error", "%s: no compliance policy for %s" % (dev["name"], dev["platform"]),
                                            "Assign the platform compliance policy.")]
        return "compliant", []
    st = pol["settings"]
    w = "%s (%s)" % (dev["name"], pol["id"])
    if "minOsVersion" in st and ver(dev["osVersion"], w) < ver(st["minOsVersion"], w):
        out.append(finding("DEV-OS-MIN", "error", "%s: OS %s below minimum %s" % (w, dev["osVersion"], st["minOsVersion"]),
                           "Update the OS through the update ring (feature update for Windows 10 -> 11)."))
    checks = [("requireBitLocker", "bitLocker", True, "DEV-BITLOCKER", "BitLocker not enabled", "Enable BitLocker via the endpoint security disk encryption policy; escrow the key to Entra."),
              ("requireSecureBoot", "secureBoot", True, "DEV-SECUREBOOT", "Secure Boot off", "Enable Secure Boot in firmware."),
              ("requireDefender", "defender", True, "DEV-DEFENDER", "Defender antimalware not healthy", "Re-enable Defender / check tamper protection."),
              ("requireFirewall", "firewall", True, "DEV-FIREWALL", "Firewall off", "Re-apply firewall profile."),
              ("blockJailbroken", "jailbroken", False, "DEV-JAILBROKEN", "Jailbroken device", "Block; device cannot be made compliant."),
              ("blockRooted", "rooted", False, "DEV-ROOTED", "Rooted device", "Block; device cannot be made compliant."),
              ("requirePasscode", "passcode", True, "DEV-PASSCODE", "No passcode", "Set a device passcode."),
              ("requireEncryption", "encrypted", True, "DEV-ENCRYPTION", "Storage not encrypted", "Enable device encryption.")]
    for setting, fact, good, code, msg, fix in checks:
        if st.get(setting):
            if dev.get(fact) is None:
                out.append(finding(code, "error", "%s: %s not reported (fail-closed)" % (w, fact), fix))
            elif dev[fact] != good:
                out.append(finding(code, "error", "%s: %s" % (w, msg), fix))
    if dev["lastCheckInUtc"] is None or \
            as_of - utc(dev["lastCheckInUtc"], w) > dt.timedelta(days=t["complianceSettings"]["validityPeriodDays"]):
        out.append(finding("DEV-STALE-CHECKIN", "error",
                           "%s: last check-in %s is older than the %d-day compliance validity period"
                           % (w, dev["lastCheckInUtc"], t["complianceSettings"]["validityPeriodDays"]),
                           "Power on, connect to the network and sync from Company Portal; investigate if the device is lost."))
    if not out:
        return "compliant", []
    if dev["firstNoncompliantUtc"] and as_of < utc(dev["firstNoncompliantUtc"], w) + dt.timedelta(hours=pol["gracePeriodHours"]):
        for f in out:
            f["severity"] = "warn"
        out.append(finding("DEV-IN-GRACE", "warn", "%s: within %dh grace period; CA still treats it as compliant"
                           % (w, pol["gracePeriodHours"]), "Fix before the grace period ends."))
        return "inGracePeriod", out
    return "noncompliant", out


def active_issues(t, workload, at):
    res = []
    for s in t["serviceHealth"]:
        if workload not in s["workloads"]:
            continue
        start = utc(s["startUtc"], s["id"])
        end = utc(s["endUtc"], s["id"]) if s["endUtc"] else None
        if start <= at and (end is None or at < end):
            res.append(s)
    return res


def evidence_check(s):
    req = REQUIRED_EVIDENCE[s["type"]]
    have = sorted({e["category"] for e in s["auditEvidence"]})
    missing = [c for c in req if c not in have]
    out = []
    if missing:
        sev = "error" if s["type"] in ("onboarding", "offboarding", "break-glass-usage", "break-glass-review") else "warn"
        out.append(finding("AUD-MISSING", sev, "missing audit evidence categories: %s" % ", ".join(missing),
                           "Attach the artifacts (ticket, log export, report) before closing the change."))
    if s["type"] in APPROVAL_TYPES and not s["input"].get("approvalRef"):
        out.append(finding("AUD-NO-APPROVAL", "error", "no HR/change approval reference",
                           "Joiner/leaver changes need an HR-LAB-/CHG-LAB- approval before any action."))
    return out, {"required": req, "provided": have, "missing": missing}


def user_by(idx, uid):
    return idx["users"][uid]


# ---------------------------------------------------------------- scenario evaluators

def eval_onboarding(t, idx, s, as_of):
    inp = s["input"]
    u = user_by(idx, inp["userId"])
    groups = need(inp, "assignGroups", list, s["id"] + ".input")
    workloads = need(inp, "requiredWorkloads", list, s["id"] + ".input")
    for g in groups:
        if g not in idx["groups"]:
            raise Malformed("SCHEMA-004", "%s: unknown group %s" % (s["id"], g))
    for w in workloads:
        if w not in t["workloads"]:
            raise Malformed("SCHEMA-004", "%s: unknown workload %s" % (s["id"], w))
    f, plan = [], []
    if not u["accountEnabled"]:
        f.append(finding("ONB-ACCOUNT-DISABLED", "error", "%s is disabled" % u["upn"], "Check HR start date / provisioning."))
    plan.append(plan_step("VERIFY_IDENTITY_SOURCE", "Entra Connect: confirm the HR-driven AD account synced (onPremisesSynced=%s)" % u["onPremisesSynced"], u["upn"]))
    if u["usageLocation"] is None:
        direct = bool(u["directLicenses"])
        f.append(finding("LIC-USAGE-LOCATION" if direct else "LIC-USAGE-LOCATION-INHERITED", "error" if direct else "warn",
                         "%s has no usageLocation; %s" % (u["upn"], "direct license assignment will fail" if direct else
                                                         "group-based licensing falls back to the tenant country (%s)" % t["tenant"]["countryCode"]),
                         "Set usageLocation from the HR record (it drives service availability and data-residency reporting)."))
        plan.append(plan_step("SET_USAGE_LOCATION", "Graph: PATCH /v1.0/users/{id} {\"usageLocation\": \"<from HR>\"}", u["upn"]))
    for g in groups:
        sku = idx["skus"][idx["groups"][g]["license"]["skuPartNumber"]]
        if sku["consumed"] >= sku["prepaid"]:
            f.append(finding("LIC-NO-SEATS", "error", "%s has %d/%d seats consumed; adding to %s fails (CountViolation)"
                             % (sku["skuPartNumber"], sku["consumed"], sku["prepaid"], g),
                             "Reclaim seats from leavers or raise a procurement request before day 1."))
        plan.append(plan_step("ADD_LICENSE_GROUP", "Graph: POST /v1.0/groups/{groupId}/members/$ref", "%s -> %s" % (u["upn"], g)))
    f += license_findings(t, idx, u, workloads, groups)
    if not u["mfaMethods"]:
        f.append(finding("ONB-MFA-TAP", "info", "%s has no MFA method yet" % u["upn"],
                         "Issue a one-time Temporary Access Pass on day 1 after in-person ID check; user registers a passkey/FIDO2."))
        plan.append(plan_step("ISSUE_TAP", "Graph: POST /v1.0/users/{id}/authentication/temporaryAccessPassMethods (isUsableOnce=true)", u["upn"]))
    for r in inp.get("roles", []):
        f.append(finding("ONB-PRIV-ROLE", "warn", "%s requested %s at onboarding" % (u["upn"], r),
                         "Grant as PIM-eligible after 30-day probation sign-off; never permanent."))
    dev_id = inp.get("primaryDeviceId")
    if dev_id is not None:
        if dev_id not in idx["devices"]:
            raise Malformed("SCHEMA-004", "%s: unknown device %s" % (s["id"], dev_id))
        state, df = device_eval(t, idx["devices"][dev_id], as_of)
        for x in df:
            x["severity"] = "warn"
        f += df
        plan.append(plan_step("VERIFY_DEVICE_COMPLIANCE", "Intune: managedDevices/{id} complianceState must be compliant before CA004 allows access",
                              "%s (%s)" % (idx["devices"][dev_id]["name"], state)))
    return f, plan


def eval_offboarding(t, idx, s, as_of):
    inp = s["input"]
    u = user_by(idx, inp["userId"])
    kind = need(inp, "terminationType", str, s["id"] + ".input")
    if kind not in ("voluntary", "involuntary"):
        raise Malformed("SCHEMA-004", "%s: terminationType must be voluntary|involuntary" % s["id"])
    legal = need(inp, "legalHold", bool, s["id"] + ".input")
    rb = need(inp, "runbook", list, s["id"] + ".input")
    steps = []
    for i, st in enumerate(rb):
        name = need(st, "step", str, "%s.runbook[%d]" % (s["id"], i))
        if name not in OFFBOARD_STEPS:
            raise Malformed("SCHEMA-004", "%s: unknown runbook step %s" % (s["id"], name))
        if name in DEVICE_STEPS:
            did = need(st, "deviceId", str, "%s.runbook[%d]" % (s["id"], i))
            if did not in idx["devices"] or idx["devices"][did]["ownerId"] != u["id"]:
                raise Malformed("SCHEMA-004", "%s: device %s is not owned by %s" % (s["id"], did, u["upn"]))
        steps.append(st)
    names = [st["step"] for st in steps]
    pos = {}
    for i, n in enumerate(names):
        pos.setdefault(n, i)
    f = []
    if u["id"] in {a["userId"] for a in t["breakGlass"]["accounts"]}:
        f.append(finding("OFF-BREAK-GLASS", "error", "%s is a break-glass account" % u["upn"],
                         "Break-glass accounts are retired only through a CAB-approved emergency-access change."))
    plans, _ = effective_plans(idx, assignments(t, idx, u))
    disable = "DISABLE_ONPREM_AD" if u["onPremisesSynced"] else "DISABLE_SIGNIN"
    required = [disable, "REVOKE_SESSIONS", "REMOVE_AUTH_METHODS", "REMOVE_LICENSES", "EXPORT_AUDIT_EVIDENCE"]
    if u["roles"]:
        required.append("REMOVE_PRIV_ROLES")
    if legal:
        required.append("SET_LITIGATION_HOLD")
    elif any(p in plans for p in ("EXCHANGE_S_ENTERPRISE", "EXCHANGE_S_DESKLESS")):
        required.append("CONVERT_MAILBOX_SHARED")
    if any(p in plans for p in ("SHAREPOINTENTERPRISE", "SHAREPOINTDESKLESS")):
        required.append("TRANSFER_ONEDRIVE")
    for n in required:
        if n not in pos:
            f.append(finding("OFF-MISSING-STEP", "error", "required step %s missing" % n, STEP_REFERENCE[n]))
    owned = [d for d in idx["devices"].values() if d["ownerId"] == u["id"] and d["managed"]]
    acted = {st["deviceId"]: st["step"] for st in steps if st["step"] in DEVICE_STEPS}
    for d in owned:
        if d["id"] not in acted:
            f.append(finding("OFF-MISSING-STEP", "error", "no retire/wipe step for managed device %s" % d["name"],
                             "Corporate: wipe after data hand-over; personal: retire (selective wipe)."))
    for did, act in acted.items():
        d = idx["devices"][did]
        if act == "WIPE_DEVICE" and d["ownership"] == "personal":
            f.append(finding("OFF-BYOD-WIPE", "error", "full wipe of personal device %s would erase personal data" % d["name"],
                             "Use RETIRE_DEVICE (selective wipe of corporate data only) on personal devices."))
        if act == "RETIRE_DEVICE" and d["ownership"] == "corporate":
            f.append(finding("OFF-CORP-RETIRE", "warn", "corporate device %s only retired, not wiped" % d["name"],
                             "Wipe corporate devices (after legal-hold collection) and return them to inventory."))
    if u["onPremisesSynced"] and "DISABLE_SIGNIN" in pos and "DISABLE_ONPREM_AD" not in pos:
        f.append(finding("OFF-SYNCED-SOURCE", "error", "%s is synced from AD DS; a cloud-only disable fails or is overwritten by sync" % u["upn"],
                         "Disable in AD DS (source of authority), then revoke sessions in Entra."))
    disable_pos = [pos[n] for n in DISABLE_STEPS if n in pos]
    first_disable = min(disable_pos) if disable_pos else None
    if first_disable is not None and "REVOKE_SESSIONS" in pos and pos["REVOKE_SESSIONS"] < first_disable:
        f.append(finding("OFF-REVOKE-BEFORE-DISABLE", "error", "sessions revoked before the account is disabled; the user can sign straight back in",
                         "Disable first, then revoke refresh tokens/sessions."))
    if kind == "involuntary" and (len(names) < 2 or names[0] not in DISABLE_STEPS or names[1] not in DISABLE_STEPS | {"REVOKE_SESSIONS"}
                                  or "REVOKE_SESSIONS" not in names[:3]):
        f.append(finding("OFF-INVOLUNTARY-ORDER", "error", "involuntary leaver: disable + revoke must be the first actions",
                         "Run disable and revoke at the time HR notifies the user, before any data steps."))
    if "REMOVE_LICENSES" in pos:
        late = [n for n in RETENTION_STEPS if n in pos and pos[n] > pos["REMOVE_LICENSES"]]
        if late:
            f.append(finding("OFF-LICENSE-BEFORE-RETENTION", "error",
                             "licenses removed before %s; mailbox/OneDrive data enters deletion retention" % ", ".join(sorted(late)),
                             "Apply litigation hold / convert mailbox / transfer OneDrive while the license is still assigned."))
    if "EXPORT_AUDIT_EVIDENCE" in pos and names[-1] != "EXPORT_AUDIT_EVIDENCE":
        f.append(finding("OFF-AUDIT-NOT-LAST", "warn", "audit evidence exported before the last action",
                         "Export audit evidence after the final step so it captures every change."))
    plan = [plan_step(st["step"], STEP_REFERENCE[st["step"]],
                      idx["devices"][st["deviceId"]]["name"] if st["step"] in DEVICE_STEPS else u["upn"]) for st in steps]
    return f, plan


def eval_access(t, idx, s, as_of):
    inp = s["input"]
    u = user_by(idx, inp["userId"])
    workload = need(inp, "workload", str, s["id"] + ".input")
    if workload not in t["workloads"]:
        raise Malformed("SCHEMA-004", "%s: unknown workload %s" % (s["id"], workload))
    reported = utc(need(inp, "reportedUtc", str, s["id"] + ".input"), s["id"] + ".reportedUtc")
    signins = need(inp, "signIns", list, s["id"] + ".input")
    f, plan = [], []
    failing = []
    for i, e in enumerate(signins):
        where = "%s.signIns[%d]" % (s["id"], i)
        code = need(e, "errorCode", int, where)
        if code not in SIGNIN_ERRORS:
            raise Malformed("SCHEMA-004", "%s: unmapped error code %d (fail-closed)" % (where, code))
        utc(need(e, "timeUtc", str, where), where)
        need(e, "id", str, where)
        if e.get("deviceId") is not None and e["deviceId"] not in idx["devices"]:
            raise Malformed("SCHEMA-004", "%s: unknown device" % where)
        if code:
            failing.append(e)
    failing.sort(key=lambda e: e["timeUtc"])
    if failing:
        e = failing[-1]
        code, msg, fix = SIGNIN_ERRORS[e["errorCode"]]
        f.append(finding(code, "error", "sign-in %s (%s): AADSTS%d %s" % (e["id"], e.get("appDisplayName", "?"), e["errorCode"], msg), fix, root=True))
        plan.append(plan_step("READ_SIGNIN_LOG", "Graph: GET /v1.0/auditLogs/signIns?$filter=userId eq '{id}'", e["id"]))
        if e["errorCode"] == 53000:
            dev = idx["devices"].get(e.get("deviceId"))
            if dev is None:
                f.append(finding("DEV-UNREGISTERED", "error", "sign-in came from an unregistered device", "Enroll the device.", root=True))
            else:
                state, df = device_eval(t, dev, as_of)
                for x in df:
                    x["rootCause"] = True
                if state == "compliant":
                    f.append(finding("DEV-STATE-LAG", "warn", "%s evaluates compliant now; CA used an older state" % dev["name"],
                                     "Sync the device and retry; check Intune reporting delays."))
                f += df
                plan.append(plan_step("READ_DEVICE_COMPLIANCE", "Graph: GET /v1.0/deviceManagement/managedDevices/{id}/deviceCompliancePolicyStates", dev["name"]))
            for iss in active_issues(t, "intune", reported):
                f.append(finding("SH-ADVISORY" if iss["classification"] == "advisory" else "SH-KNOWN-INCIDENT", "info",
                                 "%s active: %s" % (iss["id"], iss["title"]),
                                 "Note it in the ticket, but it does not explain the device's own setting violations."))
        if e["errorCode"] in (50076, 50079) and not u["mfaMethods"]:
            plan.append(plan_step("ISSUE_TAP", "Graph: POST /v1.0/users/{id}/authentication/temporaryAccessPassMethods (isUsableOnce=true)", u["upn"]))
    lic = license_findings(t, idx, u, [workload], root=True)
    f += lic
    if lic:
        plan.append(plan_step("READ_LICENSE_STATE", "Graph: GET /v1.0/users/{id}/licenseDetails", u["upn"]))
    for iss in active_issues(t, workload, reported):
        if workload != "intune" or not failing or failing[-1]["errorCode"] != 53000:
            f.append(finding("SH-KNOWN-INCIDENT" if iss["classification"] == "incident" else "SH-ADVISORY",
                             "warn", "%s active for %s: %s" % (iss["id"], workload, iss["title"]),
                             "Link the ticket to the service-health issue.", root=iss["classification"] == "incident"))
    return f, plan


def eval_service_health(t, idx, s, as_of):
    inp = s["input"]
    reports = need(inp, "reports", list, s["id"] + ".input")
    threshold = need(inp, "escalationThreshold", int, s["id"] + ".input")
    by_w = {}
    for i, r in enumerate(reports):
        where = "%s.reports[%d]" % (s["id"], i)
        if need(r, "userId", str, where) not in idx["users"]:
            raise Malformed("SCHEMA-004", "%s: unknown user" % where)
        if need(r, "workload", str, where) not in t["workloads"]:
            raise Malformed("SCHEMA-004", "%s: unknown workload" % where)
        utc(need(r, "reportedUtc", str, where), where)
        by_w.setdefault(r["workload"], []).append(r)
    f, plan = [], []
    for w, rs in sorted(by_w.items()):
        first = min(utc(r["reportedUtc"], w) for r in rs)
        issues = active_issues(t, w, first)
        plan.append(plan_step("READ_SERVICE_HEALTH", "Graph: GET /v1.0/admin/serviceAnnouncement/issues?$filter=status ne 'serviceRestored'", w))
        if any(i["classification"] == "incident" for i in issues):
            for i in issues:
                f.append(finding("SH-KNOWN-INCIDENT" if i["classification"] == "incident" else "SH-ADVISORY", "info",
                                 "%d report(s) for %s match %s: %s" % (len(rs), w, i["id"], i["title"]),
                                 "Link tickets to the issue, post a status-page/Teams-free notice (email + intranet), do not troubleshoot users individually."))
            plan.append(plan_step("COMMUNICATE", "Bank comms template: known Microsoft incident, workaround, next update time", w))
        else:
            for i in issues:
                f.append(finding("SH-ADVISORY", "info", "%s advisory active: %s" % (i["id"], i["title"]), ""))
            recent = [x for x in t["serviceHealth"] if w in x["workloads"] and x["endUtc"]
                      and dt.timedelta(0) <= first - utc(x["endUtc"], x["id"]) <= dt.timedelta(hours=24)]
            for x in recent:
                f.append(finding("SH-RESTORED-RECENTLY", "info", "%s was restored at %s; residual client-side effects possible" % (x["id"], x["endUtc"]),
                                 "Restart Outlook/Teams, clear cached credentials, then troubleshoot locally."))
            if len(rs) >= threshold:
                f.append(finding("SH-ESCALATE-MICROSOFT", "warn", "%d reports for %s with no published issue" % (len(rs), w),
                                 "Open a Microsoft support request (severity by business impact) and notify the incident manager."))
            else:
                f.append(finding("SH-LOCAL-ISSUE", "info", "%d report(s) for %s and no active Microsoft issue" % (len(rs), w),
                                 "Troubleshoot per user (licenses, device compliance, client)."))
        for r in rs:
            u = idx["users"][r["userId"]]
            f += license_findings(t, idx, u, [w], severity="warn")
            for d in idx["devices"].values():
                if d["ownerId"] == u["id"]:
                    state, df = device_eval(t, d, as_of)
                    for x in df:
                        x["severity"] = "warn"
                    f += df
    return f, plan


def eval_bg_review(t, idx, s, as_of):
    f, plan = [], []
    bg = t["breakGlass"]
    accts = bg["accounts"]
    ids = {a["userId"] for a in accts}
    if len(accts) < 2:
        f.append(finding("BG-COUNT", "error", "%d break-glass account(s); at least two are required" % len(accts), "Create a second cloud-only account."))
    for a in accts:
        u = idx["users"][a["userId"]]
        who = u["upn"]
        if u["onPremisesSynced"]:
            f.append(finding("BG-SYNCED", "error", "%s is synced from AD DS" % who, "Break-glass must be cloud-only."))
        if u["upn"].split("@", 1)[1].lower() != t["tenant"]["initialDomain"].lower():
            f.append(finding("BG-DOMAIN", "error", "%s is not on the initial (onmicrosoft) domain" % who,
                             "Use the initial domain so a federation/DNS failure cannot lock it out."))
        if not any(r["role"] == "Global Administrator" and r["assignment"] == "permanent" for r in u["roles"]):
            f.append(finding("BG-ROLE", "error", "%s is not a permanent Global Administrator" % who,
                             "Assign permanently (not PIM-eligible): PIM itself may be unavailable in an emergency."))
        if not any(m in ("fido2", "certificate") for m in u["mfaMethods"]):
            f.append(finding("BG-METHOD", "error", "%s has no phishing-resistant method (FIDO2/CBA)" % who,
                             "Register FIDO2 keys held in separate vaults; mandatory admin-portal MFA applies to these accounts too."))
        if u["licenseGroups"] or u["directLicenses"]:
            f.append(finding("BG-LICENSED", "warn", "%s holds licenses" % who, "Keep break-glass unlicensed: no mailbox, no workload dependency."))
        for p in t["conditionalAccess"]["policies"]:
            if u["id"] not in p["excludeUsers"]:
                f.append(finding("BG-CA-NOT-EXCLUDED", "error", "%s not excluded from %s" % (who, p["policyRef"]),
                                 "Exclude both break-glass accounts from every CA policy (see identity/entra BASE-001)."))
        if not any(r["enabled"] and u["id"] in r["targetsUserIds"] for r in bg["alertRules"]):
            f.append(finding("BG-ALERT", "error", "no enabled sign-in alert for %s" % who, "Alert the SOC on every break-glass sign-in."))
        if a["lastTestedUtc"] is None or as_of - utc(a["lastTestedUtc"], who) > dt.timedelta(days=bg["testIntervalDays"]):
            f.append(finding("BG-TEST-OVERDUE", "warn", "%s last tested %s (> %d days)" % (who, a["lastTestedUtc"], bg["testIntervalDays"]),
                             "Run the quarterly dual-custody sign-in test and record it."))
        if len(set(a["custodyLocations"])) < 2:
            f.append(finding("BG-CUSTODY", "error", "%s credentials not split across two locations" % who, "Split custody across HQ and DR vaults."))
        plan.append(plan_step("REVIEW_BREAK_GLASS", "Graph: GET /v1.0/users/{id}?$select=onPremisesSyncEnabled,userPrincipalName + roleManagement + authentication/methods", who))
    for u in idx["users"].values():
        if u["id"] not in ids and any(r["role"] == "Global Administrator" and r["assignment"] == "permanent" for r in u["roles"]):
            f.append(finding("PRIV-STANDING-GA", "warn", "%s holds standing Global Administrator" % u["upn"],
                             "Convert to PIM-eligible with approval; only break-glass accounts hold standing GA."))
    return f, plan


def eval_bg_usage(t, idx, s, as_of):
    inp = s["input"]
    where = s["id"] + ".input"
    uid = need(inp, "userId", str, where)
    if uid not in {a["userId"] for a in t["breakGlass"]["accounts"]}:
        raise Malformed("SCHEMA-004", "%s: %s is not a break-glass account" % (s["id"], uid))
    used = utc(need(inp, "timeUtc", str, where), where)
    need(inp, "signInId", str, where)
    f, plan = [], []
    if not inp.get("incidentRef"):
        f.append(finding("BG-USE-NO-TICKET", "error", "break-glass use without an incident ticket", "Open an INC- record and link the sign-in."))
    just = inp.get("justificationIssueId")
    iss = next((x for x in t["serviceHealth"] if x["id"] == just), None)
    if iss is None or iss not in active_issues(t, iss["workloads"][0], used):
        f.append(finding("BG-USE-NO-OUTAGE", "warn", "use is not tied to a service-health issue active at %s" % inp["timeUtc"],
                         "Document why normal admin access was unavailable."))
    rot = inp.get("credentialRotatedUtc")
    lim = dt.timedelta(hours=t["breakGlass"]["rotationDeadlineHours"])
    if rot is None or utc(rot, where) - used > lim or utc(rot, where) < used:
        f.append(finding("BG-USE-ROTATION-LATE", "error", "credentials not rotated within %dh of use" % t["breakGlass"]["rotationDeadlineHours"],
                         "Rotate password / re-seal envelope and re-register keys under dual custody."))
    if not inp.get("auditReviewedUtc"):
        f.append(finding("BG-USE-AUDIT-NOT-REVIEWED", "error", "audit log for the session not reviewed", "Second admin reviews every action taken during the session."))
    if not any(r["enabled"] and uid in r["targetsUserIds"] for r in t["breakGlass"]["alertRules"]):
        f.append(finding("BG-ALERT", "error", "no enabled sign-in alert for this account", ""))
    plan += [plan_step("READ_SIGNIN_LOG", "Graph: GET /v1.0/auditLogs/signIns/{id}", inp["signInId"]),
             plan_step("READ_DIRECTORY_AUDIT", "Graph: GET /v1.0/auditLogs/directoryAudits?$filter=initiatedBy/user/id eq '{id}'", uid),
             plan_step("ROTATE_CREDENTIAL", "Dual-custody credential rotation (offline procedure)", uid)]
    return f, plan


EVALUATORS = {"onboarding": eval_onboarding, "offboarding": eval_offboarding, "access-troubleshooting": eval_access,
              "service-health": eval_service_health, "break-glass-review": eval_bg_review, "break-glass-usage": eval_bg_usage}


def verdict(stype, findings):
    sev = {x["severity"] for x in findings}
    codes = {x["code"] for x in findings}
    if stype == "access-troubleshooting":
        return "ROOT_CAUSE_IDENTIFIED" if any(x["rootCause"] for x in findings) else "ESCALATE"
    if stype == "service-health":
        if "SH-KNOWN-INCIDENT" in codes:
            return "KNOWN_SERVICE_INCIDENT"
        return "ESCALATE_TO_MICROSOFT" if "SH-ESCALATE-MICROSOFT" in codes else "LOCAL_ISSUE"
    ok, warn, bad = VERDICTS[stype]
    return bad if "error" in sev else warn if "warn" in sev else ok


def evaluate(t, idx, s):
    as_of = utc(t["asOfUtc"], "asOfUtc")
    f, plan = EVALUATORS[s["type"]](t, idx, s, as_of)
    af, ev = evidence_check(s)
    f += af
    v = verdict(s["type"], f)
    codes = sorted({x["code"] for x in f})
    exp_codes = sorted(set(s["expected"]["findings"]))
    ok = v == s["expected"]["verdict"] and codes == exp_codes
    assert all(p["executed"] is False and p["mode"] == "PLAN_ONLY" for p in plan)
    return {"id": s["id"], "type": s["type"], "title": s["title"], "verdict": v, "expectedVerdict": s["expected"]["verdict"],
            "findingCodes": codes, "expectedFindingCodes": exp_codes,
            "unexpected": sorted(set(codes) - set(exp_codes)), "missingExpected": sorted(set(exp_codes) - set(codes)),
            "result": "PASS" if ok else "FAIL", "findings": f, "plan": plan, "auditEvidence": ev}


# ---------------------------------------------------------------- CLI / reporting

def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += [os.path.join(p, n) for n in sorted(os.listdir(p)) if n.endswith(".json")]
        else:
            files.append(p)
    if not files:
        raise Malformed("SCHEMA-001", "no scenario files")
    return files


def run(tenant_path, paths):
    t = strict_load(tenant_path)
    idx = check_tenant(t)
    scen, seen = [], set()
    for fpath in collect(paths):
        doc = strict_load(fpath)
        for i, s in enumerate(doc if isinstance(doc, list) else [doc]):
            s = check_scenario(s, "%s[%d]" % (os.path.basename(fpath), i), idx)
            if s["id"] in seen:
                raise Malformed("SCHEMA-005", "duplicate scenario id %s" % s["id"])
            seen.add(s["id"])
            scen.append(s)
    results = [evaluate(t, idx, s) for s in scen]
    overall = "PASS" if all(r["result"] == "PASS" for r in results) else "FAIL"
    return {"tool": TOOL, "mode": "offline-synthetic", "tenantStateClaimed": False, "mutationsExecuted": 0,
            "disclaimer": DISCLAIMER, "tenant": {"id": t["tenant"]["id"], "displayName": t["tenant"]["displayName"]},
            "asOfUtc": t["asOfUtc"], "overall": overall, "exitCode": 0 if overall == "PASS" else 1,
            "totals": {"scenarios": len(results), "passed": sum(r["result"] == "PASS" for r in results),
                       "failed": sum(r["result"] != "PASS" for r in results),
                       "plannedSteps": sum(len(r["plan"]) for r in results)},
            "scenarios": results}


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def render_markdown(rep, header=None):
    L = ["# M365 / endpoint operations -- offline scenario report", "", "> **%s**" % rep["disclaimer"], "",
         "| Field | Value |", "|---|---|"]
    for k, v in (header or {}).items():
        L.append("| %s | `%s` |" % (k, v))
    L += ["| Tenant (synthetic) | %s `%s` |" % (esc(rep["tenant"]["displayName"]), rep["tenant"]["id"]),
          "| As of (UTC) | %s |" % rep["asOfUtc"], "| Mutations executed | %d |" % rep["mutationsExecuted"],
          "| Overall | **%s** (%d/%d scenarios matched expectation) |" % (rep["overall"], rep["totals"]["passed"], rep["totals"]["scenarios"]),
          "", "| Scenario | Type | Verdict | Expected | Findings | Result |", "|---|---|---|---|---|---|"]
    for r in rep["scenarios"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (r["id"], r["type"], r["verdict"], r["expectedVerdict"],
                                                    ", ".join(r["findingCodes"]) or "-", r["result"]))
    for r in rep["scenarios"]:
        L += ["", "## %s -- %s" % (r["id"], esc(r["title"])), "", "Verdict **%s** (expected %s): %s" % (r["verdict"], r["expectedVerdict"], r["result"]), ""]
        if r["unexpected"] or r["missingExpected"]:
            L += ["Unexpected: %s; missing: %s" % (r["unexpected"], r["missingExpected"]), ""]
        if r["findings"]:
            L += ["| Code | Severity | Root cause | Detail | Remediation |", "|---|---|---|---|---|"]
            for x in r["findings"]:
                L.append("| %s | %s | %s | %s | %s |" % (x["code"], x["severity"], "yes" if x["rootCause"] else "", esc(x["detail"]), esc(x["remediation"])))
            L.append("")
        if r["plan"]:
            L += ["Plan (PLAN_ONLY, nothing executed):", ""]
            for i, p in enumerate(r["plan"], 1):
                L.append("%d. `%s` %s -- %s" % (i, p["action"], esc(p["target"]), esc(p["reference"])))
            L.append("")
        ev = r["auditEvidence"]
        L.append("Audit evidence: required %s; missing %s" % (", ".join(ev["required"]), ", ".join(ev["missing"]) or "none"))
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", help="scenario files or directories (default: scenarios/)")
    ap.add_argument("--tenant", default=DEFAULT_TENANT)
    ap.add_argument("--json-out")
    ap.add_argument("--md-out")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    try:
        rep = run(a.tenant, a.paths or [DEFAULT_SCENARIOS])
    except Malformed as e:
        rep = {"tool": TOOL, "mode": "offline-synthetic", "tenantStateClaimed": False, "mutationsExecuted": 0,
               "disclaimer": DISCLAIMER, "overall": "MALFORMED", "exitCode": 2, "error": {"rule": e.rule, "message": e.msg}}
        if a.json_out:
            with open(a.json_out, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(rep, indent=2) + "\n")
        print("MALFORMED %s (fail-closed, nothing evaluated)" % e, file=sys.stderr)
        return 2
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(rep, indent=2) + "\n")
    if a.md_out:
        with open(a.md_out, "w", encoding="utf-8") as fh:
            fh.write(render_markdown(rep))
    if not a.quiet:
        for r in rep["scenarios"]:
            print("%-4s %-11s %-24s %-26s %s" % (r["result"], r["id"], r["type"], r["verdict"], ",".join(r["findingCodes"]) or "-"))
            if r["result"] != "PASS":
                print("     expected %s %s; unexpected=%s missing=%s" % (r["expectedVerdict"], r["expectedFindingCodes"], r["unexpected"], r["missingExpected"]))
    print("overall=%s scenarios=%d passed=%d failed=%d plannedSteps=%d mutationsExecuted=0"
          % (rep["overall"], rep["totals"]["scenarios"], rep["totals"]["passed"], rep["totals"]["failed"], rep["totals"]["plannedSteps"]))
    return rep["exitCode"]


if __name__ == "__main__":
    sys.exit(main())
