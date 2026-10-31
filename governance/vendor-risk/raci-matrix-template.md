# Vendor Responsibility (RACI) Matrix — TEMPLATE

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Define responsibilities and risks when an organization depends on an external service. Clear ownership and retained evidence help an organization respond without sending unnecessary sensitive data.

For example: During an outage, the team uses an escalation record to distinguish its responsibilities from the fictional vendor’s responsibilities.

Key terms: **API** means an interface through which programs request operations or information. **RACI** means a responsibility table identifying who is responsible, accountable, consulted, and informed. **Mock** means a controlled substitute for a real component used in a test or demonstration.

**Before using this reference:** Do not send fictional escalation examples as real messages or copy personal data into public exercise records.

Start with the [plain-English learning path](../../docs/knowledge/governance.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **SIMULATION lab template.** Generic placeholders for the bank-it-operations-lab; not tied to any real vendor.

> R = Responsible (does the work), A = Accountable (one per row, signs off), C = Consulted,
> I = Informed. Exactly one **A** per activity. Replace role names to suit the organisation.

| # | Activity | Business owner | Integration / app owner | IT ops (on-call) | Information security | Third-party risk | Privacy / legal | Procurement | Vendor |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Define business need & data requirements (minimization) | | | | | | | | |
| 2 | Inherent-risk tiering & due diligence | | | | | | | | |
| 3 | Contract terms (SLA, security, audit rights, exit) | | | | | | | | |
| 4 | Integration build & contract tests | | | | | | | | |
| 5 | Credential issuance, storage & rotation | | | | | | | | |
| 6 | Access reviews (vendor & internal) | | | | | | | | |
| 7 | Monitoring, alerting & SLA tracking | | | | | | | | |
| 8 | Incident detection & Sev declaration | | | | | | | | |
| 9 | Security incident notification (customers / regulators) | | | | | | | | |
| 10 | BCP/DR testing & degraded-mode procedure | | | | | | | | |
| 11 | Change / API version management | | | | | | | | |
| 12 | Periodic reassessment & attestation review | | | | | | | | |
| 13 | Data retention & deletion verification | | | | | | | | |
| 14 | Exit / termination & decommission | | | | | | | | |
