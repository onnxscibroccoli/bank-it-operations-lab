# PR dispositions (audit against main only)

Prepared 2026-11-03 (EST, America/New_York) on integration/candidate-20261103c under owner directives t28u/t29u, audited against **main `8e2df97b558e69032e52a50ed0adfd311ad04578`** only (an unmerged candidate does not count). Method: `/workspace/audit/audit.py` compared every file in each PR (merge base with its base branch .. head) against main: byte-identical blob (IDENTICAL), every added line present in main's file (HUNKS_PRESENT), absent (MISSING_ON_MAIN), otherwise DIFFERS. Head-is-ancestor-of-main was also checked. **No PR was closed or commented on in this pass, and no branch was deleted.**

## In scope (t29u: #11, #15, #23-#26)

| PR | Disposition | Action | Evidence |
|---|---|---|---|
| #11 | NOT INTEGRATED | LEAVE OPEN | 6 of 7 files differ from main: reports/FINAL_REPORT.md, USER_ACTIONS_REQUIRED.md, user-actions.json, README.md and docs/DEMO_WALKTHROUGH_15MIN.md were rewritten on main by later delivery commits (aec7e5f, 3d2e920, 29d618f), but no PR is recorded as replacing #11 itself. reports/MODULE_REQUIREMENT_MAP.md (commit 9ce8b37) is not on main at all. Unique material remains on branch reports/final-report @ d500ccf (not deleted). Ambiguous, so not closable: the Final Report worker must decide whether MODULE_REQUIREMENT_MAP.md is superseded or still needs integrating. |
| #15 | INTEGRATED | CLOSE PROPOSED (needs Ian's explicit go-ahead; not closed) | All 39 files are byte-identical on main 8e2df97, and the branch has no unique material. Branch learning-guide @ 39728db stays. |
| #23 | INTEGRATED | HOLD (Acceptance Integrator; do not close yet) | Head 6a28847 is an ancestor of main 8e2df97, and all 77 files are byte-identical on main. Landed via PR #26 (merged 2026-11-03 14:30 EST, 1c683275) and PR #40 (8e2df97). |
| #24 | INTEGRATED | HOLD (Acceptance Integrator; do not close yet) | Head 838d537 is an ancestor of main, and all 5 files are byte-identical on main. Landed via PR #26 / #40. |
| #25 | INTEGRATED + INTENTIONALLY REPLACED (2 lines) | HOLD (Acceptance Integrator; do not close yet) | Head ce39504 is an ancestor of main. 13 files are identical and 1 is hunk-equivalent. In acceptance/modules/contract.py, 2 added lines (the module-status aggregation) were replaced on main by 93de4b3 'integration fix (C): module status is NOT_EXECUTED when any check is NOT_EXECUTED' (ACC-C-01..03). Landed via PR #26 / #40. |
| #26 | MERGED | none | Merged 2026-11-03 14:30 EST (19:30:33Z) as 1c683275; already closed. |

## Other open PRs (t28u list; recorded only)

| PR | Disposition | Action | Evidence |
|---|---|---|---|
| #6 | NOT INTEGRATED (security) | LEAVE OPEN | 31 files missing on main (evidence/orgs/** run bundle) and 9 differing (infra/orgs/lib, tests). orgs-security is INTEGRATED in modules.json from later fixes (B6-1/B6-2), but #6's own evidence is not on main. Security PR: not closable. |
| #8 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head 7010d05: IDENTICAL 7. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #9 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head d6efb82: HUNKS_PRESENT 8, IDENTICAL 64. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #10 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head 3e40e39: HUNKS_PRESENT 1, IDENTICAL 79. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #12 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head 31b69db: HUNKS_PRESENT 1. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #13 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head 9dc8f1f: HUNKS_PRESENT 11, IDENTICAL 1. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #16 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head 3f82697: HUNKS_PRESENT 1, IDENTICAL 7. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #17 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head 5605b78: HUNKS_PRESENT 7, IDENTICAL 210. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #18 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head f48e7e3: HUNKS_PRESENT 8, IDENTICAL 100. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #19 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head 3397dac: HUNKS_PRESENT 12, IDENTICAL 2. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |
| #21 | INTEGRATED (identical or equivalent; not reviewed for closure under t29u) | LEAVE OPEN (outside t29u scope) | head 10da54f: IDENTICAL 73. HUNKS_PRESENT means every line the PR adds is on main, and main adds later edits. |

Required-review PRs stay open: #14, #27-#34 (review records), #39, #41, #42.

## Draft audit comment for #15 (not posted)

> Disposition audit (integration/candidate-20261103c, 2026-11-03 EST): all 39 files of this PR (learning-guide @ 39728db) are byte-identical on main 8e2df97b558e69032e52a50ed0adfd311ad04578 (module learning-guide INTEGRATED in coordination/modules.json). No unique material remains; branch `learning-guide` is kept. Closing as INTEGRATED. Evidence: coordination/PR_DISPOSITIONS.md on integration/candidate-20261103c.

