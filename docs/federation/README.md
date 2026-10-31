# Federation references

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Connect sign-in and account administration across different systems. Separating sign-in from account provisioning helps diagnose why a person can authenticate but still cannot use an application.

For example: An employee signs in through one identity service while a separate process creates the account needed in another application.

Key terms: **SAML** means a format and protocol for passing authentication assertions between systems. **SCIM** means a protocol for creating, updating, and removing identity records across systems. **Federation** means a trust arrangement that lets one system rely on another system’s identity assertions.

**Before using this reference:** A working sign-in design does not prove deprovisioning, entitlement removal, or licensing works.

Start with the [plain-English learning path](../knowledge/identity.md) or [glossary](../knowledge/glossary.md). [Current integration and review policy](../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Reference only. Nothing here changes a Microsoft Entra tenant or an AWS account; every identifier is
> synthetic (`bankitlab.example`, `b9a5e000-...` GUIDs, `111122223333`-style AWS account IDs used in AWS docs).

| Doc | Content |
|---|---|
| [`saml-vs-scim.md`](saml-vs-scim.md) | SAML 2.0 authentication vs SCIM 2.0 provisioning: what each does, how they meet, failure modes |
| [`entra-to-aws-iam-identity-center.md`](entra-to-aws-iam-identity-center.md) | Microsoft Entra ID -> AWS IAM Identity Center walkthrough (SAML + SCIM + permission sets), validation, rollback, emergency access |

Related: [`identity/governance/`](../../identity/governance/README.md) (privileged-role inventory, PIM,
access reviews, break-glass, licensing).
