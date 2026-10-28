#!/usr/bin/env python3
"""Regenerate the SYNTHETIC Microsoft Graph fixtures under fixtures/graph/scenarios/.

Every object ID is a synthetic lab GUID ``b9a5e000-0000-4000-8000-<12 hex>``; the tenant is
``bankitlab.example`` (RFC 2606 reserved). Only Entra built-in role template IDs are real
Microsoft-published constants. Response shapes follow Graph v1.0:
unifiedRoleAssignmentScheduleInstance, unifiedRoleEligibilityScheduleInstance, unifiedRoleAssignment,
unifiedRoleDefinition, user, servicePrincipal, group, accessReviewInstanceDecisionItem.

  python3 identity/governance/make_fixtures.py          # write
  python3 identity/governance/make_fixtures.py --check  # fail (exit 1) on drift
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fixtures", "graph", "scenarios")
G = "https://graph.microsoft.com/v1.0"
TENANT = "b9a5e000-0000-4000-8000-0000000000f0"
DOMAIN = "bankitlab.example"
AS_OF = "2026-10-28T12:00:00Z"


def sid(n):
    return "b9a5e000-0000-4000-8000-%012x" % n


ROLE = {
    "GA": ("62e90394-69f5-4237-9190-012177145e10", "Global Administrator"),
    "PRA": ("e8611ab8-c189-46e8-94e1-60213ab1f814", "Privileged Role Administrator"),
    "PAA": ("7be44c8a-adaf-4e2a-84d6-ab2649e08a13", "Privileged Authentication Administrator"),
    "SEC": ("194ae4cb-b126-40b2-bd5b-6091b380977d", "Security Administrator"),
    "CA": ("b1be1c3e-b65d-4f19-8427-f6fa0d97feb9", "Conditional Access Administrator"),
    "EXO": ("29232cdf-9323-42fd-ade2-1d097af3e4de", "Exchange Administrator"),
    "USR": ("fe930be7-5e62-47db-91af-98c3a49a38b1", "User Administrator"),
    "APP": ("9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3", "Application Administrator"),
    "HD": ("729827e3-9c14-49f7-bb1b-9608f156bbb8", "Helpdesk Administrator"),
    "GR": ("f2ef992c-3afb-46b9-b7cf-a126ee74c451", "Global Reader"),
    "DR": ("88d8e3e3-8f55-4a1e-953a-9b9898b8876b", "Directory Readers"),
}

P_ROLEDEFS = "/roleManagement/directory/roleDefinitions?$select=id,displayName,templateId,isBuiltIn"
P_ACTIVE = "/roleManagement/directory/roleAssignmentScheduleInstances"
P_ELIGIBLE = "/roleManagement/directory/roleEligibilityScheduleInstances"
P_ASSIGNMENTS = "/roleManagement/directory/roleAssignments"
P_USERS = "/users?$select=id,displayName,userPrincipalName,userType,accountEnabled"
P_SPS = "/servicePrincipals?$select=id,displayName,appId,servicePrincipalType"
P_GROUPS = "/groups?$filter=isAssignableToRole%20eq%20true&$select=id,displayName,isAssignableToRole"
AR_DEF = sid(0x500)
AR_INST = sid(0x501)
P_AR_DECISIONS = "/identityGovernance/accessReviews/definitions/%s/instances/%s/decisions" % (AR_DEF, AR_INST)


def user(n, name, upn, user_type="Member", enabled=True):
    return {"id": sid(n), "displayName": name, "userPrincipalName": upn, "userType": user_type,
            "accountEnabled": enabled}


USERS = [
    user(0x1, "BG Emergency Access 01", "bg-emergency-01@%s" % DOMAIN),
    user(0x2, "BG Emergency Access 02", "bg-emergency-02@%s" % DOMAIN),
    user(0x10, "Avery Admin (synthetic)", "avery.admin@%s" % DOMAIN),
    user(0x11, "Blake Security (synthetic)", "blake.security@%s" % DOMAIN),
    user(0x12, "Casey Helpdesk (synthetic)", "casey.helpdesk@%s" % DOMAIN),
    user(0x13, "Devon Apps (synthetic)", "devon.apps@%s" % DOMAIN),
    user(0x14, "Emery Identity (synthetic)", "emery.identity@%s" % DOMAIN),
    user(0x15, "Finley Messaging (synthetic)", "finley.messaging@%s" % DOMAIN),
    user(0x16, "Gray Auditor (synthetic)", "gray.auditor@%s" % DOMAIN),
]
SPS = [
    {"id": sid(0x30), "displayName": "svc-directory-sync-reader (synthetic)", "appId": sid(0x130),
     "servicePrincipalType": "Application"},
]
GROUPS = [
    {"id": sid(0x40), "displayName": "grp-role-security-operators (synthetic)", "isAssignableToRole": True},
]


def active(n, who, role, a_type, start, end=None, member="Direct"):
    return {"id": "rasi-" + sid(n), "principalId": who, "roleDefinitionId": ROLE[role][0],
            "directoryScopeId": "/", "appScopeId": None, "startDateTime": start, "endDateTime": end,
            "assignmentType": a_type, "memberType": member, "roleAssignmentOriginId": sid(n + 0x1000),
            "roleAssignmentScheduleId": sid(n + 0x2000)}


def eligible(n, who, role, start, end=None, member="Direct"):
    return {"id": "resi-" + sid(n), "principalId": who, "roleDefinitionId": ROLE[role][0],
            "directoryScopeId": "/", "appScopeId": None, "startDateTime": start, "endDateTime": end,
            "memberType": member, "roleEligibilityScheduleId": sid(n + 0x3000)}


ACTIVE = [
    active(0x201, sid(0x1), "GA", "Assigned", "2026-01-05T00:00:00Z"),
    active(0x202, sid(0x2), "GA", "Assigned", "2026-01-05T00:00:00Z"),
    active(0x203, sid(0x10), "GA", "Activated", "2026-10-28T09:00:00Z", "2026-10-28T13:00:00Z"),
    active(0x204, sid(0x11), "SEC", "Activated", "2026-10-28T10:00:00Z", "2026-10-28T18:00:00Z"),
    active(0x205, sid(0x16), "GR", "Assigned", "2026-02-01T00:00:00Z"),
    active(0x206, sid(0x30), "DR", "Assigned", "2026-02-01T00:00:00Z"),
    active(0x207, sid(0x40), "SEC", "Assigned", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
    active(0x208, sid(0x12), "HD", "Assigned", "2026-08-01T00:00:00Z", "2027-01-31T23:59:59Z"),
]
ELIGIBLE = [
    eligible(0x301, sid(0x10), "GA", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
    eligible(0x302, sid(0x10), "PRA", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
    eligible(0x303, sid(0x11), "SEC", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
    eligible(0x304, sid(0x13), "APP", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
    eligible(0x305, sid(0x14), "PAA", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
    eligible(0x306, sid(0x15), "EXO", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
    eligible(0x307, sid(0x14), "CA", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
    eligible(0x308, sid(0x12), "USR", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
]


def page(context, items, next_path=None):
    body = {"@odata.context": "%s/$metadata#%s" % (G, context), "value": items}
    if next_path:
        body["@odata.nextLink"] = G + next_path
    return body


def paged(prefix, context, base_path, items, size):
    """Split items into pages. Returns (files dict, route entries dict)."""
    chunks = [items[i:i + size] for i in range(0, len(items), size)] or [[]]
    files, routes = {}, {}
    for i, chunk in enumerate(chunks):
        sep = "&" if "?" in base_path else "?"
        path = base_path if i == 0 else "%s%s$skiptoken=SYNTHETIC-%s-PAGE-%d" % (base_path, sep, prefix.upper(), i + 1)
        nxt = None
        if i + 1 < len(chunks):
            nxt = "%s%s$skiptoken=SYNTHETIC-%s-PAGE-%d" % (base_path, sep, prefix.upper(), i + 2)
        fn = "%s.page%d.json" % (prefix, i + 1)
        files[fn] = page(context, chunk, nxt)
        routes[path] = [{"status": 200, "bodyFile": fn}]
    return files, routes


def err(status, code, message, headers=None):
    r = {"status": status, "body": {"error": {"code": code, "message": message,
                                              "innerError": {"request-id": "synthetic-%d-%s" % (status, code),
                                                             "date": AS_OF}}}}
    if headers:
        r["headers"] = headers
    return r


def role_definitions():
    return [{"id": t, "templateId": t, "displayName": name, "isBuiltIn": True} for t, name in ROLE.values()]


def decisions():
    rev = {"id": sid(0x14), "displayName": "Emery Identity (synthetic)", "userPrincipalName": "emery.identity@%s" % DOMAIN}

    def d(n, principal_n, name, decision, applied, rec, reviewer=rev, just=""):
        return {"id": sid(n), "accessReviewId": AR_INST, "decision": decision, "recommendation": rec,
                "justification": just, "reviewedBy": reviewer if decision != "NotReviewed" else
                {"id": "00000000-0000-0000-0000-000000000000", "displayName": "", "userPrincipalName": ""},
                "reviewedDateTime": "2026-10-20T15:00:00Z" if decision != "NotReviewed" else None,
                "applyResult": applied, "appliedDateTime": "2026-10-27T00:05:00Z" if applied != "New" else None,
                "principal": {"@odata.type": "#microsoft.graph.userIdentity", "id": sid(principal_n),
                              "displayName": name},
                "resource": {"id": ROLE["SEC"][0], "displayName": "Security Administrator", "type": "directoryRole"}}
    return [
        d(0x601, 0x11, "Blake Security (synthetic)", "Approve", "AppliedSuccessfully", "Approve", just="on-call SOC"),
        d(0x602, 0x15, "Finley Messaging (synthetic)", "Deny", "AppliedSuccessfully", "Deny", just="no use 90d"),
        d(0x603, 0x13, "Devon Apps (synthetic)", "Deny", "New", "Deny", just="role moved to APP admin"),
        d(0x604, 0x12, "Casey Helpdesk (synthetic)", "NotReviewed", "New", "NoInfoAvailable"),
        d(0x605, 0x14, "Emery Identity (synthetic)", "Approve", "AppliedSuccessfully", "Approve", just="self"),
    ]


def scenarios():
    s = {}
    # ---- baseline (healthy, paginated) --------------------------------------------------------
    files, routes = {}, {}
    for prefix, ctx, path, items, size in (
            ("roleDefinitions", "roleManagement/directory/roleDefinitions(id,displayName,templateId,isBuiltIn)",
             P_ROLEDEFS, role_definitions(), 20),
            ("active", "roleManagement/directory/roleAssignmentScheduleInstances", P_ACTIVE, ACTIVE, 5),
            ("eligible", "roleManagement/directory/roleEligibilityScheduleInstances", P_ELIGIBLE, ELIGIBLE, 3),
            ("users", "users(id,displayName,userPrincipalName,userType,accountEnabled)", P_USERS, USERS, 5),
            ("servicePrincipals", "servicePrincipals(id,displayName,appId,servicePrincipalType)", P_SPS, SPS, 20),
            ("groups", "groups(id,displayName,isAssignableToRole)", P_GROUPS, GROUPS, 20),
            ("accessReviewDecisions", "identityGovernance/accessReviews/definitions('%s')/instances('%s')/decisions"
             % (AR_DEF, AR_INST), P_AR_DECISIONS, decisions(), 3)):
        f, r = paged(prefix, ctx, path, items, size)
        files.update(f)
        routes.update(r)
    s["baseline"] = ({"description": "Healthy synthetic tenant: 2 break-glass permanent GA, JIT (PIM) admins, "
                                     "multi-page collections. Expected exit 0.",
                      "tenantId": TENANT, "asOfUtc": AS_OF, "mode": "pim", "routes": routes}, files)

    # ---- findings ----------------------------------------------------------------------------
    f_users = USERS + [user(0x17, "Harper Former (synthetic)", "harper.former@%s" % DOMAIN, enabled=False),
                       user(0x20, "Partner Consultant (synthetic guest)",
                            "partner.consultant_partner.example#EXT#@%s" % DOMAIN, "Guest")]
    f_sps = SPS + [{"id": sid(0x31), "displayName": "svc-legacy-automation (synthetic)", "appId": sid(0x131),
                    "servicePrincipalType": "Application"}]
    f_active = [a for a in ACTIVE if a["id"] not in ("rasi-" + sid(0x202), "rasi-" + sid(0x204))] + [
        active(0x211, sid(0x15), "GA", "Assigned", "2026-03-01T00:00:00Z"),
        active(0x212, sid(0x13), "GA", "Assigned", "2026-03-01T00:00:00Z"),
        active(0x213, sid(0x14), "GA", "Assigned", "2026-03-01T00:00:00Z"),
        active(0x214, sid(0x20), "SEC", "Assigned", "2026-09-01T00:00:00Z", "2026-12-31T00:00:00Z"),
        active(0x215, sid(0x31), "PRA", "Assigned", "2025-11-01T00:00:00Z"),
        active(0x216, sid(0x12), "EXO", "Assigned", "2026-07-01T00:00:00Z", "2026-10-01T00:00:00Z"),
        active(0x217, sid(0x11), "SEC", "Activated", "2026-10-28T06:00:00Z", "2026-10-29T06:00:00Z"),
    ]
    f_elig = ELIGIBLE + [
        eligible(0x311, sid(0x99), "USR", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
        eligible(0x312, sid(0x17), "EXO", "2026-05-01T00:00:00Z", "2027-04-30T23:59:59Z"),
        eligible(0x313, sid(0x13), "CA", "2026-03-01T00:00:00Z", "2026-09-30T23:59:59Z"),
    ]
    files, routes = {}, {}
    for prefix, ctx, path, items, size in (
            ("active", "roleManagement/directory/roleAssignmentScheduleInstances", P_ACTIVE, f_active, 6),
            ("eligible", "roleManagement/directory/roleEligibilityScheduleInstances", P_ELIGIBLE, f_elig, 6),
            ("users", "users(id,displayName,userPrincipalName,userType,accountEnabled)", P_USERS, f_users, 6),
            ("servicePrincipals", "servicePrincipals(id,displayName,appId,servicePrincipalType)", P_SPS, f_sps, 20)):
        f, r = paged(prefix, ctx, path, items, size)
        files.update(f)
        routes.update(r)
    s["findings"] = ({"inherit": "baseline", "description": "Seeded governance violations (INV-001..009). "
                      "Expected exit 1.", "routes": routes}, files)

    # ---- missing fields ----------------------------------------------------------------------
    mf_active = [ACTIVE[0], ACTIVE[1],
                 {k: v for k, v in active(0x221, sid(0x10), "GA", "Activated", "2026-10-28T09:00:00Z",
                                          "2026-10-28T13:00:00Z").items() if k != "principalId"},
                 {k: v for k, v in active(0x222, sid(0x11), "SEC", "Assigned", "2026-01-01T00:00:00Z",
                                          "2027-01-01T00:00:00Z").items() if k != "roleDefinitionId"},
                 {k: v for k, v in active(0x223, sid(0x12), "HD", "Assigned", "2026-01-01T00:00:00Z",
                                          "2027-01-01T00:00:00Z").items() if k != "id"},
                 {k: v for k, v in active(0x224, sid(0x13), "APP", "Assigned", None,
                                          "2027-01-01T00:00:00Z").items() if k != "startDateTime"},
                 dict(active(0x225, sid(0x14), "CA", "Assigned", "not-a-date", "2027-01-01T00:00:00Z")),
                 dict(active(0x226, sid(0x15), "EXO", "Assigned", "2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z"),
                      assignmentType=None),
                 dict(active(0x227, sid(0x16), "GR", "Assigned", "2026-01-01T00:00:00Z"),
                      roleDefinitionId=sid(0xdead))]
    mf_users = [dict(u) for u in USERS]
    del mf_users[5]["userType"]           # Devon: userType missing -> "Unknown"
    del mf_users[8]["displayName"]        # Gray: displayName missing
    files, routes = {}, {}
    for prefix, ctx, path, items, size in (
            ("active", "roleManagement/directory/roleAssignmentScheduleInstances", P_ACTIVE, mf_active, 4),
            ("users", "users(id,displayName,userPrincipalName,userType,accountEnabled)", P_USERS, mf_users, 9)):
        f, r = paged(prefix, ctx, path, items, size)
        files.update(f)
        routes.update(r)
    s["missing-fields"] = ({"inherit": "baseline", "description": "Records with missing/invalid fields "
                            "(DQ-001..003). Must not crash. Expected exit 1.", "routes": routes}, files)

    # ---- authorization failures --------------------------------------------------------------
    s["auth-401"] = ({"inherit": "baseline", "description": "401 InvalidAuthenticationToken on the first call. "
                      "Expected exit 2, no retry.", "routes": {P_ROLEDEFS: [err(
                          401, "InvalidAuthenticationToken", "Access token is empty. (synthetic)")]}}, {})
    s["auth-403"] = ({"inherit": "baseline", "description": "403 Authorization_RequestDenied on eligibility "
                      "(missing permission/role or license). Expected exit 2, no retry.",
                      "routes": {P_ELIGIBLE: [err(403, "Authorization_RequestDenied",
                                                  "Insufficient privileges to complete the operation. (synthetic)")]}}, {})
    # ---- throttling --------------------------------------------------------------------------
    s["throttled-recover"] = ({"inherit": "baseline", "description": "429 with Retry-After twice, then 200; "
                               "503 without Retry-After once. Expected exit 0 with 3 retries.",
                               "routes": {
                                   P_ACTIVE: [err(429, "TooManyRequests", "Too many requests. (synthetic)",
                                                  {"Retry-After": "3"}),
                                              err(429, "TooManyRequests", "Too many requests. (synthetic)",
                                                  {"Retry-After": "1"}),
                                              {"status": 200, "bodyFile": "../baseline/active.page1.json"}],
                                   P_USERS: [err(503, "ServiceUnavailable", "Service unavailable. (synthetic)"),
                                             {"status": 200, "bodyFile": "../baseline/users.page1.json"}]}}, {})
    s["throttled-exhausted"] = ({"inherit": "baseline", "description": "429 Retry-After 5 forever. Expected "
                                 "exit 2 after the retry budget (4).",
                                 "routes": {P_ACTIVE: [err(429, "TooManyRequests", "Too many requests. (synthetic)",
                                                           {"Retry-After": "5"})]}}, {})
    # ---- paging / malformed ------------------------------------------------------------------
    loop = page("roleManagement/directory/roleEligibilityScheduleInstances", ELIGIBLE[:2], P_ELIGIBLE)
    s["paging-loop"] = ({"inherit": "baseline", "description": "@odata.nextLink points back at the same URL. "
                         "Expected exit 2.", "routes": {P_ELIGIBLE: [{"status": 200, "bodyFile": "eligible.loop.json"}]}},
                        {"eligible.loop.json": loop})
    s["malformed-page"] = ({"inherit": "baseline", "description": "200 page without a value array. Expected exit 2.",
                            "routes": {P_USERS: [{"status": 200, "body": {"@odata.context": G + "/$metadata#users",
                                                                          "values": []}}]}}, {})
    # ---- free tier ---------------------------------------------------------------------------
    assigns = [{"id": "ra-" + sid(n), "principalId": who, "roleDefinitionId": ROLE[r][0], "directoryScopeId": "/"}
               for n, who, r in ((0x401, sid(0x1), "GA"), (0x402, sid(0x2), "GA"), (0x403, sid(0x10), "GA"),
                                 (0x404, sid(0x11), "SEC"), (0x405, sid(0x16), "GR"), (0x406, sid(0x30), "DR"),
                                 (0x407, sid(0x12), "HD"))]
    files, routes = paged("assignments", "roleManagement/directory/roleAssignments", P_ASSIGNMENTS, assigns, 4)
    routes[P_ACTIVE] = [err(403, "Authorization_RequestDenied", "PIM API not available in this synthetic "
                            "free-tier scenario. (synthetic)")]
    s["free-tier"] = ({"inherit": "baseline", "mode": "free", "description": "Entra ID Free fallback: "
                       "roleAssignments only. Expected exit 0 with INV-010 INFO.", "routes": routes}, files)
    return s


def render():
    out = {}
    for name, (routes, files) in scenarios().items():
        out[os.path.join(name, "routes.json")] = json.dumps(routes, indent=2, sort_keys=True) + "\n"
        for fn, body in files.items():
            out[os.path.join(name, fn)] = json.dumps(body, indent=2) + "\n"
    return out


def main():
    check = "--check" in sys.argv[1:]
    want = render()
    have = {}
    for dp, _, fns in os.walk(OUT):
        for fn in fns:
            p = os.path.join(dp, fn)
            with open(p, encoding="utf-8") as fh:
                have[os.path.relpath(p, OUT)] = fh.read()
    drift = sorted(k for k in set(want) | set(have) if want.get(k) != have.get(k))
    if check:
        for k in drift:
            print("drift: %s" % k, file=sys.stderr)
        print("fixtures %s (%d files)" % ("OK" if not drift else "DRIFT", len(want)))
        return 1 if drift else 0
    for k in set(have) - set(want):
        os.remove(os.path.join(OUT, k))
    for k, text in want.items():
        p = os.path.join(OUT, k)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
    print("wrote %d fixture files to %s" % (len(want), os.path.relpath(OUT, os.getcwd())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
