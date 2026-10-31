# Escalation procedure

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Roll out software updates in controlled stages and decide when to stop or roll back. Early checks limit the spread of a bad update and give operators a recovery point.

For example: A small test group receives a change before the organization considers a wider rollout.

Key terms: **Canary** means a small first group used to observe a change before wider rollout. **Patch ring** means a group of systems assigned a particular rollout stage. **Rollback** means a deliberate return to a previous known state. **SSM** means aWS Systems Manager, including tools for managed-host operations.

**Before using this reference:** Installation, service restart, and rollback instructions can disrupt systems. Read the target, permissions, and change gates before any live use.

Start with the [plain-English learning path](../../../docs/knowledge/infrastructure.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Reference procedure. Roles and channels are placeholders (`EXAMPLE-...`).

| Tier | When | Who (role) | Response target |
|---|---|---|---|
| T0 | Any stop condition during a window | Operator running the window | immediate: halt ring, start ROLLBACK.md triage |
| T1 | Stop condition not cleared in 15 min, or rollback started | on-call SRE (`EXAMPLE-pager-rotation`) | 15 min |
| T2 | Rollback exceeds `maxRollbackMinutes`, or customer-facing impact | change manager + service owner (`EXAMPLE-change-desk`) | 30 min |
| T3 | Data integrity risk, security control failure, or regulatory-reportable outage | incident commander, security on-call, CISO delegate | 30 min; incident process takes over |

## What to send at each escalation

- Change record id and manifest id (`changeRecord`, `manifestId`).
- Ring, affected hosts/patch groups, first failure time (with time zone).
- Last good compliance summary and the failing invocation output.
- Rollback strategy chosen and current status.

## De-escalation

Close only when affected hosts are back to the pre-change or post-fix state, compliance is
re-scanned, and the evidence bundle for the cycle has the rollback entry. Remaining rings stay gated
until a new approval (APPROVAL.md).
