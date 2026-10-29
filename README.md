# bank-it-operations-lab
Reproducible IT operations reference lab

> **Lab only.** Everything in this repository is offline, synthetic or a deliberately injected SIMULATION.
> Nothing is deployed. No cloud account, Microsoft 365 tenant or real bank system is touched, and no credentials are used.

## What is integrated (branch `overnight/integration`, PR #7; not yet merged to `main`)

The authoritative list, with paths, checks and status for every module, is `coordination/modules.json`.

| Module | Source | Status | Checks (validate-all step / CI job) |
|---|---|---|---|
| Shared evidence validator (`evidence/shared`) | PR #3 | integrated | unit tests, cross-bundle checks / `offline-validation` |
| Entra Conditional Access, offline (`identity/entra`, `tests/entra`) | PR #4 | integrated. **The baseline choices are pending owner confirmation (UA-2); see `evidence/entra/BASELINE-CHOICES-PENDING.md`** | unit tests, baseline, fixture drift, evidence verify |
| AWS CDK private VPC + RDS + secure storage (`infra/aws-cdk`, `evidence/aws`) | PR #5, which **supersedes PR #1** | integrated. Exceptions EX-01..EX-04 are unapproved (UA-1); review findings B5-1 and B5-2 are open | tsc, jest, synth, cdk-nag (4 reports), synth drift / `aws-cdk` |
| PostgreSQL backup/restore harness v2 (`tests/integration/postgres`, `evidence/postgres`) | PR #2 @ `e7399fb` | integrated | v2 verify, harness self-test, fresh offline run / `postgres-restore-evidence` (5 jobs) |
| M365 / endpoint offline scenarios (`identity/m365`, `evidence/m365`) | PR #20 @ `1b3c240` | integrated; **required**. Every remediation step is PLAN_ONLY (`executed: false`, `mutationsExecuted: 0`) | `m365-scenario-evaluation`, `m365-unit-tests`, `m365-evidence-verification`, `plan-only-assertions` |
| Incident demo, SIMULATION (`scenarios/incident`, `evidence/incident`) | PR #22 @ `9f21329` | integrated; **required** | `incident-committed-runs`, `incident-fresh-run`, `incident-not-executed-negative`, `labeling-markers` |

PR #1 (`bank-aws-001`) is **superseded by PR #5**. It is still open, and its description shows the old S3 self-logging
design that PR #5 removed (ADR-0004). Only its CI workflow was carried over, adapted as `.github/workflows/aws-cdk.yml`.
Closing PR #1 is user action UA-4. PR #6 is BLOCKED: B6-1 (trail access-logs bucket logs to itself), B6-2 (exempt-role SCP bypass) and B6-3 (the requested Terraform track is missing; PR #6 is CDK only). Fixing B6-1/B6-2 alone does not admit it.

M365 counts:
- **13** scenarios evaluated, each matching its expected verdict and finding codes.
- **43** PLAN_ONLY plan steps across those scenarios. These are planned actions, not assertions.
- 29 unit tests.

## Gate behaviour (`.github/workflows/integration-gate.yml`)

- **`user-actions`** runs first. It publishes the USER ACTION REQUIRED list from `coordination/tasks.json` to the run summary and as annotations.
- **Required jobs** are listed in `coordination/modules.json` → `required_gate_jobs`.
  - `incident-fresh-run` must also report `PASS` for injection, detection, diagnosis, recovery, timeline and simulation (`required_gate_outputs`).
  - It runs a fresh SIMULATION scenario on PostgreSQL server binaries that apt installs on the runner. No services container is used.
  - If the binaries are missing, the harness exits 3 (NOT_EXECUTED). That fails the job; it never passes.
- **`final-summary`** always runs. It fails if any required job is missing, skipped, cancelled or failed, or if any required output is not `PASS`.
- **`merge-eligibility`** always runs, for that run's identity: candidate SHA, base SHA and tested-merge SHA, from `scripts/ci/provenance.py`. It applies the PR #27 C6 policy:
  - The gate code runs from `main` (once it carries the gate scripts) or from a pinned SHA, not from the candidate's own copy. The candidate's data is read with `--root`.
  - AC1 is computed at runtime from the GitHub reviews API with the read-only `GITHUB_TOKEN`. It needs an APPROVED review on the exact candidate SHA by an account other than the PR author. **A same-account review can never satisfy AC1**, and AC1 "MET" in `tasks.json` is rejected.
  - AC3 is computed at runtime. It holds only for a merge of the candidate into the **current** `main`, whose SHA is read at runtime; a merge into any other parent is invalid. All required checks must also have succeeded in that run.
  - AC2, AC4 and AC5 must be MET and bound to that exact identity, with full 40-hex SHAs. Any applied cdk-nag suppression tied to a non-APPROVED exception (`scripts/ci/check_exceptions.py`) is a blocking user action (UA-1) and keeps AC2 and AC5 UNMET.
  - The decision is uploaded as the run artifact `acceptance-decision-<tested sha>`. It is never committed into the tree it describes.
  - AC6 (final human acceptance) is a separate gate.
- **Merging into `main` is not automated here.** All third-party actions are pinned to full commit SHAs.

Run everything locally with `PG_BIN=/path/to/postgresql/bin bash scripts/validate-all.sh`. `--python-only` skips the Node and PostgreSQL parts.
