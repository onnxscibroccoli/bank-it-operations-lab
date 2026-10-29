# Independent re-review: PR #7 candidate `2e3041a`

**Verdict: CHANGES REQUIRED** for candidate `2e3041a6f5c3f56dad460e9c431f0f42799beec2`.

| Role | SHA |
|---|---|
| main | `7f50348bf1370381615eaed91c02607fe41de2f5` |
| Tested merges | `7fc806e8e2ea0801cd1473feebaf60234c7bd480`, `d8e9f0a9a2ad1d648260e2a22f700272aef70de9` |
| Gate pin | `48660b725dbf51b51a38d71fcd0150de56214496` |
| Manifest | `evidence/acceptance` @ `25908eadd2e5220ee2e813146c6ba4245f3fce73` |

- **Blocking code defect:** one, D3-a (§4).
- **Everything else** either is fixed, needs the owner to act, or is a nit.

**About this review:**
- **Who:** an independent review lane, pushing as `onnxscibroccoli`. That is the PR #7 author and the shared account. So this note is **not** an AC1 approval, **not** an attestation and **not** an independent review of `48660b7` for `independent_review`.
- **When:** 2026-10-28, ~22:30 EDT.
- **Posted:** nothing to GitHub except this branch and its draft PR.
- **Carried over:** nothing from earlier reviews. `52e362e` and its merge `3b732a6` are stale; `52e362e`→`2e3041a` changes only `coordination/tasks.json` and `reports/INTEGRATION.md`, one line each.

**VERIFIED** means I checked it this session with `gh`, `git`, a code read or a local probe. **UNVERIFIED** means I did not.

Probe files:
- `/tmp/c2e/probe.py` (box): `reviews.py` and `verify_trusted_gate.py` from a `git archive` of `48660b7`, with the real run and job JSON for runs 40805033256, 40805031022 and 40805033183.
- `merge_eligibility.py` from the same gate copy was run on the candidate tree, on a forged copy and on a modified-workflow copy.

## 0. SHAs (VERIFIED)

| Role | SHA | Check |
|---|---|---|
| Candidate | `2e3041a…` | = `origin/overnight/integration` = PR #7 head. Parent `52e362e`, grandparent `48660b7` |
| Main | `7f50348…` | = `origin/main` |
| Tested merge (main-validation) | `7fc806e…` | = `origin/candidate/main-validation-2e3041a`. Parents (`7f50348`, `2e3041a`). Empty diff vs the candidate |
| Tested merge (PR synthetic) | `d8e9f0a…` | = `refs/pull/7/merge`. Parents (`7f50348`, `2e3041a`). Empty diff vs the candidate |
| Gate pin | `48660b7…` | `gate_sha` in the manifest @ `25908ea`. It is **not** the candidate. `independent_review: null` |
| Manifest files | 27 | All 27 sha256 values match the candidate tree. The 26 gate-side files also match `48660b7`. **`integration-gate.yml` does not match `48660b7`**: the manifest holds the candidate's workflow (see D3-a) |

- `scripts/ci` and `.github/acceptance` are identical in `48660b7` and `2e3041a`.
- `evidence/acceptance` head is `36b9917`. It adds the packet and run records on top of `25908ea`; nothing is removed.

## 1. CI on all three SHAs (VERIFIED, `gh run view` + `merge-eligibility` job logs)

| Run | Event / ref | Tested | Jobs | merge-eligibility output |
|---|---|---|---|---|
| 40805027636 | push `overnight/integration` | `2e3041a` (direct) | 19 jobs: 18 success, only `merge-eligibility` failed | **NOT ELIGIBLE**. AC1/AC2/AC4/AC5 UNMET; AC3 UNMET (direct run); `TRUSTED GATE: UNVERIFIED` |
| 40805033256 | pull_request | `d8e9f0a` | 18/19, same | **NOT ELIGIBLE**. AC3 MET_AT_RUNTIME (base `7f50348`); AC1/AC2/AC4/AC5 UNMET; `TRUSTED GATE: UNVERIFIED` |
| 40805031022 | push `candidate/main-validation-2e3041a` | `7fc806e` | 18/19, same | as 40805033256 |

What CI prints (all three runs):
- `GATE_SOURCE: manifest evidence/acceptance@25908ea…`, `GATE_SHA: 48660b7…`, `HEAD is now at 48660b7`.
- `GATE HASHES MATCH: … (hash consistency only; trust of the pin is decided by --check-pin, D3)`.
- `UNVERIFIED no independently reviewed gate pin: the manifest records no qualifying review of gate_sha 48660b7…`.
- `TRUSTED GATE UNVERIFIED: merge-eligibility will be NOT ELIGIBLE (fail closed)`.
- On AC2/AC4/AC5: `owner login(s) onnxscibroccoli = the PR author / shared account: owner decisions are owner-login-bound, NOT owner-authenticated, and are insufficient-independence until a separate owner identity exists (O-5 / UA-6)`.

Other checks:
- **Other workflows:** all succeeded: aws-cdk 40805033159, offline-validation 40805033183 and 40805027568, postgres-restore-evidence 40805033155.
- **Tests: 138.**
  - CI: `Ran 138 tests` in module-registry, plan-only-assertions and offline-validation.
  - Local at `2e3041a`: `Ran 138 tests … OK`. Per file 15+24+7+14+4+7+11+18+11+15+6+6; `test_pr32_independence.py` is new (15).
- **`validate-all` 46/46:** UNVERIFIED (not re-run).
- **PR #7:** 0 reviews, 4 issue comments. All four are coordination notes by `onnxscibroccoli`; none carries the `ACCEPTANCE-ATTESTATION v2` header.

## 2. D1: the author is excluded from all attestations; run refs are verified (FIXED, VERIFIED)

### Code (`scripts/ci/reviews.py`)

- **`attestations()` :203-245.**
  - `if not author or login == author` (:230) drops every attestation by the PR author **before** the criterion is examined. That covers AC4, AC5, EXCEPTION and CONDITIONS_VERIFIED.
  - An unknown author fails closed.
  - Exception decisions from the author become `INSUFFICIENT_INDEPENDENCE`, not PROPOSED (:271).
- **`run_problem()` :175-200.** A run counts only if all of these hold:
  - name `integration-gate` and path `.github/workflows/integration-gate.yml`;
  - `head_sha` ∈ {candidate, attested tested merges};
  - `status` is `completed`;
  - conclusion `success`, **or** every job except `merge-eligibility` is `success`, with `final-summary` `success`.
- **`fetch`** now also reads the run's `path`, its `status` and `GET …/runs/{id}/jobs`. All are GET requests; there is no write call.

### Self-attestation re-posted by the author (simulated; shipped trusted config)

| Probe | AC2 | AC4 | AC5 | Exception states |
|---|---|---|---|---|
| **Full set by `onnxscibroccoli`** (EX-01..04 APPROVED + AC4/AC5 ACCEPT, bound to `2e3041a` / `7f50348` / `d8e9f0a 7fc806e` / run 40805033256) | UNMET | UNMET | UNMET | `INSUFFICIENT_INDEPENDENCE` ("ignored: INSUFFICIENT INDEPENDENCE (PR author / shared account)") |
| Same, login case variant `OnnxSciBroccoli` | UNMET | UNMET | UNMET | INSUFFICIENT_INDEPENDENCE |
| Same, with the author also put on `reviewer_allowlist` | UNMET | UNMET | UNMET | INSUFFICIENT_INDEPENDENCE |
| Same, `pr_author` unknown (fetch gap) | UNMET | UNMET | UNMET | INSUFFICIENT_INDEPENDENCE |
| Outside account | UNMET | UNMET | UNMET | PROPOSED |
| Allow-listed writer posts EXCEPTION APPROVED (not an owner) | UNMET | MET_AT_RUNTIME | UNMET (AC2) | PROPOSED |
| Separate owner on EX, AC4/AC5 by the author | MET_AT_RUNTIME | UNMET | UNMET | APPROVED |

**The rejection holds.** `merge_eligibility.py` with the author set gives **NOT ELIGIBLE**, even with gate-trust forced to VERIFIED.

### Run-ref probes

The probe config used a hypothetical separate owner `ian-separate` and an allow-listed writer `indep-rev`, so that only the run varies.

**Accepted:**
- **Positive control:** run 40805033256 (real data: PR run of `2e3041a`, conclusion `failure` with only merge-eligibility failed). AC2, AC4 and AC5 are MET_AT_RUNTIME.
- Run 40805031022, the push run of the tested merge `7fc806e`, while `7fc806e` is attested.

**Rejected** (each makes AC2/AC4/AC5 UNMET):
- run 40805031022 when `7fc806e` is not in `tested_merge`
- run 40805033183, which is `offline-validation`: success, right SHA, wrong workflow
- the right name but path `evil.yml`
- `in_progress`
- one other job failed
- `final-summary` missing
- the job list unavailable
- `head_sha` of another commit
- a run fetch error
- a stale candidate `52e362e`
- another main
- edited comments

### Is "green except merge-eligibility" an acceptable definition?

Acceptable. The evaluating run re-checks hashes, pin trust, provenance and runtime ACs itself. The referenced run is only evidence that the attester looked at a green build.

**Nit (non-blocking):** the run may be on *any* SHA the attester lists in `tested_merge`. The parents of those SHAs are not checked. Consider limiting it to {candidate, this run's tested merge}.

## 3. D2: honestly relabelled as owner-login-bound (FIXED, VERIFIED)

**Code:**
- `reviews.py:18-24` and the comment at :238 say "owner-LOGIN-bound … not owner-authenticated".
- The note at :256-260 is printed in the gate output. CI shows it for AC2, AC4 and AC5 (§1).
- `merge_eligibility.py` now says "login-bound GitHub records, never from the PR author".
- `verify_trusted_gate.py` prints `GATE HASHES MATCH … (hash consistency only …)` instead of "TRUSTED GATE VERIFIED".

**Docs and records:**
- `README.md:40`: "owner-login-bound … (not owner-authenticated: GitHub proves the login, not the person)".
- `reports/INTEGRATION.md:15` (Round 9).
- `tasks.json`: UA-1 now requires "an owner login distinct from the PR author (O-5 / UA-6)".

**UA-6 exists:** `tasks.json:472`, alias O-5, status OPEN. Action: "Create an owner identity that agents cannot use … and put it in owner_logins of the trusted config (re-reviewed and re-pinned)".

**Remaining wording (nit):** `tasks.json:984` is the historical Round 8 record `round8_ian_2150_alignment.P2`. It still says "(GitHub-authenticated author+timestamp)". It is a history entry, but it should get a "superseded by D2: login-bound" note.

`test_pr32_independence.py:97-99` asserts the new wording.

## 4. D3: pin independence (mechanism VERIFIED; **D3-a open**)

### What was fixed (VERIFIED)

**`verify_trusted_gate.py --check-pin`, `pin_trust` :79-111.** The pin is UNVERIFIED in each of these cases:
- `gate_sha` is not 40 hex;
- the candidate SHA is unknown;
- `gate_sha` equals the candidate (self-pin);
- `independent_review` is null;
- the fetched review is not APPROVED;
- the review's `commit_id` is not `gate_sha`;
- the reviewer is that PR's author;
- the reviewer is not on the **gate commit's** `reviewer_allowlist`;
- the reviewer lacks write, maintain or admin permission.

`merge_eligibility.py:204` treats anything but `status == "VERIFIED"` as **NOT ELIGIBLE**. That includes a missing `--gate-trust`. Probes:

| Probe | Result |
|---|---|
| Shipped manifest (`independent_review: null`) | UNVERIFIED: "no independently reviewed gate pin" |
| Self-pin (`gate_sha` = candidate) | UNVERIFIED: "self-pin: gate_sha … is the candidate under evaluation" |
| Review by the shared account/author | UNVERIFIED (author, and not allow-listed) |
| Reviewer not allow-listed (shipped config, allow-list empty) | UNVERIFIED |
| Review on a stale commit / COMMENTED / read-only reviewer | UNVERIFIED |
| Valid review but candidate SHA unknown | UNVERIFIED |
| Positive control: allow-listed write non-author APPROVED on `gate_sha` | VERIFIED |
| `merge_eligibility`: all ACs met (separate owner + allow-listed reviewer), gate-trust UNVERIFIED | **NOT ELIGIBLE** (rc 1) |
| Same, `--gate-trust` omitted | **NOT ELIGIBLE**: "no gate-trust result" |
| Same, gate-trust VERIFIED | ELIGIBLE (rc 0). This positive control shows that only the owner items remain |

### Who reviewed `48660b7`? Nobody (VERIFIED)

- The manifest says `independent_review: null`.
- `GET /commits/48660b7/pulls` lists only PR #7, which has 0 reviews.
- The only collaborator is `onnxscibroccoli` (admin).
- My notes (PR #32, this note) were written on `5a75d9c` and `2e3041a` under the shared account. They are **not** a GitHub review of `48660b7` and **not** independent of the shared account. They must not be recorded as `independent_review`.

### Can the candidate or the shared account still re-pin? Yes, the shared account can

- **The candidate's code cannot.** The manifest is outside the tree, and `verify()` rejects a candidate whose workflow, `scripts/ci` or config differ from the manifest (VERIFIED by probe).
- **The shared account can.**
  - `evidence/acceptance`, `main` and `overnight/integration` are all `protected=false`, and there are 0 rulesets (VERIFIED). So `onnxscibroccoli` can rewrite the manifest at will.
  - As the only admin, it can also change who has write access.
  - A VERIFIED pin needs a second, allow-listed account with write access to approve `gate_sha`. That cannot be produced from the shared account alone, but the allow-list itself comes from the pinned gate commit, which the shared account authors.
  - The closure is UA-3 plus UA-6: owner-only.

### D3-a: the reviewed pin does not cover the workflow that decides (code/design defect, blocking, VERIFIED)

- **The executed workflow is not in the pin.** The workflow that runs the check-pin step, fetches reviews and passes `--gate-trust` is the **candidate's** `integration-gate.yml`. Its hash in the manifest (`25908ea`) equals the candidate's file, **not** the file at `gate_sha` `48660b7`: `gate==manifest False`.
- **`verify()` never checks the workflow against `gate_sha`.** `GATE_SIDE` (:31) covers only `scripts/ci/` and the trusted config.
- **Consequence:** an independent review of `gate_sha` does not review the workflow, and the workflow is what feeds `merge_eligibility` its `--reviews` and `--gate-trust` files.
- **Probe:**
  - I replaced the `--check-pin` call in a copy of the candidate workflow with `echo '{"status":"VERIFIED"}' > gate-trust.json`.
  - With the manifest unchanged, `verify()` correctly rejects it.
  - When **only the manifest's workflow hash** is updated (one commit by the shared account; `gate_sha` and `independent_review` untouched), `verify()` returns no errors.
  - `pin_trust` still says VERIFIED for a valid review on `48660b7`.
  - `merge_eligibility` accepts a hand-written VERIFIED file.
- **So** once a real independent review of `48660b7` is recorded, the shared account can swap the deciding workflow without any new review.
- **Fix (code):** in `--check-pin`, require that `.github/workflows/integration-gate.yml` **at `gate_sha`** hashes to the manifest value, or add it to `GATE_SIDE`. In practice that means pinning a gate commit that contains the exact workflow, for example `52e362e`, whose workflow equals the candidate's and which is not the candidate. Then the independent review covers the deciding workflow too.
- **Residual after the fix:** a later candidate can still drop the job. That only closes with UA-3 and the gate run from protected main, which the docs state correctly.

## 5. Nits

| Nit | Status |
|---|---|
| `INTEGRATION.md` Round 8 time | **FIXED**: `reports/INTEGRATION.md:19` reads "Round 8 (2026-10-28 21:56 EDT)". Round 9 is labelled 22:10 EDT, matching the `52e362e`/`2e3041a` commit times (22:10–22:12 EDT) |
| `trusted-gate/README.md` history | **FIXED, with two new inaccuracies.** Rows for the `5a75d9c` self-pin and the `48660b7` pin were added (`evidence/acceptance` @ `25908ea`/`36b9917`). Errors in that table: (a) the `ce69f84` row is dated "~22:05", but `ce69f84` was committed at 21:44 EDT and pinned by `1901342` at 21:47 EDT, so the rows are out of order; (b) the `48660b7` row calls the gate commit "the candidate's parent". It is the grandparent (`2e3041a` → `52e362e` → `48660b7`); the packet correctly says "ancestor" |
| `tasks.json:984` P2 wording | See §3. Non-blocking |
| `run_problem` allows any attested `tested_merge` SHA | See §2. Non-blocking |

## 6. Regressions (VERIFIED unless marked)

| Item | Status | Evidence |
|---|---|---|
| **F4** (AC1) | No regression | Rejected: outside account, author, author case variant, stale `5a75d9c`, stale `52e362e`, dismissed, read-only allow-listed, CHANGES_REQUESTED on an old commit, and a later stale approval. Positive control (allow-listed writer, exact SHA) gives MET. Shipped allow-list `[]` gives UNMET |
| **R1** (in-tree forgery) | No regression | Forged `tasks.json` (AC1/2/4/5 MET with `met_for`) plus the register edited to APPROVED, even with gate-trust VERIFIED: **NOT ELIGIBLE** ("MET in tasks.json is self-asserted / in-tree") |
| **B5-2** | No regression | No change under `infra`/`evidence` since `5a75d9c`. 0 `'kms:Create*'`/`'kms:Put*'` in code and synth; the `ArnEquals aws:PrincipalArn` and `BoolIfExists` lockout guard are present |
| **F1** | No regression | `provenance.py` (gate copy) on a local merge of the candidate into non-main `5a75d9c` (`1c9638f`) gives `valid=False` "base … is not the current main" |
| **N1** | No regression | Direct push identity is `kind=direct, valid=False`; CI shows AC3 UNMET for the direct run and MET only for the two merges |
| **B5-1** | **Still OPEN (correct)** | `check_exceptions`: 5 applied suppressions (EX-01..04), all non-APPROVED. `SECURITY_EXCEPTIONS.md` is unchanged (PROPOSED). Closes only with UA-1 from a separate owner identity (UA-6) |
| Modules | OK, nothing narrowed | 26 modules: INTEGRATED 7, NOT_INTEGRATED 14, NOT_STARTED 3, BLOCKED 1, SUPERSEDED 1. No module removed, added or changed since `5a75d9c` (`modules.json` unchanged). `check_modules.py`: "7/25 … functional 7/17; denominator 26", "MODULE REGISTRY OK: 26 modules, 808 tracked files". `README.md:51` agrees. orgs `blocker.ids` = B6-1, B6-2, B6-3 |
| SIMULATION / PLAN_ONLY | OK | Grep for deploy/apply/mutating cloud, tenant or HTTP calls: only `tests/entra/test_ca_validator.py` (negative strings) and the GET-only `urllib.request.Request` in `reviews.py`/`verify_trusted_gate.py`. `m365_checks.sh plan-only-negatives`: OK. Workflows have no `: write` permission, no secrets other than `github.token`, no `id-token`, no `pull_request_target` |
| `validate-all` 46/46 | UNVERIFIED | Not re-run |

## 7. What blocks `2e3041a`

### Code defects (the candidate or gate must change)

**D3-a** (blocking): the independently reviewed pin does not bind the deciding workflow.
- The manifest takes `integration-gate.yml`'s hash from the candidate, and `verify()`/`--check-pin` never compare it with the workflow at `gate_sha`.
- Fix:
  - require the workflow at `gate_sha` to match the manifest;
  - re-pin to a non-candidate commit that contains the exact workflow (for example `52e362e`);
  - add a regression test: a manifest with a workflow hash that differs from `gate_sha` gives UNVERIFIED.

**Non-blocking nits:**
- the `trusted-gate/README.md` `ce69f84` time and order, and "parent" → "grandparent/ancestor";
- the `tasks.json:984` P2 "GitHub-authenticated" wording;
- optionally, tighten the `run_problem` tested-merge set.

### Owner-action-only items (no code can close these)

- **UA-6 / O-5:** an owner identity agents cannot use, put in `owner_logins` (re-reviewed and re-pinned). Until then every exception decision is `INSUFFICIENT_INDEPENDENCE`.
- **UA-1:** EX-01..EX-04 decisions from that identity. **EX-04 is UNRESOLVED.** Nothing is approved, which also closes B5-1.
- **AC1 and the D3 pin review:** a second human account with write access on `reviewer_allowlist`. It must (a) APPROVE `gate_sha`, recorded as `independent_review`, and (b) APPROVE PR #7 at the exact candidate SHA and post AC4/AC5.
- **UA-3:** protect `main` **and** `evidence/acceptance` (0 rulesets today), and run the gate from main.
- **UA-4:** PR #1. Carried from earlier packets; not re-verified here (UNVERIFIED).

### Verified working

- **D1:** author exclusion and run verification.
- **D2:** relabelling, plus UA-6 recorded.
- **D3:** self-pin and null review are rejected; a missing gate-trust fails closed.
- **Regressions:** none on F4, R1, B5-2, F1 and N1. B5-1 is correctly still open.
- **Other checks:** 138 tests, CI on all three SHAs, 26 modules, SIMULATION/PLAN_ONLY.

**Verdict for `2e3041a6f5c3f56dad460e9c431f0f42799beec2`: CHANGES REQUIRED (D3-a).** Even with D3-a fixed, the candidate is correctly NOT ELIGIBLE until the owner items above are done. This note is not an approval, attestation, GitHub review or `independent_review`. Nothing was posted on PR #7 or elsewhere.
