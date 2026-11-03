# Independent re-review: PR #7 candidate `1fdf25a`

**Verdict: CHANGES REQUIRED** for candidate `1fdf25ad10c56bb457d6242392f9305c539d1209`. The tested merges are `85063e80c6240fdc417460334408d998141043bd` and `07eea1cefdc15873af2a579d3795af402961edd6`. The base is `7f50348bf1370381615eaed91c02607fe41de2f5` and the gate code is `4e6fef4f5d05a72378f0e4c5ec75154efe821710`.

**B5-1 is *not* the only remaining blocker** (see §8).

- **Reviewer:** an independent review lane, pushing as `onnxscibroccoli`. That is the PR #7 author account, so this note cannot satisfy AC1 and is not a GitHub review.
- **Date:** 2026-10-28 (EDT).
- **Carry-over:** nothing carries over from the `b908a66` review (PR #30).

Labels: **VERIFIED** means I checked it in this session via `gh`, `git`, a code read or a local run/probe. **UNVERIFIED** means I did not reproduce it.

## 0. SHAs (VERIFIED)

| Role | SHA | Evidence |
|---|---|---|
| Candidate | `1fdf25a…` | Equal to `origin/overnight/integration` and PR #7 `headRefOid`. Parent `4e6fef4` |
| Base | `7f50348…` | Equal to `origin/main` and PR #7 `baseRefOid` |
| Main-validation merge | `85063e8…` | Equal to `origin/candidate/main-validation-1fdf25a`. Parents (`7f50348`, `1fdf25a`). `git diff 1fdf25a 85063e8` is empty |
| PR synthetic merge | `07eea1c…` | Equal to `refs/pull/7/merge`. Parents (`7f50348`, `1fdf25a`). `git diff 1fdf25a 07eea1c` is empty |
| Gate code | `4e6fef4…` | Ancestor of the candidate. `git ls-tree` of `scripts/ci` is identical at `4e6fef4` and `1fdf25a` |

- Commits since `b908a66`: `51e404c`, `a29f4d9`, `80f01d6`, `4e6fef4`, `1fdf25a`.
- Packet: `evidence/acceptance` @ `6bcb390`, `coordination/review-requests/PR-7-candidate-1fdf25a.md`. Status: "NOT YET REQUESTED".

## 1. CI on all three SHAs (VERIFIED, `gh run view` + job logs)

| Run | Event | Tested | Jobs | merge-eligibility |
|---|---|---|---|---|
| 40800359209 | push | `1fdf25a` (direct) | 18/19 success; only merge-eligibility failed | AC1 UNMET; AC2 UNMET (UA-1); AC3 UNMET (direct run); AC4 PARTIAL; AC5 UNMET (UA-1) |
| 40800364073 | pull_request | `07eea1c` | 18/19 success; only merge-eligibility failed | AC1 UNMET; AC2 UNMET (UA-1); **AC3 MET_AT_RUNTIME** (base 7f50348); AC4 PARTIAL; AC5 UNMET (UA-1) |
| 40800374574 | push `candidate/main-validation-1fdf25a` | `85063e8` | 18/19 success; only merge-eligibility failed | as 40800364073, with AC3 MET_AT_RUNTIME for 85063e8 |

- The other workflows on `1fdf25a` succeeded: `aws-cdk` and `offline-validation` (push and PR), and `postgres-restore-evidence` (PR). VERIFIED
- The logs show the gate checked out `main` into `.trusted/main`. Because main has no gate scripts, the job fell back to `.trusted/pinned` @ `4e6fef4` ("HEAD is now at 4e6fef4"). VERIFIED
- **Test count is 93, not 87.**
  - The module-registry job log (run 40800364073) shows `Ran 93 tests … OK`.
  - Locally at `1fdf25a`, `scripts/ci/tests` also gives `Ran 93 tests … OK`. Per file: 15 + 7 + 14 + 4 + 7 + 11 + 18 + 11 + 6 = 93.
  - `reports/INTEGRATION.md:29` says 87, so the stated erratum is correct. VERIFIED
- Local `--lint-tasks`: OK. VERIFIED
- I did not re-run `validate-all.sh` (claimed 46/46) or the aws-cdk jest suite (claimed 36/36). Both are UNVERIFIED locally; the CI jobs that run them are green.

## 2. B5-2 (KMS key admin): **FIXED**, with one minor note

VERIFIED by code, the synthesized templates and the tests in the tree:
- `infra/aws-cdk/lib/least-privilege-key.ts:12-32`: `KEY_ADMIN_ACTIONS` is an explicit list. It has no `kms:Create*`, no `kms:Put*`, no `kms:CreateGrant` and no crypto actions.
- `:68-82`: statement `KeyAdministrationByKeyAdminRoleOnly` has the condition `ArnEquals aws:PrincipalArn ∈ {role/BankItLabKmsKeyAdmin, :root}` plus `BoolIfExists kms:BypassPolicyLockoutSafetyCheck = false`.
  - `kms:PutKeyPolicy` (`:20`) is therefore limited to the admin role and the root user, and cannot bypass the lockout check.
  - The key stays manageable through the root break-glass principal.
- The account-principal `kms:CreateGrant` sits in `GrantsForAwsResourcesViaApprovedServicesOnly` (`:95-107`), conditioned on `GrantIsForAWSResource=true`, `CallerAccount` and `ViaService`.
- The committed synth templates match: all 3 CMKs carry the scoped admin statement, and no statement has `Create*`, `Put*` or an unconditioned `CreateGrant`/`PutKeyPolicy`.
- **Guard:** `infra/aws-cdk/lib/guards.ts` adds `KMS_UNCONDITIONED_ADMIN` (CreateGrant, PutKeyPolicy, Create* or Put* without a condition) and `KMS_ADMIN_WILDCARD`.
- **Tests:**
  - Negative control: `infra/aws-cdk/test/negative-controls.test.ts:99-108` expects both rules to fire on the pre-B5-2 statement.
  - Positive assertions: `secure-storage-stack.test.ts:76-91` and `network-database-stack.test.ts:86-90`.
  - The aws-cdk CI jobs are green. I did not run jest locally: UNVERIFIED.
- **Minor note (M1, non-blocking):** "CreateGrant only in the conditioned statement" is not literally true for `DatabaseKey7576F140`.
  - `evidence/aws/aws-remediation-vpc-rds/synth/BankItLabNetworkDatabase.template.json` has a CDK-generated statement with no Sid: `kms:CreateGrant`, `kms:DescribeKey` for account root, conditioned **only** on `kms:ViaService = secretsmanager.<region>`.
  - It has no `GrantIsForAWSResource` and no `CallerAccount`. It comes from the Secrets Manager secret's key grant.
  - It is conditioned, so the guard passes it. Risk is low because it is callable only through Secrets Manager, but the comment at `least-privilege-key.ts:8` over-claims.
  - Document it, or add `GrantIsForAWSResource`.

## 3. F1 (base must be `main`): **FIXED**

VERIFIED: I re-ran my previous probe against the gate copy at `4e6fef4`.
- Setup: a local `--no-ff` merge of `1fdf25a` into the old candidate `08cdf11` (local commit `9ea6060`, not pushed), with `GITHUB_EVENT_NAME=push`, `GITHUB_REF_NAME=candidate/main-validation-1fdf25a` and `TRUSTED_MAIN_SHA=7f50348…`.
- Result: `provenance.py` exits 1 with `valid: false`, "base 08cdf11… is not the current main 7f50348…: candidate was merged into a non-main parent".
- With `TRUSTED_MAIN_SHA` unset: exit 1, "current main SHA not available … base cannot be verified as main".
- Positive control `85063e8`: `valid: true`.
- Code: `provenance.py` makes a moved PR base an error, as is a base ref other than `main`. `merge` kinds require `base_sha == TRUSTED_MAIN_SHA`. The workflow sets that value from the `.trusted/main` checkout.
- Tests: `scripts/ci/tests/test_provenance_base.py` (6 tests).

## 4. F3 / R6 / R1 (AC1 source, trusted gate, forged data)

**AC1 from the reviews API: partly fixed.** VERIFIED (code and probes of `reviews.ac1_from_reviews` at `4e6fef4`)
- `scripts/ci/reviews.py:30-65`. AC1 needs all of these:
  - PR head == candidate
  - the latest decisive review per non-author login is APPROVED with `commit_id == candidate`
  - no non-author CHANGES_REQUESTED on that SHA
  - any fetch error gives UNMET (`:102`)
- An `AC1: MET` in `tasks.json` is rejected (`merge_eligibility.py`; probe: "MET in tasks.json is self-asserted").
- Probes:

| Case | AC1 result |
|---|---|
| Same-account approval | UNMET |
| Author login in a different case (`OnnxSciBroccoli`) | UNMET |
| Approval of another commit (`b908a66`) | UNMET |
| DISMISSED review | UNMET |

- **F4 (new, blocking): any GitHub account's approval counts.** VERIFIED by probe and `gh api`.
  - The repo is **public** (`visibility: public`), and its only collaborator is `onnxscibroccoli`.
  - `fetch()` drops `author_association`, and `ac1_from_reviews` never checks write permission or membership.
  - Probe: an APPROVED review on `1fdf25a` by `random-drive-by-user` gives `MET_AT_RUNTIME`.
  - So any outside GitHub user can satisfy AC1 with one click.
  - *Fix:* require `author_association ∈ {OWNER, MEMBER, COLLABORATOR}`, or a check via `GET /repos/{repo}/collaborators/{login}/permission`. Better still, an explicit allow-list of independent reviewers held outside the candidate (e.g. on `main`).
- **F5 (minor):** a non-author's CHANGES_REQUESTED on an *earlier* commit no longer blocks once the head moves (`:52-53` skips it). GitHub itself keeps such a review blocking until it is dismissed.

**Trusted gate code (R6): improved, still open.** VERIFIED (workflow read and CI logs)
- `integration-gate.yml` (merge-eligibility job, about lines 236–300) runs `provenance.py`, `reviews.py`, `check_exceptions.py` and `merge_eligibility.py` from `$GATE`.
- `$GATE` is `.trusted/main` if main has the gate scripts, otherwise `.trusted/pinned` at `TRUSTED_GATE_SHA` (`:249`), whose checkout is SHA-verified (`:276`).
- The candidate's copy of `scripts/ci` is not executed. **But a candidate can still alter the gate:**
  - **(a)** `TRUSTED_GATE_SHA` and the whole job definition live in the candidate's workflow file. On `push`, and on `pull_request` (the synthetic merge's workflow), the candidate can re-pin to any commit or replace the steps.
  - **(b)** `4e6fef4` is itself a commit by the same integrator on this branch, not code reviewed on `main`.
  - **(c)** The gate still reads all decision *data* from the candidate (`--root`): `tasks.json`, `modules.json` (including `required_gate_jobs` and `denominator_floor`), the exception register and the synth templates.
- The packet documents (a) as a residual that lasts until UA-3 (branch protection or a ruleset). `main` is still `protected: false` with 0 rulesets (VERIFIED this round via `gh api`).

**R1 (forged `tasks.json`) re-run against the `4e6fef4` gate** with `--root` pointing at an out-of-tree copy of the candidate data. VERIFIED by probe.

| Forged data | Reviews | Result |
|---|---|---|
| AC1 MET in tasks.json | author only | NOT ELIGIBLE (AC1 rejected) |
| AC2/AC4/AC5 `MET` with full `met_for` (candidate, base, tested), plus the register line changed to `Status of every entry: **APPROVED**` | `random-drive-by-user` APPROVED | **ELIGIBLE, rc 0** |

- `check_exceptions.py` on the forged register prints "all registered and APPROVED".
- **In CI**, the `tasks.json` part of this forgery is infeasible: `met_for.candidate_sha` and `tested_sha` must name the commit that contains the file, which is a hash fixed point.
- **But F6 follows from that.** VERIFIED by construction and the code at `merge_eligibility.py` `binding_problems`, which is unchanged from b908a66.
  - AC2, AC4 and AC5 can still be satisfied **only** by an in-tree `MET` with such a `met_for`. So they can **never be legitimately MET**, even after Ian approves UA-1. The merge-eligibility gate therefore cannot reach ELIGIBLE on any honest path.
  - F3 was fixed for AC1 only.
  - *Fix:* compute AC2/AC5 at runtime from `check_exceptions` plus an out-of-tree owner record. Treat AC4 as a runtime or out-of-tree attestation too.
- **F7: owner approval (UA-1) is a plain text edit in the candidate tree.** VERIFIED by code (`check_exceptions.py:12-13`, `:23-24`, `:39`).
  - Any committer can write `EX-NN status: APPROVED` and `check_exceptions.py` will accept it. Nothing ties the approval to Ian's identity.
  - The parse is also loose: `PER` matches `EX-01 status: APPROVED` anywhere in a line.
  - *Fix:* bind the approval to an owner GitHub review or signed commit, or to a record on a protected out-of-tree ref.

## 5. N1 (B6-3 Terraform track): **RESTORED**

VERIFIED:
- `coordination/modules.json` `orgs-security` is now `BLOCKED` (was `EXCLUDED`). Its `reason` says: "B6-3: the plan asked for a Terraform track and PR #6 delivers CDK only…", and `blockers: [B6-1, B6-2, B6-3]`.
- `README.md:22` says: "B6-3 (the requested Terraform track is missing; PR #6 is CDK only). Fixing B6-1/B6-2 alone does not admit it."
- Minor inconsistency: in the same entry, `blocker.ids` lists only `B6-1, B6-2`, and `blocker.unblock` says nothing about Terraform.

## 6. B5-3 and B5-1

- **B5-3 (conflict with PR #1): RESOLVED in code, still open outside it.** VERIFIED
  - The new module entry `bank-aws-001` is `SUPERSEDED`, with `superseded_by: aws-cdk`.
  - `tasks.json` AC5 now names B5-3 as resolved in code, with PR #1 open pending UA-4.
  - In code, the access-log bucket does not self-log (`secure-storage-stack.ts:32`, `:50-51`; `infra/aws-cdk/lib` changes only `guards.ts` and `least-privilege-key.ts`).
  - PR #1 is still OPEN.
- **B5-1 (suppressions vs register): still BLOCKING on owner approval UA-1.** VERIFIED
  - The register is unchanged: `SECURITY_EXCEPTIONS.md:3` says "Status of every entry: **PROPOSED, pending owner approval.**"
  - All 3 CI runs log "SECURITY EXCEPTIONS: 5 applied suppression(s), 5 tied to non-APPROVED exceptions -> AC2/AC5 stay UNMET until the owner decides (UA-1)". The gate forces AC2 and AC5 to UNMET.
  - Enforcement now fails closed, with one caveat: an unregistered suppression or a rule mismatch gives ERROR, exit 1 (`check_exceptions.py:66-79`), but approval is self-assertable (F7).

## 7. Module coverage and SIMULATION / PLAN_ONLY

**Coverage: widened, not narrowed.** VERIFIED (`modules.json` diff b908a66→1fdf25a; `check_modules.py` local run)
- **Counts:** 26 modules now, versus 22 at b908a66. None was removed. `coverage.denominator_floor: 26`, enforced by `check_modules.py:60-62`.
- **Added:**
  - `bank-aws-001` (SUPERSEDED, PR #1)
  - 3 functional gaps from the job matrix marked `NOT_STARTED`: `aws-network-edge`, `endpoint-windows-automation`, `inventory-diagrams`
- **Status changes:** only `orgs-security` changed, from EXCLUDED to BLOCKED.
- **Status totals:** INTEGRATED 7, NOT_INTEGRATED 14, NOT_STARTED 3, BLOCKED 1, SUPERSEDED 1.
  - The NOT_INTEGRATED set is the same 14 entries as at b908a66. That is the 13 functional or doc modules plus `acceptance`/`review-notes` as listed before, all still disclosed with a reason.
- **Local result:** `check_modules.py` prints "MODULE COVERAGE: 7/25 integrated (28.0%), functional 7/17; denominator 26 … MODULE REGISTRY OK".
- **Residual:** the floor and the registry are candidate data, so they are editable under R6(c). The rule says that lowering the floor "needs an owner decision recorded in tasks.json", which is self-reported.
- **Minor:** `README.md` still states no coverage ratio.

**SIMULATION / PLAN_ONLY: holds.** VERIFIED
- **Workflows:** `contents: read` everywhere. The merge-eligibility job additionally has `pull-requests: read`. There are no `secrets.*`, no `id-token` and no write permissions.
- **Live-mutation grep:** the only new network code is `scripts/ci/reviews.py`, which makes read-only GET calls to the GitHub API with the workflow token (no `method=` or `data=`). The only other hit is the absence test in `tests/entra/test_ca_validator.py`.
- **Negative tests:** `scripts/ci/m365_checks.sh plan-only-negatives` gives `M365 CHECK OK`.
- **Module code:** nothing under `identity/`, `scenarios/`, `evidence/m365` or `evidence/incident` changed since b908a66.

## 8. Verdict

**CHANGES REQUIRED** for `1fdf25ad10c56bb457d6242392f9305c539d1209`. I checked the tested merges `85063e8` and `07eea1c`, and the gate code `4e6fef4`.

| Item | Status |
|---|---|
| B5-2 | FIXED (minor M1) |
| F1 | FIXED |
| N1 | RESTORED |
| B5-3 | RESOLVED in code (PR #1 still open, UA-4) |
| AC3 runtime | MET_AT_RUNTIME on both merges |
| Test count | 93 (the erratum is correct) |
| B5-1 | OPEN, blocking on UA-1 |
| F4 | AC1 accepts an APPROVED review from **any** GitHub account on this public repo (no permission or association check) |
| F6 | AC2/AC4/AC5 can only be MET in-tree with a self-referential `met_for`, so the gate can never honestly become ELIGIBLE, even after UA-1 |
| R6 | The trusted-gate pin and job definition are still candidate-controlled (until UA-3); the decision data comes from the candidate |
| F7 | UA-1 approval is a text edit in the candidate's register, with no owner provenance |

**B5-1 is not the only remaining blocker:** F4, F6 and the R6 residual are also blocking. F5, M1 and the `blocker.ids` and README coverage nits are non-blocking.
