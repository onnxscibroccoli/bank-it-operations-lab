# Identity governance -- offline privileged-access inventory, PIM and access-review references

> **Offline / synthetic only.** Nothing in this directory authenticates to Microsoft Entra ID, calls
> Microsoft Graph, reads a credential or describes a real tenant. `graph_client.py` ships **no network
> transport**; the only transport answers from JSON fixtures. All object IDs are synthetic lab GUIDs
> (`b9a5e000-0000-4000-8000-<12 hex>`, the same prefix as `identity/entra` on the `entra-ca-offline`
> branch), the tenant is `bankitlab.example` (RFC 2606 reserved). The only real-world constants are
> Entra built-in role template IDs from the
> [permissions reference](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference).

## Layout

| Path | Purpose |
|---|---|
| `graph_client.py` | Read-only Graph client: `@odata.nextLink` paging, 429/503/504 + `Retry-After` back-off, 401/403 fail-closed, paging-loop guard. Injected transport; `FixtureTransport` only |
| `inventory.py` | Privileged role assignment inventory + findings report (JSON / Markdown / CSV). Modes `pim` (P2/Governance APIs) and `free` (roleAssignments fallback) |
| `access_review.py` | Access-review decision summary (`accessReviewInstanceDecisionItem`) with findings |
| `baseline.json` | Governance rules input: break-glass IDs, privileged + tier-0 role templates, GA maximum, max activation hours |
| `make_fixtures.py` | Deterministic generator for `fixtures/graph/scenarios/`; `--check` fails on drift |
| `fixtures/graph/scenarios/<name>/` | `routes.json` (Graph path -> ordered responses, optional `inherit`) + page bodies |
| `tests/` | `unittest` suite (stdlib only, mocked/fixture transports) |
| `docs/pim-lifecycle.md` | PIM eligible -> activate -> expire -> review lifecycle reference |
| `docs/access-review-lifecycle.md` | Access review define -> review -> apply -> evidence lifecycle reference |
| `docs/emergency-access-break-glass.md` | Break-glass operational flow (prepare, use, post-mortem, validate) |
| `docs/licensing-prerequisites.md` | Licence prerequisites with official Microsoft links and free-tier fallbacks |

Federation docs live in [`docs/federation/`](../../docs/federation/README.md); evidence runs in
[`evidence/identity-governance/`](../../evidence/identity-governance/README.md).

## Scenarios

| Scenario | What it models | Expected exit |
|---|---|---|
| `baseline` | 2 break-glass permanent GA, JIT (PIM-activated) admins, eligible assignments, a role-assignable group; collections span multiple pages | 0 |
| `findings` | Seeded violations INV-001..INV-009 (permanent GA, >4 GA, guest admin, tier-0 service principal, expired records, 24 h activation, missing break-glass GA, orphaned principal, disabled account) | 1 |
| `missing-fields` | Records missing `id` / `principalId` / `roleDefinitionId` / `startDateTime`, bad timestamp, null `assignmentType`, unknown role, user without `userType` | 1 |
| `auth-401` | `401 InvalidAuthenticationToken` on first call -- not retried | 2 |
| `auth-403` | `403 Authorization_RequestDenied` on eligibility -- not retried, no partial inventory | 2 |
| `throttled-recover` | `429 Retry-After: 3`, `429 Retry-After: 1`, then 200; `503` without header (exponential fallback) | 0 |
| `throttled-exhausted` | `429 Retry-After: 5` forever -- stops after 4 retries | 2 |
| `paging-loop` | `@odata.nextLink` points at itself | 2 |
| `malformed-page` | 200 page without a `value` array | 2 |
| `free-tier` | Entra ID Free: `roleAssignments` only, PIM API 403 | 0 (INV-010 INFO) |

## Rules

| ID | Severity | Rule |
|---|---|---|
| INV-001 | HIGH | Permanent active privileged assignment outside the break-glass allow-list |
| INV-002 | HIGH | Active Global Administrator principals > `maxGlobalAdministrators` (4; Microsoft recommends [fewer than five](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/best-practices)) |
| INV-003 | MEDIUM | Expired assignment/eligibility still returned; excluded from the effective inventory |
| INV-004 | HIGH | Privileged role held by a guest |
| INV-005 | HIGH | Tier-0 role (GA, Privileged Role Admin, Privileged Authentication Admin) held by a service principal |
| INV-006 | MEDIUM | Activation window > `maxActivationHours` (8) |
| INV-007 | HIGH | Break-glass account lacks permanent active GA ([Microsoft guidance](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access)) |
| INV-008 | MEDIUM | Principal not resolvable (orphaned/deleted) |
| INV-009 | LOW | Privileged assignment on a disabled account |
| INV-010 | INFO | Free-tier mode: no PIM data |
| DQ-001 / DQ-002 / DQ-003 | MEDIUM / LOW / MEDIUM | Missing required field (skipped) / bad or missing timestamp (treated conservatively) / unknown role (treated as privileged) |

Exit codes: `0` no HIGH/MEDIUM findings, `1` HIGH/MEDIUM findings, `2` fetch or input failure
(fail-closed: no partial inventory is produced).

## Usage

```bash
python3 identity/governance/inventory.py --scenario baseline
python3 identity/governance/inventory.py --scenario findings --json-out r.json --md-out r.md --csv-out r.csv --quiet
python3 identity/governance/inventory.py --scenario baseline --as-of 2026-10-28T13:00:00Z   # move the clock
python3 identity/governance/inventory.py --scenario free-tier                               # mode from routes.json
python3 identity/governance/access_review.py --scenario baseline
python3 identity/governance/make_fixtures.py --check
python3 -m unittest discover -s identity/governance/tests -v
```

Graph endpoints modelled (v1.0, read-only): `roleManagement/directory/roleDefinitions`,
[`roleAssignmentScheduleInstances`](https://learn.microsoft.com/en-us/graph/api/rbacapplication-list-roleassignmentscheduleinstances),
[`roleEligibilityScheduleInstances`](https://learn.microsoft.com/en-us/graph/api/rbacapplication-list-roleeligibilityscheduleinstances),
[`roleAssignments`](https://learn.microsoft.com/en-us/graph/api/rbacapplication-list-roleassignments) (free tier),
`users`, `servicePrincipals`, `groups?$filter=isAssignableToRole eq true`,
[`accessReviews/definitions/{id}/instances/{id}/decisions`](https://learn.microsoft.com/en-us/graph/api/accessreviewinstance-list-decisions).
Client behaviour follows Graph [paging](https://learn.microsoft.com/en-us/graph/paging),
[throttling](https://learn.microsoft.com/en-us/graph/throttling) and [errors](https://learn.microsoft.com/en-us/graph/errors).

## Going from synthetic to real (out of scope here)

A real read would need an app registration or managed identity with least-privilege **read**
permissions (for example `RoleManagement.Read.Directory`, `User.Read.All`, `AccessReview.Read.All`;
confirm on each API page above), a tenant licensed for the PIM / access-review APIs (see
[`docs/licensing-prerequisites.md`](docs/licensing-prerequisites.md)), and a transport object with
`get(url) -> Response`. None of that is in this repository, by design.
