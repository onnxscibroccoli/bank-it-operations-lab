workflow_lint - GitHub Actions workflow security checks (T-11)

check_workflows.py   Static checker for .github/workflows/*.yml (rules listed in its docstring). Exit 1 on any finding.
resolve_lock.py      generate: resolve exact version tags to commit SHAs via `gh api` (annotated tags dereferenced,
                     commit confirmed via repos/<owner>/<repo>/commits/<sha>) and write ACTIONS_LOCK.tsv.
                     verify: re-resolve every lock row online; fails if an exact tag no longer points at the pinned SHA.
selftest.sh          Negative self-test: fixtures/bad must produce exactly fixtures/bad/EXPECTED.tsv, fixtures/good
                     must pass, an unverified lock row and a mutated copy of the real workflows must fail.
requirements.txt     PyYAML 6.0.3, installed with pip --require-hashes.

Policy files (in .github/workflows/):
  ACTIONS_LOCK.tsv      verified pins: action, version, sha, also_tags (floating tags at the same commit), verified_at.
                        A `uses:` comment must be `# <version>` or one of also_tags (e.g. `# v5.1.0` or `# v5`).
  WORKFLOW_POLICY.json  job-level write scopes that are allowed, each with a reason.

To pin a new action:  python3 tests/integration/workflow_lint/resolve_lock.py generate /tmp/new.tsv owner/repo@vX.Y.Z
then merge the verified row into ACTIONS_LOCK.tsv and write `uses: owner/repo@<sha> # vX.Y.Z`. Never type a SHA by hand.
