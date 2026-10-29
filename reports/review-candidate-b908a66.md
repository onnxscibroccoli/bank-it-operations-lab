# Independent review: PR #7 candidate `b908a66`

**Verdict: CHANGES REQUIRED** for candidate `b908a669b302ff37f2c2ca79ed828f65e5a9f432`. The tested merges are `c11e0de90270fa5834ebb85c28069d3314a5dbf2` and `659450c853d6e4ff5865ea2c4ad339ce57d4e524`, on base `7f50348bf1370381615eaed91c02607fe41de2f5`.

- **Reviewer:** an independent review lane, pushing as the GitHub account `onnxscibroccoli`. That is the same account that authors PR #7, so **this note cannot satisfy AC1**. It is a findings record, not a GitHub review or approval.
- **Date:** 2026-10-28 (EDT).
- **Carry-over:** no earlier verdict, including my PR #28 note on `08cdf11`, carries over to this SHA.

Labels: **VERIFIED** means I checked it in this session via `gh`, `git`, a code read or a local run. **UNVERIFIED** means I did not reproduce it.

## 0. Identity of every SHA (VERIFIED)

| Role | SHA | Evidence |
|---|---|---|
| Candidate | `b908a669…` | Equal to `origin/overnight/integration`. `gh pr view 7` → `headRefOid` |
| Base | `7f50348b…` | Equal to `origin/main` and to PR #7's `baseRefOid`. It is main's only (root) commit, and an ancestor of the candidate |
| Main-validation merge | `c11e0de9…` | Equal to `origin/candidate/main-validation-b908a66`. Parents (`7f50348`, `b908a66`). `git diff b908a66 c11e0de` is empty |
| PR synthetic merge | `659450c8…` | Equal to `refs/pull/7/merge`. Parents (`7f50348`, `b908a66`). `git diff b908a66 659450c` is empty |
| Review packet | `evidence/acceptance` @ `3f3dddc` | `coordination/review-requests/PR-7-candidate-b908a66.md`; marked "NOT YET REQUESTED" |

- **Commits since `08cdf11`:** one commit, `b908a66`.
- **Files changed since `7fe6d72`:**
  - workflow and gate: `integration-gate.yml`, `merge_eligibility.py`, new `provenance.py`, and 18 new binding tests
  - `validate-all.sh`
  - docs: `README.md`, `infra/aws-cdk/README.md`, new `evidence/entra/BASELINE-CHOICES-PENDING.md`
  - records under `coordination/` and `reports/`
- **No module code changed.** Under `infra/`, the only change is one README line.
- **Nothing weakened:** no test or assertion was removed from `test_gate_required.py`. VERIFIED (diff).

## 1. AC3 runtime provenance

**CI results** (VERIFIED via `gh run view --json jobs` and the merge-eligibility job logs):

| Run | Event | Tested | Jobs | merge-eligibility AC3 |
|---|---|---|---|---|
| 40798139838 | push | `b908a66` (direct) | 18/19 success; only merge-eligibility failed | `UNMET`: "direct run: the candidate was not tested as a merge with main" |
| 40798145700 | pull_request | `659450c` | 18/19 success; only merge-eligibility failed | `MET_AT_RUNTIME`: candidate b908a66 merged into base 7f50348 as 659450c, run 40798145700 attempt 1 |
| 40798160682 | push `candidate/main-validation-b908a66` | `c11e0de` | 18/19 success; only merge-eligibility failed | `MET_AT_RUNTIME`: as 659450c, but for c11e0de and run 40798160682 |

- The other workflows on `b908a66` all succeeded: `aws-cdk`, `offline-validation` and `postgres-restore-evidence` (PR run 40798145411). VERIFIED
- In all three runs, merge-eligibility reports AC1 UNMET, AC2 PARTIAL, AC4 PARTIAL and AC5 UNMET, then exits 1. VERIFIED
- The decision artifacts `acceptance-decision-<tested_sha>` were uploaded, with 90-day retention. VERIFIED (log). I did not download them: UNVERIFIED.
- Local re-run: `scripts/ci/tests` gives 61 tests OK, and `--lint-tasks` is OK. VERIFIED

**Design** (VERIFIED, code read):
- `tasks.json` AC3 is now `COMPUTED_AT_RUNTIME`.
- `merge_eligibility.py:133-144` grants `MET_AT_RUNTIME` only when all of these hold:
  - the identity is valid
  - `kind == "merge"`
  - no required job or output in **this** run failed (`NEEDS_JSON`)
- `provenance.py:57-74` derives the identity from git parents plus the event:
  - PR: tested^2 must equal `pull_request.head.sha`.
  - main-validation: tested^2 must start with the branch suffix (7–40 hex).
  - All SHAs must be 40-hex.
- A direct push cannot satisfy AC3. This fixes the old self-referential AC3 record from `08cdf11`. **Improved.**

**New findings:**
- **F1: the base is never checked to be `main`.** VERIFIED by local probe.
  - For `candidate/main-validation-*` pushes, `base_sha` is just tested^1 (`provenance.py:70`). Nothing compares it with `origin/main` or with the PR base.
  - Probe: I made a `--no-ff` merge of `b908a66` into the **old candidate `08cdf11`** (not main) as local commit `b34537c`. I ran `provenance.py` with `GITHUB_EVENT_NAME=push` and `GITHUB_REF_NAME=candidate/main-validation-b908a66`, then `merge_eligibility.py` with all-success `NEEDS_JSON`.
  - Result: `valid: true`, `AC3: MET_AT_RUNTIME (… merged into base 08cdf11…)`. Nothing was pushed.
  - For PR runs, a moved base sets only `base_moved: true` (`provenance.py:66-67`) and is not treated as a problem.
  - `README.md` says AC3 "holds only for a merge of the candidate with `main`", so the docs do not match the code; this also feeds AC4.
  - None of the 18 binding tests covers a non-main or moved base.
  - *Fix:* require `base_sha` to equal `git rev-parse origin/main` (fetched in the job), or the event's `pull_request.base.sha`. Fail when `base_moved` is set, and add tests for both.
- **F2: AC3's "plus scripts/validate-all.sh" is only partly covered.** CI runs `validate-all.sh --python-only` (`offline-validation.yml:28`). The full 44-step validate-all PASS is a local claim. UNVERIFIED (not re-run by me).

## 2. merge_eligibility.py binding: R1, R2, R5, R6

| ID | Re-check at b908a66 | Status |
|---|---|---|
| **R1** (forged `tasks.json` gives ELIGIBLE) | **Out-of-tree probe:** a copy of `tasks.json` with AC1, AC2, AC4 and AC5 set to `MET`, `evidence: "forged"` and `met_for` = the PR run's real public identity (b908a66 / 7f50348 / 659450c). With all-success `NEEDS_JSON`, `merge_eligibility.py --tasks <copy>` prints **`ELIGIBLE`, rc 0**, and `--lint-tasks` on it prints **OK**. So the fields are still self-asserted: the gate never queries a GitHub review, an owner approval or finding status. **In CI the same forgery is infeasible by construction (see F3).** `met_for.candidate_sha` must equal the SHA of the commit that contains `tasks.json`, and `tested_sha` must equal the merge that contains it. Both are hash fixed points. | **Partly mitigated** (VERIFIED). The real path is R6. |
| **R2** (optional or prefix SHA match) | Probe: an abbreviated `met_for.candidate_sha="b908a66"` → `not a full 40-hex SHA`, NOT ELIGIBLE. A legacy `met_for_sha` → "legacy met_for_sha … a full met_for … is required", NOT ELIGIBLE. A naked MET is rejected (`merge_eligibility.py:46-49`). The only remaining prefix match is the main-validation branch suffix (`provenance.py:73`, ≥7 hex), and parent equality is checked there too. | **CLOSED** (VERIFIED) |
| **R5** (no executable merge gate) | `main`: `protected: false`, 0 rulesets. PR #7 is `MERGEABLE` while merge-eligibility is red. The gate is still advisory. | **OPEN** (VERIFIED, `gh api`) |
| **R6** (candidate grades itself) | merge-eligibility checks out the tested commit, which includes the candidate's `scripts/ci/merge_eligibility.py`, `provenance.py`, `coordination/tasks.json` and `modules.json`. A candidate that edits those files can make its own run ELIGIBLE. | **OPEN** (VERIFIED, read) |

- **F3: as designed, AC1, AC2, AC4 and AC5 can never be legitimately MET.** VERIFIED by construction.
  - The binding needs `met_for.{candidate_sha, tested_sha}` written *inside* the candidate tree. But those SHAs are hashes of that tree, which is the same self-reference that `COMPUTED_AT_RUNTIME` fixed for AC3.
  - So the gate is safe against in-tree forgery but **cannot be satisfied honestly**. The packet's suggestion of "a GitHub PR review … with `commit_id` = b908a66" is never read by the gate.
  - *Fix:* evaluate AC1 at runtime from the GitHub reviews API: an APPROVED review with `commit_id` equal to `candidate_sha`, from a login other than the PR author. Evaluate AC2 and AC5 from an out-of-tree, owner-signed record, for example on `evidence/acceptance` with protected-branch or CODEOWNERS approval. Load the gate code from the base branch (fixes R6).

## 3. AC5 findings at b908a66

- **B5-1** (suppressions applied while the register is unapproved): **OPEN.** VERIFIED
  - `NagSuppressions.addResourceSuppressions` is called at `infra/aws-cdk/lib/secure-storage-stack.ts:56` and `:68`, and at `infra/aws-cdk/lib/network-database-stack.ts:228` and `:242`.
  - `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md:3` still says: "Status of every entry: **PROPOSED, pending owner approval.**"
- **B5-2** (unconditioned root `kms:Create*`/`kms:Put*`, CreateGrant bypass): **OPEN.** VERIFIED
  - `infra/aws-cdk/lib/least-privilege-key.ts:8` has `'kms:Create*'` and `:12` has `'kms:Put*'`. Both are in `KEY_ADMIN_ACTIONS`, granted by `KeyAdministrationByAccountRoot` (`:52-53`) to `AccountRootPrincipal` with no condition.
  - `kms:Create*` includes `kms:CreateGrant`. That makes the conditioned grant statement at `:71-72` (`GrantIsForAWSResource`, `ViaService`) bypassable. `kms:Put*` includes `PutKeyPolicy`.
  - There is no change under `infra/` since `08cdf11` except one README line.
- **B5-3** (conflict with PR #1): **RESOLVED in the tree, OPEN outside it.** VERIFIED
  - `modules.json` aws-cdk has `superseded_prs: [1]`. `infra/aws-cdk/README.md:35` and `README.md:15,20` record PR #1 as superseded by #5 (ADR-0004).
  - In code, the DataBucket logs to the separate `accessLogsBucket` (`secure-storage-stack.ts:50-51`), and the access-log bucket has no self-logging (`:32`).
  - PR #1 is still **OPEN** (`gh pr view 1`: OPEN `e494bcf`), so closing it is user action UA-4.
  - `tasks.json` AC5 `detail` still does not name B5-3 or its disposition.
- **AC5 overall: UNMET** (consistent with `tasks.json`).
- **AC2: PARTIAL.** No owner approval of EX-01..EX-04.
- **AC4: PARTIAL.** It now also has the F1 README/code mismatch and the B6-3 omission (§4).

## 4. Module coverage vs. the portfolio denominator

**Denominator** (VERIFIED):
- `coordination/modules.json`: 22 modules.
- `coordination/tasks.json` `tasks[]`: PRs #1–#6.
- Open PRs #1–#27, from `gh pr list`.
- `docs/JOB_REQUIREMENTS_MATRIX.md` on `job-requirements-matrix` (PR #12): requirement rows A1–A6, B1–B16 and C1+.

**Integrated at b908a66 (6):** integration-infra (#7), shared-evidence-validator (#3), entra-offline (#4), aws-cdk (#5, supersedes #1), postgres-recovery (#2), m365-endpoint (#20), incident-demo (#22). (The integration-infra row is #7 itself, so seven entries in all.)

**Every open PR #1–#27 maps to a registry entry.** VERIFIED
- #23–#26 map to `acceptance` (NOT_INTEGRATED); #14 and #27 to `review-notes`.
- #8–#13, #15–#19 and #21 each have a NOT_INTEGRATED entry. `check_modules.py` requires their paths to be absent.
- My review PRs #28 and #29 are not registered. They are audit records only.

**Silent or under-documented narrowing:**
- **N1: PR #6's Terraform track was dropped without a note.** VERIFIED
  - `modules.json` orgs-security is `EXCLUDED`, and its `reason` cites only B6-1 and B6-2. `README.md:22` likewise says "PR #6 is excluded until findings B6-1 and B6-2 are fixed".
  - B6-3 (CDK delivered instead of the requested Terraform; Terraform coverage MISSING) appears only in a `tasks.json:279` history string. It is absent from `modules.json`, `README.md` and `reports/INTEGRATION.md`.
  - There is no Terraform module or task anywhere in the registry. So fixing B6-1/B6-2 would re-admit #6 with the Terraform requirement silently dropped.
  - *Fix:* add B6-3 to the orgs-security `reason`, and register a "terraform / IaC track" entry as `MISSING`, or as explicitly descoped by Ian.
- **N2: the multi-account / Organizations capability is not delivered at all.** VERIFIED
  - Matrix C3 (multi-account) and A4 (operationalizing an enterprise AWS environment) depend on orgs-security, which is EXCLUDED.
  - The `README.md` "What is integrated" table lists only the 6 integrated modules. The 13 NOT_INTEGRATED modules are referenced only through `modules.json`.
- **N3: most functional job-matrix areas are still NOT_INTEGRATED**, each marked "Not yet reviewed for integration". VERIFIED (registry):

| Module (PR) | Matrix requirement it covers |
|---|---|
| vendor-mock (#9) | B6 vendors / Jack Henry |
| observability (#10) | B5/B10 monitoring |
| patch-hardening (#17) | B12 patching |
| backup-dr-aws (#21) | B15b DR |
| control-mapping (#16) | B9 audit |
| identity-governance (#18) | identity |
| hybrid-operations (#19) | A2/B2 hybrid |
| team-management (#13) | A5/B1/B14 |
| learning-guide (#15) | — |
| portfolio-cases (#8) | — |
| job-requirements-matrix (#12) | — |
| final-report (#11) | — |

  - This is registered, not hidden. But a merge of PR #7 delivers about 6 of 22 modules, and the PR #7 description and packet do not state that coverage ratio.
  - Whether that is acceptable is Ian's AC6 call. UNVERIFIED as a requirement.
- **No module was relabeled or moved out of scope between `08cdf11` and `b908a66`:** `modules.json` is unchanged in that range. VERIFIED (`git diff --name-status 7fe6d72 b908a66` does not list it).

## 5. SIMULATION / PLAN_ONLY

**Holds.** VERIFIED
- All 4 workflows have `permissions: contents: read`, with no `secrets.*` and no `id-token`.
- My grep for deploy, apply, mutating AWS CLI, boto3, HTTP-write, Graph and `*-Mg*` paths finds only `tests/entra/test_ca_validator.py`, which asserts their absence.
- `scripts/ci/m365_checks.sh plan-only-negatives` → `PLAN_ONLY OK … mutationsExecuted=0` / `M365 CHECK OK`.
- Module code under `identity/`, `scenarios/`, `infra/` and `tests/` is unchanged since `08cdf11`, apart from the one-line `infra/aws-cdk/README.md` change. There, I verified the incident demo runs on a `mktemp` cluster only.

## 6. Verdict

**CHANGES REQUIRED** for `b908a669b302ff37f2c2ca79ed828f65e5a9f432`. I checked the tested merges `c11e0de` and `659450c`.

Blocking:
1. B5-1 and B5-2 are still open (§3). AC5 is UNMET.
2. F1: AC3 accepts a merge into any base, not just `main` (`provenance.py:66-74`). The README claims otherwise.
3. F3 / R6: AC1, AC2, AC4 and AC5 cannot be honestly MET through in-tree `met_for`, and the candidate supplies its own gate code. AC1 should come from the GitHub reviews API, run by base-branch code.
4. N1: PR #6's Terraform track (B6-3) has been silently dropped from the registry and README.

Non-blocking:
- R5: `main` is unprotected.
- F2: CI runs only the python subset of validate-all.
- N3: the coverage ratio is unstated.
- AC2 and AC4 are PARTIAL.

What is good: the runtime AC3 binding, full-SHA `met_for`, rejection of naked and legacy MET, 61 tests passing, and SIMULATION/PLAN_ONLY intact.
