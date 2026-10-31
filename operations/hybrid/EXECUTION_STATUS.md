# Hybrid operations: execution status

> **Execution status: NOT_EXECUTED** (all rows). Reason for every row: no authorized Windows Server / AD DS / DNS / GPO environment or Microsoft Entra tenant was available to this lab. Nothing has been run.

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Operate local Windows directory services and their connections to cloud identity. Separating directory, name-resolution, policy, and synchronization problems avoids broad changes that obscure the cause.

For example: A user can reach a server by address but not by name, so an operator investigates name resolution before changing account permissions.

Key terms: **AD DS** means active Directory Domain Services: a directory used to manage Windows identities and resources. **DNS** means domain Name System: translates names into resource-location information. **GPO** means group Policy Object: a set of Windows policy settings. **Hybrid identity** means identity management spanning local directory systems and cloud services.

**Before using this reference:** Directory, DNS, policy, and synchronization changes can affect many users. Use the documented permissions and change gates; no live execution is implied.

Start with the [plain-English learning path](../../docs/knowledge/identity.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->



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
