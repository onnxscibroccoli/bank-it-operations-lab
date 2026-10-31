# Privileged role assignment inventory -- scenario `missing-fields`

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
| inventoryRows | 14 |
| privilegedRows | 14 |
| activePrivileged | 6 |
| eligiblePrivileged | 8 |
| permanentActivePrivileged | 4 |
| findings | HIGH=2, MEDIUM=4, LOW=3, INFO=0 |

## Findings

| Severity | Rule | Subject | Detail | Record |
|---|---|---|---|---|
| HIGH | INV-001 | Emery Identity (synthetic) | permanent Assigned Conditional Access Administrator | `rasi-b9a5e000-0000-4000-8000-000000000225` |
| HIGH | INV-001 | b9a5e000-0000-4000-8000-000000000016 | permanent Assigned UNKNOWN | `rasi-b9a5e000-0000-4000-8000-000000000227` |
| MEDIUM | DQ-001 | record | active record missing id | `` |
| MEDIUM | DQ-001 | record | active record missing principalId | `rasi-b9a5e000-0000-4000-8000-000000000221` |
| MEDIUM | DQ-001 | record | active record missing roleDefinitionId | `rasi-b9a5e000-0000-4000-8000-000000000222` |
| MEDIUM | DQ-003 | b9a5e000-0000-4000-8000-00000000dead | unknown role definition; treated as privileged | `rasi-b9a5e000-0000-4000-8000-000000000227` |
| LOW | DQ-002 | rasi-b9a5e000-0000-4000-8000-000000000224 | startDateTime missing | `rasi-b9a5e000-0000-4000-8000-000000000224` |
| LOW | DQ-002 | rasi-b9a5e000-0000-4000-8000-000000000225 | bad timestamp (Invalid isoformat string: 'not-a-date'); treated as permanent | `rasi-b9a5e000-0000-4000-8000-000000000225` |
| LOW | DQ-002 | rasi-b9a5e000-0000-4000-8000-000000000226 | assignmentType None unknown; treated as Assigned | `rasi-b9a5e000-0000-4000-8000-000000000226` |

## Privileged inventory

| Role | Tier0 | State | Type | Principal | Kind | Permanent | Ends (UTC) |
|---|---|---|---|---|---|---|---|
| Global Administrator | yes | active | Assigned | BG Emergency Access 01 (break-glass) | user | yes |  |
| Global Administrator | yes | active | Assigned | BG Emergency Access 02 (break-glass) | user | yes |  |
| Global Administrator | yes | eligible | Eligible | Avery Admin (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Privileged Authentication Administrator | yes | eligible | Eligible | Emery Identity (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Privileged Role Administrator | yes | eligible | Eligible | Avery Admin (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Application Administrator |  | active | Assigned | Devon Apps (synthetic) | user | no | 2027-01-01T00:00:00Z |
| Application Administrator |  | eligible | Eligible | Devon Apps (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Conditional Access Administrator |  | active | Assigned | Emery Identity (synthetic) | user | yes |  |
| Conditional Access Administrator |  | eligible | Eligible | Emery Identity (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Exchange Administrator |  | active | Assigned | Finley Messaging (synthetic) | user | no | 2027-01-01T00:00:00Z |
| Exchange Administrator |  | eligible | Eligible | Finley Messaging (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Security Administrator |  | eligible | Eligible | Blake Security (synthetic) | user | no | 2027-04-30T23:59:59Z |
| UNKNOWN |  | active | Assigned | b9a5e000-0000-4000-8000-000000000016 | user | yes |  |
| User Administrator |  | eligible | Eligible | Casey Helpdesk (synthetic) | user | no | 2027-04-30T23:59:59Z |
