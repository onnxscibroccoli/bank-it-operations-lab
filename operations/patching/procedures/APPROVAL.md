# Ring approval gates

> Reference procedure. Example roles and change ids only.

Every ring after the canary is **gated**. A gated ring's maintenance-window task ships with
`Operation=Scan` (CFN parameters `Wave1Operation` / `Wave2Operation` default to `Scan`; the CLI
examples `register-task.wave1.json` and `register-task.wave2.json` use `Scan`). The inspector rule
`PM-TASK-GATED-SCAN` fails if a gated ring ships with `Install`.

## Gate criteria (all required)

| # | Criterion | Checked by |
|---|---|---|
| G1 | Previous ring finished with zero failed invocations above its `maxErrors` | maintenance window execution history |
| G2 | Previous ring soaked for at least `gate.minSoakHours` (lab minimum 24 h) | `PM-GATE-SOAK` + timestamps in evidence |
| G3 | Compliance summary for previous ring attached (`compliance-summary`) | `PM-GATE-EVIDENCE` |
| G4 | No open Sev1/Sev2 incident attributed to the patch set | incident tracker |
| G5 | Named approvers in `gate.approvers` have approved the change record | change record |
| G6 | Rollback path still valid (snapshots exist / previous package versions available) | ROLLBACK.md pre-checks |

## Opening a gate

1. Approver(s) record approval on the change record with the evidence links.
2. The operator flips only the gated ring's operation from `Scan` to `Install` (CFN stack update
   with `Wave1Operation=Install`, or `aws ssm update-maintenance-window-task` with the edited CLI
   input). This is the **only** change made at gate time.
3. After the ring completes, flip it back to `Scan` so the next cycle starts gated again.

## Emergency (out-of-band) patches

A critical, actively exploited vulnerability may shorten soak times but never skips the canary.
Minimum: canary install + 4 h soak + approval by the change manager and security on-call, recorded
as an emergency change. The manifest for that cycle must still pass the inspector; lower
`minSoakHours` only with a written justification in the change record (the inspector enforces a
24 h floor by default, so emergency runs are reviewed outside it on purpose).
