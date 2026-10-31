# Runbook: Group Policy

> **Execution status: NOT_EXECUTED.** No authorized AD / Group Policy environment was available. Commands are a plan; output has not been observed.

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Operate local Windows directory services and their connections to cloud identity. Separating directory, name-resolution, policy, and synchronization problems avoids broad changes that obscure the cause.

For example: A user can reach a server by address but not by name, so an operator investigates name resolution before changing account permissions.

Key terms: **AD DS** means active Directory Domain Services: a directory used to manage Windows identities and resources. **DNS** means domain Name System: translates names into resource-location information. **GPO** means group Policy Object: a set of Windows policy settings. **Hybrid identity** means identity management spanning local directory systems and cloud services.

**Before using this reference:** Directory, DNS, policy, and synchronization changes can affect many users. Use the documented permissions and change gates; no live execution is implied.

Start with the [plain-English learning path](../../knowledge/identity.md) or [glossary](../../knowledge/glossary.md). [Current integration and review policy](../../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->



## Purpose
Change Group Policy safely: design, test, deploy in rings, back up and restore.

## Scope
Domain GPOs for the tiered OU layout in [`lab-topology.md`](../../../operations/hybrid/lab-topology.md): security baselines, Windows LAPS, audit policy, firewall, user settings. Out of scope: Intune/MDM policy (separate runbook).

## Preconditions
- Gates G1–G8 met. Changes to GPOs linked at the domain root or Domain Controllers OU need the two-person rule.
- Central Store present: `\\corp.banklab.example\SYSVOL\corp.banklab.example\Policies\PolicyDefinitions` with current ADMX files.
- SYSVOL replicates with DFSR (check: `dfsrmig /getglobalstate` returns `Eliminated`).
- Full backup taken:
  ```powershell
  $p = "E:\GPOBackup\$(Get-Date -Format yyyyMMdd-HHmm)"; New-Item -ItemType Directory $p | Out-Null
  Backup-GPO -All -Path $p | Select DisplayName,Id,BackupDirectory | Export-Csv "$p\manifest.csv" -NoTypeInformation
  ```

## Procedure
1. **Design rules:** one purpose per GPO; naming `<Tier>-<Scope>-<Purpose>-v<n>` (e.g. `T1-SRV-Baseline-v3`); no edits to `Default Domain Policy` except password/account lockout/Kerberos; no edits to `Default Domain Controllers Policy` except user rights required by baseline.
2. **Change by versioning,** not in-place edit: copy the GPO, change the copy, report it:
   ```powershell
   Copy-GPO -SourceName 'T1-SRV-Baseline-v2' -TargetName 'T1-SRV-Baseline-v3'
   Get-GPOReport -Name 'T1-SRV-Baseline-v3' -ReportType Html -Path .\T1-SRV-Baseline-v3.html
   ```
3. **Pilot ring:** link to a pilot OU or security-filter to a pilot group, then on a pilot host:
   ```powershell
   New-GPLink -Name 'T1-SRV-Baseline-v3' -Target 'OU=Pilot,OU=Servers,OU=Tier1,DC=corp,DC=banklab,DC=example' -WhatIf
   gpupdate /force
   gpresult /h .\pilot-gpresult.html /f
   ```
4. **Broad ring** after 48 h without incidents: link v3 to the production OU and disable the v2 link (keep v2 for rollback for one cycle).
5. **Remote refresh** if needed: `Invoke-GPUpdate -Computer SRV01 -RandomDelayInMinutes 0 -Force`.

## Verification
- `gpresult /r` on pilot and broad hosts lists the new GPO under Applied GPOs.
- Event log `Microsoft-Windows-GroupPolicy/Operational` has no errors after refresh.
- `Get-GPInheritance -Target <OU>` shows the expected link order.
- Settings spot-checked (e.g. `auditpol /get /category:*`, LAPS password present in the directory).

## Rollback
- Fast: disable or remove the new link and re-enable v2 (`Set-GPLink -Name 'T1-SRV-Baseline-v2' -Target <OU> -LinkEnabled Yes`), then `gpupdate /force` on affected hosts.
- Corrupted or bad edits to an existing GPO: `Restore-GPO -Name '<name>' -Path <backup path>` (restores settings, not links).
- Some settings "tattoo" (registry values outside Policies keys); the backout must set them explicitly.

## Evidence
Backup manifest, HTML reports before/after, pilot `gpresult`, link state output. Use [evidence-template.md](evidence-template.md).
