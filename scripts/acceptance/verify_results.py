#!/usr/bin/env python3
"""Independent verifier for an acceptance output directory (scripts/acceptance/run.sh --out DIR).

Re-derives every verdict instead of trusting results.tsv / results.json:
  * SHA256SUMS covers every file (except postgres-run/, which has its own SHA256SUMS) and verifies;
  * C3: results.tsv and results.json carry IDENTICAL complete records (all six fields, typed), and every
    summary counter in results.json is recomputed;
  * each check row with a log has a matching '# exit_code: N' trailer; a normal check is PASS iff exit 0;
    a defect-control (DEFECT-*) is PASS iff exit != 0 AND output matches its '# reason_regex:';
  * C1: the rows match the reviewed, versioned inventory scripts/acceptance/required-checks.v1.json exactly:
    no missing, duplicate, unknown/arbitrary or downgraded (required=no) check; dynamic groups contiguous and
    >= min; the inventory sha256 recorded in results.json equals this copy (and, with --sha and git, the copy
    at the tested commit);
  * C2: overall is recomputed by gate(): PASS only if every required row is PASS. INFO is advisory-only.
  * the run is bound to one commit: target_sha is 40-hex and CHECKOUT / SOURCE-BINDING name it.

  verify_results.py DIR [--sha SHA]           consistency (+ binding to SHA)         exit 0 / 1
  verify_results.py DIR --execution-pass-for SHA   EXECUTION_PASS bound to SHA         exit 0 / 1 / 3
  verify_results.py DIR --accept-for SHA       final decision via decide.py: 0 ONLY if ACCEPTED (C4); an
                                               execution pass awaiting independent review exits 5 (REVIEW_PENDING)
  verify_results.py --selftest                 gate tests incl. exhaustive invariant I1 enumeration
"""
import csv, hashlib, itertools, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
INVENTORY = os.path.join(HERE, "required-checks.v1.json")
INVENTORY_REL = "scripts/acceptance/required-checks.v1.json"
FIELDS = ["check_id", "required", "verdict", "exit_code", "detail", "log"]
VERDICTS = ("PASS", "FAIL", "UNKNOWN", "INFO")
DEFECTS = (None, "entra-mfa-report-only")


def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_inventory(path=INVENTORY):
    return json.load(open(path))


def gate(rows):
    """FAIL if no required row, any required FAIL, any required verdict other than PASS/FAIL/UNKNOWN (e.g. INFO),
    or any unknown verdict; else UNKNOWN if any required UNKNOWN; else PASS. The single gate implementation
    (run.sh imports it)."""
    req = [r for r in rows if r.get("required") == "yes"]
    if any(r.get("required") not in ("yes", "no") for r in rows):
        return "FAIL"
    if (not req or any(r["verdict"] == "FAIL" for r in req)
            or any(r["verdict"] not in ("PASS", "FAIL", "UNKNOWN") for r in req)
            or any(r["verdict"] not in VERDICTS for r in rows)):
        return "FAIL"
    return "UNKNOWN" if any(r["verdict"] == "UNKNOWN" for r in req) else "PASS"


def inventory_errors(rows, inv):
    """C1: exact coverage of the reviewed inventory."""
    errs = []
    fixed = {c["id"]: c for c in inv["checks"]}
    adv = {a["id"]: a for a in inv["advisory"]}
    groups = [(g, re.compile(g["pattern"])) for g in inv["groups"]]
    seen, members = {}, {g["name"]: [] for g in inv["groups"]}
    for r in rows:
        i = r["check_id"]
        seen[i] = seen.get(i, 0) + 1
        if i in fixed:
            if r["required"] != "yes": errs.append(f"C1: {i} is required by inventory v{inv['version']} but recorded required={r['required']} (downgrade)")
            if r["verdict"] not in ("PASS", "FAIL", "UNKNOWN"): errs.append(f"C1/C2: required {i} has verdict {r['verdict']}")
            continue
        if i in adv:
            if r["required"] != "no": errs.append(f"C1: advisory {i} must be required=no")
            if r["verdict"] == "INFO" and not adv[i]["allow_info"]: errs.append(f"C2: {i} may not be INFO")
            continue
        for g, rx in groups:
            m = rx.match(i)
            if m:
                members[g["name"]].append(int(m.group(1)))
                if r["required"] != "yes": errs.append(f"C1: group {g['name']} member {i} downgraded to required={r['required']}")
                if r["verdict"] not in ("PASS", "FAIL", "UNKNOWN"): errs.append(f"C1/C2: required {i} has verdict {r['verdict']}")
                break
        else:
            errs.append(f"C1: {i} is not in inventory v{inv['version']} (arbitrary/unreviewed check)")
    for i, n in seen.items():
        if n > 1: errs.append(f"C1: {i} appears {n} times (duplicate)")
    for i in fixed:
        if i not in seen: errs.append(f"C1: required check {i} missing (omitted)")
    for g in inv["groups"]:
        ns = sorted(members[g["name"]])
        if len(ns) < g["min"]: errs.append(f"C1: group {g['name']} has {len(ns)} members, inventory requires >= {g['min']}")
        if ns != list(range(1, len(ns) + 1)): errs.append(f"C1: group {g['name']} members not contiguous 1..n: {ns}")
    return errs


def counters(rows):
    req = [r for r in rows if r["required"] == "yes"]
    return {"required": len(req), "pass": sum(r["verdict"] == "PASS" for r in req),
            "fail": [r["check_id"] for r in req if r["verdict"] == "FAIL"],
            "unknown": [r["check_id"] for r in req if r["verdict"] == "UNKNOWN"]}


def git_show_sha256(sha, rel):
    try:
        r = subprocess.run(["git", "-C", HERE, "show", f"{sha}:{rel}"], capture_output=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def verify(out, expect_sha=None, inventory_path=INVENTORY, quiet=False):
    errs = []
    inv = load_inventory(inventory_path)
    sums = os.path.join(out, "SHA256SUMS")
    listed = set()
    for n, line in enumerate(open(sums).read().splitlines(), 1):
        m = re.match(r"^([0-9a-f]{64}) [ *](.+)$", line)
        if not m: errs.append(f"SHA256SUMS:{n} malformed"); continue
        p = os.path.join(out, m.group(2)); listed.add(os.path.normpath(m.group(2)))
        if not os.path.isfile(p): errs.append(f"missing {m.group(2)}"); continue
        if sha256_file(p) != m.group(1): errs.append(f"hash mismatch {m.group(2)}")
    for root, _, files in os.walk(out):
        for f in files:
            rel = os.path.normpath(os.path.relpath(os.path.join(root, f), out))
            if rel != "SHA256SUMS" and not rel.startswith("postgres-run" + os.sep) and rel not in listed:
                errs.append(f"uncovered file {rel}")
    with open(os.path.join(out, "results.tsv")) as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        if rd.fieldnames != FIELDS: errs.append(f"C3: results.tsv header {rd.fieldnames} != {FIELDS}")
        rows = [dict(r) for r in rd]
    for r in rows:
        if None in r or any(v is None for v in r.values()): errs.append(f"C3: malformed TSV row {r.get('check_id')}")
    rows = [{k: (r.get(k) or "") for k in FIELDS} for r in rows]
    j = json.load(open(os.path.join(out, "results.json")))
    # C3: complete records, typed, identical in both representations
    jrows = j.get("checks")
    if not isinstance(jrows, list) or any(not isinstance(c, dict) or set(c) != set(FIELDS) or any(not isinstance(c[k], str) for k in FIELDS) for c in jrows):
        errs.append("C3: results.json checks must be a list of records with exactly the six string fields"); jrows = []
    if [{k: c[k] for k in FIELDS} for c in jrows] != rows:
        diff = [r["check_id"] for r, c in itertools.zip_longest(rows, jrows, fillvalue={}) if r != {k: c.get(k) for k in FIELDS}]
        errs.append(f"C3: results.json records differ from results.tsv at {diff[:5]}")
    for r in rows:
        if r["required"] not in ("yes", "no"): errs.append(f"C3: {r['check_id']}: required={r['required']!r}")
        if r["verdict"] not in VERDICTS: errs.append(f"C3: {r['check_id']}: verdict={r['verdict']!r}")
        if not re.fullmatch(r"-|-?\d+", r["exit_code"]): errs.append(f"C3: {r['check_id']}: exit_code={r['exit_code']!r}")
        if r["verdict"] in ("PASS", "FAIL") and r["required"] == "yes" and r["log"] in ("", "-"):
            errs.append(f"C3: required {r['check_id']} is {r['verdict']} without a log")
        if r["verdict"] == "UNKNOWN" and r["exit_code"] not in ("-", "4", "126", "127") and not r["check_id"].startswith("DEFECT-"):
            errs.append(f"C3: {r['check_id']}: UNKNOWN with exit {r['exit_code']}")
    ids = [r["check_id"] for r in rows]
    if len(ids) != len(set(ids)): errs.append("duplicate check ids")
    for r in rows:
        if r["log"] and r["log"] != "-":
            lp = os.path.join(out, r["log"])
            if not os.path.isfile(lp): errs.append(f"{r['check_id']}: log {r['log']} missing"); continue
            t = open(lp, errors="replace").read()
            m = re.findall(r"^# exit_code: (-?\d+)$", t, re.M)
            if not m or m[-1] != r["exit_code"]: errs.append(f"{r['check_id']}: log trailer {m[-1:]} != tsv exit {r['exit_code']}"); continue
            rc = int(r["exit_code"])
            if r["check_id"].startswith("DEFECT-"):
                rx = re.search(r"^# reason_regex: (.*)$", t, re.M)
                body = "\n".join(l for l in t.splitlines() if not l.startswith("# "))
                want = "FAIL" if rc == 0 else ("PASS" if rx and re.search(rx.group(1), body) else "UNKNOWN")
            elif r["check_id"] == "ACC-C-03":
                want = {0: "PASS", 4: "UNKNOWN"}.get(rc, "FAIL")
            else:
                want = "PASS" if rc == 0 else "FAIL"
            if r["verdict"] != want: errs.append(f"{r['check_id']}: verdict {r['verdict']} but exit {rc} implies {want}")
    # C1: inventory coverage + inventory identity
    errs += inventory_errors(rows, inv)
    inv_sha = sha256_file(inventory_path)
    if j.get("inventory_version") != inv["version"] or j.get("inventory_sha256") != inv_sha:
        errs.append(f"C1: results.json inventory {j.get('inventory_version')}/{j.get('inventory_sha256')} != reviewed {inv['version']}/{inv_sha}")
    # binding
    by = {r["check_id"]: r for r in rows}
    sha = j.get("target_sha", "")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha): errs.append(f"results.json target_sha {sha!r} is not a full 40-hex SHA"); sha = "?" * 40
    if expect_sha is not None and sha != expect_sha: errs.append(f"binding: results are for {sha}, expected {expect_sha}")
    if "CHECKOUT" in by and sha not in by["CHECKOUT"]["detail"]: errs.append("CHECKOUT row does not name target_sha")
    sb = by.get("SOURCE-BINDING")
    if sb and sb["verdict"] == "PASS" and sha not in sb["detail"]: errs.append("SOURCE-BINDING PASS does not name target_sha")
    if expect_sha is not None:
        at = git_show_sha256(expect_sha, INVENTORY_REL)
        if at is not None and at != inv_sha: errs.append(f"C1: inventory at {expect_sha} has sha256 {at}, verifier copy {inv_sha}")
    if j.get("injected_defect") not in DEFECTS: errs.append(f"C3: unknown injected_defect {j.get('injected_defect')!r}")
    # C2/C3: overall + counters recomputed
    g = gate(rows)
    if j.get("overall") != g: errs.append(f"results.json overall {j.get('overall')} != recomputed {g}")
    for k, v in counters(rows).items():
        if j.get(k) != v: errs.append(f"C3: results.json {k}={j.get(k)!r} != recomputed {v!r}")
    if not quiet:
        for e in errs: print("ERROR", e)
        print(f"verify_results: {'OK' if not errs else 'REJECTED'} overall={g} rows={len(rows)} errors={len(errs)}")
    return (0 if not errs else 1), j


def execution_pass_for(out, sha):
    """EXECUTION_PASS(out, sha): consistent, overall PASS, bound to sha, no injected defect. NOT acceptance (C4)."""
    rc, j = verify(out, expect_sha=sha)
    if rc != 0: print(f"execution-pass-for: REJECTED (inconsistent or unbound output) for {sha}"); return 1
    why = []
    if j["overall"] != "PASS": why.append(f"overall={j['overall']}")
    if j.get("injected_defect"): why.append(f"defect-injection run ({j['injected_defect']})")
    print(f"execution-pass-for: {'EXECUTION_PASS (not ACCEPTED: independent review is separate)' if not why else 'NOT EXECUTION_PASS: ' + '; '.join(why)} for {sha}")
    return 0 if not why else 3


def selftest():
    P = lambda i, v, req="yes": {"check_id": i, "required": req, "verdict": v}
    cases = [([P("a", "PASS")], "PASS"), ([P("a", "PASS"), P("b", "FAIL")], "FAIL"),
             ([P("a", "PASS"), P("b", "UNKNOWN")], "UNKNOWN"), ([P("a", "PASS"), P("b", "UNKNOWN", "no")], "PASS"),
             ([P("a", "UNKNOWN"), P("b", "FAIL")], "FAIL"), ([], "FAIL"), ([P("a", "SKIPPED")], "FAIL"),
             ([P("a", "PASS"), P("b", "FAIL", "no")], "PASS"), ([P("a", "INFO")], "FAIL"),
             ([P("a", "PASS"), P("b", "INFO")], "FAIL"), ([P("a", "PASS"), P("b", "INFO", "no")], "PASS"),
             ([P("a", "PASS", "maybe")], "FAIL")]
    bad = [(c, w, gate(c)) for c, w in cases if gate(c) != w]
    for c, w, g in bad: print("SELFTEST FAIL", c, "want", w, "got", g)
    print(f"gate selftest: {len(cases) - len(bad)}/{len(cases)} ok")
    cells = list(itertools.product(("PASS", "FAIL", "UNKNOWN", "INFO", "SKIPPED"), ("yes", "no")))
    n = viol = 0
    for k in range(5):
        for combo in itertools.product(cells, repeat=k):
            rows = [P(f"c{i}", v, q) for i, (v, q) in enumerate(combo)]; n += 1
            req = [r for r in rows if r["required"] == "yes"]
            ok = bool(req) and all(r["verdict"] == "PASS" for r in req) and all(r["verdict"] in VERDICTS for r in rows)
            if (gate(rows) == "PASS") != ok: viol += 1; print("I1 VIOLATION", rows, gate(rows))
    print(f"I1 exhaustive: {n} result sets, {viol} violations")
    return 1 if (bad or viol) else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]: sys.exit(selftest())
    if len(a) == 1: sys.exit(verify(a[0])[0])
    if len(a) == 3 and a[1] == "--sha": sys.exit(verify(a[0], expect_sha=a[2])[0])
    if len(a) == 3 and a[1] == "--execution-pass-for": sys.exit(execution_pass_for(a[0], a[2]))
    if len(a) >= 3 and a[1] == "--accept-for":
        sys.exit(subprocess.run([sys.executable, os.path.join(HERE, "decide.py"), a[0], "--sha", a[2], *a[3:]]).returncode)
    print(__doc__); sys.exit(64)
