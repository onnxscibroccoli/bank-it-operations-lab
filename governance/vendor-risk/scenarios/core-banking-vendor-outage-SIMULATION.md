# SIMULATION — Vendor escalation tabletop: core-banking vendor outage

> **SIMULATION. Tabletop exercise material; fictional events.** The vendor in this scenario is the fictional "Acme Core Ledger SIMULATION".
> **Note on naming:** Jack Henry is mentioned here only because it is the vendor named in the job description this lab was built against; nothing in this scenario describes, or is evidence about, Jack Henry products, APIs, contracts, service levels, contacts or real incident behaviour.
> No proprietary APIs, vendor contacts, phone numbers, service levels or contractual terms are invented here. Anything that would normally come from a contract or the bank's own policies is marked `[PLACEHOLDER: confirm from contract]` or `[PLACEHOLDER: bank-set …]`. **No authoritative compatibility evidence exists** for any real vendor or product.

## 1. Purpose and scope

- Exercise the bank's **internal** escalation, communication, evidence-handling and restoration-validation process when a third-party core-banking / ledger provider is unavailable or degraded.
- In scope: decision points, roles (see `../examples/acme-core-ledger-SIMULATION-raci.md`), questions to ask internally and of the vendor.
- Out of scope: real systems, real vendor engagement, real customer data, legal conclusions.
- Facilitator: `[PLACEHOLDER: name/role]` · Participants: see §3 · Date: `[PLACEHOLDER]` · Duration: `[PLACEHOLDER]`

## 2. Scenario narrative and injects (fictional)

| Inject | Time | Event (SIMULATION) | Discussion prompt |
|---|---|---|---|
| 1 | T+0 | Monitoring shows the account/transaction API returning errors and timeouts (cf. mock scenarios `timeout`, `rate_limit_always`); online/mobile banking shows stale balances. | Who detects, who declares severity, what is the first internal notification? |
| 2 | T+`[PLACEHOLDER]` | Branch and contact-centre staff report they cannot see current balances; card authorizations still appear to process. | Which channels are affected? Is a degraded-mode procedure invoked? |
| 3 | T+`[PLACEHOLDER]` | The vendor status page (fictional) shows "investigating" with no estimated restoration time. | What do we ask the vendor, through which contractually defined channel? |
| 4 | T+`[PLACEHOLDER]` | Some API responses return with unexpected fields or inconsistent balances (cf. `malformed_*` scenarios). | Is this an availability issue only, or a possible integrity / security issue? Does that change notification obligations? |
| 5 | T+`[PLACEHOLDER]` | The vendor reports service restored. | What must be true before *we* declare restoration? (§7) |
| 6 | T+`[PLACEHOLDER]` | Next business day: customers dispute fees and duplicate postings from the outage window. | Reconciliation, remediation, customer communications, post-incident review. |

## 3. Roles (internal)

| Role | Exercise participant |
|---|---|
| Incident commander (IT ops on-call lead) | `[PLACEHOLDER]` |
| Integration / application owner | `[PLACEHOLDER]` |
| Business owner (digital banking / operations) | `[PLACEHOLDER]` |
| Information security | `[PLACEHOLDER]` |
| Third-party risk / vendor manager (sole owner of vendor-facing communication) | `[PLACEHOLDER]` |
| Compliance / legal (notification decisions) | `[PLACEHOLDER]` |
| Communications (customer and staff messaging) | `[PLACEHOLDER]` |
| Scribe / evidence custodian | `[PLACEHOLDER]` |

## 4. Impact assessment

Answer as questions; record answers with timestamps in the incident log.

**Customer impact**
- Which customer actions fail or show stale data (balance view, transfers, bill pay, statements)? Estimated number of customers affected: `[PLACEHOLDER]`
- Are vulnerable customers or time-critical payments (payroll, loan payments, deadlines) affected?
- Are fees, overdrafts or interest likely to be applied wrongly during the window? Who decides on fee reversal?

**Channel impact**
- Online banking, mobile, branch teller, contact centre, ATM, card, ACH/wire, open-banking / third-party aggregators: affected / degraded / unaffected?
- Which channels can be switched to a degraded mode (last-known balance with "as of" timestamp, read-only mode, manual processing)?

**Operational impact**
- Which internal processes stop (end-of-day, reconciliation, fraud monitoring, regulatory reporting extracts)?
- Is the bank's own recovery-time objective for these business processes at risk? `[PLACEHOLDER: bank-set RTO from BIA]`
- Are backlogs building that must be replayed, and is replay idempotent?

**Regulatory and notification considerations (questions only; not legal advice)**
- Does the event meet the bank's internal criteria for a notifiable operational or security incident? `[PLACEHOLDER: bank incident-classification policy]`
- Which regulators, card schemes, partners or insurers may need notice, by whom, and within what timeframe? `[PLACEHOLDER: confirm with compliance/legal from applicable rules]`
- Is there any indication of unauthorized access to, or alteration of, customer information (which would change obligations)?
- What does the contract require the vendor to tell us, and when? `[PLACEHOLDER: confirm from contract]`
- Who approves external statements? `[PLACEHOLDER: bank-set approver]`

## 5. Evidence collection

| What | When | Who (collector → custodian) | How preserved |
|---|---|---|---|
| Monitoring alerts and dashboards (error rates, latency, 429s) | at detection and each status update | IT ops → evidence custodian | export / screenshot with UTC timestamp; hash recorded |
| Integration client logs (method, path template, status, request ID; **no secrets or customer data**) | continuously; snapshot at declaration and restoration | integration owner → custodian | read-only copy; SHA-256 in evidence register |
| Vendor status-page and vendor notices | each change | vendor manager → custodian | saved copy with retrieval time (UTC) and source |
| All vendor communications (tickets, emails, call notes) | as they occur | vendor manager → custodian | ticket references; call notes signed and timestamped |
| Internal decisions (severity, degraded mode, notifications, restoration) | as made | scribe | incident log entry: UTC time, decision, decider, rationale |
| Reconciliation outputs (pre/post restoration) | §7 checks | operations → custodian | report + hash |
| Customer complaints and remediation actions | through closure | operations / communications | case references |

**Chain of custody:** each item gets an ID, collector, collection time (UTC, from a synchronized clock), storage location, SHA-256, and a transfer log (from → to, time, purpose). Evidence is stored read-only in `[PLACEHOLDER: bank evidence repository]`; access is logged. Record time-zone handling explicitly (UTC in logs; local time only in human summaries, labelled).

**Lab tie-in:** `evidence/vendor/generate_evidence.py` shows the pattern (commands, logs, timestamps, hashes, `--verify`). Checklist: `evidence/vendor/escalation-evidence-checklist-SIMULATION.md`.

## 6. Escalation

**Internal tiers (bank-defined)**

| Tier | Who | Trigger (bank-set) |
|---|---|---|
| T1 | IT ops on-call + integration owner | `[PLACEHOLDER: bank-set detection threshold]` |
| T2 | Incident commander, business owner, InfoSec, vendor manager | `[PLACEHOLDER: bank-set criteria, e.g. customer-facing impact]` |
| T3 | CISO, BCP coordinator, compliance/legal, communications | `[PLACEHOLDER: bank-set criteria, e.g. possible data integrity/security issue or prolonged outage]` |
| T4 | Executive crisis team / board notification | `[PLACEHOLDER: bank-set criteria]` |

**Internal escalation questions**
- Has severity been declared, by whom, and is it recorded?
- Has any tier's trigger been met that has not yet been escalated?
- Is degraded mode active, and who approved it?
- Is any decision blocked waiting for vendor information? What is the fallback if it does not arrive?

**Vendor-facing questions** (asked only via the contractual channel: `[PLACEHOLDER: confirm from contract]`)
- What is the scope: which services, regions and clients are affected? Is it isolated to our tenant?
- What is the suspected cause? Is any security event suspected or ruled out?
- Is there any risk to data integrity (lost, duplicated or out-of-order postings)? How will it be demonstrated?
- What is the current restoration plan and estimated time? (Record as stated; do not treat as a commitment unless the contract makes it one.)
- What notifications is the vendor obligated to provide, and by when? `[PLACEHOLDER: confirm from contract]`
- What evidence will the vendor provide afterwards (timeline, root-cause analysis, logs relevant to our tenant)? `[PLACEHOLDER: confirm from contract]`
- Are fourth parties (hosting, network) involved?
- Who is the vendor's incident lead for this event? `[PLACEHOLDER: confirm from contract — do not record personal contact details in this repo]`

## 7. Update cadence (internal; set by the bank)

These intervals are **the bank's own placeholders**, not vendor service levels.

| Audience | Cadence | Owner |
|---|---|---|
| Incident bridge / responders | `[PLACEHOLDER: bank-set interval]` | Incident commander |
| Executive / T3–T4 | `[PLACEHOLDER: bank-set interval]` | Incident commander |
| Front-line staff (branch, contact centre) | `[PLACEHOLDER: bank-set interval]` | Communications |
| Customers (status page, app banner) | `[PLACEHOLDER: bank-set interval]` | Communications, approved by `[PLACEHOLDER]` |
| Vendor status requests | `[PLACEHOLDER: bank-set interval; vendor obligations — confirm from contract]` | Vendor manager |

Each update states: time (UTC + labelled local), current impact, actions since the last update, next decision point, and the time of the next update.

## 8. Restoration criteria (before the bank declares "restored")

The vendor saying the service is restored is an **input**, not a declaration. All of these must pass and be recorded:

- [ ] Health and synthetic transactions succeed from every affected channel; error and 429 rates are back to the bank-set baseline `[PLACEHOLDER: bank-set threshold]`.
- [ ] Contract validation is clean: responses match the integration contract with no unexpected fields (the lab equivalent is `integrations/vendor-mock` tests).
- [ ] Balance reconciliation: a sample (or all) of accounts match between the vendor system of record and the bank's internal ledger/GL `[PLACEHOLDER: bank-set sample size / tolerance]`.
- [ ] Transaction reconciliation for the outage window: no missing, duplicate or out-of-order postings; replayed backlogs confirmed idempotent.
- [ ] Downstream jobs (end-of-day, statements, fraud monitoring, reporting extracts) rerun or confirmed.
- [ ] Degraded-mode artefacts removed (banners, manual workarounds); manual transactions taken during the outage keyed in and reconciled.
- [ ] InfoSec confirms no indicators of compromise, or that the security track is handled separately.
- [ ] Restoration approved by `[PLACEHOLDER: bank-set approver]` with the time recorded; monitoring continues for an elevated period `[PLACEHOLDER: bank-set period]`.

## 9. Post-incident review

- Timeline from the incident log and preserved evidence (§5), reconciled against the vendor's account.
- What worked and what did not: detection, severity declaration, escalation timing, vendor engagement, communications, restoration validation.
- Contract and vendor-management follow-ups: did the vendor meet its obligations? `[PLACEHOLDER: confirm from contract]`. Feed the result into the vendor risk assessment (findings, residual risk, next review date).
- Customer remediation: fee reversals, complaints, communications (owners and completion dates).
- Control and test changes: new or updated contract tests, monitoring thresholds, degraded-mode runbook, RACI updates.
- Actions: ID, owner, due date `[PLACEHOLDER]`, tracking location `[PLACEHOLDER]`; review closed by `[PLACEHOLDER: bank-set approver]`.

## 10. Exercise record (SIMULATION)

| Field | Value |
|---|---|
| Exercise held | `[PLACEHOLDER]` |
| Participants | `[PLACEHOLDER]` |
| Key gaps found | `[PLACEHOLDER]` |
| Actions raised | `[PLACEHOLDER]` |
