# Integration manifest: candidate-20261103b

Created 2026-11-03 (EST, America/New_York) under owner directive t26u (17:00 EST). **Do not merge into `main`** until AC1 independent review and the gate-pin re-review are both done. This is not an approval. The machine-readable copy is `coordination/INTEGRATION_MANIFEST.json`.

## Candidate

- Branch: `integration/candidate-20261103b`, base `main` `8e2df97b558e69032e52a50ed0adfd311ad04578`
- Gate commit (pinned by the proposal): `a518b03e204d4b77a67e16ed83652acdbdd7b8d5`
- Tested SHA: `308512714690ba20a6d9003fcd0731b88fffd596`

## Source refs and merge bases

| Ref | SHA | Merge base with main |
|---|---|---|
| `main` | `8e2df97b558e69032e52a50ed0adfd311ad04578` | - |
| `integration/completion-20261103` | `3c417d91f97bb806ca48e5eee2e833333b9dff70` | 8c662d76834ecb2de99afebc83d31a2bb0fd3dd1 (PR #40 head; 28 ahead, 1 behind main) |
| `docs-platform (PR #41)` | `d8d77119ea7a82e326c17a6db4273bc5fa0cc5c3` | 30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6 (1 ahead, 26 behind) |
| `reports/completion-pass-20261103 (PR #39)` | `42d8e962c7e71bc48295d4472c538337264bd84e` | 30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6 (3 ahead, 26 behind) |
| `evidence/acceptance (current pin ea0c235, not changed)` | `750de1c694c4912f12bb5bb76a20ba74bc208213` | none (orphan evidence branch) |

## Overlap (relative to main 8e2df97)

| File(s) | Completion branch | PR #39 | PR #41 | Already on main |
|---|---|---|---|---|
| docs/metadata/pages.json | yes | yes (+1 entry) | yes (rewrites ~100 entries, +9) | #40 entries |
| coordination/modules.json | yes (review-notes, acceptance steps, knowledge-base) | yes (final-report paths) | no | #40 acceptance INTEGRATED |
| scripts/ci/tests/test_module_coverage.py | yes | no | no | #40 one-line change |
| docs/metadata/preserved-records.json | yes | no | no | - |
| scripts/validate-all.sh, coordination/tasks.json, reports/review-*.md, reports/independent/** | yes | no | no | no |
| README.md, docs/knowledge/**, scripts/docs/**, learning/CURRENT.md, docs/adr/STATUS.md, docs/metadata/terminology.json | no | no | yes | no |
| reports/COMPLETION_PASS_2026-11-03.* | no | yes | no | no |

## What was taken

| Source | Taken | How |
|---|---|---|
| main 8e2df97 | base: everything, including PR #40 acceptance framework (tools/acceptance/gate, acceptance/INTEGRATION-V2.md) | branch point |
| review PR heads #14 eb8d259, #27 72aa8b7, #28 fe6f24e, #29 384c610, #30 eb82d7d, #31 eccac83, #32 c795ce6, #33 9612a7b, #34 2a07e33 | 10 review/plan record files, verbatim | ordinary --no-ff merge of each head (ancestry kept; not approvals) |
| PR #41 docs-platform d8d7711 (DRAFT, owner review requested) | all 25 files (docs/knowledge sections, Pages dot-directory 404 fix, builder/search/a11y tests) | ordinary merge; pages.json 3-way merged by key |
| PR #39 reports/completion-pass-20261103 42d8e96 (DRAFT, owner review requested) | reports/COMPLETION_PASS_2026-11-03.md + .json, final-report paths, pages entry | ordinary merge, no conflict |
| integration/completion-20261103 3c417d9 (NOT merged wholesale) | re-applied by hand against main: review-notes registry entry, 10 pages.json review entries (re-pointed to this branch), validate-all acceptance/review steps (#40 had not added them), test_module_coverage [] expectation | content re-authored; old branch kept as history |
| this candidate (defect fix) | scenarios/incident/run_incident_demo.sh restore_pg_start: up to 10 start attempts after the immediate stop (integration-gate run 41728133126 on 290dd7b: 'could not bind 127.0.0.1:55432: Address already in use'). Runbook action unchanged; attempts are logged in the step log. | new commit; incident-demo owner (Portfolio Cases) to review |
| this candidate (defect fix) | scripts/docs/tests/browser.mjs (from PR #41): header-search check waited with a non-null-safe predicate that could run on the old page mid-navigation (Documentation run 41729590108: 'Cannot read properties of null'). Now waits for the URL change and uses a null-safe predicate. Local: 3/3 browser runs pass. | new commit; PR #41 owner to review |
| this candidate (new) | check_registries.py + tests (R1-R5), tasks.json reconciled{} records, UA-2 citation fix, T-11 docs-workflow SHA pins + test_actions_pinned.py, T-16 test_t16_pin_proposal.py, UNREVIEWED pin proposal, this manifest | new commits |

## Not taken

| Item | Why |
|---|---|
| integration/completion-20261103: COMPLETION_INVENTORY.md / completion-inventory.json | superseded by this manifest; kept on the old branch as history (its T-28 'merge into main' plan is superseded by directive t26u) |
| integration/completion-20261103: its own merges of PR #26/#25 and its acceptance.yml/run.sh edits | main already has the authoritative PR #40 versions |
| integration/completion-20261103: tasks.json rule text 'owner may merge' (13:21 EST) | superseded by t26u; recorded as a dated rule instead |
| evidence/acceptance re-pin | not applied: pin re-review is unmet; proposal kept at coordination/proposed-gate-pin/gate-manifest.json (independent_review null, review_status UNREVIEWED) |

## Conflict resolutions

| File | Between | Resolution | Authority |
|---|---|---|---|
| `docs/metadata/pages.json` | candidate (main + review merges) vs PR #41 | 3-way merge by key against merge base: 0 keys changed on both sides; union of 6 main-only (#40 acceptance docs) + 9 #41-only entries; then 10 review-record entries added | each side for its own keys |
| `coordination/modules.json` | PR #39 (final-report paths) vs completion branch (review-notes, knowledge-base, acceptance) | #39 merged as-is; completion-branch changes re-applied on top by hand; knowledge-base limitation rewritten to include #41 and Pages state | #39 for final-report paths; registry owner (integration) for the rest |
| `scripts/ci/tests/test_module_coverage.py` | main/#40 (expects review-notes NOT_INTEGRATED) vs completion branch (expects []) | [] (review-notes is INTEGRATED here) | registry state of this candidate |
| `scripts/validate-all.sh` | completion branch steps vs main | steps re-added with PR #40 paths (tools/acceptance/gate) plus registry reconciliation step | PR #40 for acceptance paths |
| `coordination/tasks.json` | historical statuses (2026-10-28) vs current module states | original status values kept; reconciled{} added for PR #6, #14, #26, #27 | modules.json for current state; tasks.json entries are history |

## Registry status

- modules: 28 (27 INTEGRATED, 1 SUPERSEDED); check_modules.py OK
- reconciliation: check_registries.py R1-R5 CONSISTENT (4 reconciled{} records: PR #6, #14, #26, #27)
- pages: one entry per tracked Markdown file; 10 review records Archived and frozen

## Gate pin

- Current pin: `ea0c235` (evidence/acceptance `750de1c`). It has no independent review and no longer matches `main` `8e2df97` (main integration-gate run 41703902441).
- Proposed pin: `coordination/proposed-gate-pin/gate-manifest.json`, gate_sha `a518b03e204d4b77a67e16ed83652acdbdd7b8d5`. Its review_status is **UNREVIEWED**, independent_review is null, and it is **not applied**.
- T-16 decision: merge-eligibility keeps failing closed on pushes to `main`. Fail-closed negative tests are in `scripts/ci/tests/test_t16_pin_proposal.py`.

## Checks and runs

| Workflow | Run | Result |
|---|---|---|
| acceptance | https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731058945 | success |
| integration-gate | https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731062507 | failure (merge-eligibility only, by design: GATE HASHES REJECTED vs pin ea0c235 because the a518b03 proposal is UNREVIEWED and unapplied; all 18 other jobs success) |
| offline-validation | https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731065623 | success |
| aws-cdk | https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731069473 | success |
| postgres-restore-evidence | https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731073799 | success |
| portfolio-validation | https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731076403 | success |
| Documentation knowledge base (deploy=false) | https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731137053 | success |
| local validate-all.sh with PostgreSQL 16 (box) | https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/None | PASS (54 steps) |

## Reviews required before main

- AC1: independent reviewer approves the exact candidate SHA (UA-7)
- gate-pin re-review of the proposed gate_sha, then apply the pin to evidence/acceptance
- owner review of included draft PRs #39 and #41 content
