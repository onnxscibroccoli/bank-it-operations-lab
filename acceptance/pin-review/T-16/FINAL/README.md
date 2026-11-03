# T-16 FINAL: comparison and recommendation (input to the Integrator's reconciliation)

Prepared 2026-11-03, about 17:50 EST, on `acceptance/t16-pin-review` (PR #42) by the shared agent account.
**This is input, not a competing final pin.** The final T-16 reconciliation belongs to the Integrator, at
**`coordination/T16_RECONCILIATION.md` on `integration/candidate-20261103c`**. That branch did not exist on `origin` when
this was written (checked with `git fetch` at about 17:45 EST). Nothing here edits that branch or
`integration/candidate-20261103b`, and nothing has been installed, trusted or reviewed.

## The two proposals

| | PR #42 proposal | candidate proposal |
|---|---|---|
| gate_sha | `6ea6803c0828a65fb269bb551ad5449f0d8ed948` | `a518b03e204d4b77a67e16ed83652acdbdd7b8d5` |
| where | PR #40 commit, a first-parent ancestor of main `8e2df97b`; file `../gate-manifest.main.PROPOSED-NOT-TRUSTED.json` | `integration/candidate-20261103b` only (no PR yet); file `coordination/proposed-gate-pin/gate-manifest.json` @ `caa9ce7c` |
| author | `onnxscibroccoli` (shared agent account) | `onnxscibroccoli` (shared agent account), committed 2026-11-03 17:05:39 EST, parent `e918b85b` |
| gate files equal to | main `8e2df97b` (31/31) | candidate head `caa9ce7c` (35/35) |
| independent review | none | none |

Both authors are the same shared account, so neither proposal is independent of the work it pins.

## Per-file comparison (`FILES.tsv` has all 35 paths)

There are 30 paths whose hashes are identical in the current pin, main, `6ea6803c` and `a518b03e`. They include the whole
trust core: `verify_trusted_gate.py`, `merge_eligibility.py`, `reviews.py`, `provenance.py`, `final_summary.py`,
`check_exceptions.py`, `trusted-config.json` (`reviewer_allowlist` is `[]` in all of them) and `integration-gate.yml`
(`verification/10-trust-core-unchanged.txt`). `6ea6803c` is identical to main. The differences between `a518b03e` and
`6ea6803c`/main (`diffs/6ea6803c..a518b03e-gate-files.diff`, 5 files, +313/−1):

| path | 6ea6803c / main | a518b03e | class | why |
|---|---|---|---|---|
| `scripts/ci/tests/test_module_coverage.py` | `e481f054…` | `7dba8ea5…` | implementation | One assertion follows the module registry: main expects `["review-notes(NOT_INTEGRATED)"]`, the candidate expects `[]` because it integrates review-notes. The current pin `92cd251e…` is a third wording of `[]` |
| `scripts/ci/check_registries.py` (added) | — | `82ecd70a…` | implementation | Offline consistency check across modules.json, tasks.json, pages.json and preserved-records. Called only from `scripts/validate-all.sh`, not from `integration-gate.yml` or `merge_eligibility.py`. Reads no manifest, allowlist or trusted config |
| `scripts/ci/tests/test_check_registries.py` (added) | — | `46799c01…` | implementation | Negative tests for the above |
| `scripts/ci/tests/test_actions_pinned.py` (added) | — | `cfffe17a…` | implementation | Static T-11 test that every `uses:` is pinned to a SHA. Hardening; decides no trust |
| `scripts/ci/tests/test_t16_pin_proposal.py` (added) | — | `744fdfdc…` | **trust-boundary** (test-only) | Exercises `pin_trust`, self-pin and forged reviews, and imports `verify_trusted_gate` and `test_merge_eligibility_binding`. It changes no decision code, but a weak version could hide a trust regression |

The re-pin itself (a new `gate_sha` and hash set) is a trust-boundary change whichever proposal is used. Outside the
manifest, the candidate's `.github/workflows/documentation.yml` pins 7 actions to SHAs, all matching their tags
(`verification/9-…`), and adds `integration/**` pushes. It does not run merge-eligibility. Class: implementation.

## Recommendation

**Use the `a518b03e` hash set (the candidate's gate implementation) as the basis, and treat the PR #42 `6ea6803c`
proposal as superseded.** The `6ea6803c` file stays on file for history and is not deleted.

1. **It is the tree that will be reviewed and merged.** The consolidated candidate contains main plus PR #39 and PR #41
   (their current heads change no gate file) and review-notes. A pin matches exactly one tree. `6ea6803c` rejects the
   candidate (1 changed file and 4 unlisted files), and `a518b03e` rejects main (`verification/6-…`). So pinning
   `6ea6803c` would only re-break as soon as the candidate merges.
2. **The extra delta is small and reviewable:** 4 implementation files and 1 test-only trust-boundary file, with no
   change to any trust-core file.
3. **No self-pin, and it can be review-bound.** `a518b03e` is not the candidate head (`caa9ce7c`), and it becomes a commit
   in the candidate's PR once one is opened, so a reviewer can approve that exact `commit_id`.
4. **It matches the candidate's own proposal** byte for byte (`verification/manifest-diff-candidate.txt`).

### Conditions for the Integrator

- If `integration/candidate-20261103c` changes any gate file relative to `a518b03e`, or gets new commits that do,
  rebuild the manifest for that exact commit
  (`python3 scripts/ci/verify_trusted_gate.py --build --gate-dir . --gate-head <sha> --out <file>`) and re-classify the
  delta against `FILES.tsv`. If its gate files are identical, the recommended `files` stay valid, and only `gate_sha`
  needs to point at a reviewable commit on the branch that merges.
- **No pin can verify yet.** `pin_trust` reads `reviewer_allowlist` from the pinned commit's own trusted config, and it
  is `[]` in every candidate. A human reviewer must first be added there (a heightened-review trust-boundary change),
  and the manifest must be rebuilt for the commit that carries it.

## Recommended manifest (input only, NOT trusted)

`gate-manifest.RECOMMENDED-a518b03e.PROPOSED-NOT-TRUSTED.json`: gate_sha `a518b03e`, 35 files,
`independent_review: null`. Compared with the current pin: 1 changed and 4 added.

## Tests and current behavior

- Hash mode: each pin matches only its own tree (`verification/6-…`). CI reproduces this: candidate run
  [41731062507](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731062507) rejects the current pin
  (`verification/11-…`), and so does main run 41703902441.
- D3 `--check-pin`: both proposals are **TRUSTED GATE UNVERIFIED** (`verification/7-…`).
- Suites: `scripts/ci` passes 159/159 on main and 178/178 on the candidate. Each version of `test_module_coverage.py` passes only against its own registry (`verification/8-…`).
- Regression tests (`tools/acceptance/gate/tests/test_pin_review.py`, gate check ACC-D-01): FA-T16-1 to FA-T16-10, plus
  FINAL checks. The recommended manifest is unreviewed, UNVERIFIED without a review and with forged reviews, leaves the
  trust core untouched, cannot be applied to main, and matches this table.

## Impact on acceptance behavior

- Installing the recommended hash set after a qualifying review would make "Verify the trusted gate" pass for the
  candidate tree, and only for that tree.
- `merge-eligibility` stays **NOT ELIGIBLE** until `independent_review {pr, review_id}` names an APPROVED review of the
  exact `gate_sha` by an allow-listed, write-permitted human who is not the PR author.
- `acceptance.yml` is unchanged: it ends at `EXECUTION_PASS` + `REVIEW_PENDING`, with no ACCEPTED state.

## Review requirements (unchanged; see `../README.md`)

- **Who may approve:** a human with write access who is not the PR author, not `onnxscibroccoli` and not a bot, and who
  is on `reviewer_allowlist` at the pinned commit.
- **What they must check:**
  1. rebuild the manifest from `gate_sha` and compare it with the proposal;
  2. read the 5-file delta and the classifications here;
  3. run `scripts/ci/tests` and `tools/acceptance/gate/tests` at `gate_sha`;
  4. approve that exact `commit_id`.
- **Heightened review:** `test_t16_pin_proposal.py`, the re-pin itself, and the future `reviewer_allowlist` edit.
