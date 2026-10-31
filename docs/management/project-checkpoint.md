# Project checkpoint example (synthetic)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize operational work, assign responsibility, and explain decisions to affected people. Consistent priorities and communication prevent urgent work from being lost and help teams explain tradeoffs.

For example: A service desk distinguishes a widespread urgent outage from a single-user request and records who owns each response.

Key terms: **SLA** means service Level Agreement: an agreed service obligation with defined scope. **Escalation** means involving the people with the authority or skills needed to resolve an issue. **CAB** means change Advisory Board: a group used to review proposed operational changes.

**Before using this reference:** Example service targets and rosters are not organizational commitments. Adapt them to actual staffing and contractual responsibilities.

Start with the [plain-English learning path](../knowledge/governance.md) or [glossary](../knowledge/glossary.md). [Current integration and review policy](../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **Synthetic / portfolio lab only.** Project, dates, budget and people are invented. Agents/bots
> are not equivalent to real employees. See [DISCLAIMER.md](DISCLAIMER.md).

**Project:** LAB-PRJ-07 Database resilience uplift
**Checkpoint:** #3 of 5, 2026-11-17 (week 6 of 12)
**Sponsor:** Head of Technology (outside team) | **Project owner:** P01 | **Lead:** P07
**Goal:** Prove that the ledger lab database can be restored within an RTO of 2 h and an RPO of
15 min, with evidence produced automatically (builds on this lab's Postgres backup/restore
exercise).

## Status summary

| Area | RAG | Trend | Comment |
|---|---|---|---|
| Scope | Green | → | No change requests |
| Schedule | **Amber** | ↓ | Milestone M3 is 1 week late (see below) |
| Budget | Green | → | 38% spent at 50% elapsed (example figures) |
| Risk | Amber | → | Single DBA (coverage risk R1) still open |
| Overall | **Amber** | ↓ | Recoverable if the decision below is taken today |

## Milestones

| ID | Milestone | Planned | Forecast | Status |
|---|---|---|---|---|
| M1 | Backup policy and RPO/RTO agreed with business owner | 10-13 | 10-13 | Done |
| M2 | Automated restore exercise in CI with evidence bundle | 10-27 | 10-29 | Done (2 days late, no knock-on) |
| M3 | Point-in-time recovery (PITR) to 15 min tested | 11-17 | **11-24** | In progress |
| M4 | DR runbook walkthrough with P06 as second operator | 12-08 | 12-08 | Not started |
| M5 | Handover to BAU, closure report | 12-18 | 12-18 | Not started |

## Why M3 slipped (plain facts)

- P07 spent about 1.5 days on INC-LAB-1042 (backup failures, P2) during week 5. Operational work
  correctly took priority over project work, as the team's working agreement says.
- CHG-LAB-3128 (RDS minor upgrade, which PITR testing depends on) was deferred out of the
  month-end freeze to 12-03.

## Decision requested (sponsor)

| Option | Effect | Cost / risk |
|---|---|---|
| A. Accept 1-week slip on M3, keep M4/M5 dates | Uses the plan's float. M4 still has 1 week of float left. | No extra cost. Risk: no float remains if anything else slips. |
| B. Test PITR on current version now, re-test after upgrade | M3 back on schedule | About 2 extra days of P07 time, taken from the improvement backlog |
| C. Pull P06 in full-time for 2 weeks | M3 and M4 earlier; closes R1 sooner | P06's AWS backlog (2 normal changes) slips 2 weeks |

**Recommendation: A.** Most of the slip came from incident work, and the root cause of
INC-LAB-1042 has been fixed. Option B duplicates effort. Option C's cross-training benefit is
already planned in M4. **Re-check trigger:** if M3 is not done by 11-24, escalate to option C at
the next checkpoint.

## Decisions log

| Date | Decision | By |
|---|---|---|
| 10-13 | RPO 15 min / RTO 2 h agreed for ledger lab DB | Sponsor + business owner |
| 11-03 | P07 may pause project work for P1/P2 incidents without asking for approval | P01 |
| 11-17 | (pending) Option A / B / C | Sponsor |

## Next checkpoint

2026-12-01, or earlier if any milestone forecast moves by more than 1 week.
