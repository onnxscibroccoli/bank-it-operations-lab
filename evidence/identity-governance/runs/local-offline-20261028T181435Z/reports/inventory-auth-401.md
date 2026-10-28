# Privileged role assignment inventory -- scenario `auth-401`

> **OFFLINE / SYNTHETIC. Generated from local Microsoft Graph-shaped JSON fixtures. No tenant, Microsoft Graph API call or credential was used; nothing here describes any real tenant.**

| Field | Value |
|---|---|
| Mode | `pim` |
| As of (UTC) | 2026-10-28T12:00:00Z |
| Overall | **ERROR** (exit 2) |
| Graph requests (fixture) | 1 requests, 0 pages, 0 retries |

## Error (fail-closed, no inventory produced)

```
{
  "kind": "authorization",
  "status": 401,
  "code": "InvalidAuthenticationToken",
  "requestId": "synthetic-401-InvalidAuthenticationToken",
  "url": "https://graph.microsoft.com/v1.0/roleManagement/directory/roleDefinitions?$select=id,displayName,templateId,isBuiltIn",
  "message": "HTTP 401 InvalidAuthenticationToken: Access token is empty. (synthetic)"
}
```
