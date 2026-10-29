# Runbook: DNS (AD-integrated)

> **Execution status: NOT_EXECUTED.** No authorized DNS environment was available. Commands are a plan; output has not been observed.

## Purpose
Operate Windows DNS on the DCs so AD, clients and hybrid workloads resolve names reliably.

## Scope
AD-integrated primary zones, reverse zones, forwarders, conditional forwarders to cloud private DNS (e.g. an Azure DNS Private Resolver inbound endpoint), aging/scavenging, client settings. Out of scope: public/external DNS hosting.

## Preconditions
- Gates G1–G8 met; DNS changes on forest-wide zones need the two-person rule.
- Current zone export taken: `Export-DnsServerZone -Name corp.banklab.example -FileName corp.banklab.example.bak` (file lands in `%windir%\System32\dns`).
- Known IPs of upstream resolvers and cloud resolver endpoints (synthetic: `192.0.2.100`, `192.0.2.101`).

## Procedure
1. **Inventory:**
   ```powershell
   Get-DnsServerZone | Select ZoneName,ZoneType,IsDsIntegrated,ReplicationScope,DynamicUpdate
   Get-DnsServerForwarder
   Get-DnsServerScavenging
   ```
2. **Zones:** forward zone `corp.banklab.example` replicated to `Forest` scope for `_msdcs`, `Domain` scope for the domain zone; dynamic updates `Secure` only. Reverse zone:
   ```powershell
   Add-DnsServerPrimaryZone -NetworkId '192.0.2.0/24' -ReplicationScope Domain -DynamicUpdate Secure -WhatIf
   ```
3. **Forwarders:** use the lab's approved resolvers; do not point DCs at each other's forwarders in loops.
   ```powershell
   Set-DnsServerForwarder -IPAddress 192.0.2.100,192.0.2.101 -UseRootHint $false -WhatIf
   ```
4. **Conditional forwarders for cloud private zones** (replicate to all DNS servers in the forest):
   ```powershell
   Add-DnsServerConditionalForwarderZone -Name 'privatelink.database.windows.net' `
     -MasterServers 192.0.2.100 -ReplicationScope Forest -WhatIf
   ```
   In the cloud, the reverse direction (cloud → on-prem) uses a forwarding ruleset for `corp.banklab.example` pointing to the DC IPs.
5. **Aging and scavenging:** enable on the zone, enable scavenging on **one** DC only, 7-day no-refresh + 7-day refresh. Run a report-only pass first by reviewing stale timestamps.
   ```powershell
   Set-DnsServerZoneAging -Name corp.banklab.example -Aging $true -NoRefreshInterval 7.00:00:00 -RefreshInterval 7.00:00:00 -WhatIf
   Set-DnsServerScavenging -ComputerName DC01 -ScavengingState $true -ScavengingInterval 7.00:00:00 -WhatIf
   ```
6. **Clients:** DHCP/static settings hand out DC IPs only (at least two, nearest site first).

## Verification
Test matrix from a member server and from a cloud VM:
```powershell
Resolve-DnsName corp.banklab.example
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.corp.banklab.example
Resolve-DnsName dc01.corp.banklab.example -Server 192.0.2.11
Resolve-DnsName example.com
dcdiag /test:dns /v /e
```
Expected: SRV records for every DC, external names resolve via forwarders, cloud private names resolve to private IPs.

## Rollback
- Bad forwarder: restore previous values from step 1 output with `Set-DnsServerForwarder`.
- Bad conditional forwarder: `Remove-DnsServerZone -Name <zone> -Force` (it is a forwarder zone, not data).
- Over-aggressive scavenging deleted records: re-register (`ipconfig /registerdns`, `nltest /dsregdns` on DCs, `net stop netlogon && net start netlogon`), or restore the zone from the step-0 export or an AD authoritative restore of the zone partition.

## Evidence
Step 1 inventory before/after, verification matrix with results, `dcdiag /test:dns` output. Use [evidence-template.md](evidence-template.md).
