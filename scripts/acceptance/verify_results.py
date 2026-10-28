#!/usr/bin/env python3
"""Independent verifier for an acceptance output directory (scripts/acceptance/run.sh --out DIR).

Re-derives every verdict from the per-check logs instead of trusting results.tsv:
  * SHA256SUMS covers every file (except postgres-run/, which has its own SHA256SUMS) and verifies;
  * each check row with a log has a matching '# exit_code: N' trailer;
  * a normal check is PASS iff exit 0; a defect-control (DEFECT-*) is PASS iff exit != 0 AND output matches its '# reason_regex:';
  * results.json agrees with results.tsv and its overall is recomputed:
      FAIL if any required FAIL (or no required checks), else UNKNOWN if any required UNKNOWN, else PASS.
  * every always-emitted required check is present (a silently skipped check cannot vanish from the gate);
  * the run is bound to one commit: results.json target_sha is 40-hex and CHECKOUT / SOURCE-BINDING name it.
  verify_results.py --selftest            gate tests incl. exhaustive invariant I1 enumeration.
  verify_results.py DIR --accept-for SHA  acceptance predicate: 0 only if DIR is consistent, overall PASS,
                                          bound to exactly SHA, and not a defect-injection run (invariant I1+I2).
Exit 0 if consistent (or accepted), 1 if inconsistent, 3 if consistent but NOT accepted for SHA.
"""
import csv, hashlib, itertools, json, os, re, sys

# Checks run.sh records on every run whose CHECKOUT succeeded (as PASS, FAIL or UNKNOWN). Absence = REJECTED.
ALWAYS_EMITTED = ("AWS-00", "AWS-01", "PG-01", "ENTRA-01", "ACC-A-01", "ACC-B-01", "ACC-C-01",
                  "HASH-1", "DEFECT-HASH", "SOURCE-BINDING")

def gate(rows):
    req = [r for r in rows if r["required"] == "yes"]
    # A required row may only be PASS/FAIL/UNKNOWN; INFO is advisory-only (a required INFO used to count as passing).
    if (not req or any(r["verdict"] == "FAIL" for r in req) or any(r["verdict"] not in ("PASS", "FAIL", "UNKNOWN") for r in req)
            or any(r["verdict"] not in ("PASS", "FAIL", "UNKNOWN", "INFO") for r in rows)):
        return "FAIL"
    return "UNKNOWN" if any(r["verdict"] == "UNKNOWN" for r in req) else "PASS"

def verify(out):
    errs = []
    sums = os.path.join(out, "SHA256SUMS")
    listed = set()
    for n, line in enumerate(open(sums).read().splitlines(), 1):
        m = re.match(r"^([0-9a-f]{64}) [ *](.+)$", line)
        if not m: errs.append(f"SHA256SUMS:{n} malformed"); continue
        p = os.path.join(out, m.group(2)); listed.add(os.path.normpath(m.group(2)))
        if not os.path.isfile(p): errs.append(f"missing {m.group(2)}"); continue
        if hashlib.sha256(open(p, "rb").read()).hexdigest() != m.group(1): errs.append(f"hash mismatch {m.group(2)}")
    for root, _, files in os.walk(out):
        for f in files:
            rel = os.path.normpath(os.path.relpath(os.path.join(root, f), out))
            if rel != "SHA256SUMS" and not rel.startswith("postgres-run" + os.sep) and rel not in listed:
                errs.append(f"uncovered file {rel}")
    rows = list(csv.DictReader(open(os.path.join(out, "results.tsv")), delimiter="\t"))
    ids = [r["check_id"] for r in rows]
    if len(ids) != len(set(ids)): errs.append("duplicate check ids")
    for r in rows:
        if r["log"] and r["log"] != "-":
            t = open(os.path.join(out, r["log"]), errors="replace").read()
            m = re.findall(r"^# exit_code: (-?\d+)$", t, re.M)
            if not m or m[-1] != r["exit_code"]: errs.append(f"{r['check_id']}: log trailer {m[-1:] } != tsv exit {r['exit_code']}"); continue
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
        elif r["verdict"] == "PASS" and r["check_id"] not in ("AWS-00",) and not r["check_id"].startswith("REPORT-"):
            errs.append(f"{r['check_id']}: PASS without a log")
    j = json.load(open(os.path.join(out, "results.json")))
    if [c["check_id"] for c in j["checks"]] != ids: errs.append("results.json checks != results.tsv")
    by = {r["check_id"]: r for r in rows}
    sha = j.get("target_sha", "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha or ""): errs.append(f"results.json target_sha {sha!r} is not a full 40-hex SHA")
    if "CHECKOUT" not in by: errs.append("CHECKOUT row missing")
    elif by["CHECKOUT"]["required"] != "yes" or sha not in by["CHECKOUT"]["detail"]:
        errs.append("CHECKOUT row is not required or does not name target_sha")
    elif by["CHECKOUT"]["verdict"] == "PASS":
        for i in ALWAYS_EMITTED:
            if i not in by: errs.append(f"required check {i} missing from results (silently skipped?)")
            elif by[i]["required"] != "yes": errs.append(f"check {i} must be required")
        sb = by.get("SOURCE-BINDING")
        if sb and sb["verdict"] == "PASS" and sha not in sb["detail"]: errs.append("SOURCE-BINDING PASS does not name target_sha")
    g = gate(rows)
    if j["overall"] != g: errs.append(f"results.json overall {j['overall']} != recomputed {g}")
    for e in errs: print("ERROR", e)
    print(f"verify_results: {'OK' if not errs else 'REJECTED'} overall={g} rows={len(rows)} errors={len(errs)}")
    return (0 if not errs else 1), j

def accept_for(out, sha):
    """Acceptance predicate. ACCEPTED(out, sha) <=> consistent(out) and overall==PASS and target_sha==sha and no defect injected."""
    rc, j = verify(out)
    if rc != 0: print(f"accept-for: REJECTED (inconsistent output) for {sha}"); return 1
    why = []
    if j["overall"] != "PASS": why.append(f"overall={j['overall']}")
    if j["target_sha"] != sha: why.append(f"bound to {j['target_sha']}, not {sha}")
    if j.get("injected_defect"): why.append(f"defect-injection run ({j['injected_defect']})")
    print(f"accept-for: {'ACCEPTED' if not why else 'NOT ACCEPTED: ' + '; '.join(why)} for {sha}")
    return 0 if not why else 3

def selftest():
    P = lambda i, v, req="yes": {"check_id": i, "required": req, "verdict": v}
    cases = [([P("a", "PASS")], "PASS"), ([P("a", "PASS"), P("b", "FAIL")], "FAIL"),
             ([P("a", "PASS"), P("b", "UNKNOWN")], "UNKNOWN"), ([P("a", "PASS"), P("b", "UNKNOWN", "no")], "PASS"),
             ([P("a", "UNKNOWN"), P("b", "FAIL")], "FAIL"), ([], "FAIL"), ([P("a", "SKIPPED")], "FAIL"),
             ([P("a", "PASS"), P("b", "FAIL", "no")], "PASS"), ([P("a", "INFO")], "FAIL"),
             ([P("a", "PASS"), P("b", "INFO")], "FAIL"), ([P("a", "PASS"), P("b", "INFO", "no")], "PASS")]
    bad = [(c, w, gate(c)) for c, w in cases if gate(c) != w]
    for c, w, g in bad: print("SELFTEST FAIL", c, "want", w, "got", g)
    print(f"gate selftest: {len(cases) - len(bad)}/{len(cases)} ok")
    # I1, exhaustive over every result set of length 0..4 drawn from {PASS,FAIL,UNKNOWN,INFO,SKIPPED} x {yes,no}:
    # gate == PASS  =>  at least one required row, every required row PASS, every verdict in the known set.
    cells = list(itertools.product(("PASS", "FAIL", "UNKNOWN", "INFO", "SKIPPED"), ("yes", "no")))
    n = viol = 0
    for k in range(5):
        for combo in itertools.product(cells, repeat=k):
            rows = [P(f"c{i}", v, q) for i, (v, q) in enumerate(combo)]; n += 1
            req = [r for r in rows if r["required"] == "yes"]
            ok = bool(req) and all(r["verdict"] == "PASS" for r in req) and all(r["verdict"] in ("PASS", "FAIL", "UNKNOWN", "INFO") for r in rows)
            if (gate(rows) == "PASS") != ok: viol += 1; print("I1 VIOLATION", rows, gate(rows))
            if any(r["verdict"] in ("FAIL", "UNKNOWN") for r in req) and gate(rows) == "PASS": viol += 1
    print(f"I1 exhaustive: {n} result sets, {viol} violations")
    return 1 if (bad or viol) else 0

if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]: sys.exit(selftest())
    if len(a) == 3 and a[1] == "--accept-for": sys.exit(accept_for(a[0], a[2]))
    if len(a) != 1: print(__doc__); sys.exit(64)
    sys.exit(verify(a[0])[0])
