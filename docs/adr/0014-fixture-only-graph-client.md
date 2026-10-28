# 0014: Identity governance runs on fixtures; Graph client has no network transport
- Status: **Proposed.** #18 is an open draft, not integrated in #7.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- `identity-governance@f48e7e3:identity/governance/graph_client.py` ships only `FixtureTransport`. 401 and 403 fail closed (`identity/governance/README.md`).
- `identity/governance/inventory.py` (pim and free modes) and the PIM and access-review lifecycle docs (`identity/governance/docs/`) work from committed fixtures, with `make_fixtures.py --check` for drift.
- Federation (Entra to IAM Identity Center via SAML and SCIM) is **documentation only**: `docs/federation/entra-to-aws-iam-identity-center.md` and `saml-vs-scim.md`.

## Consequences
- No tenant credentials are needed and no tenant data can leak. Nothing proves behaviour against a real tenant.
- Verified here: 65 tests OK, no drift, evidence OK (R11). Federation is unexecuted.
