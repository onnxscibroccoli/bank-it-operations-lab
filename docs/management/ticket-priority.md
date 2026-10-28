# Ticket priority definitions and triage exercise (synthetic)

> **Synthetic / portfolio lab only.** Tickets, users, times and targets are invented; targets are
> illustrative, not benchmarks. Agents/bots are not equivalent to real employees. See
> [DISCLAIMER.md](DISCLAIMER.md).

## Priority = impact x urgency

**Impact** - how much of the business is affected:

| Impact | Meaning |
|---|---|
| High | A critical service (payments, online banking back office, core identity, customer data) is down or badly degraded for many users, **or** there is a credible security or data-integrity risk |
| Medium | A service is degraded, a department or a business-critical individual is blocked, or resilience is lost (e.g. backups failing) with no current outage |
| Low | One user or a non-critical function; a workaround exists |

**Urgency** - how fast the impact grows or how close a hard deadline is:

| Urgency | Meaning |
|---|---|
| High | Harm is happening now or grows by the hour; regulatory/settlement cut-off today |
| Medium | Must be fixed within days; deadline this week |
| Low | Can wait for planned work |

| | Urgency High | Urgency Medium | Urgency Low |
|---|---|---|---|
| **Impact High** | P1 | P2 | P3 |
| **Impact Medium** | P2 | P3 | P3 |
| **Impact Low** | P3 | P4 | P4 |

Overrides: any **confirmed** security incident is at least P2, and a suspected one is triaged by
security on-call within 15 min regardless of priority. Seniority of the requester **does not**
change priority. A high-impact person being blocked can raise urgency; their title cannot.

## Targets

| Priority | Name | Hours covered | Response (acknowledge + first action) | Restore / resolve target | Update cadence | Escalation |
|---|---|---|---|---|---|---|
| P1 | Critical | 24x7 | 15 min | Service restored (workaround OK) in 4 h | Every 30 min | [matrix](../../operations/team/escalation-matrix.md) |
| P2 | High | 24x7 | 30 min | 8 h | Every 2 h | matrix |
| P3 | Medium | Business hours | 4 business hours | 3 business days | On status change, at least every 2 days | matrix |
| P4 | Low | Business hours | 1 business day | 10 business days or scheduled release | On status change | matrix |

"Restore" means the user/business impact has ended (a workaround counts). Root cause is tracked
afterwards as a problem record by P10 and has no clock in this table.

Example service-level objective: at least 95% of P1/P2 and 90% of P3/P4 meet their targets each
month (reported in the [operational review](operational-review.md)).

## Triage exercise: Tuesday morning queue

Scenario: it is **Tuesday 08:40 ET** (synthetic date 2026-11-10). P03 is on the early shift, P02
has just arrived, P06 is primary on-call (see the example rota). Ten tickets are in the queue.

| Ticket | Summary (as reported) | Impact | Urgency | Priority | Reasoning |
|---|---|---|---|---|---|
| INC-LAB-1041 | Payments team (12 users) cannot sign in to the payments approval app since 08:15; error mentions Conditional Access | High | High | **P1** | Critical service, many users, wire cut-off at 16:00 ET. Error points at identity, so page P08 as domain owner and P06 as on-call. Check recent CA changes first (CHG history). |
| INC-LAB-1042 | Nightly PostgreSQL backup for the ledger lab DB failed twice in a row | Medium | High | **P2** | No outage, but there is no recent restore point, and a third failure makes the RPO breach worse. Resilience loss on a data-integrity-critical system raises urgency. |
| INC-LAB-1043 | EDR alert: unsigned binary run on a branch PC, quarantined automatically | Medium (unknown) | High | **P2 + security overlay** | Treated as a suspected security incident: security on-call (P09) triages within 15 min. The automatic quarantine lowers urgency to below P1, but scope is unknown until P09 checks for lateral movement. |
| REQ-LAB-2210 | Executive assistant: "CFO's office printer jammed, URGENT, CFO says P1" | Low | Medium | **P4** | One device, and another printer is 10 m away. The requester's title does not raise priority. The desk still sends the workaround within minutes because that costs almost nothing. The reasoning is written in the ticket so the requester gets an explanation, not just a lower number (see the "trade-off / polite no" template in [stakeholder-updates.md](stakeholder-updates.md)). |
| INC-LAB-1044 | Lending officer cannot open the loan document system; a customer closing is at 11:00 | Low (1 user) | High | **P3, expedited** | Single user, so impact Low, but the hard deadline today makes urgency High → P3. Desk tries a workaround first (alternate workstation / web client) before 10:30 and records the deadline in the ticket. |
| INC-LAB-1045 | AWS cost anomaly alert: NAT gateway data transfer 4x normal since Sunday | Medium | Medium | **P3** (+ security check) | Cost impact, no outage. It could be misconfiguration or data exfiltration, so P09 is asked for a quick look at VPC flow logs. If anything is suspicious it is re-prioritized to P2. |
| REQ-LAB-2211 | New joiner starting Monday needs accounts and laptop | Low | Medium | **P4** (scheduled) | Standard joiner request with a date; scheduled, not urgent today. |
| INC-LAB-1046 | Intranet page shows the wrong holiday calendar | Low | Low | **P4** | Cosmetic; workaround is the HR portal. |
| INC-LAB-1047 | Teller application slow at 3 branches (screens take 20-30 s) | High | Medium | **P2** | Customer-facing, several sites, degraded rather than down. Possibly related to INC-LAB-1041 (identity) or the network. Linked to 1041 as a possible common cause. |
| REQ-LAB-2212 | Auditor requests last quarter's privileged access review evidence by Friday | Medium | Medium | **P3** | Regulatory relevance and a fixed deadline. P08 owns it. It does not compete with incident work today but must be started by Wednesday. |

### Order of work and assignment at 08:45 ET

1. **INC-LAB-1041 (P1)**. Duty manager role passes to P01 (business hours) as incident commander.
   P08 is technical lead, P06 supports, and P02 runs communications (first update by 09:00, see
   [stakeholder-updates.md](stakeholder-updates.md)). INC-LAB-1047 is linked as a possible common
   cause.
2. **INC-LAB-1043 (P2, security)**. P09 starts in parallel because it uses a different skill set and
   person, so there is no conflict with the P1.
3. **INC-LAB-1042 (P2)**. P07 takes it. If the cause is not found within 2 h, P07 takes a manual
   backup and checks it with the restore exercise.
4. **INC-LAB-1047 (P2)**. P05 checks network and server health while waiting to see whether the
   P1 fix resolves it.
5. **INC-LAB-1044 (P3, expedited)**. P03 works the workaround before 10:30.
6. **REQ-LAB-2212, INC-LAB-1045 (P3)**. Both are scheduled for today after the P1. P09 is asked
   for a 15-minute flow-log check on 1045 once 1043 is contained.
7. **P4s**. P04 picks these up on the late shift. P03 sends the printer workaround now (2 minutes).

### What the exercise demonstrates

- Priority comes from impact and urgency, not from who is asking or how loudly.
- Parallel work is planned by **skill and person**, so a P1 does not stall unrelated P2s.
- Deadlines (wire cut-off, customer closing, auditor) raise urgency, and the deadline is written
  into the ticket.
- Re-prioritization triggers are stated up front (1045 → P2 if flow logs look suspicious;
  1047 → P1 if more branches are affected).
