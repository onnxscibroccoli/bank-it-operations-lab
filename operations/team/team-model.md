# Team model: roles, RACI and coverage (synthetic)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize operational work, assign responsibility, and explain decisions to affected people. Consistent priorities and communication prevent urgent work from being lost and help teams explain tradeoffs.

For example: A service desk distinguishes a widespread urgent outage from a single-user request and records who owns each response.

Key terms: **SLA** means service Level Agreement: an agreed service obligation with defined scope. **Escalation** means involving the people with the authority or skills needed to resolve an issue. **CAB** means change Advisory Board: a group used to review proposed operational changes.

**Before using this reference:** Example service targets and rosters are not organizational commitments. Adapt them to actual staffing and contractual responsibilities.

Start with the [plain-English learning path](../../docs/knowledge/governance.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **Synthetic / portfolio lab only.** Personas are placeholders, not employees. Not evidence of
> real people-management experience. See [`docs/management/DISCLAIMER.md`](../../docs/management/DISCLAIMER.md).

## Roster

| ID | Role | Reports to | Core accountabilities | On-call pool |
|---|---|---|---|---|
| P01 | IT Operations Manager | Head of Technology (outside team) | Service performance against targets, prioritization of the team's work, budget, staffing, final internal escalation point | Duty manager |
| P02 | Service Desk Lead | P01 | Ticket intake and triage quality, desk staffing, knowledge base, customer satisfaction | Duty manager |
| P03 | Service Desk Analyst (early shift) | P02 | First-line resolution, triage, user communication | - |
| P04 | Service Desk Analyst (late shift) | P02 | First-line resolution, triage, user communication | - |
| P05 | Systems Engineer (Windows/Linux) | P01 | Server builds, patching, backups at OS level, monitoring | Technical |
| P06 | Cloud Engineer (AWS) | P01 | AWS accounts, VPC, IaC (CDK), cost and guardrails | Technical |
| P07 | Database Administrator (PostgreSQL) | P01 | Database availability, backup/restore exercises, performance | Technical |
| P08 | Identity & Access Engineer (Entra ID) | P01 | Conditional Access, privileged roles, joiner/mover/leaver automation | Technical |
| P09 | Security Operations Analyst | P01 (dotted line to CISO, outside team) | Alert triage, vulnerability tracking, security incident first response | Security |
| P10 | Change & Problem Manager | P01 | CAB chair, change calendar, problem records, post-incident reviews | Duty manager |

Span of control: P01 has 7 direct reports plus P02's two analysts indirectly, which is within a
manageable range for one manager; P02 acts as team lead for the desk.

## RACI

R = Responsible (does the work), A = Accountable (one per row, signs off), C = Consulted,
I = Informed.

| Activity | P01 | P02 | P03/P04 | P05 | P06 | P07 | P08 | P09 | P10 |
|---|---|---|---|---|---|---|---|---|---|
| Ticket intake and triage | I | A | R | C | C | C | C | C | I |
| P1 incident command | A | C | I | R* | R* | R* | R* | R* | C |
| P1 stakeholder communication | A | R | I | C | C | C | C | C | C |
| Security incident first response | I | I | I | C | C | C | C | R | I |
| Security incident decision to escalate to CISO | A | I | - | - | - | - | C | R | I |
| Standard change execution | I | I | R** | R | R | R | R | I | A |
| Normal change approval (CAB) | C | C | - | C | C | C | C | C | A/R |
| Emergency change approval | A | I | - | C | C | C | C | C | R |
| OS patching | I | I | - | A/R | C | C | - | C | C |
| AWS guardrails and IaC | I | - | - | C | A/R | - | C | C | C |
| Database backup/restore exercise | I | - | - | C | C | A/R | - | I | I |
| Conditional Access / privileged roles | I | - | - | - | C | - | A/R | C | C |
| Quarterly access review | A | I | - | C | C | C | R | C | I |
| Problem management / root cause | I | C | I | C | C | C | C | C | A/R |
| Monthly operational review | A | R | I | C | C | C | C | C | R |
| On-call rota and fatigue limits | A | C | - | C | C | C | C | C | R |
| Knowledge base articles | I | A | R | R | R | R | R | R | C |

`R*` = the on-call or domain engineer for the affected service is Responsible for technical
resolution; the incident commander role is described in [`escalation-matrix.md`](escalation-matrix.md).
`R**` = desk analysts may run only pre-approved standard changes from the catalogue (e.g. password
reset, MFA re-registration with identity proofing).

## Skills coverage matrix

`3` = primary owner, `2` = trained backup (can handle P1 alone), `1` = can follow a runbook,
blank = none.

| Domain | P01 | P02 | P03 | P04 | P05 | P06 | P07 | P08 | P09 | P10 | Primary/backup |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Service desk / end-user | 1 | 3 | 2 | 2 | 1 | | | 1 | | 1 | P02 / P03, P04 |
| Windows/Linux servers | 1 | | | | 3 | 2 | 1 | | 1 | | P05 / P06 |
| AWS (VPC, IAM, CDK) | | | | | 2 | 3 | | 1 | 1 | | P06 / P05 |
| PostgreSQL | | | | | 1 | 1 | 3 | | | | P07 / **gap** |
| Entra ID / Conditional Access | 1 | 1 | 1 | 1 | | 1 | | 3 | 2 | | P08 / P09 |
| Security monitoring | | | | | 1 | 1 | | 2 | 3 | | P09 / P08 |
| Backup and restore | | | | | 2 | 1 | 3 | | | | P07 / P05 |
| Change / problem process | 2 | 2 | | | | | | | | 3 | P10 / P01, P02 |

### Coverage risks found (and planned actions)

| # | Risk | Effect | Action | Owner | Due (example) |
|---|---|---|---|---|---|
| R1 | PostgreSQL has no level-2 backup | P1 database incident while P07 is on leave depends on vendor support | Pair P06 with P07 on the backup/restore exercise until P06 reaches level 2; restore runbook walkthrough each month | P07 | +8 weeks |
| R2 | Security monitoring backup (P08) is also Identity primary | An identity-driven security incident overloads one person | Cross-train P05 to level 2 on alert triage; external MSSP retainer for overflow | P09 | +12 weeks |
| R3 | Only two desk analysts | One absence leaves a shift uncovered | P02 covers the gap; P10 trained to level 1 as reserve; leave requests capped at one analyst at a time | P02 | in place |

## Working agreements

- Planned leave needs the domain backup to be available; P01 approves overlapping leave only if
  the coverage matrix still shows a level-2 person for each domain.
- Work is prioritized in this order: active P1/P2 incidents > security fixes with a regulatory
  deadline > changes already on the CAB calendar > project work > improvement backlog. See
  [`docs/management/ticket-priority.md`](../../docs/management/ticket-priority.md).
- Each engineer reserves about 20% of the week for operational improvement (runbooks, automation,
  cross-training) so that coverage risks actually close.
