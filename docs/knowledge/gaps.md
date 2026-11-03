# Documentation gap inventory

A file-level list of what is still missing, out of date, or in conflict, as of 2026-11-03 at main `8e2df97b558e69032e52a50ed0adfd311ad04578` plus the docs-platform branch (PR #41, not merged). Each item names the file, the problem, how it was found, and who can act on it.

## Preserved records that are out of date

These files are byte-locked by [preserved-records.json](../metadata/preserved-records.json). Changing them means updating that manifest, which the standard reserves for an owner decision. Companion pages now carry the current position.

| File(s) | Problem | Found by | Mitigation |
|---|---|---|---|
| `learning/README.md`, `learning/INVENTORY.md`, `learning/weeks/*.md` | Say main has only README.md and that all PRs are open drafts. They tell you to check out branches | reading against main | [learning/CURRENT.md](../../learning/CURRENT.md) |
| `learning/SETUP.md`, `learning/weeks/week-01.md`, `week-02.md` | Built on PR #1's evidence layout (`evidence/aws/run-cmd.sh`, `SHA256SUMS`, `bank-aws-001-cdk.yml`), which is not on main | citation check: 82 of 98 pinned paths on main | Mapping table in learning/CURRENT.md |
| `docs/adr/README.md` and all seventeen ADRs | Status lines say source PRs are unmerged. ADRs 0001, 0002 and 0010 cite PR #1/#6-only paths. ADRs 0003, 0004 and 0009 cite `reports/review-pr3-pr6.md` (PR #14, not on main) | same check | [docs/adr/STATUS.md](../adr/STATUS.md) |
| `inventory/ARCHITECTURE.md` | Ten Mermaid diagrams with no written equivalent. They render as source text | grep for Mermaid fences | none yet; owned by the inventory-diagrams module |

## Conflicting records (not documentation-owned)

| File | Conflict | Who can resolve |
|---|---|---|
| `coordination/modules.json` (`aws-cdk.limitations`) | Says "PR #14 B5-1/B5-2 open". `coordination/tasks.json` and `reports/INTEGRATION.md` record B5-2 as fixed in `80f01d6`, which is on main | registry maintainer, or Ian |
| `coordination/modules.json` (`orgs-security`) | INTEGRATED, while tasks.json lists B6-1, B6-2 and B6-3 as blocking | registry maintainer, or Ian |
| `coordination/modules.json` (16 of 28 modules, including `learning-guide`, `backup-dr-aws`, `postgres-recovery`, `observability`) | No `limitations` or `reason`, so the discovery report shows "Not documented in registry; review required" | registry maintainer |
| `backup/aws/lib/backup-key.ts` | Still grants `kms:Create*`/`kms:Put*` to the account root. Its comment says the pattern was copied before the B5-2 fix. This is a code question, recorded here because ADR 0016 depends on it | backup-dr-aws owner |

## Missing or thin content

| File | Gap |
|---|---|
| `docs/metadata/pages.json` | All 238 pages have verification level "Not established". No page records scoped verification evidence, even where a check ran. Tutorials describe their local runs in prose only |
| `docs/metadata/pages.json` (reading guides) | 210 pages have reading guides, but they share only 18 distinct overview, why and example texts (one per subject template). They are not page-specific explanations |
| `docs/knowledge/glossary.md` | 15 full entries. The other terms in `terminology.json` (75 in total) have one-line definitions without per-term authoritative references |
| `docs/knowledge/tutorials.md` | No executable Terraform walkthrough (`infra/orgs/terraform`). No live PostgreSQL restore or incident crash run, because the workstation had no PostgreSQL server binaries |
| `docs/knowledge/troubleshooting.md` | Nothing yet for the Terraform track, hybrid Windows runbooks or screen reader problems |
| `docs/knowledge/accessibility.md` | Manual keyboard, screen reader, zoom, forced-colour visual and cognitive reviews not done |
| `scripts/docs/search-core.js` / indexed reading guides | Search recall is broad. Sample questions match 165–238 of 238 pages, because the shared reading-guide text is indexed for every page. Ranking puts the intended page first for the tested queries, but filtering by relevance is weak |
| `docs/knowledge/topics.md` | Subject categories come from metadata. Some legacy categories are broad (61 governance-compliance pages) |
| `reports/ACCEPTANCE.md` | Header says "DRAFT candidate. Not merged to main", but it is on main since PR #40. Not a documentation-owned path |
| `reports/FINAL_REPORT.md` (preserved) | Says the registry reports "24/26 integrated". At `8e2df97` the module-registry job prints `26/27 integrated`. [PR #39](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/39) (open draft, not merged) adds dated sidecar records (`reports/COMPLETION_PASS_2026-11-03.md`, `HUMAN_DECISION_PACKET_2026-11-03.md`) instead of editing it. Until #39 merges, main has no current status record for these reports |
| `.github/workflows/integration-gate.yml` / trusted manifest on `evidence/acceptance` | `merge-eligibility` fails on main `8e2df97` and on every PR, because `scripts/ci/tests/test_module_coverage.py` (changed by PR #40) differs from the trusted manifest at `750de1c`. Integrator work, recorded in PR #39 |
| `docs/AI_PROMPTS.md` | Prompts reference PR #7 and #35 as moving targets. Not re-checked against main |

## Publishing

| Item | State |
|---|---|
| GitHub Pages | Enabled (`build_type: workflow`). Latest deployment: main `8e2df97` on 2026-11-03 at 14:32 EST (run 41703901979). The live site returns HTTP 200 with 229 indexed pages |
| `pages/.github/pull_request_template.html` | Still 404 on the live site (checked 2026-11-03). The builder change on this branch writes `pages/dot-github/...` and returns 200 locally. It is not deployed: `pages/dot-github/...` also returns 404 live until PR #41 merges and deploys |
| Root `README.md` | Said "A public website is not yet deployed". Corrected on this branch |
| PR #15 (`learning-guide`) | Still an open draft, though its content reached main through PR #35 |

## Owner-only actions

- Decide whether any ADR moves from Proposed to Accepted, against a specific commit.
- Decide whether preserved learning and ADR records may be edited (manifest update) or must stay frozen with companion pages.
- Review PR #41 (owner review required by its description), merge it if acceptable, then confirm the push deploys Pages, or run **Documentation knowledge base → Run workflow → deploy** on main.
- Close or keep PR #15, now that its content is on main.
- Arrange a human accessibility review (keyboard and at least one screen reader).
- The user actions open in `coordination/tasks.json` at `8e2df97` are outside documentation: UA-2 (Entra baseline), UA-3 (protect `main` and `evidence/acceptance`) and UA-7 (invite an independent reviewer). [PR #39](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/39) sets out the options.
