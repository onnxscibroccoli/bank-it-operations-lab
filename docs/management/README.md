# Service management examples (synthetic)

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
