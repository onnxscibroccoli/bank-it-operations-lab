# SIMULATION — RACI matrix: Acme Core Ledger SIMULATION integration

> **SIMULATION.** Fictional vendor; illustrative role assignments. R = Responsible, A = Accountable
> (exactly one per row), C = Consulted, I = Informed.

| # | Activity | Business owner | Integration owner | IT ops on-call | InfoSec | Third-party risk | Privacy / legal | Procurement | Vendor (SIM) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Business need & data requirements (minimization) | A | R | I | C | C | C | I | I |
| 2 | Tiering & due diligence | C | C | I | C | A/R | C | C | R |
| 3 | Contract terms (SLA, 24 h incident notice, audit rights, exit) | C | C | I | C | C | R | A | C |
| 4 | Integration build & contract tests (`integrations/vendor-mock`) | I | A/R | C | C | I | I | I | C |
| 5 | Credential issuance, storage & rotation (CUEC) | I | A/R | R | C | I | I | I | R |
| 6 | Access reviews (vendor support & our console users) | I | R | I | A | C | I | I | R |
| 7 | Monitoring, alerting & SLA tracking | I | C | A/R | I | I | I | C | R |
| 8 | Incident detection & Sev declaration | I | C | A/R | C | I | I | I | R |
| 9 | Security-incident notification (customers / regulators) | C | C | I | A | C | R | I | R |
| 10 | BCP/DR test & degraded-mode procedure | A | R | R | C | C | I | I | R |
| 11 | API change / version management (re-run contract tests) | I | A/R | C | C | I | I | I | R |
| 12 | Periodic reassessment & attestation review | C | C | I | C | A/R | C | I | R |
| 13 | Retention & deletion verification | C | R | I | C | C | A | I | R |
| 14 | Exit / termination & decommission | A | R | R | C | C | C | R | R |

Check: every row has exactly one A (see `evidence/vendor` RACI lint in the evidence run).
