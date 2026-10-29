#!/usr/bin/env python3
"""Offline, read-only systemd unit hardening inspector for bank-it-operations-lab.

Parses a .service unit plus optional drop-in .conf files (merged the way systemd merges them:
drop-ins in lexical filename order after the unit, last scalar assignment wins, empty assignment
resets, list settings accumulate), then reports a `systemd-analyze security`-style exposure
estimate (0.0 = fully locked down, 10.0 = no sandboxing). It is an approximation written for
review/evidence, NOT a replacement for `systemd-analyze security` on the real host, and it never
installs, reloads, starts or modifies a unit.

With --target-systemd N (or --distro ID from compat/systemd-directives.json) it also flags
directives or values the target systemd does not understand -- systemd ignores those with a
warning, so the protection silently disappears -- and scores the unit as the target would run it.

It also fails when a later drop-in weakens a setting an earlier file had hardened (for example an
empty `CapabilityBoundingSet=~` or `ProtectSystem=` reset in a 90-*.conf).

Exit codes: 0 effective exposure <= threshold, nothing unsupported, no drop-in regression; 1 findings;
2 malformed input (fail closed). Python stdlib only.

Usage:
  score_units.py UNIT [--dropin FILE ...] [--target-systemd N | --distro ID]
                 [--threshold X] [--json]
  score_units.py --render-matrix           # print COMPATIBILITY.md body from the compat JSON
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMPAT = os.path.join(HERE, "..", "compat", "systemd-directives.json")
DEFAULT_THRESHOLD = 4.0
KNOWN_SECTIONS = {"Unit", "Service", "Install"}
LIST_KEYS = {"CapabilityBoundingSet", "AmbientCapabilities", "SystemCallFilter", "RestrictAddressFamilies",
             "ReadWritePaths", "ReadOnlyPaths", "InaccessiblePaths", "ExecStart", "ExecStartPre",
             "ExecStartPost", "Environment", "IPAddressDeny", "IPAddressAllow"}
BOOL_TRUE = {"1", "yes", "true", "on"}
BOOL_FALSE = {"0", "no", "false", "off"}
ALL_CAPS = {
    "CAP_AUDIT_CONTROL", "CAP_AUDIT_READ", "CAP_AUDIT_WRITE", "CAP_BLOCK_SUSPEND", "CAP_BPF",
    "CAP_CHECKPOINT_RESTORE", "CAP_CHOWN", "CAP_DAC_OVERRIDE", "CAP_DAC_READ_SEARCH", "CAP_FOWNER",
    "CAP_FSETID", "CAP_IPC_LOCK", "CAP_IPC_OWNER", "CAP_KILL", "CAP_LEASE", "CAP_LINUX_IMMUTABLE",
    "CAP_MAC_ADMIN", "CAP_MAC_OVERRIDE", "CAP_MKNOD", "CAP_NET_ADMIN", "CAP_NET_BIND_SERVICE",
    "CAP_NET_BROADCAST", "CAP_NET_RAW", "CAP_PERFMON", "CAP_SETFCAP", "CAP_SETGID", "CAP_SETPCAP",
    "CAP_SETUID", "CAP_SYS_ADMIN", "CAP_SYS_BOOT", "CAP_SYS_CHROOT", "CAP_SYS_MODULE", "CAP_SYS_NICE",
    "CAP_SYS_PACCT", "CAP_SYS_PTRACE", "CAP_SYS_RAWIO", "CAP_SYS_RESOURCE", "CAP_SYS_TIME",
    "CAP_SYS_TTY_CONFIG", "CAP_SYSLOG", "CAP_WAKE_ALARM",
}
DANGEROUS_CAPS = {
    "CAP_SYS_ADMIN", "CAP_SYS_PTRACE", "CAP_SYS_MODULE", "CAP_SYS_RAWIO", "CAP_SYS_BOOT", "CAP_SYS_TIME",
    "CAP_DAC_OVERRIDE", "CAP_DAC_READ_SEARCH", "CAP_SETUID", "CAP_SETGID", "CAP_SETPCAP", "CAP_SETFCAP",
    "CAP_CHOWN", "CAP_FOWNER", "CAP_FSETID", "CAP_NET_ADMIN", "CAP_NET_RAW", "CAP_BPF", "CAP_PERFMON",
    "CAP_LINUX_IMMUTABLE", "CAP_MAC_ADMIN", "CAP_MAC_OVERRIDE", "CAP_SYSLOG", "CAP_MKNOD", "CAP_KILL",
    "CAP_AUDIT_CONTROL", "CAP_IPC_OWNER", "CAP_SYS_CHROOT",
}
RISKY_FAMILIES = {"AF_PACKET", "AF_NETLINK"}
ENUMS = {
    "ProtectSystem": {"strict": 1.0, "full": 0.66, "yes": 0.33, "true": 0.33, "on": 0.33, "1": 0.33,
                      "no": 0.0, "false": 0.0, "off": 0.0, "0": 0.0},
    "ProtectHome": {"yes": 1.0, "true": 1.0, "on": 1.0, "1": 1.0, "tmpfs": 1.0, "read-only": 0.5,
                    "no": 0.0, "false": 0.0, "off": 0.0, "0": 0.0},
    "ProtectControlGroups": {"yes": 1.0, "true": 1.0, "on": 1.0, "1": 1.0, "strict": 1.0, "private": 0.8,
                             "no": 0.0, "false": 0.0, "off": 0.0, "0": 0.0},
    "PrivateTmp": {"yes": 1.0, "true": 1.0, "on": 1.0, "1": 1.0, "disconnected": 1.0,
                   "no": 0.0, "false": 0.0, "off": 0.0, "0": 0.0},
    "ProtectProc": {"invisible": 1.0, "noaccess": 1.0, "ptraceable": 0.5, "default": 0.0},
    "ProcSubset": {"pid": 1.0, "all": 0.0},
}
BOOLS = ["NoNewPrivileges", "PrivateDevices", "PrivateNetwork", "PrivateUsers", "PrivateIPC",
         "ProtectKernelTunables", "ProtectKernelModules", "ProtectKernelLogs", "ProtectClock",
         "ProtectHostname", "RestrictSUIDSGID", "RestrictRealtime", "LockPersonality",
         "MemoryDenyWriteExecute", "DynamicUser", "RemoveIPC"]

# (id, directive or pseudo-check, weight, description)
CHECKS = [
    ("RunsAsNonRoot", "User", 10, "service runs as a dedicated non-root user (User= or DynamicUser=yes)"),
    ("NoNewPrivileges", "NoNewPrivileges", 8, "NoNewPrivileges=yes blocks setuid/file-capability escalation"),
    ("CapabilityBoundingSet", "CapabilityBoundingSet", 9, "bounding set excludes dangerous capabilities"),
    ("AmbientCapabilities", "AmbientCapabilities", 5, "no dangerous ambient capabilities granted"),
    ("ProtectSystem", "ProtectSystem", 7, "ProtectSystem=strict (full=partial)"),
    ("ProtectHome", "ProtectHome", 5, "ProtectHome=yes (read-only=partial)"),
    ("PrivateTmp", "PrivateTmp", 5, "PrivateTmp=yes"),
    ("PrivateDevices", "PrivateDevices", 5, "PrivateDevices=yes"),
    ("ProtectKernelTunables", "ProtectKernelTunables", 5, "ProtectKernelTunables=yes"),
    ("ProtectKernelModules", "ProtectKernelModules", 5, "ProtectKernelModules=yes"),
    ("ProtectKernelLogs", "ProtectKernelLogs", 3, "ProtectKernelLogs=yes"),
    ("ProtectControlGroups", "ProtectControlGroups", 4, "ProtectControlGroups=yes"),
    ("ProtectClock", "ProtectClock", 3, "ProtectClock=yes"),
    ("ProtectHostname", "ProtectHostname", 2, "ProtectHostname=yes"),
    ("ProtectProc", "ProtectProc", 3, "ProtectProc=invisible"),
    ("ProcSubset", "ProcSubset", 2, "ProcSubset=pid"),
    ("RestrictSUIDSGID", "RestrictSUIDSGID", 4, "RestrictSUIDSGID=yes"),
    ("RestrictRealtime", "RestrictRealtime", 2, "RestrictRealtime=yes"),
    ("RestrictNamespaces", "RestrictNamespaces", 5, "RestrictNamespaces=yes"),
    ("RestrictAddressFamilies", "RestrictAddressFamilies", 5, "address families allow-listed, no AF_PACKET/AF_NETLINK"),
    ("LockPersonality", "LockPersonality", 2, "LockPersonality=yes"),
    ("MemoryDenyWriteExecute", "MemoryDenyWriteExecute", 4, "MemoryDenyWriteExecute=yes"),
    ("SystemCallFilter", "SystemCallFilter", 7, "system calls allow-listed (e.g. @system-service)"),
    ("SystemCallArchitectures", "SystemCallArchitectures", 3, "SystemCallArchitectures=native"),
    ("RemoveIPC", "RemoveIPC", 1, "RemoveIPC=yes"),
    ("PrivateNetwork", "PrivateNetwork", 4, "PrivateNetwork=yes (only for services with no network needs)"),
    ("PrivateUsers", "PrivateUsers", 3, "PrivateUsers=yes"),
    ("IPAddressDeny", "IPAddressDeny", 3, "IPAddressDeny=any with explicit IPAddressAllow="),
    ("UMask", "UMask", 2, "UMask=0027 or stricter"),
]


class Malformed(Exception):
    pass


def load_compat():
    with open(COMPAT, encoding="utf-8") as fh:
        return json.load(fh)


def parse_file(path, is_dropin):
    """Return list of (section, key, value, source, lineno)."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except (OSError, UnicodeDecodeError) as exc:
        raise Malformed("cannot read %s: %s" % (path, exc))
    out, section, buf, start = [], None, "", 0
    name = os.path.basename(path)
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if buf:
            line = buf + " " + line
            buf = ""
        elif not line or line[0] in "#;":
            continue
        if line.endswith("\\"):
            buf, start = line[:-1].rstrip(), start or i
            continue
        ln = start or i
        start = 0
        if line.startswith("["):
            if not line.endswith("]"):
                raise Malformed("%s:%d: bad section header %r" % (name, ln, line))
            section = line[1:-1]
            if section not in KNOWN_SECTIONS and not section.startswith("X-"):
                raise Malformed("%s:%d: unknown section [%s]" % (name, ln, section))
            continue
        if section is None:
            raise Malformed("%s:%d: assignment outside any section" % (name, ln))
        if "=" not in line:
            raise Malformed("%s:%d: not a key=value line: %r" % (name, ln, line))
        key, val = line.split("=", 1)
        key, val = key.strip(), val.strip()
        if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", key):
            raise Malformed("%s:%d: invalid key %r" % (name, ln, key))
        out.append((section, key, val, name, ln))
    if buf:
        raise Malformed("%s: file ends inside a line continuation" % name)
    if not is_dropin:
        if not any(s == "Service" for s, *_ in out):
            raise Malformed("%s: no [Service] section" % name)
        if not any(s == "Service" and k == "ExecStart" and v for s, k, v, *_ in out):
            raise Malformed("%s: [Service] has no ExecStart=" % name)
    return out


def merge(unit, dropins):
    """Merge assignments; returns (scalars, lists, provenance)."""
    entries = parse_file(unit, False)
    for d in sorted(dropins, key=lambda p: os.path.basename(p)):
        if not d.endswith(".conf"):
            raise Malformed("drop-in %s must end in .conf" % d)
        entries += parse_file(d, True)
    scalars, lists, prov = {}, {}, {}
    for section, key, val, src, ln in entries:
        if section != "Service":
            continue
        if key in LIST_KEYS:
            if val == "":
                lists[key] = [""]  # explicit reset marker kept for semantic evaluation
            else:
                lists.setdefault(key, []).append(val)
        elif val == "":
            scalars.pop(key, None)
        else:
            scalars[key] = val
        prov[key] = "%s:%d" % (src, ln)
    return scalars, lists, prov


def norm_bool(key, val):
    v = val.lower()
    if v in BOOL_TRUE:
        return True
    if v in BOOL_FALSE:
        return False
    raise Malformed("%s=%s is not a boolean" % (key, val))


def validate_values(scalars):
    for k in BOOLS:
        if k in scalars:
            norm_bool(k, scalars[k])
    for k, allowed in ENUMS.items():
        if k in scalars and scalars[k].lower() not in allowed:
            raise Malformed("%s=%s is not one of %s" % (k, scalars[k], sorted(allowed)))
    if "UMask" in scalars and not re.match(r"^0?[0-7]{3,4}$", scalars["UMask"]):
        raise Malformed("UMask=%s is not octal" % scalars["UMask"])
    if "RestrictNamespaces" in scalars:
        v = scalars["RestrictNamespaces"].lower()
        if v not in BOOL_TRUE | BOOL_FALSE and not re.match(r"^~?[a-z ]+$", v):
            raise Malformed("RestrictNamespaces=%s invalid" % scalars["RestrictNamespaces"])


def cap_state(assignments, where):
    state = None  # None == unrestricted (full set)
    for a in assignments:
        if a == "":
            state = set()
            continue
        if a == "~":
            state = None
            continue
        inv = a.startswith("~")
        caps = set(a[1:].split() if inv else a.split())
        unknown = caps - ALL_CAPS
        if unknown:
            raise Malformed("%s: unknown capability %s" % (where, ", ".join(sorted(unknown))))
        if inv:
            state = (set(ALL_CAPS) if state is None else state) - caps
        else:
            state = (set() if state is None else state) | caps
    return set(ALL_CAPS) if state is None else state


def list_mode(assignments):
    """Return (mode, items) for allow/deny list settings after resets. mode in unset/allow/deny."""
    mode, items = "unset", set()
    for a in assignments:
        if a == "":
            mode, items = "unset", set()
            continue
        inv = a.startswith("~")
        vals = set((a[1:] if inv else a).split())
        if mode == "unset":
            mode, items = ("deny" if inv else "allow"), vals
        elif (mode == "deny") == inv:
            items |= vals
        elif mode == "allow" and inv:
            items -= vals
        else:
            items -= vals
    return mode, items


def supported(key, val, version, compat):
    """Return None if supported on target, else the minimum version needed."""
    d = compat["directives"].get(key)
    if d is None or version is None:
        return None
    need = d["minVersion"]
    for v, ver in d.get("values", {}).items():
        if v in val.split() or v == val.lower() or ("@" in v and v in val):
            need = max(need, ver)
    return need if version < need else None


def evaluate(scalars, lists):
    def b(k):
        return k in scalars and norm_bool(k, scalars[k])
    res = {}
    user = scalars.get("User", "")
    res["RunsAsNonRoot"] = 1.0 if b("DynamicUser") or (user and user not in ("root", "0")) else 0.0
    for k in BOOLS:
        res[k] = 1.0 if b(k) else 0.0
    for k, table in ENUMS.items():
        res[k] = table[scalars[k].lower()] if k in scalars else 0.0
    caps = cap_state(lists.get("CapabilityBoundingSet", []), "CapabilityBoundingSet")
    res["CapabilityBoundingSet"] = 1.0 - len(caps & DANGEROUS_CAPS) / float(len(DANGEROUS_CAPS))
    amb = cap_state([""] + lists.get("AmbientCapabilities", []), "AmbientCapabilities")
    res["AmbientCapabilities"] = 0.0 if amb & DANGEROUS_CAPS else 1.0
    rn = scalars.get("RestrictNamespaces", "").lower()
    res["RestrictNamespaces"] = 1.0 if rn in BOOL_TRUE else (0.0 if rn in BOOL_FALSE or not rn else 0.5)
    mode, fams = list_mode(lists.get("RestrictAddressFamilies", []))
    if mode == "allow":
        res["RestrictAddressFamilies"] = 1.0 if "none" in fams or not (fams & RISKY_FAMILIES) else 0.5
    else:
        res["RestrictAddressFamilies"] = 0.5 if mode == "deny" and RISKY_FAMILIES <= fams else 0.0
    mode, _ = list_mode(lists.get("SystemCallFilter", []))
    res["SystemCallFilter"] = {"allow": 1.0, "deny": 0.5, "unset": 0.0}[mode]
    res["SystemCallArchitectures"] = 1.0 if scalars.get("SystemCallArchitectures", "") == "native" else 0.0
    ipd = []
    for a in lists.get("IPAddressDeny", []):
        ipd = [] if a == "" else ipd + a.split()
    res["IPAddressDeny"] = 1.0 if "any" in ipd else (0.5 if ipd else 0.0)
    um = scalars.get("UMask")
    res["UMask"] = 1.0 if um and (int(um, 8) & 0o027) == 0o027 else 0.0
    return res


def strip_unsupported(scalars, lists, version, compat):
    unsupported = []
    s2, l2 = {}, {}
    for k, v in scalars.items():
        need = supported(k, v, version, compat)
        if need:
            unsupported.append({"directive": k, "value": v, "needsSystemd": need})
        else:
            s2[k] = v
    for k, vals in lists.items():
        keep = []
        for v in vals:
            need = supported(k, v, version, compat) if v else None
            if need:
                unsupported.append({"directive": k, "value": v, "needsSystemd": need})
            else:
                keep.append(v)
        if keep:
            l2[k] = keep
    return s2, l2, unsupported


def exposure(res):
    total = sum(w for _, _, w, _ in CHECKS)
    missing = sum(w * (1.0 - res[cid]) for cid, _, w, _ in CHECKS)
    return round(10.0 * missing / total, 1)


def rating(x):
    return "GOOD" if x <= 3.0 else ("MEDIUM" if x <= 6.0 else "EXPOSED")


def score(unit, dropins=(), target=None, threshold=DEFAULT_THRESHOLD, compat=None):
    compat = compat or load_compat()
    scalars, lists, prov = merge(unit, list(dropins))
    validate_values(scalars)
    declared = evaluate(scalars, lists)
    unsupported = []
    effective = declared
    if target is not None:
        s2, l2, unsupported = strip_unsupported(scalars, lists, target, compat)
        effective = evaluate(s2, l2)
    checks = [{"id": cid, "directive": d, "weight": w, "description": desc,
               "declaredScore": round(declared[cid], 2), "effectiveScore": round(effective[cid], 2),
               "setAt": prov.get(d) or (prov.get("DynamicUser") if cid == "RunsAsNonRoot" else None)}
              for cid, d, w, desc in CHECKS]
    eff = exposure(effective)
    findings = []
    # Drop-in regression: a later drop-in must never weaken what an earlier layer set.
    ordered = sorted(dropins, key=os.path.basename)
    regressions = []
    if ordered:
        best = {}
        for i in range(len(ordered)):
            s_i, l_i, _ = merge(unit, ordered[:i + 1])
            validate_values(s_i)
            r_i = evaluate(s_i, l_i)
            for cid, v in r_i.items():
                if v > best.get(cid, (-1, None))[0]:
                    best[cid] = (v, os.path.basename(ordered[i]))
        base_s, base_l, _ = merge(unit, [])
        for cid, v in evaluate(base_s, base_l).items():
            if v > best.get(cid, (-1, None))[0]:
                best[cid] = (v, os.path.basename(unit))
        for cid, _, _, _ in CHECKS:
            peak, where = best[cid]
            if declared[cid] + 1e-9 < peak:
                regressions.append({"check": cid, "peakScore": round(peak, 2), "peakAt": where,
                                    "finalScore": round(declared[cid], 2)})
                findings.append("%s weakened by a later drop-in (%.2f at %s -> %.2f final)"
                                % (cid, peak, where, declared[cid]))
    if eff > threshold:
        findings.append("effective exposure %.1f exceeds threshold %.1f" % (eff, threshold))
    for u in unsupported:
        findings.append("%s=%s needs systemd >= %d (target %d): ignored on target"
                        % (u["directive"], u["value"], u["needsSystemd"], target))
    return {
        "tool": "score_units", "mode": "offline-read-only", "hostModified": False,
        "unit": os.path.basename(unit), "dropins": [os.path.basename(d) for d in sorted(dropins, key=os.path.basename)],
        "targetSystemd": target, "threshold": threshold,
        "declaredExposure": exposure(declared), "effectiveExposure": eff, "rating": rating(eff),
        "unsupported": unsupported, "regressions": regressions, "checks": checks, "findings": findings,
        "overall": "FAIL" if findings else "PASS",
    }


def render_matrix(compat):
    ds = compat["distros"]
    head = "| Directive | min systemd | " + " | ".join("%s (%d)" % (d["name"], d["systemd"]) for d in ds) + " |"
    sep = "|---|---|" + "---|" * len(ds)
    rows = [head, sep]
    for k in sorted(compat["directives"]):
        info = compat["directives"][k]
        mv = info["minVersion"]
        cells = ["yes" if d["systemd"] >= mv else "**no**" for d in ds]
        rows.append("| `%s=` | %s | %s |" % (k, mv if mv else "< 187", " | ".join(cells)))
        for val, ver in sorted(info.get("values", {}).items()):
            cells = ["yes" if d["systemd"] >= ver else "**no**" for d in ds]
            rows.append("| `%s=%s` | %d | %s |" % (k, val, ver, " | ".join(cells)))
    return "\n".join(rows) + "\n"


def render_text(rep):
    out = ["%s + %s  (offline estimate; nothing applied)" % (rep["unit"], ", ".join(rep["dropins"]) or "no drop-ins")]
    for c in rep["checks"]:
        mark = "ok " if c["effectiveScore"] >= 1.0 else ("~  " if c["effectiveScore"] > 0 else "-- ")
        out.append("  %s %-24s w=%-2d %s" % (mark, c["id"], c["weight"], c["description"]))
    if rep["targetSystemd"] is not None:
        out.append("target systemd %d: %d unsupported directive(s)" % (rep["targetSystemd"], len(rep["unsupported"])))
    out.append("declared exposure %.1f, effective exposure %.1f [%s], threshold %.1f"
               % (rep["declaredExposure"], rep["effectiveExposure"], rep["rating"], rep["threshold"]))
    for f in rep["findings"]:
        out.append("  FINDING: %s" % f)
    out.append("overall: %s" % rep["overall"])
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("unit", nargs="?")
    ap.add_argument("--dropin", action="append", default=[])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--target-systemd", type=int)
    g.add_argument("--distro")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--render-matrix", action="store_true")
    a = ap.parse_args(argv)
    compat = load_compat()
    if a.render_matrix:
        sys.stdout.write(render_matrix(compat))
        return 0
    if not a.unit:
        ap.error("unit is required")
    target = a.target_systemd
    if a.distro:
        match = [d for d in compat["distros"] if d["id"] == a.distro]
        if not match:
            msg = "unknown distro %s" % a.distro
            print(json.dumps({"tool": "score_units", "overall": "MALFORMED", "error": msg}, indent=2)
                  if a.json else "MALFORMED: %s" % msg)
            return 2
        target = match[0]["systemd"]
    try:
        rep = score(a.unit, a.dropin, target, a.threshold, compat)
    except Malformed as exc:
        print(json.dumps({"tool": "score_units", "overall": "MALFORMED", "error": str(exc)}, indent=2)
              if a.json else "MALFORMED: %s" % exc)
        return 2
    print(json.dumps(rep, indent=2) if a.json else render_text(rep))
    return 0 if rep["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
