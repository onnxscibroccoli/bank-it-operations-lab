# Service management examples (synthetic)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize operational work, assign responsibility, and explain decisions to affected people. Consistent priorities and communication prevent urgent work from being lost and help teams explain tradeoffs.

For example: A service desk distinguishes a widespread urgent outage from a single-user request and records who owns each response.

Key terms: **SLA** means service Level Agreement: an agreed service obligation with defined scope. **Escalation** means involving the people with the authority or skills needed to resolve an issue. **CAB** means change Advisory Board: a group used to review proposed operational changes.

**Before using this reference:** Example service targets and rosters are not organizational commitments. Adapt them to actual staffing and contractual responsibilities.

Start with the [plain-English learning path](../knowledge/governance.md) or [glossary](../knowledge/glossary.md). [Current integration and review policy](../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **Synthetic / portfolio lab only.** See [DISCLAIMER.md](DISCLAIMER.md). No real people,
> tickets or changes. Agents/bots used to build this lab are not equivalent to real employee
> management.

These documents show how the fictional lab team in [`operations/team/`](../../operations/team/)
would run day-to-day service management. Scenarios reference components that exist elsewhere in
this lab (Postgres backup/restore exercise, Entra Conditional Access baseline, AWS CDK stack) so the
examples are concrete, but every ticket, change and meeting is invented.

## Layout

| Path | Purpose |
|---|---|
| [`DISCLAIMER.md`](DISCLAIMER.md) | Scope and limits of this material |
| [`ticket-priority.md`](ticket-priority.md) | P1-P4 definitions (impact x urgency), response/resolution targets, and a triage exercise of 10 sample tickets with reasoning |
| [`change-review.md`](change-review.md) | CAB-style change process: standard / normal / emergency, risk scoring, and worked examples of each |
| [`project-checkpoint.md`](project-checkpoint.md) | Example mid-project checkpoint (RAG status, decisions, re-prioritization) |
| [`operational-review.md`](operational-review.md) | Example monthly operational review (SLA results, incidents, problems, actions) |
| [`stakeholder-updates.md`](stakeholder-updates.md) | Sample communications: P1 incident updates, change notice, project status, "no" / trade-off message |

Team structure, RACI, coverage, on-call and the escalation matrix live in
[`operations/team/`](../../operations/team/).

## How the pieces connect

1. A ticket arrives and is triaged with [`ticket-priority.md`](ticket-priority.md).
2. The priority sets the response clock and, via the
   [escalation matrix](../../operations/team/escalation-matrix.md), who is paged and when.
3. Any fix that changes production goes through [`change-review.md`](change-review.md)
   (emergency path for P1 fixes, with retrospective CAB review).
4. Results roll up into the [monthly operational review](operational-review.md) and project work into
   [checkpoints](project-checkpoint.md); both feed the [stakeholder updates](stakeholder-updates.md).
