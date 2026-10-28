# systemd service hardening -- reference drop-ins and offline inspector

> **Example / offline.** Units and drop-ins here are review material. Nothing in this repository
> installs them, runs `systemctl`, or changes a host.

## Layout

| Path | What it is |
|---|---|
| `systemd/units/bank-lab-app.service` | Example localhost HTTP service, deliberately unhardened so each drop-in layer is reviewable. |
| `systemd/units/bank-lab-root-agent.service` | Example "vendor agent as shipped" (root, no sandbox) -- what an unreviewed unit scores. |
| `systemd/dropins/05-hardening-legacy-219.conf` | Subset understood by systemd 219 (RHEL/CentOS 7, Amazon Linux 2). |
| `systemd/dropins/10-hardening-baseline.conf` | Low-breakage baseline (`NoNewPrivileges`, `PrivateTmp`, `PrivateDevices`, `ProtectSystem=full`, `ProtectKernel*`, `RestrictSUIDSGID`, ...). systemd >= 242. |
| `systemd/dropins/20-hardening-strict.conf` | Strict layer (`ProtectSystem=strict`, empty `CapabilityBoundingSet=`, `SystemCallFilter=@system-service`, `RestrictAddressFamilies`, `IPAddressDeny=any`, ...). systemd >= 247. |
| `systemd/dropins/30-net-bind-service.conf` | Opt-in exception re-adding only `CAP_NET_BIND_SERVICE`. |
| `compat/systemd-directives.json` | Directive -> minimum systemd version, distro -> systemd version (single source of truth). |
| `COMPATIBILITY.md` | Matrix by distro, generated from the JSON (drift-tested). |
| `tools/score_units.py` | Offline, read-only inspector: merges unit + drop-ins like systemd, scores a `systemd-analyze security`-style exposure (0-10), flags directives the target systemd would silently ignore, and flags later drop-ins that weaken earlier hardening. |
| `tests/` | 27 CLI fixture cases (`fixtures/INDEX.json`) plus semantic and shipped-example tests. |

## Run

```bash
D=operations/hardening/systemd/dropins
python3 operations/hardening/tools/score_units.py operations/hardening/systemd/units/bank-lab-app.service \
  --dropin $D/10-hardening-baseline.conf --dropin $D/20-hardening-strict.conf --distro rhel9
python3 operations/hardening/tools/score_units.py --render-matrix
python3 -m unittest discover -s operations/hardening/tests -v     # or: python3 -m pytest operations/hardening/tests
```

Exit codes: `0` effective exposure <= threshold (default 4.0), nothing unsupported, no drop-in
regression; `1` findings; `2` malformed unit/drop-in (fail closed).

## Scorer vs `systemd-analyze security`

The scorer is a deliberately simple, explainable approximation (26 weighted checks). It is not
systemd's algorithm. The evidence run in `evidence/host-operations/runs/` records both for the same
inputs; ordering agrees (root agent > unhardened app > baseline > strict) while absolute numbers
differ. Use `systemd-analyze security <unit>` on a real host as the authority.

## Rollout guidance

Apply one layer at a time per service, canary first, the same way as patches
(`operations/patching/procedures/CANARY.md`): install drop-in, `systemctl daemon-reload`, restart,
check health and `journalctl -u <unit>` for `EPERM`/`SIGSYS`/`Read-only file system`, soak, then
widen. Roll back by deleting the drop-in and reloading. Those host steps are for operators on real
hosts under a change record; this repository never performs them.
