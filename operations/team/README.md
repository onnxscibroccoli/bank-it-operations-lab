# Lab IT operations team model (synthetic)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize operational work, assign responsibility, and explain decisions to affected people. Consistent priorities and communication prevent urgent work from being lost and help teams explain tradeoffs.

For example: A service desk distinguishes a widespread urgent outage from a single-user request and records who owns each response.

Key terms: **SLA** means service Level Agreement: an agreed service obligation with defined scope. **Escalation** means involving the people with the authority or skills needed to resolve an issue. **CAB** means change Advisory Board: a group used to review proposed operational changes.

**Before using this reference:** Example service targets and rosters are not organizational commitments. Adapt them to actual staffing and contractual responsibilities.

Start with the [plain-English learning path](../../docs/knowledge/governance.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **Synthetic / portfolio lab only.** The ten personas below are invented role placeholders
> (`P01`..`P10`), not real people. Agents/bots used to build this lab are **not equivalent** to
> managing real employees. See [`docs/management/DISCLAIMER.md`](../../docs/management/DISCLAIMER.md).

A fictional 10-person IT operations team supporting a small bank's internal platforms: service desk,
Windows/Linux servers, AWS landing zone, PostgreSQL, Entra ID, and first-line security monitoring.
Business hours are 08:00-18:00 America/New_York (ET), Monday-Friday; critical services are
supported 24x7 through on-call.

## Layout

| Path | Purpose |
|---|---|
| [`team-model.md`](team-model.md) | Roster, role descriptions, RACI, skills coverage matrix, single-points-of-failure |
| [`on-call.md`](on-call.md) | Service-desk shift pattern, on-call tiers, rotation rules, handover, fatigue limits |
| [`oncall-rotation.csv`](oncall-rotation.csv) | Example 8-week rotation (primary / secondary / duty manager / security) |
| [`escalation-matrix.md`](escalation-matrix.md) | Functional and hierarchical escalation by priority and elapsed time, plus vendor and business contacts |

Ticket priorities, change review, checkpoints, operational reviews and sample communications are in
[`docs/management/`](../../docs/management/).

## Design choices

- **Every technical domain has a named primary and backup** so no one person is a single point of
  failure; where that is not yet true it is listed as a risk in [`team-model.md`](team-model.md).
- **The person who implements a change never approves it** (segregation of duties). The Change &
  Problem Manager (`P10`) chairs CAB; the Ops Manager (`P01`) is the escalation point above CAB.
- **On-call load is spread over four engineers** with a one-week primary shift, a following
  secondary shift, and a mandatory rest week (see [`on-call.md`](on-call.md)).
