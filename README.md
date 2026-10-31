# Bank IT operations portfolio

**Delivery candidate — assembled, not independently approved or merged.** This is a personal lab developed with AI assistance. It demonstrates reproducible operational tooling and engineering judgment; it does not claim employment, banking experience, regulatory compliance, or management of real staff.

No cloud account, Microsoft tenant, or bank system is accessed. Cloud templates are **STATIC_VALIDATED**, tenant actions are **PLAN_ONLY**, and fictional vendor/incident examples are **SIMULATION**. A successful automated check does not establish deployment or owner acceptance.

## Start here

**One small next step:** read the [repo navigator](docs/REPO_NAVIGATOR.md#start-here-fast-mode), then choose one check. You do not need to read the entire repository.

- [Reviewer checklist, short PR text and one-page status](docs/REVIEWER_GUIDE.md)
- [20 Copilot, 10 Gemini and 10 ChatGPT prompts](docs/AI_PROMPTS.md)

- [15-minute demonstration](docs/DEMO_WALKTHROUGH_15MIN.md)
- [Job requirements and evidence](docs/JOB_REQUIREMENTS_MATRIX.md)
- [Project case studies](portfolio/README.md)
- [Delivery report and limitations](reports/FINAL_REPORT.md)
- [Remaining owner actions](reports/USER_ACTIONS_REQUIRED.md)

```bash
git clone --branch delivery/portfolio https://github.com/onnxscibroccoli/bank-it-operations-lab.git
cd bank-it-operations-lab
git rev-parse HEAD  # record the exact version you demonstrate
bash scripts/validate-all.sh --python-only
```

The offline suite needs Python 3.10+, OpenSSL 3.x, Git and Bash. No pip packages or credentials are needed. Full PostgreSQL simulation and Node/CDK checks run in GitHub Actions; local full validation additionally needs Node 20+, npm and PostgreSQL server binaries. PostgreSQL cluster initialization must run as a non-root user.

## How the pieces fit

AWS/CDK describes infrastructure without deploying it. Entra validates synthetic identity policies. PostgreSQL exercises backup and recovery in a lab. Shared evidence validators and integration workflows connect their results; these modules are not one running application. A passing module test and permission to merge are separate facts.

AC1 requires independent exact-candidate review; AC2 requires authorized exception decisions; AC3 requires successful checks for the same candidate/base/tested merge; AC4 requires truthful documentation; AC5 requires closure of blocking findings. AC6 is separate final human acceptance. See the [plain-English acceptance table](docs/REPO_NAVIGATOR.md#4-ac1ac6-in-plain-english).

## Evidence labels

| Label | Meaning |
|---|---|
| EXECUTED_LOCAL / EXECUTED_CI | The specific named tool or test ran locally / in Actions; does not imply a live deployment. |
| STATIC_VALIDATED | Configuration or templates were checked without deployment. |
| SIMULATION | Fictional inputs or an intentionally injected incident. |
| PLAN_ONLY | Proposed actions; no tenant changes executed. |
| NOT_EXECUTED | Runbook or operational activity not performed. |

## Module inventory

The machine-readable authority is [coordination/modules.json](coordination/modules.json). INTEGRATED means present in this delivery tree with registered checks; it does not mean reviewed, accepted, or merged. Owner authentication does not make the merge gate eligible. The coverage count includes documentation and is not a production-readiness score.

| Module | State | Entry point |
|---|---|---|
| integration-infra | INTEGRATED | [.github/workflows](.github/workflows) |
| shared-evidence-validator | INTEGRATED | [evidence/shared](evidence/shared) |
| entra-offline | INTEGRATED | [identity/entra](identity/entra) |
| aws-cdk | INTEGRATED | [infra/aws-cdk](infra/aws-cdk) |
| postgres-recovery | INTEGRATED | [tests/integration](tests/integration) |
| orgs-security | INTEGRATED | [infra/orgs](infra/orgs) static only; B6-1/B6-2/B6-3 repaired; not accepted |
| acceptance | NOT_INTEGRATED | Not delivered |
| review-notes | NOT_INTEGRATED | Not delivered |
| portfolio-cases | INTEGRATED | [portfolio](portfolio) |
| vendor-mock | INTEGRATED | [integrations](integrations) |
| observability | INTEGRATED | [observability](observability) |
| final-report | INTEGRATED | [reports/FINAL_REPORT.md](reports/FINAL_REPORT.md) |
| job-requirements-matrix | INTEGRATED | [docs/JOB_REQUIREMENTS_MATRIX.md](docs/JOB_REQUIREMENTS_MATRIX.md) |
| team-management | INTEGRATED | [docs/management](docs/management) |
| learning-guide | INTEGRATED | [learning](learning) |
| control-mapping | INTEGRATED | [governance/controls](governance/controls) |
| patch-hardening | INTEGRATED | [operations/hardening](operations/hardening) |
| identity-governance | INTEGRATED | [identity/governance](identity/governance) |
| hybrid-operations | INTEGRATED | [operations/hybrid](operations/hybrid) |
| m365-endpoint | INTEGRATED | [identity/m365](identity/m365) |
| backup-dr-aws | INTEGRATED | [backup](backup) |
| incident-demo | INTEGRATED | [scenarios](scenarios) |
| bank-aws-001 | SUPERSEDED | Not delivered |
| aws-network-edge | INTEGRATED | [infra/aws-network](infra/aws-network) static only; not deployed |
| endpoint-windows-automation | INTEGRATED | [operations/endpoint](operations/endpoint) STATIC_VALIDATED; not run on Windows |
| inventory-diagrams | INTEGRATED | [Static inventory and generated diagrams](inventory/README.md) |
| owner-authentication | INTEGRATED | [governance/owner-auth](governance/owner-auth) allow-list empty; AC1 still unmet |

## Validation and release

[PR #35](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/35) is the delivery review. [PR #7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) preserves the earlier candidate and coordination record.

`portfolio-validation` runs offline module suites, base AWS/Backup/Organizations/network CDK, Terraform schema validation, PowerShell behavior tests and fresh PostgreSQL exercises before packaging. The existing workflows run the base AWS static tests, PostgreSQL recovery, M365 scenarios and incident simulation. Read each run's exact commit and job conclusions; do not reuse a green result for a different revision.

The separate `merge-eligibility` gate remains fail-closed. Independent reviewer configuration, trusted gate review/protection, owner authentication and exception decisions remain unresolved. This branch changes trusted-file content and therefore also requires deliberate independent re-pinning. No approval or exception is inferred from this README.

The portfolio workflow also runs for PRs targeting the delivery branch. Its `run-summary` job runs after successful or failed dependencies, lists all required job results and outstanding user actions, and uploads `portfolio-run-summary.json` with the tested SHA and run identity. Missing, skipped, cancelled or failed required jobs make the summary fail. This report is validation evidence, not approval; workflow cancellation or runner failure can still prevent its delivery.

Historical reports and old acceptance commands remain in their source PRs; they do not supersede the current gate. No auto-merge is enabled.
