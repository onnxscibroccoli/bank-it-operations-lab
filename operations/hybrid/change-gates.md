# Change gates for hybrid runbooks

> **Execution status: NOT_EXECUTED.** These gates have never been exercised. No runbook in this lab may be executed until every gate below is met.

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Operate local Windows directory services and their connections to cloud identity. Separating directory, name-resolution, policy, and synchronization problems avoids broad changes that obscure the cause.

For example: A user can reach a server by address but not by name, so an operator investigates name resolution before changing account permissions.

Key terms: **AD DS** means active Directory Domain Services: a directory used to manage Windows identities and resources. **DNS** means domain Name System: translates names into resource-location information. **GPO** means group Policy Object: a set of Windows policy settings. **Hybrid identity** means identity management spanning local directory systems and cloud services.

**Before using this reference:** Directory, DNS, policy, and synchronization changes can affect many users. Use the documented permissions and change gates; no live execution is implied.

Start with the [plain-English learning path](../../docs/knowledge/identity.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->



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
