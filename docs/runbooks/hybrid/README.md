# Hybrid infrastructure runbooks

> **Execution status: NOT_EXECUTED.** None of these runbooks has been run. No authorized Windows Server, AD DS, DNS, Group Policy or Microsoft Entra environment was available. Treat every command as a reviewed plan. Names and addresses are synthetic (see [`operations/hybrid/lab-topology.md`](../../../operations/hybrid/lab-topology.md)).

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Operate local Windows directory services and their connections to cloud identity. Separating directory, name-resolution, policy, and synchronization problems avoids broad changes that obscure the cause.

For example: A user can reach a server by address but not by name, so an operator investigates name resolution before changing account permissions.

Key terms: **AD DS** means active Directory Domain Services: a directory used to manage Windows identities and resources. **DNS** means domain Name System: translates names into resource-location information. **GPO** means group Policy Object: a set of Windows policy settings. **Hybrid identity** means identity management spanning local directory systems and cloud services.

**Before using this reference:** Directory, DNS, policy, and synchronization changes can affect many users. Use the documented permissions and change gates; no live execution is implied.

Start with the [plain-English learning path](../../knowledge/identity.md) or [glossary](../../knowledge/glossary.md). [Current integration and review policy](../../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->



| Runbook | Covers |
|---|---|
| [windows-server-baseline.md](windows-server-baseline.md) | Build, hardening, patching and health of Windows Server hosts |
| [active-directory.md](active-directory.md) | DC promotion, FSMO, replication health, backup/restore, Recycle Bin, krbtgt reset, tiering |
| [dns.md](dns.md) | AD-integrated zones, forwarders, conditional forwarders to cloud DNS, scavenging, troubleshooting |
| [group-policy.md](group-policy.md) | GPO design, change control, backup/restore, troubleshooting |
| [hybrid-identity.md](hybrid-identity.md) | Microsoft Entra Connect Sync / Cloud Sync: readiness, staging mode, filtering, PHS, upgrades, DR |
| [incident-playbooks.md](incident-playbooks.md) | DC down, replication failure, DNS outage, bad GPO, sync stopped, mass deletion, account lockouts |
| [evidence-template.md](evidence-template.md) | What to capture when a runbook is eventually executed |

Every runbook has the same sections: Purpose, Scope, Preconditions, Procedure, Verification, Rollback, Evidence. Execution gates are in [`operations/hybrid/change-gates.md`](../../../operations/hybrid/change-gates.md); status per runbook is in [`operations/hybrid/EXECUTION_STATUS.md`](../../../operations/hybrid/EXECUTION_STATUS.md).
