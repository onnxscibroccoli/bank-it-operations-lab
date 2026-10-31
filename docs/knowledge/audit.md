# Discovery, capability coverage, and documentation gaps

## Scope and baseline

Snapshot: 2026-10-31, delivery candidate `85fbf9d24954ecfdb5cbea30199e212c7daf2c61` plus the documentation increment. Main remains the initial README-only commit. No other development branch was merged. Existing module declarations below are attributed registry statements, not new verification results.

The baseline has 207 Markdown files. The generator indexes every tracked or unignored Markdown file and produces `inventory.json` with a complete file inventory and module-to-document mapping, and `coverage.json` with curated/legacy counts. Historical evidence is preserved verbatim.

## Capability coverage map

The registry's INTEGRATED label means code or documentation is present in this delivery tree. A declared evidence class is not a current successful execution. For each module, inspect its source README, tests, workflow, and run identity before concluding anything about operational readiness.

| Capability | Registry state | Declared evidence class | Source / documentation entry |
|---|---|---|---|
| integration-infra | INTEGRATED | EXECUTED_CI | [.github/workflows](../../.github/workflows) |
| shared-evidence-validator | INTEGRATED | EXECUTED_LOCAL, EXECUTED_CI | [evidence/shared](../../evidence/shared) |
| entra-offline | INTEGRATED | EXECUTED_LOCAL, EXECUTED_CI, STATIC_VALIDATED | [identity/entra](../../identity/entra) |
| aws-cdk | INTEGRATED | EXECUTED_LOCAL, EXECUTED_CI, STATIC_VALIDATED | [infra/aws-cdk](../../infra/aws-cdk) |
| postgres-recovery | INTEGRATED | EXECUTED_LOCAL, EXECUTED_CI | [tests/integration](../../tests/integration) |
| orgs-security | INTEGRATED | STATIC_VALIDATED | [infra/orgs](../../infra/orgs) |
| acceptance | NOT_INTEGRATED | Not declared | Not present in this branch |
| review-notes | NOT_INTEGRATED | Not declared | Not present in this branch |
| portfolio-cases | INTEGRATED | Not declared | [portfolio](../../portfolio) |
| vendor-mock | INTEGRATED | Not declared | [integrations](../../integrations) |
| observability | INTEGRATED | Not declared | [observability](../../observability) |
| final-report | INTEGRATED | Not declared | [reports/FINAL_REPORT.md](../../reports/FINAL_REPORT.md) |
| job-requirements-matrix | INTEGRATED | Not declared | [docs/JOB_REQUIREMENTS_MATRIX.md](../../docs/JOB_REQUIREMENTS_MATRIX.md) |
| team-management | INTEGRATED | Not declared | [docs/management](../../docs/management) |
| learning-guide | INTEGRATED | Not declared | [learning](../../learning) |
| control-mapping | INTEGRATED | Not declared | [governance/controls](../../governance/controls) |
| patch-hardening | INTEGRATED | Not declared | [operations/hardening](../../operations/hardening) |
| identity-governance | INTEGRATED | Not declared | [identity/governance](../../identity/governance) |
| hybrid-operations | INTEGRATED | Not declared | [operations/hybrid](../../operations/hybrid) |
| m365-endpoint | INTEGRATED | EXECUTED_LOCAL, EXECUTED_CI, PLAN_ONLY | [identity/m365](../../identity/m365) |
| backup-dr-aws | INTEGRATED | Not declared | [backup](../../backup) |
| incident-demo | INTEGRATED | EXECUTED_LOCAL, EXECUTED_CI, SIMULATION | [scenarios](../../scenarios) |
| bank-aws-001 | SUPERSEDED | Not declared | Not present in this branch |
| aws-network-edge | INTEGRATED | STATIC_VALIDATED | [infra/aws-network](../../infra/aws-network) |
| endpoint-windows-automation | INTEGRATED | STATIC_VALIDATED | [operations/endpoint](../../operations/endpoint) |
| inventory-diagrams | INTEGRATED | STATIC_VALIDATED | [inventory](../../inventory) |
| owner-authentication | INTEGRATED | STATIC_VALIDATED | [governance/owner-auth](../../governance/owner-auth) |
| knowledge-base | INTEGRATED | Not declared | [scripts/docs](../../scripts/docs) |

## Findings and limitations

- Documentation is spread across modules, evidence directories, runbooks, and historical review records. Keep paths stable; index rather than relocate.
- Source relationships and required checks exist in the module registry. Some narrative limitations refer to older findings; they need independent reconciliation before status promotion.
- Existing evidence includes deliberately invalid historical records and simulated outcomes. A uniform success label would misrepresent them.
- Legacy pages lack the new metadata contract and progressive explanations. The portal visibly marks this review gap rather than inventing status.
- Existing Mermaid/code diagrams need individual review for equivalent text; the initial portal renders them as source text, not inferred images.
- The initial glossary covers fifteen common terms. The broader vocabulary, individual reference coverage, and audience-specific pathways remain incomplete.
- Search uses deterministic tokens and related terms. It is not semantic reasoning; broad matches can include irrelevant historical pages. Curated educational pages receive a small documented preference.
- Accessibility baseline had no documentation portal to test. New interface checks apply only to the new interface and curated pages. They do not certify historical content.

## Next increments

1. Review each major module's evidence and write a standalone capability page, starting with PostgreSQL, identity, and incident response.
2. Expand glossary entries and validate their sources; report missing definitions without fabricating them.
3. Improve legacy headings, code fences, diagram equivalents, and anchor validation while preserving evidence files.
4. Complete assistive-technology testing with real users and record unresolved findings.
5. Publish documentation after branch review and Pages setup, separately from infrastructure changes.

## AI and contributor use

The machine inventory includes source paths, related PRs, declared checks, documentation coverage gaps, and explicit fresh-verification boundaries. Use it to choose the next review, not to claim every capability has passed. The [metadata standard](standards.md) controls new pages; the [development guide](development.md) explains reproduction.
