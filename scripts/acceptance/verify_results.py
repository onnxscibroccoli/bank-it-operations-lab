#!/usr/bin/env python3
"""Independent verifier for an acceptance output directory (scripts/acceptance/run.sh --out DIR).

Re-derives every verdict from the per-check logs instead of trusting results.tsv:
  * SHA256SUMS covers every file (except postgres-run/, which has its own SHA256SUMS) and verifies;
  * each check row with a log has a matching '# exit_code: N' trailer;
  * a normal check is PASS iff exit 0; a defect-control (DEFECT-*) is PASS iff exit != 0 AND output matches its '# reason_regex:';
  * results.json agrees with results.tsv and its overall is recomputed:
      FAIL if any required FAIL (or no required checks), else UNKNOWN if any required UNKNOWN, else PASS.
  verify_results.py --selftest   proves the gate returns FAIL/UNKNOWN for synthetic bad result sets.
Exit 0 if consistent, 1 otherwise.
"""
import csv, hashlib, json, os, re, sys, tempfile

def gate(rows):
    req = [r for r in rows if r["required"] == "yes"]
    if not req or any(r["verdict"] == "FAIL" for r in req) or any(r["verdict"] not in ("PASS", "FAIL", "UNKNOWN", "INFO") for r in rows):
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
            else:
                want = "PASS" if rc == 0 else "FAIL"
            if r["verdict"] != want: errs.append(f"{r['check_id']}: verdict {r['verdict']} but exit {rc} implies {want}")
        elif r["verdict"] == "PASS" and r["check_id"] not in ("AWS-00",) and not r["check_id"].startswith("REPORT-"):
            errs.append(f"{r['check_id']}: PASS without a log")
    j = json.load(open(os.path.join(out, "results.json")))
    if [c["check_id"] for c in j["checks"]] != ids: errs.append("results.json checks != results.tsv")
    g = gate(rows)
    if j["overall"] != g: errs.append(f"results.json overall {j['overall']} != recomputed {g}")
    for e in errs: print("ERROR", e)
    print(f"verify_results: {'OK' if not errs else 'REJECTED'} overall={g} rows={len(rows)} errors={len(errs)}")
    return 0 if not errs else 1

def selftest():
    P = lambda i, v, req="yes": {"check_id": i, "required": req, "verdict": v}
    cases = [([P("a", "PASS")], "PASS"), ([P("a", "PASS"), P("b", "FAIL")], "FAIL"),
             ([P("a", "PASS"), P("b", "UNKNOWN")], "UNKNOWN"), ([P("a", "PASS"), P("b", "UNKNOWN", "no")], "PASS"),
             ([P("a", "UNKNOWN"), P("b", "FAIL")], "FAIL"), ([], "FAIL"), ([P("a", "SKIPPED")], "FAIL"),
             ([P("a", "PASS"), P("b", "FAIL", "no")], "PASS")]
    bad = [(c, w, gate(c)) for c, w in cases if gate(c) != w]
    for c, w, g in bad: print("SELFTEST FAIL", c, "want", w, "got", g)
    print(f"gate selftest: {len(cases) - len(bad)}/{len(cases)} ok")
    return 1 if bad else 0

if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]: sys.exit(selftest())
    if len(sys.argv) != 2: print(__doc__); sys.exit(64)
    sys.exit(verify(sys.argv[1]))
