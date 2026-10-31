# SIMULATION — Vendor escalation tabletop: core-banking vendor outage

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Define responsibilities and risks when an organization depends on an external service. Clear ownership and retained evidence help an organization respond without sending unnecessary sensitive data.

For example: During an outage, the team uses an escalation record to distinguish its responsibilities from the fictional vendor’s responsibilities.

Key terms: **API** means an interface through which programs request operations or information. **RACI** means a responsibility table identifying who is responsible, accountable, consulted, and informed. **Mock** means a controlled substitute for a real component used in a test or demonstration.

**Before using this reference:** Do not send fictional escalation examples as real messages or copy personal data into public exercise records.

Start with the [plain-English learning path](../../../docs/knowledge/governance.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **SIMULATION. Tabletop exercise material; all events are fictional.** The vendor in this exercise
> is the fictional **Acme Core Ledger SIMULATION**. For how this relates to the real vendor named in
> the job posting, see [§0 Real vendor vs fictional system](#0-real-vendor-vs-fictional-system).
> This document invents no proprietary APIs, vendor contacts, phone numbers, service levels or
> contractual terms. Anything that would come from a contract is marked
> `[PLACEHOLDER: confirm from contract]`, and anything the bank decides for itself is marked
> `[PLACEHOLDER: bank-set …]`. **No authoritative compatibility evidence exists** for any real
> vendor or product.

## 0. Real vendor vs fictional system

| | Real vendor named in the job posting | Fictional system used in this lab |
|---|---|---|
| Name | Jack Henry: named in the job description this lab was built against, and used **only as context** for why a core-banking vendor escalation exercise is relevant to the role | **Acme Core Ledger SIMULATION**, which does not exist |
| What this repo contains about it | Nothing beyond this context statement. No Jack Henry (or Banno) product, API, contract, service level, contact or incident behaviour is described or assumed | The fictional API contract, mock, client and tests in [`integrations/vendor-mock`](../../../integrations/vendor-mock/README.md), and the fictional [assessment](../examples/acme-core-ledger-SIMULATION-assessment.md) and [RACI](../examples/acme-core-ledger-SIMULATION-raci.md) |
| Compatibility | The mock does **not** reflect any Jack Henry or Banno API, and nothing here claims that it does | Validated only against its own fictional contract |

Rules applied throughout this repo (enforced by [`check_governance.py`](../check_governance.py)):
- Jack Henry is mentioned only in this section of this scenario, and Banno appears only in the no-compatibility statement above.
- The vendor-mock contract, code, fixtures and tests never name Jack Henry or Banno.
- Every vendor-dependent value in the exercise is a placeholder, not an invented number.

## 1. Exercise overview and objectives

**Purpose:** rehearse the bank's **internal** response when a third-party core-banking / ledger
provider is unavailable or degraded. That means escalating, communicating, preserving evidence,
validating restoration and learning from the event.

**Objectives.** By the end of the exercise, participants should be able to:
1. Declare severity and escalate through the internal tiers, with recorded decisions and owners (§5).
2. Assess customer, channel, operational and regulatory-notification impact using the questions in §3.
3. Name what evidence is collected, when, by whom, and how chain of custody is kept (§4).
4. Separate vendor statements from the bank's own decisions. Vendor commitments come only from the contract (`[PLACEHOLDER: confirm from contract]`).
5. Apply restoration criteria (§7) rather than accepting "the vendor says it's fixed".
6. Produce post-incident review actions that feed the vendor risk assessment and the RACI (§8).

**Scope:** decision-making, roles and questions. **Out of scope:** real systems, real vendor
engagement, real customer data, legal conclusions.

| Logistics | Value |
|---|---|
| Date / duration | `[PLACEHOLDER: bank-set]` |
| Facilitator | `[PLACEHOLDER: name/role]` |
| Scribe / evidence custodian | `[PLACEHOLDER: name/role]` |
| Materials | this scenario; the [evidence checklist](../../../evidence/vendor/escalation-evidence-checklist-SIMULATION.md); the [RACI](../examples/acme-core-ledger-SIMULATION-raci.md); the [assessment template](../vendor-risk-assessment-template.md) §5–§6; the [fictional assessment](../examples/acme-core-ledger-SIMULATION-assessment.md) |

## 2. Roles

Role assignments follow the [SIMULATION RACI](../examples/acme-core-ledger-SIMULATION-raci.md), rows 7–10 and 14.

| Role | Responsibilities in the exercise | Participant |
|---|---|---|
| Facilitator | Runs the injects, keeps time, asks probing questions, does not solve the problem | `[PLACEHOLDER]` |
| Incident commander (IT ops on-call lead) | Declares severity, runs the bridge, owns the internal update cadence (RACI row 8) | `[PLACEHOLDER]` |
| Integration / application owner | Interprets client errors, runs contract validation, leads technical restoration checks | `[PLACEHOLDER]` |
| Business owner (digital banking / operations) | Customer and channel impact, degraded-mode decisions, accountable for BCP (RACI row 10) | `[PLACEHOLDER]` |
| Information security | Decides whether there is a security or integrity concern, accountable for incident notification (RACI row 9) | `[PLACEHOLDER]` |
| Third-party risk / vendor manager | **Sole** owner of communication with the vendor; records vendor statements | `[PLACEHOLDER]` |
| Compliance / legal | Assesses notification obligations; approves external statements | `[PLACEHOLDER]` |
| Communications | Staff and customer messaging | `[PLACEHOLDER]` |
| Scribe / evidence custodian | Incident log, evidence register, chain of custody (§4) | `[PLACEHOLDER]` |
| Observer / evaluator | Scores the exercise against the objectives (§9) | `[PLACEHOLDER]` |

## Injects and facilitator notes (fictional)

Times are relative to T+0, and the facilitator sets the intervals. Each inject names the
[vendor-mock](../../../integrations/vendor-mock/README.md) failure scenario that serves as its
fictional technical analogue. Those scenarios can be run offline to show participants what the
integration client does.

| # | Time | Inject (SIMULATION) | Mock analogue | Discussion prompts | Facilitator notes: what good looks like |
|---|---|---|---|---|---|
| 1 | T+0 | Monitoring alerts: the account/transaction API returns timeouts; online and mobile banking show stale balances. | `timeout`, `timeout_once` | Who detects it? Who declares severity? What is the first internal notification? | Severity is declared and logged with a UTC time. T1 is engaged (§5). The client's bounded retries are understood, so there is no retry storm. The evidence custodian is named. |
| 2 | T+`[PLACEHOLDER]` | The API starts answering with rate-limit responses carrying long Retry-After values; branch and contact-centre staff cannot see current balances. | `rate_limit_always`, `rate_limit_long` | Which channels are affected? Do we invoke degraded mode? Do we escalate to T2? | The channel impact table is filled in (§3). The business owner decides on degraded mode. The client fails fast rather than waiting indefinitely. A front-line script is requested. |
| 3 | T+`[PLACEHOLDER]` | The fictional vendor status page says "investigating" and gives no restoration estimate. | — | What do we ask the vendor, and through which channel? Who asks? | Only the vendor manager contacts the vendor, through `[PLACEHOLDER: confirm from contract]`. The questions in §5 are used. Statements are recorded as statements, not commitments. |
| 4 | T+`[PLACEHOLDER]` | Some responses arrive with unexpected fields or inconsistent balances. | `malformed_extra_field`, `malformed_missing_field`, `malformed_wrong_type` | Is this availability only, or a possible integrity or security issue? Does that change notification duties? | InfoSec opens a security/integrity track. T3 is considered. Compliance runs the notification assessment (§3). The client rejects the malformed data instead of ingesting it. |
| 5 | T+`[PLACEHOLDER]` | Authentication to the API starts failing for some requests while the vendor rotates infrastructure. | `auth_token_rejected`, `auth_token_expired_once` | Is this our credential problem or the vendor's? Who may rotate credentials? | Rotation follows RACI row 5. Credentials are not shared on the bridge. No secrets end up in logs or evidence. |
| 6 | T+`[PLACEHOLDER]` | The vendor reports the service restored. | `normal` | What must be true before *we* declare restoration? | §7 criteria are applied. Restoration is declared by the bank's approver, not by the vendor. Elevated monitoring continues. |
| 7 | Next business day | Customers dispute fees and duplicate postings from the outage window. | — | How do we reconcile, remediate and communicate? Who owns the post-incident review? | Reconciliation is evidenced. Fee-reversal decisions are made by the business owner. The post-incident review is scheduled (§8). |

Facilitator guidance:
- Don't reveal later injects early.
- If the group accepts a vendor restoration estimate as a commitment, ask: "Where is that in the contract?" The answer is `[PLACEHOLDER: confirm from contract]`.
- If the group names specific vendor deadlines, ask where they come from. Unless the contract says so, they are not commitments.

## 3. Impact assessment

Record answers with UTC timestamps in the incident log, and reassess at each update cycle (§6).

**Customer impact**
- Which customer actions fail or show stale data: balance view, transfers, bill pay, statements, card controls?
- How many customers are affected, and how are they segmented (retail, business, vulnerable)? `[PLACEHOLDER: bank estimate method]`
- Are time-critical payments at risk (payroll, loan payments, tax or other deadlines)?
- Could fees, overdrafts or interest be applied wrongly during the window? Who decides on reversals?
- What do customers see now, and is it accurate?

**Channel impact**

| Channel | Affected / degraded / unaffected | Degraded-mode option | Decision owner |
|---|---|---|---|
| Online banking | | last-known balance with "as of" time and banner | business owner |
| Mobile app | | as above | business owner |
| Branch / teller | | manual procedure `[PLACEHOLDER: bank runbook]` | operations |
| Contact centre | | scripted responses | communications |
| ATM / card | | `[PLACEHOLDER: bank runbook]` | operations |
| ACH / wire / payments | | queue / manual `[PLACEHOLDER: bank runbook]` | operations |
| Third-party aggregators | | `[PLACEHOLDER]` | integration owner |

**Operational impact**
- Which internal processes stop or degrade: end-of-day, reconciliation, fraud monitoring, regulatory reporting extracts, GL posting?
- Is the bank's own recovery-time objective for these processes at risk? `[PLACEHOLDER: bank-set RTO from BIA]`
- Are backlogs building? Is replay idempotent, and who approves it?
- Which staff are diverted, and is there fatigue or hand-over risk on a long incident?

**Regulatory and notification considerations** (questions only; not legal advice)
- Does the event meet the bank's internal criteria for a notifiable operational or security incident? `[PLACEHOLDER: bank incident-classification policy]`
- Which regulators, card schemes, partners or insurers may need notice, from whom, and within what timeframe? `[PLACEHOLDER: confirm with compliance/legal from applicable rules]`
- Is there any sign of unauthorized access to, or alteration of, customer information? That would change the obligations.
- What does the contract require the vendor to tell us, and when? `[PLACEHOLDER: confirm from contract]`
- Who approves external statements, and where is the approval recorded? `[PLACEHOLDER: bank-set approver]`

## 4. Evidence collection

Use the [evidence checklist](../../../evidence/vendor/escalation-evidence-checklist-SIMULATION.md) during the exercise.

| What | When | Who (collector → custodian) | How preserved |
|---|---|---|---|
| Monitoring alerts and dashboards (error rates, latency, rate-limit responses) | at detection, then each update cycle | IT ops → evidence custodian | export or screenshot with UTC timestamp; SHA-256 recorded |
| Integration client logs (method, path template, status, request ID; **no secrets or customer data**) | continuously; snapshots at declaration and restoration | integration owner → custodian | read-only copy; hash in the evidence register |
| Vendor status page and notices | every change | vendor manager → custodian | saved copy with retrieval time (UTC) and source |
| All vendor communications (tickets, messages, call notes) | as they happen | vendor manager → custodian | ticket references; call notes signed and timestamped |
| Internal decisions (severity, tier changes, degraded mode, notifications, restoration) | as made | scribe | incident-log entry: UTC time, decision, decider, rationale |
| Reconciliation outputs (before and after restoration) | during §7 checks | operations → custodian | report plus hash |
| Customer complaints and remediation | through closure | operations / communications | case references |

**Chain of custody**
- Every item gets an ID, collector, collection time (UTC, from a synchronized clock), storage location, SHA-256 and transfer log (from → to, UTC time, purpose).
- Evidence is stored read-only in `[PLACEHOLDER: bank evidence repository]`, and access is logged.
- Logs use UTC. Human summaries may show local time, labelled with its zone.
- Hashes are re-verified at closure. The lab pattern is `evidence/vendor/generate_evidence.py --verify`.

## 5. Escalation

**Internal tiers (bank-defined)**

| Tier | Who | Trigger | Exit / de-escalation |
|---|---|---|---|
| T1 | IT ops on-call + integration owner | `[PLACEHOLDER: bank-set detection threshold]` | resolved, or escalated to T2 |
| T2 | Incident commander, business owner, InfoSec, vendor manager | `[PLACEHOLDER: bank-set criteria, e.g. customer-facing impact]` | §7 criteria met |
| T3 | CISO, BCP coordinator, compliance/legal, communications | `[PLACEHOLDER: bank-set criteria, e.g. possible integrity/security issue or prolonged outage]` | security track closed; notification decisions recorded |
| T4 | Executive crisis team / board notification | `[PLACEHOLDER: bank-set criteria]` | per crisis-management plan `[PLACEHOLDER]` |

**Internal escalation questions**
- Has severity been declared, by whom, and is it recorded?
- Has any tier's trigger been met without an escalation?
- Is degraded mode active? Who approved it, and when is it reviewed?
- Is any decision blocked waiting for vendor information? What is the fallback if it doesn't arrive?
- Has the security/integrity track been opened or explicitly ruled out?
- Are notification clocks running? Who is tracking them? `[PLACEHOLDER: confirm with compliance/legal]`

**Vendor-facing questions** (asked only by the vendor manager, through the contractual channel `[PLACEHOLDER: confirm from contract]`)
- Scope: which services, regions and clients are affected? Is the impact specific to our tenant?
- Cause: what is suspected? Has a security event been suspected or ruled out?
- Integrity: is there any risk of lost, duplicated or out-of-order postings? How will that be demonstrated to us?
- Restoration: what is the plan and the current estimate? Record it as stated; it is not a commitment unless the contract makes it one.
- Obligations: what notifications and updates must the vendor give, and by when? `[PLACEHOLDER: confirm from contract]`
- Afterwards: what will the vendor provide (timeline, root-cause analysis, logs relevant to our tenant)? `[PLACEHOLDER: confirm from contract]`
- Fourth parties: are hosting or network providers involved?
- Incident lead: who leads for the vendor? `[PLACEHOLDER: confirm from contract — do not record personal contact details in this repo]`

## 6. Update cadence (internal; set by the bank)

These intervals are **the bank's own placeholders, not vendor service levels**. What the vendor
owes the bank comes only from the contract (`[PLACEHOLDER: confirm from contract]`).

| Audience | Cadence | Channel | Owner |
|---|---|---|---|
| Incident bridge / responders | `[PLACEHOLDER: bank-set interval]` | bridge | incident commander |
| Executives / T3–T4 | `[PLACEHOLDER: bank-set interval]` | briefing note | incident commander |
| Front-line staff (branch, contact centre) | `[PLACEHOLDER: bank-set interval]` | staff notice / script | communications |
| Customers (status page, app banner) | `[PLACEHOLDER: bank-set interval]` | public channels | communications, approved by `[PLACEHOLDER]` |
| Requests to the vendor for status | `[PLACEHOLDER: bank-set interval]` | contractual channel | vendor manager |

Every update gives:
- the time (UTC, plus labelled local time)
- current impact
- actions since the last update
- open decisions
- the next decision point
- when the next update is due

Missing an update is itself a reason to escalate.

## 7. Restoration criteria (before the bank declares "restored")

The vendor saying the service is restored is an **input**, not a declaration. Every item below
must pass, and each must be recorded with evidence and a UTC time.

- [ ] **Availability:** health checks and synthetic transactions succeed from every affected channel. Error and rate-limit rates are back to the bank-set baseline `[PLACEHOLDER: bank-set threshold]`.
- [ ] **Contract validation:** responses match the integration contract, with no unexpected or missing fields. The lab analogue is a clean `integrations/vendor-mock` test run.
- [ ] **Balance reconciliation:** sampled (or all) accounts match between the vendor system of record and the bank's internal ledger/GL. `[PLACEHOLDER: bank-set sample size / tolerance]`
- [ ] **Transaction reconciliation:** no missing, duplicate or out-of-order postings in the outage window; replayed backlogs confirmed idempotent.
- [ ] **Downstream jobs:** end-of-day, statements, fraud monitoring and reporting extracts rerun or confirmed.
- [ ] **Manual work:** transactions taken manually during the outage keyed in and reconciled; degraded-mode banners and workarounds removed.
- [ ] **Security:** InfoSec confirms there are no indicators of compromise, or that the security track is being handled separately.
- [ ] **Approval:** restoration approved by `[PLACEHOLDER: bank-set approver]` and the time recorded. Elevated monitoring for `[PLACEHOLDER: bank-set period]`. Customers and staff told.

## 8. Post-incident review

| Step | Content | Owner |
|---|---|---|
| Timeline | Built from the incident log and preserved evidence (§4), reconciled with the vendor's account | scribe / incident commander |
| What worked / what didn't | detection, severity declaration, escalation timing, vendor engagement, update cadence, restoration validation | incident commander |
| Vendor performance | Did the vendor meet its obligations? `[PLACEHOLDER: confirm from contract]` Feed this into the [assessment](../vendor-risk-assessment-template.md) §5–§7 (findings, residual risk, next review date) | third-party risk |
| Customer remediation | fee reversals, complaints, communications; owners and completion dates | business owner |
| Control and test changes | new or updated contract tests (for example, add a mock scenario for any newly seen failure mode), monitoring thresholds, degraded-mode runbook, [RACI](../raci-matrix-template.md) updates | integration owner / InfoSec |
| Actions | ID, owner, due date `[PLACEHOLDER]`, tracking location `[PLACEHOLDER]` | incident commander |

The review is blameless, and it is held within `[PLACEHOLDER: bank-set interval]` of restoration.

## 9. Completion and sign-off

**Exercise completion criteria**
- [ ] All injects run and discussed
- [ ] Each objective in §1 scored by the evaluator: met / partially met / not met
- [ ] Gaps recorded, and each gap turned into an action with an owner
- [ ] Evidence checklist reviewed for completeness
- [ ] Assessment findings and RACI updates proposed where needed

| Objective | Score | Evidence / notes |
|---|---|---|
| 1 Severity and escalation | `[PLACEHOLDER]` | |
| 2 Impact assessment | `[PLACEHOLDER]` | |
| 3 Evidence and chain of custody | `[PLACEHOLDER]` | |
| 4 Vendor statements vs commitments | `[PLACEHOLDER]` | |
| 5 Restoration criteria | `[PLACEHOLDER]` | |
| 6 Post-incident actions | `[PLACEHOLDER]` | |

| Sign-off role | Name | Date | Signature / approval reference |
|---|---|---|---|
| Facilitator | `[PLACEHOLDER]` | | |
| Business owner | `[PLACEHOLDER]` | | |
| Information security | `[PLACEHOLDER]` | | |
| Third-party risk | `[PLACEHOLDER]` | | |
| BCP coordinator | `[PLACEHOLDER]` | | |

SIMULATION: no sign-off is recorded in this repository. This is lab material, not an approval.

## 10. Cross-references

- [Vendor risk assessment template](../vendor-risk-assessment-template.md): §5 BCP/DR, §6 continuity / escalation / exit
- [SIMULATION assessment of the fictional vendor](../examples/acme-core-ledger-SIMULATION-assessment.md)
- [RACI template](../raci-matrix-template.md) and [SIMULATION RACI](../examples/acme-core-ledger-SIMULATION-raci.md)
- [Data minimization and retention notes](../data-minimization-and-retention.md)
- [Escalation evidence checklist](../../../evidence/vendor/escalation-evidence-checklist-SIMULATION.md) and [evidence README](../../../evidence/vendor/README.md)
- [Fictional technical analogue: vendor-mock](../../../integrations/vendor-mock/README.md), whose failure scenarios are defined in `integrations/vendor-mock/vendor_mock/mock.py`
