# Week 5: Identity evidence, staged rollout and regression fixtures (identity and governance 2 of 3)

**Branch:** `$PR4` = `entra-ca-offline@d302c99`.
**Delivered files used:** `evidence/entra/{README.md,generate_evidence.py}`, `evidence/entra/runs/local-offline-20261028T150359Z/`, `tests/entra/make_fixtures.py`, `tests/entra/fixtures/INDEX.json`.

## Daily exercises
**Day 1: Verify committed evidence.** `python3 evidence/entra/generate_evidence.py --verify evidence/entra/runs/local-offline-20261028T150359Z`
- *Expected:* `verify … OK`, exit 0. (Executed: E09.)

**Day 2: Read SUMMARY.json.** Find `git.commitSha`, `inputHashes`, and the expected vs actual exit code per fixture. Explain why the evidence
is committed *on top of* the validated commit (`evidence/entra/README.md`).

**Day 3: Fixture design.** Read `INDEX.json`. There are 37 fixtures: 1 `valid-`, 17 `neg-` and 19 `malformed-`. Each fixture is one targeted mutation from
`identity/entra/policies/` (`make_fixtures.py`). Pick three and predict the failing rule before you run them.

**Day 4: Staged rollout.** CA005/CA006 are report-only. Use `riskPoliciesMustBeReportOnly` and BASE-007 to explain how the lab models a staged rollout.
Run `neg-risk-enforced.json`. *Observed (E09):* exit 1, BASE-007 FAIL.

**Day 5: Generate a fresh run (scratch clone only).** `generate_evidence.py` writes a new `runs/local-offline-<UTC>/` directory and expects a clean, committed tree.
Do this in a throwaway clone, not in your main worktree.

## Failure injection and recovery
Do both in a scratch copy: `mkdir /tmp/e && cp -r identity tests evidence /tmp/e/ && cd /tmp/e`.
- **Fixture drift.** Change the first `"enabled"` to `"disabled"` in `tests/entra/fixtures/neg-missing-mfa.json`, then run `python3 tests/entra/make_fixtures.py --check`.
  *Observed (E09):* `fixture drift: ['neg-missing-mfa.json']`, exit 1. *Recovery:* `python3 tests/entra/make_fixtures.py` regenerates the fixtures, and `--check` then exits 0.
- **Input changed after evidence.** Edit `identity/entra/policies/CA001-*.json` (for example the displayName), then run `python3 evidence/entra/generate_evidence.py --verify evidence/entra/runs/local-offline-20261028T150359Z`.
  *Observed (E09):* `input changed since evidence run: identity/entra/policies/CA001-…json` and `FAIL (1)`, exit 1.
  Side effect: `make_fixtures.py` then crashes with `KeyError: 'CA001'`, because it locates policies by displayName prefix. That is a real coupling worth discussing.
  *Recovery:* restore the file, then `--verify` returns OK.

## Answer notes
- Hashing the validator, the tests *and* the fixtures into SUMMARY.json ties a PASS to exact code, which is stronger than PR #1's approach (PR #3 §1).
- Generating fixtures by mutation keeps the negatives in sync with the baseline as the baseline evolves.

## Architecture tradeoffs
- Committing evidence next to code makes it reviewable, but it adds churn and invites hand-edits. Hashes plus `--verify` mitigate this.
- Report-only first reduces lockout risk but delays enforcement. The flag makes the decision explicit and testable.

## Fifteen-minute walkthrough
`--verify` OK → SUMMARY.json anatomy → INDEX.json taxonomy → BASE-007 and staged rollout.

## Interview questions
1. How do you prove a validator PASS came from a specific code version?
2. What are the risks of generated negative fixtures?
3. How would you move CA005 from report-only to enforced, and what evidence would you require first?

## PENDING / UNEXECUTED
- P-W5: Day 5 fresh-run generation (`generate_evidence.py` without `--verify`) was not executed while writing this guide.
