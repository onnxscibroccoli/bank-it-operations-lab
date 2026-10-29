#!/usr/bin/env python3
"""R6 hardening (PR #30/#31): the candidate must not be able to weaken the verifier. Stdlib only.

The gate manifest (gate-manifest.json) is read from a TRUSTED location, never from the candidate: from main
(.github/acceptance/gate-manifest.json) when main carries one, else from the evidence/acceptance branch
(trusted-gate/gate-manifest.json). It records:
  gate_sha   the commit whose scripts/ci and .github/acceptance/trusted-config.json are executed/read by the gate;
  files      {path: sha256} for every verifier file (scripts/ci/**, the trusted config) and for
             .github/workflows/integration-gate.yml.
Checks (any failure -> exit 1, AC3 cannot be met in that run):
  1. the trusted gate checkout is exactly gate_sha;
  2. every verifier file in the trusted checkout hashes to the manifest value, and scripts/ci has no extra file;
  3. the CANDIDATE's copies of all manifest files hash to the manifest value, and the candidate's scripts/ci has no
     extra file: a candidate that modifies integration-gate.yml, scripts/ci or the trusted config without a matching
     trusted manifest update is rejected.
Residual: the job that runs this check is defined in the candidate's workflow file. A candidate could delete the step;
only UA-3 (branch protection / ruleset on main requiring the gate, with the gate run from main) closes that fully.
Usage: verify_trusted_gate.py --manifest FILE --gate-dir DIR --candidate-dir DIR --gate-head SHA [--out FILE]
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
GATE_SIDE = ("scripts/ci/",  ".github/acceptance/trusted-config.json")


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def listing(root, sub="scripts/ci"):
    base = Path(root) / sub
    return sorted(str(p.relative_to(root)) for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts) if base.is_dir() else []


def build(gate_dir, workflow_file, gate_sha):
    files = {f: sha256(Path(gate_dir) / f) for f in listing(gate_dir)}
    files[".github/acceptance/trusted-config.json"] = sha256(Path(gate_dir) / ".github/acceptance/trusted-config.json")
    files[".github/workflows/integration-gate.yml"] = sha256(workflow_file)
    return {"schema": "bank-lab/gate-manifest/v1", "gate_sha": gate_sha, "files": dict(sorted(files.items()))}


def verify(man, gate_dir, cand_dir, gate_head):
    errs = []
    gs = (man or {}).get("gate_sha") or ""
    if not HEX40.match(gs):
        return ["manifest gate_sha missing or not 40-hex"]
    if (gate_head or "").strip().lower() != gs:
        errs.append(f"trusted gate checkout is {gate_head}, manifest pins {gs}")
    files = (man or {}).get("files") or {}
    if not files or ".github/workflows/integration-gate.yml" not in files or not any(f.startswith("scripts/ci/") for f in files):
        errs.append("manifest must list scripts/ci/** and .github/workflows/integration-gate.yml")
    man_ci = sorted(f for f in files if f.startswith("scripts/ci/"))
    for side, root in (("trusted gate", gate_dir), ("candidate", cand_dir)):
        for f, h in files.items():
            if side == "trusted gate" and not f.startswith(GATE_SIDE):
                continue
            p = Path(root) / f
            if not p.is_file():
                errs.append(f"{side}: {f} missing")
            elif sha256(p) != h:
                errs.append(f"{side}: {f} differs from the trusted manifest" + (" (candidate modifies the verifier without a matching trusted update)" if side == "candidate" else ""))
        extra = sorted(set(listing(root)) - set(man_ci))
        if extra:
            errs.append(f"{side}: files in scripts/ci not in the trusted manifest: {', '.join(extra)}")
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--gate-dir")
    ap.add_argument("--candidate-dir")
    ap.add_argument("--gate-head")
    ap.add_argument("--out")
    ap.add_argument("--build", action="store_true", help="write a manifest (--gate-dir, --workflow, --gate-head) to --out")
    ap.add_argument("--workflow")
    a = ap.parse_args(argv)
    if a.build:
        m = build(a.gate_dir, a.workflow, a.gate_head)
        Path(a.out).write_text(json.dumps(m, indent=1) + "\n")
        print(f"manifest: gate_sha {a.gate_head}, {len(m['files'])} files"); return 0
    try:
        man = json.loads(Path(a.manifest).read_text())
    except (OSError, ValueError, TypeError) as e:
        man, errs = None, [f"trusted manifest unreadable: {e}"]
    else:
        errs = verify(man, a.gate_dir, a.candidate_dir, a.gate_head)
    if a.out:
        Path(a.out).write_text(json.dumps({"schema": "bank-lab/gate-verification/v1", "manifest_gate_sha": (man or {}).get("gate_sha"),
                                           "gate_head": a.gate_head, "ok": not errs, "errors": errs}, indent=2) + "\n")
    for e in errs:
        print("ERROR " + e)
    print("TRUSTED GATE " + ("VERIFIED: verifier code, trusted config and workflow match the trusted manifest" if not errs else f"REJECTED: {len(errs)} error(s)"))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
