# Rollback procedure

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Roll out software updates in controlled stages and decide when to stop or roll back. Early checks limit the spread of a bad update and give operators a recovery point.

For example: A small test group receives a change before the organization considers a wider rollout.

Key terms: **Canary** means a small first group used to observe a change before wider rollout. **Patch ring** means a group of systems assigned a particular rollout stage. **Rollback** means a deliberate return to a previous known state. **SSM** means aWS Systems Manager, including tools for managed-host operations.

**Before using this reference:** Installation, service restart, and rollback instructions can disrupt systems. Read the target, permissions, and change gates before any live use.

Start with the [plain-English learning path](../../../docs/knowledge/infrastructure.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Reference procedure. Rollback is a decision made by a human on the change record; no tooling in
> this repository performs it.

## Triggers

Any canary stop condition (CANARY.md), any ring exceeding `maxErrors`, a post-patch Sev1/Sev2
attributed to the patch set, or a security control regression (e.g. a hardened unit no longer
starting with its drop-ins).

## Decision

| Situation | Strategy | Target time |
|---|---|---|
| One or a few packages at fault, host healthy enough to log in | `package-downgrade` | < 30 min |
| Host does not boot / kernel or glibc regression / unknown blast radius | `snapshot-restore` (from the pre-install snapshot) | < 60 min |
| Stateless, auto-scaled fleet | `instance-replace` from the previous AMI | per ASG refresh |

`maxRollbackMinutes` in the manifest (lab default 60) is the budget; exceeding it escalates to the
next tier in ESCALATION.md.

## package-downgrade (dnf/yum based)

1. Freeze the ring: set the ring's task back to `Scan` / disable the window.
2. Identify the transaction: `dnf history list` then `dnf history info <id>`.
3. Undo it: `dnf history undo <id>` (or `dnf downgrade <pkg>-<prev-version>`).
4. Add the offending package to the baseline's `RejectedPatches` with `RejectedPatchesAction=BLOCK`
   so it is not reinstalled next window.
5. Reboot if a kernel, glibc, systemd or openssl package was involved.
6. Verify exactly as in CANARY.md step 5.

## snapshot-restore

1. Stop the instance; detach the root volume; create a volume from the pre-install snapshot
   recorded in the change record; attach as root; start.
2. Confirm application data volumes were **not** rolled back unless intended.
3. Verify (CANARY.md step 5) and re-run an SSM `Scan` so compliance reflects reality.

## Afterwards

Record the rollback in the cycle evidence (`evidence/host-operations/`), including timestamps,
the strategy used, and the before/after compliance summaries. Keep affected rings gated until a
fixed package or a `RejectedPatches` entry is in place and a new canary has passed.
