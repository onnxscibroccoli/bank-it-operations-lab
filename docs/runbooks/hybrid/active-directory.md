# Runbook: Active Directory Domain Services

> **Execution status: NOT_EXECUTED.** No authorized AD DS environment was available. Commands are a plan; output has not been observed.

## Purpose
Deploy, operate, back up and recover AD DS for the synthetic `corp.banklab.example` forest.

## Scope
DC promotion and demotion, FSMO roles, replication health, system-state backup and restore, AD Recycle Bin, krbtgt rotation, tiered admin model. Out of scope: trusts with other forests, schema extensions for third-party apps.

## Preconditions
- Gates G1–G8 met; Tier 0 two-person rule applies to every step.
- Hosts built per [windows-server-baseline.md](windows-server-baseline.md), static IPs, correct time.
- DSRM password generated and stored in the lab vault (never in this repo).

## Procedure

### A. First DC / new forest (lab build only)
```powershell
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
Install-ADDSForest -DomainName 'corp.banklab.example' -DomainNetbiosName 'BANKLAB' `
  -InstallDns -SafeModeAdministratorPassword (Read-Host -AsSecureString 'DSRM') -WhatIf
```
Remove `-WhatIf` only after review. Then point the DC's DNS client to its partner DC first and itself (loopback) second.

### B. Additional DC
```powershell
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
Install-ADDSDomainController -DomainName 'corp.banklab.example' -SiteName 'HQ' -InstallDns `
  -Credential (Get-Credential) -SafeModeAdministratorPassword (Read-Host -AsSecureString 'DSRM') -WhatIf
```

### C. Daily health check
```powershell
dcdiag /e /q                       # errors only, all DCs
repadmin /replsummary
repadmin /showrepl * /csv > showrepl.csv
netdom query fsmo
Get-ADDomainController -Filter * | Select HostName,Site,IsGlobalCatalog,OperatingSystem
w32tm /monitor
```

### D. FSMO transfer (planned)
```powershell
Move-ADDirectoryServerOperationMasterRole -Identity DC02 -OperationMasterRole PDCEmulator,RIDMaster -WhatIf
```
Seize (`-Force`) only when the old holder is permanently gone and will never return to the network.

### E. Backup
- Daily: `wbadmin start systemstatebackup -backupTarget:E: -quiet` on at least two DCs; copy offline.
- Keep backups younger than the tombstone lifetime (default 180 days); target 30-day retention.
- Quarterly: restore test into an isolated network.

### F. Enable AD Recycle Bin (one-way, forest-wide)
```powershell
Enable-ADOptionalFeature 'Recycle Bin Feature' -Scope ForestOrConfigurationSet -Target 'corp.banklab.example' -WhatIf
```
Restore a deleted object: `Get-ADObject -Filter 'samAccountName -eq "jdoe"' -IncludeDeletedObjects | Restore-ADObject`.

### G. krbtgt rotation
Reset twice, waiting at least the maximum ticket lifetime (default 10 h) **and** full replication between resets. Prefer Microsoft's published reset script in its simulation mode first. During a suspected compromise, follow the incident playbook instead.

### H. Privileged access hygiene
- Domain Admins / Enterprise Admins / Schema Admins empty except break-glass and named Tier 0 admins; Schema Admins empty by default.
- Tier 0 admins in `Protected Users`; admin accounts not mail-enabled and not synced to the cloud.
- Review monthly: `Get-ADGroupMember 'Domain Admins' -Recursive`.

## Verification
- `dcdiag` shows no failed tests; `repadmin /replsummary` shows 0 fails and largest delta below 1 h within a site.
- `netdom query fsmo` matches [`lab-topology.md`](../../../operations/hybrid/lab-topology.md).
- `Get-ADOptionalFeature -Filter 'name -like "Recycle*"'` lists enabled scopes.
- Last successful backup shown by `wbadmin get versions` is less than 24 h old.

## Rollback
- Failed promotion: `Uninstall-ADDSDomainController` (or forced removal plus metadata cleanup with `ntdsutil` / ADUC) and remove stale DNS records.
- Bad FSMO transfer: transfer back with the same cmdlet.
- Deleted objects: Recycle Bin restore; if not enabled, authoritative restore: boot DC into DSRM, restore system state, `ntdsutil "activate instance ntds" "authoritative restore" "restore subtree <DN>"`, reboot normally.
- **Never** revert a DC from a VM snapshot outside VM-GenerationID-aware platforms; it causes USN rollback.

## Evidence
Outputs of section C before and after, FSMO list, backup log, restore-test record, group membership review. Use [evidence-template.md](evidence-template.md).
