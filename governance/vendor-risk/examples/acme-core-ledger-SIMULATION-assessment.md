# SIMULATION — Vendor Risk Assessment: Acme Core Ledger SIMULATION

> **SIMULATION. Fictional vendor, invented answers.** "Acme Core Ledger SIMULATION" does not exist.
> No real vendor, product, contract, attestation report or customer data was used. This document
> does **not** assert compatibility with Banno / Jack Henry or any other real vendor or product, and
> **no authoritative compatibility evidence exists** — the only "contract" is the lab's own fictional
> `integrations/vendor-mock/contract/openapi.json`.

## 0. Header

| Field | Value |
|---|---|
| Vendor legal name | Acme Core Ledger SIMULATION (fictional) |
| Service assessed | Read-only account & transaction API (SIMULATION) |
| Assessment ID / version | VRA-SIM-2026-001 / v0.1 |
| Assessment type | Initial (lab) |
| Business owner | SIMULATION Digital Banking Product Owner |
| Assessor | SIMULATION Third-Party Risk Analyst |
| Date / next review due | 2026-10-28 / 2027-10-28 (SIMULATION) |
| Compatibility evidence | **NONE.** Fictional contract only; no vendor-published spec, sandbox or agreement |

## 1. Inherent risk and tiering

| Factor | Rating | Rationale (SIMULATION) |
|---|---|---|
| Criticality | H | Balances shown to customers in online banking |
| Data sensitivity | M | Masked account numbers, balances, generic transaction descriptions; no SSN/PAN/name |
| Access / connectivity | M | Outbound API calls only, read-only scopes |
| Substitutability | H | Core-adjacent data feed; replacement estimated 9–12 months |
| Regulatory exposure | M | Customer financial information (GLBA-type obligations assumed) |
| Concentration | M | Vendor hosts on a single cloud provider (fourth party) |
| **Resulting tier** | **2 — High** | |

## 2. Data classification and flows

| Data element | Classification | Direction | Needed? | Stored by vendor? | Location |
|---|---|---|---|---|---|
| `account_id` (opaque `SIM-ACCT-…`) | Confidential | from vendor | yes | yes (SoR) | US (SIMULATION) |
| `masked_number` (`****NNNN`) | Confidential | from vendor | yes, masked only | yes | US |
| balances (minor units) | Confidential | from vendor | yes | yes | US |
| transactions (id, time, amount, direction, generic description) | Confidential | from vendor | yes | yes | US |
| customer name / SSN / address | Restricted | — | **no — not in contract; rejected if sent** | n/a to this integration | — |
| OAuth client secret | Restricted | to vendor | yes | vendor IdP | secret manager (ours) |

- TLS 1.2+ in transit; vendor states AES-256 at rest with vendor-managed keys `[~]` (customer-managed keys not offered).
- Subprocessors: one cloud IaaS provider (SIMULATION).

## 3. Access

| Q | Answer (SIMULATION) | Evidence ref |
|---|---|---|
| A1 | OAuth2 client-credentials; tokens 300 s TTL | contract `Token`; tests `AuthenticationFailure` |
| A2 | `[x]` scopes `accounts:read`, `transactions:read`; missing scope → 403 | `test_insufficient_scope_is_403`, `test_not_found_and_forbidden` |
| A3 | `[~]` secret in secret manager; 90-day rotation is a manual process | finding F2 |
| A4 | `[~]` vendor support access via break-glass with ticket; we receive monthly report, not real-time | finding F3 |
| A5 | `[x]` vendor console behind our SSO + MFA | (SIMULATION statement) |
| A6 | `[~]` public internet with egress allow-list; private link not offered | — |
| A7 | `[x]` API audit log export, 90-day retention at vendor | — |

## 4. Security control questions (SOC 2-style placeholders)

| ID | Answer (SIMULATION) | Evidence ref |
|---|---|---|
| C1 | `[~]` SOC 2 Type II-style report claimed for a 12-month period; **not reviewed — no real report exists** | finding F1 |
| C2 | `[ ]` CUECs (credential rotation, access review of our users) not yet assigned owners | finding F2 |
| C3 | `[x]` claimed | — |
| C4 | `[~]` 90-day API deprecation notice claimed; versioned contract in lab only | contract `info.version` |
| C5 | `[x]` annual pen test, summary available on request (claimed) | — |
| C6 | `[~]` 72 h incident notification offered; we require 24 h | finding F4 |
| C7 | `[x]` 99.9 % monthly uptime SLA; status page | — |
| C8 | `[x]` logical tenant segregation (claimed) | — |
| C9 | `[x]` read-only; client validates every response, fails closed | `MalformedResponses`, `ValidatorNegatives` |
| C10 | `[x]` contract prohibits secondary use (SIMULATION) | — |
| C11 | `[~]` lab contract + offline contract tests exist; **no authoritative vendor spec or sandbox** | `evidence/vendor/README.md` |

## 5. Business continuity and disaster recovery

| ID | Answer (SIMULATION) |
|---|---|
| B1 | Vendor RTO 4 h / RPO 15 min; last DR test 2026-06 "passed" (claimed, unverified) |
| B2 | Two regions of one cloud provider → fourth-party concentration `[~]` |
| B3 | Our RTO for balance display: 8 h → vendor RTO meets it `[x]` |
| B4 | Degraded mode: show last-known balance with "as of" timestamp + banner; no cache of transaction detail beyond 24 h |
| B5 | `[ ]` no joint exercise yet — finding F5 |
| B6 | `[x]` timeouts (bounded retries, backoff), 429 with Retry-After (honoured, capped at 30 s), auth failure and malformed responses verified offline | tests `Timeout`, `RateLimiting`, `AuthenticationFailure`, `MalformedResponses` |

## 6. Continuity, escalation and exit

| ID | Answer (SIMULATION) |
|---|---|
| E1 | Data escrow not offered; 180-day wind-down clause on change of control `[~]` |
| E2 | 90 days for API deprecation; 30 days for subprocessor change |
| E3 | Annual financial statements review by Procurement |
| E4 | Sev1 = API unavailable or data exposure; Sev1 declared by our IT ops on-call |
| E5 | Vendor 24x7 Sev1 line → account manager (4 h) → exec sponsor (24 h) — SIMULATION contacts only |
| E6 | Integration owner → IT ops on-call → CISO + BCP coordinator → COO; customer/regulator notification decision: CISO with Legal |
| E7 | Escalate if: outage > 30 min, any suspected data exposure, sustained 429s > 15 min, 2 SLA misses in a quarter, contract-test failure against a new API version |
| X1 | Full export (JSON/CSV) within 30 days at no charge — `[ ]` test export not yet performed |
| X2 | Deletion certificate within 60 days incl. backups `[~]` (subprocessor deletion attested by vendor only) |
| X3 | 6 months transition assistance at contract rates |
| X4 | Alternate: in-house read replica from core SoR (est. 9–12 months) |
| X5 | Integration owner: revoke client credentials, remove egress allow-list, archive contract tests and evidence |
| X6 | Exit plan drafted 2026-10-28; not rehearsed `[ ]` |

## 7. Findings and treatment (SIMULATION)

| # | Finding | Risk | Treatment | Owner | Due |
|---|---|---|---|---|---|
| F1 | No attestation report actually reviewed; no authoritative compatibility evidence | H | Mitigate: obtain and review report + vendor spec/sandbox before any production use | Third-party risk | before go-live |
| F2 | CUEC owners unassigned; manual secret rotation | M | Mitigate: assign owners (see RACI), automate rotation | Integration owner | +60 days |
| F3 | Vendor support access reported monthly, not real-time | M | Mitigate: require access-event feed | Information security | renewal |
| F4 | Incident notification 72 h vs required 24 h | H | Mitigate: contract amendment | Legal / Procurement | before signature |
| F5 | No joint BCP exercise; exit not rehearsed | M | Mitigate: schedule tabletop + test export | BCP coordinator | +90 days |

Residual risk (SIMULATION): **High until F1 and F4 are closed** — not approved for production.

## 8. Data minimization and retention

Applied per `../data-minimization-and-retention.md`: masked numbers only; no names/SSNs in contract;
unexpected fields rejected (tested); tokens memory-only; logs keep metadata only; transaction cache ≤ 24 h.

## 9. Sign-off

SIMULATION — no sign-off recorded. This is lab material, not an approval.
