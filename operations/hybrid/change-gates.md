# Change gates for hybrid runbooks

> **Execution status: NOT_EXECUTED.** These gates have never been exercised. No runbook in this lab may be executed until every gate below is met.

| # | Gate | Pass condition |
|---|---|---|
| G1 | Authorization | Written approval naming the environment (lab only), the runbook and the operator |
| G2 | Change record | Normal or standard change raised (see `docs/management/change-review.md` once merged); risk scored; backout written |
| G3 | Isolation | Target is an isolated lab. No production forest, tenant or trust is reachable from it |
| G4 | Backups | Verified system-state backup of 2 DCs from within 24 h; GPO backup taken; for sync changes, connector config exported |
| G5 | Health baseline | `dcdiag` and `repadmin /replsummary` clean, or known failures recorded before work starts |
| G6 | Window | Maintenance window agreed; service owner and on-call informed |
| G7 | Two-person rule | Tier 0 changes (DCs, schema, krbtgt, sync server, GPOs linked at domain root) need an operator and a reviewer |
| G8 | Evidence | Evidence folder created from `docs/runbooks/hybrid/evidence-template.md` before the first command |

Stop conditions during execution: unexpected replication errors, authentication failures outside the change scope, sync export deletions above the threshold, or any step whose output does not match the expected result. On a stop, run the runbook's rollback section and raise an incident.
