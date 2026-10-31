# SAML authentication vs SCIM provisioning

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Connect sign-in and account administration across different systems. Separating sign-in from account provisioning helps diagnose why a person can authenticate but still cannot use an application.

For example: An employee signs in through one identity service while a separate process creates the account needed in another application.

Key terms: **SAML** means a format and protocol for passing authentication assertions between systems. **SCIM** means a protocol for creating, updating, and removing identity records across systems. **Federation** means a trust arrangement that lets one system rely on another system’s identity assertions.

**Before using this reference:** A working sign-in design does not prove deprovisioning, entitlement removal, or licensing works.

Start with the [plain-English learning path](../knowledge/identity.md) or [glossary](../knowledge/glossary.md). [Current integration and review policy](../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Reference only; all values are synthetic. Sources:
> [Entra single sign-on](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/what-is-single-sign-on),
> [Entra app provisioning](https://learn.microsoft.com/en-us/entra/identity/app-provisioning/user-provisioning),
> [IAM Identity Center SCIM provisioning](https://docs.aws.amazon.com/singlesignon/latest/userguide/provision-automatically.html),
> [IAM Identity Center with Entra ID](https://docs.aws.amazon.com/singlesignon/latest/userguide/idp-microsoft-entra.html).

## One-line answer

**SAML proves who someone is at sign-in time. SCIM tells the application, ahead of time, which users and
groups exist.** IAM Identity Center needs both when Entra ID is the identity source: SAML for every
sign-in, SCIM so that users and groups exist in Identity Center to receive account and permission-set
assignments.

## Side by side

| | SAML 2.0 (authentication / SSO) | SCIM 2.0 (provisioning / lifecycle) |
|---|---|---|
| Question answered | "Is this person who they claim to be, right now?" | "Which users and groups should exist in the app, with what attributes?" |
| Direction | Browser-mediated: IdP (Entra) signs an assertion, browser posts it to the SP's ACS URL | Server-to-server: Entra provisioning service calls the app's SCIM REST endpoint |
| When | On every sign-in | On a sync cycle driven by the IdP, plus on-demand provisioning |
| Trust material | IdP signing certificate (in metadata) + SP entity ID / ACS URL | Bearer token issued by the app (IAM Identity Center access token) + SCIM endpoint URL |
| Payload | Signed XML assertion: `NameID`, attributes, audience, validity window | JSON `User` / `Group` resources: `userName`, `name`, `displayName`, `emails`, `externalId`, `active`, group `members` |
| Creates the user? | No (in IAM Identity Center a SAML assertion for a user not provisioned fails) | Yes: create, update, deactivate / delete |
| Removes access? | Indirectly: user can no longer authenticate at the IdP | Directly: deprovisions or deactivates the user and group membership |
| Licence (Entra) | SSO for pre-integrated (gallery) enterprise apps is free ([plan SSO: licensing](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/plan-sso-deployment#licensing)); assigning **groups** to an app is a P1 feature ([Entra pricing](https://www.microsoft.com/en-us/security/business/microsoft-entra-pricing)) | User provisioning available on Free; **group** provisioning needs P1 or above ([licensing fundamentals](https://learn.microsoft.com/en-us/entra/id-governance/licensing-fundamentals)) |
| Typical failure | Clock skew, wrong ACS/entity ID, expired signing cert, `NameID` not matching a provisioned username | Expired SCIM token, missing required attribute, multi-value attribute, nested group not provisioned, user not assigned to the app |

## How they must line up (IAM Identity Center)

AWS states that the attribute Entra sends as the SAML subject `NameID` must be the same attribute that
SCIM maps to `userName`; otherwise sign-in fails. AWS also recommends mapping SCIM `externalId` to a
stable, unique value such as the Entra `objectId` so renames do not break assignments.

```
Entra user (synthetic)                        SCIM -> IAM Identity Center user          SAML assertion at sign-in
  objectId  b9a5e000-...-000000000010   ──▶  externalId  b9a5e000-...-000000000010
  userPrincipalName avery.admin@bankitlab.example ──▶ userName avery.admin@bankitlab.example ◀── NameID avery.admin@bankitlab.example
  givenName / surname / displayName     ──▶  name.givenName / name.familyName / displayName (all required)
  mail                                  ──▶  emails[primary] (single value, unique)
```

Synthetic SCIM `User` as the provisioning service would send it (illustrative):

```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "externalId": "b9a5e000-0000-4000-8000-000000000010",
  "userName": "avery.admin@bankitlab.example",
  "name": {"givenName": "Avery", "familyName": "Admin"},
  "displayName": "Avery Admin (synthetic)",
  "emails": [{"value": "avery.admin@bankitlab.example", "type": "work", "primary": true}],
  "active": true
}
```

Synthetic SAML assertion subject and attributes (abridged, illustrative):

```xml
<saml:Subject>
  <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">avery.admin@bankitlab.example</saml:NameID>
</saml:Subject>
<saml:AttributeStatement>
  <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress">
    <saml:AttributeValue>avery.admin@bankitlab.example</saml:AttributeValue>
  </saml:Attribute>
</saml:AttributeStatement>
```

## Governance consequences

* **Joiner**: assign the user (or a group, with P1) to the Entra enterprise app; SCIM creates the user and
  group membership; AWS permission-set assignments on that group take effect; SAML lets them sign in.
* **Mover**: group membership change in Entra, then SCIM updates membership, then AWS access changes on the next sync.
* **Leaver**: disabling the Entra account blocks SAML immediately; SCIM then deactivates the Identity
  Center user. Existing AWS console or CLI sessions can outlive both, so the leaver runbook must also
  cover active-session handling on the AWS side.
* **Access reviews** on the Entra groups that are assigned to the AWS app therefore govern AWS access
  ([access-review-lifecycle](../../identity/governance/docs/access-review-lifecycle.md)).
