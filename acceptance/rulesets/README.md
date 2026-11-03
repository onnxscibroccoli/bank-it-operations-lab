# Branch rulesets for `main` and `evidence/acceptance`: staged rollout, prepared, NOT active

Status on 2026-11-03, about 17:50 EST: **prepared only, nothing activated.**

- The repository has no rulesets (`GET /rulesets` returns `[]`) and `main` has no branch protection.
- Evaluate mode is not available. One earlier attempt was refused with
  `422 Enforcement evaluate option is not supported on this plan. Please upgrade to Enterprise` (`api-attempt-20261103.txt`;
  that attempt used an earlier, unstaged file that is now replaced). It will not be retried.
- Every file here has `"enforcement": "disabled"` and `"bypass_actors": []`. None of them names the shared agent account
  `onnxscibroccoli`, or any bot, as a reviewer, code owner or bypass actor (`tools/acceptance/gate/tests/test_rulesets.py`).

## Why staged

The repository's only collaborator is `onnxscibroccoli`, the shared agent account. It authors every PR, and GitHub never
counts an author's own approval. Turning on a required review or code-owner review now would leave **no valid way to
update** `main` or `evidence/acceptance`. `merge-eligibility` is red until T-16 is closed (`../pin-review/T-16/`), so
requiring it now would also block every merge. Each stage below always leaves a working update path.

| stage | when | `main` | `evidence/acceptance` | update path that still works |
|---|---|---|---|---|
| **0** (safe now) | any time | `stage0-main.ruleset.json`: no deletion, no force-push, **31** required checks (all real check names except `merge-eligibility`), strict (up to date) | `stage0-evidence-acceptance.ruleset.json`: no deletion, no force-push, linear history | main: open a PR, wait for the 31 checks to pass, merge it (no approval required). evidence: fast-forward pushes as today |
| **1** | after a human reviewer (not the shared account, not a bot) is invited with write access **and** `.github/CODEOWNERS` naming them is committed to both branches (`CODEOWNERS.proposed`) | `stage1-main.ruleset.json`: stage 0 plus a PR with 1 approval, code-owner review, approval after the last push, stale reviews dismissed, threads resolved, merge commits only | `stage1-evidence-acceptance.ruleset.json`: stage 0 plus the same PR rule, rebase or squash only | a PR approved by the human reviewer |
| **2** | after T-16 is closed: the reviewer is on `reviewer_allowlist`, a reviewed pin is installed, and `merge-eligibility` is green on `main` | `stage2-main.ruleset.json`: stage 1 plus `merge-eligibility` (all 32 checks) | unchanged from stage 1 (no workflow runs for PRs to this branch) | a PR that is approved and merge-eligible |

Notes:
- Linear history is not required on `main`, because the integration history relies on merge commits. It is required on
  `evidence/acceptance`, which already has a linear history (0 merges in 12 commits).
- In stage 0 the strict policy means a PR has to be up to date with `main` before merging. When `main` moves, the
  checks re-run (the acceptance job takes about 20 minutes).
- Moving between stages means replacing the previous stage's ruleset, not stacking them, so `PUT` the new rules into the same ruleset id.
- `required-status-checks.main.txt` lists the exact names (from the real PR #40 runs on `8c662d76`) and where they came from.

## Owner-ready commands (run by the owner, not by an agent)

```bash
R=onnxscibroccoli/bank-it-operations-lab
# Stage 0: store, inspect, then switch on
gh api -X POST repos/$R/rulesets --input acceptance/rulesets/stage0-main.ruleset.json                 # created disabled
gh api -X POST repos/$R/rulesets --input acceptance/rulesets/stage0-evidence-acceptance.ruleset.json  # created disabled
gh api repos/$R/rulesets --jq '.[] | "\(.id) \(.name) \(.enforcement)"'
gh api -X PUT repos/$R/rulesets/<main-id> -f enforcement=active
gh api -X PUT repos/$R/rulesets/<evidence-id> -f enforcement=active
# Stage 1 (after a human reviewer and CODEOWNERS exist): replace the rules, keeping each id
jq '.enforcement="active"' acceptance/rulesets/stage1-main.ruleset.json | gh api -X PUT repos/$R/rulesets/<main-id> --input -
jq '.enforcement="active"' acceptance/rulesets/stage1-evidence-acceptance.ruleset.json | gh api -X PUT repos/$R/rulesets/<evidence-id> --input -
# Stage 2 (after T-16 is closed and merge-eligibility is green on main)
jq '.enforcement="active"' acceptance/rulesets/stage2-main.ruleset.json | gh api -X PUT repos/$R/rulesets/<main-id> --input -
# Roll back any stage: gh api -X PUT repos/$R/rulesets/<id> -f enforcement=disabled
```
