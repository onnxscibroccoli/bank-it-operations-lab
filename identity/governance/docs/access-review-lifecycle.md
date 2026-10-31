# Access review lifecycle reference

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Control who can use a system and what they are allowed to do. Reviewing access reduces unnecessary exposure of information and privileged operations.

For example: A colleague changes jobs; their old administrator access should be reviewed instead of silently carried into the new role.

Key terms: **Authentication** means checking a claimed identity. **Authorization** means deciding which actions an identified person or program may perform. **RBAC** means role-based access control assigns permissions through roles. **PIM** means privileged Identity Management controls eligibility and time-limited activation of powerful roles. **Conditional Access** means a policy decision based on signals such as identity, device, and sign-in conditions.

**Before using this reference:** Real tenant operations require separately reviewed permissions and licensing; this document is not authorization to access employee records.

Start with the [plain-English learning path](../../../docs/knowledge/identity.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Reference only; this repository creates no review. A real tenant needs Microsoft Entra ID Governance
> for in-scope member users (some capabilities work with P2); see [licensing](licensing-prerequisites.md).
> Sources: [access reviews overview](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview),
> [create an access review](https://learn.microsoft.com/en-us/entra/id-governance/create-access-review),
> [review Entra roles in PIM](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-create-roles-and-resource-roles-review),
> [list decisions (Graph)](https://learn.microsoft.com/en-us/graph/api/accessreviewinstance-list-decisions).

## Objects

```
accessReviewScheduleDefinition   (what is reviewed, who reviews, recurrence, settings)
   └── accessReviewInstance      (one occurrence: startDateTime..endDateTime, status)
          └── accessReviewInstanceDecisionItem   (one principal x resource: decision, reviewedBy,
                                                  justification, recommendation, applyResult)
```

The synthetic fixture `fixtures/graph/scenarios/baseline/accessReviewDecisions.page*.json` holds five
decision items for a Security Administrator role review (definition `...000000000500`, instance
`...000000000501`); `access_review.py` summarises them.

## Lifecycle

| Phase | What happens | Bank control | Evidence |
|---|---|---|---|
| 1. Define | Scope (privileged roles, role-assignable groups, the AWS app assignment groups), reviewers, recurrence, duration | Privileged roles reviewed quarterly; reviewer is the role owner or manager, never the person reviewed; security team as second stage | Definition JSON export |
| 2. Start | Instance opens; reviewers notified | Reminders on | Instance ID and dates |
| 3. Review | Reviewer records Approve / Deny / DontKnow with justification; decision helpers (recommendations, for example inactivity) shown | Justification required to approve a privileged role (AR-004) | Decision items |
| 4. Close | Instance ends. "If reviewers don't respond": No change / Remove access / Approve access / Take recommendations | **Remove access** for privileged roles (fail-closed) | Not-reviewed count (AR-001) |
| 5. Apply | Results applied (auto-apply or manual); `applyResult` set per item | Auto-apply on; a Deny that is not `AppliedSuccessfully*` is an exception (AR-002) | `applyResult` per item |
| 6. Evidence | Export decisions; reconcile against the post-review inventory | Self-approval is an exception (AR-003) | `access_review.py --json-out`, before/after `inventory.py` reports |

## Findings modelled in `access_review.py`

| ID | Severity | Rule |
|---|---|---|
| AR-001 | MEDIUM | Decision still `NotReviewed` |
| AR-002 | HIGH | `Deny` whose `applyResult` is not `AppliedSuccessfully*` (access still present) |
| AR-003 | HIGH | Reviewer approved their own access |
| AR-004 | MEDIUM | `Approve` with an empty justification |
| DQ-001 | MEDIUM | Malformed decision item |

## Free-tier fallback (manual certification)

1. Run `inventory.py --mode free --csv-out review-<quarter>.csv` (in a real deployment, against a real export).
2. Each role owner marks every row keep or remove with a justification; nobody certifies their own row.
3. Removals run under change tickets; re-run the inventory and diff.
4. Keep the signed CSV, ticket IDs and both inventory reports as evidence. The AR-00x rules above apply
   to the sign-off sheet unchanged.
