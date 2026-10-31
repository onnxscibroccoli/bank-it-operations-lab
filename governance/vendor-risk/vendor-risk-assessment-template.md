# Vendor Risk Assessment — TEMPLATE

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Define responsibilities and risks when an organization depends on an external service. Clear ownership and retained evidence help an organization respond without sending unnecessary sensitive data.

For example: During an outage, the team uses an escalation record to distinguish its responsibilities from the fictional vendor’s responsibilities.

Key terms: **API** means an interface through which programs request operations or information. **RACI** means a responsibility table identifying who is responsible, accountable, consulted, and informed. **Mock** means a controlled substitute for a real component used in a test or demonstration.

**Before using this reference:** Do not send fictional escalation examples as real messages or copy personal data into public exercise records.

Start with the [plain-English learning path](../../docs/knowledge/governance.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **SIMULATION lab template.** Generic placeholders for the bank-it-operations-lab; not tied to any real vendor.

> Template for lab use. Replace every `<placeholder>`. SOC 2-style questions are placeholders, not
> AICPA criteria text. Do not record real secrets, customer data or confidential contract terms in
> this repository.

## 0. Header

| Field | Value |
|---|---|
| Vendor legal name | `<name>` |
| Service / product assessed | `<service>` |
| Assessment ID / version | `<VRA-YYYY-NNN>` / `<v>` |
| Assessment type | `<initial / periodic / change-triggered / exit>` |
| Business owner | `<name, role>` |
| Assessor (2nd line) | `<name, role>` |
| Date / next review due | `<YYYY-MM-DD>` / `<YYYY-MM-DD>` |
| Compatibility evidence | `<authoritative source (vendor-published spec, sandbox results, contract) or "NONE">` |

## 1. Inherent risk and tiering

| Factor | Rating (L/M/H) | Rationale |
|---|---|---|
| Criticality to customer-facing / core operations | | |
| Volume & sensitivity of data handled | | |
| Degree of system access / connectivity | | |
| Substitutability (time to replace) | | |
| Regulatory exposure (e.g. GLBA, state privacy, card-scheme rules) | | |
| Concentration / fourth-party dependence | | |
| **Resulting tier** | `<1 critical / 2 high / 3 moderate / 4 low>` | |

## 2. Data classification and flows

| Data element | Classification (`Public/Internal/Confidential/Restricted`) | Direction | Needed? (see §8) | Stored by vendor? | Location / residency |
|---|---|---|---|---|---|
| `<element>` | | `<to vendor / from vendor / both>` | `<yes / no / masked>` | | |

- Data-flow diagram reference: `<link>`
- Encryption in transit (min TLS version) / at rest (algorithm, key ownership): `<...>`
- Fourth parties / subprocessors receiving data: `<list>`

## 3. Access

| Question | Answer | Evidence ref |
|---|---|---|
| A1 Authentication method (OAuth2 client-credentials, mTLS, API key …)? | | |
| A2 Least-privilege scopes defined and enforced per integration? | | |
| A3 Credential storage (secret manager), rotation period, revocation SLA? | | |
| A4 Vendor staff access to our data: who, how approved, logged, reviewed? | | |
| A5 Our staff access to vendor console: SSO + MFA, joiner/mover/leaver process? | | |
| A6 Network path (private link / allow-listed egress / public internet)? | | |
| A7 Audit logs available to us: content, retention, export method? | | |

## 4. Security control questions (SOC 2-style PLACEHOLDERS)

| ID | Area | Placeholder question | Answer | Evidence ref |
|---|---|---|---|---|
| C1 | Governance | Current independent attestation (type, period, scope, carve-outs, exceptions)? Bridge letter? | | |
| C2 | Governance | Complementary user-entity controls (CUECs) we must operate? Owner for each? | | |
| C3 | Logical access | MFA for privileged access; quarterly access reviews? | | |
| C4 | Change mgmt | Change approval, segregation of duties, API versioning & deprecation notice period? | | |
| C5 | Ops / monitoring | 24x7 monitoring, vulnerability mgmt SLAs, pen-test cadence and summary shared? | | |
| C6 | Incident mgmt | Notification SLA for security incidents affecting our data (hours)? Named contact? | | |
| C7 | Availability | Contractual uptime SLA, measurement method, service credits, status page? | | |
| C8 | Confidentiality | Encryption, key management, data segregation between tenants? | | |
| C9 | Processing integrity | Idempotency, reconciliation reports, error/duplicate handling? | | |
| C10 | Privacy | Use of our data for vendor's own purposes (analytics, model training) prohibited? | | |
| C11 | Integration contract | Authoritative, versioned API spec provided? Sandbox available? Contract tests against it? | | |

## 5. Business continuity and disaster recovery

| ID | Question | Answer | Evidence ref |
|---|---|---|---|
| B1 | Vendor RTO / RPO for this service; how tested; last test date and result? | | |
| B2 | Geographic redundancy; single points of failure; fourth-party (cloud) concentration? | | |
| B3 | Our own RTO/RPO for the dependent business process — does vendor meet it? | | |
| B4 | Our degraded-mode procedure if vendor is unavailable (manual workaround, queueing, customer comms)? | | |
| B5 | Joint BCP exercise held with vendor in last 12 months? | | |
| B6 | Client behaviour under vendor failure verified (timeouts, retries, rate limits, malformed data)? | | |

## 6. Continuity, escalation and exit-plan questions

**Continuity**
- E1 What happens to service and data if the vendor is acquired, insolvent, or exits the product line? Escrow (source / data)?
- E2 Notice period for material service changes, API deprecations, subprocessor changes?
- E3 Financial health review cadence and source?

**Escalation**
- E4 Severity matrix and response times (Sev1/2/3) — who on our side declares severity?
- E5 Named escalation path at vendor (L1 → account mgr → exec sponsor) with 24x7 contact for Sev1?
- E6 Our internal escalation: integration owner → IT ops on-call → CISO / BCP coordinator → executive; regulator / customer notification decision owner?
- E7 Trigger thresholds that force escalation (e.g. >N minutes outage, any data exposure, repeated SLA miss)?

**Exit**
- X1 Data return: format, completeness, timeframe, cost; verified by test export?
- X2 Certified deletion/destruction after return, including backups and subprocessors; certificate timeframe?
- X3 Transition assistance period and rates; termination-for-convenience terms?
- X4 Replacement options identified (alternate vendor / in-house) and estimated migration time?
- X5 Credential revocation, network/allow-list removal, and integration decommission checklist owner?
- X6 Exit plan last reviewed / rehearsed (date)?

## 7. Findings and treatment

| # | Finding | Risk (L/M/H) | Treatment (accept / mitigate / transfer / avoid) | Owner | Due |
|---|---|---|---|---|---|

Residual risk: `<L/M/H>` — Risk-acceptance authority: `<role>`

## 8. Data minimization and retention

See `data-minimization-and-retention.md`. Record per data element: purpose, minimum form
(masked/tokenized/aggregated), retention at vendor, retention on our side, deletion method.

## 9. Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Business owner | | | |
| Information security | | | |
| Third-party risk (2nd line) | | | |
| Privacy / legal | | | |
