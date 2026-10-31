# PIM lifecycle reference: Microsoft Entra roles

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Control who can use a system and what they are allowed to do. Reviewing access reduces unnecessary exposure of information and privileged operations.

For example: A colleague changes jobs; their old administrator access should be reviewed instead of silently carried into the new role.

Key terms: **Authentication** means checking a claimed identity. **Authorization** means deciding which actions an identified person or program may perform. **RBAC** means role-based access control assigns permissions through roles. **PIM** means privileged Identity Management controls eligibility and time-limited activation of powerful roles. **Conditional Access** means a policy decision based on signals such as identity, device, and sign-in conditions.

**Before using this reference:** Real tenant operations require separately reviewed permissions and licensing; this document is not authorization to access employee records.

Start with the [plain-English learning path](../../../docs/knowledge/identity.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Reference only; this repository configures no tenant. A real tenant needs Entra ID P2 or Entra ID
> Governance ([licensing](licensing-prerequisites.md)); the free-tier fallback is at the end.
> Sources: [What is PIM](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure),
> [role settings](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings),
> [activate a role](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-activate-role),
> [PIM deployment plan](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-deployment-plan),
> [PIM Graph APIs](https://learn.microsoft.com/en-us/graph/api/resources/privilegedidentitymanagementv3-overview).

## States

```
                 assign eligible (time-bound)              activate (MFA, approval, justification)
  [no access] ─────────────────────────────────▶ [eligible] ─────────────────────────────────────▶ [active: Activated]
       ▲                                             │  ▲                                                │
       │ eligibility ends or is removed by review    │  └────────── activation expires (<= max hours) ───┘
       └─────────────────────────────────────────────┘                  or the user deactivates
  [active: Assigned]  direct active assignment (permanent or time-bound); permanent reserved for break-glass
```

| Lifecycle step | Graph object (read) | Inventory field |
|---|---|---|
| Eligible assignment | `unifiedRoleEligibilityScheduleInstance` | `state=eligible`, `assignmentType=Eligible` |
| Activation | `unifiedRoleAssignmentScheduleInstance`, `assignmentType=Activated` | `state=active`, `startDateTime` / `endDateTime` |
| Direct active | `unifiedRoleAssignmentScheduleInstance`, `assignmentType=Assigned` | `permanent=true` when `endDateTime` is null |
| Through a group | `memberType=Group` (role-assignable group) | `memberType` |

## Bank baseline (what `baseline.json` and `inventory.py` enforce)

| Setting | Bank value | Why / rule |
|---|---|---|
| Standing (permanent active) privileged access | Only the 2 break-glass accounts | INV-001, INV-007 |
| Active Global Administrators | <= 4 including break-glass | Microsoft recommends fewer than five; INV-002 |
| Activation maximum duration | 8 h (PIM allows 1 to 24 h) | INV-006 |
| On activation | Require MFA (prefer an authentication context with phishing-resistant strength), justification and ticket number | PIM role settings |
| Approval | Required for tier-0 roles (GA, Privileged Role Admin, Privileged Authentication Admin), at least 2 approvers who are not the requester | avoids the approval lock-out Microsoft describes in its emergency-access guidance |
| Eligible assignment duration | Time-bound, at most 12 months, renewed through an access review | INV-003 flags expired data that still appears |
| Guests and service principals | No privileged roles for guests; no tier-0 roles for service principals | INV-004, INV-005 |
| Notifications | Role activation and assignment alerts to the security mailbox | PIM role settings |

## Operational flow

1. **Request**: the admin raises a ticket naming role, scope and duration.
2. **Assign eligible** (Privileged Role Administrator): time-bound eligibility with `directoryScopeId` as
   narrow as the task allows (an administrative unit rather than `/` where possible).
3. **Activate**: the admin activates in PIM, completes MFA, enters justification and ticket; tier-0 needs approval.
4. **Use**: the work happens inside the activation window, from a privileged access workstation.
5. **Expire or deactivate**: the activation ends at `endDateTime`; deactivate early when done.
6. **Review**: quarterly access review of eligible and active assignments to privileged roles
   ([access-review-lifecycle.md](access-review-lifecycle.md)); a deny removes the eligibility.
7. **Evidence**: inventory report (`inventory.py --json-out --md-out --csv-out`) before and after the
   review, PIM audit history export, ticket IDs.

## Licence-expiry hazard

If the P2 or Governance licence lapses, Microsoft documents that **eligible assignments are removed** and
**active time-bound assignments become permanent**. Monitor licence expiry. After a lapse, run the
inventory in `free` mode and treat every remaining assignment as standing access (INV-001 review).

## Free-tier fallback

Eligibility and activation do not exist without PIM. Use dedicated cloud-only admin accounts, keep the
number of role holders minimal, add and remove direct role assignments under change tickets, and
reconcile with `inventory.py --mode free` (scenario `free-tier`) on a fixed schedule.
