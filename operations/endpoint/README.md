# Endpoint and Windows automation (static)

PowerShell for a synthetic joiner/mover/leaver and an Intune compliance baseline.
Nothing here runs against Active Directory, Entra, or Intune. The checker is Python and
does not require Windows. Evidence class: **STATIC_VALIDATED**. A Pester run on a
domain-joined host is **NOT_EXECUTED**.

Regulatory context, not a control test of a bank:

- Interagency Guidelines (access control, least privilege): a joiner gets one role group; a leaver is disabled and removed from privileged groups before any license change.
- FFIEC Architecture, Infrastructure, and Operations: endpoint firewall policy is default-deny inbound.
- The scripts refuse cleartext passwords, `Invoke-Expression`, and an unconstrained execution-policy bypass.
