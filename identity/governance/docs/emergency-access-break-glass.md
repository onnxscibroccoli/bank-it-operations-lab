# Emergency access (break-glass) operational flow

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Control who can use a system and what they are allowed to do. Reviewing access reduces unnecessary exposure of information and privileged operations.

For example: A colleague changes jobs; their old administrator access should be reviewed instead of silently carried into the new role.

Key terms: **Authentication** means checking a claimed identity. **Authorization** means deciding which actions an identified person or program may perform. **RBAC** means role-based access control assigns permissions through roles. **PIM** means privileged Identity Management controls eligibility and time-limited activation of powerful roles. **Conditional Access** means a policy decision based on signals such as identity, device, and sign-in conditions.

**Before using this reference:** Real tenant operations require separately reviewed permissions and licensing; this document is not authorization to access employee records.

Start with the [plain-English learning path](../../../docs/knowledge/identity.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Reference only; this repository creates and uses no account. Synthetic break-glass IDs:
> `b9a5e000-0000-4000-8000-000000000001` and `...000000000002` (the same IDs as the `identity/entra`
> baseline on branch `entra-ca-offline`).
> Primary source: [Manage emergency access admin accounts](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access).
> AWS side: [IAM Identity Center emergency access](https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access.html).

## Account standard (Microsoft guidance, bank interpretation)

| Requirement | Bank standard | Checked by |
|---|---|---|
| Count | Exactly 2 cloud-only accounts | `baseline.json` `breakGlass.userIds` |
| Domain | Initial `*.onmicrosoft.com` domain, not federated or synced (the fixtures use `bankitlab.example` only because they are synthetic) | manual |
| Role | Global Administrator, **active permanent** (not PIM-eligible) | INV-007; exempt from INV-001 |
| Authentication | Phishing-resistant: FIDO2 passkey (preferred) or certificate-based authentication, different from the daily admin methods; satisfies mandatory MFA | manual and CA baseline |
| Conditional Access | Excluded from every CA policy that blocks or restricts sign-in (report-only policies need no exclusion) | `identity/entra` BASE-001 (branch `entra-ca-offline`) |
| Not tied to a person | No personal phone, MFA or SSPR registration; credentials not subject to expiry or inactivity clean-up | quarterly drill |
| Storage | Keys in two separate fire-proof safes; dual control | quarterly drill |
| Monitoring | Alert on **every** sign-in by either object ID (Log Analytics `SigninLogs` or SIEM), critical severity | alert rule |

## Flow

```
 ┌──────────────┐  declare  ┌──────────────────┐  dual-control  ┌──────────────┐  restore  ┌──────────────┐
 │ Normal admin │─incident─▶│ IC approves use  │─key retrieval─▶│ Sign in from │──normal──▶│ Post-mortem  │
 │ path broken  │           │ (2 people, log)  │                │ PAW, minimal │ admin path│ + rotate     │
 └──────────────┘           └──────────────────┘                │ fix only     │           └──────────────┘
                                                                 └──────────────┘
```

1. **Trigger**: only when normal admin paths fail: federation or IdP outage, MFA service or device
   outage, PIM approval deadlock (all tier-0 eligible and no approver available), last GA lost.
2. **Declare**: the incident commander opens a P1 incident, records the reason and names two operators.
3. **Retrieve**: two people retrieve the key from the safe and log time, names and seal numbers.
4. **Sign in**: from a privileged access workstation; the SOC receives the alert and confirms it is expected.
5. **Act minimally**: restore the normal path (fix a CA policy, re-enable a PIM approver, restore the
   IdP); no unrelated changes; record every action.
6. **Exit**: sign out, return and re-seal the key, confirm normal admins can work.
7. **Post-mortem (within 5 business days)**: export sign-in and audit logs for both accounts, classify
   the use (drill, genuine emergency, misuse), review every action, rotate credentials or re-register
   keys if exposure is possible, update this runbook.
8. **Evidence**: incident ticket, safe log, alert record, log exports, and an inventory report showing
   both accounts still hold permanent GA (INV-007 clean).

## Validation drill (at least every 90 days, and after staff or subscription changes)

* Tell the SOC beforehand; sign in with each account; perform a read-only admin task; sign out.
* Confirm the alert fired for each account, the CA exclusions are intact, no personal MFA or SSPR
  methods were registered, and the authorised-person list and safe combinations are current.
* Run the inventory check (as in `python3 identity/governance/inventory.py --scenario baseline`) against
  the export and attach the report.

## AWS counterpart

IAM Identity Center depends on the external IdP (Entra) for sign-in. AWS recommends preparing an
emergency path before any disruption: either direct SAML federation to critical-operations IAM roles in
individual accounts (works while Identity Center is unavailable but the IdP is up), or AWS break-glass
access that does not depend on the IdP. See
[`docs/federation/entra-to-aws-iam-identity-center.md`](../../../docs/federation/entra-to-aws-iam-identity-center.md#emergency-access).
