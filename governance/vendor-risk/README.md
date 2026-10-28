# Vendor (third-party) risk — templates and SIMULATION example

> **SIMULATION / lab material.** Templates are generic placeholders; the filled example concerns the
> **fictional** vendor "Acme Core Ledger SIMULATION". Control questions are *SOC 2-style
> placeholders* written for this lab; they are not AICPA Trust Services Criteria text and do not
> constitute an audit, attestation or regulatory guidance. Nothing here asserts, or provides
> authoritative evidence of, compatibility with any real vendor or product (including Banno / Jack
> Henry). Answers in the example are invented. In particular, the numbers in the Acme example
> (uptime, RTO/RPO, notice periods) are fictional and belong only to the fictional vendor. The
> escalation scenario deliberately contains no vendor numbers at all.

| File | Purpose |
|---|---|
| `vendor-risk-assessment-template.md` | Blank assessment: tiering, data classification, access, security controls, BCP/DR, continuity / escalation / exit questions, data minimization & retention, sign-off |
| `raci-matrix-template.md` | Blank responsibility (RACI) matrix for the vendor lifecycle and incidents |
| `data-minimization-and-retention.md` | Data minimization and retention notes for vendor integrations |
| `examples/acme-core-ledger-SIMULATION-assessment.md` | Filled SIMULATION assessment of the fictional vendor |
| `examples/acme-core-ledger-SIMULATION-raci.md` | Filled SIMULATION RACI matrix |
| `scenarios/core-banking-vendor-outage-SIMULATION.md` | Vendor-escalation tabletop: a fictional outage at the core-banking vendor, covering impact assessment, evidence collection, escalation questions, the bank-set update cadence, restoration criteria and post-incident review. Jack Henry appears only as the vendor named in the job description. No real APIs, contacts, SLAs or contract terms; those are `[PLACEHOLDER: confirm from contract]` |
| `check_governance.py` | Lint. RACI: exactly one Accountable per row. Template: all sections present. Examples: SIMULATION label and disclaimer. Scenarios: required sections, SIMULATION label and contract placeholders; Jack Henry only in the job-description statement; no SLA-like numbers attributed to a vendor; no phone numbers, emails or URLs |
| `tests/test_check_governance.py` | Offline unit tests for the lint, positive and negative |

Evidence mapping for the technical controls (contract tests) lives in `evidence/vendor/README.md`.

Legend for answers: `[ ]` open, `[x]` satisfied, `[~]` partial / compensating control, `N/A`.
