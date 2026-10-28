#!/usr/bin/env python3
"""Offline Conditional Access (CA) policy validator for the bank IT operations lab.

Validates JSON fixtures shaped like Microsoft Graph ``conditionalAccessPolicy``
objects against (a) a strict structural schema and (b) the bank CA baseline in
``baseline.json``.

OFFLINE / SYNTHETIC ONLY: this tool never contacts Microsoft Entra ID or Graph,
reads no credentials, and its results describe the fixture files given to it,
never the state of any tenant.

Fail-closed: anything unparseable, of the wrong type, with unknown keys or
unknown enum values fails the run; baseline rules are then reported as
NOT_EVALUATED and the overall result is FAIL.

Exit codes:
  0  all schema and baseline rules PASS
  1  input well-formed, one or more baseline rules FAIL
  2  malformed / unknown input (schema FAIL) or usage error -- fail closed

Python standard library only (3.9+).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

TOOL_NAME = "entra-ca-offline-validator"
TOOL_VERSION = "1.0.0"
DISCLAIMER = (
    "OFFLINE / SYNTHETIC: results describe local JSON fixtures only. No Entra ID tenant, "
    "Microsoft Graph API or credential was used. This report makes NO claim about the "
    "configuration or state of any tenant."
)

EXIT_PASS = 0
EXIT_BASELINE_FAIL = 1
EXIT_MALFORMED = 2

GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

VALID_STATES = {"enabled", "disabled", "enabledForReportingButNotEnforced"}
POLICY_KEYS = {
    "@odata.type", "id", "templateId", "displayName", "description", "state",
    "createdDateTime", "modifiedDateTime", "conditions", "grantControls", "sessionControls",
}
POLICY_REQUIRED = {"displayName", "state", "conditions", "grantControls"}
CONDITION_KEYS = {
    "users", "applications", "clientAppTypes", "platforms", "locations", "devices",
    "signInRiskLevels", "userRiskLevels", "servicePrincipalRiskLevels", "insiderRiskLevels",
    "clientApplications", "authenticationFlows",
}
USER_LIST_KEYS = {"includeUsers", "excludeUsers", "includeGroups", "excludeGroups", "includeRoles", "excludeRoles"}
USER_OBJ_KEYS = {"includeGuestsOrExternalUsers", "excludeGuestsOrExternalUsers"}
USER_KEYWORDS = {"All", "None", "GuestsOrExternalUsers"}
APP_LIST_KEYS = {"includeApplications", "excludeApplications", "includeUserActions",
                 "includeAuthenticationContextClassReferences"}
APP_OBJ_KEYS = {"applicationFilter", "globalSecureAccess", "networkAccess"}
APP_KEYWORDS = {"All", "None", "Office365", "MicrosoftAdminPortals"}
USER_ACTIONS = {"urn:user:registersecurityinfo", "urn:user:registerdevice"}
CLIENT_APP_TYPES = {"all", "browser", "mobileAppsAndDesktopClients", "exchangeActiveSync",
                    "easSupported", "other"}
LEGACY_CLIENT_APP_TYPES = {"exchangeActiveSync", "other"}
RISK_LEVELS = {"low", "medium", "high", "hidden", "none"}
PLATFORMS = {"all", "android", "iOS", "windows", "windowsPhone", "macOS", "linux"}
PLATFORM_KEYS = {"includePlatforms", "excludePlatforms"}
LOCATION_KEYS = {"includeLocations", "excludeLocations"}
LOCATION_KEYWORDS = {"All", "AllTrusted"}
BUILT_IN_CONTROLS = {"block", "mfa", "compliantDevice", "domainJoinedDevice",
                     "approvedApplication", "compliantApplication", "passwordChange"}
DEVICE_CONTROLS = {"compliantDevice", "domainJoinedDevice"}
GRANT_KEYS = {"operator", "builtInControls", "customAuthenticationFactors", "termsOfUse",
              "authenticationStrength"}
AUTH_STRENGTH_KEYS = {"id", "displayName", "description", "policyType", "requirementsSatisfied",
                      "allowedCombinations", "createdDateTime", "modifiedDateTime"}
SESSION_KEYS = {"applicationEnforcedRestrictions", "cloudAppSecurity", "signInFrequency",
                "persistentBrowser", "continuousAccessEvaluation", "disableResilienceDefaults",
                "secureSignInSession"}
BASELINE_KEYS = {"_comment", "schemaVersion", "breakGlass", "privilegedRoleTemplateIds",
                 "authenticationStrengths", "riskPoliciesMustBeReportOnly"}

# (id, category, title)
RULES: List[Tuple[str, str, str]] = [
    ("SCHEMA-001", "schema", "Every input file parses as JSON (no duplicate keys) and the policy set is non-empty"),
    ("SCHEMA-002", "schema", "Each policy has the conditionalAccessPolicy shape: required keys present, no unknown keys, correct types"),
    ("SCHEMA-003", "schema", "state is one of enabled | disabled | enabledForReportingButNotEnforced"),
    ("SCHEMA-004", "schema", "conditions (users, applications, clientAppTypes, platforms, locations, risk levels) are well-formed with known values"),
    ("SCHEMA-005", "schema", "grantControls well-formed: operator AND|OR, known builtInControls, block is exclusive, at least one control"),
    ("SCHEMA-006", "schema", "Policy ids and displayNames are unique across the set"),
    ("BASE-001", "baseline", "Break-glass accounts are excluded from every policy (and never explicitly included)"),
    ("BASE-002", "baseline", "Legacy authentication (exchangeActiveSync + other) is blocked for All users on All apps by an enabled policy"),
    ("BASE-003", "baseline", "An enabled policy requires MFA for All users on All apps (AND semantics, only break-glass excluded)"),
    ("BASE-004", "baseline", "All privileged admin roles require phishing-resistant MFA via an enabled policy with no role exclusions"),
    ("BASE-005", "baseline", "No policy blocks All users without exclusions"),
    ("BASE-006", "baseline", "An enabled policy requires a compliant device for All users on All apps"),
    ("BASE-007", "baseline", "Risk-based policies (sign-in / user risk) are report-only during staged rollout"),
]


class InputError(Exception):
    """Raised for malformed input that must fail the run closed."""


def _no_dup_hook(pairs):
    out: Dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise InputError("duplicate JSON key %r" % k)
        out[k] = v
    return out


def _reject_constant(name):
    raise InputError("non-standard JSON constant %s" % name)


def load_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    try:
        return json.loads(text, object_pairs_hook=_no_dup_hook, parse_constant=_reject_constant)
    except InputError as exc:
        raise InputError("%s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s: invalid JSON: %s" % (path, exc))


def load_policy_set(path: str) -> Tuple[List[Tuple[str, Any]], List[str]]:
    """Return ([(source_label, policy_obj)], [errors]). Never raises for bad content."""
    errors: List[str] = []
    policies: List[Tuple[str, Any]] = []
    if os.path.isdir(path):
        files = sorted(f for f in os.listdir(path) if f.endswith(".json"))
        others = sorted(f for f in os.listdir(path)
                        if not f.endswith(".json") and not f.startswith(".") and f.lower() != "readme.md")
        for f in others:
            errors.append("%s: unexpected non-JSON file in policy directory" % os.path.join(path, f))
        sources = [os.path.join(path, f) for f in files]
    elif os.path.isfile(path):
        sources = [path]
    else:
        return [], ["%s: path does not exist" % path]
    for src in sources:
        try:
            doc = load_json(src)
        except InputError as exc:
            errors.append(str(exc))
            continue
        if isinstance(doc, dict) and "value" in doc:
            extra = set(doc) - {"value", "@odata.context"}
            if extra:
                errors.append("%s: unknown keys in Graph list envelope: %s" % (src, sorted(extra)))
            doc = doc["value"]
        if isinstance(doc, list):
            for i, p in enumerate(doc):
                policies.append(("%s[%d]" % (src, i), p))
        else:
            policies.append((src, doc))
    if not policies and not errors:
        errors.append("%s: policy set is empty" % path)
    return policies, errors


def load_baseline(path: str) -> Dict[str, Any]:
    b = load_json(path)
    if not isinstance(b, dict):
        raise InputError("baseline must be a JSON object")
    unknown = set(b) - BASELINE_KEYS
    if unknown:
        raise InputError("baseline has unknown keys: %s" % sorted(unknown))
    bg = b.get("breakGlass")
    if not isinstance(bg, dict) or set(bg) - {"userIds", "groupIds"}:
        raise InputError("baseline.breakGlass must be an object with userIds/groupIds")
    for k in ("userIds", "groupIds"):
        v = bg.get(k, [])
        if not isinstance(v, list) or not all(isinstance(x, str) and GUID_RE.match(x) for x in v):
            raise InputError("baseline.breakGlass.%s must be a list of GUIDs" % k)
    if not bg.get("userIds"):
        raise InputError("baseline.breakGlass.userIds must list at least one break-glass account")
    roles = b.get("privilegedRoleTemplateIds")
    if not isinstance(roles, dict) or not roles or not all(GUID_RE.match(r) for r in roles):
        raise InputError("baseline.privilegedRoleTemplateIds must be a non-empty map of GUID -> name")
    strengths = b.get("authenticationStrengths")
    if (not isinstance(strengths, dict) or not isinstance(strengths.get("phishingResistantMfa"), str)
            or not all(isinstance(v, str) and GUID_RE.match(v) for v in strengths.values())):
        raise InputError("baseline.authenticationStrengths must map names to GUIDs incl. phishingResistantMfa")
    if not isinstance(b.get("riskPoliciesMustBeReportOnly", False), bool):
        raise InputError("baseline.riskPoliciesMustBeReportOnly must be boolean")
    return b


# ----------------------------------------------------------------------------- schema

def _str_list(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) and x for x in v)


def _check_id_list(where: str, v: Any, keywords: set, out: List[str], allow_other=False) -> None:
    if not _str_list(v):
        out.append("%s must be a list of non-empty strings" % where)
        return
    if len(set(v)) != len(v):
        out.append("%s contains duplicates" % where)
    for x in v:
        if x in keywords or GUID_RE.match(x) or allow_other:
            continue
        out.append("%s: %r is neither a GUID nor one of %s" % (where, x, sorted(keywords)))


def check_policy_shape(label: str, p: Any) -> Dict[str, List[str]]:
    """Return {rule_id: [findings]} for SCHEMA-002..005 on one policy."""
    f: Dict[str, List[str]] = {"SCHEMA-002": [], "SCHEMA-003": [], "SCHEMA-004": [], "SCHEMA-005": []}
    s2, s3, s4, s5 = f["SCHEMA-002"], f["SCHEMA-003"], f["SCHEMA-004"], f["SCHEMA-005"]
    if not isinstance(p, dict):
        s2.append("%s: policy must be a JSON object, got %s" % (label, type(p).__name__))
        return f
    missing = POLICY_REQUIRED - set(p)
    if missing:
        s2.append("%s: missing required keys %s" % (label, sorted(missing)))
    unknown = set(p) - POLICY_KEYS
    if unknown:
        s2.append("%s: unknown top-level keys %s" % (label, sorted(unknown)))
    if "displayName" in p and not (isinstance(p["displayName"], str) and p["displayName"].strip()):
        s2.append("%s: displayName must be a non-empty string" % label)
    if "id" in p and not (isinstance(p["id"], str) and GUID_RE.match(p["id"])):
        s2.append("%s: id must be a GUID" % label)
    for k in ("description", "templateId", "createdDateTime", "modifiedDateTime"):
        if k in p and p[k] is not None and not isinstance(p[k], str):
            s2.append("%s: %s must be a string or null" % (label, k))

    if "state" in p and p["state"] not in VALID_STATES:
        s3.append("%s: invalid state %r (allowed %s)" % (label, p.get("state"), sorted(VALID_STATES)))

    # conditions
    c = p.get("conditions")
    if "conditions" in p:
        if not isinstance(c, dict):
            s4.append("%s: conditions must be an object" % label)
        else:
            unknown = set(c) - CONDITION_KEYS
            if unknown:
                s4.append("%s: unknown conditions keys %s" % (label, sorted(unknown)))
            u = c.get("users")
            if not isinstance(u, dict):
                s4.append("%s: conditions.users must be an object" % label)
            else:
                unknown = set(u) - USER_LIST_KEYS - USER_OBJ_KEYS
                if unknown:
                    s4.append("%s: unknown conditions.users keys %s" % (label, sorted(unknown)))
                for k in USER_LIST_KEYS:
                    if k in u:
                        _check_id_list("%s: conditions.users.%s" % (label, k), u[k], USER_KEYWORDS, s4)
                for k in USER_OBJ_KEYS:
                    if k in u and u[k] is not None and not isinstance(u[k], dict):
                        s4.append("%s: conditions.users.%s must be an object or null" % (label, k))
                if not any(u.get(k) for k in ("includeUsers", "includeGroups", "includeRoles",
                                              "includeGuestsOrExternalUsers")):
                    s4.append("%s: conditions.users has no include target" % label)
            a = c.get("applications")
            if not isinstance(a, dict):
                s4.append("%s: conditions.applications must be an object" % label)
            else:
                unknown = set(a) - APP_LIST_KEYS - APP_OBJ_KEYS
                if unknown:
                    s4.append("%s: unknown conditions.applications keys %s" % (label, sorted(unknown)))
                for k in ("includeApplications", "excludeApplications"):
                    if k in a:
                        _check_id_list("%s: conditions.applications.%s" % (label, k), a[k], APP_KEYWORDS, s4)
                if "includeUserActions" in a:
                    if not _str_list(a["includeUserActions"]) or set(a["includeUserActions"]) - USER_ACTIONS:
                        s4.append("%s: conditions.applications.includeUserActions has unknown values" % label)
                if "includeAuthenticationContextClassReferences" in a and \
                        not _str_list(a["includeAuthenticationContextClassReferences"]):
                    s4.append("%s: includeAuthenticationContextClassReferences must be a string list" % label)
                for k in APP_OBJ_KEYS:
                    if k in a and a[k] is not None and not isinstance(a[k], dict):
                        s4.append("%s: conditions.applications.%s must be an object or null" % (label, k))
                if not any(a.get(k) for k in ("includeApplications", "includeUserActions",
                                              "includeAuthenticationContextClassReferences")):
                    s4.append("%s: conditions.applications has no include target" % label)
            cat = c.get("clientAppTypes")
            if not _str_list(cat) or not cat:
                s4.append("%s: conditions.clientAppTypes must be a non-empty string list" % label)
            else:
                bad = set(cat) - CLIENT_APP_TYPES
                if bad:
                    s4.append("%s: unknown clientAppTypes %s" % (label, sorted(bad)))
                if "all" in cat and len(cat) > 1:
                    s4.append("%s: clientAppTypes 'all' must not be combined with other values" % label)
            for k in ("signInRiskLevels", "userRiskLevels", "servicePrincipalRiskLevels"):
                if k in c and c[k] is not None:
                    if not _str_list(c[k]) or set(c[k]) - RISK_LEVELS:
                        s4.append("%s: conditions.%s must be a list drawn from %s" % (label, k, sorted(RISK_LEVELS)))
            if "insiderRiskLevels" in c and c["insiderRiskLevels"] is not None and not isinstance(c["insiderRiskLevels"], str):
                s4.append("%s: conditions.insiderRiskLevels must be a string or null" % label)
            pl = c.get("platforms")
            if pl is not None:
                if not isinstance(pl, dict) or set(pl) - PLATFORM_KEYS:
                    s4.append("%s: conditions.platforms must be an object with include/excludePlatforms" % label)
                else:
                    for k in PLATFORM_KEYS:
                        if k in pl and (not _str_list(pl[k]) or set(pl[k]) - PLATFORMS):
                            s4.append("%s: conditions.platforms.%s has unknown values" % (label, k))
                    if not pl.get("includePlatforms"):
                        s4.append("%s: conditions.platforms.includePlatforms must be non-empty" % label)
            loc = c.get("locations")
            if loc is not None:
                if not isinstance(loc, dict) or set(loc) - LOCATION_KEYS:
                    s4.append("%s: conditions.locations must be an object with include/excludeLocations" % label)
                else:
                    for k in LOCATION_KEYS:
                        if k in loc:
                            _check_id_list("%s: conditions.locations.%s" % (label, k), loc[k], LOCATION_KEYWORDS, s4)
                    if not loc.get("includeLocations"):
                        s4.append("%s: conditions.locations.includeLocations must be non-empty" % label)
            for k in ("devices", "clientApplications", "authenticationFlows"):
                if k in c and c[k] is not None and not isinstance(c[k], dict):
                    s4.append("%s: conditions.%s must be an object or null" % (label, k))

    # grant controls
    g = p.get("grantControls")
    sc = p.get("sessionControls")
    if "sessionControls" in p and sc is not None:
        if not isinstance(sc, dict) or set(sc) - SESSION_KEYS:
            s2.append("%s: sessionControls must be null or an object with known keys" % label)
    if "grantControls" in p:
        if g is None:
            if not sc:
                s5.append("%s: grantControls is null and no sessionControls -- policy enforces nothing" % label)
        elif not isinstance(g, dict):
            s5.append("%s: grantControls must be an object or null" % label)
        else:
            unknown = set(g) - GRANT_KEYS
            if unknown:
                s5.append("%s: unknown grantControls keys %s" % (label, sorted(unknown)))
            if g.get("operator") not in ("AND", "OR"):
                s5.append("%s: grantControls.operator must be AND or OR, got %r" % (label, g.get("operator")))
            bic = g.get("builtInControls", [])
            if not isinstance(bic, list) or not all(isinstance(x, str) for x in bic):
                s5.append("%s: grantControls.builtInControls must be a string list" % label)
                bic = []
            bad = set(bic) - BUILT_IN_CONTROLS
            if bad:
                s5.append("%s: unknown builtInControls %s" % (label, sorted(bad)))
            if len(set(bic)) != len(bic):
                s5.append("%s: builtInControls contains duplicates" % label)
            for k in ("customAuthenticationFactors", "termsOfUse"):
                if k in g and not (isinstance(g[k], list) and all(isinstance(x, str) for x in g[k])):
                    s5.append("%s: grantControls.%s must be a string list" % (label, k))
            st = g.get("authenticationStrength")
            if st is not None:
                if not isinstance(st, dict) or set(st) - AUTH_STRENGTH_KEYS:
                    s5.append("%s: grantControls.authenticationStrength must be an object with known keys" % label)
                elif not (isinstance(st.get("id"), str) and GUID_RE.match(st["id"])):
                    s5.append("%s: grantControls.authenticationStrength.id must be a GUID" % label)
            if "block" in bic and (len(bic) > 1 or st or g.get("termsOfUse") or g.get("customAuthenticationFactors")):
                s5.append("%s: 'block' must be the only grant control" % label)
            if "mfa" in bic and st:
                s5.append("%s: 'mfa' and authenticationStrength cannot be combined" % label)
            if not bic and not st and not g.get("termsOfUse") and not g.get("customAuthenticationFactors"):
                s5.append("%s: grantControls has no controls" % label)
    return f


# ----------------------------------------------------------------------------- helpers

def _users(p) -> Dict[str, List[str]]:
    return p["conditions"]["users"]


def _apps(p) -> Dict[str, List[str]]:
    return p["conditions"]["applications"]


def _grant(p) -> Dict[str, Any]:
    return p.get("grantControls") or {}


def _controls(p) -> List[str]:
    return list(_grant(p).get("builtInControls") or [])


def _is_block(p) -> bool:
    return "block" in _controls(p)


def _targets_all_users(p) -> bool:
    return "All" in (_users(p).get("includeUsers") or [])


def _targets_all_apps(p) -> bool:
    return "All" in (_apps(p).get("includeApplications") or []) and not (_apps(p).get("excludeApplications"))


def _client_types(p) -> set:
    return set(p["conditions"].get("clientAppTypes") or [])


def _covers_modern_clients(p) -> bool:
    t = _client_types(p)
    return "all" in t or {"browser", "mobileAppsAndDesktopClients"} <= t


def _has_risk_condition(p) -> bool:
    c = p["conditions"]
    return bool(c.get("signInRiskLevels") or c.get("userRiskLevels") or c.get("servicePrincipalRiskLevels")
                or c.get("insiderRiskLevels"))


def _narrowing_conditions(p) -> List[str]:
    """Conditions that narrow scope beyond users/apps/clientAppTypes."""
    c = p["conditions"]
    out = []
    if _has_risk_condition(p):
        out.append("risk levels")
    pl = c.get("platforms")
    if pl and (set(pl.get("includePlatforms") or []) != {"all"} or pl.get("excludePlatforms")):
        out.append("platforms")
    loc = c.get("locations")
    if loc and (set(loc.get("includeLocations") or []) != {"All"} or loc.get("excludeLocations")):
        out.append("locations")
    for k in ("devices", "clientApplications", "authenticationFlows"):
        if c.get(k):
            out.append(k)
    return out


def _only_break_glass_excluded(p, baseline) -> Tuple[bool, List[str]]:
    bg = baseline["breakGlass"]
    u = _users(p)
    extra = []
    for k, allowed in (("excludeUsers", set(bg["userIds"])), ("excludeGroups", set(bg.get("groupIds") or []))):
        extra += ["%s:%s" % (k, x) for x in (u.get(k) or []) if x not in allowed]
    if u.get("excludeRoles"):
        extra += ["excludeRoles:%s" % x for x in u["excludeRoles"]]
    if u.get("excludeGuestsOrExternalUsers"):
        extra.append("excludeGuestsOrExternalUsers")
    return (not extra), extra


def _name(p) -> str:
    return p.get("displayName", "<unnamed>")


# ----------------------------------------------------------------------------- baseline rules

def rule_break_glass(policies, baseline) -> List[str]:
    bg = baseline["breakGlass"]
    bg_users, bg_groups = set(bg["userIds"]), set(bg.get("groupIds") or [])
    out = []
    for p in policies:
        u = _users(p)
        excluded = set(u.get("excludeUsers") or [])
        excluded_groups = set(u.get("excludeGroups") or [])
        # every break-glass user excluded directly, or every break-glass group excluded
        users_ok = bg_users <= excluded
        groups_ok = bool(bg_groups) and bg_groups <= excluded_groups
        if not (users_ok or groups_ok):
            out.append("%s: break-glass account(s) not excluded: %s"
                       % (_name(p), sorted(bg_users - excluded)))
        inc = (set(u.get("includeUsers") or []) & bg_users) | (set(u.get("includeGroups") or []) & bg_groups)
        if inc:
            out.append("%s: break-glass object(s) explicitly included: %s" % (_name(p), sorted(inc)))
    return out


def rule_legacy_auth(policies, baseline) -> List[str]:
    for p in policies:
        if (p["state"] == "enabled" and _is_block(p) and _targets_all_users(p) and _targets_all_apps(p)
                and ("all" in _client_types(p) or LEGACY_CLIENT_APP_TYPES <= _client_types(p))
                and not _narrowing_conditions(p) and _only_break_glass_excluded(p, baseline)[0]):
            return []
    return ["no enabled policy blocks clientAppTypes %s for All users / All apps with only break-glass excluded"
            % sorted(LEGACY_CLIENT_APP_TYPES)]


def _requires_mfa(p) -> bool:
    g = _grant(p)
    bic = set(_controls(p))
    strength = g.get("authenticationStrength")
    has_mfa = "mfa" in bic or bool(strength)
    if not has_mfa:
        return False
    # With OR, any other control would satisfy the policy without MFA.
    if g.get("operator") == "OR":
        others = bic - {"mfa"}
        return not others and not g.get("termsOfUse") and not g.get("customAuthenticationFactors")
    return True


def rule_all_users_mfa(policies, baseline) -> List[str]:
    near = []
    for p in policies:
        if not (_targets_all_users(p) and _targets_all_apps(p)):
            continue
        reasons = []
        if p["state"] != "enabled":
            reasons.append("state=%s" % p["state"])
        if not _requires_mfa(p):
            reasons.append("grant does not enforce MFA (needs mfa/authenticationStrength with AND semantics)")
        if not _covers_modern_clients(p):
            reasons.append("clientAppTypes do not cover browser + mobileAppsAndDesktopClients")
        if _narrowing_conditions(p):
            reasons.append("scope narrowed by %s" % _narrowing_conditions(p))
        ok, extra = _only_break_glass_excluded(p, baseline)
        if not ok:
            reasons.append("non-break-glass exclusions %s" % extra)
        if not reasons:
            return []
        if "mfa" in _controls(p) or _grant(p).get("authenticationStrength"):
            near.append("%s: %s" % (_name(p), "; ".join(reasons)))
    return ["no enabled policy requires MFA for All users on All apps"] + near


def rule_admin_phishing_resistant(policies, baseline) -> List[str]:
    required = set(baseline["privilegedRoleTemplateIds"])
    pr_id = baseline["authenticationStrengths"]["phishingResistantMfa"]
    covered = set()
    for p in policies:
        g = _grant(p)
        st = g.get("authenticationStrength") or {}
        if not (p["state"] == "enabled" and st.get("id") == pr_id and _targets_all_apps(p)
                and _covers_modern_clients(p) and not _narrowing_conditions(p)):
            continue
        if g.get("operator") == "OR" and (_controls(p) or g.get("termsOfUse") or g.get("customAuthenticationFactors")):
            continue
        u = _users(p)
        if u.get("excludeRoles"):
            continue
        if not _only_break_glass_excluded(p, baseline)[0]:
            continue
        if _targets_all_users(p):
            covered |= required
        else:
            covered |= set(u.get("includeRoles") or []) & required
    missing = required - covered
    return ["privileged role %s (%s) lacks an enabled phishing-resistant MFA policy on All apps"
            % (r, baseline["privilegedRoleTemplateIds"][r]) for r in sorted(missing)]


def rule_no_unscoped_block(policies, baseline) -> List[str]:
    out = []
    for p in policies:
        if _is_block(p) and _targets_all_users(p):
            u = _users(p)
            if not any(u.get(k) for k in ("excludeUsers", "excludeGroups", "excludeRoles",
                                          "excludeGuestsOrExternalUsers")):
                out.append("%s: blocks All users with no exclusions (tenant lockout risk)" % _name(p))
    return out


def rule_compliant_device(policies, baseline) -> List[str]:
    near = []
    for p in policies:
        if not (_targets_all_users(p) and _targets_all_apps(p)):
            continue
        g = _grant(p)
        bic = set(_controls(p))
        if "compliantDevice" not in bic:
            continue
        reasons = []
        if p["state"] != "enabled":
            reasons.append("state=%s" % p["state"])
        if g.get("operator") == "OR" and (bic - DEVICE_CONTROLS or g.get("authenticationStrength")
                                          or g.get("termsOfUse") or g.get("customAuthenticationFactors")):
            reasons.append("operator OR lets a non-device control satisfy the policy")
        if not _covers_modern_clients(p):
            reasons.append("clientAppTypes do not cover browser + mobileAppsAndDesktopClients")
        if _narrowing_conditions(p):
            reasons.append("scope narrowed by %s" % _narrowing_conditions(p))
        ok, extra = _only_break_glass_excluded(p, baseline)
        if not ok:
            reasons.append("non-break-glass exclusions %s" % extra)
        if not reasons:
            return []
        near.append("%s: %s" % (_name(p), "; ".join(reasons)))
    return ["no enabled policy requires grant control 'compliantDevice' for All users on All apps"] + near


def rule_risk_report_only(policies, baseline) -> List[str]:
    if not baseline.get("riskPoliciesMustBeReportOnly", False):
        return []
    return ["%s: risk-based policy must be enabledForReportingButNotEnforced, is %s" % (_name(p), p["state"])
            for p in policies if _has_risk_condition(p) and p["state"] == "enabled"]


BASELINE_RULES = {
    "BASE-001": rule_break_glass,
    "BASE-002": rule_legacy_auth,
    "BASE-003": rule_all_users_mfa,
    "BASE-004": rule_admin_phishing_resistant,
    "BASE-005": rule_no_unscoped_block,
    "BASE-006": rule_compliant_device,
    "BASE-007": rule_risk_report_only,
}


# ----------------------------------------------------------------------------- driver

def validate(policy_path: str, baseline_path: str) -> Dict[str, Any]:
    findings: Dict[str, List[str]] = {rid: [] for rid, _, _ in RULES}
    baseline = None
    try:
        baseline = load_baseline(baseline_path)
    except InputError as exc:
        findings["SCHEMA-001"].append("baseline: %s" % exc)

    loaded, errors = load_policy_set(policy_path)
    findings["SCHEMA-001"].extend(errors)
    for label, p in loaded:
        try:
            shape = check_policy_shape(label, p)
        except Exception as exc:  # fail closed on any unexpected shape
            shape = {"SCHEMA-002": ["%s: validator error (fail-closed): %s: %s" % (label, type(exc).__name__, exc)]}
        for rid, msgs in shape.items():
            findings[rid].extend(msgs)
    ids, names = {}, {}
    for label, p in loaded:
        if isinstance(p, dict):
            for key, seen in (("id", ids), ("displayName", names)):
                v = p.get(key)
                if isinstance(v, str):
                    if v in seen:
                        findings["SCHEMA-006"].append("duplicate %s %r in %s and %s" % (key, v, seen[v], label))
                    else:
                        seen[v] = label

    schema_ok = baseline is not None and not any(findings[r] for r, cat, _ in RULES if cat == "schema")
    policies = [p for _, p in loaded]
    results = []
    for rid, cat, title in RULES:
        if cat == "schema":
            status = "FAIL" if findings[rid] else "PASS"
        elif not schema_ok:
            status = "NOT_EVALUATED"
            findings[rid] = ["not evaluated: input failed schema validation (fail-closed)"]
        else:
            try:
                findings[rid] = BASELINE_RULES[rid](policies, baseline)
            except Exception as exc:  # fail closed on any unexpected shape
                findings[rid] = ["validator error (fail-closed): %s: %s" % (type(exc).__name__, exc)]
            status = "FAIL" if findings[rid] else "PASS"
        results.append({"id": rid, "category": cat, "title": title, "status": status, "findings": findings[rid]})

    if not schema_ok:
        overall, code = "FAIL", EXIT_MALFORMED
    elif any(r["status"] != "PASS" for r in results):
        overall, code = "FAIL", EXIT_BASELINE_FAIL
    else:
        overall, code = "PASS", EXIT_PASS
    return {
        "tool": TOOL_NAME,
        "toolVersion": TOOL_VERSION,
        "mode": "offline-synthetic",
        "tenantStateClaimed": False,
        "disclaimer": DISCLAIMER,
        "input": {"policies": policy_path, "baseline": baseline_path,
                  "policyCount": len(loaded),
                  "policyNames": [p.get("displayName") if isinstance(p, dict) else None for _, p in loaded]},
        "overall": overall,
        "exitCode": code,
        "rules": results,
    }


def render_markdown(report: Dict[str, Any], extra_header: Optional[Dict[str, str]] = None) -> str:
    lines = ["# Entra Conditional Access -- offline validation report", "",
             "> **%s**" % report["disclaimer"], ""]
    for k, v in (extra_header or {}).items():
        lines.append("- **%s:** `%s`" % (k, v))
    lines += ["- **Tool:** `%s %s`" % (report["tool"], report["toolVersion"]),
              "- **Mode:** `%s` (tenantStateClaimed = `%s`)" % (report["mode"], str(report["tenantStateClaimed"]).lower()),
              "- **Policies input:** `%s` (%d policies)" % (report["input"]["policies"], report["input"]["policyCount"]),
              "- **Baseline:** `%s`" % report["input"]["baseline"],
              "- **Overall:** **%s** (exit code %d)" % (report["overall"], report["exitCode"]), "",
              "| Rule | Category | Result | Title |", "|---|---|---|---|"]
    for r in report["rules"]:
        lines.append("| %s | %s | %s | %s |" % (r["id"], r["category"], r["status"], r["title"]))
    fails = [r for r in report["rules"] if r["findings"]]
    if fails:
        lines += ["", "## Findings", ""]
        for r in fails:
            for msg in r["findings"]:
                lines.append("- `%s` %s" % (r["id"], msg.replace("|", "\\|")))
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("policies", nargs="?", default=os.path.join(here, "policies"),
                    help="policy directory (*.json) or a single JSON file (policy, list, or Graph {value:[...]})")
    ap.add_argument("--baseline", default=os.path.join(here, "baseline.json"))
    ap.add_argument("--json-out", help="write the JSON report to this path")
    ap.add_argument("--md-out", help="write the markdown report to this path")
    ap.add_argument("--quiet", action="store_true", help="do not print the JSON report to stdout")
    args = ap.parse_args(argv)
    report = validate(args.policies, args.baseline)
    text = json.dumps(report, indent=2, sort_keys=False)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    if args.md_out:
        with open(args.md_out, "w", encoding="utf-8") as fh:
            fh.write(render_markdown(report))
    if not args.quiet:
        print(text)
    print("overall=%s exit=%d" % (report["overall"], report["exitCode"]), file=sys.stderr)
    return report["exitCode"]


if __name__ == "__main__":
    sys.exit(main())
