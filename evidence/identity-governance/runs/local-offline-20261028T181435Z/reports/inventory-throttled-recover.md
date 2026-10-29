# Privileged role assignment inventory -- scenario `throttled-recover`

> **OFFLINE / SYNTHETIC. Generated from local Microsoft Graph-shaped JSON fixtures. No tenant, Microsoft Graph API call or credential was used; nothing here describes any real tenant.**

| Field | Value |
|---|---|
| Mode | `pim` |
| As of (UTC) | 2026-10-28T12:00:00Z |
| Overall | **PASS** (exit 0) |
| Graph requests (fixture) | 13 requests, 10 pages, 3 retries |

## Summary

| Metric | Value |
|---|---|
| inventoryRows | 16 |
| privilegedRows | 14 |
| activePrivileged | 6 |
| eligiblePrivileged | 8 |
| permanentActivePrivileged | 2 |
| findings | HIGH=0, MEDIUM=0, LOW=0, INFO=0 |

## Findings

| Severity | Rule | Subject | Detail | Record |
|---|---|---|---|---|
| - | - | - | none | - |

## Privileged inventory

| Role | Tier0 | State | Type | Principal | Kind | Permanent | Ends (UTC) |
|---|---|---|---|---|---|---|---|
| Global Administrator | yes | active | Activated | Avery Admin (synthetic) | user | no | 2026-10-28T13:00:00Z |
| Global Administrator | yes | active | Assigned | BG Emergency Access 01 (break-glass) | user | yes |  |
| Global Administrator | yes | active | Assigned | BG Emergency Access 02 (break-glass) | user | yes |  |
| Global Administrator | yes | eligible | Eligible | Avery Admin (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Privileged Authentication Administrator | yes | eligible | Eligible | Emery Identity (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Privileged Role Administrator | yes | eligible | Eligible | Avery Admin (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Application Administrator |  | eligible | Eligible | Devon Apps (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Conditional Access Administrator |  | eligible | Eligible | Emery Identity (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Exchange Administrator |  | eligible | Eligible | Finley Messaging (synthetic) | user | no | 2027-04-30T23:59:59Z |
| Helpdesk Administrator |  | active | Assigned | Casey Helpdesk (synthetic) | user | no | 2027-01-31T23:59:59Z |
| Security Administrator |  | active | Activated | Blake Security (synthetic) | user | no | 2026-10-28T18:00:00Z |
| Security Administrator |  | active | Assigned | grp-role-security-operators (synthetic) | group | no | 2027-04-30T23:59:59Z |
| Security Administrator |  | eligible | Eligible | Blake Security (synthetic) | user | no | 2027-04-30T23:59:59Z |
| User Administrator |  | eligible | Eligible | Casey Helpdesk (synthetic) | user | no | 2027-04-30T23:59:59Z |
