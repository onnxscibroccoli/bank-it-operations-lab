# Integration manifest: candidate-20261103c

Created 2026-11-03 (EST, America/New_York) under owner directive t27u (17:35 EST, continuing t26u). **Do not merge into `main`** until AC1 independent review and the gate-pin re-review are both done. This is not an approval. The machine-readable copy is `coordination/INTEGRATION_MANIFEST.json`.

## Candidate

- Branch: `integration/candidate-20261103c`, base `main` `8e2df97b558e69032e52a50ed0adfd311ad04578`
- Gate commit (pinned by the proposal): `39c71f9eebf8bb72663515a29b52609d02dceea4`
- Tested SHA: `see report (head of this branch at test time)`

## Source refs and merge bases

| Ref | SHA | Merge base with main |
|---|---|---|
| `main` | `8e2df97b558e69032e52a50ed0adfd311ad04578` | - |
| `reports/completion-pass-20261103 (PR #39 @ b6e23ba per t27u; head moved to 0ee1e97 at 17:39 EST, DRAFT)` | `0ee1e97b9b87ad15678f92987e5efbde3cac6687` | 8e2df97 = main (6 ahead at 0ee1e97; main merged in by 9462c5b, not rebased) |
| `acceptance/t16-pin-review (PR #42, not merged; compared only)` | `9589d891` | 8e2df97 = main |
| `docs-platform (PR #41 @ 70535c5, DRAFT)` | `70535c5c81c10696f177de1eb05a9933146f5bf2` | 8e2df97 = main (3 ahead, 0 behind; main merged in by fea62ec, not rebased) |
| `integration/candidate-20261103b (previous candidate, not merged)` | `caa9ce7c1b1538d8da920463db77c93c05fe882b` | 8e2df97 = main |
| `integration/completion-20261103 (history, not merged)` | `3c417d91f97bb806ca48e5eee2e833333b9dff70` | 8c662d76834ecb2de99afebc83d31a2bb0fd3dd1 |
| `evidence/acceptance (current pin ea0c235, not changed)` | `750de1c694c4912f12bb5bb76a20ba74bc208213` | none (orphan evidence branch) |

## Overlap (relative to main 8e2df97)

| File(s) | Carried from 20261103b | PR #39 | PR #41 | Already on main |
|---|---|---|---|---|
| docs/metadata/pages.json | yes (11 keys) | yes (+2 keys) | yes (5 changed, +9) | 229 keys incl. #40 |
| coordination/modules.json | yes | yes (+3 final-report paths) | no | #40 acceptance INTEGRATED |
| scripts/docs/tests/browser.mjs | yes (navigation fix) | no | yes | older version |
| README.md, docs/knowledge/**, scripts/docs/** (other), learning/CURRENT.md, docs/adr/STATUS.md, terminology.json | no | no | yes | no |
| reports/COMPLETION_PASS_2026-11-03.*, HUMAN_DECISION_PACKET_2026-11-03.md | no | yes | no | no |
| scripts/ci/**, validate-all.sh, documentation.yml, tasks.json, preserved-records.json, scenarios/incident, reports/review-*, reports/independent/** | yes | no | no | no |

## What was taken

| Source | Taken | How |
|---|---|---|
| main 8e2df97 | base: everything, including PR #40 acceptance framework | branch point |
| PR #41 docs-platform @ 70535c5 (DRAFT, owner review requested) | all 25 files (knowledge-base sections, Pages dot-directory fix, builder/search/a11y tests, ADR status, learning page) | ordinary --no-ff merge FIRST (it owns the docs builder and pages.json schema that #39's entries must satisfy); clean |
| PR #39 reports/completion-pass-20261103 @ b6e23ba (DRAFT, owner review requested) | reports/COMPLETION_PASS_2026-11-03.md, completion-pass-2026-11-03.json, HUMAN_DECISION_PACKET_2026-11-03.md, final-report paths in modules.json, 2 pages.json entries | ordinary --no-ff merge SECOND (b6e23ba); clean. Then an ordinary merge of the drift b6e23ba..0ee1e97 (Ian, 17:39 EST: decision packet split A/B, completion report refresh; pages.json changed only #39's own 2 keys); clean |
| review PR heads #14 eb8d259, #27 72aa8b7, #28 fe6f24e, #29 384c610, #30 eb82d7d, #31 eccac83, #32 c795ce6, #33 9612a7b, #34 2a07e33 (heads unchanged since 20261103b) | 10 review/plan record files, verbatim | ordinary --no-ff merge of each head; not approvals |
| integration/candidate-20261103b @ caa9ce7 (carried forward, not merged) | scripts/ci/check_registries.py + test_check_registries.py, test_actions_pinned.py (T-11), test_t16_pin_proposal.py (T-16), test_module_coverage.py [] expectation, documentation.yml SHA pins + integration/** push trigger, validate-all.sh registry/acceptance/review steps, tasks.json reconciled{} records, modules.json (review-notes INTEGRATED, UA-2 fix, UA-3/6/7 limitation, acceptance validate_all_steps), preserved-records.json review hashes, 11 pages.json entries (10 archived reviews + this manifest), incident restart retry (scenarios/incident/run_incident_demo.sh, owner Portfolio Cases), docs browser navigation fix (scripts/docs/tests/browser.mjs, owner PR #41 / docs-platform) | files checked out from caa9ce7 where 20261103b was the only changer; modules.json re-applied with #39's new HUMAN_DECISION_PACKET path; pages.json entries added by key |
| gate decision (this candidate) | scripts/ci/tests/test_module_coverage.py set to the exact bytes of the CURRENT pin ea0c235 (sha256 92cd251e..., asserts incomplete == []) instead of 20261103b's comment-only variant (7dba8ea5...) | new commit; trust delta vs current pin is then only 4 added files (see coordination/T16_RECONCILIATION.md) |
| PR #41 @ 70535c5 per-file decisions | scripts/docs/tests/browser.mjs: CANDIDATE fix kept (70535c5 still has the non-null-safe predicate that failed Documentation run 41729590108; fix verified 3/3 locally and in run 41731137053). docs/metadata/pages.json: candidate is a strict superset of 70535c5 (all #41 keys byte-equal; +#39 keys, +10 review records, +3 coordination pages). Every other #41 file byte-identical to 70535c5 | recorded decision; owner of browser.mjs: docs-platform / PR #41 |
| this candidate (new) | coordination/T16_RECONCILIATION.md (PR #42 vs candidate pin), coordination/PR_DISPOSITIONS.md + tasks.json pr_dispositions (audit vs main; nothing closed) | new commit |
| this candidate (new) | UNREVIEWED gate-pin proposal re-pointed to this branch's gate commit (hashes identical to the a518b03 proposal), this manifest, tasks.json t27u rule + candidate_checkpoint | new commits |

## Not taken

| Item | Why |
|---|---|
| PR #41 d8d7711 / PR #39 42d8e96 as merged on 20261103b | superseded by the new heads 70535c5 / b6e23ba (each merged main in) |
| 20261103b proposed pin (gate_sha a518b03) | superseded by the proposal on this branch's gate commit; identical file hashes |
| 20261103b INTEGRATION_MANIFEST content | superseded by this manifest; kept on that branch as history |
| evidence/acceptance re-pin | not applied (t27u: do not apply the proposed pin; pin re-review unmet) |

## Conflict resolutions

| File | Between | Resolution | Authority |
|---|---|---|---|
| `docs/metadata/pages.json` | PR #41 @ 70535c5 vs PR #39 @ b6e23ba (both based on main 8e2df97) | git merge clean; verified equal to a key-by-key union. Keys changed by BOTH: none. #41: 5 changed (docs/knowledge/ai.md, development.md, glossary.md, publishing.md, start.md), 9 added (docs/adr/STATUS.md, docs/knowledge/accessibility.md, gaps.md, lifecycle.md, reference.md, topics.md, troubleshooting.md, tutorials.md, learning/CURRENT.md). #39: 2 added (reports/COMPLETION_PASS_2026-11-03.md, reports/HUMAN_DECISION_PACKET_2026-11-03.md). Then 11 integration keys added (10 Archived review records, coordination/INTEGRATION_MANIFEST.md). 229 main -> 251 keys. | each PR for its own keys; integration for review/manifest keys |
| `coordination/modules.json` | PR #39 (final-report +3 paths) vs 20261103b carry-forward | 20261103b version + #39's reports/HUMAN_DECISION_PACKET_2026-11-03.md path; knowledge-base limitation re-pointed to #41 70535c5 | #39 for final-report paths; integration for registry state |
| `other shared files` | #39 vs #41 | none: #39 touches only modules.json, pages.json and 3 new reports; #41 does not touch modules.json | - |

## Registry status

- modules: 28 (27 INTEGRATED, 1 SUPERSEDED); check_modules.py OK
- reconciliation: check_registries.py R1-R5 CONSISTENT (4 reconciled{} records: PR #6, #14, #26, #27)
- pages: one entry per tracked Markdown file; 10 review records Archived and frozen; 251 keys

## Gate pin

- Current pin: `ea0c235` (evidence/acceptance `750de1c`). It has no independent review and no longer matches `main` `8e2df97` (main integration-gate run 41703902441).
- Proposed pin: `coordination/proposed-gate-pin/gate-manifest.json`, gate_sha `39c71f9eebf8bb72663515a29b52609d02dceea4`. Its review_status is **UNREVIEWED**, independent_review is null, and it is **not applied**.
- T-16 decision: merge-eligibility keeps failing closed on pushes to `main`. Fail-closed negative tests are in `scripts/ci/tests/test_t16_pin_proposal.py`.

## Checks and runs

The runs are recorded in a later records-only commit.

## Reviews required before main

- PENDING - AC1: independent reviewer approves the exact candidate SHA (UA-7)
- gate-pin re-review of the proposed gate_sha, then apply the pin to evidence/acceptance
- owner review of included draft PRs #39 and #41 content
