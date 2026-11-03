# T-16: the stale trusted pin behind the red `merge-eligibility`

Prepared 2026-11-03 (EST) on branch `acceptance/t16-pin-review` by the shared agent account, working as acceptance integrator.
**This is a proposal. It is not a review and not an approval.** The proposed manifest has **not** been pushed to
`evidence/acceptance`, is not in `.github/acceptance/`, and is not in any other location the gate reads.

## Finding

The trusted manifest is `evidence/acceptance@750de1c694c4912f12bb5bb76a20ba74bc208213:trusted-gate/gate-manifest.json`.
It pins `gate_sha ea0c23597e1eec9bd15ecccc16b40a6ecbe057ae` (31 files) and has `independent_review: null`.
When it is compared with `main @ 8e2df97b558e69032e52a50ed0adfd311ad04578`, **exactly one entry is stale**. The other
30 match, and neither side has a file the other lacks:

| field | value |
|---|---|
| path | `scripts/ci/tests/test_module_coverage.py` |
| old pinned sha256 (blob at `ea0c2359`) | `92cd251e7325b7892ccab83a9af6e81b13c58f9e2f9394b0d83d7890dda6ac9d` |
| current sha256 on main (blob at `6ea6803c` = `8e2df97b`) | `e481f054a2d68d75122c46298a5de831dea9d09f121f364ae43ae35bae48f5e9` |
| failing run | integration-gate run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441) on the main push `8e2df97b`, step "Verify the trusted gate", `GATE HASHES REJECTED: 1 error(s)` (`verification/0-…`) |

### History of the file (sha256 of each version)

| commit | date | version | sha256 |
|---|---|---|---|
| `51e404c4` | 2026-10-28 21:14 EDT | created (asserts acceptance and review-notes NOT_INTEGRATED) | `c7f641a7…` (the earlier pin `af49a27` had this hash) |
| `0d30e56e` | 2026-10-29 00:39 EDT | offline-gate repair; main `30e0a832` carries this version (`diffs/1-…`) | `49f6a8f8…` |
| `ea0c2359` on `integration/completion-20261103` (not on main, no PR) | 2026-11-03 13:35 EST | asserts `incomplete == []` (marks **both** acceptance and review-notes INTEGRATED) (`diffs/2-…`) | `92cd251e…` (**pinned**) |
| `6ea6803c` in PR #40, merged into main as `8e2df97b` | 2026-11-03 13:40 EST | asserts `incomplete == ["review-notes(NOT_INTEGRATED)"]` (only acceptance INTEGRATED) (`diffs/3-…`) | `e481f054…` (**main**) |

`diffs/4-…` is the pinned-to-main diff: two lines in one assertion of `test_denominator_counts_every_status`.
`diffs/5-…` is the `--stat` for all gate files `ea0c2359..8e2df97b`, and this is the only file that differs.

### Reason

Two parallel lines of work changed the same test assertion in different ways on the same afternoon.
`evidence/acceptance` was re-pinned at 13:35 EST (`750de1c6`) to the `integration/completion-20261103` gate commit
`ea0c2359`. That branch also registers `review-notes` as INTEGRATED. Five minutes later, PR #40's commit `6ea6803c`
updated the assertion for acceptance only. PR #40 was merged into main, and `integration/completion-20261103` was not.
main's `coordination/modules.json` still has `review-notes` NOT_INTEGRATED. So the pinned version **fails** on main
(`verification/5-…`: `['review-notes(NOT_INTEGRATED)'] != []`), and main's version passes (11/11; the full `scripts/ci` suite passes 159/159).
The fix is to re-pin to main's version. The other option, changing main's test to match the pin, would make main's own suite fail.

## Proposed correction (not installed)

`gate-manifest.PROPOSED-NOT-TRUSTED.json` was built with main's own `verify_trusted_gate.py --build`, which takes hashes
from git objects only. It has:

- `gate_sha 6ea6803c0828a65fb269bb551ad5449f0d8ed948`. This is PR #40's registry/docs commit, a first-parent ancestor of
  main. Its gate files are byte-identical to main `8e2df97b` (31 of 31). It was chosen over `8e2df97b` because the pin
  must not equal the candidate (D3 self-pin), and `8e2df97b` is itself the candidate of the main push run. It is also a
  commit inside PR #40, which a reviewer can review.
- one changed entry versus the current pin (`verification/manifest-diff.txt`);
- `independent_review: null`.

## Verification (all local, read-only, main's gate code)

| file | result |
|---|---|
| `verification/1-current-manifest-vs-main.txt` | current pin vs main: **REJECTED**, 1 error (reproduces CI) |
| `verification/2-proposed-manifest-vs-main.txt` | proposed pin vs main: GATE HASHES MATCH (hash consistency only) |
| `verification/3-proposed-manifest-check-pin.txt` | proposed pin, D3: **TRUSTED GATE UNVERIFIED**, "no independently reviewed gate pin" |
| `verification/4-current-manifest-check-pin.txt` | current pin, D3: also UNVERIFIED (`independent_review` null) |
| `verification/5-module-coverage-tests.txt` | pinned version fails on main; main's version passes |

The regression tests are in `tools/acceptance/gate/tests/test_pin_review.py` (gate check ACC-D-01). They run
`scripts/ci/verify_trusted_gate.py` from main read-only:
FA-T16-1 (unapproved proposed manifest → UNVERIFIED), FA-T16-2 (UNVERIFIED even when the checkout, executing code and
workflow all bind to the pin), FA-T16-3 (an approval by the shared agent account, who is the PR author, is rejected even
if allow-listed), FA-T16-4 (a reviewer who is not on the allowlist is rejected; the allowlist is empty today), FA-T16-5
(a read-only reviewer is rejected), FA-T16-6 (self-pin is rejected), FA-T16-7 (the proposal is not installed at the
trusted path on main), and a positive control showing the rule can verify, so the negative results are not vacuous.

## Impact of re-pinning

- **Hash step:** once an owner installs it, the "Verify the trusted gate" step passes for main and for any PR that
  leaves gate files unchanged. PRs that change `scripts/ci/**`, the trusted config or `integration-gate.yml` are still rejected.
- **`merge-eligibility` stays red (NOT ELIGIBLE).** `merge_eligibility.py` recomputes D3 itself and finds no qualifying
  `independent_review`, so the result is `TRUSTED GATE UNVERIFIED`. A re-pin alone does not turn it green, and this is intended.
- **To get to green**, the owner has to do all of the following:
  1. invite a human reviewer with write access (today the only collaborator is the shared agent account);
  2. add that login to `reviewer_allowlist` in `.github/acceptance/trusted-config.json` (empty today, so no review can
     qualify). That changes a pinned file, so the pin must then be rebuilt for the commit that carries it;
  3. have the reviewer submit an APPROVED review whose `commit_id` equals the final `gate_sha`;
  4. record `independent_review {pr, review_id}` and install the manifest on `evidence/acceptance` once its own protection (UA-3) is in place.
- No production, AWS, Entra or Graph change is involved.
- `verification/` holds the full outputs. `SHA256SUMS` covers every file in this directory except itself and is checked by the tests.
