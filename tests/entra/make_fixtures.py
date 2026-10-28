#!/usr/bin/env python3
"""Regenerate the negative / malformed CA fixtures under tests/entra/fixtures/.

Each fixture is derived from the known-good baseline set in identity/entra/policies/
by one targeted mutation, and written in the Graph list shape {"value": [...]}.
All IDs are synthetic lab GUIDs. Run from anywhere:

    python3 tests/entra/make_fixtures.py          # write fixtures
    python3 tests/entra/make_fixtures.py --check  # exit 1 if committed fixtures drifted
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
POLICY_DIR = os.path.join(ROOT, "identity", "entra", "policies")
OUT = os.path.join(HERE, "fixtures")
CTX = "OFFLINE SYNTHETIC FIXTURE -- not exported from any tenant"


def load_valid():
    names = sorted(f for f in os.listdir(POLICY_DIR) if f.endswith(".json"))
    out = []
    for n in names:
        with open(os.path.join(POLICY_DIR, n), encoding="utf-8") as fh:
            out.append(json.load(fh))
    return out


def by_prefix(policies, prefix):
    for p in policies:
        if p["displayName"].startswith(prefix):
            return p
    raise KeyError(prefix)


def mutate(fn):
    ps = copy.deepcopy(load_valid())
    fn(ps)
    return {"@odata.context": CTX, "value": ps}


def _set(prefix, path, value):
    def f(ps):
        o = by_prefix(ps, prefix)
        for k in path[:-1]:
            o = o[k]
        o[path[-1]] = value
    return f


def _del(prefix, path):
    def f(ps):
        o = by_prefix(ps, prefix)
        for k in path[:-1]:
            o = o[k]
        del o[path[-1]]
    return f


def _drop(prefix):
    def f(ps):
        ps.remove(by_prefix(ps, prefix))
    return f


GLOBAL_ADMIN = "62e90394-69f5-4237-9190-012177145e10"

# name -> (json document or raw text, description)
FIXTURES = {
    # ---- positive
    "valid-graph-envelope.json": (mutate(lambda ps: None), "valid baseline set in Graph {value:[...]} shape"),
    # ---- baseline negatives (well-formed, exit 1)
    "neg-missing-mfa.json": (mutate(_set("CA002", ["grantControls", "builtInControls"], ["approvedApplication"])),
                             "All-users policy grants approvedApplication instead of MFA"),
    "neg-mfa-policy-removed.json": (mutate(_drop("CA002")), "All-users MFA policy absent"),
    "neg-mfa-or-bypass.json": (mutate(_set("CA002", ["grantControls"], {
        "operator": "OR", "builtInControls": ["mfa", "compliantApplication"], "customAuthenticationFactors": [],
        "termsOfUse": [], "authenticationStrength": None})), "MFA ORed with compliantApplication (bypassable)"),
    "neg-mfa-report-only.json": (mutate(_set("CA002", ["state"], "enabledForReportingButNotEnforced")),
                                 "All-users MFA only report-only"),
    "neg-mfa-extra-exclusion.json": (mutate(_set("CA002", ["conditions", "users", "excludeGroups"],
                                                 ["a11ab000-0000-4000-8000-0000000000aa"])),
                                     "All-users MFA excludes a non-break-glass group"),
    "neg-missing-compliant-device.json": (mutate(_set("CA004", ["grantControls", "builtInControls"], ["mfa"])),
                                          "device policy grant lacks compliantDevice"),
    "neg-device-or-bypass.json": (mutate(_set("CA004", ["grantControls"], {
        "operator": "OR", "builtInControls": ["compliantDevice", "mfa"], "customAuthenticationFactors": [],
        "termsOfUse": [], "authenticationStrength": None})), "compliantDevice ORed with mfa (non-compliant device passes)"),
    "neg-device-disabled.json": (mutate(_set("CA004", ["state"], "disabled")), "compliant device policy disabled"),
    "neg-break-glass-not-excluded.json": (mutate(_set("CA002", ["conditions", "users", "excludeUsers"],
                                                      ["b9a5e000-0000-4000-8000-000000000001"])),
                                          "second break-glass account not excluded from MFA policy"),
    "neg-break-glass-included.json": (mutate(_set("CA003", ["conditions", "users", "includeUsers"],
                                                  ["b9a5e000-0000-4000-8000-000000000002"])),
                                      "break-glass account explicitly included"),
    "neg-unscoped-block.json": (mutate(_set("CA001", ["conditions", "users", "excludeUsers"], [])),
                                "legacy-auth block targets All users with no exclusions"),
    "neg-legacy-auth-not-blocked.json": (mutate(_set("CA001", ["state"], "disabled")), "legacy auth block disabled"),
    "neg-legacy-auth-partial.json": (mutate(_set("CA001", ["conditions", "clientAppTypes"], ["exchangeActiveSync"])),
                                     "legacy block omits 'other' clients"),
    "neg-admin-weak-strength.json": (mutate(_set("CA003", ["grantControls", "authenticationStrength"],
                                                 {"id": "00000000-0000-0000-0000-000000000002", "displayName": "MFA"})),
                                     "admin roles use plain MFA strength, not phishing-resistant"),
    "neg-admin-role-missing.json": (mutate(lambda ps: by_prefix(ps, "CA003")["conditions"]["users"]["includeRoles"].remove(GLOBAL_ADMIN)),
                                    "Global Administrator not targeted by admin policy"),
    "neg-admin-role-excluded.json": (mutate(_set("CA003", ["conditions", "users", "excludeRoles"], [GLOBAL_ADMIN])),
                                     "admin policy excludes Global Administrator"),
    "neg-risk-enforced.json": (mutate(_set("CA005", ["state"], "enabled")), "risk policy enforced before staged rollout"),
    # ---- malformed (fail closed, exit 2)
    "malformed-truncated.json": ('{"value": [{"displayName": "CA-trunc", "state": "enab', "truncated JSON"),
    "malformed-nan.json": ('{"displayName": "x", "state": "enabled", "conditions": NaN, "grantControls": null}',
                           "non-standard JSON constant"),
    "malformed-duplicate-key.json": ('{"displayName": "dup", "state": "enabled", "state": "disabled", '
                                     '"conditions": {}, "grantControls": null}', "duplicate JSON key"),
    "malformed-not-object.json": (["CA001", "CA002"], "policies are strings, not objects"),
    "malformed-empty-set.json": ({"value": []}, "empty policy set"),
    "malformed-unknown-top-key.json": (mutate(_set("CA002", ["enforceEverywhere"], True)), "unknown top-level key"),
    "malformed-unknown-condition.json": (mutate(_set("CA002", ["conditions", "deviceStates"], {"includeStates": ["All"]})),
                                         "unknown / deprecated conditions key"),
    "malformed-invalid-state.json": (mutate(_set("CA002", ["state"], "on")), "invalid state value"),
    "malformed-missing-state.json": (mutate(_del("CA002", ["state"])), "state missing"),
    "malformed-unknown-control.json": (mutate(_set("CA002", ["grantControls", "builtInControls"], ["requireMagic"])),
                                       "unknown builtInControl"),
    "malformed-bad-operator.json": (mutate(_set("CA002", ["grantControls", "operator"], "XOR")), "invalid grant operator"),
    "malformed-block-combined.json": (mutate(_set("CA001", ["grantControls", "builtInControls"], ["block", "mfa"])),
                                      "block combined with other controls"),
    "malformed-empty-grant.json": (mutate(_set("CA002", ["grantControls", "builtInControls"], [])), "grant with no controls"),
    "malformed-wrong-type.json": (mutate(_set("CA002", ["conditions", "users", "includeUsers"], "All")),
                                  "includeUsers is a string, not a list"),
    "malformed-bad-guid.json": (mutate(_set("CA002", ["conditions", "users", "excludeUsers"], ["breakglass@bank.example"])),
                                "UPN instead of object id GUID"),
    "malformed-unknown-client-app.json": (mutate(_set("CA001", ["conditions", "clientAppTypes"], ["exchangeActiveSync", "pop3"])),
                                          "unknown clientAppType"),
    "malformed-bad-risk-level.json": (mutate(_set("CA005", ["conditions", "signInRiskLevels"], ["critical"])),
                                      "unknown risk level"),
    "malformed-duplicate-id.json": (mutate(lambda ps: ps.append(copy.deepcopy(ps[0]))), "duplicate policy id/name"),
    "malformed-no-users-target.json": (mutate(_set("CA002", ["conditions", "users"], {"excludeUsers": []})),
                                       "users condition has no include target"),
}


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def render(doc):
    return doc if isinstance(doc, str) else json.dumps(doc, indent=2) + "\n"


def main(argv):
    check = "--check" in argv
    os.makedirs(OUT, exist_ok=True)
    drift = []
    index = {}
    for name, (doc, desc) in sorted(FIXTURES.items()):
        index[name] = desc
        path = os.path.join(OUT, name)
        text = render(doc)
        if check:
            if not os.path.exists(path) or _read(path) != text:
                drift.append(name)
        else:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
    idx_text = json.dumps({"_note": CTX, "fixtures": index}, indent=2) + "\n"
    idx_path = os.path.join(OUT, "INDEX.json")
    if check:
        if not os.path.exists(idx_path) or _read(idx_path) != idx_text:
            drift.append("INDEX.json")
        extra = sorted(set(os.listdir(OUT)) - set(FIXTURES) - {"INDEX.json"})
        drift += ["unexpected:%s" % e for e in extra]
        if drift:
            print("fixture drift: %s" % drift, file=sys.stderr)
            return 1
        return 0
    with open(idx_path, "w", encoding="utf-8") as fh:
        fh.write(idx_text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
