# Change review process, CAB-style (synthetic)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize operational work, assign responsibility, and explain decisions to affected people. Consistent priorities and communication prevent urgent work from being lost and help teams explain tradeoffs.

For example: A service desk distinguishes a widespread urgent outage from a single-user request and records who owns each response.

Key terms: **SLA** means service Level Agreement: an agreed service obligation with defined scope. **Escalation** means involving the people with the authority or skills needed to resolve an issue. **CAB** means change Advisory Board: a group used to review proposed operational changes.

**Before using this reference:** Example service targets and rosters are not organizational commitments. Adapt them to actual staffing and contractual responsibilities.

Start with the [plain-English learning path](../knowledge/governance.md) or [glossary](../knowledge/glossary.md). [Current integration and review policy](../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> **Synthetic / portfolio lab only.** Change records, dates and people are invented. The process
> is a teaching example loosely in the style of ITIL change enablement, not any organization's
> policy. Agents/bots are not equivalent to real employees. See [DISCLAIMER.md](DISCLAIMER.md).

## Change types

| Type | What it is | Approval | Lead time | Examples |
|---|---|---|---|---|
| **Standard** | Low-risk, repeatable, with a documented procedure that CAB has pre-approved as a *change model* | Pre-approved; logged, no per-change CAB | None beyond the schedule | Monthly non-prod OS patching, password/MFA reset with identity proofing, adding a user to a pre-approved group |
| **Normal** | Anything else that is planned | Risk-based: Low → P10 (Change Manager); Medium/High → weekly CAB | 5 business days (Low: 2) | Enabling a Conditional Access policy, RDS parameter change, new AWS VPC endpoint |
| **Emergency** | Needed to restore service in a P1/P2 or close an actively exploited vulnerability; can't wait for CAB | Emergency CAB (ECAB): duty manager/P01 **plus** one technical approver who is not the implementer; verbal OK recorded in the ticket | Immediate | Rolling back a change that caused a P1, emergency patch for an exploited CVE |

Rule for every type: **the implementer cannot approve their own change**.

## Risk score (normal changes)

Score each factor from 1 to 3 and add them up (range 5-15):

| Factor | 1 | 2 | 3 |
|---|---|---|---|
| Blast radius | One system, non-prod | One prod service | Several prod services / all users |
| Complexity | Config toggle, scripted | Multi-step, scripted | Manual, multi-team |
| Backout | Instant, tested | Tested, > 30 min | Untested or not possible |
| Testing | Tested in non-prod with evidence | Partial | None |
| Timing | Low-usage window | Business hours, non-critical | Near a business deadline (month-end, cut-off) |

**5-7 Low** (Change Manager approves) | **8-11 Medium** (CAB) | **12-15 High** (CAB + P01 + business
owner sign-off; a test run in non-prod with evidence is mandatory).

## CAB

- **When:** weekly, Thursday 10:00-10:45 ET (example).
- **Members:** P10 (chair), P01, domain owners of the services affected, P09 (security), P02 (user
  impact and service-desk readiness). Business service owner attends for High-risk changes.
- **Inputs:** change records submitted by Monday 17:00 ET, each with: description and reason, risk
  score, implementation plan, test evidence, backout plan, communication plan, schedule and
  owner, and a link to the evidence bundle where one exists (this lab's `evidence/**` convention).
- **Outcomes:** Approved / Approved with conditions / Deferred (with reason) / Rejected.
- **Freeze windows:** month-end (last 2 business days and first business day), and public holiday
  weeks. Only emergency changes are allowed during a freeze.
- **Post-implementation review (PIR):** required for every emergency change, every failed change,
  and every change that caused an incident.

## Worked example 1: standard change

**CHG-LAB-3101: Monthly Linux patching, non-production** (change model SM-04, pre-approved by CAB
2026-09-03, valid 12 months)

| Field | Value |
|---|---|
| Implementer | P05 |
| Window | 2026-11-12 19:00-21:00 ET |
| Procedure | Runbook SM-04: snapshot → patch → reboot → health checks → evidence capture |
| Approval | Pre-approved model, logged by P10. No CAB discussion. |
| Result | 14/14 hosts patched, health checks passed, evidence attached |

A change stops qualifying as standard if it hits a host the model doesn't list, if its runbook
step fails, or if the change model has expired. In those cases it is raised as a normal change.

## Worked example 2: normal change (Medium risk, approved with conditions)

**CHG-LAB-3120: Enable Conditional Access policy "Block high sign-in risk"** (moves the lab's
CA005 from report-only to enabled. See `identity/entra/` on the integration branch for the
synthetic baseline.)

| Field | Value |
|---|---|
| Requester / implementer | P08 |
| Reason | Report-only data shows the policy would have blocked 3 risky sign-ins in 30 days and produced no false positives on privileged accounts. Enabling it closes an audit finding. |
| Risk score | Blast radius 3, complexity 1, backout 1 (switch back to report-only, about 5 min), testing 2 (report-only data, no non-prod tenant), timing 1 → **8 = Medium → CAB** |
| Plan | Tue 2026-11-10 07:30 ET: enable the policy. Break-glass accounts stay excluded (baseline rule BASE-001). Run the offline validator before and after. P02 briefs the desk on the expected "blocked by policy" calls. |
| Backout | Set state back to `enabledForReportingButNotEnforced`. Trigger: more than 2 verified false-positive blocks, or any block on a payments or treasury user. |
| CAB 2026-11-05 decision | **Approved with conditions**: (1) implement before 08:00 ET, outside the payments peak; (2) P08 monitors sign-in logs until 10:00; (3) P09 confirms named-location list is current. |

## Worked example 3: emergency change (linked to the P1 in the triage exercise)

At 08:15 ET on 2026-11-10, payments users were blocked (INC-LAB-1041, P1). Condition 3 above had
been signed off from a list exported on 11-03. The new VPN egress range put in place on 11-07 was
not on that list, so the identity provider scored those sign-ins as anonymous-IP risk.

**CHG-LAB-3125: Emergency backout of CHG-LAB-3120**

| Field | Value |
|---|---|
| Implementer | P08 |
| ECAB approvers | P01 (incident commander) + P06 (technical, not the implementer), verbally at 08:52 ET, recorded in INC-LAB-1041 |
| Action | CA005 back to report-only at 08:55 ET. Payments sign-ins confirmed working at 09:02 ET. |
| Risk accepted | High-risk sign-ins are not blocked again until the re-run. MFA (CA002) still applies, so residual risk is small for a few days. |
| Follow-up | PIR on 2026-11-12. New normal change CHG-LAB-3131 adds the VPN range as a trusted named location, then re-enables the policy. |

### PIR summary (2026-11-12)

| Question | Answer |
|---|---|
| What went well | The backout plan existed and took 3 minutes. The trigger was clear. Users were informed within 15 minutes. |
| What went wrong | A CAB condition was checked against data that was 7 days old. The VPN change (CHG-LAB-3112) and the CA change were never linked on the change calendar. |
| Actions | (1) Change records must list dependencies on network/identity changes in the last 14 days; owner P10, due 11-19. (2) The named-location check is re-run on implementation day; owner P08, applies from CHG-LAB-3131. (3) The CAB calendar view highlights changes to the same service within 7 days; owner P10, due 11-26. |
| Blame | None. The process gap was the cause, so the fix is in the process. |

## Example: deferred change

**CHG-LAB-3128: RDS minor version upgrade (ledger lab DB)**. Risk score 10 (Medium). It was
requested for 2026-11-30, which falls in the month-end freeze. **Deferred** to 2026-12-03. Another
reason: P07's backup is level 1 only (coverage risk R1), so CAB asked for P06 to pair with P07 on
the change as cross-training.
