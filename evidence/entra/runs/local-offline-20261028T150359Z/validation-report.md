# Entra Conditional Access -- offline validation report

> **OFFLINE / SYNTHETIC: results describe local JSON fixtures only. No Entra ID tenant, Microsoft Graph API or credential was used. This report makes NO claim about the configuration or state of any tenant.**

- **Validated commit:** `e8771c9aa09b3e1c60d87b04cd65a266b673eed8`
- **Run:** `local-offline-20261028T150359Z`
- **Generated (UTC):** `2026-10-28T15:04:00Z`
- **Tool:** `entra-ca-offline-validator 1.0.0`
- **Mode:** `offline-synthetic` (tenantStateClaimed = `false`)
- **Policies input:** `identity/entra/policies` (7 policies)
- **Baseline:** `identity/entra/baseline.json`
- **Overall:** **PASS** (exit code 0)

| Rule | Category | Result | Title |
|---|---|---|---|
| SCHEMA-001 | schema | PASS | Every input file parses as JSON (no duplicate keys) and the policy set is non-empty |
| SCHEMA-002 | schema | PASS | Each policy has the conditionalAccessPolicy shape: required keys present, no unknown keys, correct types |
| SCHEMA-003 | schema | PASS | state is one of enabled \| disabled \| enabledForReportingButNotEnforced |
| SCHEMA-004 | schema | PASS | conditions (users, applications, clientAppTypes, platforms, locations, risk levels) are well-formed with known values |
| SCHEMA-005 | schema | PASS | grantControls well-formed: operator AND\|OR, known builtInControls, block is exclusive, at least one control |
| SCHEMA-006 | schema | PASS | Policy ids and displayNames are unique across the set |
| BASE-001 | baseline | PASS | Break-glass accounts are excluded from every policy (and never explicitly included) |
| BASE-002 | baseline | PASS | Legacy authentication (exchangeActiveSync + other) is blocked for All users on All apps by an enabled policy |
| BASE-003 | baseline | PASS | An enabled policy requires MFA for All users on All apps (AND semantics, only break-glass excluded) |
| BASE-004 | baseline | PASS | All privileged admin roles require phishing-resistant MFA via an enabled policy with no role exclusions |
| BASE-005 | baseline | PASS | No policy blocks All users without exclusions |
| BASE-006 | baseline | PASS | An enabled policy requires a compliant device for All users on All apps |
| BASE-007 | baseline | PASS | Risk-based policies (sign-in / user risk) are report-only during staged rollout |
