# Independent re-review: PR #7 candidate `5a75d9c`

**Verdict: CHANGES REQUIRED** for candidate `5a75d9ca742e28d8f0a18b590b1bfecb5f7b2b03`. The tested merges are `38e82679475a607aa8c109f9f368133d5ea0e21c` and `decbb08813e3780d048d98fd7c6a8c596eee2dc0`. Main is `7f50348bf1370381615eaed91c02607fe41de2f5`, and the manifest is `evidence/acceptance` @ `274a3b9bcdace2e8cc1ef6e3c842b9643dcd28ce`.

- **Reviewer:** an independent review lane, pushing as `onnxscibroccoli`. That is the PR #7 author account, so this note is not an AC1 approval, not an attestation and not a GitHub review.
- **Date:** 2026-10-28 (EDT).
- **What I did not do:** post anything to GitHub other than this branch and its draft PR.
- **Carry-over:** nothing carries over from earlier reviews. `e9310f3` is superseded and was not reviewed.

Labels: **VERIFIED** means I checked it in this session via `gh`, `git`, a code read or a local probe. **UNVERIFIED** means I did not reproduce it.

## 0. SHAs (VERIFIED)

| Role | SHA | Evidence |
|---|---|---|
| Candidate | `5a75d9c…` | Equal to `origin/overnight/integration` and PR #7 `headRefOid`. Parent `e9310f3` (superseded) |
| Main | `7f50348…` | Equal to `origin/main` and PR #7 `baseRefOid` |
| Main-validation merge | `38e8267…` | Equal to `origin/candidate/main-validation-5a75d9c`. Parents (`7f50348`, `5a75d9c`). Empty diff vs the candidate |
| PR synthetic merge | `decbb08…` | Equal to `refs/pull/7/merge`. Parents (`7f50348`, `5a75d9c`). Empty diff vs the candidate |
| Trusted manifest | `274a3b9…` | On `evidence/acceptance` (current head `63af215` adds only the packet and run records). `trusted-gate/gate-manifest.json`: `gate_sha = 5a75d9c…` (**the candidate itself**). All 26 listed sha256 values match the candidate tree |

- Commits since `1fdf25a`: `ce69f84`, `e9310f3`, `5a75d9c`.
- Packet: `coordination/review-requests/PR-7-candidate-5a75d9c.md` on `evidence/acceptance`. Status: "NOT YET REQUESTED".
- **Errata:**
  - The packet's known erratum holds: `reports/INTEGRATION.md:10` labels Round 8 "~22:15 EDT", but the runs started at 21:56 EDT.
  - Also stale: the history table in `trusted-gate/README.md` lists only `ce69f84` and not the current `5a75d9c` pin.

## 1. CI on all three SHAs (VERIFIED, `gh run view` + job logs)

| Run | Event | Tested | Jobs | merge-eligibility |
|---|---|---|---|---|
| 40803392582 | push | `5a75d9c` (direct) | 18/19 success; only merge-eligibility failed | AC1/AC2/AC4/AC5 UNMET; AC3 UNMET (direct run) |
| 40803398543 | pull_request | `decbb08` | 18/19 success; only merge-eligibility failed | AC1/AC2/AC4/AC5 UNMET; **AC3 MET_AT_RUNTIME** (base 7f50348) |
| 40803394450 | push `candidate/main-validation-5a75d9c` | `38e8267` | 18/19 success; only merge-eligibility failed | as 40803398543 |

- All three runs log `GATE_SOURCE: manifest evidence/acceptance@274a3b9…`, `HEAD is now at 5a75d9c` (the gate checkout) and `TRUSTED GATE VERIFIED`.
- Permissions are reported as `{"onnxscibroccoli": admin}`.
- `SECURITY EXCEPTIONS: 5 applied … 5 tied to non-APPROVED`.
- The other workflows succeeded: aws-cdk 40803398477, offline-validation 40803398592 and 40803392447, and postgres-restore-evidence 40803398499.
- **Tests: 123, not 93.**
  - CI logs show `Ran 123 tests` in module-registry and offline-validation.
  - Locally at `5a75d9c`: `Ran 123 tests … OK` (15+24+7+14+4+7+11+18+11+6+6).
  - The earlier 93 count is superseded by the added tests.
  - One test, `test_runtime_status_only_for_ac3`, was removed. That is expected now that AC1/AC2/AC4/AC5 are runtime-computed.
- I did not re-run `validate-all` (claimed 46/46): UNVERIFIED.

## 2. F4: AC1 allow-list, Write-permission check, exact-SHA state (code VERIFIED; criterion still UNMET)

**Code read: `scripts/ci/reviews.py:64-108`.**
- The latest decisive review per login is taken (COMMENTED/PENDING are ignored, and DISMISSED supersedes).
- A review counts only if it is APPROVED, its `commit_id` equals the candidate, it is not from the PR author (case-insensitive), it is on `reviewer_allowlist`, and its permission is in `{admin, maintain, write}` via `GET /collaborators/{login}/permission`.
- Any undismissed CHANGES_REQUESTED on any commit blocks.
- `fetch` queries permission only for allow-listed logins.

**Probe:** `ac1_from_reviews` from the gate copy at `5a75d9c`, identity = PR #7.

| Probe | Result |
|---|---|
| Outside account (not allow-listed), APPROVED on the exact SHA | UNMET, VERIFIED |
| Author `onnxscibroccoli`, APPROVED on the exact SHA (also with case variation) | UNMET, VERIFIED |
| Allow-listed writer, APPROVED on the stale commit `e9310f3` | UNMET, VERIFIED |
| Allow-listed writer, APPROVED then DISMISSED | UNMET, VERIFIED |
| Allow-listed account with `read` / `triage` permission | UNMET, VERIFIED |
| Allow-listed writer: CHANGES_REQUESTED on an old commit, plus a later approval on the exact SHA by someone else | UNMET (blocks), VERIFIED |
| Allow-listed writer: approved exact SHA, then a later APPROVED on a stale commit | UNMET (latest wins), VERIFIED |
| Positive control: allow-listed `write`, non-author, APPROVED on the exact SHA | MET_AT_RUNTIME, VERIFIED |

**Live state (VERIFIED):**
- `reviewer_allowlist` in the trusted config is `[]`.
- The repository has one collaborator, `onnxscibroccoli` (admin).
- PR #7 has 0 reviews.

So AC1 cannot be met until the owner adds a second human account with write access, pins it in a re-reviewed trusted config, and that account approves. That is an **owner action**, not a code defect.

## 3. F6: external SHA-bound attestations for AC2/AC4/AC5 (binding VERIFIED; authentication defective)

**Where they live:** plain issue comments on PR #7 (`decision_pr: 7`) that start with `ACCEPTANCE-ATTESTATION v2`. `fetch` reads `GET /issues/7/comments` and `GET /actions/runs/{id}`.

**Who can write them:** any account that can comment on PR #7. The repository is public, so that is any GitHub user. Only comments from `owner_logins` and the allow-list are counted.

**Binding (`reviews.py:117-250`), probed (VERIFIED). Rejected:**
- an outside account
- a wrong `candidate`
- a wrong `main`
- a wrong `tested_merge`
- a `workflow_run` whose `head_sha` is not the candidate
- edited comments (`updated_at != created_at`)
- EXCEPTION decisions from a non-owner reviewer
- APPROVED_WITH_CONDITIONS without a later CONDITIONS_VERIFIED

The latest decision wins, and AC5 requires AC2.

**Minor gap (code):** the `workflow_run` check verifies only `head_sha`. It does not check that the run is `integration-gate` or that it concluded `success`. Tighten this.

**R1 re-run** (`merge_eligibility.py` from the gate copy, all `needs` forced to success):

| Input | Result |
|---|---|
| Real tree, no attestations | NOT ELIGIBLE: AC1/AC2/AC4/AC5 UNMET, AC3 MET_AT_RUNTIME (VERIFIED) |
| **R1 forged tree:** `tasks.json` AC1/AC2/AC4/AC5 = MET with matching `met_for`, and the register text edited to APPROVED, no attestations | **NOT ELIGIBLE**: "MET in tasks.json is self-asserted / in-tree; … must be computed at runtime" (VERIFIED). **R1 closed.** |
| **Self-supply:** real tree plus a full v2 attestation set posted by `onnxscibroccoli` (EX-01..04 APPROVED, AC4 ACCEPT, AC5 ACCEPT, bound to candidate/main/decbb08/run 40803398543) | **AC2 = AC4 = AC5 = MET_AT_RUNTIME** (VERIFIED). Only AC1 remains UNMET. |

**Can the candidate forge or self-supply attestations? Yes, through its author account.**
- `owner_logins = ["onnxscibroccoli"]`, and `attestations()` accepts AC4/AC5 from `is_owner or is_reviewer`.
- `onnxscibroccoli` is also the PR #7 author, the account behind every commit, and the account every agent lane (including this one) uses for `gh`.
- The author check that exists for AC1 is **not** applied to AC4/AC5. So the account that wrote the candidate can supply its own "independent acceptance" (AC5) and "acceptance" (AC4) for it.
- **Code defect D1:** reject AC4/AC5 attestations from the PR author, mirroring AC1. Even then, D2 below still applies.

## 4. F7: owner-authenticated exception decisions (defective; nothing approved)

**How Ian's identity is checked:** `comment.user.login ∈ owner_logins` and `GET /collaborators/{login}/permission ∈ {admin}`. That is all.
- A third party cannot fake this. An outside account or a non-owner reviewer is rejected (VERIFIED).
- **But it is not Ian-specific. Defect D2:** the only owner login is the same GitHub identity that all agents operate with.
  - `tasks.json:397-401` (UA-1) tells "the owner account onnxscibroccoli" to post the decisions.
  - Any agent with the shared `gh` credential can post an EXCEPTION APPROVED comment that the gate will attribute to "Ian". GitHub cannot distinguish Ian from the agents.
  - The probe above shows the effect: AC2 becomes MET.
- **Fix:** this needs an owner action, an identity that agents cannot use. Options:
  - a separate Ian-only GitHub account in `owner_logins`, with the shared account removed;
  - a decision signed with a key the agents do not hold (for example SSH- or GPG-signed with a verified fingerprint pinned in the trusted config);
  - a ruleset-protected path only Ian can write.
- The code part of the fix: once that identity exists, the trusted config and the attestation check must require it. Until then the gate should say "owner identity not separable" rather than present comment authorship as owner authentication.

**Current state (VERIFIED):**
- 0 ACCEPTANCE comments on PR #7.
- `check_exceptions` reports 5 applied suppressions (EX-01..04; EX-02 covers 2 resources), all tied to PROPOSED entries.
- `SECURITY_EXCEPTIONS.md:3` reads "PROPOSED, pending owner approval".
- **EX-04 is UNRESOLVED** (`reports/INTEGRATION.md:23`).
- Nothing is approved.

## 5. R6: trusted manifest (verifier VERIFIED; trust root not independent)

`verify_trusted_gate.py` works as described (code read plus CI logs):
- it checks that the gate checkout equals `gate_sha`;
- it checks every manifest file's sha256 in both the gate and the candidate;
- it rejects extra `scripts/ci` files.

All 26 hashes match `5a75d9c` (VERIFIED).

**Can the candidate change the pin, the job or the manifest? Yes.**
- **Pin:** `gate_sha` is `5a75d9c`, the candidate under review. The "trusted" gate code and `trusted-config.json` are the candidate's own, re-pinned at 21:56 EDT by commit `274a3b9`, authored by `onnxscibroccoli`. No independent review of `5a75d9c` existed when it was pinned; the packet says "NOT YET REQUESTED".
- **Manifest:**
  - `evidence/acceptance` is not protected (`branches/evidence/acceptance` `protected=false`), and there are 0 rulesets.
  - It is writable by the same shared account. A later candidate can widen `reviewer_allowlist` or `owner_logins` and push a matching manifest from the same account.
- **Job:**
  - The merge-eligibility job, its `ref: evidence/acceptance` and the verify step are all defined in the candidate's own `integration-gate.yml`.
  - Its hash is checked, but only by a step the candidate defines. A candidate can delete or re-point that step. The packet (P4) and the `verify_trusted_gate.py` docstring both admit this.
- **Main:** `branches/main` `protected=false` and 0 rulesets, so **UA-3 is still open** (VERIFIED).

**Closure needs owner action:**
- **UA-3:** protect main and require the gate, run from main.
- **The manifest must live on protected `main`:** `.github/acceptance/gate-manifest.json`, which the gate already prefers.
- **The pin must point at a gate commit that has been independently reviewed.**

Until then, "trusted" means only "hash-consistent with what the integrator account last pinned". Treat this as a stated residual, not a closed finding. The `pull_request_target` claim holds: none is used (VERIFIED, grep).

## 6. Regressions and minor fixes (VERIFIED unless marked)

| Item | Status | Evidence |
|---|---|---|
| **B5-1** | **OPEN (correctly still open)** | 5 cdk-nag suppressions are still applied while EX-01..04 are PROPOSED (`check_exceptions`). This is now a gate blocker (AC2 UNMET) rather than a silent pass, and is disclosed at `reports/INTEGRATION.md:69,366`. It closes only with UA-1 owner decisions, so it is not a code defect |
| **B5-2** | FIXED, no regression | No `'kms:Create*'` / `'kms:Put*'` in `least-privilege-key.ts`; 0 hits in the synth templates; the `aws:PrincipalArn` `ArnEquals` condition and `BoolIfExists kms:BypassPolicyLockoutSafetyCheck=false` are still present. The comment at `:8-12` now accurately states that the CDK Secret `CreateGrant` statement is conditioned only on `kms:ViaService` (CreateGrant comment fixed) |
| **F1** | FIXED | `provenance.py` probe: candidate merged into non-main `08cdf11` (local merge `0a7956c`), `TRUSTED_MAIN_SHA=7f50348` gives `valid=False` "base … is not the current main". The real runs show base `7f50348` |
| **N1** | No regression | `scripts/ci` tests pass (123), and the merge-eligibility output distinguishes direct/merge runs (AC3 UNMET on the direct run) |
| **orgs `blocker.ids`** | FIXED | `['B6-1','B6-2','B6-3']`, and `unblock` covers B6-3 (Terraform track) |
| **README integrated ratio** | FIXED | `README.md:51` "7 of 25 modules integrated (28.0%; functional 7/17; denominator 26 …)" matches `check_modules.py`: `7/25 … functional 7/17; denominator 26` |
| **Test count** | 123 (supersedes "93") | See §1 |
| **Module completeness** | OK | 26 modules: INTEGRATED 7, NOT_INTEGRATED 14, NOT_STARTED 3, BLOCKED 1, SUPERSEDED 1. Versus `1fdf25a`, no module was removed or added and no status changed (scripted diff). `check_modules.py`: "MODULE REGISTRY OK: 26 modules, 807 tracked files all claimed" |
| **SIMULATION / PLAN_ONLY** | OK | Grep for deploy/apply/mutating cloud or tenant calls finds only `tests/entra/test_ca_validator.py` (negative-test strings) and `scripts/ci/reviews.py` (read-only GitHub GETs). `m365_checks.sh plan-only-negatives`: OK. Workflow permissions are read-only (`contents/pull-requests/issues/actions: read`); no secrets and no `id-token` |
| `validate-all` 46/46 | UNVERIFIED | Not re-run |

## 7. What blocks `5a75d9c`

### Code / design defects (the candidate must change)

- **D1 (F6):** AC4/AC5 attestations are accepted from the PR author.
  - `attestations()` admits `is_owner`, and the owner login is the author of PR #7.
  - AC5 "independent acceptance" can therefore be self-supplied (probe: AC4 = AC5 = MET_AT_RUNTIME).
  - **Fix:** exclude `pr_author` from AC4/AC5, as AC1 already does. Also require the `workflow_run` to be an `integration-gate` run with conclusion `success`.
- **D2 (F7):** "owner-authenticated" exception decisions are authenticated only by the login `onnxscibroccoli`, the shared account all agents push and comment with.
  - Any agent can post Ian's EX decisions (probe: AC2 MET_AT_RUNTIME).
  - **Fix:** after the owner provides a separable identity (O-5), point the config at it.
  - Until then, the gate and docs must not claim owner authentication. They should report it as "owner identity not separable from agent identity".
- **D3 (R6 / process):** the manifest pins `gate_sha` = the candidate itself, on an unprotected branch the same account can write.
  - The "trusted" gate is not independent of the code it gates.
  - **Fix:** pin only an independently reviewed gate commit. State this residual explicitly in the packet: P4 covers only the job-definition residual, not the self-pin.
- **Errata (non-blocking):**
  - `reports/INTEGRATION.md:10`: the Round 8 time is 21:56 EDT, not ~22:15.
  - The `trusted-gate/README.md` history table is missing the `5a75d9c` re-pin.

### Owner-action-only items (no code change can close these)

- **O-1 / UA-1:** decisions on EX-01..EX-04. **EX-04 is UNRESOLVED.** No exception is approved. This also closes B5-1.
- **O-2 (AC1):** add a second human GitHub account with write access to `reviewer_allowlist` (re-reviewed config + re-pinned manifest), and have it submit an APPROVED review on the exact SHA.
- **O-3 / UA-3:** branch protection or a ruleset on `main` requiring the gate, run from main. Move `gate-manifest.json` onto protected main and protect `evidence/acceptance`. Currently `main`, `evidence/acceptance` and `overnight/integration` are all unprotected, and there are 0 rulesets.
- **O-4 / UA-4:** close or decide PR #1 (carried from the packet; not re-verified here, so UNVERIFIED).
- **O-5:** an Ian-only identity (a separate account or a pinned signing key) so that D2 can be closed.

### Verified working

- **F4:** the AC1 code is correct.
- **R1:** an in-tree forgery is rejected.
- **Attestation binding:** candidate, main, tested merge, run head SHA and edit rejection all work.
- **Fixes:** F1, B5-2, N1 and the minor fixes (blocker.ids B6-3, the CreateGrant comment, README 7/25).
- **Other checks:** module completeness, 123 tests and SIMULATION / PLAN_ONLY.

**Verdict for `5a75d9ca742e28d8f0a18b590b1bfecb5f7b2b03`: CHANGES REQUIRED** (D1, D2, D3). Even with those fixed, the candidate cannot become eligible until O-1 to O-5 are done.

This note is not an approval, attestation or GitHub review. I posted no comments on PR #7 or anywhere else.
