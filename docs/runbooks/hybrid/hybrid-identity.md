# Runbook: Hybrid identity (Microsoft Entra Connect Sync / Cloud Sync)

> **Execution status: NOT_EXECUTED.** No authorized AD forest or Microsoft Entra tenant was available. Commands are a plan; output has not been observed. Tenant names are placeholders (`<tenant>.onmicrosoft.com`, UPN suffix `banklab.example`).

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Operate local Windows directory services and their connections to cloud identity. Separating directory, name-resolution, policy, and synchronization problems avoids broad changes that obscure the cause.

For example: A user can reach a server by address but not by name, so an operator investigates name resolution before changing account permissions.

Key terms: **AD DS** means active Directory Domain Services: a directory used to manage Windows identities and resources. **DNS** means domain Name System: translates names into resource-location information. **GPO** means group Policy Object: a set of Windows policy settings. **Hybrid identity** means identity management spanning local directory systems and cloud services.

**Before using this reference:** Directory, DNS, policy, and synchronization changes can affect many users. Use the documented permissions and change gates; no live execution is implied.

Start with the [plain-English learning path](../../knowledge/identity.md) or [glossary](../../knowledge/glossary.md). [Current integration and review policy](../../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->



## Purpose
Synchronize identities from `corp.banklab.example` to Microsoft Entra ID safely: readiness, install, scoping, upgrades, monitoring and recovery.

## Scope
Microsoft Entra Connect Sync (server-based) **or** Microsoft Entra Cloud Sync (lightweight agents); password hash sync (PHS) as the sign-in method, optionally with Seamless SSO. Out of scope: AD FS federation, device writeback design, Conditional Access (see `identity/entra/` on the integration branch).

## Preconditions
- Gates G1–G8 met. Sync servers and agents are **Tier 0** assets: PAW-only admin, two-person rule, no other roles on the host.
- Decision recorded: Cloud Sync (preferred where its feature set is enough: multi-forest disconnected, simpler HA) vs Connect Sync (needed for e.g. device writeback, complex attribute flows, large directories).
- UPN suffix `banklab.example` added in AD and verified in the tenant; users' UPNs match it.
- **IdFix** run against in-scope OUs; duplicates and invalid characters in `proxyAddresses`, `userPrincipalName`, `mail` fixed.
- Sync service account / gMSA created per vendor guidance; cloud side uses a dedicated account or the built-in provisioning identity, never a personal admin.
- Hybrid Identity Administrator role (least privilege) assigned to the operator for the window only (PIM).
- Current Connect configuration exported (Connect Sync: the wizard's *View or export current configuration*), and the sync server's install version recorded. Use only a currently supported Connect version.

## Procedure

### A. Scoping
- Sync `OU=Users` and `OU=Groups` under each tier as required; **exclude** `Tier0`, `ServiceAccounts`, `Quarantine`. Admin accounts are cloud-only, not synced.
- Source anchor: `ms-DS-ConsistencyGuid` (default for new installs).

### B. Install (Connect Sync, primary + staging)
1. Install on `SYNC01` with custom settings: PHS, OU filtering per A, accidental-deletion prevention on.
2. Install on `SYNC02` with the same config and **staging mode enabled** (it imports and syncs but does not export).
3. Keep the deletion threshold enabled (default 500 objects; lower for a small lab):
   ```powershell
   Import-Module ADSync
   Enable-ADSyncExportDeletionThreshold -DeletionThreshold 100
   ```

### B'. Install (Cloud Sync)
1. Install the provisioning agent on two member servers (HA); configure in the Entra admin center: scope by OU, PHS on, accidental-deletion prevention with a threshold.
2. Use *Provision on demand* for one pilot user before enabling the configuration.

### C. Routine operations (Connect Sync)
```powershell
Get-ADSyncScheduler                         # SyncCycleEnabled, StagingModeEnabled, NextSyncCycleStartTimeInUTC
Get-ADSyncConnectorRunStatus                # is a run in progress?
Start-ADSyncSyncCycle -PolicyType Delta     # after a small, reviewed change
```
Before any configuration change, pause the scheduler and resume after:
```powershell
Set-ADSyncScheduler -SyncCycleEnabled $false
# ... change, then preview on the staging server (section D) ...
Set-ADSyncScheduler -SyncCycleEnabled $true
```

### D. Change preview with staging mode
1. Apply the change on `SYNC02` (staging) first; run full import + full sync there.
2. Export pending changes for the Entra connector and analyse them:
   ```
   csexport "<tenant>.onmicrosoft.com - AAD" %temp%\export.xml /f:x
   CSExportAnalyzer %temp%\export.xml > %temp%\export.csv
   ```
3. Review adds/updates/deletes; only if expected, apply the same change on `SYNC01`.

### E. Upgrade / swing migration
Upgrade the staging server first (or build a new one), verify with D, then switch roles: enable staging mode on the active server, disable it on the upgraded one, run a delta cycle, watch exports.

### F. Monitoring
- Microsoft Entra Connect Health (Connect Sync) or the Cloud Sync agent status and provisioning logs.
- Alerts: no successful sync for > 3 h, export errors, deletion threshold hit, PHS heartbeat missing.
- If Seamless SSO is used, roll the `AZUREADSSO` computer account Kerberos key at least every 30 days per vendor guidance.

## Verification
- `Get-ADSyncScheduler`: `SyncCycleEnabled = True` on the active server, `StagingModeEnabled = True` on the standby only.
- Pilot user: exists in Entra ID with `onPremisesSyncEnabled = true`, correct UPN, can sign in with the AD password (PHS).
- Provisioning or Connect Health: last sync successful, 0 export errors, no unexpected deletes.
- Excluded OUs (Tier0, ServiceAccounts) have **no** objects in the tenant.

## Rollback
- Bad scoping or rule change: pause scheduler, revert the change on the active server from the exported configuration, preview on staging, resume.
- Active server failed: promote the staging server (disable staging mode, run a delta sync), then rebuild the failed one in staging mode.
- Deletion threshold hit: **do not** disable the threshold blindly. Investigate; if deletes are wrong, fix scope and run a full sync; if right, `Disable-ADSyncExportDeletionThreshold` for one export, then re-enable it.
- Wrongly deleted cloud objects: restore from Entra ID *Deleted users* (soft-delete, 30 days) after fixing the source.

## Evidence
IdFix summary, scheduler output from both servers, staging export analysis, pilot user screenshots (redacted), health/provisioning log export. Use [evidence-template.md](evidence-template.md).
