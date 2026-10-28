#!/usr/bin/env python3
"""Dry-run inspector for bank-it-operations-lab patch-cycle manifests.

Reads a patch manifest (JSON) plus the SSM CLI-input files it references and
reports whether the rollout plan is safe to hand to a change board. It NEVER
calls AWS, never runs `aws`, never patches a host: it only parses local files.

Exit codes (same convention as the other lab validators):
  0  manifest parsed and every rule passed
  1  manifest parsed but one or more rules failed
  2  malformed input (unreadable, invalid JSON, duplicate key, wrong type,
     unknown key, missing required field) -- fail closed

Usage:
  python3 operations/patching/tools/inspect_patch_manifest.py MANIFEST [--json] [--plan]

Python stdlib only.
"""
import argparse
import json
import os
import re
import sys

PATCHING_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

TOP_KEYS = {"schemaVersion": str, "exampleData": bool, "manifestId": str, "description": str,
            "changeRecord": str, "baselines": list, "rings": list, "rollback": dict, "escalation": dict}
TOP_REQUIRED = {"schemaVersion", "manifestId", "changeRecord", "baselines", "rings", "rollback", "escalation"}
BASELINE_KEYS = {"id": str, "operatingSystem": str, "source": str, "patchGroups": list}
RING_KEYS = {"name": str, "order": int, "patchGroups": list, "operation": str, "maxConcurrency": str,
             "maxErrors": str, "rebootOption": str, "preSnapshot": bool, "soakHours": int,
             "gate": (dict, type(None)), "windowTask": str}
RING_REQUIRED = set(RING_KEYS) - {"windowTask"}
GATE_KEYS = {"requires": str, "minSoakHours": int, "approvers": list, "evidence": list}
ROLLBACK_KEYS = {"procedure": str, "strategies": list, "maxRollbackMinutes": int}
ESCALATION_KEYS = {"procedure": str, "contacts": list}
CONTACT_KEYS = {"role": str, "channel": str}

OPERATIONS = {"Scan", "Install"}
REBOOT_OPTIONS = {"RebootIfNeeded", "NoReboot"}
ROLLBACK_STRATEGIES = {"package-downgrade", "snapshot-restore", "instance-replace"}
SSM_OS = {"AMAZON_LINUX_2", "AMAZON_LINUX_2023", "REDHAT_ENTERPRISE_LINUX", "UBUNTU", "DEBIAN",
          "CENTOS", "ORACLE_LINUX", "ROCKY_LINUX", "ALMA_LINUX", "SUSE", "WINDOWS", "MACOS"}
RATE_RE = re.compile(r"^(?:[1-9][0-9]*|0)%?$")
ACCOUNT_ID_RE = re.compile(r"(?<![0-9])[0-9]{12}(?![0-9])")
REAL_ID_RE = re.compile(r"\b(?:pb|mw|i|mi)-[0-9a-f]{17}\b")

CANARY_MAX_CONCURRENCY = 1
MIN_GATE_SOAK_HOURS = 24


class Malformed(Exception):
    pass


def _no_dupes(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise Malformed("duplicate key %r" % k)
        seen[k] = v
    return seen


def _reject_constant(name):
    raise Malformed("non-finite number %s" % name)


def load_json(path):
    shown = os.path.relpath(path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        raise Malformed("cannot read %s: %s" % (shown, exc.strerror or exc))
    try:
        return json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_reject_constant), text
    except Malformed as exc:
        raise Malformed("%s: %s" % (shown, exc))
    except ValueError as exc:
        raise Malformed("%s: invalid JSON: %s" % (shown, exc))


def check_shape(obj, spec, required, where):
    if not isinstance(obj, dict):
        raise Malformed("%s: expected object" % where)
    unknown = sorted(set(obj) - set(spec))
    if unknown:
        raise Malformed("%s: unknown key(s) %s" % (where, ", ".join(unknown)))
    missing = sorted(set(required) - set(obj))
    if missing:
        raise Malformed("%s: missing required key(s) %s" % (where, ", ".join(missing)))
    for k, typ in spec.items():
        if k in obj:
            v = obj[k]
            if isinstance(v, bool) and typ is int:
                raise Malformed("%s.%s: expected integer, got boolean" % (where, k))
            if not isinstance(v, typ):
                raise Malformed("%s.%s: wrong type %s" % (where, k, type(v).__name__))


def str_list(v, where, allow_empty=False):
    if not all(isinstance(x, str) and x for x in v):
        raise Malformed("%s: expected list of non-empty strings" % where)
    if not v and not allow_empty:
        raise Malformed("%s: must not be empty" % where)


def resolve(manifest_dir, rel, where):
    if os.path.isabs(rel):
        raise Malformed("%s: path must be relative: %s" % (where, rel))
    path = os.path.abspath(os.path.join(manifest_dir, rel))
    return path


def parse_rate(s, where):
    if not RATE_RE.match(s):
        raise Malformed("%s: %r is not an integer or percentage" % (where, s))
    if s.endswith("%"):
        pct = int(s[:-1])
        if pct > 100:
            raise Malformed("%s: percentage over 100" % where)
        return ("pct", pct)
    return ("abs", int(s))


def validate_structure(m):
    check_shape(m, TOP_KEYS, TOP_REQUIRED, "manifest")
    if m["schemaVersion"] != "1.0.0":
        raise Malformed("manifest.schemaVersion: unsupported %r" % m["schemaVersion"])
    if not m["baselines"]:
        raise Malformed("manifest.baselines: must not be empty")
    if not m["rings"]:
        raise Malformed("manifest.rings: must not be empty")
    for i, b in enumerate(m["baselines"]):
        w = "baselines[%d]" % i
        check_shape(b, BASELINE_KEYS, set(BASELINE_KEYS), w)
        str_list(b["patchGroups"], w + ".patchGroups")
    for i, r in enumerate(m["rings"]):
        w = "rings[%d]" % i
        check_shape(r, RING_KEYS, RING_REQUIRED, w)
        str_list(r["patchGroups"], w + ".patchGroups")
        parse_rate(r["maxConcurrency"], w + ".maxConcurrency")
        parse_rate(r["maxErrors"], w + ".maxErrors")
        if r["gate"] is not None:
            check_shape(r["gate"], GATE_KEYS, set(GATE_KEYS), w + ".gate")
            str_list(r["gate"]["approvers"], w + ".gate.approvers", allow_empty=True)
            str_list(r["gate"]["evidence"], w + ".gate.evidence", allow_empty=True)
    check_shape(m["rollback"], ROLLBACK_KEYS, set(ROLLBACK_KEYS), "rollback")
    str_list(m["rollback"]["strategies"], "rollback.strategies", allow_empty=True)
    check_shape(m["escalation"], ESCALATION_KEYS, set(ESCALATION_KEYS), "escalation")
    for i, c in enumerate(m["escalation"]["contacts"]):
        check_shape(c, CONTACT_KEYS, set(CONTACT_KEYS), "escalation.contacts[%d]" % i)


def inspect(path):
    """Return a report dict. Raises Malformed for exit-2 conditions."""
    manifest, raw = load_json(path)
    validate_structure(manifest)
    mdir = os.path.dirname(os.path.abspath(path))
    results = []

    def rule(rule_id, ok, detail):
        results.append({"rule": rule_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    # --- referenced files (loaded first so malformed references fail closed) ---
    baselines = {}
    for b in manifest["baselines"]:
        src = resolve(mdir, b["source"], "baselines[%s].source" % b["id"])
        if not os.path.isfile(src):
            rule("PM-REF-BASELINE", False, "baseline %s: source not found %s" % (b["id"], b["source"]))
            continue
        doc, text = load_json(src)
        baselines[b["id"]] = (b, doc, text)
    tasks = {}
    for r in manifest["rings"]:
        if "windowTask" in r:
            src = resolve(mdir, r["windowTask"], "rings[%s].windowTask" % r["name"])
            if not os.path.isfile(src):
                rule("PM-REF-TASK", False, "ring %s: windowTask not found %s" % (r["name"], r["windowTask"]))
                continue
            doc, text = load_json(src)
            tasks[r["name"]] = (doc, text)

    # --- ring ordering ---
    rings = sorted(manifest["rings"], key=lambda r: r["order"])
    names = [r["name"] for r in rings]
    orders = [r["order"] for r in rings]
    rule("PM-RING-ORDER", orders == list(range(1, len(rings) + 1)) and len(set(names)) == len(names),
         "ring orders %s must be 1..N and names unique" % orders)

    first = rings[0]
    c_kind, c_val = parse_rate(first["maxConcurrency"], "canary")
    e_kind, e_val = parse_rate(first["maxErrors"], "canary")
    rule("PM-CANARY-SIZE", c_kind == "abs" and 1 <= c_val <= CANARY_MAX_CONCURRENCY,
         "first ring %r maxConcurrency=%s (must be an absolute count <= %d)"
         % (first["name"], first["maxConcurrency"], CANARY_MAX_CONCURRENCY))
    rule("PM-CANARY-ERRORS", e_val == 0,
         "first ring %r maxErrors=%s (must be 0: any canary failure stops the ring)"
         % (first["name"], first["maxErrors"]))
    rule("PM-CANARY-NOGATE", first["gate"] is None,
         "first ring %r must not depend on a gate" % first["name"])

    all_groups = {g for b in manifest["baselines"] for g in b["patchGroups"]}
    seen_groups = {}
    for idx, r in enumerate(rings):
        n = r["name"]
        rule("PM-OPERATION", r["operation"] in OPERATIONS, "ring %s operation=%s" % (n, r["operation"]))
        rule("PM-REBOOT", r["rebootOption"] in REBOOT_OPTIONS, "ring %s rebootOption=%s" % (n, r["rebootOption"]))
        unknown = sorted(set(r["patchGroups"]) - all_groups)
        rule("PM-PATCHGROUP-KNOWN", not unknown,
             "ring %s patch groups not registered to any baseline: %s" % (n, unknown or "none"))
        dup = sorted(g for g in r["patchGroups"] if g in seen_groups)
        rule("PM-PATCHGROUP-UNIQUE", not dup,
             "ring %s reuses patch groups already in another ring: %s" % (n, dup or "none"))
        for g in r["patchGroups"]:
            seen_groups[g] = n
        if r["operation"] == "Install":
            rule("PM-PRESNAPSHOT", r["preSnapshot"], "ring %s installs; preSnapshot must be true" % n)
        rule("PM-SOAK", r["soakHours"] >= 0, "ring %s soakHours=%d" % (n, r["soakHours"]))
        if idx > 0:
            g = r["gate"]
            prev = rings[idx - 1]["name"]
            if g is None:
                rule("PM-GATE-PRESENT", False, "ring %s has no approval gate" % n)
                continue
            rule("PM-GATE-PRESENT", True, "ring %s gated" % n)
            rule("PM-GATE-ORDER", g["requires"] == prev,
                 "ring %s gate requires %r; previous ring is %r" % (n, g["requires"], prev))
            rule("PM-GATE-APPROVERS", len(g["approvers"]) >= 1, "ring %s approvers=%s" % (n, g["approvers"]))
            rule("PM-GATE-SOAK", g["minSoakHours"] >= MIN_GATE_SOAK_HOURS,
                 "ring %s minSoakHours=%d (>= %d)" % (n, g["minSoakHours"], MIN_GATE_SOAK_HOURS))
            rule("PM-GATE-EVIDENCE", "compliance-summary" in g["evidence"],
                 "ring %s gate evidence must include compliance-summary" % n)

    # --- baselines ---
    for bid, (b, doc, _text) in sorted(baselines.items()):
        rule("PM-BASELINE-OS", b["operatingSystem"] in SSM_OS and doc.get("OperatingSystem") == b["operatingSystem"],
             "baseline %s manifest OS %s vs file OS %s" % (bid, b["operatingSystem"], doc.get("OperatingSystem")))
        rule("PM-BASELINE-REJECT-BLOCK", doc.get("RejectedPatchesAction") == "BLOCK",
             "baseline %s RejectedPatchesAction=%s" % (bid, doc.get("RejectedPatchesAction")))
        prules = (doc.get("ApprovalRules") or {}).get("PatchRules") or []
        delayed = bool(prules) and all(isinstance(p, dict) and ("ApproveAfterDays" in p or "ApproveUntilDate" in p)
                                       for p in prules)
        rule("PM-BASELINE-DELAY", delayed,
             "baseline %s: every approval rule needs ApproveAfterDays/ApproveUntilDate (%d rules)" % (bid, len(prules)))

    # --- window tasks vs manifest ---
    for r in rings:
        if r["name"] not in tasks:
            continue
        doc, _ = tasks[r["name"]]
        params = ((doc.get("TaskInvocationParameters") or {}).get("RunCommand") or {}).get("Parameters") or {}
        rule("PM-TASK-DOCUMENT", doc.get("TaskArn") == "AWS-RunPatchBaseline" and doc.get("TaskType") == "RUN_COMMAND",
             "ring %s task %s/%s" % (r["name"], doc.get("TaskArn"), doc.get("TaskType")))
        rule("PM-TASK-RATES", doc.get("MaxConcurrency") == r["maxConcurrency"] and doc.get("MaxErrors") == r["maxErrors"],
             "ring %s task MaxConcurrency/MaxErrors %s/%s vs manifest %s/%s"
             % (r["name"], doc.get("MaxConcurrency"), doc.get("MaxErrors"), r["maxConcurrency"], r["maxErrors"]))
        op = (params.get("Operation") or [None])[0]
        if r["gate"] is not None:
            rule("PM-TASK-GATED-SCAN", op == "Scan",
                 "gated ring %s ships its task as Operation=%s (must be Scan until the gate is approved)" % (r["name"], op))
        else:
            rule("PM-TASK-OPERATION", op == r["operation"], "ring %s task Operation=%s vs manifest %s"
                 % (r["name"], op, r["operation"]))
        reboot = (params.get("RebootOption") or [None])[0]
        rule("PM-TASK-REBOOT", reboot == r["rebootOption"], "ring %s task RebootOption=%s" % (r["name"], reboot))

    # --- rollback / escalation ---
    rb = manifest["rollback"]
    rule("PM-ROLLBACK-PROCEDURE", os.path.isfile(resolve(mdir, rb["procedure"], "rollback.procedure")),
         "rollback procedure %s exists" % rb["procedure"])
    bad = sorted(set(rb["strategies"]) - ROLLBACK_STRATEGIES)
    rule("PM-ROLLBACK-STRATEGY", bool(rb["strategies"]) and not bad,
         "rollback strategies %s (unknown: %s)" % (rb["strategies"], bad or "none"))
    rule("PM-ROLLBACK-TIME", 0 < rb["maxRollbackMinutes"] <= 240, "maxRollbackMinutes=%d" % rb["maxRollbackMinutes"])
    es = manifest["escalation"]
    rule("PM-ESCALATION-PROCEDURE", os.path.isfile(resolve(mdir, es["procedure"], "escalation.procedure")),
         "escalation procedure %s exists" % es["procedure"])
    rule("PM-ESCALATION-CONTACTS", len(es["contacts"]) >= 1, "%d escalation contacts" % len(es["contacts"]))

    # --- no real identifiers in example data ---
    texts = [raw] + [t for _, _, t in baselines.values()] + [t for _, t in tasks.values()]
    leaks = sorted({m for t in texts for m in ACCOUNT_ID_RE.findall(t) + REAL_ID_RE.findall(t)})
    rule("PM-NO-REAL-IDS", not leaks, "account/resource ids found: %s" % (leaks or "none"))

    failed = [r for r in results if r["result"] == "FAIL"]
    return {
        "tool": "inspect_patch_manifest",
        "mode": "dry-run",
        "awsCallsMade": False,
        "manifest": os.path.relpath(os.path.abspath(path), os.getcwd()),
        "manifestId": manifest["manifestId"],
        "exampleData": manifest.get("exampleData", False),
        "overall": "FAIL" if failed else "PASS",
        "rules": results,
        "plan": [{"order": r["order"], "ring": r["name"], "patchGroups": r["patchGroups"],
                  "operation": r["operation"], "maxConcurrency": r["maxConcurrency"],
                  "maxErrors": r["maxErrors"], "soakHours": r["soakHours"],
                  "gate": r["gate"]} for r in rings],
    }


def render_text(rep, plan):
    out = ["patch manifest %s (%s) -- DRY RUN, no AWS calls" % (rep["manifestId"], rep["manifest"])]
    if rep["exampleData"]:
        out.append("NOTE: manifest is marked exampleData=true")
    for r in rep["rules"]:
        out.append("  [%s] %-24s %s" % (r["result"], r["rule"], r["detail"]))
    if plan:
        out.append("planned rollout (would happen only after approval; nothing is executed):")
        for p in rep["plan"]:
            gate = "after %s + %dh soak, approvers=%s" % (p["gate"]["requires"], p["gate"]["minSoakHours"],
                                                         ",".join(p["gate"]["approvers"])) if p["gate"] else "first ring"
            out.append("  %d. %-7s %-8s groups=%s concurrency=%s errors=%s soak=%dh (%s)"
                       % (p["order"], p["ring"], p["operation"], ",".join(p["patchGroups"]),
                          p["maxConcurrency"], p["maxErrors"], p["soakHours"], gate))
    out.append("overall: %s" % rep["overall"])
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("manifest")
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    ap.add_argument("--plan", action="store_true", help="also print the dry-run rollout plan")
    a = ap.parse_args(argv)
    try:
        rep = inspect(a.manifest)
    except Malformed as exc:
        msg = {"tool": "inspect_patch_manifest", "overall": "MALFORMED", "error": str(exc)}
        print(json.dumps(msg, indent=2) if a.json else "MALFORMED: %s" % exc)
        return 2
    print(json.dumps(rep, indent=2) if a.json else render_text(rep, a.plan))
    return 0 if rep["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
