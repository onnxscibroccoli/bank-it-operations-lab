# FINAL REPORT: bank-it-operations-lab

> **DEADLINE: midnight ET (00:00 EDT, Thursday 2026-10-29), the end of Wednesday 2026-10-28.**
> **Remaining window at commit time (2026-10-28 21:47 EDT): about 2 h 12 min.**
> Status: **not complete.** Nothing is merged into `main` (`7f50348`, unchanged). The live integration candidate is PR #7 @ `1fdf25a`. It integrates **7 of 25 active modules**: 26 registered, 1 superseded. Every technical CI job is green, and its merge-eligibility check reports **NOT ELIGIBLE** (AC1, AC2, AC4 and AC5 UNMET; AC3 MET at runtime). No non-author review exists on any PR. Nothing here claims completion that was not verified.

- Repo: https://github.com/onnxscibroccoli/bank-it-operations-lab
- Snapshot: 2026-10-28, about 21:47 EDT (UTC-4). The live candidate is in §L; other current heads are in §0c. Older sections are kept as history and name the SHA they checked. `main` @ [`7f50348`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/7f50348bf1370381615eaed91c02607fe41de2f5) holds only `README.md` and has not changed since the repo was created.
- **Nothing is merged into `main`. Nothing is deployed. No AWS, Entra or Graph credentials were used.** All 31 PRs (#1–#31) are open. None has an APPROVED GitHub review from an account other than the PR author. Review notes #14 and #27–#31 come from the author account `onnxscibroccoli`.
- **Evidence labels:**
  - **[re-run]**: re-executed on the box for this report.
  - **[CI]**: a linked GitHub Actions run.
  - **[#14 review]**: the independent review notes in [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) (`reports/review-pr3-pr6.md` @ `eb8d259`, which includes checkpoint 2). They were written by a reviewer who is neither the code author nor this automation. They are **not** a GitHub review and **not** a human sign-off.
  - **[PR body]**: taken from the PR text only.
  - **UNVERIFIED**: not checked.
- **Rule: a passing scanner is not enough.** Zero cdk-nag errors, a passing `cfn-s3-selflog` or a passing `sha256sum -c` shows only that a tool ran. Acceptance also needs review of the exact SHA, adjudicated exceptions, docs that match the code, and no blocking findings. #5 is the example: both cdk-nag packs report 0 unsuppressed errors, yet #14 found a KMS privilege-escalation path that the scanner and the repo's own guard (`guards.ts#kmsWildcards`) both miss.
- Companion files: [`MODULE_REQUIREMENT_MAP.md`](MODULE_REQUIREMENT_MAP.md) (per-module job row, authoritative source, falsifiable acceptance requirement, evidence, review disposition), [`USER_ACTIONS_REQUIRED.md`](USER_ACTIONS_REQUIRED.md) and [`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md). Hiring-manager entry points: root [`README.md`](../README.md), [`docs/DEMO_WALKTHROUGH_15MIN.md`](../docs/DEMO_WALKTHROUGH_15MIN.md), and the job-matrix addendum on branch `docs/job-matrix-addendum` @ [`9fb49fa`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/9fb49fa96903bf5b0de58dad7c5741c30d6a7d3d/docs/JOB_REQUIREMENTS_MATRIX.md).

## L. Live candidate: PR #7 @ `1fdf25a` (checked about 21:40 EDT)

- **#7 head:** `1fdf25ad10c56bb457d6242392f9305c539d1209` (pushed 21:25 EDT; confirmed with `gh pr view 7` at 21:42 EDT). **main:** `7f50348bf1370381615eaed91c02607fe41de2f5`, unchanged; the gate confirmed `main_sha_at_runtime` equals the base.
- **New since `7fe6d72`:** `b908a66` (AC3 provenance, root README), `51e404c` (module registry, 26 modules), `a29f4d9`, `80f01d6` (**B5-2 fix**: least-privilege KMS key admin), `4e6fef4` (trusted gate: AC1 from the reviews API, exception register blocks AC2/AC5) and `1fdf25a`. That is 7 commits and 45 files.
- **CI at `1fdf25a`:**
  - integration-gate [40800364073](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800364073) (pull_request) and [40800359209](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800359209) (push): 18/19 success.
  - main-validation [40800374574](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800374574) (merge `85063e8`): 18/19.
  - In all three, the only failing job is `merge-eligibility`, which fails by design while criteria are unmet.
  - aws-cdk [40800363940](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800363940): Jest 36/36.
  - postgres-restore-evidence [40800363954](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800363954) and offline-validation [40800364076](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800364076): success.
- **merge-eligibility (run 40800364073, gate code pinned at `4e6fef4`):** `NOT ELIGIBLE`.
  - `AC1: UNMET` (no APPROVED review by a non-author account).
  - `AC2: UNMET` (UA-1: 5 applied suppressions tied to non-APPROVED EX-01..EX-04).
  - `AC3: MET_AT_RUNTIME` (`07eea1c`).
  - `AC4: UNMET (PARTIAL)`.
  - `AC5: UNMET` (UA-1).
- **Re-run here at `1fdf25a`:**
  - `validate-all.sh --python-only` PASS (33 steps)
  - `scripts/ci/tests` 93 OK
  - shared validator 16, Entra 25, M365 29 OK
  - Postgres VERIFIED
  - AWS `SHA256SUMS` 44/44 OK
  - `check_modules.py`: `MODULE COVERAGE: 7/25 integrated (28.0%)`
- **Reviews of the live candidate:** [#31](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/31) @ `eccac83` says **CHANGES REQUIRED** on `1fdf25a`. It confirms B5-2, F1, N1 and B5-3 fixed. It lists as still open:
  - B5-1 (UA-1)
  - F4: AC1 accepts an approval from any GitHub account on this public repo
  - F6: AC2/AC4/AC5 can only reach MET via self-referential in-tree `met_for`
  - R6: the pin is candidate-controlled
  - F7: approval is a text edit

  It was written from the author account, so it is not an AC1 approval. F4, F6, R6 and F7 are **as reported, not re-verified here**. [#30](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/30) gave the same verdict on `b908a66`.
- **Superseded:** final candidate `7fe6d72` (§P, history) and `b908a66`. The README and demo walkthrough are re-pinned to `1fdf25a`.

## M. Module coverage and revised ETA (about 21:47 EDT)

Full map: [`MODULE_REQUIREMENT_MAP.md`](MODULE_REQUIREMENT_MAP.md). Source classes:
- **supervisory:** FFIEC IT Handbook; OCC Bulletin 2023-17, the OCC/FRB/FDIC interagency third-party guidance.
- **industry:** NIST SP 800-53/61/34/40/137.
- **product:** AWS, Microsoft, PostgreSQL, systemd, GitHub and cdk-nag documentation.
- **project-specific (repo-defined):** AC1–AC6, `modules.json`, the exception register and the job matrix.

**No regulatory source** (statute or regulation text) is mapped. Everything is "mapped to"; no certification or compliance is claimed.

| Active modules (denominator) | Integrated in `1fdf25a` | Verified (re-run or CI at exact SHA) | Independently accepted |
|---|---|---|---|
| **25** (26 registered − 1 SUPERSEDED) | **7** (28.0%) | 14; plus 1 partial (#21) and 1 unverified (#6) | **0** |

The earlier figure of 22 planned modules was wrong. It left out the 3 NOT_STARTED registry modules.

**Revised ETA** (map §4):
- **Earliest:** about 01:30–03:00 EDT Thursday.
- **Likely:** Thursday daytime or later.
- **Main uncertainty:** AC1 needs an approving account other than `onnxscibroccoli`, and none has been identified. #31's F6 gate-design fix is also needed.
- **Critical-path owner:** the integrator, with Ian (UA-1, UA-2, AC6) and an unidentified independent reviewer on the path.

**No merge meeting AC1–AC5 is achievable by midnight on current evidence.**

## R. User-action reconciliation (re-done about 21:47 EDT against `1fdf25a`)

CI prints, in run [40800364073](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800364073), `user-actions` job:
```
USER ACTION REQUIRED: 4 — UA-1; UA-2; UA-3; UA-4
MODULE COVERAGE: 7/25 integrated (28.0%), functional 7/17; denominator 26 (BLOCKED=1, INTEGRATED=7, NOT_INTEGRATED=14, NOT_STARTED=3, SUPERSEDED=1)
```
and, in `merge-eligibility`, five `BLOCKING USER ACTION (UA-1): suppression … is applied while EX-0N is PROPOSED` lines.

Reconciled top line: **`USER ACTION REQUIRED: 2 — UA-1 EX-01..EX-04 decisions to record in the register (EX-04 role-review gap); UA-2 Entra CA baseline choices`**.

**Correction:** this report's 21:04 EDT reconciliation marked EX-01 and EX-03 "RESOLVED_BY_RECORD" and narrowed UA-1 to EX-04. That was too strong. Ian's decisions on EX-01, EX-03 and EX-04 are **conditional**. None is recorded as `APPROVED` in the register. The live gate's `check_exceptions.py` counts only the exact word `APPROVED`, so **UA-1 covers all four exceptions** until the register is updated. Per-exception detail is in §3.

| ID | CI item | Reconciled class | Evidence |
|---|---|---|---|
| UA-1 | Approve or reject EX-01..EX-04 and the applied cdk-nag suppressions | **USER_ACTION_REQUIRED**, blocking AC2/AC5 | Register @ `1fdf25a`: "Status of every entry: **PROPOSED, pending owner approval.**" `check_exceptions.py` reports 5 suppressions tied to PROPOSED entries. Decisions relayed by Ian are in §3. None is an unconditional approval except EX-02 |
| UA-2 | Confirm the Entra CA baseline choices | **USER_ACTION_REQUIRED** | `evidence/entra/BASELINE-CHOICES-PENDING.md` @ `1fdf25a` records them as PENDING. No decision is recorded |
| UA-3 | Branch protection on `main` | **OWNER_DECISION, non-blocking** | `GET …/branches/main/protection` → 404 "Branch not protected" (unset, not 403). Admin is held. `blocks: []` |
| UA-4 | Close PR #1 as superseded | **HOUSEKEEPING** | `bank-aws-001` is SUPERSEDED in `modules.json`. AC4 notes PR #1's body is stale |
| UA-5 | AC6 final acceptance | **NOT_YET_ACTIONABLE** | Applies only after AC1–AC5 are MET for one SHA |

Not user actions:
- **AC1 is a GATE.** It needs a non-author APPROVED review on the exact SHA.
- **#31's F4, F6 and R6 are AUTONOMOUS_FIX items for the integrator.**
- **B5-2 is FIXED**, per `tasks.json` and #31.

This report does not edit `coordination/tasks.json` or the register; both belong to other owners. The full history of the earlier reconciliation at `08cdf11` and `7fe6d72` is in git history at commit `29969b4`.

## P. Final portfolio sprint (about 20:24 EDT): evidence classification of every artifact

Labels, used throughout the portfolio docs:
- **EXECUTED**: it ran; a CI run URL or an evidence hash is cited. Offline runs on synthetic data are EXECUTED for the tool, never for a live system.
- **SIMULATION**: it ran against a simulated or fictional system (#22 incident demo, #9 vendor mock).
- **NOT_EXECUTED**: reference only (runbooks, designs, undeployed IaC, documentation).

"Re-run" = re-executed on the box at about 20:20–20:25 EDT against the cited head (unit tests, verifiers, `sha256sum -c`).

### P1. Integration candidate #7

- #7 has moved to `f3c5c46`. Since `4f54a01` it added the integration gate (`82ab7e6`), required M365 checks (`02ac2de`), merges of **#20 at exact SHA `1b3c240`** (`c6c1061`) and **#22 at exact SHA `9f21329`** (`0964281`), required checks for both (`5f159f1`), and a record commit (`f3c5c46`). These are merges into the integration branch, **not into `main`**.
- **Candidate `5f159f1`: EXECUTED (CI).** integration-gate [run 40792426144](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426144): 18 of 19 jobs success; `merge-eligibility` failure = **NOT ELIGIBLE** (by design). aws-cdk [40792426294](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426294), postgres [40792426140](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426140), offline-validation [40792426193](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426193), offline-validation push [40792418146](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792418146): success.
- **Head `f3c5c46`:** integration-gate [run 40793001918](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793001918) again 18/19, `merge-eligibility` NOT ELIGIBLE with notices `AC1: UNMET`, `AC2: PARTIAL`, `AC3: MET for 5f159f1…, not this SHA`, `AC4: PARTIAL`, `AC5: UNMET`. aws-cdk [40793001811](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793001811), postgres [40793001796](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793001796), offline-validation [40793001807](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793001807): success.
- **Re-run:** `scripts/validate-all.sh --python-only` PASS (30 steps) at both `5f159f1` and `f3c5c46` (needs a git work tree; a plain tarball fails the module-registry step). The two trees differ only in `coordination/` and `reports/INTEGRATION.md`.
- **Discrepancy:** #7's own review packet (`coordination/review-requests/PR-7-candidate-5f159f1.md`) says the review is **NOT YET REQUESTED**. No independent review of `5f159f1` exists, so AC1 is unmet.
- Earlier candidate `02ac2de` had a **failing** offline-validation ([40791325340](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40791325340)); it was superseded by `5f159f1`, which passes.

### P2. Per-artifact classification

| PR @ head | Artifact | Label | Evidence (checked here unless noted) |
|---|---|---|---|
| #2 @ `e7399fb` | Postgres backup/restore harness v2 | **EXECUTED (CI)**, real PostgreSQL | [run 40741329107](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107); `verify_evidence.py ci-service-40741329107-1` re-run: VERIFIED, problems=0; integrated CI [40792426140](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426140) |
| #5 @ `099479e` | AWS CDK VPC + RDS + nag | **EXECUTED (CI)** synth/Jest/nag; deployment **NOT_EXECUTED** | [40792426294](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40792426294); open B5-1, B5-2 |
| #4 @ `d302c99` | Entra CA validator | **EXECUTED** offline; tenant **NOT_EXECUTED** | bundle 46 hashes OK; `ca_validator.py` re-run `overall=PASS` |
| #3 @ `fb36341` | Shared evidence validator | **EXECUTED (CI)** | offline-validation runs above |
| #20 @ `1b3c240` | M365 / endpoint scenarios | **EXECUTED** offline, PLAN_ONLY (`mutationsExecuted=0`) | 29 tests re-run OK; bundle 20 hashes OK; `m365_ops.py` re-run 13/13; CI m365 jobs success in 40792426144. **Resolves the earlier UNVERIFIED note on #20** |
| #22 @ `9f21329` | Incident demo | **SIMULATION** | `timeline.py --verify` re-run PASS; 38 hashes OK; `incident-fresh-run` success in 40792426144. Head moved `3f13622` → `9f21329` (labels + notes only) |
| #26 @ `eb42b23` | Acceptance vertical slice | **EXECUTED (CI)** | §0b |
| #23, #24, #25 | Acceptance contract / runner / adapters | **EXECUTED (CI)**, not re-run | [40747710616](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40747710616), [40747893103](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40747893103), [40748526680](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748526680) |
| #10 @ `3e40e39` | Observability collector | **EXECUTED** local offline, no CI | 64 tests re-run OK; bundle 44 hashes OK |
| #9 @ `d6efb82` | Vendor API mock, vendor risk, RACI | **SIMULATION** (fictional vendor), no CI | 45 + 25 tests re-run OK (vendor-mock needs `-t .` from its own dir, per its README); 3 bundles OK |
| #17 @ `5605b78` | Patch rings, hardening | **EXECUTED** inspectors; patching **NOT_EXECUTED**; no CI | 9 + 18 tests re-run OK; bundle 102 hashes OK |
| #18 @ `f48e7e3` | Identity governance | **EXECUTED** offline; PIM/federation **NOT_EXECUTED**; no CI | 65 tests re-run OK; bundle 49 hashes OK |
| #16 @ `3f82697` | FFIEC AIO mapping | **EXECUTED** validator; mapping is a study reference | 10 tests re-run OK |
| #21 @ `10da54f` | AWS Backup DR + cost model | **NOT_EXECUTED** (all 7 recovery items); cost model EXECUTED offline | `RECOVERY_EXECUTION_STATUS.json`; 8 cost tests OK; 72 hashes OK; CDK Jest not re-run |
| #19 @ `3397dac` | Hybrid Windows/AD/DNS/GPO runbooks | **NOT_EXECUTED** | `EXECUTION_STATUS.md` all rows; lint re-run 0 findings |
| #6 @ `e5e7f46` | Organizations / SCP / GuardDuty / Security Hub | **NOT_EXECUTED** reference, blocked B6-1/B6-2 | local static evidence only |
| #13, #15, #8, #12 | Team model; learning guide; case studies; job matrix | **NOT_EXECUTED** (documentation) | n/a |
| #14, #27 | Independent review notes | review documents, not GitHub reviews | n/a |

### P3. Job posting alignment

- The posting text is **not in the repo**. The only in-repo source is the matrix (#12 @ `31b69db`), which cites the JobLeads page. That page was re-read at about 20:20 EDT: live, and consistent with matrix rows A1–D4. **Discrepancy:** schema.org `validThrough` (2026-10-22) is earlier than `datePosted` (2026-10-27).
- The newer modules are mapped to requirement IDs in the **matrix addendum (section G)** on branch `docs/job-matrix-addendum` @ [`9fb49fa`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/9fb49fa96903bf5b0de58dad7c5741c30d6a7d3d/docs/JOB_REQUIREMENTS_MATRIX.md). It is built on #12's head, appends only, and leaves sections A–F and the coverage counts to the matrix owner.

### P4. Documentation handoff for the integrator

Files: `README.md` (root; **conflicts with the root README that #7 has carried since `b908a66`**, still present at `1fdf25a`, which `modules.json` assigns to integration-infra; the integrator chooses: keep #7's and link to this hub, or move this hub to `docs/`), `docs/DEMO_WALKTHROUGH_15MIN.md`, `reports/MODULE_REQUIREMENT_MAP.md`, `reports/FINAL_REPORT.md`, `reports/USER_ACTIONS_REQUIRED.md`, `reports/user-actions.json`, `reports/EVIDENCE_MANIFEST.md` on `reports/final-report`; `docs/JOB_REQUIREMENTS_MATRIX.md` on `docs/job-matrix-addendum` (parent `31b69db`). None of it changes code, workflows, or another module's files.

## 0a. Accelerated completion plan ([#27](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27) @ `72aa8b7`, ChatGPT independent review): per-item verified status
Source: `reports/independent/chatgpt/accelerated-completion-plan-20261028.md` (snapshot about 17:57 EDT) and `acceptance-181bcdd-review.md`. This report only records status. Implementation belongs to the lane owners #27 names.

Status key:
- **VERIFIED**: checked here at about 18:08 EDT.
- **OPEN**: not done, or not shown.
- **UNVERIFIED**: claimed but not checked here.

| Plan item | Lane / owner (per #27) | Status | Evidence |
|---|---|---|---|
| P0: assess the repaired C1–C4 at a frozen SHA | E: independent review | **PARTIAL.** Re-checked here at `eb42b23` (§0b). #27 itself ran the 32 tests at `35674c4`. No independent SHA-bound *closure* record exists yet | §0b |
| P0: authenticate review provenance; bind approval scope to requirements and SHA | A: Worker D, plus the owner | **OPEN.** `decide.py` takes reviews only via `--reviews`; reviewer identity is an unauthenticated string. All PRs share one author account, so a GitHub approval by that account is impossible → AC1 **GATE** (§R; formerly listed as UA-1) | `decide.py --help`; PR author check |
| P0: wire the final decision into one actual merge gate | B: integrator, plus the owner | **OPEN.** CI computes the decision (`REVIEW_PENDING`, exit 5, asserted) but nothing enforces it: `main` has **no branch protection and no rulesets** (API 404 / `[]`) → CI UA-3, **OWNER_DECISION, non-blocking** (§R: 404 unset, not a 403 permission failure) | [run 40776065038](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776065038) log; GitHub API |
| P0: test current main + candidate together; serialize merges | B: integrator | **OPEN / UNVERIFIED.** The workflows test the PR head. No combined main+candidate run was found | C5 in #27 |
| P0: every in-scope module present **and** registered with an executable check | B, C | **OPEN.** The inventory `required-checks.v1.json` covers AWS, Postgres, Entra, workers A/B/C and hashes only. Monitoring, incident, backup, patch, identity-gov, M365, hybrid, vendor and orgs have no required checks | `scripts/acceptance/required-checks.v1.json` @ `eb42b23` |
| P1: full-SHA action pins, 7-day retention, timeouts | B: integrator | **OPEN.** `acceptance.yml` @ `eb42b23` still uses `actions/*@v5` tags and `retention-days: 30` (C5) | file @ `eb42b23` |
| P1: update coordinator policy and obsolete PR text (C6) | Coordinator (#7) | **DONE in #7 @ `4f54a01`** (VERIFIED). `tasks.json` rules now permit independently proven automated merges, keep AC6 human portfolio acceptance separate, and keep every technical blocker. Open PR bodies (for example #7's "Do not merge without independent human review") were not re-checked | `coordination/tasks.json` @ `4f54a01` |
| P1: module CI adapters, job mapping, operator demo, consolidated report | C, D | **OPEN.** Module tests pass locally (§1), but most modules still have no CI. #22 is a SIMULATION demo with no CI | §1 |
| P1: reconcile #6 self-logging before including it | C: #6 owner | **OPEN.** #6 head is still `e5e7f46`; B6-1 and B6-2 are unchanged | head table |
| Hardening: derive dynamic HASH/ENTRA members from the tree (no minimum counts) | A | **OPEN** (VERIFIED). The inventory still says "contiguous 1..n with n >= min" (`min: 17`, `min: 1`) | inventory @ `eb42b23` |
| Hardening: `git_show_sha256()` must fail closed | A | **OPEN** (VERIFIED). It still returns `None` on error (`verify_results.py:101-106`) | file @ `eb42b23` |
| Hardening: review records scoped to explicit requirement IDs | A | **UNVERIFIED** | — |
| User-action reporting format (top line plus typed fields) | Reports (this PR) **and** B (the Actions job) | **Report side DONE** in `USER_ACTIONS_REQUIRED.md` and `reports/user-actions.json`. **The Actions publishing job is OPEN** (lane B, `.github/workflows/**`, outside this role) | this commit |
| At the deadline, publish the actual state: delivered / tested / accepted / merged / pending / user actions | Reports (this PR) | This report, refreshed at each checkpoint. **Merged: none. Accepted: none.** | — |

## 0b. C1–C6 repair status (findings from #27 review of `181bcdd`)
The repairs are in #26: `85c66cf` (invariants), `17cfaea` ("repair C1-C4 from independent review (PR #27)"), `35674c4` (assurance note) and the current head **`eb42b23`**.

| Finding | Status | Verification |
|---|---|---|
| **C1** The verifier accepted bundles that were missing required checks | **REPAIRED (VERIFIED locally at `eb42b23`)** | #27's own probe (one `ARBITRARY` PASS row with resealed hashes) is now `verify_results: REJECTED … errors=34`, exit 1. A reviewed inventory `required-checks.v1.json` is bound to the tested commit. Remaining weakness: groups use **minimum counts** (hardening item above) |
| **C2** A required INFO produced PASS | **REPAIRED (VERIFIED locally)** | `gate([required=yes, verdict=INFO])` → `FAIL` |
| **C3** JSON and TSV verdicts could disagree; the target was not bound | **REPAIRED (VERIFIED locally)** | #27's TSV-PASS/JSON-FAIL probe → `REJECTED … errors=33`, exit 1. `verify()` now takes `expect_sha`. CI shows `SOURCE-BINDING` PASS at the target and FAIL on the defect run |
| **C4** Contract approval was not the executable final gate | **PARTIALLY REPAIRED.** Decision logic exists; it is **not enforced** | **[CI] [40776065038](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776065038)** (push, `eb42b23`, success): `OVERALL=PASS required=44`; `execution-pass-for: EXECUTION_PASS (not ACCEPTED …)`; `decide exit=5`; `{"state": "REVIEW_PENDING", "technically_eligible": true, "contract_valid": true, "reviews_supplied": 0}`. Still open: authenticated review provenance (AC1 gate) and an enforced merge gate (CI UA-3, non-blocking owner decision; §R) |
| Regression suite | **VERIFIED** | `python3 -m unittest discover -s scripts/acceptance/tests` at `eb42b23`: 32 tests OK (this box). #27 reports the same at `35674c4` |
| CI at `eb42b23` | **VERIFIED: all success** | acceptance push [40776065038](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776065038), acceptance PR [40776074032](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776074032), aws-cdk [40776074036](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776074036), postgres [40776073933](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776073933), offline-validation [40776073952](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776073952). At `35674c4`, aws-cdk run 40776057836 was **cancelled** (superseded) |
| **C5** Action tags, 30-day retention, head-only testing | **OPEN (VERIFIED as not fixed)** | `acceptance.yml` @ `eb42b23` |
| **C6** Obsolete coordination constraints | **DONE in #7 @ `4f54a01`** (VERIFIED in `tasks.json`) | see §0a |

## 0c. Current heads of all PRs and branches (GitHub API, about 18:08 EDT; #7, #11, #22 refreshed at about 20:24 EDT)
`main` = `7f50348` (unchanged). All 27 PRs are open drafts, none merged, all authored by `onnxscibroccoli`.

| PR | Branch | Head |
|---|---|---|
| [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) | `bank-aws-001` | `e494bcfc` |
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | `ci-evidence-postgres` | `e7399fbb` |
| [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) | `review/pr1-pr2-evidence-audit` | `fb363411` |
| [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) | `entra-ca-offline` | `d302c99d` |
| [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) | `aws-remediation-vpc-rds` | `099479e6` |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | `orgs-security-refs` | `e5e7f460` |
| [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) | `overnight/integration` | `1fdf25a` (live candidate; see §L) |
| [#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8) | `portfolio-cases` | `7010d05a` |
| [#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) | `vendor-mock` | `d6efb825` |
| [#10](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/10) | `observability` | `3e40e39d` |
| [#11](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/11) | `reports/final-report` | this commit (parent `e31cce9`) |
| [#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12) | `job-requirements-matrix` | `31b69db9` |
| [#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13) | `team-management` | `9dc8f1f5` |
| [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) | `review/pr3-pr6` | `eb8d2595` |
| [#15](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/15) | `learning-guide` | `39728dbe` |
| [#16](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/16) | `control-mapping` | `3f826975` |
| [#17](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/17) | `patch-hardening` | `5605b788` |
| [#18](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/18) | `identity-governance` | `f48e7e3f` |
| [#19](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/19) | `hybrid-operations` | `3397dac9` |
| [#20](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/20) | `m365-endpoint` | `1b3c2403` |
| [#21](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/21) | `backup-dr-aws` | `10da54f8` |
| [#22](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/22) | `incident-demo` | `9f21329` (was `3f136225`; see §P2) |
| [#23](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/23) | `acceptance-contract` | `6a28847b` |
| [#24](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/24) | `acceptance-runner` | `838d537a` |
| [#25](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/25) | `acceptance-adapters` | `ce395047` |
| [#26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26) | `acceptance/vertical-slice` | `eb42b237` |
| [#27](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27) | `review/chatgpt-acceptance-181bcdd` | `72aa8b74` |

Heads that **moved since the last verification** in this report, and were not re-verified here:
- #7 `4f54a01`: CI green, [40774982708](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40774982708) aws-cdk, [40774983086](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40774983086) postgres, [40774982933](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40774982933) offline-validation, plus push runs
- #8 `7010d05`
- #9 `d6efb82`
- #15 `39728db`
- #20 `1b3c240`: **now verified** (§P2): 29 tests, evidence hashes, and CI inside #7
- #26 `eb42b23`: verified, §0b

## 0. Update at about 17:43 EDT: three claims from Ian, each verified before recording
| # | Claim | Verified here? | What was checked / discrepancies |
|---|---|---|---|
| 1 | Acceptance vertical slice complete: [#26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26) @ `181bcdd`, Actions run 40749373581 green | **VERIFIED, with limits** | **Run:** [40749373581](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749373581) is workflow `acceptance`, push, head **`181bcdd1420d699c37aa928b636b9332aca83e57`** (= #26 head), conclusion **success**, created 14:53:58 EDT. All 3 jobs succeeded.<br>**Log, `acceptance @ target SHA` job:** `CHECKOUT … worktree HEAD == 181bcdd…`, `OVERALL=PASS required=43 fail=[] unknown=[]`, `verify_results: OK overall=PASS rows=45 errors=0`. PG-01..03 PASS (PG 18 offline cluster). DEFECT-AWS, -ENTRA and -HASH PASS (each detected for its intended reason).<br>**Log, `defect control` job:** injected CA002 report-only → `OVERALL=FAIL`, as asserted.<br>**Other runs at the same SHA:** the PR-event runs [40749387217](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387217) (acceptance), [40749387209](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387209) (aws-cdk), [40749387223](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387223) (offline-validation) and [40749387416](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387416) (postgres) all succeeded.<br>**Limits and discrepancies:**<br>• #26's own `reports/ACCEPTANCE.md` §5 still lists UNKNOWN gaps: results are not yet emitted as a contract document, there is no independent `concur` record, C's contract is provisional, and AWS/RDS/Entra are not executed live.<br>• [#25](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/25) `acceptance-adapters` has moved to `ce39504` (a contract emitter); #26 integrated the earlier `c6aa238`.<br>• #26 carries all of #7 (`49122f2`) as its base, so merging it means merging #2–#5. Its packet says it does not approve that.<br>• "Complete" here means an executable gate that runs green in CI on a draft PR. It is **not** merged, **not** human-reviewed and **not** accepted into `main` |
| 2 | Postgres v2 verification complete on [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) @ `eb8d259` | **VERIFIED, by reading plus spot re-runs** | #14 head is `eb8d259` ("checkpoint 2", 14:16 commit; section dated 14:30 EDT).<br>**What #14 verified:** harness v2 at `2aac93c`/`e7399fb` asserts the reason for every negative (N01–N06 regexes); a setup failure gives NOT_RUN, never PASS; the S04 version gate; the replay of the bad run 40630856041 now gives ERROR, not PASS; the verifier rejects a forged PASS; the CI artifacts of run 40741329107 are byte-identical to the committed runs; the NOTE.md and STATUS.json corrections are accurate; there are no `continue-on-error` false-green paths. Verdict: **"Status of priority B: remediated."**<br>**My own re-runs at `e7399fb`:** `selftest_harness.sh` passes 26/26 assertions. `verify_evidence.py` gives VERIFIED on ci-service (36 cases), ci-offline (38) and local-offline-v2 (38); REJECTED on the mismatch control (correct); HISTORICAL (exit 3) on both v1 runs. Run 40741329107 is head `2aac93c`, push, success.<br>**Open, non-blocking (from #14):**<br>• the declared-reason regex is checked before the env/version-error regex, so a log containing both is classed PASS<br>• the verifier trusts the run's own EXPECTATIONS.tsv<br>• `cdk-synth` shows green when no CDK app exists<br>#14 did **not** run the PG scenario locally, and it is agent review notes, not a human GitHub review |
| 3 | Incident demo [#22](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/22) open with an executed SIMULATION | **VERIFIED: open draft @ `3f13622`; SIMULATION evidence verifies** | **Run:** `evidence/incident/runs/local-20261028T181818Z` (executed 14:18 EDT on the lab box). SHA256SUMS 38/38 OK. `timeline.py --verify` → `VERIFY PASS (SIMULATION run …)`. `selftest.sh <run>` → 4/4 PASS (pristine verifies, forged MTTD rejected, missing detection event rejected, missing PG → NOT_EXECUTED exit 3).<br>**SUMMARY.json:** `simulation: SIMULATION`, status PASS, 19/19 steps, MTTD 3.584 s, MTTR 8.593 s, DB unavailable 3.878 s.<br>**This is a SIMULATION:** a deliberate `pg_ctl stop -m immediate` on a throwaway loopback lab DB. It is **not a live incident** and not production; the escalation is illustrative.<br>**Caveats:** no CI on #22. It uses PG 17.10 binaries from an npm embedded-postgres package. I did not re-execute the demo itself, only verified its committed evidence and ran the self-test |

## 1. Per-module acceptance: 5 criteria
- **C1 Review:** an independent reviewer examined the **exact current head SHA**. A human GitHub review is still needed for merge (G1 below).
- **C2 Exceptions:** every suppression, allowlist entry or policy choice is adjudicated by the owner.
- **C3 Checks:** CI and/or a local re-run passes on that SHA, including negative tests that are able to fail (no false PASS).
- **C4 Docs:** the README, PR body and evidence match the code.
- **C5 Findings:** no unresolved blocking findings remain, and no superseded unsafe code is carried.

Key: ✅ met · ⚠️ partial or conditional · ❌ not met · — not applicable

| Module (PR @ head) | C1 Review | C2 Exceptions | C3 Checks | C4 Docs | C5 Findings | Accepted? |
|---|---|---|---|---|---|---|
| BANK-AWS-001 storage ([#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) @ `e494bcf`) | ⚠️ Reviewed at this SHA only by #3's audit; no GitHub review | — | ✅ [CI 40631310661](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631310661). [re-run]: hashes 87/87, Jest 21/21, synth OK | ❌ Describes the self-logging design as secure | ❌ AccessLogsBucket logs to itself ([re-run] `cfn-s3-selflog` ERROR). Superseded by #5 | **No: close as superseded** |
| Postgres backup/restore ([#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) @ `e7399fb`) | ⚠️ [#14 review] checkpoint 2 at `2aac93c`/`e7399fb`: false-PASS fix **remediated** (agent notes; no human GitHub review) | — | ✅ [CI 40741546543](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741546543) and [40741536430](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741536430). [re-run] self-test 26/26; verifier VERIFIED on 3 current runs, REJECTED on the control, HISTORICAL on the v1 runs | ✅ PR body updated | ✅ No blocking items. Non-blocking hardening: regex ordering, self-attested EXPECTATIONS.tsv, cdk-synth green-on-skip | **Conditional:** needs a human review of `e7399fb` |
| Evidence audit and shared validator ([#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) @ `fb36341`) | ⚠️ [#14 review]: **Approve** at exact SHA | — | ✅ [re-run] 13/13. No CI of its own; runs in #7 CI | ✅ | ✅ none blocking | **Conditional:** needs a human GitHub review |
| Entra CA offline ([#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) @ `d302c99`) | ⚠️ [#14 review]: **Approve with comments** at exact SHA | ⚠️ Baseline choices unconfirmed (risk policies report-only, device scope, 12 roles) | ✅ [re-run] 25/25, validator exit 0, evidence verify OK | ✅ | ✅ Non-blocking follow-ups: CA007 baseline rule, failing rule IDs in logs, CI | **Conditional:** owner confirms the baseline and a human reviews |
| AWS remediation VPC+RDS ([#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) @ `099479e`) | ⚠️ [#14 review]: **Request changes** at exact SHA | ⚠️ EX-01..EX-04: Ian's decisions relayed (EX-02 accepted; EX-01, EX-03 and EX-04 conditional). The register @ `1fdf25a` is still PROPOSED, so UA-1 is open (§3) | ✅ [re-run] hashes 32/32, tsc OK, Jest 33/33, synth OK, `cfn-s3-selflog` OK. Also runs in #7 CI | ❌ The "least-privilege CMK" claim is contradicted by B5-2. "One rule, one resource" is wrong (EX-02 covers 2 resources). The register still says PROPOSED | ❌ **B5-2**: unconditioned `kms:Create*`/`kms:Put*` for account root on 3 CMKs allows CreateGrant/PutKeyPolicy escalation. **B5-1**: suppressions were applied before approval. **B5-3**: conflicts with #1 | **No** |
| Organizations reference ([#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) @ `e5e7f46`) | ⚠️ [#14 review]: **Request changes** at exact SHA | ⚠️ 2 parliament allowlist entries, not adjudicated | ✅ [re-run] hashes 66/66, Jest 49/49, synth OK. **No CI** | ❌ The "hardened S3" README claim is false. The Terraform-to-CDK deviation is undocumented | ❌ **B6-1** S3 self-logging ([re-run] ERROR). **B6-2** exempt-role-name SCP bypass. **B6-3** Terraform plan deviation | **No** |
| Integration ([#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) @ `49122f2`) | ❌ No human review of `49122f2`. #14 reviewed only its postgres harness portion | ⚠️ Inherits #5 | ✅ [CI] at `49122f2`, all success: aws-cdk [40743606730](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743606730); offline-validation [40743606409](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743606409) and [40743592407](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743592407); postgres [40743606483](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743606483). Also exercised inside #26's acceptance run (base). Earlier head `afb41278`: CI green, `validate-all.sh --python-only` 20/20 [re-run] | ⚠️ Its own AC4 is PARTIAL | ❌ It integrates #5 with unresolved **B5-2**, while #7's AC5 says MET (not re-read at `49122f2`) | **No** |
| Portfolio case studies ([#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8) @ `6c25c05`) | ❌ None | — | ⚠️ [re-run] citation check (§4): 130/130 GitHub links resolve, all blob/tree/commit links are SHA-pinned, and the 5 cited Actions runs match conclusion and SHA | ⚠️ Prose claims not checked beyond the links | ✅ none found | **No:** needs review |
| Vendor mock, SIMULATION ([#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) @ `88a3785`) | ❌ None | — | ✅ [re-run] 45/45 tests, `check_governance.py` exit 0, both evidence runs verify (12/12 and 14/14). **No CI** | ✅ Labeled SIMULATION; claims no real-vendor compatibility | ✅ none found | **No:** needs review and CI |
| Observability ([#10](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/10) @ `3e40e39`) | ❌ None | — | ✅ [re-run] 64/64 tests, `generate_evidence.py --verify` PASS, SHA256SUMS 44/44. The evidence is for `2613ea2`, a clean tree. **No CI** | ⚠️ Not reviewed beyond the README | UNVERIFIED (no code review done) | **No:** needs review |
| Job requirements matrix ([#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12) @ `31b69db`) | ❌ | — | UNVERIFIED | UNVERIFIED | UNVERIFIED | **No:** opened during the snapshot, not checked |
| Synthetic team model ([#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13) @ `9dc8f1f`) | ❌ | — | UNVERIFIED | UNVERIFIED | UNVERIFIED | **No:** opened during the snapshot, not checked |
| Review notes #3–#6 ([#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) @ `981db0a`) | — (it is the review) | — | Spot-checked: B6-1 and the #5 exception facts agree with this report's [re-run] and template extracts | ✅ | — | Docs only. Summary in §4a |
| Backup/DR AWS ([#21](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/21) `backup-dr-aws` @ `10da54f`) | ❌ None | ⚠️ Has its own `SECURITY_EXCEPTIONS.md`, not adjudicated | ⚠️ [re-run] SHA256SUMS 72/72 OK; cost-model tests 8/8; evidence-validator tests 8/8; CDK: tsc OK, Jest OK (46 passed, 46 total), synth OK. **No CI** | ⚠️ Not reviewed | UNVERIFIED | **No.** PR #21 opened 14:17 EDT. `RECOVERY_EXECUTION_STATUS.json` says **NOT_EXECUTED** for every backup, copy and restore job: no recovery has been demonstrated |
| Incident demo, SIMULATION ([#22](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/22) @ `3f13622`) | ❌ | — | ✅ [re-run] evidence verifies (38/38), `--verify` PASS, self-test 4/4. **No CI** | ✅ Labeled SIMULATION throughout | UNVERIFIED (no code review) | **No:** a simulation demo, not a live incident; needs review |
| Acceptance contract A ([#23](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/23) @ `6a28847`) | ⚠️ #26 packet: ACCEPT (Worker D, agent) | — | Exercised inside #26 CI (ACC-A-01/02 PASS) | UNVERIFIED | — | **No:** lands via #26 |
| Acceptance runner B ([#24](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/24) @ `838d537`) | ⚠️ #26 packet: ACCEPT | — | Exercised inside #26 CI (ACC-B PASS) | UNVERIFIED | — | **No:** lands via #26 |
| Acceptance adapters C ([#25](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/25) @ `ce39504`) | ⚠️ #26 packet: ACCEPT WITH FIX, reviewed at `c6aa238` | — | Only `c6aa238` is exercised in #26. **`ce39504` (contract emitter) is not integrated** | UNVERIFIED | ⚠️ The PASS+NOT_EXECUTED bug was fixed only in #26 (`93de4b3`) | **No** |
| **Acceptance vertical slice ([#26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26) @ `eb42b23`)** | ⚠️ #27 review of `181bcdd`: CHANGES REQUIRED (C1–C6). C1–C3 repaired; C4 partial (§0b) | — | ✅ **[CI] at `eb42b23`**: [40776065038](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776065038) EXECUTION_PASS, decision **REVIEW_PENDING** (correct), plus 4 PR-event runs green. Earlier: [40749373581](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749373581) @ `181bcdd` | ⚠️ The assurance note says DRAFT, not an approval | ❌ C5 open; carries #5's B5-2 via #7 | **No:** technically eligible, review pending, no merge gate |
| Learning guide and ADRs ([#15](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/15) @ `52a63c0`) | ❌ | — | ✅ [re-run] all 40 `sha:path` citations exist (`git cat-file -e`). Two more matches are ARN fragments, not citations | UNVERIFIED (prose) | — | **No:** needs review |
| FFIEC AIO control mapping ([#16](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/16) @ `3f82697`) | ❌ | — | ✅ [re-run] 10/10 tests; `validate_mapping.py` reports MAPPING VALID (17 rows, 97 artifacts; OBSERVED=0) | UNVERIFIED (mapping accuracy against FFIEC text) | — | **No:** needs review. Lab only, not an exam or certification |
| Patch rings and hardening ([#17](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/17) @ `5605b78`) | ❌ | — | ✅ [re-run] 18/18 + 9/9 tests; evidence `--verify` PASS (113 inputs); SHA256SUMS 102/102. **No CI** | UNVERIFIED | UNVERIFIED | **No:** needs review |
| Identity governance, Graph fixtures ([#18](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/18) @ `f48e7e3`) | ❌ | — | ✅ [re-run] 65/65 tests; evidence `--verify` OK; SHA256SUMS 49/49. **No CI** | UNVERIFIED | UNVERIFIED | **No:** needs review |
| Hybrid/AD runbooks ([#19](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/19) @ `3397dac`) | ❌ | — | ✅ [re-run] 10/10 tests; `check_hybrid_runbooks.py`: 12 files, 0 findings. The runbooks themselves are marked NOT_EXECUTED | UNVERIFIED | — | **No:** needs review |
| M365/endpoint scenarios ([#20](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/20) @ `86a555a`) | ❌ | — | ⚠️ [re-run] `m365_ops.py`: 13/13 scenarios PASS, 0 mutations executed. **No unit tests and no committed evidence run** (only `.gitignore` under `evidence/m365`) | UNVERIFIED | — | **No:** needs review and evidence |
| Final report ([#11](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/11)) | ❌ | — | — | — | — | Draft |

## 2. Merge policy and per-PR merge-gate status
**Policy (recorded per Ian):** nothing merges into `main` until **all** gates G1–G7 pass for the exact head SHA, and G8–G9 hold. Automation never merges, closes PRs or deploys.
- **G1:** a human reviewer examined and approved the exact head SHA.
- **G2:** every exception is adjudicated.
- **G3:** all checks pass on that SHA.
- **G4:** docs match the code.
- **G5:** integration-tested with the other PRs it ships with.
- **G6:** revalidated against current `main` right before merge.
- **G7:** post-merge verification on `main` (CI plus evidence re-verify), with a revert if it fails.
- **G8:** no false-pass tests.
- **G9:** no superseded unsafe code is carried.

| PR | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 | ❌ | — | ✅ | ❌ | ❌ superseded in #7 | ⚠️ conflicts with #5 | n/a | ✅ | ❌ self-logging | **BLOCKED (close)** |
| #2 | ❌ (#14 agent review: remediated) | — | ✅ | ✅ | ✅ in #7 and #26 | ⚠️ re-check at merge | pending | ✅ **v2 fix verified** ([#14 review] checkpoint 2 plus [re-run] self-test and verifier) | ✅ | **BLOCKED (G1 only)** |
| #3 | ❌ (agent approve only) | — | ✅ | ✅ | ✅ in #7 | ⚠️ | pending | ✅ | ✅ | **BLOCKED (G1)** |
| #4 | ❌ (agent approve with comments only) | ⚠️ baseline choices | ✅ | ✅ | ✅ in #7 | ⚠️ | pending | ✅ 19 malformed + negative fixtures fail closed [re-run 25/25] | ✅ | **BLOCKED (G1, G2)** |
| #5 | ❌ (request changes) | ⚠️ EX-01..EX-04 PROPOSED in the register (UA-1) | ✅ | ❌ | ✅ in #7 | ⚠️ conflicts with #1 | pending | ⚠️ the allowlist test misses stack-level suppressions [#14] | ✅ | **BLOCKED (G1, G2, G4)**; B5-2 is fixed in #7 @ `80f01d6` |
| #6 | ❌ (request changes) | ⚠️ | ⚠️ no CI | ❌ | ❌ not integrated | ⚠️ | pending | ✅ | ❌ self-logging, SCP bypass | **BLOCKED** |
| #7 | ❌ | ⚠️ | ✅ CI at `49122f2` | ⚠️ | ✅ (it is the integration; also tested via #26) | ⚠️ | pending | ✅ postgres (per #2) | ❌ carries #5's B5-2 | **BLOCKED** |
| #8–#10, #12, #13, #15–#21 | ❌ | — (`backup-dr-aws` has unadjudicated exceptions) | ⚠️ local re-runs only, no CI (#12 and #13 not checked; #20 has no tests) | ⚠️ | ❌ | ⚠️ | pending | ✅ none known where tests exist; UNVERIFIED elsewhere | ✅ | **BLOCKED (G1)**. `backup-dr-aws` has no PR at all |
| #26 (plus #23–#25) | ❌ | ⚠️ inherits #5 via #7 | ✅ [CI 40749373581] | ⚠️ open gaps in ACCEPTANCE.md | ✅ via its own CI | ⚠️ | pending | ✅ gate self-test and defect control | ❌ carries #5's B5-2 via #7 | **BLOCKED** |
| #22 | ❌ | — | ⚠️ local only, no CI | ✅ | ❌ | ⚠️ | pending | ✅ self-test rejects forged evidence | ✅ | **BLOCKED (G1)** |
| #14, #11 | ❌ | — | — | ✅ | — | ⚠️ | pending | — | — | Docs only, BLOCKED (G1) |

G6 note: `main` is still `7f50348`, and GitHub reports every PR as MERGEABLE. #1 and #5 conflict with each other on `infra/aws-cdk/**` (per [#14 review], via `git merge-tree`). G6 has to be redone after any merge.

## 3. Security exception register: EX-01..EX-04 (#5), reconciled at `1fdf25a`

**Decisions recorded here are only those Ian relayed.** On 2026-10-28 at 21:41 EDT (recovery directive), consistent with the 14:10 EDT relay:
- EX-01: **accepted, pending policy verification**.
- EX-02: **accepted as a limitation**.
- EX-03: **conditional on scope verification**.
- EX-04: **conditional on role review**.

No approval beyond these was given. The register file `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` @ `1fdf25a` still reads "**PROPOSED, pending owner approval**" for every entry. The live gate unblocks an entry only on an exact `EX-NN status: APPROVED` line (`scripts/ci/check_exceptions.py` lines 12–13). This report has **not** written any such line. It would also be wrong to write `APPROVED` for a conditional decision before Ian confirms the condition.

Facts below were checked in the synth templates @ `1fdf25a`:
- `BankItLabSecureStorage.template.json` sha256 `9ba9be1d627acb4b…`
- `BankItLabNetworkDatabase.template.json` sha256 `c3dd0a0ce47e4708…`

Both are listed in the bundle's `SHA256SUMS`, which re-checked 44/44 OK. They are templates only and were never deployed.

| ID | Rule / resource | Ian's decision (relayed) | Register @ `1fdf25a` | Condition | Verification evidence | Reconciled status |
|---|---|---|---|---|---|---|
| EX-01 | NIST.800.53.R5-S3DefaultEncryptionKMS / AccessLogsBucket | Accepted, pending policy verification | PROPOSED | Bucket-policy verification | **Bucket:** `AccessLogsBucket83982689` has SSE-S3 (`AES256`), all 4 Block Public Access flags, versioning Enabled and `BucketOwnerEnforced`.<br>**Policy:** `AccessLogsBucketPolicy7F77476F` denies `s3:*` when `aws:SecureTransport=false`. It allows `s3:PutObject` only to `logging.s3.amazonaws.com` on `/data-bucket/*`, with `aws:SourceArn` = DataBucket and `aws:SourceAccount` = this account.<br>**Product source:** the AWS S3 docs ([server access logging](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html), re-read 21:42 EDT): "The destination bucket must use Amazon S3 managed keys (SSE-S3)" | **CONDITIONALLY ACCEPTED.** The condition evidence is verified by this report. It is **not APPROVED** until Ian confirms the verification and the register is updated |
| EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled / AccessLogsBucket and DataBucket | Accepted as a limitation | PROPOSED | None | Both buckets have versioning Enabled and `DeletionPolicy: Retain`, and no `ReplicationConfiguration`. The register's "Why" still says "not expressible in an env-agnostic, never-deployed lab stack". The 14:10 relay rejected that wording, so a docs fix by the #5 owner is still open | **ACCEPTED (limitation), per Ian.** It is not yet recorded in the register, so the gate still counts it PROPOSED |
| EX-03 | AwsSolutions-IAM5 / RdsMonitoringPolicy | Conditional on scope verification | PROPOSED | Exact wildcard scope | **Policy:** `RdsMonitoringPolicy5DA8ACAC` statement 1 grants `logs:CreateLogGroup` and `PutRetentionPolicy` on `…:<region>:<account>:log-group:RDSOSMetrics`, with no wildcard. Statement 2 grants `CreateLogStream`, `PutLogEvents`, `DescribeLogStreams` and `GetLogEvents` on `…:log-group:RDSOSMetrics:log-stream:*` only.<br>**Role:** `RdsMonitoringRole696C9BB4` trusts `monitoring.rds.amazonaws.com` with `aws:SourceAccount` | **CONDITIONAL.** The scope evidence is verified by this report and matches the register's claim. It is **not APPROVED** until Ian confirms |
| EX-04 | AwsSolutions-IAM4 / BackupPlanPostgresRole (`AWSBackupServiceRolePolicyForBackup`) | Conditional on role review | PROPOSED | Role review | **Trust:** `BackupPlanPostgresRole2A2CEBDF` trusts `backup.amazonaws.com` with **no `aws:SourceAccount` condition** (unchanged at `1fdf25a`, unlike the monitoring role).<br>**Managed policy:** the AWS docs ([AWS Backup service roles](https://docs.aws.amazon.com/aws-backup/latest/devguide/iam-service-roles.html), re-read 21:42 EDT) document `AWSBackupServiceRolePolicyForBackup` as the default backup service-role policy.<br>**Vault:** #14 notes the vault has no access policy or Vault Lock | **CONDITIONAL; the role review finds a gap.** Ian chooses: (a) accept as is, or (b) require the #5 owner to add `aws:SourceAccount` and then re-review |

Separately, **B5-2** (KMS key-admin escalation) is recorded as fixed in `80f01d6`, and #31 confirms it. This report did not audit the new key policy.

## 4a. PR #14 independent review: summary (`reports/review-pr3-pr6.md` @ `eb8d259`)
The reviewer is neither the author nor this automation. The review is local, credential-free and read-only, and it reviewed the exact head SHAs of #3 `fb36341`, #4 `d302c99`, #5 `099479e` and #6 `e5e7f46`. These are review notes, **not a GitHub review or a human sign-off**.

| PR | Verdict | Blocking items |
|---|---|---|
| #3 | **Approve** | none |
| #4 | **Approve with comments** | none. Follow-ups: a CA007 baseline rule, failing rule IDs in the evidence logs, CI |
| #5 | **Request changes** | **B5-1** suppressions were applied while the register said PROPOSED. **B5-2** unconditioned `kms:Create*`/`kms:Put*` for account root on 3 CMKs (CreateGrant/PutKeyPolicy escalation). **B5-3** conflict with #1 on `infra/aws-cdk/**` |
| #6 | **Request changes** | **B6-1** `TrailAccessLogsBucket` logs to itself. **B6-2** any account can create a role with an exempt name and bypass the SCPs. **B6-3** CDK was delivered where the plan asked for Terraform; the deviation is undocumented and the Terraform items are MISSING |

**Checkpoint 2 (`eb8d259`, section dated 14:30 EDT) supersedes checkpoint 1 on the Postgres item:** the harness v2 false-PASS remediation is reviewed and **remediated** (details in §0, item 2). The other review steps remain: the #6 SCP absent-key check, re-reviewing #5 after the EX sign-off and the KMS fix, re-reviewing #6, and reviewing #7 at its exact head.

Checkpoint 1 (14:15 EDT, now superseded on this point) said:
- The #2 CI false PASSes (N01, N04, N05, N06 in `ci-service-40630856041-1`) are VERIFIED. The remediation is marked **"open / no fix commit reviewed"**, even though #2's harness v2 (`e7399fb`) and #7 claim the fix. Until the reviewer reviews `e7399fb`, treat the fix as **unreviewed**.
- Still unconfirmed:
  - the absent-key behaviour of the #6 encryption SCPs
  - the second parliament allowlist entry
  - all live behaviour
  - the Terraform requirement, which is not in the repo
- Remaining review steps:
  - review the #2 fix
  - check the #6 SCP absent-key behaviour
  - re-review #5 after the EX sign-off and the KMS fix
  - re-review #6 after B6-1 and B6-2 are fixed
  - extend the self-log checker to catch A→B→A loops

## 4. Reviews done for earlier updates (2026-10-28 about 14:25 EDT)
- **#10 observability @ `3e40e39`** [re-run]:
  - `python3 -m unittest discover -s observability/tests` ran 64 tests: OK.
  - `generate_evidence.py --verify` on `runs/local-offline-20261028T180832Z`: VERIFY PASS.
  - `sha256sum -c`: 44/44.
  - `SUMMARY.json` records commit `2613ea2`, clean tree, overall PASS.
  - No CI. A code review was **not** done.
- **#8 portfolio @ `6c25c05`** [re-run]:
  - Every one of the 130 distinct GitHub links in `portfolio/*.md` resolves through the GitHub API (HTTP 200) in onnxscibroccoli/{Grasshopper, helix, broccoli-core, civicpatch, omnikali, broccoli-rish}.
  - The links are 45 blob, 18 tree and 5 commit links (all SHA-pinned), plus 42 PRs, 15 repo roots and 5 Actions runs.
  - All 5 cited runs match their stated conclusion (success) and head SHA: Grasshopper 40667390721 @ `4e5525c`, broccoli-core 39352779867 @ `2d3b595`, civicpatch 40713410326 @ `cd94213`, helix 40687102198 @ `8f68703` and omnikali 40691477149 @ `67108f2`.
  - **Not checked:** whether the prose claims match the cited file contents, and whether "latest run" statements are still current.
- **#9 vendor mock** moved to `88a3785` and was re-run there: 45/45 tests, governance lint OK, 2 evidence runs verify.
- **#2** PR body re-read: it is updated and no longer stale.

## 5. CI summary (all times EDT)
- **`bank-aws-001-cdk`** (#1): 4/4 runs succeeded, 00:07–00:16.
- **`postgres-restore-evidence`** (#2):
  - [40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041) and [40630876341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630876341) at `daf8d82`: **failed** (00:10).
  - Runs at `e610015`, `2aac93c` and `e7399fb`: success (00:12, 14:02, 14:03).
- **#7 `overnight/integration`**:
  - At `876f7b7`: 6/6 runs succeeded (14:03).
  - At `0f57289`: 5/5 runs succeeded (14:10).
  - At **`afb41278`** (current head): 4/4 runs succeeded (14:13). The push event triggered only `offline-validation`; the pull_request event ran all three workflows.
- **No CI** on #3, #4, #5, #6, #8, #9, #10, #12–#20 or `backup-dr-aws`. #3, #4 and #5 are covered only through #7.
- The full run list is in `EVIDENCE_MANIFEST.md`.

## 6. Not verified / known gaps
- Nothing was deployed. No live AWS, Entra, Graph or Access Analyzer validation was run, and no compliance certification is claimed.
- The cdk-nag counts and the #6 parliament/SCP lint results are **[PR body]** or **[#14 review]**; they were not recomputed here.
- #12 and #13 are not reviewed. The prose of #8, #10 and #15–#20 was not reviewed.
- The `backup-dr-aws` CDK results are as stated in §1. No real backup or restore has run (NOT_EXECUTED).
- Actions are pinned by tag, not SHA.
- No PR has a human GitHub review.
