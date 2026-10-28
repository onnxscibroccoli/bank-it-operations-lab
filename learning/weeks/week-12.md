# Week 12: Capstone: an end-to-end evidence review (architecture defense 3 of 3)

**All branches.** Goal: produce *your own* review in the style of `review/pr1-pr2-evidence-audit@fb36341:reports/review-pr1-pr2.md`, covering PRs #4, #5 and #6, which PR #3 did not review.

## Daily exercises
**Day 1: Re-run everything** with the commands in `learning/execution/EXECUTION_LOG.md`. Compare your numbers with E01-E14. Any difference is a finding.

**Day 2: Hash and command checks across bundles.**
```bash
cd $PR5 && (cd evidence/aws/aws-remediation-vpc-rds && sha256sum -c SHA256SUMS --quiet) && echo ok
cd $PR6 && sha256sum -c evidence/orgs/SHA256SUMS --quiet && echo ok
```
- *Observed (E02):* both OK (32 and 66 entries). Note that the two bundles use different path roots, which is a consistency finding.

**Day 3: Synth drift.** Fresh synth versus committed for PR #5 and PR #6. *Observed (E01, E10):* PR #6 has 3 templates, all identical. PR #5 SecureStorage is identical. PR #5 NetworkDatabase differs only by `aws:asset:*` Metadata, because the committed one was synthesized without `--no-asset-metadata`.

**Day 4: Write the review.** Cover scope, method, results per check, honest claims, gaps, and verdicts. Cite paths and lines.

**Day 5: Present it** (15 minutes), then defend it against the interview questions from weeks 10-11.

## Failure injection and recovery
Pick any two injections from weeks 1-9 and show detection and recovery live.

## Answer notes
Findings this guide's own runs surfaced (all reproducible):
1. `scripts/parliament.sh gated` crashes with `JSONDecodeError` when the parliament `pkg_resources` warning is emitted (setuptools 80.10.2), and `PYTHONWARNINGS=ignore` works around it (E12).
2. PR #5 NetworkDatabase template drift is explained by synth flags (E01).
3. No static guard covers RDS `DeletionProtection` (E14).
4. `make_fixtures.py` depends on policy displayName prefixes (E09).

## Fifteen-minute walkthrough
Scope → method → a results table → the top 3 findings → verdicts → what remains unproven.

## Interview questions
1. What makes evidence trustworthy to an auditor who distrusts you?
2. What is the difference between "static evidence" and a deployment record?
3. Which single gap in this lab would you close first, and why?

## PENDING / UNEXECUTED
Consolidated in `learning/execution/PENDING.md`.
