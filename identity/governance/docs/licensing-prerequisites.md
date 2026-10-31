# Licensing prerequisites (PIM, access reviews, provisioning) and free-tier fallbacks

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Control who can use a system and what they are allowed to do. Reviewing access reduces unnecessary exposure of information and privileged operations.

For example: A colleague changes jobs; their old administrator access should be reviewed instead of silently carried into the new role.

Key terms: **Authentication** means checking a claimed identity. **Authorization** means deciding which actions an identified person or program may perform. **RBAC** means role-based access control assigns permissions through roles. **PIM** means privileged Identity Management controls eligibility and time-limited activation of powerful roles. **Conditional Access** means a policy decision based on signals such as identity, device, and sign-in conditions.

**Before using this reference:** Real tenant operations require separately reviewed permissions and licensing; this document is not authorization to access employee records.

Start with the [plain-English learning path](../../../docs/knowledge/identity.md) or [glossary](../../../docs/knowledge/glossary.md). [Current integration and review policy](../../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Reference only. This lab **does not assume any paid licence** and runs entirely on synthetic
> fixtures. Licensing changes; re-read the linked Microsoft pages before any purchase or design
> decision. Summarised from the pages as read on 2026-10-28.

Primary source: [Microsoft Entra ID Governance licensing fundamentals](https://learn.microsoft.com/en-us/entra/id-governance/licensing-fundamentals)
(see also [Microsoft Entra licensing](https://learn.microsoft.com/en-us/entra/fundamentals/licensing)).

## What needs what

| Capability used by this lab's references | Free | P1 | P2 | ID Governance | Source |
|---|---|---|---|---|---|
| Directory role assignments (`roleAssignments` read, built-in roles) | yes | yes | yes | yes | [List role assignments](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/view-assignments) |
| Privileged Identity Management (eligible / time-bound assignments, activation, approval) | -- | -- | yes | yes | [licensing fundamentals: PIM](https://learn.microsoft.com/en-us/entra/id-governance/licensing-fundamentals#privileged-identity-management) |
| PIM for Groups | -- | -- | yes | yes | same page, features-by-licence table |
| Access reviews: capabilities previously GA in P2 | -- | -- | yes | yes | [licensing fundamentals: access reviews](https://learn.microsoft.com/en-us/entra/id-governance/licensing-fundamentals#access-reviews) |
| Access reviews: newer capabilities (ML-assisted, inactive-only scope, PIM for Groups reviews, catalog reviews) | -- | -- | -- | yes | same page |
| SAML SSO to pre-integrated (gallery) enterprise apps such as AWS IAM Identity Center | yes | yes | yes | yes | [Plan SSO: licensing](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/plan-sso-deployment#licensing) |
| Assigning **groups** (not just users) to an enterprise app | -- | yes | yes | n/a | [Entra plans & pricing](https://www.microsoft.com/en-us/security/business/microsoft-entra-pricing) |
| Automated **user** provisioning (SCIM) to SaaS apps, e.g. AWS IAM Identity Center | yes | yes | yes | yes | same page, "Provisioning" rows |
| Automated **group** provisioning to SaaS apps | -- | yes | yes | yes | same page, "Provisioning" rows |
| Conditional Access (used by `identity/entra` on branch `entra-ca-offline`) | -- | yes | yes | n/a (Governance needs a P1/P2 prerequisite) | [Microsoft Entra licensing](https://learn.microsoft.com/en-us/entra/fundamentals/licensing) |

Key statements from Microsoft (paraphrased; see the linked page for exact wording):

* PIM requires **Microsoft Entra ID P2 or Microsoft Entra ID Governance** licences for users with
  eligible or time-bound assignments, users who approve activations, and users assigned to or
  performing access reviews.
* Access reviews require **Microsoft Entra ID Governance** for member users in scope (reviewers and
  reviewed); some capabilities still operate with P2. Microsoft states no new IGA capabilities will be
  added to the P2 SKU.
* Microsoft Entra ID Governance needs a **prerequisite** subscription that contains the `AAD_PREMIUM`
  (P1) or `AAD_PREMIUM_P2` service plan, depending on which Governance product is bought.
* **When a PIM licence expires:** permanent assignments are unaffected; active time-bound assignments
  become active permanent; **eligible assignments are removed**; ongoing reviews of Entra roles end.
  Plan for this: it silently converts just-in-time access into standing access.
* Guests governed by ID Governance features are billed on a monthly-active-user model and need an Azure
  subscription linked for guest billing.

## Free-tier fallbacks (no paid licence)

| Control | Paid feature | Free-tier fallback used or modelled here |
|---|---|---|
| Privileged inventory | PIM schedule-instance APIs | `inventory.py --mode free` reads `roleAssignments` only (scenario `free-tier`) and reports INV-010 INFO that permanence and eligibility are unknown. Treat **every** assignment as standing access |
| Just-in-time admin | PIM eligible + activation | Separate cloud-only admin accounts, minimum number of role holders, change-ticketed add/remove of direct role assignments, removal at end of task; reconcile with the inventory |
| MFA for admins | Conditional Access (P1) | [Security defaults](https://learn.microsoft.com/en-us/entra/fundamentals/security-defaults) (all-or-nothing; must be turned off to use Conditional Access) plus Microsoft's [mandatory MFA](https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-mandatory-multifactor-authentication) for admin portals |
| Periodic access certification | Access reviews (Governance/P2) | Quarterly manual review: export the `inventory.py` CSV, each owner signs off every row (keep/remove + justification), changes run under a ticket, signed CSV + ticket IDs kept as evidence. The `access_review.py` rules (self-review, unapplied deny, not reviewed) apply equally to a manual sign-off sheet |
| Group provisioning to AWS | SCIM group provisioning (P1) | Provision users through SCIM (Free), then manage group membership in IAM Identity Center or assign users directly; see [`docs/federation/entra-to-aws-iam-identity-center.md`](../../../docs/federation/entra-to-aws-iam-identity-center.md) |
| Audit retention | Longer retention with P1/P2 | Export sign-in and audit logs on a schedule ([download logs](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-download-logs)); retention differs by licence, check the linked page |

## Checking what a tenant has (manual, read-only; not done by this lab)

Microsoft's documented path: Entra admin center as License Administrator, **Billing > Licenses >
Licensed features** and **All products**. A Global Administrator can start an ID Governance trial from
the Microsoft 365 admin center when a prerequisite product is present.
