# Escalation matrix (synthetic)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize operational work, assign responsibility, and explain decisions to affected people. Consistent priorities and communication prevent urgent work from being lost and help teams explain tradeoffs.

For example: A service desk distinguishes a widespread urgent outage from a single-user request and records who owns each response.

Key terms: **SLA** means service Level Agreement: an agreed service obligation with defined scope. **Escalation** means involving the people with the authority or skills needed to resolve an issue. **CAB** means change Advisory Board: a group used to review proposed operational changes.

**Before using this reference:** Example service targets and rosters are not organizational commitments. Adapt them to actual staffing and contractual responsibilities.

Start with the [plain-English learning path](../../docs/knowledge/governance.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **Synthetic / portfolio lab only.** Roles and personas are placeholders; contacts outside the
> team (Head of Technology, CISO, vendors) are generic roles, not real people or companies.
> Agents/bots are not equivalent to real employees.

Priority definitions and targets come from
[`docs/management/ticket-priority.md`](../../docs/management/ticket-priority.md). Two kinds of
escalation run in parallel:

- **Functional** - move the ticket to someone with more skill or access.
- **Hierarchical** - tell someone with more authority, because the target is at risk or the
  business impact needs a decision (spend, customer communication, invoking DR).

## Functional escalation path

| Level | Who | Enters when |
|---|---|---|
| L1 | Service desk (P03/P04, lead P02) | Every ticket starts here (or with on-call out of hours) |
| L2 | Primary on-call (out of hours) or domain backup (business hours) | L1 cannot resolve with a KB article within 30 min (P3) or immediately (P1/P2) |
| L3 | Domain primary owner (see coverage matrix) | L2 has no workaround within 30 min (P1) / 2 h (P2) / 1 business day (P3) |
| L4 | Vendor support (cloud provider, database support, identity provider, MSSP) | L3 suspects a product defect or the provider's platform, or the domain primary is unavailable (coverage risk R1) |

## Hierarchical escalation by priority and elapsed time

Times are measured from ticket creation. "Notify" means a page or call for P1/P2 and a ticket
update plus chat message for P3/P4.

| Priority | At start | No acknowledgement | 50% of restore target | 75% of restore target | Target breached |
|---|---|---|---|---|---|
| **P1** (restore 4 h) | Page primary on-call **and** duty manager; duty manager becomes incident commander (IC) | 15 min: page secondary; 30 min: call P01 | 2 h: P01 informs Head of Technology; IC decides whether to invoke DR / business continuity | 3 h: Head of Technology + business owner decide on customer communication | P01 and Head of Technology; post-incident review mandatory |
| **P2** (restore 8 h) | Page primary on-call (24x7); desk informs P02 | 30 min: page secondary; 60 min: duty manager | 4 h: duty manager | 6 h: P01 | P01; reviewed at monthly operational review |
| **P3** (resolve 3 business days) | Queue for domain team | 4 business hours: P02 reassigns | 1.5 days: P02 | 2.25 days: domain primary owner + P02 agree plan | P01 informed via weekly breach report |
| **P4** (resolve 10 business days) | Queue | 1 business day: P02 | - | - | P02; batch-reviewed weekly |

### Security overlay

Any ticket that may be a security incident (suspected compromise, data exposure, malware,
unexpected privileged access) is **also** routed to security on-call regardless of its priority.

| Trigger | Escalate to | Within |
|---|---|---|
| Suspected security incident of any priority | Security on-call (P09 / P08) | 15 min |
| Confirmed compromise, or customer data possibly exposed | CISO (outside team) + P01 | 30 min of confirmation |
| Possible regulatory or legal notification | CISO engages Compliance and Legal (outside team) | CISO decides; the team does not decide on notification |

The ops team never decides on regulatory notification itself. Its job is to give accurate facts
and timestamps quickly to the people who do.

## Roles during a P1

| Role | Default holder | Responsibilities |
|---|---|---|
| Incident commander (IC) | Duty manager (out of hours) / P01 (business hours) | Owns the timeline and decisions, assigns work, sets the next update time; does not do hands-on fixing |
| Technical lead | Primary on-call or domain primary owner | Diagnosis and fix; proposes emergency changes |
| Communications lead | P02 (business hours) / IC (out of hours) | Stakeholder updates on the set cadence (templates in [`stakeholder-updates.md`](../../docs/management/stakeholder-updates.md)) |
| Scribe | Secondary on-call or a desk analyst | Timestamped log in the incident ticket |

## Contact directory (role-based, fictional)

| Contact | Used for | Channel (example) |
|---|---|---|
| Duty manager | P1 command, emergency change approval | Paging tool rota "ops-duty-manager" |
| Primary / secondary technical | P1/P2 response | Paging tool rota "ops-technical" |
| Security on-call | Security triage | Paging tool rota "ops-security" |
| Head of Technology | P1 at 2 h, DR invocation | Phone tree (held by P01) |
| CISO | Confirmed security incidents | Phone tree (held by P09) |
| Business service owners (Payments, Lending, Branch ops) | Impact confirmation, customer comms decisions | Listed per service in the service catalogue (not part of this lab) |
| Vendors | L4 technical escalation | Contract reference in vendor register (not part of this lab) |
