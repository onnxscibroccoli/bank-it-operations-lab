# Hybrid operations: execution status

> **Execution status: NOT_EXECUTED** (all rows). Reason for every row: no authorized Windows Server / AD DS / DNS / GPO environment or Microsoft Entra tenant was available to this lab. Nothing has been run.

Allowed values: `NOT_EXECUTED` (current), `EXECUTED_IN_LAB` (needs the evidence below, committed under `evidence/hybrid/<runbook>/<date>/`), `RETIRED`.

| Runbook | Status | Evidence required before status can change |
|---|---|---|
| [Windows Server baseline](../../docs/runbooks/hybrid/windows-server-baseline.md) | NOT_EXECUTED | Build record, `Get-ComputerInfo` excerpt, applied baseline report, patch level (`Get-HotFix`), Defender/firewall state |
| [Active Directory DS](../../docs/runbooks/hybrid/active-directory.md) | NOT_EXECUTED | `dcdiag /v` and `repadmin /replsummary` output, FSMO holders, system-state backup log, Recycle Bin state, restore test record |
| [DNS](../../docs/runbooks/hybrid/dns.md) | NOT_EXECUTED | Zone list, forwarder/conditional forwarder config, scavenging settings, `Resolve-DnsName` test matrix results |
| [Group Policy](../../docs/runbooks/hybrid/group-policy.md) | NOT_EXECUTED | GPO backup manifest, HTML reports before/after, `gpresult` from a pilot host, change record |
| [Hybrid identity (Entra Connect / Cloud Sync)](../../docs/runbooks/hybrid/hybrid-identity.md) | NOT_EXECUTED | IdFix report, staging-mode export comparison, scheduler state, Connect Health / provisioning log screenshots (redacted) |
| [Incident playbooks](../../docs/runbooks/hybrid/incident-playbooks.md) | NOT_EXECUTED | Tabletop or lab exercise record per scenario, timeline, and actions |
| [Evidence template](../../docs/runbooks/hybrid/evidence-template.md) | NOT_EXECUTED | n/a (template); used by the rows above |

Reviewer sign-off for any status change: change owner plus a second reviewer (two-person rule, see [`change-gates.md`](change-gates.md)).
