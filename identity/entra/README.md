# Entra ID Conditional Access -- offline baseline and validator

> **Offline / synthetic only.** Nothing in this directory talks to Microsoft Entra ID or
> Microsoft Graph, reads credentials, or describes a real tenant. Object IDs for users,
> groups and policies are synthetic lab GUIDs. The only real-world constants are the
> Entra built-in role template IDs and the built-in authentication-strength IDs.

## Layout

| Path | Purpose |
|---|---|
| `policies/*.json` | Bank CA baseline, one Graph `conditionalAccessPolicy` object per file |
| `baseline.json` | Bank rules input: break-glass accounts, privileged role template IDs, auth-strength IDs, rollout flags |
| `ca_validator.py` | Python 3 stdlib validator (schema + baseline rules), fail-closed |

### Policies

| File | State | Users | Grant |
|---|---|---|---|
| CA001 Block legacy authentication | enabled | All (break-glass excluded) | block on `exchangeActiveSync` + `other` |
| CA002 Require MFA | enabled | All (break-glass excluded) | `mfa` (AND) |
| CA003 Admin phishing-resistant MFA | enabled | 12 privileged role templates | authenticationStrength `...0004` (phishing-resistant) |
| CA004 Require compliant device | enabled | All (break-glass excluded), all platforms | `compliantDevice` (AND) |
| CA005 Block high sign-in risk | report-only | All (break-glass excluded) | block |
| CA006 High user risk -> password change | report-only | All (break-glass excluded) | `mfa` AND `passwordChange`, sign-in frequency every time |
| CA007 Block admin portals off trusted locations | enabled | privileged roles | block on `MicrosoftAdminPortals` outside `AllTrusted` |

## Rules

| ID | Rule |
|---|---|
| SCHEMA-001 | Input parses as strict JSON (no duplicate keys, no NaN/Infinity), set non-empty, baseline well-formed |
| SCHEMA-002 | Policy object shape: required keys, no unknown keys, types |
| SCHEMA-003 | `state` in `enabled` / `disabled` / `enabledForReportingButNotEnforced` |
| SCHEMA-004 | `conditions` well-formed: known keys, GUID-or-keyword IDs, known clientAppTypes / platforms / risk levels, an include target |
| SCHEMA-005 | `grantControls` well-formed: `AND`/`OR`, known controls, `block` exclusive, `mfa` not combined with authenticationStrength, at least one control |
| SCHEMA-006 | Unique policy `id` and `displayName` |
| BASE-001 | Break-glass accounts excluded from every policy and never explicitly included |
| BASE-002 | Enabled policy blocks legacy auth (`exchangeActiveSync`, `other`) for All users / All apps |
| BASE-003 | Enabled policy requires MFA for All users / All apps, AND semantics, only break-glass excluded, not narrowed by location/platform/risk |
| BASE-004 | Every privileged role is covered by an enabled phishing-resistant MFA policy with no role exclusions |
| BASE-005 | No policy blocks All users without exclusions |
| BASE-006 | Enabled policy requires `compliantDevice` for All users / All apps (an `OR` with a non-device control fails) |
| BASE-007 | Risk-based policies are report-only while `riskPoliciesMustBeReportOnly` is true |

Report-only and disabled policies never satisfy BASE-002/003/004/006.

## Usage

```bash
python3 identity/entra/ca_validator.py                       # validate policies/ against baseline.json
python3 identity/entra/ca_validator.py path/to/export.json   # a single policy, a list, or Graph {"value": [...]}
python3 identity/entra/ca_validator.py --json-out r.json --md-out r.md --quiet
```

Exit codes: `0` all rules PASS, `1` baseline FAIL, `2` malformed/unknown input (fail-closed; baseline
rules are reported `NOT_EVALUATED`).

Tests: `python3 -m unittest discover -s tests/entra -v` (see `tests/entra/README.md`).
Evidence: `python3 evidence/entra/generate_evidence.py` (see `evidence/entra/README.md`).
