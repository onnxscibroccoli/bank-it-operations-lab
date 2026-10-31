# Endpoint and Windows automation (static)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Describe and validate administrative changes to user devices before applying them. Plans and expected results make operational intent reviewable before permissions or devices change.

For example: An operator checks a Windows configuration plan and reviews a Microsoft 365 onboarding scenario without modifying a real account.

Key terms: **Endpoint** means a user or service device connected to an organization’s systems. **M365** means microsoft 365, a collection of productivity and administration services. **Intune** means microsoft’s device and application management service. **Plan-only** means produces proposed actions without executing those actions.

**Before using this reference:** No actual device enrollment, mailbox change, or tenant modification is proven. Real execution needs separate permission and environment checks.

Start with the [plain-English learning path](../../docs/knowledge/identity.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


PowerShell for a synthetic joiner/mover/leaver and an Intune compliance baseline.
Nothing here runs against Active Directory, Entra, or Intune. The checker is Python and
does not require Windows. Evidence class: **STATIC_VALIDATED**. A Pester run on a
domain-joined host is **NOT_EXECUTED**.

Regulatory context, not a control test of a bank:

- Interagency Guidelines (access control, least privilege): a joiner gets one role group; a leaver is disabled and removed from privileged groups before any license change.
- FFIEC Architecture, Infrastructure, and Operations: endpoint firewall policy is default-deny inbound.
- The scripts refuse cleartext passwords, `Invoke-Expression`, and an unconstrained execution-policy bypass.

The lifecycle command only emits JSON tagged `mode=PLAN_ONLY`, `executed=false`, `mutationsExecuted=0`. Actions execute in Pester on an Ubuntu PowerShell runner, not against a domain or tenant. `lab.example` identities are synthetic. Invalid input and unsupported actions must throw.

`python3 operations/endpoint/validate_baseline.py` checks Intune settings and the firewall reference. Its tests mutate settings, CIDRs, ports and action values to prove rejection. The profile default blocks unmatched inbound traffic; it is deliberately separate from explicit rules because an explicit block-all rule overrides specific allows in Windows Firewall. No Windows firewall was changed.

References: [Windows Firewall rule precedence](https://learn.microsoft.com/windows/security/operating-system-security/network-security/windows-firewall/rules), [Pester CI](https://pester.dev/docs/v5/commands/Invoke-Pester).
