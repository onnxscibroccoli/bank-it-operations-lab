# Canary ring procedure

> Reference procedure for the bank-it-operations-lab. Example values only; nothing in this
> repository runs it against real hosts.

## Purpose

Expose each monthly patch set to the smallest useful slice of the estate first, with a hard stop on
the first failure, before any wider ring is allowed to install.

## Ring definition

| Setting | Value | Where it is set |
|---|---|---|
| Patch groups | `canary`, `canary-rhel` (tag `PatchGroup`) | `ssm/cli/register-target.canary.json`, CFN `WindowCanaryTargets` |
| Operation | `Install` | `ssm/cli/register-task.canary.json` |
| MaxConcurrency / MaxErrors | `1` / `0` | same; enforced by `PM-CANARY-SIZE`, `PM-CANARY-ERRORS` |
| Reboot | `RebootIfNeeded` | same |
| Window | Tuesday 02:00 America/New_York, 3 h, 1 h cutoff | `ssm/cli/create-maintenance-window.canary.json` |
| Soak | 48 h minimum before the wave1 gate can open | `manifests/patch-manifest.example.json` |

Canary membership: at least one host per OS family, per application tier, and per AMI lineage in
use. Canary hosts must be production-like (same baseline, same agents, same hardening drop-ins) but
must not be the only instance of any service.

## Steps

1. **T-24h: dry run.** `python3 operations/patching/tools/inspect_patch_manifest.py
   operations/patching/manifests/<cycle>.json --plan` must exit `0`. Attach output to the change record.
2. **T-24h: scan.** A `Scan` run against the canary group records the missing-patch list (expected
   delta). Keep the compliance summary as "before" evidence.
3. **T-1h: pre-snapshot.** Take EBS snapshots / AMI of each canary host (`preSnapshot: true`). Record
   snapshot ids in the change record. No snapshot, no install.
4. **T0: install.** The maintenance window runs `AWS-RunPatchBaseline` `Install` one host at a time;
   `MaxErrors=0` stops the window on the first failed invocation.
5. **T+1h: verify.** For each host: SSM compliance `COMPLIANT`, reboot completed, `systemctl
   --failed` empty, application health check green, hardening drop-ins still loaded
   (`systemctl show -p NoNewPrivileges,ProtectSystem <unit>`).
6. **Soak 48h.** Watch error rates, latency, auth failures, and kernel/OOM logs against the prior week.
7. **Sign-off.** Produce the canary sign-off (see
   `evidence/host-operations/examples/canary-signoff.example.md`) and request the wave1 gate
   ([APPROVAL.md](APPROVAL.md)).

## Stop conditions

Any of: a failed invocation, a host not back within 15 minutes of reboot, a `NON_COMPLIANT` result
after install, a failed systemd unit that was healthy before, or a health-check regression. On any
stop condition: do **not** open the wave1 gate, start [ROLLBACK.md](ROLLBACK.md) for affected hosts,
and follow [ESCALATION.md](ESCALATION.md).
