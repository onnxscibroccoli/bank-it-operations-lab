# 0011: Integrate on a separate branch; merge only exact head SHAs that pass gates G1-G9
- Status: **Proposed.** #7 and #11 are open drafts. No PR has a human review (G1 unmet for all of them).
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- Module PRs are combined on `overnight/integration@49122f2` and never pushed directly to `main`. `reports/INTEGRATION.md` records each PR's disposition: #3, #5, #4 and #2 integrated in that order, #1 superseded by #5, #6 awaiting changes.
- A single entry point, `scripts/validate-all.sh`, runs every check: `--python-only` gives 20 steps, and the full run (with Node and `PG_BIN`) gives 32. CI runs it through `.github/workflows/offline-validation.yml` and `.github/workflows/aws-cdk.yml`.
- Merge policy (`reports/final-report@54d6fbd:reports/USER_ACTIONS_REQUIRED.md`): a PR merges only when G1-G7 hold for its **exact head SHA**, and G8 (no false-pass tests) and G9 (no superseded unsafe code) also hold.
- #7's acceptance conditions AC1-AC5 are recorded in `reports/INTEGRATION.md`. AC1 is unmet because there is no human review.

## Consequences
- Interface defects between PRs show up at integration time. The `postgres-negatives` checker passed vacuously on v2 and was fixed in `05941a9` (learning/execution R03).
- The integration branch has to be re-validated every time a source PR moves (#2 was re-merged at `e7399fb` in `e76d8a4`).
- AC3 is recorded as MET for `afb41278`, with 8/8 CI jobs passing. `49122f2` is a docs-only head on top of it, and its own CI is also 8/8 green (R14).
- #11 asks for #7's AC5 ("no known weakening") to be corrected, because #14's B5-2 exists in the integrated #5 code.
- Verified here: `validate-all.sh` gave PASS for 20 steps and PASS for 32 steps (R04, R05).
