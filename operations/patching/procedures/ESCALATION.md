# Escalation procedure

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
