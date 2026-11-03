#!/usr/bin/env python3
"""Cross-registry consistency check (candidate-20261103b, owner directive t26u task 4).

Deterministic, offline, stdlib only. Reconciles three registries that were maintained separately:
  coordination/modules.json        module status, PRs, paths, limitations
  coordination/tasks.json          per-PR integration records (tasks[], related_prs[]) and user_actions[]
  docs/metadata/pages.json         one metadata entry per tracked Markdown file
  docs/metadata/preserved-records.json  sha256 of frozen historical records

Rules (each violation is one error line; exit 1 if any):
  R1  every tasks[]/related_prs[] PR maps to exactly one module listing it in prs[];
      its recorded status agrees with that module's status (integrated->INTEGRATED, superseded->SUPERSEDED),
      or the record carries reconciled{as_of, current_module, current_status, note} whose current_* match the
      module. The original status is never rewritten: it stays as history.
  R2  pages.json keys == tracked Markdown files (no missing entry, no orphan entry).
  R3  every preserved record exists, matches its sha256 and has a pages.json entry.
  R4  every Markdown file of the review-notes module is frozen in preserved-records and is lifecycle Archived.
  R5  every UA-n cited in modules.json exists in tasks.json user_actions, and every unresolved UA whose task_id is
      PR-<n> is cited by the module that lists PR n (a module may also cite UAs of other PRs, e.g. a superseded one).
"""
import hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS_MAP = {"integrated": "INTEGRATED", "superseded": "SUPERSEDED"}


def tracked_markdown(root):
    out = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root, text=True)
    return sorted({p for p in out.splitlines() if p.lower().endswith(".md") and (Path(root) / p).is_file()})


def _md_in(paths, files):
    return sorted(f for f in files for p in paths if f == p or f.startswith(p.rstrip("/") + "/"))


def check(modules, tasks, pages, preserved, md_files, root=ROOT):
    errs = []
    mods = modules["modules"]
    by_pr = {}
    for m in mods:
        for n in m.get("prs", []):
            by_pr.setdefault(n, []).append(m)
    # R1
    for kind in ("tasks", "related_prs"):
        for rec in tasks.get(kind, []):
            n, st = rec.get("pr"), rec.get("status")
            owners = by_pr.get(n, [])
            if len(owners) != 1:
                errs.append(f"R1 {kind} PR #{n}: listed by {len(owners)} modules (need exactly 1)")
                continue
            m = owners[0]
            if STATUS_MAP.get(st) == m["status"]:
                continue
            rc = rec.get("reconciled")
            if not isinstance(rc, dict) or not all(isinstance(rc.get(k), str) and rc[k] for k in ("as_of", "current_module", "current_status", "note")):
                errs.append(f"R1 {kind} PR #{n}: status {st!r} disagrees with module {m['id']} {m['status']} and no reconciled record")
            elif rc["current_module"] != m["id"] or rc["current_status"] != m["status"]:
                errs.append(f"R1 {kind} PR #{n}: reconciled says {rc['current_module']}/{rc['current_status']}, registry says {m['id']}/{m['status']}")
    # R2
    keys = set(pages)
    for f in sorted(set(md_files) - keys):
        errs.append(f"R2 missing pages.json entry: {f}")
    for f in sorted(keys - set(md_files)):
        errs.append(f"R2 orphan pages.json entry (no tracked file): {f}")
    # R3
    for f, digest in sorted(preserved.items()):
        p = Path(root) / f
        if not p.is_file():
            errs.append(f"R3 preserved record missing: {f}")
        elif hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            errs.append(f"R3 preserved record changed: {f}")
        if f not in pages:
            errs.append(f"R3 preserved record has no pages.json entry: {f}")
    # R4
    rn = [m for m in mods if m["id"] == "review-notes"]
    if rn:
        for f in _md_in(rn[0]["paths"], md_files):
            if f not in preserved:
                errs.append(f"R4 review record not frozen in preserved-records: {f}")
            if pages.get(f, {}).get("lifecycle_status") != "Archived":
                errs.append(f"R4 review record not lifecycle Archived: {f}")
    # R5
    uas = {u["id"]: u for u in tasks.get("user_actions", [])}
    cited = {}
    for m in mods:
        for u in sorted(set(re.findall(r"\bUA-\d+\b", json.dumps(m)))):
            cited.setdefault(u, []).append(m)
    for u, ms in sorted(cited.items()):
        if u not in uas:
            errs.append(f"R5 {', '.join(x['id'] for x in ms)} cite unknown {u}")
            continue
    for u, ua in sorted(uas.items()):
        t = re.match(r"PR-(\d+)", ua.get("task_id", ""))
        if not t or ua.get("status") == "RESOLVED":
            continue
        n = int(t.group(1))
        for m in by_pr.get(n, []):
            if m not in cited.get(u, []):
                errs.append(f"R5 {u} (task {ua['task_id']}, {ua.get('status')}) is not cited by module {m['id']}")
    return errs


def load(root=ROOT):
    j = lambda p: json.loads((Path(root) / p).read_text())
    return (j("coordination/modules.json"), j("coordination/tasks.json"), j("docs/metadata/pages.json"),
            j("docs/metadata/preserved-records.json"), tracked_markdown(root))


def main(argv=None):
    errs = check(*load(), root=ROOT)
    for e in errs:
        print("ERROR", e)
    print(f"REGISTRIES {'INVALID: %d error(s)' % len(errs) if errs else 'CONSISTENT'}: modules.json / tasks.json / pages.json / preserved-records.json")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
