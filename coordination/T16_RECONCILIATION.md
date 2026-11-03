# T-16 reconciliation: one gate-pin proposal for candidate-20261103c

Prepared 2026-11-03 (EST, America/New_York) for the Acceptance Integrator to review. Integration-agent work on the shared account: **not a review, not an approval**. Nothing here is installed on `evidence/acceptance`, and the gate stays fail-closed.

## The two proposals

| | PR #42 (`acceptance/t16-pin-review` @ `9589d891`) | candidate-20261103c (`coordination/proposed-gate-pin/gate-manifest.json`) |
|---|---|---|
| gate_sha | `6ea6803c0828a65fb269bb551ad5449f0d8ed948` (inside PR #40, ancestor of main) | `39c71f9eebf8bb72663515a29b52609d02dceea4` (gate commit on this branch) |
| binds | main `8e2df97` code: 31 files, byte-identical to main | the final candidate code: 35 files |
| delta vs current pin `ea0c235` | 1 file: `scripts/ci/tests/test_module_coverage.py` (`92cd251e` -> main `e481f054`) | 4 added files, 0 changed (the candidate uses the pinned `92cd251e` bytes of `test_module_coverage.py`) |
| delta vs main | none | 5 trust-boundary files (below) |
| independent_review | null | null (review_status UNREVIEWED) |
| installed | no | no |

## Which gate implementation is intended

Both proposals keep main's gate logic unchanged: `verify_trusted_gate.py`, `merge_eligibility.py`, `reviews.py`, `provenance.py`, `trusted-config.json` (with `reviewer_allowlist: []`) and `integration-gate.yml` hash the same in all four columns below. They differ only because each binds different code:

- **#42 binds main as it is.** It fixes main's red `merge-eligibility` hash check. main's test asserts `review-notes(NOT_INTEGRATED)`, which is true on main.
- **This proposal binds the candidate** that goes to independent review. On the candidate, review-notes is INTEGRATED, so the test asserts `incomplete == []`. Those are the exact bytes already pinned at `ea0c235`. The candidate also adds the registry check and the T-11/T-16 tests.

If #42 were installed, this candidate would still be rejected (5 mismatches). If this proposal were installed, main would be rejected (`test_module_coverage.py` plus 4 extra files). **Conclusion:** for the candidate going to independent review, this proposal supersedes `6ea6803c`. #42 stays the right fix only if main moves without this candidate. Either way, the pin must be reviewed by an allow-listed, write-permitted non-author (UA-7) before anyone installs it.

## Trust-boundary changes vs main (heightened review)

| File | Status | Purpose |
|---|---|---|
| `scripts/ci/check_registries.py` | ADDED (not on main) | new: R1-R5 registry reconciliation (modules/tasks/pages/preserved records); read-only, no network; run by validate-all.sh |
| `scripts/ci/tests/test_actions_pinned.py` | ADDED (not on main) | new (T-11): every workflow `uses:` is a 40-hex SHA or a local workflow |
| `scripts/ci/tests/test_check_registries.py` | ADDED (not on main) | new: 10 tests for R1-R5 including negatives |
| `scripts/ci/tests/test_module_coverage.py` | CHANGED vs main | assertion `incomplete == []` (review-notes INTEGRATED on the candidate); bytes equal the current pin ea0c235 |
| `scripts/ci/tests/test_t16_pin_proposal.py` | ADDED (not on main) | new (T-16): the proposal stays UNREVIEWED; unreviewed, forged, non-allow-listed and self-pin manifests are UNVERIFIED; direct pushes to main and missing approval are NOT ELIGIBLE |

None of the 5 files is imported by `merge_eligibility.py`, `verify_trusted_gate.py` or any other `scripts/ci/*.py` module, and `integration-gate.yml` does not name them. They are tests or registry checks inside the hashed `scripts/ci/` tree. The gate workflow's "CI self-tests" step (`unittest discover -s scripts/ci/tests`, integration-gate.yml line 66) does run the three added tests. An option for the reviewer (not taken, because directive t26u named `scripts/ci/check_registries.py`): move the 4 added files outside `scripts/ci/`. The candidate would then hash-match the current pin `ea0c235` exactly. It would still be TRUSTED GATE UNVERIFIED (no independent review), so still NOT ELIGIBLE.

## All trusted files (sha256, first 8 hex)

| File | current pin ea0c235 | main 8e2df97 | #42 proposal 6ea6803c | candidate proposal | candidate vs main |
|---|---|---|---|---|---|
| `.github/acceptance/trusted-config.json` | `8ee6d89e` | `8ee6d89e` | `8ee6d89e` | `8ee6d89e` | identical to main |
| `.github/workflows/integration-gate.yml` | `d031430a` | `d031430a` | `d031430a` | `d031430a` | identical to main |
| `scripts/ci/check_exceptions.py` | `e6e0d439` | `e6e0d439` | `e6e0d439` | `e6e0d439` | identical to main |
| `scripts/ci/check_incident_run.py` | `b2d22f49` | `b2d22f49` | `b2d22f49` | `b2d22f49` | identical to main |
| `scripts/ci/check_labels.py` | `235254bd` | `235254bd` | `235254bd` | `235254bd` | identical to main |
| `scripts/ci/check_modules.py` | `7286fcd9` | `7286fcd9` | `7286fcd9` | `7286fcd9` | identical to main |
| `scripts/ci/check_plan_only.py` | `c12ad8f5` | `c12ad8f5` | `c12ad8f5` | `c12ad8f5` | identical to main |
| `scripts/ci/check_registries.py` | absent | absent | absent | `82ecd70a` | ADDED (not on main) |
| `scripts/ci/final_summary.py` | `e4af382e` | `e4af382e` | `e4af382e` | `e4af382e` | identical to main |
| `scripts/ci/incident_checks.sh` | `a7ea0fb3` | `a7ea0fb3` | `a7ea0fb3` | `a7ea0fb3` | identical to main |
| `scripts/ci/m365_checks.sh` | `a92a7b20` | `a92a7b20` | `a92a7b20` | `a92a7b20` | identical to main |
| `scripts/ci/merge_eligibility.py` | `37411f06` | `37411f06` | `37411f06` | `37411f06` | identical to main |
| `scripts/ci/portfolio_checks.sh` | `85c78935` | `85c78935` | `85c78935` | `85c78935` | identical to main |
| `scripts/ci/portfolio_summary.py` | `56a7b91c` | `56a7b91c` | `56a7b91c` | `56a7b91c` | identical to main |
| `scripts/ci/provenance.py` | `cfa67c8c` | `cfa67c8c` | `cfa67c8c` | `cfa67c8c` | identical to main |
| `scripts/ci/reviews.py` | `fe17ef43` | `fe17ef43` | `fe17ef43` | `fe17ef43` | identical to main |
| `scripts/ci/tests/test_ac_repairs_b908a66.py` | `06123f9a` | `06123f9a` | `06123f9a` | `06123f9a` | identical to main |
| `scripts/ci/tests/test_ac_runtime_pr31.py` | `06d334b1` | `06d334b1` | `06d334b1` | `06d334b1` | identical to main |
| `scripts/ci/tests/test_actions_pinned.py` | absent | absent | absent | `cfffe17a` | ADDED (not on main) |
| `scripts/ci/tests/test_check_labels.py` | `4c1e2aa9` | `4c1e2aa9` | `4c1e2aa9` | `4c1e2aa9` | identical to main |
| `scripts/ci/tests/test_check_plan_only.py` | `ec93a3c6` | `ec93a3c6` | `ec93a3c6` | `ec93a3c6` | identical to main |
| `scripts/ci/tests/test_check_registries.py` | absent | absent | absent | `46799c01` | ADDED (not on main) |
| `scripts/ci/tests/test_fresh_run_wiring.py` | `9b2192fb` | `9b2192fb` | `9b2192fb` | `9b2192fb` | identical to main |
| `scripts/ci/tests/test_gate_required.py` | `c3c169ef` | `c3c169ef` | `c3c169ef` | `c3c169ef` | identical to main |
| `scripts/ci/tests/test_incident_requirements.py` | `22805bea` | `22805bea` | `22805bea` | `22805bea` | identical to main |
| `scripts/ci/tests/test_merge_eligibility_binding.py` | `7af563ed` | `7af563ed` | `7af563ed` | `7af563ed` | identical to main |
| `scripts/ci/tests/test_module_coverage.py` | `92cd251e` | `e481f054` | `e481f054` | `92cd251e` | CHANGED vs main |
| `scripts/ci/tests/test_portfolio_summary.py` | `8107b4c2` | `8107b4c2` | `8107b4c2` | `8107b4c2` | identical to main |
| `scripts/ci/tests/test_pr32_independence.py` | `00bcc69d` | `00bcc69d` | `00bcc69d` | `00bcc69d` | identical to main |
| `scripts/ci/tests/test_pr33_pin_binding.py` | `44c0104c` | `44c0104c` | `44c0104c` | `44c0104c` | identical to main |
| `scripts/ci/tests/test_provenance_base.py` | `24161846` | `24161846` | `24161846` | `24161846` | identical to main |
| `scripts/ci/tests/test_t16_pin_proposal.py` | absent | absent | absent | `744fdfdc` | ADDED (not on main) |
| `scripts/ci/tests/test_verify_trusted_gate.py` | `1f33d3a8` | `1f33d3a8` | `1f33d3a8` | `1f33d3a8` | identical to main |
| `scripts/ci/user_actions.py` | `22debdae` | `22debdae` | `22debdae` | `22debdae` | identical to main |
| `scripts/ci/verify_trusted_gate.py` | `e3057ccd` | `e3057ccd` | `e3057ccd` | `e3057ccd` | identical to main |

## Evidence references

- #42 package: `acceptance/pin-review/T-16/` on `acceptance/t16-pin-review` @ `9589d891`: README.md, `verification/0-ci-main-8e2df97b-run-41703902441.txt` (main gate failure), `verification/1..5`, `diffs/1..5`, `gate-manifest.PROPOSED-NOT-TRUSTED.json`, SHA256SUMS.
- Current pin: `evidence/acceptance@750de1c694c4912f12bb5bb76a20ba74bc208213:trusted-gate/gate-manifest.json` (gate_sha `ea0c235`, independent_review null).
- Candidate proposal: `coordination/proposed-gate-pin/gate-manifest.json` (hashes from `git show <gate_sha>:<path>` via `verify_trusted_gate.build`; `test_t16_pin_proposal.py` re-derives them from HEAD).
- Superseded proposal: `integration/candidate-20261103b` gate_sha `a518b03` (its test_module_coverage was a comment-only variant `7dba8ea5`).

## Status

PENDING: independent review (AC1, UA-7) of the candidate SHA and pin review of the gate_sha above, then owner approval of the re-pin. Until then the gate reports TRUSTED GATE UNVERIFIED and merge-eligibility is NOT ELIGIBLE.

## Update: PR #42 moved to `8065a44` (committed 17:43 EST)

PR #42's `acceptance/pin-review/T-16/FINAL/` now recommends gate_sha `a518b03e` (the 20261103b gate commit, bound to candidate `caa9ce7`) and marks `6ea6803c` as superseded. That recommendation and this one differ in **one file only**:

| File | a518b03e (#42 FINAL) | 39c71f9 (this proposal) | Note |
|---|---|---|---|
| `scripts/ci/tests/test_module_coverage.py` | `7dba8ea5…` | `92cd251e…` (= current pin `ea0c235`) | Same assertion (`incomplete == []`); differs only in a comment line |

The other 34 files are byte-identical. `a518b03e` is not an ancestor of `integration/candidate-20261103c`, and with `7dba8ea5` it would not match this candidate's tree. For this candidate, the matching pin is `39c71f9eebf8bb72663515a29b52609d02dceea4`. Its delta versus the current pin is the 4 added files only. Suggested follow-up for the Acceptance Integrator: re-point #42's FINAL recommendation to `39c71f9` (relay only; no agent was messaged).
