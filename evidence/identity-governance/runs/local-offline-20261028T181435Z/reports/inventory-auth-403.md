# Privileged role assignment inventory -- scenario `auth-403`

> **OFFLINE / SYNTHETIC. Generated from local Microsoft Graph-shaped JSON fixtures. No tenant, Microsoft Graph API call or credential was used; nothing here describes any real tenant.**

| Field | Value |
|---|---|
| Mode | `pim` |
| As of (UTC) | 2026-10-28T12:00:00Z |
| Overall | **ERROR** (exit 2) |
| Graph requests (fixture) | 8 requests, 7 pages, 0 retries |

## Error (fail-closed, no inventory produced)

```
{
  "kind": "authorization",
  "status": 403,
  "code": "Authorization_RequestDenied",
  "requestId": "synthetic-403-Authorization_RequestDenied",
  "url": "https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilityScheduleInstances",
  "message": "HTTP 403 Authorization_RequestDenied: Insufficient privileges to complete the operation. (synthetic)"
}
```
