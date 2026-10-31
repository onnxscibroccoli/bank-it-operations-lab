# Rollback drill -- EXAMPLE

> **EXAMPLE DATA.** A tabletop record showing the fields a rollback entry needs. No host was
> rolled back; ids and times are invented.

| Field | Value |
|---|---|
| Trigger | canary invocation failed on i-EXAMPLEcanary002 (service failed to start after reboot) |
| Ring halted | yes -- `MaxErrors=0` stopped the window at 06:19 UTC (02:19 America/New_York, UTC-4) |
| Strategy | `package-downgrade` (`dnf history undo <id>`) |
| Package | EXAMPLE-libfoo 2.4 -> 2.3, added to `RejectedPatches` (BLOCK) |
| Duration | 22 min (budget `maxRollbackMinutes`: 60) |
| Escalation | T1 on-call SRE paged at +15 min per ESCALATION.md |
| Verification | service healthy, re-scan COMPLIANT with the rejected package excluded |
| Follow-up | wave1 kept gated; new canary scheduled after vendor fix |
