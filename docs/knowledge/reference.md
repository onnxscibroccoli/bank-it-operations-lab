# Technical reference

This page indexes the reference material: what each module is, where its decisions are recorded, and how the documentation's own data is structured. Read it when you need a precise source rather than an explanation. For explanations, start at [Start learning](start.md).

## Modules

The authoritative list is [coordination/modules.json](../../coordination/modules.json): 28 modules, each with its paths, required checks, evidence classes and limitations. A generated, file-level cross-reference of modules to their documentation is written to `dist/docs/inventory.json` by `python3 scripts/docs/audit.py` after a build. The registry's own statement of a module's limits is quoted in each page's status panel and in [the discovery report](audit.md).

| Area | Module reference | Validation entry point |
|---|---|---|
| AWS storage, network and database (CDK) | [infra/aws-cdk](../../infra/aws-cdk/README.md) | `cd infra/aws-cdk && npm ci && npx jest` |
| AWS Organizations guardrails | [infra/orgs](../../infra/orgs/README.md), [Terraform track](../../infra/orgs/terraform/README.md) | see module README |
| AWS network edge | [infra/aws-network](../../infra/aws-network/README.md) | see module README |
| AWS Backup and DR reference | [backup/aws](../../backup/aws/README.md), [runbooks](../runbooks/aws-backup/README.md) | see module README; runbooks are NOT_EXECUTED |
| PostgreSQL backup and restore harness | [tests/integration](../../tests/integration/README.md), [evidence](../../evidence/postgres/README.md) | `python3 tests/integration/postgres/verify_evidence.py <run>` |
| Entra Conditional Access (offline) | [identity/entra](../../identity/entra/README.md), [tests](../../tests/entra/README.md) | `python3 -m unittest discover -s tests/entra -v` |
| Identity governance (fixture Graph client) | [identity/governance](../../identity/governance/README.md) | `python3 identity/governance/inventory.py --scenario baseline ...` |
| Microsoft 365 and endpoint (offline) | [identity/m365](../../identity/m365/README.md), [operations/endpoint](../../operations/endpoint/README.md) | see module README |
| Observability | [observability](../../observability/README.md) | `python3 observability/run_healthcheck.py evaluate ...` |
| Incident simulation | [scenarios/incident](../../scenarios/incident/README.md) | `python3 scenarios/incident/lib/timeline.py --verify <run>` |
| Vendor API mock (SIMULATION) | [integrations/vendor-mock](../../integrations/vendor-mock/README.md) | `python3 -m unittest discover -s tests -t . -v` in the module |
| Patching and hardening | [operations/patching](../../operations/patching/README.md), [operations/hardening](../../operations/hardening/README.md) | see module README |
| Hybrid Windows, AD DS, DNS, GPO | [operations/hybrid](../../operations/hybrid/README.md), [runbooks](../runbooks/hybrid/README.md) | runbooks are NOT_EXECUTED |
| Shared evidence validator | [evidence/shared](../../evidence/shared/README.md) | `bash scripts/validate-all.sh --python-only` |
| Acceptance gate (offline; never reports ACCEPTED) | [tools/acceptance](../../tools/acceptance/README.md), [gate](../../tools/acceptance/gate), [adapters](../../acceptance/modules/README.md), [schemas](../../schemas/acceptance/README.md), [integration record](../../acceptance/INTEGRATION-V2.md) | `python3 -m unittest discover -s tools/acceptance/tests -v` |
| Asset inventory and diagrams | [inventory](../../inventory/README.md), [architecture](../../inventory/ARCHITECTURE.md) | see module README |

Exact commands and observed results for the runnable rows are in [Tutorials](tutorials.md).

## Architecture decisions

- [ADR index](../adr/README.md): seventeen repository-level decisions (0001–0017), each citing the branch and commit where its code lived when written.
- [ADR status on main](../adr/STATUS.md): where each decision's code is now on main, and why every ADR is still Proposed.
- Module-level ADRs also exist inside some modules, in `infra/aws-cdk/docs/adr`, `infra/orgs/docs/adr` and `backup/aws/docs/adr`.

## Status vocabulary

[Status vocabulary](lifecycle.md) defines the four separate vocabularies: documentation lifecycle, evidence labels, registry states and ADR status. The [glossary](glossary.md) defines technical terms.

## Documentation data and tooling

| File | Purpose |
|---|---|
| [docs/metadata/pages.json](../metadata/pages.json) | Per-page metadata: id, description, category, audience levels, lifecycle status, limitations, source files, related development, verification level/scope/date/evidence, last review date, optional reading guide |
| [docs/metadata/schema.json](../metadata/schema.json) | JSON Schema the builder enforces for pages.json |
| [docs/metadata/terminology.json](../metadata/terminology.json) | Canonical term definitions; each must appear in the glossary |
| [docs/metadata/preserved-records.json](../metadata/preserved-records.json) | SHA-256 digests of byte-locked historical records |
| [scripts/docs/build.py](../../scripts/docs/build.py) | Static builder: Markdown to sanitized HTML, `search-index.json`, `metadata.json`, `coverage.json`, `llms.txt` |
| [scripts/docs/search-core.js](../../scripts/docs/search-core.js) | Token and alias search scoring; no network calls |
| [scripts/docs/tests](../../scripts/docs/tests) | Python build/metadata tests, Node search tests, Playwright browser and axe checks |
| [.github/workflows/documentation.yml](../../.github/workflows/documentation.yml) | CI build, checks and GitHub Pages deployment |

Metadata lives in this sidecar file rather than in front matter inside each Markdown file. That keeps preserved records byte-identical, so their digests still match. The owning module shown on each page is derived at build time from the longest matching registry path; it names a module, not a person.

## Reports and records

- [Acceptance packet](../../reports/ACCEPTANCE.md) (its header still says DRAFT and not merged, but it reached main with PR #40), [acceptance invariant assurance](../../reports/ACCEPTANCE_INVARIANT_ASSURANCE.md).
- [Final report](../../reports/FINAL_REPORT.md), [evidence manifest](../../reports/EVIDENCE_MANIFEST.md), [owner actions](../../reports/USER_ACTIONS_REQUIRED.md), [integration record](../../reports/INTEGRATION.md).
- [Reviewer guide](../REVIEWER_GUIDE.md), [fifteen-minute walkthrough](../DEMO_WALKTHROUGH_15MIN.md), [job requirements matrix](../JOB_REQUIREMENTS_MATRIX.md).
