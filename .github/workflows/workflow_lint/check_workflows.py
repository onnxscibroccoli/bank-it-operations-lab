#!/usr/bin/env python3
"""Workflow security checker (fails closed).

Usage: check_workflows.py [--workflows DIR] [--lock FILE] [--policy FILE] [--tsv OUT]

Rules (rule id -> what fails):
  PARSE            workflow file is not valid YAML / not a mapping
  UNPINNED         external `uses:` not pinned to a full 40-hex commit SHA (docker:// must use @sha256:)
  LOCK_MISSING     pinned SHA not present (or not verified) in ACTIONS_LOCK.tsv for that action
  LOCK_COMMENT     pin has no `# vX.Y.Z` comment, or the comment is not a tag the lockfile maps to that SHA
  PERMS_TOP        no top-level `permissions:`, or it is write-all / read-all / grants any write
  PERMS_JOB        job grants write-all, or a write scope not allow-listed in WORKFLOW_POLICY.json
  PERSIST_CREDS    actions/checkout step without `persist-credentials: false`
  PR_TARGET        `pull_request_target` trigger
  WORKFLOW_RUN     `workflow_run` trigger (untrusted artifacts / privileged context)
  INJECTION        ${{ github.event.* | github.head_ref | inputs.* }} interpolated into a `run:` script
  CURL_PIPE_SH     download piped straight into a shell (curl|bash, wget|sh, ...)
Exit 0 if no findings, 1 if any finding, 2 on usage error.
"""
import argparse, json, os, re, sys

try:
    import yaml
except ImportError:  # fail closed: never silently skip
    print("ERROR: PyYAML is required (pip install --require-hashes -r requirements.txt)", file=sys.stderr)
    sys.exit(2)

SHA40 = re.compile(r"^[0-9a-f]{40}$")
INJECT = re.compile(r"\$\{\{[^}]*\b(github\.event\.|github\.head_ref|inputs\.)[^}]*\}\}")
CURL_PIPE = re.compile(r"\b(curl|wget)\b[^\n|;]*\|\s*(sudo\s+)?(ba|z|da)?sh\b")
READ_VALUES = {"read", "none"}


class Loader(yaml.SafeLoader):
    pass


# YAML 1.1 turns the key `on` into True; keep it as the string "on".
Loader.yaml_implicit_resolvers = {k: [(t, r) for t, r in v if t != "tag:yaml.org,2002:bool"]
                                  for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}


def load_lock(path):
    lock = {}  # (action, sha) -> set(tags)
    if not os.path.exists(path):
        return lock
    with open(path) as f:
        header = None
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            cols = line.rstrip("\n").split("\t")
            if header is None:
                header = cols
                continue
            row = dict(zip(header, cols))
            if row.get("verified") != "yes":
                continue
            tags = {row["version"]} | {t for t in row.get("also_tags", "").split(",") if t and t != "-"}
            lock.setdefault((row["action"], row["sha"]), set()).update(tags)
    return lock


def uses_lines(text):
    """Map each `uses:` value to its trailing comment, by raw line (YAML drops comments)."""
    out = {}
    for n, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^\s*(?:-\s*)?uses:\s*['\"]?([^\s'\"#]+)['\"]?\s*(?:#\s*(\S+))?", line)
        if m:
            out.setdefault(m.group(1), []).append((n, m.group(2)))
    return out


def as_bool_false(v):
    return v is False or (isinstance(v, str) and v.strip().lower() == "false")


def check_file(path, lock, policy):
    findings = []
    rel = os.path.basename(path)
    text = open(path, encoding="utf-8").read()

    def add(rule, where, msg):
        findings.append((rel, rule, where, msg))

    try:
        doc = yaml.load(text, Loader=Loader)
    except yaml.YAMLError as e:
        add("PARSE", "-", str(e).splitlines()[0]); return findings
    if not isinstance(doc, dict):
        add("PARSE", "-", "not a mapping"); return findings

    comments = uses_lines(text)
    on = doc.get("on", {})
    events = [on] if isinstance(on, str) else (list(on) if isinstance(on, (list, dict)) else [])
    if "pull_request_target" in events:
        add("PR_TARGET", "on", "pull_request_target runs with a write token and secrets in the base context")
    if "workflow_run" in events:
        add("WORKFLOW_RUN", "on", "workflow_run consumes artifacts/results from untrusted runs in a privileged context")

    top = doc.get("permissions", "__missing__")
    if top == "__missing__":
        add("PERMS_TOP", "permissions", "missing top-level permissions (token defaults may be write)")
    elif isinstance(top, str):
        add("PERMS_TOP", "permissions", f"top-level permissions: {top} (use {{}} or explicit read scopes)")
    elif isinstance(top, dict):
        for k, v in top.items():
            if str(v) not in READ_VALUES:
                add("PERMS_TOP", f"permissions.{k}", f"top-level grants {k}: {v}; grant writes per job only")
    elif top is not None:
        add("PERMS_TOP", "permissions", f"unexpected value {top!r}")

    for jid, job in (doc.get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue
        jp = job.get("permissions")
        allowed = set(policy.get("job_write_allowlist", {}).get(f"{rel}:{jid}", []))
        if isinstance(jp, str):
            if jp == "write-all":
                add("PERMS_JOB", f"jobs.{jid}.permissions", "write-all")
            elif jp == "read-all":
                add("PERMS_JOB", f"jobs.{jid}.permissions", "read-all is broader than needed; list scopes")
        elif isinstance(jp, dict):
            for k, v in jp.items():
                if str(v) == "write" and k not in allowed:
                    add("PERMS_JOB", f"jobs.{jid}.permissions.{k}", f"write scope {k} not in WORKFLOW_POLICY.json allowlist")
        juses = job.get("uses")
        steps = list(job.get("steps") or [])
        refs = [(f"jobs.{jid}.uses", juses, None)] if juses else []
        for i, st in enumerate(steps):
            if isinstance(st, dict) and st.get("uses"):
                refs.append((f"jobs.{jid}.steps[{i}]", st["uses"], st))
            if isinstance(st, dict) and isinstance(st.get("run"), str):
                run = st["run"]
                for m in INJECT.finditer(run):
                    add("INJECTION", f"jobs.{jid}.steps[{i}].run", f"{m.group(0)} interpolated into a script; pass via env:")
                if CURL_PIPE.search(run):
                    add("CURL_PIPE_SH", f"jobs.{jid}.steps[{i}].run", "download piped into a shell")
        for where, ref, st in refs:
            ref = str(ref)
            if ref.startswith("./"):
                continue
            if ref.startswith("docker://"):
                if "@sha256:" not in ref:
                    add("UNPINNED", where, f"{ref} (docker image not pinned by digest)")
                continue
            name, _, ver = ref.partition("@")
            action = "/".join(name.split("/")[:2])
            if not SHA40.match(ver):
                add("UNPINNED", where, f"{ref} is not a full commit SHA")
            else:
                tags = lock.get((action, ver))
                if tags is None:
                    add("LOCK_MISSING", where, f"{action}@{ver} not verified in ACTIONS_LOCK.tsv")
                cms = [c for _, c in comments.get(ref, [])]
                if not cms or any(c is None for c in cms):
                    add("LOCK_COMMENT", where, f"{ref} has no '# vX.Y.Z' version comment")
                elif tags is not None and any(c not in tags for c in cms):
                    add("LOCK_COMMENT", where, f"comment {sorted(set(cms))} not a tag of {ver[:12]} (lock: {sorted(tags)})")
            if st is not None and action == "actions/checkout":
                w = st.get("with") or {}
                if not as_bool_false(w.get("persist-credentials", True)):
                    add("PERSIST_CREDS", where, "actions/checkout without persist-credentials: false")
    return findings


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "../../.."))
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflows", default=os.path.join(root, ".github/workflows"))
    ap.add_argument("--lock", default=os.path.join(root, ".github/workflows/ACTIONS_LOCK.tsv"))
    ap.add_argument("--policy", default=os.path.join(root, ".github/workflows/WORKFLOW_POLICY.json"))
    ap.add_argument("--tsv")
    a = ap.parse_args()
    lock = load_lock(a.lock)
    policy = json.load(open(a.policy)) if os.path.exists(a.policy) else {}
    files = sorted(os.path.join(a.workflows, f) for f in os.listdir(a.workflows) if f.endswith((".yml", ".yaml")))
    if not files:
        print("ERROR: no workflow files found", file=sys.stderr); return 2
    allf = []
    for p in files:
        allf += check_file(p, lock, policy)
    lines = ["file\trule\tlocation\tdetail"] + ["\t".join(f) for f in allf]
    if a.tsv:
        open(a.tsv, "w").write("\n".join(lines) + "\n")
    for f in allf:
        print("FINDING", *f, sep="  ")
    print(f"checked {len(files)} workflow files, {len(lock)} verified lock entries: "
          + (f"{len(allf)} findings -> FAIL" if allf else "0 findings -> PASS"))
    return 1 if allf else 0


if __name__ == "__main__":
    sys.exit(main())
