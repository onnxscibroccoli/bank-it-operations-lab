# Privileged role assignment inventory -- scenario `findings`

> **OFFLINE / SYNTHETIC. Generated from local Microsoft Graph-shaped JSON fixtures. No tenant, Microsoft Graph API call or credential was used; nothing here describes any real tenant.**

| Field | Value |
|---|---|
| Mode | `pim` |
| As of (UTC) | 2026-10-28T12:00:00Z |
| Overall | **FINDINGS** (exit 1) |
| Graph requests (fixture) | 10 requests, 10 pages, 0 retries |

## Summary

| Metric | Value |
|---|---|
| inventoryRows | 22 |
| privilegedRows | 20 |
| activePrivileged | 10 |
| eligiblePrivileged | 10 |
| permanentActivePrivileged | 5 |
| findings | HIGH=8, MEDIUM=4, LOW=1, INFO=0 |

## Findings

| Severity | Rule | Subject | Detail | Record |
|---|---|---|---|---|
| HIGH | INV-001 | Devon Apps (synthetic) | permanent Assigned Global Administrator | `rasi-b9a5e000-0000-4000-8000-000000000212` |
| HIGH | INV-001 | Emery Identity (synthetic) | permanent Assigned Global Administrator | `rasi-b9a5e000-0000-4000-8000-000000000213` |
| HIGH | INV-001 | Finley Messaging (synthetic) | permanent Assigned Global Administrator | `rasi-b9a5e000-0000-4000-8000-000000000211` |
| HIGH | INV-001 | svc-legacy-automation (synthetic) | permanent Assigned Privileged Role Administrator | `rasi-b9a5e000-0000-4000-8000-000000000215` |
| HIGH | INV-002 | Global Administrator | 5 active principals > 4 | `` |
| HIGH | INV-004 | Partner Consultant (synthetic guest) | active Security Administrator | `rasi-b9a5e000-0000-4000-8000-000000000214` |
| HIGH | INV-005 | svc-legacy-automation (synthetic) | active Privileged Role Administrator | `rasi-b9a5e000-0000-4000-8000-000000000215` |
| HIGH | INV-007 | b9a5e000-0000-4000-8000-000000000002 | no permanent active Global Administrator assignment found | `` |
| MEDIUM | INV-003 | rasi-b9a5e000-0000-4000-8000-000000000216 | active Exchange Administrator ended 2026-10-01T00:00:00Z (asOf 2026-10-28T12:00:00Z) | `rasi-b9a5e000-0000-4000-8000-000000000216` |
| MEDIUM | INV-003 | resi-b9a5e000-0000-4000-8000-000000000313 | eligible Conditional Access Administrator ended 2026-09-30T23:59:59Z (asOf 2026-10-28T12:00:00Z) | `resi-b9a5e000-0000-4000-8000-000000000313` |
| MEDIUM | INV-006 | Blake Security (synthetic) | Security Administrator activation 24.0h > 8h | `rasi-b9a5e000-0000-4000-8000-000000000217` |
| MEDIUM | INV-008 | b9a5e000-0000-4000-8000-000000000099 | eligible on User Administrator | `resi-b9a5e000-0000-4000-8000-000000000311` |
| LOW | INV-009 | Harper Former (synthetic) | eligible Exchange Administrator on disabled account | `resi-b9a5e000-0000-4000-8000-000000000312` |

## Privileged inventory

| Role | Tier0 | State | Type | Principal | Kind | Permanent | Ends (UTC) |
|---|---|---|---|---|---|---|---|
| Global Administrator | yes | active | Activated | Avery Admin (synthetic) | user | no | 2026-10-28T13:00:00Z |
| Global Administrator | yes | active | Assigned | BG Emergency Access 01 (break-glass) | user | yes |  |
| Global Administrator | yes | active | Assigned | Devon Apps (synthetic) | user | yes |  |
| Global Administrator | yes | active | Assigned | Emery Identity (synthetic) | user | yes |  |
| Global Administrator | yes | active | Assigned | Finley Messaging (synthetic) | user | yes |  |
| Global Administrator | yes | eligible | Eligible | Avery Admin (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Privileged Authentication Administrator | yes | eligible | Eligible | Emery Identity (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Privileged Role Administrator | yes | active | Assigned | svc-legacy-automation (synthetic) | servicePrincipal | yes |  |
| Privileged Role Administrator | yes | eligible | Eligible | Avery Admin (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Application Administrator |  | eligible | Eligible | Devon Apps (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Conditional Access Administrator |  | eligible | Eligible | Emery Identity (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Exchange Administrator |  | eligible | Eligible | Finley Messaging (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Exchange Administrator |  | eligible | Eligible | Harper Former (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Helpdesk Administrator |  | active | Assigned | Casey Helpdesk (synthetic) | user | no | 2027-01-31T23:59:59Z |
| Security Administrator |  | active | Activated | Blake Security (synthetic) | user | no | 2026-10-29T06:00:00Z |
| Security Administrator |  | active | Assigned | Partner Consultant (synthetic guest) | user | no | 2026-12-31T00:00:00Z |
| Security Administrator |  | active | Assigned | grp-role-security-operators (synthetic) | group | no | 2027-04-30T23:59:59Z |
| Security Administrator |  | eligible | Eligible | Blake Security (synthetic) | user | no | 2027-04-30T23:59:59Z |
| User Administrator |  | eligible | Eligible | b9a5e000-0000-4000-8000-000000000099 | unresolved | no | 2027-04-30T23:59:59Z |
| User Administrator |  | eligible | Eligible | Casey Helpdesk (synthetic) | user | no | 2027-04-30T23:59:59Z |
