# SIMULATION — Vendor Risk Assessment: Acme Core Ledger SIMULATION

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Define responsibilities and risks when an organization depends on an external service. Clear ownership and retained evidence help an organization respond without sending unnecessary sensitive data.

For example: During an outage, the team uses an escalation record to distinguish its responsibilities from the fictional vendor’s responsibilities.

Key terms: **API** means an interface through which programs request operations or information. **RACI** means a responsibility table identifying who is responsible, accountable, consulted, and informed. **Mock** means a controlled substitute for a real component used in a test or demonstration.

**Before using this reference:** Do not send fictional escalation examples as real messages or copy personal data into public exercise records.

Start with the [plain-English learning path](../../../docs/knowledge/governance.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **SIMULATION. Fictional vendor, invented answers.** "Acme Core Ledger SIMULATION" does not exist.
> No real vendor, product, contract, attestation report or customer data was used. This document
> does **not** assert compatibility with Banno / Jack Henry or any other real vendor or product, and
> **no authoritative compatibility evidence exists** — the only "contract" is the lab's own fictional
> `integrations/vendor-mock/contract/openapi.json`.
>
> Vendor-dependent values (service levels, RTO/RPO, notice periods, retention, timeframes) are
> **not invented**: they are `[PLACEHOLDER: confirm from contract]`. Bank-internal values are
> `[PLACEHOLDER: bank-set …]`. The scenario `../scenarios/core-banking-vendor-outage-SIMULATION.md` exercises §5–§6.

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
| Substitutability | H | Core-adjacent data feed; replacement effort `[PLACEHOLDER: bank estimate]` |
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
| A1 | OAuth2 client-credentials; token lifetime per the fictional contract's `expires_in` (lab value only) | contract `Token`; tests `AuthenticationFailure` |
| A2 | `[x]` scopes `accounts:read`, `transactions:read`; missing scope → 403 | `test_insufficient_scope_is_403`, `test_not_found_and_forbidden` |
| A3 | `[~]` secret in secret manager; rotation interval `[PLACEHOLDER: bank-set]` is a manual process | finding F2 |
| A4 | `[~]` vendor support access via break-glass with ticket; we receive monthly report, not real-time | finding F3 |
| A5 | `[x]` vendor console behind our SSO + MFA | (SIMULATION statement) |
| A6 | `[~]` public internet with egress allow-list; private link not offered | — |
| A7 | `[x]` API audit log export; vendor log retention `[PLACEHOLDER: confirm from contract]` | — |

## 4. Security control questions (SOC 2-style placeholders)

| ID | Answer (SIMULATION) | Evidence ref |
|---|---|---|
| C1 | `[~]` SOC 2 Type II-style report claimed for a period `[PLACEHOLDER: confirm from report]`; **not reviewed — no real report exists** | finding F1 |
| C2 | `[ ]` CUECs (credential rotation, access review of our users) not yet assigned owners | finding F2 |
| C3 | `[x]` claimed | — |
| C4 | `[~]` API deprecation notice period `[PLACEHOLDER: confirm from contract]`; versioned contract in lab only | contract `info.version` |
| C5 | `[x]` pen-test cadence and summary availability `[PLACEHOLDER: confirm from contract]` | — |
| C6 | `[ ]` incident-notification timeframe `[PLACEHOLDER: confirm from contract]`; bank requirement `[PLACEHOLDER: bank-set]` | finding F4 |
| C7 | `[ ]` availability commitment and measurement `[PLACEHOLDER: confirm from contract]`; status page (claimed) | — |
| C8 | `[x]` logical tenant segregation (claimed) | — |
| C9 | `[x]` read-only; client validates every response, fails closed | `MalformedResponses`, `ValidatorNegatives` |
| C10 | `[x]` contract prohibits secondary use (SIMULATION) | — |
| C11 | `[~]` lab contract + offline contract tests exist; **no authoritative vendor spec or sandbox** | `evidence/vendor/README.md` |

## 5. Business continuity and disaster recovery

| ID | Answer (SIMULATION) |
|---|---|
| B1 | Vendor RTO / RPO `[PLACEHOLDER: confirm from contract]`; last DR test date and result `[PLACEHOLDER: confirm from contract]` (unverified) |
| B2 | Two regions of one cloud provider → fourth-party concentration `[~]` |
| B3 | Our RTO for balance display `[PLACEHOLDER: bank-set RTO from BIA]` → comparison with vendor RTO pending `[ ]` |
| B4 | Degraded mode: show last-known balance with "as of" timestamp + banner; transaction-detail cache limited to `[PLACEHOLDER: bank-set period]` |
| B5 | `[ ]` no joint exercise yet — finding F5 |
| B6 | `[x]` timeouts (bounded retries, backoff), 429 with Retry-After (honoured, capped at 30 s), auth failure and malformed responses verified offline | tests `Timeout`, `RateLimiting`, `AuthenticationFailure`, `MalformedResponses` |

## 6. Continuity, escalation and exit

| ID | Answer (SIMULATION) |
|---|---|
| E1 | Data escrow not offered (claimed); wind-down terms on change of control `[PLACEHOLDER: confirm from contract]` `[ ]` |
| E2 | Notice periods for API deprecation and subprocessor change `[PLACEHOLDER: confirm from contract]` |
| E3 | Financial statements review by Procurement at `[PLACEHOLDER: bank-set cadence]` |
| E4 | Sev1 = API unavailable or data exposure; Sev1 declared by our IT ops on-call |
| E5 | Vendor escalation path and response times `[PLACEHOLDER: confirm from contract]` — no contacts recorded in this repo |
| E6 | Integration owner → IT ops on-call → CISO + BCP coordinator → COO; customer/regulator notification decision: CISO with Legal |
| E7 | Escalate if: outage beyond `[PLACEHOLDER: bank-set threshold]`, any suspected data exposure, sustained 429s beyond `[PLACEHOLDER: bank-set threshold]`, repeated missed vendor obligations, contract-test failure against a new API version (see `../scenarios/core-banking-vendor-outage-SIMULATION.md` §5) |
| X1 | Data export format, timeframe and cost `[PLACEHOLDER: confirm from contract]` — `[ ]` test export not yet performed |
| X2 | Deletion certificate scope (incl. backups, subprocessors) and timeframe `[PLACEHOLDER: confirm from contract]` `[ ]` |
| X3 | Transition-assistance period and rates `[PLACEHOLDER: confirm from contract]` |
| X4 | Alternate: in-house read replica from core SoR (effort `[PLACEHOLDER: bank estimate]`) |
| X5 | Integration owner: revoke client credentials, remove egress allow-list, archive contract tests and evidence |
| X6 | Exit plan drafted 2026-10-28; not rehearsed `[ ]` |

## 7. Findings and treatment (SIMULATION)

| # | Finding | Risk | Treatment | Owner | Due |
|---|---|---|---|---|---|
| F1 | No attestation report actually reviewed; no authoritative compatibility evidence | H | Mitigate: obtain and review report + vendor spec/sandbox before any production use | Third-party risk | before go-live |
| F2 | CUEC owners unassigned; manual secret rotation | M | Mitigate: assign owners (see RACI), automate rotation | Integration owner | `[PLACEHOLDER: bank-set]` |
| F3 | Vendor support access reported monthly, not real-time | M | Mitigate: require access-event feed | Information security | renewal |
| F4 | Incident-notification timeframe not confirmed against the bank requirement | H | Mitigate: contract amendment | Legal / Procurement | before signature |
| F5 | No joint BCP exercise; exit not rehearsed | M | Mitigate: run tabletop `../scenarios/core-banking-vendor-outage-SIMULATION.md` + test export | BCP coordinator | `[PLACEHOLDER: bank-set]` |

Residual risk (SIMULATION): **High until F1 and F4 are closed** — not approved for production.

## 8. Data minimization and retention

Applied per `../data-minimization-and-retention.md`: masked numbers only; no names/SSNs in contract;
unexpected fields rejected (tested); tokens memory-only; logs keep metadata only; transaction cache limited to `[PLACEHOLDER: bank-set period]`.

## 9. Sign-off

SIMULATION — no sign-off recorded. This is lab material, not an approval.
