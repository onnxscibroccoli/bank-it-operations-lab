# Canary sign-off -- EXAMPLE

> **EXAMPLE DATA.** Illustrative record of what a canary sign-off contains. Not a real change,
> host, or approval.

| Field | Value |
|---|---|
| Change record | CHG-EXAMPLE-0001 |
| Manifest | `bank-lab-2026-11-monthly` (inspector exit 0 attached) |
| Ring | canary (`canary`, `canary-rhel`) |
| Window | 2026-11-10 02:00-02:32 America/New_York (UTC-5) |
| Hosts | i-EXAMPLEcanary001, i-EXAMPLEcanary002 |
| Pre-snapshots | snap-EXAMPLE-001, snap-EXAMPLE-002 |
| Result | 2/2 COMPLIANT, 0 failed, both rebooted and healthy within 6 min |
| systemd | `systemctl --failed`: 0 units; hardening drop-ins still loaded on bank-lab-app |
| Soak | 2026-11-10 02:32 -> 2026-11-12 02:32 America/New_York (48 h), no regressions in error rate or latency |
| Evidence | `describe-instance-patch-states.canary.example.json`, `list-compliance-summaries.example.json` |
| Gate request | wave1 -- approvers: service-owner, change-advisory-board |
