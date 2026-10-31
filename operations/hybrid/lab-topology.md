# Synthetic reference topology

> **Execution status: NOT_EXECUTED.** This topology is a design assumption for the runbooks. It has not been built.

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Operate local Windows directory services and their connections to cloud identity. Separating directory, name-resolution, policy, and synchronization problems avoids broad changes that obscure the cause.

For example: A user can reach a server by address but not by name, so an operator investigates name resolution before changing account permissions.

Key terms: **AD DS** means active Directory Domain Services: a directory used to manage Windows identities and resources. **DNS** means domain Name System: translates names into resource-location information. **GPO** means group Policy Object: a set of Windows policy settings. **Hybrid identity** means identity management spanning local directory systems and cloud services.

**Before using this reference:** Directory, DNS, policy, and synchronization changes can affect many users. Use the documented permissions and change gates; no live execution is implied.

Start with the [plain-English learning path](../../docs/knowledge/identity.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->



## Forest and sites

| Item | Value (synthetic) |
|---|---|
| Forest / domain | `corp.banklab.example` (single domain forest) |
| NetBIOS | `BANKLAB` |
| Functional level | Windows Server 2016 or higher (target: highest level all DCs support) |
| Sites | `HQ` (192.0.2.0/26), `DR` (192.0.2.64/26) |
| Domain controllers | `DC01` (HQ, PDC emulator, RID, infrastructure), `DC02` (HQ, schema master, domain naming master), `DC03` (DR) |
| All DCs | Server Core where possible, AD-integrated DNS, Global Catalog |
| Sync server | `SYNC01` (member server, Tier 0), plus `SYNC02` in staging mode, **or** two Cloud Sync agents |
| Tenant | `banklab.example` (synthetic, verified UPN suffix `banklab.example`) |

## OU layout (tiered administration)

```
corp.banklab.example
├── Tier0          (DCs live in the default Domain Controllers OU; Tier0 holds admin accounts, PAWs, SYNC01/02)
│   ├── Accounts
│   ├── Groups
│   └── Devices
├── Tier1          (member servers and their admins)
│   ├── Accounts
│   ├── Groups
│   └── Servers
├── Tier2          (workstations and helpdesk)
│   ├── Accounts
│   ├── Groups
│   └── Workstations
├── Users          (standard staff, in sync scope)
├── ServiceAccounts (gMSA preferred; out of sync scope)
└── Quarantine     (disabled objects pending deletion; out of sync scope)
```

## Assumptions

- Time: PDC emulator syncs to an external NTP source; all other DCs use domain hierarchy.
- Backups: daily system-state backup of at least two DCs, kept offline/immutable, 30-day retention.
- Admin access only from privileged access workstations (PAWs); no internet browsing from Tier 0.
- Windows LAPS manages local administrator passwords on Tier 1 and Tier 2.
