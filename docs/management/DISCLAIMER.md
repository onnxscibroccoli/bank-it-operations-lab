# Disclaimer: synthetic lab data

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize operational work, assign responsibility, and explain decisions to affected people. Consistent priorities and communication prevent urgent work from being lost and help teams explain tradeoffs.

For example: A service desk distinguishes a widespread urgent outage from a single-user request and records who owns each response.

Key terms: **SLA** means service Level Agreement: an agreed service obligation with defined scope. **Escalation** means involving the people with the authority or skills needed to resolve an issue. **CAB** means change Advisory Board: a group used to review proposed operational changes.

**Before using this reference:** Example service targets and rosters are not organizational commitments. Adapt them to actual staffing and contractual responsibilities.

Start with the [plain-English learning path](../knowledge/governance.md) or [glossary](../knowledge/glossary.md). [Current integration and review policy](../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **Synthetic / portfolio lab only.** Everything under `operations/team/` and `docs/management/`
> is invented example material for the `bank-it-operations-lab` portfolio. No real bank, team,
> employee, customer, ticket, incident or change record is described. Persona IDs (`P01`..`P09`),
> ticket IDs (`INC-LAB-*`, `REQ-LAB-*`), change IDs (`CHG-LAB-*`) and all dates, times and figures
> are made up.

## What this material is

- A worked example of how an IT operations team for a small regulated (banking-style) environment
  could define roles, coverage, on-call, ticket priorities, escalation, change review, project
  checkpoints and operational reviews.
- A demonstration of prioritization reasoning and stakeholder communication, written so a reviewer
  can follow (and disagree with) each decision.

## What this material is not

- **Not evidence of real people-management experience.** Parts of this repository were produced
  with help from AI agents/bots. Coordinating agents or bots is **not equivalent** to hiring,
  coaching, appraising, scheduling or being accountable for real employees, and nothing here should
  be read as claiming that it is.
- Not a policy of any real organization, not legal/regulatory advice, and not a substitute for an
  organization's own ITSM, HR, labor-law or regulatory obligations (e.g. on-call compensation,
  working-time rules, supervisory notification deadlines).
- The response/resolution targets are illustrative numbers chosen to be internally consistent, not
  benchmarks.
