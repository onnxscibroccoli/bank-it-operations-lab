# Privileged role assignment inventory -- scenario `free-tier`

> **OFFLINE / SYNTHETIC. Generated from local Microsoft Graph-shaped JSON fixtures. No tenant, Microsoft Graph API call or credential was used; nothing here describes any real tenant.**

| Field | Value |
|---|---|
| Mode | `free` |
| As of (UTC) | 2026-10-28T12:00:00Z |
| Overall | **PASS** (exit 0) |
| Graph requests (fixture) | 7 requests, 7 pages, 0 retries |

## Summary

| Metric | Value |
|---|---|
| inventoryRows | 7 |
| privilegedRows | 5 |
| activePrivileged | 5 |
| eligiblePrivileged | 0 |
| permanentActivePrivileged | 0 |
| findings | HIGH=0, MEDIUM=0, LOW=0, INFO=1 |

## Findings

| Severity | Rule | Subject | Detail | Record |
|---|---|---|---|---|
| INFO | INV-010 | tenant | roleAssignments has no schedule data; run in 'pim' mode where licensed | `` |

## Privileged inventory

| Role | Tier0 | State | Type | Principal | Kind | Permanent | Ends (UTC) |
|---|---|---|---|---|---|---|---|
| Global Administrator | yes | active | Unknown (free tier) | Avery Admin (synthetic) | user | unknown |  |
| Global Administrator | yes | active | Unknown (free tier) | BG Emergency Access 01 (break-glass) | user | unknown |  |
| Global Administrator | yes | active | Unknown (free tier) | BG Emergency Access 02 (break-glass) | user | unknown |  |
| Helpdesk Administrator |  | active | Unknown (free tier) | Casey Helpdesk (synthetic) | user | unknown |  |
| Security Administrator |  | active | Unknown (free tier) | Blake Security (synthetic) | user | unknown |  |
