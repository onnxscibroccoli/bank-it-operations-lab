# Acceptance framework integration v2 (`acceptance/integration-v2`)

Integrator: Worker D (independent of implementers A–C). Recorded 2026-11-03 (America/New_York).
This record is **not an approval**. The gate ends at `EXECUTION_PASS` + `REVIEW_PENDING`; it has no `ACCEPTED` state.

## Starting points (verified with `git rev-parse` against `origin` before work)

| ref | SHA |
|---|---|
| `main` | `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6` |
| `acceptance/vertical-slice` (PR #26) | `eb42b23747d5b686d9540c93e445a713b4e56c5d` |
| `acceptance-contract` A (PR #23) | `6a28847b222ad0d32a45a78f7350dee30ddc7749` |
| `acceptance-runner` B (PR #24) | `838d537abff7edd3f870c8c3d19d7287dd1dce97` |
| `acceptance-adapters` C (PR #25) | `ce39504783247b1fffe71785b4505711c2d1b5e5` (C was integrated at `c6aa238e` + Worker D fix `93de4b3d`) |
| `review/chatgpt-acceptance-181bcdd` (PR #27) | `72aa8b7422a79ab237f9d3a2a5e871be9ce9f952` |

## Commits on this branch (first parent)

| commit | what |
|---|---|
| `1c683275` | normal merge of `acceptance/vertical-slice @ eb42b23` onto `main @ 30e0a832` (A, B, C and D history preserved; no conflicts; the slice's `overnight/integration` base `49122f2` is already an ancestor of main) |
| `060a5df3` | pure rename `scripts/acceptance/*` → `tools/acceptance/gate/*` (`required-checks.v1.json` → `required-checks.json`) |
| `2f32bf3f` | gate v2 (fail-closed binding, derived groups, scope registration, provenance, recomputed state/summary, `postgres-run/**` hashing, scoped reviews, no ACCEPTED) + real-git-repo regression tests + proof script + compatibility shim |
| `094b8a02` | HASH group handles repo-root-relative bundles; workflow moved to the new path, `--sha` everywhere, CI regression proof, push-to-main verification; C5 pins + 7-day retention |
| `98fc405a` | this record |
| `ff306d68` | normal merge of `acceptance-adapters` (C) head `ce395047`, which adds `emit_shared.py`, C's mapping onto A's contract. The slice had integrated C only up to `c6aa238e` (the PR #25 divergence noted in `coordination/modules.json`) |
| `bd67b156` | ACC-C-02 also runs C's emitter (`--shared-out`); decision staging excludes it |
| `6ea6803c` | registry and docs bookkeeping needed for main's required checks (see below) |

## D-1: path reconciliation

The slice put the gate in `scripts/acceptance/**`. The owned paths are `acceptance/**`, `schemas/acceptance/**`,
`tools/acceptance/**` and `tests/acceptance-contract/**`, so the gate moved to **`tools/acceptance/gate/`**, next to worker B's
runner. A (`schemas/acceptance`, `tests/acceptance-contract`) and B (`tools/acceptance/{runner.py,checks.json,tests}`) are
unchanged from `6a28847b` / `838d537a`. C (`acceptance/modules`) is C's head `ce395047` plus Worker D's fix `93de4b3d`.

Files outside the owned paths, which are all the minimum needed:

| path | why |
|---|---|
| `.github/workflows/acceptance.yml` | the existing acceptance workflow from the slice: new gate path, `--sha` binding, regression proof, C5 pins/retention, `push: main` verification |
| `scripts/acceptance/run.sh` | 3-line compatibility shim (`exec tools/acceptance/gate/run.sh "$@"`) so the historically documented first command still works |
| `coordination/modules.json` | the `acceptance` entry only: NOT_INTEGRATED → INTEGRATED, with `ci_jobs` = the three `acceptance.yml` jobs and the second report path. Main's required `module-registry` job fails closed while NOT_INTEGRATED paths exist |
| `scripts/ci/tests/test_module_coverage.py` | one assertion that hard-coded `acceptance(NOT_INTEGRATED)` as incomplete. **Note:** `scripts/ci/**` is hashed by main's trusted gate manifest. `merge-eligibility` already fails on main @ `30e0a832` for 8 other `scripts/ci` drifts, and the manifest needs an owner re-pin (UA-3) in any case |
| `docs/metadata/pages.json` | 6 additive entries (documentation `test_every_document_has_metadata` requires one per tracked `.md`) |
| `reports/ACCEPTANCE.md`, `reports/ACCEPTANCE_INVARIANT_ASSURANCE.md` | historical evidence carried in by the merge, **byte-identical to eb42b23** (not edited). Where they say `scripts/acceptance/…` or that ACCEPTED is reachable, this record supersedes them. |

Not touched: `reports/independent/chatgpt/**` (it isn't on this branch; PR #27 is unchanged), `coordination/tasks.json`, `scripts/ci/*.py`, `.github/acceptance/**`, every other workflow, and all module and evidence content.

First command (unchanged contract): `bash tools/acceptance/gate/run.sh <40-hex SHA> --out acceptance-out`
(or `bash scripts/acceptance/run.sh …`). Exit 0 = EXECUTION_PASS, 1 = FAIL, 2 = required UNKNOWN. Then
`python3 tools/acceptance/gate/decide.py acceptance-out --sha <SHA>` exits 5 = REVIEW_PENDING.

## What the gate now rejects (fail closed)

The checker is `verify_results.py`, which is mandatory before `decide.py`:
- **Missing check or evidence:** every inventory id must be present exactly once. A required PASS/FAIL needs its log and exit trailer.
- **Duplicate, downgraded or unknown ids** (C1).
- **Required INFO** (C2).
- **Contradictions:** JSON≠TSV records, recomputed counters or overall (C3); `execution_state` is recomputed (R4); `SUMMARY.md` is re-rendered and compared.
- **Unreadable or nonexistent commit:** `git cat-file -e <sha>^{commit}` must succeed; the inventory must exist at the SHA and match the verifier's copy (R1/R2); `--sha` is mandatory.
- **Group members are derived from the tree at the SHA:** HASH-i must name the i-th `evidence/<x>/**/SHA256SUMS`; ENTRA-04.i the i-th `evidence/entra/runs/<run>`. So a dropped or extra member can't hide behind `min`.
- **Scope:** every tracked file at the SHA must fall under a registered module path, which has checks, or a declared non-module path. Every module path must exist. Portfolio paths on main that this gate does not check are registered with a `contract_id` and exported to A's contract as **non-required UNKNOWN**, so they are visible gaps that never count as PASS.
- **Provenance:** `results.json.provenance` must be present: `github-actions`, with a numeric run id/attempt and `workflow_ref` = `<repo>/.github/workflows/acceptance.yml@…`, or `local`. `authenticated` must be `false` (the gate cannot authenticate).
- **`postgres-run/**`** is covered by the top-level `SHA256SUMS` (R7).
- **Reviews** (`--reviews`): each record must name `requirement_ids` that exist in the exported document. It is attached only to those. A blanket or unknown-id review, or a reviewer string that looks like the recorder or integrator, makes the decision INVALID.
- **No ACCEPTED:** a fully concurring (unauthenticated) review set gives `REVIEW_CONCURRED_UNAUTHENTICATED` (exit 7). `--accept-for` can never exit 0.

## C1–C6 disposition (PR #27)

| finding | disposition | commit | tests |
|---|---|---|---|
| C1 inventory completeness | **Resolved.** Base repair `17cfaea`; v2 adds fail-closed inventory-at-SHA, derived group members and scope registration | `17cfaea3`, `2f32bf3f` | `C1Inventory.*` (7), `FA03`, `FA04.*`, `FA05` |
| C2 required INFO → PASS | **Resolved** | `17cfaea3` | `C2Info.*` (4) |
| C3 JSON/TSV / summary contradictions | **Resolved.** v2 adds recomputed `execution_state` and the SUMMARY.md comparison | `17cfaea3`, `2f32bf3f` | `C3Records.*` (7), `FA07`, `FA08` |
| C4 shared contract in the final gate; EXECUTION_PASS vs REVIEW_PENDING | **Resolved, with a substitute for authenticated review.** The run is exported into A's contract and evaluated by A's unmodified checker. Reviews are scoped per requirement. The gate never reports ACCEPTED. *Substitute:* authenticated review binding (a GitHub review on the exact SHA by a non-author) stays outside this gate. The owner's AC1 binding in main's `integration-gate` / `merge-eligibility` (`coordination/tasks.json`) is the authenticated path. | `17cfaea3`, `2f32bf3f` | `C4Decision.*`, `FA01.*`, `FA10.*`, `FA11.*`, `I1.*`, `I2.*` |
| C5 action SHAs, 7-day retention, main+candidate | **Pins and retention resolved** (`actions/checkout@fbc6f39…` v5.1.0, `setup-node@a0853c2…` v5.0.0, `setup-python@a26af69…` v5.6.0, `upload-artifact@330a01c…` v5.0.0, resolved from the upstream tags on 2026-11-03; `retention-days: 7`). **Main+candidate: substitute.** The branch is built on current main, it is merged only when the PR is up to date with main (so head == combined tree), and a `push: main` run re-verifies the resulting main commit. | `094b8a02` | workflow runs |
| C6 obsolete merge restrictions in `coordination/tasks.json` | **Resolved upstream by the coordinator, no change here.** Main's `coordination/tasks.json` (commit `4f54a016`) replaces "never merge into main from automation" and the HUMAN-only AC1 wording (`policy_source.replaces`), with AC6 kept as the separate human portfolio gate. Coordinator-owned, outside the owned paths. | `4f54a016` (main) | n/a |

PR #29 (Lane E) residuals: **R1** substitute (no ACCEPTED state, the commit must exist, provenance is type-checked; authentication deferred). **R2** resolved (`FA02`, `FA03`). **R3** resolved as defence in depth (`FA11`); moot, because ACCEPTED is unreachable. **R4** resolved (`FA07`). **R5** deferred: there's no branch protection or ruleset on `main` (checked through the API, 404/`[]`). That is an owner/admin repo setting, outside the owned paths. **R6** deferred: the CI still runs the candidate's own gate. Main had no gate before this merge, so a base-branch gate is possible only afterwards. Follow-up: run `main`'s `tools/acceptance/gate` against the candidate, or add it to main's trusted gate manifest. **R7** resolved (`FA09`).

## Regression proof (the same test file run against the old gate)

`tools/acceptance/gate/tests/prove_regressions.sh eb42b23…` runs `test_invariants.py` against eb42b23's
`scripts/acceptance` gate (in a temporary git repo) and against this gate. CI runs it in the `gate-selftest` job.
Local result (box, 2026-11-03), with every FA case FAIL on old and ok on new:

| case | old eb42b23 | new |
|---|---|---|
| FA01 any reviewer string → ACCEPTED (R1); `--accept-for` exit 0 | FAIL (old exit 0) | ok |
| FA02 nonexistent commit accepted (R1/R2) | FAIL | ok |
| FA03 inventory absent at tested commit (R2) | FAIL | ok |
| FA04 dropped end member / wrong member path | FAIL | ok |
| FA05 unregistered tracked path | FAIL | ok |
| FA06 missing / malformed / "authenticated" provenance | FAIL | ok |
| FA07 self-reported execution_state (R4) | FAIL | ok |
| FA08 contradictory SUMMARY.md | FAIL | ok |
| FA09 postgres-run outside top-level hashes (R7) | FAIL | ok |
| FA10 blanket review applied to every requirement | FAIL | ok |
| FA11 self-review variant "Worker D (recorder)" (R3) | FAIL | ok |
| FA12 unbound `verify_results.py DIR` | FAIL | ok |

C1–C3 were already closed at eb42b23. Against `181bcdd` (the commit PR #27 reviewed), the review's own probe gives
`required_INFO → PASS`, `missing_checks → 0`, `json_disagrees → 0`; this gate gives `FAIL`, `1`, `1`.
Two older tests, `C4Decision.test_dispute_blocks` and `I1.test_required_unknown…`, also show FAIL on old. That's only because old
A-contract export rejects the new `requirement_ids` field (old exit 1 = INVALID). It isn't a false acceptance.

## Local full run (box, offline, PG 16 binaries)

`bash scripts/acceptance/run.sh 6ea6803c0828a65fb269bb551ad5449f0d8ed948`: **exit 0, EXECUTION_PASS**. 55 required checks
PASS, 0 FAIL, 0 UNKNOWN (27 HASH bundles, ACC-C-03 live-offline and ACC-D-01 included). `decide.py`: **REVIEW_PENDING
(exit 5)**, with 29 blockers that are all "required PASS lacks an independent reviewer concurrence". Verifying the same
output against the parent SHA is rejected (I2).

## Limits

Offline lab gate only: no AWS deploy, no Entra/Graph, no production. Hashes prove byte consistency, not authorship. Provenance
fields are recorded, not authenticated. Whole-portfolio acceptance (AC6) and authenticated independent review are outside this gate.
