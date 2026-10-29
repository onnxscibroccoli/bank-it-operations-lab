#!/usr/bin/env python3
"""SIMULATION incident run requirements (PR #22 module). Usage: check_incident_run.py RUN_DIR [--json-out F] [--summary F]

Evaluates six requirements for ONE run directory and prints one line per requirement:
  injection   failure_injected event + every inject_* step PASS
  detection   detected event after injection, metrics.mttd_s > 0
  diagnosis   diagnosed event + at least one diag_* step, all PASS
  recovery    restore_started, db_restarted, data_integrity_verified, service_restored events + every restore_*/verify_* step PASS
  timeline    TIMELINE.md present and scenarios/incident/lib/timeline.py --verify exits 0
  simulation  every event, SUMMARY.json, TIMELINE.md and the directory label SIMULATION.md carry the SIMULATION marker
Status per requirement: PASS, FAIL or NOT_EXECUTED. A run whose SUMMARY.json says NOT_EXECUTED (for example no
PostgreSQL binaries) makes EVERY requirement NOT_EXECUTED; that is never PASS and the exit code is 1.
Exit 0 only when all six are PASS. Standard library only; reads files, executes only timeline.py --verify.
"""
import argparse, csv, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQS = ["injection", "detection", "diagnosis", "recovery", "timeline", "simulation"]


def load_events(run):
    evs = []
    for line in (run / "events.jsonl").read_text().splitlines():
        if line.strip():
            evs.append(json.loads(line))
    return evs


def load_steps(run):
    with open(run / "COMMANDS.tsv", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def steps_ok(steps, prefix, need_one=True):
    sel = [s for s in steps if s.get("step_id", "").startswith(prefix)]
    if need_one and not sel:
        return False, f"no {prefix}* steps"
    bad = [s["step_id"] for s in sel if s.get("result") != "PASS"]
    return (not bad), (f"{len(sel)} {prefix}* step(s) PASS" if not bad else f"{prefix}* not PASS: {', '.join(bad)}")


def evaluate(run, label_required=True):
    res = {}
    summ_p = run / "SUMMARY.json"
    if not summ_p.exists():
        return {r: ("NOT_EXECUTED", "SUMMARY.json missing: the scenario did not run") for r in REQS}
    summ = json.loads(summ_p.read_text())
    if summ.get("status") == "NOT_EXECUTED":
        why = str(summ.get("reason", "not executed"))
        return {r: ("NOT_EXECUTED", why) for r in REQS}
    try:
        evs, steps = load_events(run), load_steps(run)
    except (OSError, ValueError) as e:
        return {r: ("FAIL", f"unreadable run: {e}") for r in REQS}
    names = [e.get("event") for e in evs]
    ts = {e.get("event"): e.get("ts", "") for e in evs}
    metrics = summ.get("metrics") or {}

    ok, why = steps_ok(steps, "inject_")
    res["injection"] = ("PASS", why) if ok and "failure_injected" in names else ("FAIL", why if not ok else "no failure_injected event")

    mttd = metrics.get("mttd_s")
    det_ok = "detected" in names and "failure_injected" in names and ts["detected"] > ts["failure_injected"] \
        and isinstance(mttd, (int, float)) and not isinstance(mttd, bool) and mttd > 0
    res["detection"] = ("PASS", f"detected after injection, mttd_s={mttd}") if det_ok else ("FAIL", f"detection not shown (mttd_s={mttd!r})")

    ok, why = steps_ok(steps, "diag_")
    res["diagnosis"] = ("PASS", why) if ok and "diagnosed" in names else ("FAIL", why if not ok else "no diagnosed event")

    need = ["restore_started", "db_restarted", "data_integrity_verified", "service_restored"]
    miss = [n for n in need if n not in names]
    ok1, w1 = steps_ok(steps, "restore_")
    ok2, w2 = steps_ok(steps, "verify_")
    rec_ok = ok1 and ok2 and not miss and summ.get("status") == "PASS"
    res["recovery"] = ("PASS", f"{w1}; {w2}; events present") if rec_ok else \
        ("FAIL", "; ".join(x for x in [w1 if not ok1 else "", w2 if not ok2 else "", ("missing events " + ", ".join(miss)) if miss else "",
                                         "" if summ.get("status") == "PASS" else f"run status {summ.get('status')}"] if x))

    tl = ROOT / "scenarios/incident/lib/timeline.py"
    if not (run / "TIMELINE.md").exists():
        res["timeline"] = ("FAIL", "TIMELINE.md missing")
    elif not tl.exists():
        res["timeline"] = ("FAIL", "timeline.py missing (incident module not integrated)")
    else:
        p = subprocess.run([sys.executable, str(tl), "--verify", str(run)], capture_output=True, text=True)
        res["timeline"] = ("PASS", "timeline.py --verify OK (metrics re-derived, hashes checked)") if p.returncode == 0 \
            else ("FAIL", f"timeline.py --verify exit {p.returncode}")

    bad = [i for i, e in enumerate(evs) if e.get("simulation") != "SIMULATION"]
    probs = []
    if bad: probs.append(f"{len(bad)} event(s) without simulation=SIMULATION")
    if summ.get("simulation") != "SIMULATION": probs.append("SUMMARY.json simulation marker missing")
    if "SIMULATION" not in (run / "TIMELINE.md").read_text() if (run / "TIMELINE.md").exists() else True: probs.append("TIMELINE.md lacks SIMULATION")
    lab = run / "SIMULATION.md"
    if label_required and not (lab.exists() and lab.read_text().lstrip().startswith("# SIMULATION")):
        probs.append("SIMULATION.md directory label missing or not starting with '# SIMULATION'")
    res["simulation"] = ("PASS", f"{len(evs)} events, summary, timeline and label marked SIMULATION") if not probs else ("FAIL", "; ".join(probs))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--json-out")
    ap.add_argument("--summary")
    ap.add_argument("--no-label", action="store_true", help="fresh CI runs: the directory label is not written by the runner")
    a = ap.parse_args(argv)
    run = Path(a.run)
    res = evaluate(run, label_required=not a.no_label)
    for r in REQS:
        st, why = res[r]
        print(f"{r:<11} {st:<12} {why}")
    verdict = "PASS" if all(res[r][0] == "PASS" for r in REQS) else \
        ("NOT_EXECUTED" if any(res[r][0] == "NOT_EXECUTED" for r in REQS) else "FAIL")
    print(f"INCIDENT REQUIREMENTS {verdict}: {run}")
    if verdict == "NOT_EXECUTED":
        print(f"::error title=incident NOT_EXECUTED::{run}: requirement not executed; acceptance is blocked (never PASS)")
    if a.json_out:
        Path(a.json_out).write_text(json.dumps({"run": str(run), "verdict": verdict,
                                                "requirements": {r: {"status": res[r][0], "detail": res[r][1]} for r in REQS}}, indent=2) + "\n")
    if a.summary:
        with open(a.summary, "a") as f:
            f.write(f"### SIMULATION incident requirements: **{verdict}** (`{run}`)\n\n| requirement | status | detail |\n|---|---|---|\n")
            for r in REQS:
                f.write(f"| {r} | {res[r][0]} | {res[r][1].replace('|', '/')} |\n")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
