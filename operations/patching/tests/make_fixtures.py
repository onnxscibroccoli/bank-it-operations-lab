#!/usr/bin/env python3
"""Regenerate operations/patching/tests/fixtures/ from the example manifest.

Each fixture is a single mutation of manifests/patch-manifest.example.json with paths rewritten
for the fixtures directory. Prefix encodes the expected inspector exit code:
valid- 0, neg- 1, malformed- 2. `--check` exits 1 if committed fixtures drift.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")
SRC = os.path.join(HERE, "..", "manifests", "patch-manifest.example.json")


def base():
    with open(SRC, encoding="utf-8") as fh:
        m = json.load(fh)
    def fix(p):
        return "../../" + p[len("../"):] if p.startswith("../") else p
    for b in m["baselines"]:
        b["source"] = fix(b["source"])
    for r in m["rings"]:
        if "windowTask" in r:
            r["windowTask"] = fix(r["windowTask"])
    m["rollback"]["procedure"] = fix(m["rollback"]["procedure"])
    m["escalation"]["procedure"] = fix(m["escalation"]["procedure"])
    return m


def mut(fn):
    m = base()
    fn(m)
    return json.dumps(m, indent=2) + "\n"


def ring(m, name):
    return next(r for r in m["rings"] if r["name"] == name)


def fixtures():
    out = {}
    out["valid-example-manifest.json"] = (mut(lambda m: None), "example manifest as shipped")
    out["valid-no-window-task.json"] = (mut(lambda m: [r.pop("windowTask") for r in m["rings"]]),
                                        "windowTask is optional")
    neg = {
        "neg-canary-concurrency-percent": (lambda m: ring(m, "canary").update(maxConcurrency="10%"),
                                           "canary sized as a percentage"),
        "neg-canary-concurrency-5": (lambda m: ring(m, "canary").update(maxConcurrency="5"), "canary too wide"),
        "neg-canary-errors": (lambda m: ring(m, "canary").update(maxErrors="1"), "canary tolerates an error"),
        "neg-canary-gated": (lambda m: ring(m, "canary").update(gate={"requires": "wave1", "minSoakHours": 24,
                             "approvers": ["x"], "evidence": ["compliance-summary"]}), "canary has a gate"),
        "neg-missing-gate": (lambda m: ring(m, "wave1").update(gate=None), "wave1 ungated"),
        "neg-gate-wrong-order": (lambda m: ring(m, "wave2")["gate"].update(requires="canary"),
                                 "wave2 gated on canary instead of wave1"),
        "neg-no-approver": (lambda m: ring(m, "wave1")["gate"].update(approvers=[]), "gate without approvers"),
        "neg-short-soak": (lambda m: ring(m, "wave1")["gate"].update(minSoakHours=4), "gate soak below 24h"),
        "neg-gate-no-compliance-evidence": (lambda m: ring(m, "wave1")["gate"].update(evidence=["canary-signoff"]),
                                            "gate evidence missing compliance-summary"),
        "neg-no-presnapshot": (lambda m: ring(m, "wave1").update(preSnapshot=False), "install without snapshot"),
        "neg-unknown-patchgroup": (lambda m: ring(m, "wave2")["patchGroups"].append("wave3"),
                                   "ring targets a patch group no baseline owns"),
        "neg-duplicate-patchgroup": (lambda m: ring(m, "wave1")["patchGroups"].append("canary"),
                                     "same patch group in two rings"),
        "neg-ring-order-gap": (lambda m: ring(m, "wave2").update(order=5), "ring order not contiguous"),
        "neg-bad-operation": (lambda m: ring(m, "wave1").update(operation="InstallNow"), "unknown operation"),
        "neg-bad-reboot": (lambda m: ring(m, "wave1").update(rebootOption="Always"), "unknown reboot option"),
        "neg-task-rate-mismatch": (lambda m: ring(m, "wave1").update(maxConcurrency="50%"),
                                   "manifest rate disagrees with the CLI task"),
        "neg-gated-task-install": (lambda m: ring(m, "wave1").update(windowTask="../../ssm/cli/register-task.canary.json",
                                   maxConcurrency="1", maxErrors="0"), "gated ring points at an Install task"),
        "neg-baseline-no-delay": (lambda m: m["baselines"][0].update(source="baseline-no-delay.json"),
                                  "baseline auto-approves with no delay and RejectedPatchesAction ALLOW_AS_DEPENDENCY"),
        "neg-baseline-os-mismatch": (lambda m: m["baselines"][0].update(operatingSystem="UBUNTU"),
                                     "manifest OS differs from baseline file"),
        "neg-missing-baseline-file": (lambda m: m["baselines"][0].update(source="does-not-exist.json"),
                                      "baseline source missing"),
        "neg-rollback-unknown-strategy": (lambda m: m["rollback"].update(strategies=["hope"]), "unknown rollback"),
        "neg-rollback-no-procedure": (lambda m: m["rollback"].update(procedure="../../procedures/NOPE.md"),
                                      "rollback procedure missing"),
        "neg-rollback-too-slow": (lambda m: m["rollback"].update(maxRollbackMinutes=600), "rollback budget > 4h"),
        "neg-no-escalation-contacts": (lambda m: m["escalation"].update(contacts=[]), "no escalation contacts"),
        "neg-real-account-id": (lambda m: m.update(changeRecord="CHG-123456789012"), "12-digit account-like id"),
    }
    for name, (fn, why) in neg.items():
        out[name + ".json"] = (mut(fn), why)
    good = base()
    raw = json.dumps(good, indent=2)
    malformed = {
        "malformed-truncated": (raw[: len(raw) // 2], "truncated JSON"),
        "malformed-duplicate-key": (raw.replace('"schemaVersion": "1.0.0",',
                                                '"schemaVersion": "1.0.0",\n  "schemaVersion": "1.0.0",', 1),
                                    "duplicate key"),
        "malformed-not-object": ("[]\n", "top level is an array"),
        "malformed-nan": (raw.replace('"soakHours": 48', '"soakHours": NaN', 1), "NaN literal"),
        "malformed-unknown-top-key": (mut(lambda m: m.update(autoApproveEverything=True)), "unknown key"),
        "malformed-unknown-ring-key": (mut(lambda m: ring(m, "canary").update(skipCanary=True)), "unknown ring key"),
        "malformed-missing-rings": (mut(lambda m: m.pop("rings")), "required key missing"),
        "malformed-empty-rings": (mut(lambda m: m.update(rings=[])), "no rings"),
        "malformed-wrong-type": (mut(lambda m: ring(m, "canary").update(order="1")), "order is a string"),
        "malformed-bool-as-int": (mut(lambda m: ring(m, "canary").update(soakHours=True)), "bool where int expected"),
        "malformed-bad-percent": (mut(lambda m: ring(m, "wave1").update(maxConcurrency="ten%")), "rate not numeric"),
        "malformed-percent-over-100": (mut(lambda m: ring(m, "wave1").update(maxErrors="150%")), "rate > 100%"),
        "malformed-schema-version": (mut(lambda m: m.update(schemaVersion="2.0.0")), "unsupported schema"),
        "malformed-absolute-path": (mut(lambda m: m["baselines"][0].update(source="/etc/passwd")), "absolute path"),
        "malformed-baseline-truncated": (mut(lambda m: m["baselines"][0].update(source="baseline-truncated.json")),
                                         "referenced baseline is invalid JSON"),
    }
    for name, (text, why) in malformed.items():
        out[name + ".json"] = (text if text.endswith("\n") else text + "\n", why)
    # referenced helper files (not manifests)
    with open(os.path.join(HERE, "..", "ssm", "cli", "create-patch-baseline.al2023.json"), encoding="utf-8") as fh:
        bl = json.load(fh)
    nd = copy.deepcopy(bl)
    for r in nd["ApprovalRules"]["PatchRules"]:
        r.pop("ApproveAfterDays", None)
    nd["RejectedPatchesAction"] = "ALLOW_AS_DEPENDENCY"
    helpers = {"baseline-no-delay.json": json.dumps(nd, indent=2) + "\n",
               "baseline-truncated.json": json.dumps(bl, indent=2)[:200] + "\n"}
    return out, helpers


def expected(name):
    return {"valid-": 0, "neg-": 1, "malformed-": 2}[next(p for p in ("valid-", "neg-", "malformed-")
                                                          if name.startswith(p))]


def render():
    fx, helpers = fixtures()
    files = {n: t for n, (t, _) in fx.items()}
    files.update(helpers)
    index = {"generatedBy": "operations/patching/tests/make_fixtures.py",
             "fixtures": [{"file": n, "expectedExit": expected(n), "why": w} for n, (_, w) in sorted(fx.items())],
             "helpers": sorted(helpers)}
    files["INDEX.json"] = json.dumps(index, indent=2) + "\n"
    return files


def main():
    files = render()
    if "--check" in sys.argv:
        drift = []
        on_disk = set(os.listdir(FIX)) if os.path.isdir(FIX) else set()
        for n, t in files.items():
            p = os.path.join(FIX, n)
            if not os.path.isfile(p) or open(p, encoding="utf-8").read() != t:
                drift.append(n)
        drift += sorted(on_disk - set(files))
        print("fixture drift: %s" % (drift or "none"))
        return 1 if drift else 0
    os.makedirs(FIX, exist_ok=True)
    for n, t in files.items():
        with open(os.path.join(FIX, n), "w", encoding="utf-8") as fh:
            fh.write(t)
    print("wrote %d files to %s" % (len(files), os.path.relpath(FIX)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
