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
- **`merge-eligibility`** always runs, for that run's identity: candidate SHA, base SHA (must equal the **current** `main`, read at runtime) and tested-merge SHA, from `scripts/ci/provenance.py`. It applies the PR #27 C6 policy, and **every technical AC is decided at runtime from authenticated evidence, never from the candidate's own files**:
  - **Trusted gate (R6):** the gate code and the reviewer allow-list come from a trusted manifest (main, else the `evidence/acceptance` branch). The code is checked out by SHA and hash-verified, and the candidate's `scripts/ci`, `.github/acceptance/trusted-config.json` and `integration-gate.yml` must match the manifest (`verify_trusted_gate.py`). Full closure needs branch protection on `main` (UA-3).
  - **AC1:** an APPROVED GitHub review on the exact candidate SHA by an account that is not the PR author, is on the trusted `reviewer_allowlist` and has write/maintain/admin permission; no undismissed CHANGES_REQUESTED from anyone else. **A same-account review can never satisfy AC1**, and neither can a random GitHub account's approval.
  - **AC2:** for every applied exception, an effective owner decision (`ACCEPTANCE-ATTESTATION v2`, `criterion: EXCEPTION`) on PR #7 bound to the exception id, scope, evidence, candidate, main, tested merge and Actions run. States: PROPOSED / APPROVED / REJECTED / APPROVED_WITH_CONDITIONS (effective only after a later CONDITIONS_VERIFIED) / SUPERSEDED. The exception register's own text never approves anything.
  - **AC3:** a merge of the candidate into the current `main` whose required checks all succeeded in that run.
  - **AC4 / AC5:** `ACCEPTANCE-ATTESTATION v2` comments (`criterion: AC4` / `AC5`, `decision: ACCEPT`) by the owner or an allow-listed reviewer, bound to the same candidate / main / tested merge / run; AC5 also needs AC2. GitHub authenticates the author and timestamp; edited comments are ignored. The decision artifact keeps candidate-produced evidence (never sufficient) separate from this independent acceptance.
  - The decision is uploaded as the run artifact `acceptance-decision-<tested sha>`. It is never committed into the tree it describes.
  - AC6 (final human acceptance) is a separate gate.
- **Path to ELIGIBLE** (all owner actions; see `coordination/tasks.json` → `accelerated_plan.round7_pr31_repairs.path_to_eligible` and the USER ACTION REQUIRED list):
  1. Protect `main` (UA-3, exact settings in the UA-3 instructions).
  2. Add an independent reviewer as a collaborator with Write, and add its login to `reviewer_allowlist` in the trusted config.
  3. That reviewer approves PR #7 at the exact candidate SHA.
  4. The owner posts one `ACCEPTANCE-ATTESTATION v2` comment per exception (EX-01..EX-04) and for AC4 / AC5 on PR #7 (format in `scripts/ci/reviews.py` and the UA-1 instructions). No new candidate commit is needed.
  5. Re-run the gate.
- **Module coverage (current):** 7 of 25 modules integrated (28.0%; functional 7/17; denominator 26 including 1 SUPERSEDED, 1 BLOCKED, 14 NOT_INTEGRATED and 3 NOT_STARTED). See `coordination/modules.json`.
- **Merging into `main` is not automated here.** All third-party actions are pinned to full commit SHAs.

Run everything locally with `PG_BIN=/path/to/postgresql/bin bash scripts/validate-all.sh`. `--python-only` skips the Node and PostgreSQL parts.
