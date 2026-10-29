# Review request: PR #7 candidate `1fdf25ad10c56bb457d6242392f9305c539d1209` and its tested merges

**Purpose:** independent concurrence on **exactly** this candidate and its tested merges with `main`:

| Role | SHA |
|---|---|
| Candidate (`overnight/integration` head = PR #7 head) | `1fdf25ad10c56bb457d6242392f9305c539d1209` |
| Base (`main`, verified at runtime by the gate) | `7f50348bf1370381615eaed91c02607fe41de2f5` |
| Tested merge, `candidate/main-validation-1fdf25a` (`--no-ff`) | `85063e80c6240fdc417460334408d998141043bd` |
| Tested merge, GitHub PR #7 synthetic `refs/pull/7/merge` | `07eea1cefdc15873af2a579d3795af402961edd6` |
| Gate code actually executed by merge-eligibility (pinned) | `4e6fef4f5d05a72378f0e4c5ec75154efe821710` (`scripts/ci` identical in the candidate) |

Both merges have parents (`7f50348`, `1fdf25a`), and their trees are identical to the candidate's.

> **Earlier reviews and approvals do not transfer.** That includes PR #30's CHANGES REQUIRED on `b908a66`, every note on `b908a66`, `a29f4d9`, `08cdf11`/`771045e`, `7fe6d72`, `5f159f1`, `02ac2de`, `82ab7e6` and `eb42b23`, and PRs #14, #27, #28 and #29.
>
> A verdict counts only if it names `1fdf25ad10c56bb457d6242392f9305c539d1209`.
>
> **For AC1 specifically,** the gate counts only a GitHub review on PR #7 that is APPROVED, has `commit_id` = `1fdf25ad…`, and comes from an account other than the PR author `onnxscibroccoli`. A findings note pushed by `onnxscibroccoli`, like PRs #28–#30, cannot satisfy AC1.

Everything here is offline, synthetic and SIMULATION. There are no cloud or tenant calls, no credentials and no deploys.

## What changed since `b908a66` (verify: `git log --oneline b908a66..1fdf25a`; `git diff --stat b908a66 1fdf25a`)

| Commit | What |
|---|---|
| `51e404c` | Ian's module-coverage patch: `modules.json` lists 26 modules with `denominator_floor` 26, `orgs-security` is BLOCKED, `check_modules.py`/`user_actions.py` fail closed on coverage, and 11 new tests |
| `a29f4d9` | `scripts/ci/tests` now runs in validate-all and in the module-registry job (it previously ran nowhere in CI); `--coverage-json` argument check |
| `80f01d6` | **B5-2:** KMS key admin is scoped to role `BankItLabKmsKeyAdmin` or the root user via `aws:PrincipalArn`. No `Create*`/`Put*`, no `CreateGrant`, and `PutKeyPolicy` is lockout-safe. New guard and negative control. Evidence pass 4; the pass-3 outputs are kept unmodified in `superseded/` |
| `4e6fef4` | **F1:** base must equal the current `main` (moved or non-main base is INVALID).<br>**F3/R6:** AC1 comes from the reviews API (`reviews.py`), and AC1 MET in-tree is rejected. `--root` lets the data be evaluated while the code runs from a trusted copy.<br>**B5-1:** `check_exceptions.py` makes applied suppressions tied to non-APPROVED exceptions a blocking user action that keeps AC2/AC5 UNMET.<br>21 new tests |
| `1fdf25a` | The merge-eligibility job runs the trusted gate (main, else pinned `4e6fef4`), with `pull-requests: read` for the read-only `GITHUB_TOKEN`. Records: N1 (B6-3 restored in the orgs BLOCKED reason and README), B5-3 resolved in code (PR #1 open pending UA-4), AC1 COMPUTED_AT_RUNTIME |

## Claimed results (verify)

| Item | Claim |
|---|---|
| Local `validate-all` (PostgreSQL 16.15) | PASS, 46/46 steps, on `1fdf25a` and on `85063e8` |
| integration-gate on `85063e8` (run 40800374574), `07eea1c` (run 40800364073), and the `1fdf25a` push (run 40800359209) | Each run: 18 of 19 jobs succeed; only merge-eligibility fails, by design |
| `scripts/ci/tests` in CI | 93 tests OK (module-registry job). *Erratum:* `reports/INTEGRATION.md` round 6 says "87 tests in total"; the correct figure is 93 (72 + 6 + 15) |
| aws-cdk | jest 36/36, 0 unsuppressed Non-Compliant, synth drift none |
| Fresh SIMULATION incident run | All six PASS on apt PostgreSQL 18.6 |
| Decision artifacts (on `evidence/acceptance` under `candidates/1fdf25a…/runs/`) | AC3 `MET_AT_RUNTIME` for both merges, with base = `main` at runtime `7f50348`.<br>AC1 UNMET: no non-author APPROVED review.<br>AC2/AC5 UNMET: UA-1 blocking, 5 applied suppressions on PROPOSED EX-01..04.<br>AC4 PARTIAL. **NOT ELIGIBLE** |

## Questions

1. **F1:** can a merge into anything other than the current `main` still produce a valid merge identity? Check `provenance.py` and `tests/test_provenance_base.py`.
2. **F3/R6:** is `reviews.ac1_from_reviews` correct? Consider same-account reviews, case variants, approval of another commit, dismissed reviews, a later CHANGES_REQUESTED, a moved head, and fetch failure.
3. **R6:** is running the gate from pinned `4e6fef4` (or `main`) with `--root` data enough? The residual: on `pull_request` the workflow file comes from the candidate, so the pin is editable until UA-3 (branch protection or ruleset). Is that an acceptable documented limit?
4. **B5-1:** does `check_exceptions.py` fail closed? It should error on an unregistered or mismatched suppression and block on any non-APPROVED entry, and it must not approve anything.
5. **B5-2:** is the new key policy least-privilege and still manageable? Is the root-user break-glass and `BoolIfExists` lockout condition correct? Is anything left that allows `CreateGrant` or `PutKeyPolicy` unconditioned?
6. **N1 / coverage:** is B6-3 now visible? Is the 26-module denominator honest?
7. Has any check been removed or weakened relative to `b908a66`? (The `test_merge_eligibility_binding` harness now supplies runtime AC1 reviews and a clean exceptions fixture. One evidence-empty test moved from AC1 to AC2, because AC1 MET is now rejected outright.)

## Verdict format

Reply with:
- `CONCUR` / `CHANGES REQUIRED` / `COMMENT`
- the exact SHAs `1fdf25ad10c56bb457d6242392f9305c539d1209` and the tested merge(s) you checked
- the reviewer's identity and the date
- numbered findings with file and line

For AC1, the review must be a GitHub PR review on PR #7, `commit_id` = `1fdf25ad…`, from an account other than `onnxscibroccoli`.

## Review disposition

**NOT YET REQUESTED.** It has been prepared and not sent; Ian will route it. No independent review exists for this exact SHA.
