# Branch rulesets for `main` and `evidence/acceptance`: prepared, NOT active

Status on 2026-11-03 17:05 EST: **prepared only.** No ruleset exists on the repository (`GET /rulesets` returns `[]`)
and no branch protection exists on `main`.

- Creating `main.ruleset.json` with `"enforcement": "evaluate"` was attempted once through the API. GitHub refused it
  with `422 Enforcement evaluate option is not supported on this plan. Please upgrade to Enterprise to enable it.`
  (see `api-attempt-20261103.txt`). The repository is owned by a personal account, so evaluate mode is not available.
- Nothing was activated. `"enforcement": "active"` was not attempted: that would block merges and is the owner's decision.

## Files

| file | what |
|---|---|
| `main.ruleset.json` | `main`: PR required, 1 approval, code-owner review, approval after the last push, stale reviews dismissed, threads resolved, merge-commit only (the integration history depends on normal merges, so linear history is **not** required here), no deletion, no force-push, 32 required status checks (strict / up to date) |
| `evidence-acceptance.ruleset.json` | `evidence/acceptance`: the same PR and review rules, plus **linear history** (append-only records), no deletion, no force-push. No status checks are required because no workflow runs for PRs to this branch (only `Documentation knowledge base`, which tests `main` content) |
| `required-status-checks.main.txt` | the exact check-run names, taken from the real PR #40 runs on `8c662d76`, and where they came from |
| `CODEOWNERS.proposed` | a CODEOWNERS file with a placeholder for a human owner |
| `api-attempt-20261103.txt` | the API response |

Both files set `"bypass_actors": []`. Neither file names the shared agent account `onnxscibroccoli`, or any bot, as a
reviewer, code owner or bypass actor (`tools/acceptance/gate/tests/test_rulesets.py` checks this).

## What the owner needs to do first

1. **Add a human reviewer.** The repository's only collaborator is `onnxscibroccoli` (admin), which is the shared agent
   account that authors every PR. GitHub never counts a PR author's own approval, so with these rules nothing can merge
   until a second human account with write access is invited.
2. Replace the placeholder in `CODEOWNERS.proposed` and commit it as `.github/CODEOWNERS` on both branches, through a reviewed PR.
3. Decide whether `merge-eligibility` should be required right away. It is on the list because it is the gate. It is red
   until T-16 is resolved (`acceptance/pin-review/T-16/README.md`), so requiring it blocks every merge to `main` until then.

## Owner-ready commands (run by the owner, not by an agent)

```bash
R=onnxscibroccoli/bank-it-operations-lab
# Evaluate mode needs GitHub Enterprise. On this plan, use "active" (enforcing) or "disabled" (stored only):
jq '.enforcement="disabled"' acceptance/rulesets/main.ruleset.json > /tmp/main.json   # or "active" once steps 1-3 are done
gh api -X POST repos/$R/rulesets --input /tmp/main.json
jq '.enforcement="disabled"' acceptance/rulesets/evidence-acceptance.ruleset.json > /tmp/ev.json
gh api -X POST repos/$R/rulesets --input /tmp/ev.json
gh api repos/$R/rulesets                                       # list; note the ids
# later, to switch one on:  gh api -X PUT repos/$R/rulesets/<id> -f enforcement=active
# Enterprise only, as written: gh api -X POST repos/$R/rulesets --input acceptance/rulesets/main.ruleset.json
```
