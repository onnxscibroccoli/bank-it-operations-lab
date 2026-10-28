# Privileged role assignment inventory -- scenario `malformed-page`

> **OFFLINE / SYNTHETIC. Generated from local Microsoft Graph-shaped JSON fixtures. No tenant, Microsoft Graph API call or credential was used; nothing here describes any real tenant.**

| Field | Value |
|---|---|
| Mode | `pim` |
| As of (UTC) | 2026-10-28T12:00:00Z |
| Overall | **ERROR** (exit 2) |
| Graph requests (fixture) | 2 requests, 2 pages, 0 retries |

## Error (fail-closed, no inventory produced)

```
{
  "kind": "response",
  "status": null,
  "code": null,
  "requestId": null,
  "url": "https://graph.microsoft.com/v1.0/users?$select=id,displayName,userPrincipalName,userType,accountEnabled",
  "message": "collection page without a 'value' array"
}
```
