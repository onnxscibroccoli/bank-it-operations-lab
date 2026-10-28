# Runbook: Windows Server baseline

> **Execution status: NOT_EXECUTED.** No authorized Windows Server environment was available. Commands are a plan; output has not been observed.

## Purpose
Build and keep Windows Server hosts (DCs, sync servers, member servers) in a known, hardened, patched state.

## Scope
Windows Server 2022/2025 in the synthetic `corp.banklab.example` lab. Server Core preferred for DCs. Out of scope: application-specific hardening.

## Preconditions
- Gates G1–G8 in [`change-gates.md`](../../../operations/hybrid/change-gates.md) met.
- Supported install media with verified hash; licence handled by the lab owner.
- Target security baseline chosen (Microsoft Security Baseline for the server version, or CIS benchmark) and its GPO backup available for import.
- Static IP plan from [`lab-topology.md`](../../../operations/hybrid/lab-topology.md).

## Procedure
1. **Install and name.** Install the OS, then set name, IP and DNS (DNS points to DCs, never to a public resolver on domain members):
   ```powershell
   Rename-Computer -NewName 'SRV01' -Restart
   New-NetIPAddress -InterfaceAlias 'Ethernet' -IPAddress 192.0.2.20 -PrefixLength 26 -DefaultGateway 192.0.2.1
   Set-DnsClientServerAddress -InterfaceAlias 'Ethernet' -ServerAddresses 192.0.2.10,192.0.2.11
   ```
2. **Patch** to the current cumulative update before joining (WSUS / Windows Update / Azure Update Manager per lab design). Record `Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5`.
3. **Join the domain** into the correct tiered OU (not the default `Computers` container):
   ```powershell
   Add-Computer -DomainName corp.banklab.example -OUPath 'OU=Servers,OU=Tier1,DC=corp,DC=banklab,DC=example' -Restart
   ```
4. **Apply baseline** through GPO (preferred, see [group-policy.md](group-policy.md)), not by local edits. Confirm with `gpresult /r /scope computer`.
5. **Harden:** remove unused roles/features (`Get-WindowsFeature | Where-Object Installed`), disable SMBv1 (`Get-SmbServerConfiguration | Select EnableSMB1Protocol` should be `False`), keep Windows Firewall on for all profiles, enable Defender (`Get-MpComputerStatus`), confirm Windows LAPS policy applies.
6. **Logging:** set Security log size per baseline, enable advanced audit policy via GPO, forward events to the lab collector.
7. **Monthly patching:** pilot ring (1 host per role) → wait 48 h → broad ring. For DCs, patch one DC at a time and run the AD health checks between hosts.

## Verification
- `Get-ComputerInfo -Property OsName,OsVersion,CsDomain` shows expected values.
- `Get-NetFirewallProfile | Select Name,Enabled` all `True`.
- `Get-MpComputerStatus | Select AMServiceEnabled,RealTimeProtectionEnabled` both `True`.
- `gpresult /r /scope computer` lists the baseline GPOs.
- No pending reboot after patching; host reports to monitoring.

## Rollback
- Failed cumulative update: uninstall by KB via `wusa /uninstall /kb:<number>` or roll back from the pre-change snapshot (lab VMs only; never snapshot-revert a DC, see [active-directory.md](active-directory.md)).
- Baseline breaks an app: unlink or security-filter the GPO for that host, then raise an exception record. Do not edit the baseline GPO in place.

## Evidence
Use [evidence-template.md](evidence-template.md): build record, outputs of the verification commands, patch list, baseline GPO report.
