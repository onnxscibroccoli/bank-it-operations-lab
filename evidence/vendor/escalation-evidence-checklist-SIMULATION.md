# SIMULATION — Vendor escalation evidence checklist

> **SIMULATION.** This checklist goes with `governance/vendor-risk/scenarios/core-banking-vendor-outage-SIMULATION.md`.
> It is for tabletop use only, with a fictional vendor. It has no real contacts, service levels or contract terms; where those would go it uses `[PLACEHOLDER: confirm from contract]`.
> No authoritative compatibility evidence exists for any real vendor or product.

Every item records: **evidence ID**, **what**, **collected at (UTC, synchronized clock)**, **collected by**, **custodian**, **storage location**, **SHA-256**, and **transfer log** (from → to, UTC time, purpose).

## At detection / severity declaration
- [ ] Monitoring alert export (error rate, latency, 429 counts) and dashboard snapshot
- [ ] Integration client log snapshot. Metadata only: method, path template, status, request ID. No secrets, tokens or customer data.
- [ ] Incident log entry: severity, declared by, UTC time, rationale
- [ ] Vendor status-page capture with retrieval time and source

## During the incident (each update cycle, at the `[PLACEHOLDER: bank-set interval]`)
- [ ] Internal status update as issued (audience, time, content)
- [ ] Vendor communications: ticket references, notices, signed and timestamped call notes. Vendor channel: `[PLACEHOLDER: confirm from contract]`
- [ ] Decisions: degraded mode, escalation tier changes, notification decisions (decider, UTC time, rationale)
- [ ] Notification-assessment record from compliance/legal: `[PLACEHOLDER: bank incident-classification policy]`

## Before declaring restored
- [ ] Synthetic transaction results from each affected channel
- [ ] Contract-validation run output (the lab equivalent is an `evidence/vendor/runs/<label>/` run)
- [ ] Balance and transaction reconciliation reports for the outage window, with tolerance `[PLACEHOLDER: bank-set]`
- [ ] Downstream job rerun confirmations
- [ ] InfoSec "no indicators of compromise" statement, or a pointer to the separate security track
- [ ] Restoration approval: approver, UTC time

## Post-incident
- [ ] Consolidated timeline reconciled with the vendor's account
- [ ] Vendor's root-cause analysis and other deliverables owed under the contract: `[PLACEHOLDER: confirm from contract]`
- [ ] Customer remediation log (fee reversals, complaints)
- [ ] Post-incident review record and actions (owner, due date)
- [ ] Updates to the vendor risk assessment (findings, residual risk) and to the RACI
- [ ] Evidence register closed: hashes re-verified, access log reviewed, retention set per the records schedule
