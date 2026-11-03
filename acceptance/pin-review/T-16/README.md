# T-16: the stale trusted pin behind the red `merge-eligibility`

Updated 2026-11-03, about 17:45 EST, on `acceptance/t16-pin-review` (PR #42), by the shared agent account working as acceptance integrator.
**This is a proposal. It is not a review and not an approval.** Neither corrected manifest has been pushed to
`evidence/acceptance` or put in `.github/acceptance/`, and neither is marked trusted anywhere.

## Refs (re-checked with `git fetch` before this update)

| ref | SHA |
|---|---|
| `evidence/acceptance` (the manifest's location; has not moved) | `750de1c694c4912f12bb5bb76a20ba74bc208213` |
| current pin `gate_sha` | `ea0c23597e1eec9bd15ecccc16b40a6ecbe057ae` (on `integration/completion-20261103` @ `3c417d91`; unmerged, no PR) |
| `main` (has not moved since PR #40) | `8e2df97b558e69032e52a50ed0adfd311ad04578` |
| **consolidated candidate** `integration/candidate-20261103b` (no PR yet) | head `caa9ce7c1b1538d8da920463db77c93c05fe882b`, tested SHA `308512714690ba20a6d9003fcd0731b88fffd596`, gate commit `a518b03e204d4b77a67e16ed83652acdbdd7b8d5` |

The candidate is based on main `8e2df97b`. It merges PR #39 and PR #41, preserves review records #28/#30–#34, and makes
review-notes INTEGRATED. Its gate files are byte-identical from `a518b03e` to the head `caa9ce7c` (35/35). The other open
PRs (#39, #41) are contained in it and change no gate file, so there is no other consolidation candidate.

## 1. The 31 trusted entries (`trusted-gate/gate-manifest.json` @ `750de1c6`)

| # | path | pinned sha256 | class |
|---|---|---|---|
| 1 | `.github/acceptance/trusted-config.json` | `8ee6d89e234842f4b556fa74a149596f4128d25a52254d44f12d4275f2a05325` | trust-boundary |
| 2 | `.github/workflows/integration-gate.yml` | `d031430acdc49237d25f538b9129cf3d01966634dec9663ee3b8a2c722325dc4` | trust-boundary |
| 3 | `scripts/ci/check_exceptions.py` | `e6e0d4394ea88a6666317d83bd75c18c9ee7a00b6ce943b8e32babd416ba87e6` | trust-boundary |
| 4 | `scripts/ci/check_incident_run.py` | `b2d22f498eb27f3051b904d7bb0723b80b5fd60b91b8f20b0c73e94540d95105` | implementation |
| 5 | `scripts/ci/check_labels.py` | `235254bdbbd6ed4db5849e8a04f24e055bceb746ac2df2c4f9ba51f71d82a82b` | implementation |
| 6 | `scripts/ci/check_modules.py` | `7286fcd929016e153b8b6d1def19088c31aafc525fabc685f38e5f4c62760402` | implementation |
| 7 | `scripts/ci/check_plan_only.py` | `c12ad8f5d0e5954749df099f044d78b44bc457477183ad1adb340952098d1e94` | implementation |
| 8 | `scripts/ci/final_summary.py` | `e4af382e0f9e7fb68889148ef414788d1ac7124fadf1ab4bd3fa5f1559d83476` | trust-boundary |
| 9 | `scripts/ci/incident_checks.sh` | `a7ea0fb30906d07fb99c39335ff35d0dfe1eb4a38612453b6989c951b1f2b83e` | implementation |
| 10 | `scripts/ci/m365_checks.sh` | `a92a7b2076bd79e1b8d5d06b14a15d0103df32fde500f9bc52c3d9a8a15a1838` | implementation |
| 11 | `scripts/ci/merge_eligibility.py` | `37411f06d452269891a7c05023f8ffaaa2ab0bb4bfd902836fab5e83e4a14083` | trust-boundary |
| 12 | `scripts/ci/portfolio_checks.sh` | `85c78935878ee88fc2179572c582baaecd7e5aab24557adc0255cb17ff90a012` | implementation |
| 13 | `scripts/ci/portfolio_summary.py` | `56a7b91cf4ee38beb0761345c5f77f68756001ef246344e3fb898765ea9b3568` | implementation |
| 14 | `scripts/ci/provenance.py` | `cfa67c8ce376fdd18190c0912aea6789f7b4d118b3270a60ec88e4faacaced5a` | trust-boundary |
| 15 | `scripts/ci/reviews.py` | `fe17ef432447dbb5bcff41f21748d667bc910c04356583695a229320a3f57127` | trust-boundary |
| 16 | `scripts/ci/tests/test_ac_repairs_b908a66.py` | `06123f9a0a970794409f4aa941faff8e243953de27e06a4c8dee23c6e749f445` | trust-boundary |
| 17 | `scripts/ci/tests/test_ac_runtime_pr31.py` | `06d334b1187ca21d61714047c8661deb9a32ecbc640bd5aa8b1781a2e83ef26e` | trust-boundary |
| 18 | `scripts/ci/tests/test_check_labels.py` | `4c1e2aa9adbe09919c0e084b52833c642acdf0eb3ef146d5060a439163e59903` | implementation |
| 19 | `scripts/ci/tests/test_check_plan_only.py` | `ec93a3c68220b6a51e2c0572a25e1791c87d5d735f9a79c17e7ccaf2c2393320` | implementation |
| 20 | `scripts/ci/tests/test_fresh_run_wiring.py` | `9b2192fb0cff761e4ef51fc59a8ff59b59ac32b8373c9a419ae2b04f9835acd6` | implementation |
| 21 | `scripts/ci/tests/test_gate_required.py` | `c3c169ef690fbadf516c22e2730006390f4b3b26f5c64f636a0cbc6e0a2dfb15` | trust-boundary |
| 22 | `scripts/ci/tests/test_incident_requirements.py` | `22805bea237e4aed27fd9ea87341a92bd841c16048ef6f21a852142ffb760e5d` | implementation |
| 23 | `scripts/ci/tests/test_merge_eligibility_binding.py` | `7af563edddd0152ca5c5527557f577d9f5c149679b090c7a9b99eb2fa5599a93` | trust-boundary |
| 24 | `scripts/ci/tests/test_module_coverage.py` | `92cd251e7325b7892ccab83a9af6e81b13c58f9e2f9394b0d83d7890dda6ac9d` | implementation |
| 25 | `scripts/ci/tests/test_portfolio_summary.py` | `8107b4c26ab110d9271665c6984602031c43d5ea88249bc5afac8238eed802ff` | implementation |
| 26 | `scripts/ci/tests/test_pr32_independence.py` | `00bcc69d8e9575adff6ab4abdcf3af338c57fee8991edf86b182462a7a2949c9` | trust-boundary |
| 27 | `scripts/ci/tests/test_pr33_pin_binding.py` | `44c0104c7432412db2817817e347563147e21b3a77588555a1de33fbf39b2bb9` | trust-boundary |
| 28 | `scripts/ci/tests/test_provenance_base.py` | `2416184688f95683f5e37873825090d7ddcc6682fa3ed548252c368043e4f38d` | trust-boundary |
| 29 | `scripts/ci/tests/test_verify_trusted_gate.py` | `1f33d3a84186c4ab03ffeaf54c170025e111030a547cf50596f7f7e7d777eee6` | trust-boundary |
| 30 | `scripts/ci/user_actions.py` | `22debdae0a88ed4f1d683b7c490e5c10db54f4fbb1f228c78d75b1e4d0a0d59b` | implementation |
| 31 | `scripts/ci/verify_trusted_gate.py` | `e3057ccd4d845d9292348209296d29ba84d73ab40dc6b11e6ff88f093d09390f` | trust-boundary |

## 2. Mismatches against main and the candidate

`FILES.tsv` has the hashes of every path in all three versions (pin, main, candidate). The rows that differ:

| path | pinned | main `8e2df97b` | candidate `a518b03e` | class | reason |
|---|---|---|---|---|---|
| `scripts/ci/check_registries.py` | — | — (same) | `82ecd70a1188ecd7fde99f577cf30340f5ff571ef243f6fb833570213de7e697` (ADDED) | **implementation** | NEW in candidate: offline cross-registry consistency check (modules.json/tasks.json/pages.json/preserved-records); called only from scripts/validate-all.sh, not from integration-gate.yml or merge_eligibility.py; reads no manifest, allowlist or trusted config |
| `scripts/ci/tests/test_actions_pinned.py` | — | — (same) | `cfffe17a39a36af1d762f1098ab0270829ffb1ac125f15e079a8f8d4d95f38f6` (ADDED) | **implementation** | NEW in candidate: T-11 static test that every workflow uses: is a local workflow or a 40-hex SHA; hardening, decides no trust |
| `scripts/ci/tests/test_check_registries.py` | — | — (same) | `46799c01143cf968994c800ecce535508f14dba9515536604840af8005339193` (ADDED) | **implementation** | NEW in candidate: negative tests for check_registries.py |
| `scripts/ci/tests/test_module_coverage.py` | `92cd251e7325b7892ccab83a9af6e81b13c58f9e2f9394b0d83d7890dda6ac9d` | `e481f054a2d68d75122c46298a5de831dea9d09f121f364ae43ae35bae48f5e9` (CHANGED) | `7dba8ea5483c5404164992ca3a3389d2403e98e342f09cd5e75d973588ca7d31` (CHANGED) | **implementation** | one assertion in the module-registry coverage test follows coordination/modules.json; no trust logic. Main expects [review-notes(NOT_INTEGRATED)], the candidate expects [] (it integrates review-notes), the pin expects [] from the unmerged integration/completion-20261103 |
| `scripts/ci/tests/test_t16_pin_proposal.py` | — | — (same) | `744fdfdc052ddcf800bcdedbce0e4760e935b38fa603e75ed971579ce4f8e5db` (ADDED) | **trust-boundary** | NEW in candidate: tests of pin_trust / self-pin / forged reviews against the proposed pin; imports verify_trusted_gate and test_merge_eligibility_binding |

Every other entry (30 of 31) is byte-identical in the pin, main and the candidate. That includes the whole trust core:
`verify_trusted_gate.py`, `merge_eligibility.py`, `reviews.py`, `provenance.py`, `final_summary.py`, `check_exceptions.py`,
`.github/acceptance/trusted-config.json` (`reviewer_allowlist` is `[]` in all three) and `integration-gate.yml`
(`verification/10-…`). The candidate also changes `.github/workflows/documentation.yml`. That file is **not** in the
manifest and does not run merge-eligibility. It pins 7 actions to SHAs, all of which match their tags
(`verification/9-…`), and adds `integration/**` to the push trigger (`diffs/9-…`). Class: implementation (supply-chain hardening).

### History behind each mismatch

- `test_module_coverage.py`:
  - `51e404c4` (2026-10-28 21:14 EDT) created it;
  - `0d30e56e` (2026-10-29 00:39 EDT) is main `30e0a832`'s version;
  - `ea0c2359` (2026-11-03 13:35 EST, `integration/completion-20261103`) asserts `[]`, and evidence/acceptance `750de1c6` pinned it at 13:35;
  - `6ea6803c` (13:40 EST, PR #40, merged into main as `8e2df97b`) asserts `["review-notes(NOT_INTEGRATED)"]`;
  - `a518b03e` (17:05 EST, candidate) asserts `[]` again, with a different comment from the pin.
  - Diffs: `diffs/1-…` to `diffs/4-…`, `diffs/6-…`, `diffs/7-…`.
- The 4 added files: all come from the single candidate commit `a518b03e` ("registry reconciliation, T-11 action pins, T-16 fail-closed tests"). Full diffs are in `diffs/8-…`.

## Root cause

The pin was taken from a branch that never landed. At 13:35 EST, `evidence/acceptance` was re-pinned to `ea0c2359` on
`integration/completion-20261103`, with no PR and no review. Main instead received PR #40 at 13:40, which changed the same
`test_module_coverage.py` assertion differently, because review-notes was not integrated on main. The trusted manifest was
never rebuilt from main. So main's own verifier copy has not matched the pin since the PR #40 merge (19:30 UTC = 14:30 EST).
The candidate carries a third version and adds 4 verifier-directory files, so it fails against both the current pin and the
main proposal. Neither tree can be fixed by changing code without making its own test suite fail (`verification/8-…`):
each version of the test passes only against its own tree's registry.

## 3. Classification

- **Implementation** (no effect on how trust is decided): `test_module_coverage.py` (a registry assertion),
  `check_registries.py` and `test_check_registries.py` (registry consistency; called only from `scripts/validate-all.sh`;
  they read no manifest, allowlist or config), and `test_actions_pinned.py` (a static workflow-pinning test).
- **Trust boundary:** `test_t16_pin_proposal.py`. It is test-only and changes no decision code. It exercises `pin_trust`,
  self-pin and forged reviews, and imports `verify_trusted_gate` and `test_merge_eligibility_binding`. A weakened version
  could hide a trust regression, so it gets heightened review.
- **Trust boundary, by definition:** the re-pin itself (a new `gate_sha` and a new hash set in the trusted manifest).

## 4. Corrected manifests (proposals, NOT trusted, not installed)

> **Superseded recommendation:** see `FINAL/README.md`. The main-only proposal (`6ea6803c`) is kept for history. The recommended input to the Integrator's `coordination/T16_RECONCILIATION.md` (on `integration/candidate-20261103c`) is the `a518b03e` hash set.

| file | for | gate_sha | vs current pin |
|---|---|---|---|
| `gate-manifest.main.PROPOSED-NOT-TRUSTED.json` | main as it is (`8e2df97b`) | `6ea6803c0828a65fb269bb551ad5449f0d8ed948` (PR #40 commit; gate files identical to main; not a self-pin of main's merge commit) | 1 changed |
| `gate-manifest.candidate-20261103b.PROPOSED-NOT-TRUSTED.json` | only if the candidate is what merges | `a518b03e204d4b77a67e16ed83652acdbdd7b8d5` | 1 changed, 4 added |

Both were built with main's `verify_trusted_gate.py --build` from git objects, and both have `independent_review: null`.
The candidate one has the same files and `gate_sha` as the candidate's own `coordination/proposed-gate-pin/gate-manifest.json`
(`verification/manifest-diff-candidate.txt`). **Pick one:** a manifest pins one tree. The main pin rejects the candidate,
and the candidate pin rejects main (`verification/6-…`).

## Test results

- Hash mode (`verification/6-…`): each pin matches only its own tree. The current pin rejects main (1 error) and the
  candidate (2 errors). This is reproduced in CI: main run 41703902441 (`verification/0-…`) and candidate run
  [41731062507](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731062507) (`verification/11-…`).
- D3 `--check-pin` (`verification/3-…`, `verification/7-…`): **both proposals are TRUSTED GATE UNVERIFIED** (no independently reviewed pin).
- Suites (`verification/8-…`): `scripts/ci` passes 159/159 on main and 178/178 on the candidate.
- Regression tests (`tools/acceptance/gate/tests/test_pin_review.py`, run by ACC-D-01):
  - FA-T16-1 to FA-T16-7 (main proposal);
  - FA-T16-8: neither proposal changes a trust-core file;
  - FA-T16-9: the candidate proposal is UNVERIFIED unreviewed, with an approval from the shared account, and with an approval from someone not on the allowlist;
  - FA-T16-10: a pin for one tree cannot be reused for the other;
  - a check that this table matches the manifests;
  - a check that `SHA256SUMS` is complete.

## Impact on acceptance behavior

- Once an owner installs a reviewed pin, the "Verify the trusted gate" step passes for the pinned tree. A PR that changes
  `scripts/ci/**`, the trusted config or `integration-gate.yml` without a new reviewed pin is still rejected.
- **`merge-eligibility` stays red (NOT ELIGIBLE) even after a re-pin** until `independent_review {pr, review_id}` names a
  qualifying review. Today none can qualify: `reviewer_allowlist` is `[]`, and the only collaborator is the shared agent
  account, which authors every PR.
- The acceptance workflow is unaffected: it still ends at `EXECUTION_PASS` + `REVIEW_PENDING` and never reports ACCEPTED.
- Nothing touches production, AWS, Entra or Graph.

## Independent-review requirements

**Who may approve:** a human GitHub account with write, maintain or admin permission on the repository who is not the
author of the PR carrying `gate_sha`, is not `onnxscibroccoli` (the shared agent account) and is not a bot. That login must
first be added to `reviewer_allowlist` in `.github/acceptance/trusted-config.json` through a reviewed change. That edit is
itself a trust-boundary change, and it means the pin has to be rebuilt for the commit that carries it.

**What they must check, for the chosen tree:**

1. `gate_sha` is on the branch that will merge, and is not that branch's merge or candidate commit (no self-pin).
2. Re-run `python3 scripts/ci/verify_trusted_gate.py --build --gate-dir . --gate-head <gate_sha> --out /tmp/m.json` and
   compare `files` with the proposal. They must be identical.
3. Read every diff in `diffs/` and check the classifications in `FILES.tsv`.
4. Run `python3 -m unittest discover -s scripts/ci/tests` at `gate_sha` (it must pass), and
   `python3 -m unittest discover -s tools/acceptance/gate/tests`.
5. Submit an APPROVED review whose `commit_id` equals `gate_sha`. Then the owner records `{pr, review_id}` and installs the
   manifest on `evidence/acceptance` (protected first, `acceptance/rulesets/`).

**Heightened review** (line-by-line reading, plus a second person if one is available) for any change to:
`verify_trusted_gate.py`, `merge_eligibility.py`, `reviews.py`, `provenance.py`, `final_summary.py`, `check_exceptions.py`,
`.github/acceptance/trusted-config.json` (especially `reviewer_allowlist`), `.github/workflows/integration-gate.yml`, the
tests of those files (including the candidate's new `test_t16_pin_proposal.py`), and the manifest's `gate_sha` or hash set.
In this T-16 delta the only such items are `test_t16_pin_proposal.py` (candidate only) and the re-pin itself.

`SHA256SUMS` covers every other file in this directory and is checked by the tests.
