# Browse topics by subject and depth

Use this page when you know the subject but not the document. Every indexed page appears below, grouped by its subject (the `category` field in [page metadata](../metadata/pages.json)), with its lifecycle status and the depth levels it serves. The list is generated at build time from that metadata, so it cannot drift from the search index.

## How depth levels work

Each page declares one or more audience levels. Read in this order and stop whenever you have what you need:

1. **beginner**: everyday language, no account or installation needed.
2. **operator**: responsibilities, procedures, and what to check.
3. **engineer**: source code, commands, tests, and evidence formats.
4. **architect**: design decisions, tradeoffs, and limits.
5. **reference**: preserved records and detailed material to consult rather than read start to finish.

The search page has a **Depth level** filter that uses the same values. A level describes intended readers. It does not say the content was reviewed or verified; see the [status vocabulary](lifecycle.md).

## Recommended entry point for each subject

| Subject | Start with | Then go deeper |
|---|---|---|
| Getting started | [Start learning](start.md) | [Repository navigator](../REPO_NAVIGATOR.md) |
| Identity and access | [Control employee permissions](identity.md) | [Identity governance module](../../identity/governance/README.md), [Entra policy validator](../../identity/entra/README.md), [federation notes](../federation/README.md) |
| Backup and disaster recovery | [Backups and recovery](recovery.md) | [PostgreSQL restore harness](../../tests/integration/README.md), [AWS Backup reference](../../backup/aws/README.md), [AWS Backup runbooks](../runbooks/aws-backup/README.md) |
| Incident response | [Investigate an outage](incident.md) | [Incident simulation](../../scenarios/incident/README.md), [observability module](../../observability/README.md) |
| Infrastructure as code | [Infrastructure as code](infrastructure.md) | [AWS CDK module](../../infra/aws-cdk/README.md), [Organizations module](../../infra/orgs/README.md), [network edge](../../infra/aws-network/README.md) |
| Operating systems and automation | [Infrastructure as code](infrastructure.md) | [Patching](../../operations/patching/README.md), [hardening](../../operations/hardening/README.md), [hybrid Windows operations](../../operations/hybrid/README.md), [endpoint automation](../../operations/endpoint/README.md) |
| Governance and evidence | [Read evidence responsibly](governance.md) | [Architecture decisions](../adr/README.md), [ADR status on main](../adr/STATUS.md), [vendor risk](../../governance/vendor-risk/README.md) |
| Structured learning | [Twelve-week guide on main](../../learning/CURRENT.md) | [Original guide](../../learning/README.md) |
| Using the documentation itself | [Technical reference](reference.md) | [Troubleshooting](troubleshooting.md), [Learn with AI](ai.md) |

## All pages by subject

Archived pages are listed last within each subject. Archived means a preserved historical record whose bytes are protected; read its stated date and revision before relying on it.

<!-- generated:topic-catalog -->
