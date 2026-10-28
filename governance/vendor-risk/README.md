# Vendor (third-party) risk — templates and SIMULATION example

> **SIMULATION / lab material.** Templates are generic placeholders; the filled example concerns the
> **fictional** vendor "Acme Core Ledger SIMULATION". Control questions are *SOC 2-style
> placeholders* written for this lab; they are not AICPA Trust Services Criteria text and do not
> constitute an audit, attestation or regulatory guidance. Nothing here asserts, or provides
> authoritative evidence of, compatibility with any real vendor or product (including Banno / Jack
> Henry). Answers in the example are invented. Vendor-dependent values (service levels, RTO/RPO,
> notice periods, retention, timeframes) are never invented. They appear as `[PLACEHOLDER: confirm
> from contract]`, and the lint enforces this for the assessment example and the scenario.

| File | Purpose |
|---|---|
| `vendor-risk-assessment-template.md` | Blank assessment: tiering, data classification, access, security controls, BCP/DR, continuity / escalation / exit questions, data minimization & retention, sign-off |
| `raci-matrix-template.md` | Blank responsibility (RACI) matrix for the vendor lifecycle and incidents |
| `data-minimization-and-retention.md` | Data minimization and retention notes for vendor integrations |
| `examples/acme-core-ledger-SIMULATION-assessment.md` | Filled SIMULATION assessment of the fictional vendor |
| `examples/acme-core-ledger-SIMULATION-raci.md` | Filled SIMULATION RACI matrix |
| `scenarios/core-banking-vendor-outage-SIMULATION.md` | Vendor-escalation tabletop for a fictional core-banking outage. §0 *Real vendor vs fictional system*: Jack Henry is the real vendor named in the job posting and is used only as context; Acme Core Ledger SIMULATION and the `integrations/vendor-mock` API are fictional and reflect no Jack Henry/Banno API. Also covers objectives, roles, injects with facilitator notes and vendor-mock analogues, impact assessment, evidence collection, escalation, the bank-set update cadence, restoration criteria, post-incident review, completion and sign-off, and cross-references |
| `check_governance.py` | Lint. RACI: exactly one Accountable per row. Template: all sections present. Examples: SIMULATION label and disclaimer; the assessment may contain no SLA-like numbers at all. Scenarios: all required sections, SIMULATION label and contract placeholders; Jack Henry/Banno only in §0, which must state the real-vs-fictional distinction; relative links resolve; cited mock scenarios exist; no vendor SLA numbers, phone numbers, emails or URLs. Vendor-mock: Jack Henry/Banno never appear in its contract, code, fixtures or tests |
| `tests/test_check_governance.py` | Offline unit tests for the lint, positive and negative |

Evidence mapping for the technical controls (contract tests) lives in `evidence/vendor/README.md`.

Legend for answers: `[ ]` open, `[x]` satisfied, `[~]` partial / compensating control, `N/A`.
