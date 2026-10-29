# M365 / endpoint operations -- offline scenario report

> **OFFLINE / SYNTHETIC. Evaluated from local JSON in this repository. No Microsoft 365 / Entra ID / Intune tenant, Microsoft Graph call or credential was used, and no change was made anywhere. Every remediation step is PLAN_ONLY (executed=false).**

| Field | Value |
|---|---|
| Validated commit | `8452788d69d91373a26d4963f4a8f8547163913a` |
| Run | `local-offline-20261028T181845Z` |
| Generated (UTC) | `2026-10-28T18:18:45Z` |
| Tenant (synthetic) | Northwind Lab Bank (SYNTHETIC) `5a1e0000-0000-4000-8000-00000000a001` |
| As of (UTC) | 2026-10-28T16:00:00Z |
| Mutations executed | 0 |
| Overall | **PASS** (13/13 scenarios matched expectation) |

| Scenario | Type | Verdict | Expected | Findings | Result |
|---|---|---|---|---|---|
| M365-ACC-001 | access-troubleshooting | ROOT_CAUSE_IDENTIFIED | ROOT_CAUSE_IDENTIFIED | CA-DEVICE-NOT-COMPLIANT, DEV-BITLOCKER, DEV-OS-MIN, SH-ADVISORY | PASS |
| M365-ACC-002 | access-troubleshooting | ROOT_CAUSE_IDENTIFIED | ROOT_CAUSE_IDENTIFIED | LIC-PREREQ, LIC-WORKLOAD-MISSING, SH-ADVISORY | PASS |
| M365-ACC-003 | access-troubleshooting | ROOT_CAUSE_IDENTIFIED | ROOT_CAUSE_IDENTIFIED | LIC-WORKLOAD-MISSING | PASS |
| M365-ACC-004 | access-troubleshooting | ROOT_CAUSE_IDENTIFIED | ROOT_CAUSE_IDENTIFIED | AUTH-MFA-REGISTRATION-REQUIRED | PASS |
| M365-BG-001 | break-glass-review | COMPLIANT_WITH_WARNINGS | COMPLIANT_WITH_WARNINGS | BG-TEST-OVERDUE, PRIV-STANDING-GA | PASS |
| M365-BG-002 | break-glass-usage | POST_USE_COMPLETE | POST_USE_COMPLETE | - | PASS |
| M365-OFF-001 | offboarding | APPROVED | APPROVED | - | PASS |
| M365-OFF-002 | offboarding | REJECTED | REJECTED | OFF-BYOD-WIPE, OFF-LICENSE-BEFORE-RETENTION, OFF-MISSING-STEP, OFF-REVOKE-BEFORE-DISABLE | PASS |
| M365-ONB-001 | onboarding | READY | READY | ONB-MFA-TAP | PASS |
| M365-ONB-002 | onboarding | BLOCKED | BLOCKED | LIC-USAGE-LOCATION-INHERITED, LIC-WORKLOAD-MISSING, ONB-MFA-TAP | PASS |
| M365-ONB-003 | onboarding | BLOCKED | BLOCKED | LIC-NO-SEATS, ONB-MFA-TAP, ONB-PRIV-ROLE | PASS |
| M365-SH-001 | service-health | KNOWN_SERVICE_INCIDENT | KNOWN_SERVICE_INCIDENT | LIC-WORKLOAD-MISSING, SH-KNOWN-INCIDENT | PASS |
| M365-SH-002 | service-health | LOCAL_ISSUE | LOCAL_ISSUE | DEV-STALE-CHECKIN, SH-LOCAL-ISSUE, SH-RESTORED-RECENTLY | PASS |

## M365-ACC-001 -- Payments ops user blocked from Outlook: AADSTS53000 on a non-compliant laptop

Verdict **ROOT_CAUSE_IDENTIFIED** (expected ROOT_CAUSE_IDENTIFIED): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| CA-DEVICE-NOT-COMPLIANT | error | yes | sign-in SI-LAB-3002 (Outlook (synthetic)): AADSTS53000 Conditional Access requires a compliant device (CA004) and the device is not | Remediate the device compliance settings below, then sync the device in Company Portal. |
| DEV-OS-MIN | error | yes | NWL-LT-0506 (CP-WIN-BANK): OS 10.0.19045 below minimum 10.0.22631 | Update the OS through the update ring (feature update for Windows 10 -> 11). |
| DEV-BITLOCKER | error | yes | NWL-LT-0506 (CP-WIN-BANK): BitLocker not enabled | Enable BitLocker via the endpoint security disk encryption policy; escrow the key to Entra. |
| SH-ADVISORY | info |  | IN-LAB-0004 active: Delays in device compliance status reporting for some Windows devices (SYNTHETIC) | Note it in the ticket, but it does not explain the device's own setting violations. |

Plan (PLAN_ONLY, nothing executed):

1. `READ_SIGNIN_LOG` SI-LAB-3002 -- Graph: GET /v1.0/auditLogs/signIns?$filter=userId eq '{id}'
2. `READ_DEVICE_COMPLIANCE` NWL-LT-0506 -- Graph: GET /v1.0/deviceManagement/managedDevices/{id}/deviceCompliancePolicyStates

Audit evidence: required sign-in-log, diagnosis, resolution; missing none

## M365-ACC-002 -- Contractor cannot enroll in Intune: license group disables the Entra ID P1 prerequisite

Verdict **ROOT_CAUSE_IDENTIFIED** (expected ROOT_CAUSE_IDENTIFIED): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| LIC-WORKLOAD-MISSING | error | yes | finley.contractor@nwlab-bank.example: workload 'intune' needs one of ['AAD_PREMIUM', 'AAD_PREMIUM_P2']; AAD_PREMIUM disabled in group:GRP-LIC-E3-CONTRACTOR | Assign a license group whose SKU includes the plan (or re-enable the disabled plan); never hand out ad-hoc direct licenses. |
| LIC-PREREQ | error | yes | finley.contractor@nwlab-bank.example: plan INTUNE_A is enabled but its prerequisite ['AAD_PREMIUM', 'AAD_PREMIUM_P2'] is not (group-based licensing reports a dependency violation) | Fix the license group's disabledPlans so prerequisites stay enabled. |
| SH-ADVISORY | warn |  | IN-LAB-0004 active for intune: Delays in device compliance status reporting for some Windows devices (SYNTHETIC) | Link the ticket to the service-health issue. |

Plan (PLAN_ONLY, nothing executed):

1. `READ_LICENSE_STATE` finley.contractor@nwlab-bank.example -- Graph: GET /v1.0/users/{id}/licenseDetails

Audit evidence: required sign-in-log, diagnosis, resolution; missing none

## M365-ACC-003 -- Wealth advisor: sign-in succeeds but Outlook says the mailbox cannot be found

Verdict **ROOT_CAUSE_IDENTIFIED** (expected ROOT_CAUSE_IDENTIFIED): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| LIC-WORKLOAD-MISSING | error | yes | gray.advisor@nwlab-bank.example: workload 'mailbox' needs one of ['EXCHANGE_S_ENTERPRISE', 'EXCHANGE_S_DESKLESS']; EXCHANGE_S_ENTERPRISE disabled in group:GRP-LIC-E3-MIGRATION | Assign a license group whose SKU includes the plan (or re-enable the disabled plan); never hand out ad-hoc direct licenses. |

Plan (PLAN_ONLY, nothing executed):

1. `READ_LICENSE_STATE` gray.advisor@nwlab-bank.example -- Graph: GET /v1.0/users/{id}/licenseDetails

Audit evidence: required sign-in-log, diagnosis, resolution; missing none

## M365-ACC-004 -- Treasury user blocked with AADSTS50079 after phone replacement (no MFA method left)

Verdict **ROOT_CAUSE_IDENTIFIED** (expected ROOT_CAUSE_IDENTIFIED): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| AUTH-MFA-REGISTRATION-REQUIRED | error | yes | sign-in SI-LAB-3601 (My Sign-Ins (synthetic)): AADSTS50079 User must register for MFA but has no usable method | Verify identity out of band (call back on HR-record number), issue a one-time Temporary Access Pass, have the user register a phishing-resistant method. |

Plan (PLAN_ONLY, nothing executed):

1. `READ_SIGNIN_LOG` SI-LAB-3601 -- Graph: GET /v1.0/auditLogs/signIns?$filter=userId eq '{id}'
2. `ISSUE_TAP` harper.treasury@nwlab-bank.example -- Graph: POST /v1.0/users/{id}/authentication/temporaryAccessPassMethods (isUsableOnce=true)

Audit evidence: required sign-in-log, diagnosis, resolution; missing none

## M365-BG-001 -- Quarterly emergency-access (break-glass) review

Verdict **COMPLIANT_WITH_WARNINGS** (expected COMPLIANT_WITH_WARNINGS): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| BG-TEST-OVERDUE | warn |  | bg.bravo@nwlab-bank.onmicrosoft.example last tested 2026-06-02T15:00:00Z (> 90 days) | Run the quarterly dual-custody sign-in test and record it. |
| PRIV-STANDING-GA | warn |  | jordan.itadmin@nwlab-bank.example holds standing Global Administrator | Convert to PIM-eligible with approval; only break-glass accounts hold standing GA. |

Plan (PLAN_ONLY, nothing executed):

1. `REVIEW_BREAK_GLASS` bg.alpha@nwlab-bank.onmicrosoft.example -- Graph: GET /v1.0/users/{id}?$select=onPremisesSyncEnabled,userPrincipalName + roleManagement + authentication/methods
2. `REVIEW_BREAK_GLASS` bg.bravo@nwlab-bank.onmicrosoft.example -- Graph: GET /v1.0/users/{id}?$select=onPremisesSyncEnabled,userPrincipalName + roleManagement + authentication/methods

Audit evidence: required break-glass-review, alert-config, test-record; missing none

## M365-BG-002 -- Break-glass Alpha used during the MFA push/SMS outage (MFA-LAB-0003)

Verdict **POST_USE_COMPLETE** (expected POST_USE_COMPLETE): PASS

Plan (PLAN_ONLY, nothing executed):

1. `READ_SIGNIN_LOG` SI-LAB-6001 -- Graph: GET /v1.0/auditLogs/signIns/{id}
2. `READ_DIRECTORY_AUDIT` b9a5e000-0000-4000-8000-000000000001 -- Graph: GET /v1.0/auditLogs/directoryAudits?$filter=initiatedBy/user/id eq '{id}'
3. `ROTATE_CREDENTIAL` b9a5e000-0000-4000-8000-000000000001 -- Dual-custody credential rotation (offline procedure)

Audit evidence: required sign-in-log, incident-ticket, credential-rotation, audit-review; missing none

## M365-OFF-001 -- Involuntary termination of a synced commercial lender under legal hold

Verdict **APPROVED** (expected APPROVED): PASS

Plan (PLAN_ONLY, nothing executed):

1. `DISABLE_ONPREM_AD` dana.lender@nwlab-bank.example -- AD DS: Disable-ADAccount <samAccountName>, then wait for (or trigger) Entra Connect delta sync
2. `REVOKE_SESSIONS` dana.lender@nwlab-bank.example -- Graph: POST /v1.0/users/{id}/revokeSignInSessions
3. `REMOVE_AUTH_METHODS` dana.lender@nwlab-bank.example -- Graph: DELETE /v1.0/users/{id}/authentication/<method>Methods/{methodId}
4. `SET_LITIGATION_HOLD` dana.lender@nwlab-bank.example -- Exchange Online PowerShell: Set-Mailbox <upn> -LitigationHoldEnabled $true
5. `TRANSFER_ONEDRIVE` dana.lender@nwlab-bank.example -- SharePoint admin: grant the manager site-collection admin on the user's OneDrive
6. `RETIRE_DEVICE` DANA-IPHONE -- Graph: POST /v1.0/deviceManagement/managedDevices/{deviceId}/retire (selective wipe)
7. `WIPE_DEVICE` NWL-LT-0404 -- Graph: POST /v1.0/deviceManagement/managedDevices/{deviceId}/wipe (factory reset)
8. `REMOVE_FROM_GROUPS` dana.lender@nwlab-bank.example -- Graph: DELETE /v1.0/groups/{groupId}/members/{id}/$ref
9. `REMOVE_LICENSES` dana.lender@nwlab-bank.example -- Group-based: remove from GRP-LIC-* groups; direct: POST /v1.0/users/{id}/assignLicense removeLicenses
10. `EXPORT_AUDIT_EVIDENCE` dana.lender@nwlab-bank.example -- Purview audit search + Entra audit/sign-in log export for the user, hashed into the ticket

Audit evidence: required approval, identity-change, session-revocation, device-action, mailbox-retention, license-removal; missing none

## M365-OFF-002 -- Retiring employee: draft runbook with ordering and BYOD-wipe defects (rejected at review)

Verdict **REJECTED** (expected REJECTED): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| OFF-MISSING-STEP | error |  | no retire/wipe step for managed device NWL-LT-0909 | Corporate: wipe after data hand-over; personal: retire (selective wipe). |
| OFF-BYOD-WIPE | error |  | full wipe of personal device IRA-PIXEL would erase personal data | Use RETIRE_DEVICE (selective wipe of corporate data only) on personal devices. |
| OFF-REVOKE-BEFORE-DISABLE | error |  | sessions revoked before the account is disabled; the user can sign straight back in | Disable first, then revoke refresh tokens/sessions. |
| OFF-LICENSE-BEFORE-RETENTION | error |  | licenses removed before CONVERT_MAILBOX_SHARED, TRANSFER_ONEDRIVE; mailbox/OneDrive data enters deletion retention | Apply litigation hold / convert mailbox / transfer OneDrive while the license is still assigned. |

Plan (PLAN_ONLY, nothing executed):

1. `REVOKE_SESSIONS` ira.retiring@nwlab-bank.example -- Graph: POST /v1.0/users/{id}/revokeSignInSessions
2. `DISABLE_SIGNIN` ira.retiring@nwlab-bank.example -- Graph: PATCH /v1.0/users/{id} {"accountEnabled": false}
3. `REMOVE_AUTH_METHODS` ira.retiring@nwlab-bank.example -- Graph: DELETE /v1.0/users/{id}/authentication/<method>Methods/{methodId}
4. `REMOVE_LICENSES` ira.retiring@nwlab-bank.example -- Group-based: remove from GRP-LIC-* groups; direct: POST /v1.0/users/{id}/assignLicense removeLicenses
5. `CONVERT_MAILBOX_SHARED` ira.retiring@nwlab-bank.example -- Exchange Online PowerShell: Set-Mailbox <upn> -Type Shared; grant manager FullAccess
6. `TRANSFER_ONEDRIVE` ira.retiring@nwlab-bank.example -- SharePoint admin: grant the manager site-collection admin on the user's OneDrive
7. `WIPE_DEVICE` IRA-PIXEL -- Graph: POST /v1.0/deviceManagement/managedDevices/{deviceId}/wipe (factory reset)
8. `EXPORT_AUDIT_EVIDENCE` ira.retiring@nwlab-bank.example -- Purview audit search + Entra audit/sign-in log export for the user, hashed into the ticket

Audit evidence: required approval, identity-change, session-revocation, device-action, mailbox-retention, license-removal; missing none

## M365-ONB-001 -- New credit-risk analyst: E3 via group, Autopilot laptop, Temporary Access Pass on day 1

Verdict **READY** (expected READY): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| ONB-MFA-TAP | info |  | blake.analyst@nwlab-bank.example has no MFA method yet | Issue a one-time Temporary Access Pass on day 1 after in-person ID check; user registers a passkey/FIDO2. |

Plan (PLAN_ONLY, nothing executed):

1. `VERIFY_IDENTITY_SOURCE` blake.analyst@nwlab-bank.example -- Entra Connect: confirm the HR-driven AD account synced (onPremisesSynced=True)
2. `ADD_LICENSE_GROUP` blake.analyst@nwlab-bank.example -> GRP-LIC-E3-STAFF -- Graph: POST /v1.0/groups/{groupId}/members/$ref
3. `ISSUE_TAP` blake.analyst@nwlab-bank.example -- Graph: POST /v1.0/users/{id}/authentication/temporaryAccessPassMethods (isUsableOnce=true)
4. `VERIFY_DEVICE_COMPLIANCE` NWL-LT-0101 (compliant) -- Intune: managedDevices/{id} complianceState must be compliant before CA004 allows access

Audit evidence: required approval, identity-change, license-assignment, mfa-registration; missing none

## M365-ONB-002 -- Branch teller on F3 asks for desktop Outlook/Excel; usageLocation missing

Verdict **BLOCKED** (expected BLOCKED): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| LIC-USAGE-LOCATION-INHERITED | warn |  | avery.teller@nwlab-bank.example has no usageLocation; group-based licensing falls back to the tenant country (US) | Set usageLocation from the HR record (it drives service availability and data-residency reporting). |
| LIC-WORKLOAD-MISSING | error |  | avery.teller@nwlab-bank.example: workload 'desktop-apps' needs one of ['OFFICESUBSCRIPTION']; no assigned SKU includes it | Assign a license group whose SKU includes the plan (or re-enable the disabled plan); never hand out ad-hoc direct licenses. |
| ONB-MFA-TAP | info |  | avery.teller@nwlab-bank.example has no MFA method yet | Issue a one-time Temporary Access Pass on day 1 after in-person ID check; user registers a passkey/FIDO2. |

Plan (PLAN_ONLY, nothing executed):

1. `VERIFY_IDENTITY_SOURCE` avery.teller@nwlab-bank.example -- Entra Connect: confirm the HR-driven AD account synced (onPremisesSynced=True)
2. `SET_USAGE_LOCATION` avery.teller@nwlab-bank.example -- Graph: PATCH /v1.0/users/{id} {"usageLocation": "<from HR>"}
3. `ADD_LICENSE_GROUP` avery.teller@nwlab-bank.example -> GRP-LIC-F3-BRANCH -- Graph: POST /v1.0/groups/{groupId}/members/$ref
4. `ISSUE_TAP` avery.teller@nwlab-bank.example -- Graph: POST /v1.0/users/{id}/authentication/temporaryAccessPassMethods (isUsableOnce=true)

Audit evidence: required approval, identity-change, license-assignment, mfa-registration; missing none

## M365-ONB-003 -- SOC analyst needs E5 (Defender for Endpoint, PIM) but E5 seats are exhausted

Verdict **BLOCKED** (expected BLOCKED): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| LIC-NO-SEATS | error |  | LAB_M365_E5 has 15/15 seats consumed; adding to GRP-LIC-E5-SECOPS fails (CountViolation) | Reclaim seats from leavers or raise a procurement request before day 1. |
| ONB-MFA-TAP | info |  | casey.secops@nwlab-bank.example has no MFA method yet | Issue a one-time Temporary Access Pass on day 1 after in-person ID check; user registers a passkey/FIDO2. |
| ONB-PRIV-ROLE | warn |  | casey.secops@nwlab-bank.example requested Security Reader at onboarding | Grant as PIM-eligible after 30-day probation sign-off; never permanent. |

Plan (PLAN_ONLY, nothing executed):

1. `VERIFY_IDENTITY_SOURCE` casey.secops@nwlab-bank.example -- Entra Connect: confirm the HR-driven AD account synced (onPremisesSynced=True)
2. `ADD_LICENSE_GROUP` casey.secops@nwlab-bank.example -> GRP-LIC-E5-SECOPS -- Graph: POST /v1.0/groups/{groupId}/members/$ref
3. `ISSUE_TAP` casey.secops@nwlab-bank.example -- Graph: POST /v1.0/users/{id}/authentication/temporaryAccessPassMethods (isUsableOnce=true)

Audit evidence: required approval, identity-change, license-assignment, mfa-registration; missing none

## M365-SH-001 -- Six Teams tickets in 20 minutes during an active Microsoft incident (TM-LAB-0001)

Verdict **KNOWN_SERVICE_INCIDENT** (expected KNOWN_SERVICE_INCIDENT): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| SH-KNOWN-INCIDENT | info |  | 6 report(s) for teams match TM-LAB-0001: Users may be unable to join meetings or load chat history (SYNTHETIC) | Link tickets to the issue, post a status-page/Teams-free notice (email + intranet), do not troubleshoot users individually. |
| LIC-WORKLOAD-MISSING | warn |  | parker.intern@nwlab-bank.example: workload 'teams' needs one of ['TEAMS1']; no assigned SKU includes it | Assign a license group whose SKU includes the plan (or re-enable the disabled plan); never hand out ad-hoc direct licenses. |
| LIC-WORKLOAD-MISSING | warn |  | parker.intern@nwlab-bank.example: workload 'teams' needs one of ['EXCHANGE_S_ENTERPRISE', 'EXCHANGE_S_DESKLESS']; no assigned SKU includes it | Assign a license group whose SKU includes the plan (or re-enable the disabled plan); never hand out ad-hoc direct licenses. |

Plan (PLAN_ONLY, nothing executed):

1. `READ_SERVICE_HEALTH` teams -- Graph: GET /v1.0/admin/serviceAnnouncement/issues?$filter=status ne 'serviceRestored'
2. `COMMUNICATE` teams -- Bank comms template: known Microsoft incident, workaround, next update time

Audit evidence: required service-health-snapshot, user-communication; missing none

## M365-SH-002 -- Two loan-ops users report Outlook problems after EX-LAB-0002 was restored

Verdict **LOCAL_ISSUE** (expected LOCAL_ISSUE): PASS

| Code | Severity | Root cause | Detail | Remediation |
|---|---|---|---|---|
| SH-RESTORED-RECENTLY | info |  | EX-LAB-0002 was restored at 2026-10-28T12:30:00Z; residual client-side effects possible | Restart Outlook/Teams, clear cached credentials, then troubleshoot locally. |
| SH-LOCAL-ISSUE | info |  | 2 report(s) for mailbox and no active Microsoft issue | Troubleshoot per user (licenses, device compliance, client). |
| DEV-STALE-CHECKIN | warn |  | NWL-LT-1212 (CP-WIN-BANK): last check-in 2026-09-19T11:00:00Z is older than the 30-day compliance validity period | Power on, connect to the network and sync from Company Portal; investigate if the device is lost. |

Plan (PLAN_ONLY, nothing executed):

1. `READ_SERVICE_HEALTH` mailbox -- Graph: GET /v1.0/admin/serviceAnnouncement/issues?$filter=status ne 'serviceRestored'

Audit evidence: required service-health-snapshot, user-communication; missing none
