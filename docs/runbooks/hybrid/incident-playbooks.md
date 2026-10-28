# Runbook: Hybrid incident playbooks

> **Execution status: NOT_EXECUTED.** None of these playbooks has been exercised, including as a tabletop. Commands are a plan; output has not been observed.

## Purpose
First-response steps for common Windows Server / AD / DNS / GPO / sync incidents, so the on-call engineer can stabilize before escalating.

## Scope
Synthetic `corp.banklab.example` lab. Priorities follow the lab's ticket-priority model. Security-suspected incidents go to the security on-call at once.

## Preconditions
- On-call has PAW access and the Tier 0 break-glass procedure.
- The relevant runbook is open: [active-directory.md](active-directory.md), [dns.md](dns.md), [group-policy.md](group-policy.md), [hybrid-identity.md](hybrid-identity.md).

## Procedure

| Scenario | Detect | First response | Escalate when |
|---|---|---|---|
| DC down | Monitoring, `dcdiag /e /q` | Confirm other DCs serve the site (`nltest /dsgetdc:corp.banklab.example /force`); check FSMO holder; do not seize roles in the first hour | DC holds PDC/RID and cannot return in 4 h |
| Replication failure | `repadmin /replsummary` fails > 0 | `repadmin /showrepl <DC>` for error code; check DNS, time (`w32tm /stripchart`), firewall; `repadmin /syncall /AdeP` after fix | Error 8606/lingering objects or USN rollback suspected |
| DNS outage | Clients cannot resolve SRV records | `Get-Service DNS`; `dcdiag /test:dns`; check forwarders; restart DNS service on one DC at a time | All DCs affected or zone data missing |
| Bad GPO deployed | Spike of tickets after a link change | Disable the new link, re-enable previous version, `Invoke-GPUpdate` to affected OU | Settings tattooed or DCs affected |
| Sync stopped | No successful sync > 3 h | `Get-ADSyncScheduler`, `Get-ADSyncConnectorRunStatus`; check service, network/proxy to Entra endpoints, credentials | Not fixed in 2 h: promote staging server |
| Mass deletion staged | Deletion threshold alert | Leave threshold on; pause scheduler; find cause (OU moved, filter change) | Always notify identity owner before any export |
| Account lockout storm | Event 4740 on PDC emulator | Identify source (`Caller Computer Name`), disable stale credentials/service; check for password spray | Pattern suggests attack: security on-call |
| Suspected Tier 0 compromise | Alert or unexplained admin change | Isolate, preserve logs, do **not** reset krbtgt ad hoc | Immediately: security on-call and incident manager |

## Verification
After each incident: affected health check from the matching runbook is clean, the user impact is confirmed resolved, and the timeline is recorded.

## Rollback
Each first response is reversible: re-enable links, restart services, resume the scheduler. Irreversible actions (FSMO seize, authoritative restore, krbtgt reset, threshold override) need incident-manager approval and the two-person rule.

## Evidence
Timeline, commands run with output, decision points, and the post-incident review. Use [evidence-template.md](evidence-template.md).
