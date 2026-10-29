# M365 / endpoint operator runbooks (synthetic lab)

> Reference procedures behind the `m365_ops.py` rules. Commands are shown for orientation and are
> **never run by this repository**. In a real tenant, each step needs an approved ticket and least-privilege
> PIM activation. Rule codes are given in brackets.

## 1. Onboarding (joiner)
1. **Approval.** Confirm an HR joiner ticket (`HR-LAB-*`) with start date, role and manager [AUD-NO-APPROVAL].
2. **Identity source.** Hybrid users are created in AD DS by the HR feed and synced by Entra Connect. Do not create cloud duplicates.
3. **usageLocation.** Set it from the HR record. Direct license assignment fails without it. Group-based licensing inherits the
   tenant country, which can be wrong for cross-border staff [LIC-USAGE-LOCATION, LIC-USAGE-LOCATION-INHERITED].
4. **Licensing through groups only.** Add the user to one `GRP-LIC-*` group. Before day 1, check that:
   - the SKU covers every required workload. For example, F3 has no desktop Office, and the Teams calendar needs an Exchange plan [LIC-WORKLOAD-MISSING];
   - no plan prerequisite is disabled in the group. In the lab model Intune needs Entra ID P1 [LIC-PREREQ];
   - seats are free, so the group does not go into CountViolation [LIC-NO-SEATS].
5. **MFA bootstrap.** Do an in-person or video ID check, issue a one-time Temporary Access Pass, and have the user register a passkey or FIDO2 key [ONB-MFA-TAP].
6. **Privileged roles.** Never grant them at onboarding. After probation, grant them as PIM-eligible with approval [ONB-PRIV-ROLE].
7. **Device.** Autopilot or Company Portal enrollment. The device must be compliant before CA004 allows access [DEV-*].
8. **Evidence.** Keep the approval, the identity change, the license assignment and the MFA registration (plus the device compliance report).

## 2. Offboarding (leaver)
Order matters. Use the earliest step that removes access, and keep the license until data retention is done.

| # | Step | Why |
|---|---|---|
| 1 | Disable in **AD DS** for synced users, otherwise in Entra | A cloud-only disable of a synced user fails or is overwritten by sync [OFF-SYNCED-SOURCE] |
| 2 | Revoke sessions / refresh tokens | Revoking before the disable lets the user sign straight back in [OFF-REVOKE-BEFORE-DISABLE] |
| 3 | Remove authentication methods, then privileged roles | Stops MFA re-registration and standing privilege |
| 4 | Litigation hold (if Legal requires it) **or** convert the mailbox to shared, then transfer OneDrive | Must happen **before** license removal [OFF-LICENSE-BEFORE-RETENTION] |
| 5 | Devices: **wipe** corporate devices, **retire** (selective wipe) personal ones | Wiping a personal device destroys personal data [OFF-BYOD-WIPE, OFF-CORP-RETIRE] |
| 6 | Remove from groups, then licenses (via the group) | Frees seats |
| 7 | Export audit evidence last | So it captures every change [OFF-AUDIT-NOT-LAST] |

For involuntary leavers, steps 1-2 run at the moment HR starts the meeting [OFF-INVOLUNTARY-ORDER]. Break-glass accounts
never go through this runbook [OFF-BREAK-GLASS].

## 3. Access troubleshooting
1. Get the **sign-in log entry** (correlation ID, AADSTS code, CA result, device ID) before changing anything.
2. Map the code:

| AADSTS | Meaning | Action |
|---|---|---|
| 50126 | bad credentials | Check for a password spray across users first, then use SSPR |
| 50053 | locked / blocked IP | Confirm it was the user before unlocking |
| 50057 | account disabled | Check for an offboarding; never re-enable on the caller's word |
| 50076 | MFA required | User completes MFA |
| 50079 | MFA registration required | Out-of-band identity check (call back on the HR number), then a one-time TAP |
| 53000 | device not compliant | Read the Intune policy state and fix the settings (OS, BitLocker, ...) |
| 53003 | blocked by CA | Read the policy result; **never** add a per-user exclusion to "fix" it |

3. If sign-in succeeds but the workload fails, check `licenseDetails` and disabled plans [LIC-*].
4. Check service health for the workload at the time of the report [SH-*]. An Intune reporting advisory does **not**
   explain real setting violations.
5. Unknown codes go to an escalation, not a guess. The engine fails closed on unmapped codes.

## 4. Service-health triage
1. Group tickets by workload and time. Compare them with the active service-health issues.
2. **Active incident.** Link the tickets, communicate through a channel that is not affected (email/intranet if Teams is down),
   and stop per-user troubleshooting [SH-KNOWN-INCIDENT].
3. **Restored in the last 24h.** Expect client-side residue: restart the client and clear cached credentials [SH-RESTORED-RECENTLY].
4. **No issue and at or above the threshold.** Open a Microsoft support request and notify the incident manager [SH-ESCALATE-MICROSOFT].
5. **No issue and below the threshold.** Troubleshoot locally [SH-LOCAL-ISSUE].
6. In every case, check each reporter's license and device. An unlicensed user stays broken after Microsoft fixes the incident.

## 5. Emergency access (break-glass)
**Standard:** at least two accounts [BG-COUNT] that are:
- cloud-only [BG-SYNCED] and on the initial onmicrosoft domain [BG-DOMAIN];
- **permanent** Global Administrator, not PIM [BG-ROLE];
- set up with phishing-resistant FIDO2/CBA keys stored in two separate vaults [BG-METHOD, BG-CUSTODY];
- excluded from every CA policy, matching `identity/entra` BASE-001 [BG-CA-NOT-EXCLUDED];
- unlicensed [BG-LICENSED];
- covered by a SOC alert on every sign-in [BG-ALERT];
- tested with dual custody every 90 days [BG-TEST-OVERDUE].

No other user holds standing Global Administrator [PRIV-STANDING-GA].

**Use:** only when normal admin access is unavailable (an outage or a CA lockout). Two custodians are required. Link an incident
ticket [BG-USE-NO-TICKET] and the outage [BG-USE-NO-OUTAGE]. Afterwards:
- rotate credentials within 24h [BG-USE-ROTATION-LATE];
- have a second admin review every audit entry from the session [BG-USE-AUDIT-NOT-REVIEWED].
