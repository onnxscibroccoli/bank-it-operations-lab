# Review request: PR #7 candidate `2e3041a6f5c3f56dad460e9c431f0f42799beec2` and its tested merges

**Purpose:** independent concurrence on **exactly** this candidate. It contains the repairs for PR #32 (CHANGES REQUIRED on `5a75d9c`: D1, D2, D3 and the nits).

| Role | SHA |
|---|---|
| Candidate (`overnight/integration` head = PR #7 head) | `2e3041a6f5c3f56dad460e9c431f0f42799beec2` |
| Base (`main`, verified at runtime) | `7f50348bf1370381615eaed91c02607fe41de2f5` |
| Tested merge, `candidate/main-validation-2e3041a` (`--no-ff`) | `7fc806e8e2ea0801cd1473feebaf60234c7bd480` |
| Tested merge, PR #7 synthetic `refs/pull/7/merge` | `d8e9f0a9a2ad1d648260e2a22f700272aef70de9` |
| Gate pin (manifest `evidence/acceptance:trusted-gate/gate-manifest.json` @ `25908ea`) | `48660b725dbf51b51a38d71fcd0150de56214496`. This is the gate commit, an ancestor of the candidate, **not the candidate**. `independent_review: null`, so the gate reports **TRUSTED GATE UNVERIFIED** |

Both merges have parents (`7f50348`, `2e3041a`), and their trees are identical to the candidate's (`f3f7fd3`).

> **Nothing transfers.** That covers PR #32 on `5a75d9c`, PR #31 on `1fdf25a`, PR #30 on `b908a66`, and every note on `52e362e`. `52e362e` was pushed and tested, then superseded by `2e3041a`, which only corrects two recorded times; `candidate/main-validation-52e362e` = `3b732a6` is stale. Also every earlier SHA.
>
> A verdict counts only if it names `2e3041a6f5c3f56dad460e9c431f0f42799beec2`. For AC1, it must be an APPROVED GitHub review on PR #7 with that `commit_id`, from an allow-listed, write-permitted account that is not `onnxscibroccoli`.

Offline / SIMULATION only. No cloud or tenant calls, no credentials, no deploys.

## Changes since `5a75d9c` (`git log --oneline 5a75d9c..2e3041a`)

| Commit | What |
|---|---|
| `48660b7` (gate) | **D1:** the PR author never attests: AC4, AC5, EXCEPTION or CONDITIONS_VERIFIED. An unknown author fails closed. `workflow_run` must be an `integration-gate` run (name and path), completed, with head = the candidate or an attested tested merge. All jobs must be green except the fail-closed merge-eligibility job, and final-summary must be green. *(A run's overall conclusion cannot be `success` before acceptance, because merge-eligibility fails by design.)*<br>**D2:** owner decisions are **owner-login-bound, NOT owner-authenticated**. Decisions from the author / shared account are `INSUFFICIENT_INDEPENDENCE` (blocking).<br>**D3:** `verify_trusted_gate.py --check-pin`: the pin must not be the candidate, and must carry an API-verified APPROVED review on `gate_sha` by an allow-listed, write+, non-author account. Otherwise TRUSTED GATE UNVERIFIED, and merge-eligibility `--gate-trust` gives NOT ELIGIBLE. The hash step now prints "GATE HASHES MATCH (hash consistency only)".<br>15 new tests (138 total) |
| `52e362e` (workflow + records) | Pin step; `--gate-trust`; artifact `gate-trust.json`. README, INTEGRATION Round 9 and `tasks.json` are relabelled. **UA-6 (O-5)** is recorded: an owner identity distinct from the shared account. **UA-3** now also protects `evidence/acceptance`. The Round 8 time is corrected to 21:56 EDT |
| `2e3041a` | Records only: the Round 9 / UA-6 times are corrected to 22:10 EDT |

On `evidence/acceptance`, `trusted-gate/README.md` now has history rows for the `5a75d9c` self-pin and for this pin.

## Results (verify)

| Item | Claim |
|---|---|
| Local `validate-all` (PostgreSQL 16.15) | PASS, 46/46 steps, on `7fc806e` |
| integration-gate: PR 40805033256 (`d8e9f0a`), main-validation 40805031022 (`7fc806e`), push 40805027636 | Only merge-eligibility fails (NOT ELIGIBLE). `GATE HASHES MATCH`; `TRUSTED GATE UNVERIFIED` (no independently reviewed pin) |
| aws-cdk 40805033159, offline-validation 40805033183 / 40805027568, postgres-restore-evidence 40805033155 | success |
| `scripts/ci/tests` | 138 OK (local and CI) |
| Decisions (`candidates/2e3041a…/runs/`) | AC3 MET_AT_RUNTIME (both merges).<br>AC1 UNMET: allow-list empty.<br>AC2 UNMET: EX-01..04 PROPOSED, and the owner login = the PR author (insufficient independence).<br>AC4/AC5 UNMET.<br>TRUSTED GATE UNVERIFIED.<br>**NOT ELIGIBLE** |

## Questions

1. **D1:** can any attestation by the PR author (any case, any criterion) count? Can a run that is failed, in progress, from another workflow or path, or on another commit be referenced (`reviews.run_problem`)? Is "green except the fail-closed merge-eligibility job" an acceptable definition of a successful gate run?
2. **D2:** is any remaining text in code, docs or `tasks.json` presenting a login check as owner authentication?
3. **D3:** can the pin become VERIFIED without an independent APPROVED review on `gate_sha`? Can it be the candidate? Does a missing or unknown `--gate-trust` fail closed?
4. **Residual:** the job definition is still in the candidate's workflow, and `evidence/acceptance` is unprotected until UA-3. Is that stated accurately?

## Verdict format

`CONCUR` / `CHANGES REQUIRED` / `COMMENT`; the exact SHAs; the reviewer's identity and the date; numbered findings with file:line.

## Review disposition

**NOT YET REQUESTED.** It has been prepared and not sent; Ian will route it.
