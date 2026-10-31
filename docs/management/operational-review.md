# Monthly operational review example: November 2026 (synthetic)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize operational work, assign responsibility, and explain decisions to affected people. Consistent priorities and communication prevent urgent work from being lost and help teams explain tradeoffs.

For example: A service desk distinguishes a widespread urgent outage from a single-user request and records who owns each response.

Key terms: **SLA** means service Level Agreement: an agreed service obligation with defined scope. **Escalation** means involving the people with the authority or skills needed to resolve an issue. **CAB** means change Advisory Board: a group used to review proposed operational changes.

**Before using this reference:** Example service targets and rosters are not organizational commitments. Adapt them to actual staffing and contractual responsibilities.

Start with the [plain-English learning path](../knowledge/governance.md) or [glossary](../knowledge/glossary.md). [Current integration and review policy](../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **Synthetic / portfolio lab only.** All volumes, percentages and events are invented to be
> internally consistent with the other examples. Agents/bots are not equivalent to real
> employees. See [DISCLAIMER.md](DISCLAIMER.md).

**Meeting:** 2026-12-03 14:00-15:00 ET | **Chair:** P01 | **Prepared by:** P02 (service desk), P10
(change/problem) | **Attendees:** all team leads and domain owners, plus the business service
owner for Payments for item 2

## 1. Headline

One P1 this month (INC-LAB-1041), restored in 47 min, within its target. It was caused by a change
we approved, so the main improvement actions are about change review, not the technical fix. P2
target attainment was below objective (8/9). The other measures met their objectives.

## 2. Service levels

| Priority | Tickets | Met target | Attainment | Objective | Status |
|---|---|---|---|---|---|
| P1 | 1 | 1 | 100% | 95% | Met |
| P2 | 9 | 8 | 89% | 95% | **Missed** |
| P3 | 64 | 59 | 92% | 90% | Met |
| P4 | 212 | 197 | 93% | 90% | Met |

The P2 miss was INC-LAB-1047 (teller app slow at 3 branches). It was restored at 9 h 10 min
against an 8 h target. The team waited on the P1 fix as the probable common cause, and when that
didn't help, a branch WAN circuit fault was found after about 6 h. **Learning:** when two incidents
are linked as a possible common cause, set a time-box (2 h) after which the second one is worked
on independently.

## 3. Incidents and problems

| Ref | Summary | Priority | Restored in | Problem record | Status |
|---|---|---|---|---|---|
| INC-LAB-1041 | Payments sign-in blocked by new CA policy | P1 | 47 min | PRB-LAB-0091 | PIR done, 3 actions (see change review) |
| INC-LAB-1042 | Ledger DB backup failed twice | P2 | 5 h 20 min | PRB-LAB-0092 | Root cause: storage quota. Alert added at 80%. |
| INC-LAB-1043 | EDR quarantine on branch PC | P2 | 1 h 05 min | - | Not a compromise: unsigned vendor updater. Allow-listed via normal change. |
| INC-LAB-1047 | Teller app slow, 3 branches | P2 | 9 h 10 min | PRB-LAB-0093 | Carrier fault. Carrier ticket closed, monitoring added. |

## 4. Changes

| Type | Count | Successful | Caused incident | Notes |
|---|---|---|---|---|
| Standard | 38 | 38 | 0 | Patching, access requests |
| Normal | 11 | 10 | 1 | CHG-LAB-3120 → INC-LAB-1041 |
| Emergency | 2 | 2 | 0 | CHG-LAB-3125 (backout), CHG-LAB-3126 (browser patch for an actively exploited CVE) |
| **Change success rate** | 51 | 50 | | **98%** (objective 95%) |
| Emergency share | | | | 3.9% of all changes (watch level: 5%) |

## 5. On-call health

| Measure | November | Comment |
|---|---|---|
| Out-of-hours pages | 23 | 15 came from one noisy disk-space alert on a non-prod host. Tuned on 11-20 (action closed). |
| Nights with > 2 h paged | 1 (P06 on 11-10, WAN alerts during INC-LAB-1047) | Fatigue rule applied: late start next day |
| Missed acknowledgements | 0 | |
| Rota swaps | 2 | Both logged 48 h ahead |

## 6. Coverage and people risks

| Risk | Status | Change since last month |
|---|---|---|
| R1 PostgreSQL backup | Open | P06 paired on the restore exercise. Target is level 2 by end of December (project M4). |
| R2 Security backup overload | Open | P05 started alert-triage training: 2 of 6 sessions done |
| R3 Two desk analysts | Mitigated | No uncovered shifts this month |

## 7. Actions

| # | Action | Owner | Due | Status |
|---|---|---|---|---|
| A1 | Change records list related network/identity changes from the last 14 days | P10 | 11-19 | Done |
| A2 | Re-run named-location check on implementation day | P08 | from CHG-LAB-3131 | Done |
| A3 | CAB calendar highlights same-service changes within 7 days | P10 | 11-26 | **Late**, new date 12-10 (tooling) |
| A4 | Add a 2 h time-box to the linked-incident procedure | P02 | 12-10 | New |
| A5 | Decide on project LAB-PRJ-07 option A/B/C | Sponsor via P01 | 11-17 | Done: option A |

## 8. Decisions needed from leadership

None this month. Item for awareness: if R2 is still open at the end of Q1, the MSSP retainer hours
may need to increase (an estimate will come to the next review).
