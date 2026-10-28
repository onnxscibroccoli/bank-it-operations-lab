# Privileged role assignment inventory -- scenario `throttled-exhausted`

> **OFFLINE / SYNTHETIC. Generated from local Microsoft Graph-shaped JSON fixtures. No tenant, Microsoft Graph API call or credential was used; nothing here describes any real tenant.**

| Field | Value |
|---|---|
| Mode | `pim` |
| As of (UTC) | 2026-10-28T12:00:00Z |
| Overall | **ERROR** (exit 2) |
| Graph requests (fixture) | 10 requests, 5 pages, 4 retries |

## Error (fail-closed, no inventory produced)

```
{
  "kind": "throttled",
  "status": 429,
  "code": "TooManyRequests",
  "requestId": "synthetic-429-TooManyRequests",
  "url": "https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleInstances",
  "message": "HTTP 429 after 4 retries"
}
```
