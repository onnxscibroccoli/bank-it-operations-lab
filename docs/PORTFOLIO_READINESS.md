# Portfolio reviewer readiness — bank-it-operations-lab

> **Status:** Reviewable documentation plan, not a production certification. **As of:** 2026-11-11. **Tracking:** [local issue](https://github.com/onnxscibroccoli/bank-it-operations-lab/issues/50) · [cross-repository ledger](https://github.com/onnxscibroccoli/broccoli-core/issues/102).  
> Do not interpret AI-assisted source development, successful offline tests or simulations as independently verified industry employment, compliance, or live operations.

## One-minute technical orientation

**Focus:** Infrastructure security, identity policy and data recovery. Credential-free AWS CDK infrastructure synthesis, a strict synthetic Entra Conditional Access schema/baseline validator, and real PostgreSQL restore exercises against disposable database instances.

**What is demonstrable:** The listed source files and explicitly scoped CI runs can be inspected. A reviewer can evaluate the code, rerun supported unit tests, and challenge the architecture decisions. Any claimed practical capability requires the corresponding test, environment, and source revision; not all systems are integrated or generally available.

## Source and reviewer starting points

| Evidence | Path |
| --- | --- |
| Entra offline policy validator | [Inspect](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/main/identity/entra/ca_validator.py) |
| AWS private database infrastructure | [Inspect](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/main/infra/aws-cdk/lib/network-database-stack.ts) |
| PostgreSQL failure/restore harness | [Inspect](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/main/tests/integration/postgres/run_restore_scenario.sh) |
| CI definitions | [Inspect](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/main/.github/workflows/offline-validation.yml) |

## Executed CI references (historical, scoped)

| Check | Exact run |
| --- | --- |
| Offline validation on main | [Run 41751288188](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41751288188) |
| Docs publication on main | [Run 41751288267](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41751288267) |
| Integration gate not eligible on main | [Run 41751288395](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41751288395) |

These run links refer to the specific branch/commit shown on GitHub. They must not be silently attributed to a different current HEAD, production environment, device or approval state.

## Reproduce the relevant local checks

After cloning the repository and reviewing dependencies and safe environment requirements:

```sh
bash scripts/validate-all.sh --python-only
```

This is a **documented command**, not a claim that this portfolio PR executed it. Some modules require dependencies or privileges, and a missing dependency must be reported rather than converted into a false PASS.

## Ordered actionable changes

1. [ ] Explain a 15-minute case study with commands and negative controls; reuse docs/DEMO_WALKTHROUGH_15MIN.md.
2. [ ] Add concise README link to this reviewer map and distinguish current main from historical candidate snapshots.
3. [ ] Refresh job-requirement/evidence matrix only when source SHA has been confirmed; do not imply actual banking experience.
4. [ ] Triage ordinary failing CI separately from expected governance failure; do not weaken AC1–AC6.
5. [ ] After authorized external review, reconcile acceptance exceptions including EX-04 AWS trust assumptions.

## Maturity and verification boundary

Offline/static/synthetic only: no live AWS account, Entra tenant, bank system or real vendor control is tested here. An integration gate failure is an explicit unresolved review boundary, not a missing green badge.

## Release and artifact strategy

Publish docs/site with links to exact completed workflow runs; do not publish a production infrastructure package or bank compliance attestation.

## Safe continuation after interruption

1. Follow the local issue and the [master execution ledger](https://github.com/onnxscibroccoli/broccoli-core/issues/102); inspect existing PRs before creating new ones.
2. Check `git rev-parse HEAD`, repo default branch, current feature branches and fresh Actions conclusions.
3. For each checklist item, implement the smallest change on a reviewable PR; record exact SHA, test scope, successes, failed/untested checks and outstanding decisions.
4. Keep a previously failing independent-approval requirement or live-device gate unresolved until a legitimately authorized actor/environment supplies evidence.
5. Re-read this document against source after changing implementation. Do **not** mark a checklist item complete merely because it is documented.

**Human-only / outside repository assertions:** employment history, professional tenure, team-management responsibilities, third-party audit and approvals.