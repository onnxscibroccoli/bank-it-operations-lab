# Walkthrough: Microsoft Entra ID -> AWS IAM Identity Center (SAML + SCIM)

> **Reference walkthrough; nothing in this repository performs these steps.** No Entra tenant or AWS
> account is changed by this lab. Identifiers are synthetic: tenant `bankitlab.example`
> (`b9a5e000-0000-4000-8000-0000000000f0`), AWS account IDs `111122223333` / `444455556666` (AWS
> documentation placeholders). Copy real URLs and certificates only from the metadata files the two
> services generate; never hand-type them.
>
> Authoritative sources (re-read before doing this for real):
> AWS [Configure SAML and SCIM with Microsoft Entra ID and IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/idp-microsoft-entra.html),
> AWS [SCIM provisioning considerations](https://docs.aws.amazon.com/singlesignon/latest/userguide/provision-automatically.html),
> AWS [manage an external identity provider](https://docs.aws.amazon.com/singlesignon/latest/userguide/manage-your-identity-source-idp.html),
> AWS [permission sets](https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsetsconcept.html),
> Microsoft [SSO tutorial: AWS IAM Identity Center](https://learn.microsoft.com/en-us/entra/identity/saas-apps/aws-single-sign-on-tutorial),
> Microsoft [provisioning tutorial: AWS IAM Identity Center](https://learn.microsoft.com/en-us/entra/identity/saas-apps/aws-single-sign-on-provisioning-tutorial).
> Background: [`saml-vs-scim.md`](saml-vs-scim.md).

## Target design

```
 Microsoft Entra ID (bankitlab.example)                            AWS Organizations (management acct 111122223333)
 ┌──────────────────────────────────────────┐                      ┌────────────────────────────────────────────────┐
 │ Enterprise app "AWS IAM Identity Center" │── SAML 2.0 (SSO) ───▶│ IAM Identity Center (identity source: external │
 │  - users/groups assigned to the app      │── SCIM 2.0 (sync) ──▶│ IdP)                                           │
 │  - groups: grp-aws-<acct>-<permset>       │                      │  groups (from SCIM) ─▶ permission sets ─▶ accounts│
 │  - PIM for Groups (P2/Gov) optional       │                      │  e.g. grp-aws-prod-readonly ─▶ ReadOnly ─▶ 444455556666│
 └──────────────────────────────────────────┘                      └────────────────────────────────────────────────┘
```

| Synthetic Entra group | Permission set | AWS account | Session duration |
|---|---|---|---|
| `grp-aws-prod-readonly` | `BankReadOnly` (AWS managed `ReadOnlyAccess`) | `444455556666` (prod) | 4 h |
| `grp-aws-prod-ops` | `BankOperator` (customer-managed, scoped) | `444455556666` | 1 h |
| `grp-aws-sandbox-admin` | `BankSandboxAdmin` (`AdministratorAccess`) | sandbox account | 4 h |
| `grp-aws-security-audit` | `BankSecurityAudit` (`SecurityAudit`) | all accounts | 4 h |

Principle: **Entra group membership is the only way to get AWS access**; nobody is assigned directly in
IAM Identity Center, so Entra access reviews and the joiner/mover/leaver process govern AWS too.

## Prerequisites and licensing

* An Entra tenant and an AWS organization with IAM Identity Center enabled (AWS doc prerequisites).
* Entra roles: at least **Cloud Application Administrator** to add and configure the enterprise app
  (per the AWS tutorial). Use PIM activation for it where licensed.
* AWS: an IAM Identity Center administrator in the management or delegated administrator account.
* Licensing ([details](../../identity/governance/docs/licensing-prerequisites.md)): SAML SSO and SCIM
  **user** provisioning work on Entra ID Free. Assigning **groups** to the app and SCIM **group**
  provisioning need Entra ID P1 or higher. *Free-tier fallback:* assign users individually to the app
  and maintain group membership in IAM Identity Center (Identity Store APIs remain usable alongside
  SCIM, per AWS); accept that group lifecycle then lives in AWS, and review it there.

## Step 0: plan and change control

1. Raise a change: changing the IAM Identity Center identity source affects every existing Identity
   Center user and assignment; read AWS's "considerations for changing your identity source" first.
2. Confirm the AWS emergency path works **before** the cut-over ([emergency access](#emergency-access)).
3. Decide the username attribute: `userPrincipalName` here, used for both SAML `NameID` and SCIM `userName`.
4. Pick 1 pilot user and 1 pilot group (synthetic: `avery.admin@bankitlab.example`, `grp-aws-sandbox-admin`).

## Step 1: Entra enterprise application

1. Entra admin center -> **Enterprise applications** -> **New application** -> search the gallery for
   **AWS IAM Identity Center** -> **Create**.
2. **Properties**: assignment required = **Yes** (only assigned users/groups can sign in or be provisioned).
3. **Owners**: the IAM platform team (not individuals' personal accounts).

## Step 2: IAM Identity Center: switch identity source to the external IdP

1. IAM Identity Center console -> **Settings** -> **Identity source** -> **Actions** -> **Change identity
   source** -> **External identity provider**.
2. **Download** the IAM Identity Center SAML metadata file (contains the ACS URL and SP entity ID).
3. Keep this page open; the IdP metadata is uploaded in Step 3.

## Step 3: SAML (authentication)

1. Entra app -> **Single sign-on** -> **SAML** -> **Upload metadata file** -> the AWS file from Step 2.
   This fills **Identifier (Entity ID)** and **Reply URL (ACS URL)**; save.
2. Check **Attributes & Claims**: unique user identifier (`NameID`) = `user.userprincipalname`; it must
   equal what SCIM maps to `userName` (Step 4).
3. **SAML Signing Certificate**: download **Federation Metadata XML**; note the certificate expiry date
   in the operations calendar with an alert well before expiry.
4. Back in IAM Identity Center (Step 2 page): upload the Entra Federation Metadata XML -> accept the change.
5. Test is only possible after the pilot user exists in Identity Center (SCIM, Step 4) or is created
   there manually with a matching username.

## Step 4: SCIM (provisioning)

1. IAM Identity Center -> **Settings** -> **Automatic provisioning** -> **Enable**. Copy the **SCIM endpoint**
   and **Access token** (shown once). Store the token in the team secret store, never in this repo;
   record its expiry and monitor it (AWS: "How to monitor access token expiry").
2. Entra app -> **Provisioning** -> mode **Automatic** -> **Tenant URL** = SCIM endpoint, **Secret Token** =
   access token -> **Test Connection** -> **Save**.
3. **Mappings** (users): `userPrincipalName` -> `userName`; `givenName`, `surname`, `displayName` (all
   required by Identity Center, users missing any are not provisioned); one email only (multi-value
   attributes fail); map a stable unique ID (for example `objectId`) to `externalId`.
4. **Scope**: "Sync only assigned users and groups". Assign the pilot group to the app (P1) or the pilot
   user (Free).
5. **Provision on demand** for the pilot user, then **Start provisioning**.
6. Known limits (AWS doc): nested groups are **not** expanded (only direct members of assigned groups
   are provisioned); dynamic groups are provisioned with their direct members; removing an attribute in
   Entra does not remove it in Identity Center; after enabling SCIM, users cannot be edited in the
   Identity Center console.

## Step 5: permission sets and account assignments (AWS)

1. Create permission sets (table above) with explicit **session duration**; prefer AWS managed
   job-function policies or tightly scoped customer-managed policies; add permissions boundaries where used.
2. **AWS accounts** -> select account -> **Assign users or groups** -> pick the **SCIM-provisioned group**
   -> permission set. Never assign individual users.
3. Optional: ABAC with attributes for access control (AWS tutorial Step 5).

## Step 6: validate (pilot)

| # | Check | Expected |
|---|---|---|
| 1 | Pilot user appears in Identity Center with `externalId` set and the correct group | present |
| 2 | Sign in from the AWS access portal (SP-initiated) and from My Apps (IdP-initiated) | lands in portal; sees only assigned accounts/permission sets |
| 3 | CloudTrail in the target account | activity attributed to the `AWSReservedSSO_<PermissionSet>_<suffix>` role session for the pilot user |
| 4 | Remove the user from the Entra group, wait for a sync / provision on demand | assignment gone in Identity Center |
| 5 | Disable the user in Entra | SAML sign-in fails at once; SCIM deactivates the user |
| 6 | Provisioning logs in Entra | no errors for the pilot objects |

Then widen in waves (by group), keeping the old identity source runbook until all waves pass.

## Rollback

* Before Step 2: delete the Entra enterprise app (no AWS impact).
* After Step 2: switch the identity source back to the previous source per AWS's identity-source
  documentation, then re-create assignments as needed; this is disruptive, which is why the pilot and
  the emergency path come first.
* Disable SCIM by turning off provisioning in the Entra app and disabling automatic provisioning in
  IAM Identity Center; delete the access token.

## Operations

| Cadence | Task | Evidence |
|---|---|---|
| Continuous | Alert on Entra provisioning failures and on SAML signing-certificate and SCIM token expiry | alert rules |
| Quarterly | Access review of every `grp-aws-*` group assigned to the app ([lifecycle](../../identity/governance/docs/access-review-lifecycle.md)); free tier: manual sign-off | review export |
| Quarterly | Reconcile: Entra group members vs Identity Center group members vs account assignments; no direct user assignments | diff report |
| Annually | Rotate the SAML signing certificate (new cert, update AWS, then retire old) and the SCIM token | change records |
| Every 90 days | Emergency-access drill (below) | drill record |

## Emergency access

Identity Center sign-in depends on Entra. AWS recommends setting up emergency access **before** any
disruption and testing it periodically ([AWS emergency access](https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access.html)):

* **IdP up, Identity Center unavailable**: direct SAML 2.0 federation from Entra to a small set of
  critical-operations IAM roles in individual accounts ([IAM SAML providers](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_saml.html)),
  assigned to a dedicated emergency group, alerting on every use.
* **IdP (Entra) unavailable**: AWS break-glass access that does not depend on the IdP (tightly
  controlled IAM principals or root-user procedures with hardware MFA, credentials in dual-control
  safes), alerting on every use.
* **Entra itself locked out**: the Entra break-glass flow
  ([`emergency-access-break-glass.md`](../../identity/governance/docs/emergency-access-break-glass.md)).

Every emergency use gets an incident, a post-mortem, credential rotation where needed and an evidence
bundle, mirroring the Entra flow.
