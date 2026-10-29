# Independent re-review: PR #7 candidate `a9d0f64`

**Verdict: CONCUR (code only) for candidate `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45`.**

| Role | SHA |
|---|---|
| main | `7f50348bf1370381615eaed91c02607fe41de2f5` |
| Tested merges | `cbbabfe38e2f35cf2b64301b994c906c10a33584`, `172e392b7dee7523d044ef485ed9d46594b3a414` |
| Gate pin | `af49a27d6cef040478edafe8324d83b919ea9ffb` |
| Manifest | `evidence/acceptance` @ `da4f14e7666260171d7433432f066d767253ba8f` |

- **No blocking code defects remain.** Only owner actions block (§7).
- **This is a concurrence on code only.** It is **not** an approval, not an AC1 review, not an attestation, and not an `independent_review` of the pin.
- **The candidate is correctly NOT ELIGIBLE.** It cannot become eligible as it stands: the owner actions require trusted-config changes, so they will produce a new pin and a new candidate SHA, which need a fresh review.

**About this review:**
- **Who:** an independent review lane, pushing as `onnxscibroccoli`, the PR #7 author and shared account.
- **When:** 2026-10-28, ~22:45 EDT.
- **Posted:** nothing to GitHub except this branch and its draft PR.
- **Carried over:** nothing from earlier reviews. `2e3041a`, `52e362e` and earlier are stale.

**VERIFIED** means I checked it this session with `gh`, `git`, a code read or a local probe. **UNVERIFIED** means I did not.

Probe files (box):
- `/tmp/ca9/pin_probe.py` and `/tmp/ca9/probe.py`.
- The gate code is a git worktree at `af49a27`.
- Scratch commits live only in the local clone `/tmp/ca9/scr` and were never pushed:

| Scratch commit | What it is |
|---|---|
| `226ee22` | Evil workflow |
| `b3c7b41` | Positive-control pin (allow-list `[indep-rev]`) |
| `bf5ce79` | Its child candidate |
| `e198b76` | Pin without the workflow |
| `20fe0af` | Fake merge |

## 0. SHAs and the pin (VERIFIED)

| Role | SHA | Check |
|---|---|---|
| Candidate | `a9d0f64…` | = `origin/overnight/integration` = PR #7 head. **Parent = `af49a27`** (the pin) |
| Main | `7f50348…` | = `origin/main` |
| Tested merge (main-validation) | `cbbabfe…` | = `origin/candidate/main-validation-a9d0f64`. Parents (`7f50348`, `a9d0f64`) locally and via `GET /commits`. Empty diff vs the candidate |
| Tested merge (PR synthetic) | `172e392…` | = `refs/pull/7/merge`. Same parents. Empty diff |
| Manifest | `da4f14e` | Schema v2, `gate_sha = af49a27…`, `hash_source: git show af49a27:<path>`, `independent_review: null`. 28 files; **all 28 sha256 equal both `git show af49a27:<path>` and `git show a9d0f64:<path>`** |

**The pin is byte-identical to the candidate for all gate objects (VERIFIED):**
- `scripts/ci` tree: `a87084f` in both.
- `.github` tree: `7512de0` in both.
- `git diff af49a27 a9d0f64` touches only `coordination/tasks.json` and `reports/INTEGRATION.md`.

**Parent-of-candidate under the "never the candidate" rule: OK.**
- `pin_trust` rejects `gate_sha == candidate`. In my probe, a manifest naming `a9d0f64` itself gave UNVERIFIED with "self-pin".
- The parent is a distinct, immutable commit. The real control is the required independent APPROVED review **on `af49a27`**: it reviews exactly the gate bytes the candidate runs.
- Because the bytes are identical, "not the candidate" is a formality here. That is acceptable, because the trust comes from the review, not from the SHA being different.

**Claim "52e362e predates D3-a": TRUE (VERIFIED).**
- `52e362e:scripts/ci` = tree `23e4618`, identical to `48660b7` (the pre-D3-a gate).
- Its workflow blob is `a8a5168`; the pin's is `9723b38`.
- So pinning `52e362e` would fail the executing-file check against `a9d0f64`, as `tasks.json:1043` and `INTEGRATION.md:15` say.

`evidence/acceptance` head is `7f047e8`. It adds only the packet and run records on top of `da4f14e`.

## 1. CI on all three SHAs (VERIFIED, `gh run view` + `merge-eligibility` job logs)

| Run | Event / ref | Tested | Jobs | merge-eligibility |
|---|---|---|---|---|
| 40806583044 | push `overnight/integration` | `a9d0f64` (direct) | 19 jobs: 18 success, only `merge-eligibility` failed | **NOT ELIGIBLE**. AC1/AC2/AC4/AC5 UNMET; AC3 UNMET (direct) |
| 40806586164 | pull_request | `172e392` | 18/19, same | **NOT ELIGIBLE**. AC3 MET_AT_RUNTIME (base `7f50348`) |
| 40806583574 | push `candidate/main-validation-a9d0f64` | `cbbabfe` | 18/19, same | **NOT ELIGIBLE**. AC3 MET_AT_RUNTIME |

What CI prints:
- `GATE_SHA: af49a27…`, `GATE_SOURCE: manifest evidence/acceptance@da4f14e…`, `HEAD is now at af49a27`.
- `TRUSTED GATE: UNVERIFIED`, whose **only** reason is `no independently reviewed gate pin: the manifest records no qualifying review of gate_sha af49a27…`.
- So in CI the pinned blobs, the manifest, the running `scripts/ci`, the config and the workflow at `GITHUB_WORKFLOW_SHA` all matched. Otherwise the binding reasons would have been printed, as they are in the probes below.
- The AC2/AC4/AC5 notes keep the owner-login-bound / UA-6 wording.

Other checks:
- **Other workflows:** all succeeded: aws-cdk 40806586095, offline-validation 40806586447 and 40806582288, postgres-restore-evidence 40806586124.
- **Tests: 152 (claim TRUE).**
  - CI: `Ran 152 tests` in module-registry, plan-only-assertions and offline-validation.
  - Local at `a9d0f64`: `Ran 152 tests … OK`. Per file 15+24+7+14+4+7+11+18+11+15+14+6+6; `test_pr33_pin_binding` is new (14).
- **`validate-all` 46/46:** UNVERIFIED (not re-run).
- **PR #7:** 0 reviews, 0 `ACCEPTANCE-ATTESTATION` comments (4 coordination comments total). `GET /commits/af49a27/pulls` lists only PR #7.

## 2. D3-a: the pin binds the deciding workflow (FIXED, VERIFIED)

### Code

- **`verify_trusted_gate.pin_binding` :165-211.** For every manifest file, the **expected** hash is `sha256(git show <gate_sha>:path)`, computed at runtime (`git_blob` :148). It must equal:
  1. the manifest value;
  2. the **executing** copy:
     - the running `scripts/ci` modules, with no extra file;
     - the `--config` actually read;
     - `integration-gate.yml` at **`GITHUB_WORKFLOW_SHA`**, read with `git show` from the workspace repo.
- **Other checks in `pin_binding`:** the gate checkout HEAD must equal `gate_sha`. A missing or non-40-hex `GITHUB_WORKFLOW_SHA`, or an unreadable workflow at it, makes the result UNVERIFIED.
- **`gate_trust_at_runtime` :213** combines the binding with `pin_trust`: no self-pin, plus an API-verified independent review.
- **`merge_eligibility.compute_gate_trust` :105**, called at :223, recomputes trust **inside the gate code**. `--gate-trust` files are ignored, with a notice (:225).
- **`build()` :45** now builds a manifest from git objects of the pin.
- **Workflow:** it sparse-checks-out `.github/workflows` in the gate (:295), and passes `--manifest/--gate-repo/--workflow-repo` (:339). Reading `GITHUB_TOKEN` is read-only.

### Probes (`gate_trust_at_runtime` from `af49a27`, real manifest `da4f14e`)

| Probe | Result | Reasons (besides "no independently reviewed gate pin") |
|---|---|---|
| Baseline: workflow at PR merge `172e392` / at candidate `a9d0f64` | UNVERIFIED | none (binding OK) |
| **Swap the workflow only** (executing workflow = evil `226ee22`, which writes `{"status":"VERIFIED"}`) | UNVERIFIED | "the EXECUTING workflow (at 226ee22…) differs from the pinned commit" |
| **Swap the workflow and the manifest** (manifest workflow hash = evil hash) | UNVERIFIED | "manifest hash differs from the file at the pinned commit (manifest not derived from the pin)" + executing-workflow mismatch |
| Same, plus a recorded `independent_review` | UNVERIFIED | both binding errors remain |
| **Swap the gate scripts** (executing `reviews.py` modified) | UNVERIFIED | "scripts/ci/reviews.py: the executing copy differs from the pinned commit" |
| Extra file in executing `scripts/ci` (`sitecustomize.py`) | UNVERIFIED | "executing scripts/ci has files not in the pinned manifest" |
| Swap the config (allow-list `[sock]`) | UNVERIFIED | "the trusted config being read differs from the pinned commit" |
| **Pin without the workflow** (`e198b76`, checkout at it) | UNVERIFIED | "integration-gate.yml: not present at pinned commit" |
| Gate checkout ≠ `gate_sha` | UNVERIFIED | "gate checkout HEAD … is not the pinned gate_sha" |
| **`GITHUB_WORKFLOW_SHA` mismatch** (older `2e3041a`) | UNVERIFIED | "the EXECUTING workflow (at 2e3041a…) differs" |
| `GITHUB_WORKFLOW_SHA` not in the repo (`000…`) | UNVERIFIED | "… not readable" |
| **`GITHUB_WORKFLOW_SHA` missing** / abbreviated | UNVERIFIED | "executing workflow commit unknown … cannot bind the deciding workflow" |
| Self-pin (`gate_sha` = `a9d0f64`) | UNVERIFIED | "self-pin" + checkout mismatch |
| **Positive control** (scratch pin `b3c7b41` with allow-list `[indep-rev]`, manifest from `build()`, workflow at child `bf5ce79`, valid review) | **VERIFIED** | none |
| Same pin, executing workflow = evil `226ee22` | UNVERIFIED | executing-workflow mismatch |
| Same pin, review by `onnxscibroccoli` / no token | UNVERIFIED | author / not allow-listed / not fetched |

### `merge_eligibility.py` CLI (gate copy, `GITHUB_WORKFLOW_SHA=172e392`)

| Run | Result |
|---|---|
| Real tree | NOT ELIGIBLE. `TRUSTED GATE: UNVERIFIED`, only for "no independently reviewed gate pin" |
| **Forged `--gate-trust` VERIFIED file** with the R1 forged tree, with the author self-set, or with full positive attestation data (separate owner) | All NOT ELIGIBLE. The file is "ignored: gate trust is recomputed by the gate code"; with no `--manifest/--gate-repo` the reason is "no trusted manifest / gate checkout / trusted config given" |

### Residual: owner-only, stated accurately

- **The workflow can still be malicious.** The gate code is still *invoked* by the workflow in the candidate, so a malicious workflow could skip the gate.
- **An inline env override is the same residual.** `GITHUB_WORKFLOW_SHA` cannot be overridden through `env:` or `GITHUB_ENV` (GitHub docs). An inline `GITHUB_WORKFLOW_SHA=<pin> python3 …` inside a step can, though: probe "evil workflow spoofs SHA = pin" passes the binding.
- **Who stops it:** only **UA-3** (branch protection or a ruleset requiring the gate run from protected main). Packet Q3 and `verify_trusted_gate.py` state this.
- **Within that boundary**, every input the honest gate reads is now bound to the reviewed pin.

## 3. Tested-merge parent checks (FIXED; one non-blocking residual)

**Code.** `reviews.py:229` requires every attested `tested_merge` to have parents **exactly** `[main, candidate]`. The parents come from `GET /commits/{sha}` (fetched in `fetch`, at most 4 per comment), or the entry must be this run's own validated merge identity. The API confirms that `cbbabfe` and `172e392` have parents (`7f50348`, `a9d0f64`).

**Probes** (separate-owner config):

| Extra attested `tested_merge` entry | Result |
|---|---|
| A fake SHA with no parent data | all UNMET |
| Parents (main, other) | all UNMET |
| Parents (candidate, main), reversed | all UNMET |
| Three parents | all UNMET |
| Commit fetch error | all UNMET |

**Residual (non-blocking nit):**
- A **fake merge** (`20fe0af`) is still accepted. It has the right parents (`7f50348`, `a9d0f64`) but an **altered tree** (an extra README line). A green-looking `integration-gate` run on it can be referenced as the `workflow_run`: AC4 is MET in the probe.
- Only an authorized, non-author attester could post such an attestation, and the evaluating run still tests its own validated merge. So this does not let the candidate or the shared account self-supply anything.
- Optional hardening: compare the tree with `git merge-tree` of (main, candidate), or limit `workflow_run.head_sha` to {candidate, this run's tested merge}.

## 4. Nits

| Nit | Status |
|---|---|
| `tasks.json` P2 wording | **FIXED.** `tasks.json:984` now reads "owner-login-bound / reviewer-login-bound: GitHub vouches for the login and timestamp, not the person; PR #32 D2". No remaining positive claim of "owner-authenticated" or "GitHub-authenticated" in code, docs or records (grep; only negations and test assertions remain) |
| trusted-gate README times | **FIXED** (`evidence/acceptance` @ `da4f14e`/`7f047e8`). The `ce69f84` row reads "21:47 (commit 21:44)", matching the git times (21:44:11 and 21:47:48 EDT). The new `af49a27` row is 22:28, matching commit 22:28:11 EDT |
| "Grandparent" | **FIXED.** The `48660b7` row now says "the candidate's grandparent (`2e3041a` → `52e362e` → `48660b7`)" |
| `INTEGRATION.md` Round 8 time | Still correct (21:56 EDT) |
| New wording nit (non-blocking) | `verify_trusted_gate.py:274` still prints "trust of the pin is decided by --check-pin, D3". Since PR #33 it is decided by `merge_eligibility` recomputing it; the `--check-pin` output now says "informational". Reword |
| Fake-merge tree | See §3. Non-blocking |
| New time-label nit (non-blocking) | `reports/INTEGRATION.md:46` labels "Round 7 (2026-10-28 ~22:00 EDT)", but Round 7's commits `ce69f84`/`e9310f3` were made at 21:44 and 21:47 EDT, before Round 8 (21:56). It should read ~21:44–21:47 EDT |

## 5. Regressions (VERIFIED unless marked)

| Item | Status | Evidence |
|---|---|---|
| **D1** | No regression | Author full self-set (also case variant, author allow-listed, author unknown): AC2/AC4/AC5 UNMET and `INSUFFICIENT_INDEPENDENCE`. Run-ref probes reject the wrong workflow or path, in_progress, a failed other job, final-summary missing, jobs unavailable, another `head_sha`, a fetch error, an unattested tested merge, a stale candidate, another main, and edited comments. Positive controls (real runs 40806586164 and 40806583574) give MET |
| **D2** | No regression | Gate output (CI) and docs say owner-login-bound. UA-6 OPEN |
| **D3** | No regression | Self-pin, null review, author review, not allow-listed, stale or COMMENTED review, read-only reviewer and unknown candidate all give UNVERIFIED (§2) |
| **F4** | No regression | Rejected: outside account, author, author case variant, stale `5a75d9c`/`52e362e`, dismissed, read-only allow-listed, CHANGES_REQUESTED on an old commit, later stale approval. Allow-listed write on the exact SHA gives MET; shipped `[]` gives UNMET |
| **R1** | No regression | Forged `tasks.json` plus register edited to APPROVED plus forged VERIFIED trust file: NOT ELIGIBLE ("self-asserted / in-tree") |
| **B5-2** | No regression | No changes to `infra`, `evidence` or `modules.json` since `2e3041a`. 0 `kms:Create*`/`Put*` in code and synth; lockout guards present |
| **F1** | No regression | `provenance.py` (pin) on a local merge into non-main `2e3041a` (`9d75e19`) gives `valid=False` "not the current main" |
| **N1** | No regression | Direct identity `kind=direct, valid=False`; CI AC3 UNMET on the direct run only |
| **B5-1** | **Still OPEN (correct)** | `check_exceptions`: 5 applied suppressions, all non-APPROVED; register line 3 "PROPOSED, pending owner approval" |
| Modules | OK, nothing narrowed | 26 modules: INTEGRATED 7, NOT_INTEGRATED 14, NOT_STARTED 3, BLOCKED 1, SUPERSEDED 1. `modules.json` unchanged. `check_modules.py`: "7/25 … denominator 26", "26 modules, 809 tracked files". `README.md:51` agrees. orgs `blocker.ids` = B6-1..3 |
| SIMULATION / PLAN_ONLY | OK | Grep for deploy/apply/mutating cloud, tenant or HTTP calls: only negative test strings and GET-only `urllib.request.Request` (`reviews.py:317`, `verify_trusted_gate.py:127`). `m365_checks.sh plan-only-negatives`: OK. No `: write` permissions, `id-token` or `pull_request_target` in workflows |
| `validate-all` 46/46 | UNVERIFIED | Not re-run |

## 6. Repository state (VERIFIED)

- `main`, `evidence/acceptance` and `overnight/integration` are all `protected=false`, and there are 0 rulesets.
- The only collaborator is `onnxscibroccoli` (admin).
- PR #7 has 0 reviews and 0 attestations. `independent_review` for `af49a27` is null; no one has reviewed it.
- My notes are under the shared account and are **not** that review.

## 7. What blocks `a9d0f64`

### Code defects

**None blocking.** Non-blocking nits:
- `verify_trusted_gate.py:274` wording.
- The `INTEGRATION.md:46` Round 7 time label.
- Optional fake-merge tree hardening (§3).

### Owner-action-only items (these alone block)

- **UA-6 / O-5:** an owner identity that agents cannot use, in `owner_logins`. Until then every exception decision is `INSUFFICIENT_INDEPENDENCE`.
- **UA-1:** EX-01..EX-04 decisions from that identity. **EX-04 is UNRESOLVED.** Nothing is approved; this also closes B5-1.
- **AC1 and the D3 pin review:** a second human account with write access on `reviewer_allowlist`. It must:
  - (a) APPROVE the pin commit, recorded as `independent_review {pr, review_id}`;
  - (b) APPROVE PR #7 at the exact candidate SHA;
  - (c) post AC4/AC5.
- **UA-3:** protect `main` and `evidence/acceptance` (0 rulesets today), and require the gate run from main. This closes the malicious-workflow and inline-env residual (§2).
- **UA-4:** PR #1. Carried from earlier packets; not re-verified (UNVERIFIED).

**Re-review will be needed.** UA-6 and the AC1 allow-list change `trusted-config.json`, which is a pinned gate file. So they require a **new pin commit, a new candidate SHA and a fresh review**. This concurrence binds only `a9d0f64` and does not transfer.

**Verdict for `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45`: CONCUR — code only.**
- No code defects remain; only owner actions block.
- This is not an approval, AC1 review, attestation or `independent_review`.
- The gate correctly reports NOT ELIGIBLE.
- Nothing was posted on PR #7 or elsewhere.
