#!/usr/bin/env python3
"""SIMULATION - build (or --verify) the incident timeline for one run directory.

Inputs (written by run_incident_demo.sh): events.jsonl, monitor.tsv, COMMANDS.tsv.
Outputs: TIMELINE.md (America/New_York + UTC), SUMMARY.json.
--verify re-derives every metric from events.jsonl / monitor.tsv, re-checks SHA256SUMS and the
SIMULATION labels, and exits non-zero on any mismatch (so a hand-edited summary cannot pass).
"""
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
REQUIRED = ["baseline_healthy", "failure_injected", "detected", "diagnosed",
            "restore_started", "db_restarted", "data_integrity_verified", "service_restored"]


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def ny(d):
    return d.astimezone(NY).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " " + d.astimezone(NY).tzname()


def load(run):
    with open(os.path.join(run, "events.jsonl"), encoding="utf-8") as fh:
        events = [json.loads(l) for l in fh if l.strip()]
    with open(os.path.join(run, "monitor.tsv"), encoding="utf-8") as fh:
        polls = list(csv.DictReader(fh, delimiter="\t"))
    with open(os.path.join(run, "COMMANDS.tsv"), encoding="utf-8") as fh:
        cmds = list(csv.DictReader(fh, delimiter="\t"))
    return events, polls, cmds


def metrics(events, polls):
    first = {}
    for e in events:
        first.setdefault(e["event"], e)
    missing = [k for k in REQUIRED if k not in first]
    if missing:
        return None, first, missing
    t = {k: ts(first[k]["ts"]) for k in REQUIRED}
    inj = t["failure_injected"]
    # independent cross-check: the first UNHEALTHY poll that STARTED after injection
    after = [p for p in polls if ts(p["started_utc"]) >= inj]
    bad = next((p for p in after if p["overall"] != "HEALTHY"), None)
    good = next((p for p in after if bad and int(p["seq"]) > int(bad["seq"]) and p["overall"] == "HEALTHY"), None)
    sec = lambda a, b: round((t[b] - t[a]).total_seconds(), 3)
    m = {
        "mttd_s": sec("failure_injected", "detected"),
        "time_to_diagnose_s": sec("detected", "diagnosed"),
        "detect_to_restore_s": sec("detected", "service_restored"),
        "mttr_s": sec("failure_injected", "service_restored"),
        "db_unavailable_s": sec("failure_injected", "db_restarted"),
        "first_unhealthy_poll_seq": int(bad["seq"]) if bad else None,
        "first_healthy_poll_after_seq": int(good["seq"]) if good else None,
        "poll_cross_check": bool(bad and good
                                 and bad["finished_utc"] == first["detected"]["detail"].get("poll_finished_utc")
                                 and good["finished_utc"] == first["service_restored"]["detail"].get("poll_finished_utc")),
        "polls_total": len(polls),
        "polls_unhealthy": sum(1 for p in polls if p["overall"] != "HEALTHY"),
    }
    return m, first, []


def build(run):
    events, polls, cmds = load(run)
    m, first, missing = metrics(events, polls)
    failed_cmds = [c for c in cmds if c["result"] != "PASS"]
    status = "PASS" if (m and m["poll_cross_check"] and not failed_cmds) else "FAIL"
    summary = {"simulation": "SIMULATION", "run_id": os.path.basename(os.path.abspath(run)),
               "status": status, "missing_events": missing, "metrics": m,
               "failed_steps": [c["step_id"] for c in failed_cmds],
               "steps_total": len(cmds), "timezone_reported": "America/New_York"}
    lines = ["# SIMULATION — incident timeline (%s)" % summary["run_id"], "",
             "> **SIMULATION.** Fault injected on purpose into a throwaway local lab. No real bank, customer, "
             "vendor or production system was involved. Notifications listed here were **not sent**.", "",
             "Status: **%s**  " % status]
    if m:
        lines += ["MTTD **%.3f s** · time to diagnose %.3f s · detect→restore %.3f s · **MTTR %.3f s** "
                  "(injection → monitor-confirmed HEALTHY) · DB unavailable %.3f s" %
                  (m["mttd_s"], m["time_to_diagnose_s"], m["detect_to_restore_s"], m["mttr_s"], m["db_unavailable_s"]),
                  "", "Polls: %d total, %d UNHEALTHY; cross-check against monitor.tsv: %s" %
                  (m["polls_total"], m["polls_unhealthy"], "OK" if m["poll_cross_check"] else "MISMATCH")]
    lines += ["", "| # | Time (America/New_York) | UTC | Event | Detail |", "|---|---|---|---|---|"]
    for i, e in enumerate(events, 1):
        d = ts(e["ts"])
        det = e["detail"] if isinstance(e["detail"], str) else json.dumps(e["detail"], sort_keys=True)
        lines.append("| %d | %s | %s | `%s` | %s |" % (i, ny(d), e["ts"], e["event"], det.replace("|", "\\|")))
    lines += ["", "## Monitor polls (observability `collect`)", "",
              "| seq | finished (America/New_York) | exit | overall | failed checks |", "|---|---|---|---|---|"]
    for p in polls:
        lines.append("| %s | %s | %s | %s | %s |" % (p["seq"], ny(ts(p["finished_utc"])), p["exit_code"],
                                                    p["overall"], p["failed_checks"] or "—"))
    with open(os.path.join(run, "TIMELINE.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(os.path.join(run, "SUMMARY.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


def verify(run):
    errs = []
    events, polls, cmds = load(run)
    m, _, missing = metrics(events, polls)
    with open(os.path.join(run, "SUMMARY.json"), encoding="utf-8") as fh:
        s = json.load(fh)
    if missing:
        errs.append("missing events: %s" % missing)
    if s.get("metrics") != m:
        errs.append("SUMMARY.json metrics do not match values re-derived from events.jsonl/monitor.tsv")
    if s.get("simulation") != "SIMULATION" or any(e.get("simulation") != "SIMULATION" for e in events):
        errs.append("SIMULATION label missing")
    sums = os.path.join(run, "SHA256SUMS")
    with open(sums, encoding="utf-8") as fh:
        for line in fh:
            h, name = line.rstrip("\n").split("  ", 1)
            with open(os.path.join(run, name), "rb") as f:
                if hashlib.sha256(f.read()).hexdigest() != h:
                    errs.append("hash mismatch: %s" % name)
    for e in errs:
        print("VERIFY FAIL:", e)
    print("VERIFY", "FAIL" if errs else "PASS", "(SIMULATION run %s)" % os.path.basename(os.path.abspath(run)))
    return 1 if errs else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--verify":
        sys.exit(verify(sys.argv[2]))
    if len(sys.argv) == 2:
        sys.exit(build(sys.argv[1]))
    sys.exit("usage: timeline.py RUN_DIR | --verify RUN_DIR")
