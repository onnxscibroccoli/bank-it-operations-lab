# Week 8: Incident review: a CI failure and false passes (resilience and incidents 2 of 3)

**Branches:** `$PR2` (`ci-evidence-postgres@e610015`), `$PR3` (`review/pr1-pr2-evidence-audit@fb36341`).
**Delivered files used:** `evidence/postgres/runs/ci-service-40630856041-1/{NOTE.md,COMMANDS.tsv,logs/}`, commit `e610015` message,
`tests/integration/postgres/run_restore_scenario.sh` (lines 104-111 and 140-146), `reports/review-pr1-pr2.md` §2 and §5,
`evidence/shared/{validate_evidence.py,negative-expectations.postgres.json}`.

## The incident (from delivered evidence)
- **What happened.** Run 40630856041 failed. pg_dump 18.6 (ubuntu-latest runner) against a `postgres:16` service: pg_dump 18 emits `SET transaction_timeout = 0;`, which PG 16 rejects (`NOTE.md`).
- **Fix.** `e610015`: service image changed to `postgres:18`, plus a `client_server_major_match` setup step.
- **Second finding (PR #3).** In that failing run, N01, N04, N05 and N06 were recorded as PASS, but they failed for unrelated reasons (`transaction_timeout`, missing relation).
  `NOTE.md:4` ("Negative tests behaved as expected") is therefore inaccurate.

## Daily exercises
**Day 1: Timeline.** Build it from `NOTE.md`, `git log origin/ci-evidence-postgres`, and PR #3 §2. Separate detection, diagnosis, fix and verification.

**Day 2: Reproduce the false-pass detection.**
```bash
cd $PR2 && python3 $PR3/evidence/shared/validate_evidence.py postgres-negatives evidence/postgres/runs/ci-service-40630856041-1; echo rc=$?
```
- *Observed (E13):* 4 × `ERROR FALSE-PASS` (N01, N04, N05, N06) and `INVALID (4 errors, 0 warnings)`.

**Day 3: Root cause in code.** Read lines 140-146 at `e610015`. N01, N05 and N06 chain setup with `&&` inside one `bash -c`, so any setup failure counts as "expected failure".
Write (in your notes, not in the repo) a fix that runs setup as separate `setup` steps and asserts the error text.

**Day 4: Version-skew guard.** Read `client_server_major_match`. PR #3 §5 notes that `cut -c1-2` on `server_version_num` is wrong for servers below 10. Explain why.

**Day 5: Write a post-incident review** using the template below and cite file paths only.

## Failure injection and recovery
- Re-run the shared checker on the **passing** offline run (expected OK) and the **failing** CI run (expected 4 FALSE-PASS). Executed: E13.
- In a scratch copy of the offline run (`cp -r evidence/postgres/runs/local-offline-20261028T041038Z /tmp/pgneg`), change `does not exist` to `is missing` in `logs/*N03*`, then re-run `postgres-negatives /tmp/pgneg`.
  *Observed (E13):* `ERROR FALSE-PASS N03_restore_missing_database …` and `INVALID (1 errors, 0 warnings)`, exit 1. *Recovery:* delete the copy.

## Post-incident review template
Summary · Impact (lab: CI red, misleading evidence) · Timeline · Root causes (version skew; test-design defect) · What went well (failure evidence preserved, `if: always()` upload) ·
What went wrong (inaccurate NOTE.md; passing service run not committed) · Actions (PR #3 recommendations 3-6) · Evidence links.

## Answer notes
- Preserving the failing run's evidence is what made the false-pass finding possible.
- "Exit code non-zero" is not the same as "failed for the intended reason".

## Architecture tradeoffs
- Floating runner images (`ubuntu-latest`) versus pinned images: floating ones bring surprise skew (Ubuntu 26.04 → pg_dump 18), and pinned ones bring update debt.
- Independent reviewer branch (PR #3) versus self-review: PR #3 was read-only on the PR branches and found issues that the authors' own evidence hid.

## Fifteen-minute walkthrough
Failing run → NOTE.md claim → `postgres-negatives` output → code lines → fix and the remaining recommendations.

## Interview questions
1. How do you prevent "expected failure" tests from hiding real failures?
2. What evidence would you keep from a failed pipeline, and for how long?
3. How do you handle a teammate's inaccurate incident note?

## PENDING / UNEXECUTED
- The PR #3 recommendations are **not implemented** on PR #2 at `e610015`.
