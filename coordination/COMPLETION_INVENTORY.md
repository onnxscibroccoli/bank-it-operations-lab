# Completion inventory (STEP 1)

Created 2026-11-03 (EST, America/New_York) on `integration/completion-20261103`, off `main` `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6`. The machine-readable copy is `coordination/completion-inventory.json`.

> **Not an approval.** No module is independently reviewed, and AC1 is UNMET. Each module's limitations label its simulations and substitutes. This checkpoint does not merge into `main`.

## Refs

| Ref | SHA |
|---|---|
| `main` | `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6` |
| `delivery/portfolio` | `aa6a38b9d2221d579bff91bb1cdf55227343db76` |
| `overnight/integration` | `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45` |
| `acceptance/vertical-slice` | `eb42b23747d5b686d9540c93e445a713b4e56c5d` |
| `evidence/acceptance(before T-01)` | `7f047e8638ee8cfc3dae9c7c359103835be91f4f` |
| `evidence/acceptance(after T-01)` | `750de1c694c4912f12bb5bb76a20ba74bc208213` |
| `trusted_gate_pin(gate_sha)` | `ea0c23597e1eec9bd15ecccc16b40a6ecbe057ae` |
| `integration_branch` | `integration/completion-20261103 (head = records-only child of the gate commit)` |

Ancestry: delivery/portfolio and overnight/integration are ancestors of main (main is 1 ahead of delivery/portfolio, 17 ahead of overnight/integration). acceptance/vertical-slice had 14 commits not in main (merge-base 49122f2); merged cleanly.

Drift: modules.json has 28 modules (not 26): aws-network-edge, endpoint-windows-automation, inventory-diagrams, owner-authentication, knowledge-base added by delivery; acceptance and review-notes move to INTEGRATED on the integration branch.

## Gap counts (28 modules + 5 priority rows)

| Gap type | Count | Meaning |
|---|---|---|
| BLOCKING | 2 | blocks trustworthy acceptance/merge |
| DOC_STALE | 2 | docs lag current state |
| EVIDENCE | 1 | historical evidence preservation/verification |
| FOLLOW_UP | 1 | technical follow-up with no user action |
| NONE | 2 | no gap |
| NOT_EXECUTED | 1 | needs an environment we do not have; labelled |
| PARTIAL | 7 | delivered with a stated scope gap |
| REVIEW | 14 | no open code gap; independent review pending (AC1) |
| USER_ACTION | 3 | needs Ian |

## Modules

| Module | Goal | Implementation (path@SHA) | Checks (CI jobs) | Evidence | Owner | Gap | Tasks |
|---|---|---|---|---|---|---|---|
| `integration-infra` (INTEGRATED) | CI gate: module registry, user-actions, offline validation, merge eligibility from a trusted manifest | `.github/workflows@30e0a83`<br>`.github/acceptance@30e0a83`<br>`scripts/validate-all.sh@30e0a83`<br>`scripts/ci@30e0a83`<br>`coordination@30e0a83`<br>`reports/INTEGRATION.md@30e0a83`<br>`README.md@30e0a83`<br>`.gitignore@30e0a83` | `integration-gate.yml:user-actions`<br>`integration-gate.yml:module-registry`<br>`integration-gate.yml:final-summary`<br>`integration-gate.yml:merge-eligibility` | - | Integrator | **BLOCKING**: main integration-gate run 41242239019 FAILED: merge-eligibility manifest mismatch (main scripts/ci changed by delivery commits; manifest pinned af49a27). Pin has no independent review -> TRUSTED GATE UNVERIFIED. | T-01, T-16 |
| `shared-evidence-validator` (INTEGRATED) | Shared evidence validator (hashes, S3 self-logging, postgres negatives) | `evidence/shared@30e0a83`<br>`reports/review-pr1-pr2.md@30e0a83` | `offline-validation.yml:validate` | `evidence/shared` | PR Reviewer | **REVIEW**: No open code gap; unreviewed by an independent account. | T-27 |
| `entra-offline` (INTEGRATED) | Entra Conditional Access baseline validated offline | `identity/entra@30e0a83`<br>`tests/entra@30e0a83`<br>`evidence/entra@30e0a83` | `offline-validation.yml:validate` | `evidence/entra` | Integrator | **USER_ACTION**: Synthetic policies only (labelled). Baseline choices await owner confirmation (UA-2). | T-19 |
| `aws-cdk` (INTEGRATED) | Remediated VPC/RDS CDK app with cdk-nag gate | `infra/aws-cdk@30e0a83`<br>`evidence/aws@30e0a83` | `aws-cdk.yml:synth-and-test` | `evidence/aws` | AWS Remediation | **USER_ACTION**: Static synth only, nothing deployed (labelled). EX-01..EX-04 unapproved; EX-04 unresolved (UA-1). | T-17 |
| `postgres-recovery` (INTEGRATED) | PostgreSQL backup/restore exercise with verified evidence | `tests/integration@30e0a83`<br>`evidence/postgres@30e0a83` | `postgres-restore-evidence.yml:harness-selftest`<br>`postgres-restore-evidence.yml:restore-exercise-service`<br>`postgres-restore-evidence.yml:restore-exercise-offline`<br>`postgres-restore-evidence.yml:version-mismatch-control` | `evidence/postgres` | Backup DR | **EVIDENCE**: Committed evidence verified (38 cases); dump artifacts of committed runs not checked (--require-artifacts only on fresh runs). | T-18 |
| `orgs-security` (INTEGRATED) | AWS Organizations SCPs, org CloudTrail, security services (CDK + Terraform) | `infra/orgs@30e0a83`<br>`evidence/orgs@30e0a83` | `portfolio-validation.yml:offline`<br>`portfolio-validation.yml:orgs-static`<br>`portfolio-validation.yml:terraform-static` | `evidence/orgs` | AWS Remediation | **PARTIAL**: Terraform track partial, no CDK parity; no plan/apply (labelled). PR #6 original evidence (31 files: cdk-nag reports, logs, synth) not on main. | T-23, T-10 |
| `acceptance` (INTEGRATED) | Executable, SHA-bound acceptance framework (contract, runner, adapters, vertical slice) | `scripts/acceptance@integration/completion-20261103`<br>`schemas/acceptance@integration/completion-20261103`<br>`tools/acceptance@integration/completion-20261103`<br>`acceptance@integration/completion-20261103`<br>`tests/acceptance-contract@integration/completion-20261103`<br>`reports/ACCEPTANCE.md@integration/completion-20261103`<br>`reports/ACCEPTANCE_INVARIANT_ASSURANCE.md@integration/completion-20261103` | `acceptance.yml:gate-selftest`<br>`acceptance.yml:acceptance`<br>`acceptance.yml:defect-control` | - | Integrator | **FOLLOW_UP**: Integrated on integration/completion-20261103 (not yet main). C1-C4 fixed (17cfaea); C5 fixed on branch; open: fail-closed inventory binding when git show fails, dynamic-group minimum counts, review-record scope. I2 PARTIALLY ENFORCED (no protection). | T-02, T-03, T-04, T-05, T-06 |
| `review-notes` (INTEGRATED) | Preserved review history | `reports/review-pr3-pr6.md@integration/completion-20261103`<br>`reports/independent@integration/completion-20261103`<br>`reports/review-candidate-08cdf11.md@integration/completion-20261103`<br>`reports/review-acceptance-vertical-slice.md@integration/completion-20261103`<br>`reports/review-candidate-b908a66.md@integration/completion-20261103`<br>`reports/review-candidate-1fdf25a.md@integration/completion-20261103`<br>`reports/review-candidate-5a75d9c.md@integration/completion-20261103`<br>`reports/review-candidate-2e3041a.md@integration/completion-20261103`<br>`reports/review-candidate-a9d0f64.md@integration/completion-20261103` | - | - | PR Reviewer | **NONE**: Preserved on integration branch (records only, not approvals). | T-08 |
| `portfolio-cases` (INTEGRATED) | Source-grounded case studies | `portfolio@30e0a83` | `portfolio-validation.yml:offline` | - | Portfolio Cases | **REVIEW**: Integrated at PR #8 head 7010d05; PR still open draft; unreviewed. | T-09, T-27 |
| `vendor-mock` (INTEGRATED) | Banking-vendor API mock and vendor-risk governance | `integrations@30e0a83`<br>`evidence/vendor@30e0a83`<br>`governance/vendor-risk@30e0a83` | `portfolio-validation.yml:offline` | `evidence/vendor` | Integrator | **REVIEW**: SIMULATION (labelled). Integrated at PR #9 head d6efb82 with later repairs; PR still open. | T-09, T-27 |
| `observability` (INTEGRATED) | Host health collector and synthetic monitoring | `observability@30e0a83`<br>`evidence/observability@30e0a83` | `portfolio-validation.yml:offline` | `evidence/observability` | Integrator | **REVIEW**: Synthetic data (labelled). Integrated at PR #10 head 3e40e39; PR still open. | T-09, T-27 |
| `final-report` (INTEGRATED) | Final report, evidence manifest, user actions | `reports/FINAL_REPORT.md@30e0a83`<br>`reports/EVIDENCE_MANIFEST.md@30e0a83`<br>`reports/USER_ACTIONS_REQUIRED.md@30e0a83`<br>`reports/user-actions.json@30e0a83`<br>`docs/DEMO_WALKTHROUGH_15MIN.md@30e0a83` | `portfolio-validation.yml:offline` | - | Final Report | **DOC_STALE**: Integrated at PR #11 head d500ccf with later edits; must be refreshed for acceptance integration, Pages live, 28-module coverage. | T-25, T-09 |
| `job-requirements-matrix` (INTEGRATED) | Job requirements matrix mapped to evidence | `docs/JOB_REQUIREMENTS_MATRIX.md@30e0a83` | `portfolio-validation.yml:offline` | - | Job Matrix | **DOC_STALE**: Matrix predates acceptance integration and the five delivery modules. | T-24, T-09 |
| `team-management` (INTEGRATED) | Team model and service management examples | `docs/management@30e0a83`<br>`operations/team@30e0a83` | `portfolio-validation.yml:offline` | - | Portfolio Cases | **REVIEW**: Synthetic team model (labelled). Integrated at PR #13 head 9dc8f1f with later edits; PR open. | T-09, T-27 |
| `learning-guide` (INTEGRATED) | Twelve-week learning guide and ADRs | `learning@30e0a83`<br>`docs/adr@30e0a83`<br>`docs/REPO_NAVIGATOR.md@30e0a83`<br>`docs/REVIEWER_GUIDE.md@30e0a83`<br>`docs/AI_PROMPTS.md@30e0a83` | `portfolio-validation.yml:offline` | - | Portfolio Cases | **PARTIAL**: Learning guide is legacy Markdown; not linked into knowledge-base structured topics/search query set. | T-14, T-09 |
| `control-mapping` (INTEGRATED) | FFIEC AIO control mapping | `governance/controls@30e0a83`<br>`evidence/control-review@30e0a83` | `portfolio-validation.yml:offline` | `evidence/control-review` | Job Matrix | **REVIEW**: FFIEC mapping is a lab mapping, not an audit opinion (labelled). PR #16 open. | T-09, T-27 |
| `patch-hardening` (INTEGRATED) | SSM patch rings and host hardening | `operations/hardening@30e0a83`<br>`operations/patching@30e0a83`<br>`evidence/host-operations@30e0a83` | `portfolio-validation.yml:offline` | `evidence/host-operations` | AWS Remediation | **REVIEW**: Not executed on real hosts (labelled). PR #17 open. | T-09, T-27 |
| `identity-governance` (INTEGRATED) | Identity governance with offline Graph fixtures | `identity/governance@30e0a83`<br>`docs/federation@30e0a83`<br>`evidence/identity-governance@30e0a83` | `portfolio-validation.yml:offline` | `evidence/identity-governance` | Integrator | **REVIEW**: Offline Graph fixtures only (labelled). PR #18 open. | T-09, T-27 |
| `hybrid-operations` (INTEGRATED) | Windows Server/AD DS/hybrid runbooks | `operations/hybrid@30e0a83`<br>`docs/runbooks/hybrid@30e0a83` | `portfolio-validation.yml:offline` | - | Portfolio Cases | **REVIEW**: Documentation only, no Windows/AD execution (labelled). Main differs from PR #19 head in 12 files (later delivery edits); PR open. | T-09, T-27 |
| `m365-endpoint` (INTEGRATED) | M365/Intune endpoint scenarios (plan-only) | `identity/m365@30e0a83`<br>`evidence/m365@30e0a83` | `integration-gate.yml:m365-scenario-evaluation`<br>`integration-gate.yml:m365-unit-tests`<br>`integration-gate.yml:m365-evidence-verification`<br>`integration-gate.yml:plan-only-assertions` | `evidence/m365` | Integrator | **REVIEW**: Plan-only (labelled). PR #20 draft, 0 reviews (AC1). | T-20 |
| `backup-dr-aws` (INTEGRATED) | AWS Backup DR reference and cost model | `backup@30e0a83`<br>`evidence/backup@30e0a83`<br>`docs/runbooks/aws-backup@30e0a83` | `portfolio-validation.yml:offline`<br>`portfolio-validation.yml:backup-static` | `evidence/backup` | Backup DR | **REVIEW**: Reference + cost model, nothing deployed (labelled). PR #21 open. | T-09, T-27 |
| `incident-demo` (INTEGRATED) | Incident demo scenario with evidence | `scenarios@30e0a83`<br>`evidence/incident@30e0a83` | `integration-gate.yml:incident-committed-runs`<br>`integration-gate.yml:incident-fresh-run`<br>`integration-gate.yml:incident-not-executed-negative`<br>`integration-gate.yml:labeling-markers` | `evidence/incident` | Portfolio Cases | **REVIEW**: Synthetic scenario (labelled). PR #22 has no reviews (AC1). | T-27 |
| `bank-aws-001` (SUPERSEDED) | First planned AWS module (superseded) | `reports/MORNING_REPORT.md@30e0a83`<br>`infra/aws-cdk/lib/evidence-validator.ts@30e0a83`<br>`infra/aws-cdk/scripts/validate-evidence.ts@30e0a83` | - | - | AWS Remediation | **NONE**: SUPERSEDED by PR #5 (aws-cdk). PR #1 closed (UA-4 RESOLVED). | - |
| `aws-network-edge` (INTEGRATED) | Private network edge CDK app | `infra/aws-network@30e0a83` | `portfolio-validation.yml:network-edge` | - | AWS Remediation | **REVIEW**: Credential-free CDK app, not deployed (labelled). No PR; delivered directly in delivery/portfolio. | T-27 |
| `endpoint-windows-automation` (INTEGRATED) | Windows endpoint baseline automation (Pester) | `operations/endpoint@30e0a83` | `portfolio-validation.yml:offline`<br>`portfolio-validation.yml:endpoint-pester` | - | Integrator | **NOT_EXECUTED**: Pester on a domain-joined Windows host NOT_EXECUTED (needs a real host; out of scope without user environment). | T-22 |
| `inventory-diagrams` (INTEGRATED) | Asset inventory and diagrams | `inventory@30e0a83` | `portfolio-validation.yml:offline` | - | Portfolio Cases | **REVIEW**: Integrated via PR #35; unreviewed. | T-27 |
| `owner-authentication` (INTEGRATED) | Owner signature authentication design | `governance/owner-auth@30e0a83` | `portfolio-validation.yml:offline` | - | Integrator | **USER_ACTION**: Prototype; no enrolled human key, adapter or revocation policy (UA-6). | T-26 |
| `knowledge-base` (INTEGRATED) | Accessible searchable knowledge base published on GitHub Pages | `scripts/docs@30e0a83`<br>`docs/knowledge@30e0a83`<br>`docs/metadata@30e0a83`<br>`docs/index.md@30e0a83`<br>`AGENTS.md@30e0a83`<br>`llms.txt@30e0a83`<br>`.github/pull_request_template.md@30e0a83` | `documentation.yml:validate` | - | Final Report | **PARTIAL**: Pages live; 210/221 pages legacy; automated WCAG subset on 12 pages only; no manual/screen-reader test; documentation.yml actions not SHA-pinned and does not run on integration/** pushes. | T-11, T-12, T-13 |

## Priorities 2–6

| Priority | Goal | Implementation | Docs | Checks | Evidence | Owner | Gap | Tasks |
|---|---|---|---|---|---|---|---|---|
| `P2-elite-docs` | Elite documentation: structured, linted, navigable | `docs/knowledge/*.md@30e0a83`<br>`docs/index.md@30e0a83`<br>`AGENTS.md@30e0a83`<br>`llms.txt@30e0a83`<br>`docs/AI_PROMPTS.md@30e0a83` | `docs/knowledge/standards.md`<br>`docs/knowledge/publishing.md` | documentation.yml:validate (markdownlint, audit.py, impact.py) | docs/metadata/validation-20261031.json | Final Report | **PARTIAL**: 13 curated knowledge pages; 210 of 221 indexed pages still legacy Markdown; final report/job matrix stale vs current state. | T-12, T-24, T-25 |
| `P3-search-learning` | Natural-language search and learning paths | `scripts/docs/search-core.js@30e0a83`<br>`scripts/docs/search.js@30e0a83`<br>`learning/@30e0a83` | `docs/knowledge/start.md`<br>`learning/` | documentation.yml:validate (node --test search.test.mjs; browser.mjs) | docs/metadata/validation-20261031.json (14 search regressions; 10 NL queries top-5) | Portfolio Cases | **PARTIAL**: Search query set covers curated topics only; learning guide weeks not mapped to search/topic pages. | T-14 |
| `P4-accessibility` | WCAG 2.2 AA accessible site | `scripts/docs/tests/browser.mjs@30e0a83`<br>`scripts/docs/style.css@30e0a83` | `docs/knowledge/standards.md` | documentation.yml:validate (axe-core 4.11.0 via Playwright Chromium; keyboard checks) | docs/metadata/validation-20261031.json: 12 pages, 0 violations, 0 incomplete | Final Report | **PARTIAL**: Automated subset only (labelled: no WCAG conformance claim); 12 of 221 pages scanned; no human screen-reader/manual test (needs a human tester). | T-13 |
| `P5-trustworthy-acceptance` | Trustworthy SHA-bound acceptance: AC1-AC5 computed at runtime, trusted gate, acceptance framework | `scripts/ci@30e0a83`<br>`scripts/acceptance@integration/completion-20261103`<br>`evidence/acceptance:trusted-gate/gate-manifest.json@7f047e8` | `reports/ACCEPTANCE.md`<br>`reports/ACCEPTANCE_INVARIANT_ASSURANCE.md`<br>`evidence/acceptance:trusted-gate/README.md` | integration-gate.yml:merge-eligibility<br>acceptance.yml:gate-selftest<br>acceptance.yml:acceptance<br>acceptance.yml:defect-control | main integration-gate run 41242239019 (FAILED: manifest mismatch) | Integrator | **BLOCKING**: (1) main gate manifest mismatch; (2) pin has no independent review; (3) no independent reviewer account (AC1, UA-7); (4) no protection/rulesets on main and evidence/acceptance (UA-3); (5) owner identity = shared agent account (UA-6); (6) acceptance follow-ups T-03..T-05. | T-01, T-02, T-03, T-04, T-05, T-15, T-16 |
| `P6-actions-pages` | GitHub Actions CI and GitHub Pages publication | `.github/workflows/documentation.yml@30e0a83`<br>`.github/workflows/acceptance.yml@integration/completion-20261103` | `docs/knowledge/publishing.md` | documentation.yml:validate<br>documentation.yml:deploy | Pages API: has_pages true, build_type workflow, source main, https enforced; site HTTP 200; github-pages deployments at 30e0a83 (2026-10-31 17:11/17:14/17:25 EDT) | Integrator | **PARTIAL**: Pages enabled and live: NO user action needed. documentation.yml uses tag-pinned actions (not SHA) and does not run on integration/** pushes (needs dispatch or PR). Deploy is a public publish; only on main push. | T-11 |

## Blocking gaps

### (a) Acceptance framework and C1–C6

- PRs #23 (`6a28847`) and #24 (`838d537`) are ancestors of PR #26 (`eb42b23`). PR #26 is merged on this branch, and the merge was conflict-free. PR #25 diverged: its head `ce39504` adds `acceptance/modules/emit_shared.py` and a test that #26 dropped. It is merged separately and its tests pass.
- C1–C4 (PR #27 at `181bcdd`) were fixed at `17cfaea`, with regression tests in `scripts/acceptance/tests` (32 tests pass).
- C5 is fixed on this branch: actions are pinned to the SHAs the other workflows use, retention is 7 days, and the workflow runs on `main` and `integration/**`, so the combined candidate gets tested.
- C6 is reconciled in `coordination/tasks.json`. The superseded rule text is kept for the record.
- The overnight gate fixes (D1–D3-a) live in `scripts/ci` and are separate from the C-series. The two do not conflict: `scripts/acceptance` and `scripts/ci` are disjoint.
- Remaining follow-ups: T-03 (fail closed when `git show` fails; today a missing inventory skips the comparison), T-04 (dynamic-group minimum counts) and T-05 (review-record scope).
- Trust: `main`'s integration-gate merge-eligibility failed in run 41242239019 on a manifest mismatch. T-01 re-pins to the integration gate commit, which carries `main`'s `scripts/ci` plus a one-line registry test update. The pin still has no independent review, so it stays TRUSTED GATE UNVERIFIED. AC1, UA-3, UA-6 and UA-7 are still open.

### (b) GitHub Pages

- Pages is enabled: `has_pages` true, `build_type` workflow, source `main`, HTTPS enforced. The site https://onnxscibroccoli.github.io/bank-it-operations-lab/ returns HTTP 200, and github-pages deployments exist at `30e0a83`. **No user action is needed to enable Pages.**
- Remaining gaps: `documentation.yml` actions are not SHA-pinned, and the workflow does not run on `integration/**` pushes (it has to be dispatched) (T-11). Accessibility coverage is partial (T-13).

## Tasks

| ID | Task | Owner | Gap type | State |
|---|---|---|---|---|
| T-01 | Re-pin trusted gate manifest on evidence/acceptance to the integration gate commit (main 30e0a83 scripts/ci plus the one-line test_module_coverage.py update for the newly INTEGRATED modules); the candidate head is a later records-only commit, so gate_sha != candidate. Gate stays TRUSTED GATE UNVERIFIED until independently reviewed. | Integrator | BLOCKING | done in STEP 1 (normal commit on evidence/acceptance) |
| T-02 | Integrate acceptance framework: PR #26 eb42b23 (contains #23, #24, #25@c6aa238) + diverged PR #25 head ce39504. | Integrator | BLOCKING | done on integration/completion-20261103 |
| T-03 | verify_results.py: fail closed when git show of the inventory at the expected SHA fails; convert tests from fake SHAs to real commits. | Integrator (code) + PR Reviewer (review) | FOLLOW_UP | open |
| T-04 | Dynamic groups HASH-*/ENTRA-*: replace minimum counts with exact expected counts derived from the tree at the tested SHA. | Integrator + PR Reviewer | FOLLOW_UP | open |
| T-05 | Review records: scope each review to explicit requirement IDs instead of copying to every requirement. | Integrator + PR Reviewer | FOLLOW_UP | open |
| T-06 | C5: pin acceptance.yml actions to SHAs, 7-day retention, run on main and integration/**. | Integrator | FOLLOW_UP | done on integration branch |
| T-07 | C6: reconcile obsolete merge/approval constraints in coordination/tasks.json. | Integrator | FOLLOW_UP | done on integration branch (historical text kept) |
| T-08 | Preserve review records PRs #14, #27-#34 on the branch (records, not approvals). | Integrator | EVIDENCE | done on integration branch |
| T-09 | Disposition of open draft module PRs #6, #8-#13, #15-#19, #21 (content integrated at their exact heads in aec7e5f, later repaired on main): close as integrated with a comment. Externally visible: needs Ian's OK. | Integrator | USER_ACTION | proposed |
| T-10 | Preserve PR #6 original evidence (31 files at e5e7f46 absent from main) with an annotated checkpoint tag or evidence/orgs/history/pr6-e5e7f46/. | AWS Remediation | EVIDENCE | proposed |
| T-11 | documentation.yml: pin actions to full SHAs; validate on integration/** pushes; keep deploy main-only. | Integrator | PARTIAL | proposed (needs SHA lookup for configure-pages/deploy-pages/upload-pages-artifact) |
| T-12 | Migrate highest-traffic legacy Markdown to structured knowledge topics. | Final Report | PARTIAL | proposed |
| T-13 | Extend axe scan to all generated pages; human screen-reader test is a human task (label as NOT_EXECUTED until done). | Final Report | PARTIAL | proposed |
| T-14 | Map learning-guide weeks to knowledge topics and add search regressions for them. | Portfolio Cases | PARTIAL | proposed |
| T-15 | Independent reviewer account (UA-7), rulesets on main + evidence/acceptance (UA-3), separate owner identity (UA-6). | Ian | USER_ACTION | open |
| T-16 | Decide main-push behaviour of merge-eligibility (direct pushes always NOT ELIGIBLE -> permanently red). Option: report-only on push to main; requires gate change + re-pin + review. | Integrator | FOLLOW_UP | proposed |
| T-17 | AWS exceptions EX-01..EX-04 decisions (EX-04 unresolved); PR #14 B5-1/B5-2 status re-check against main. | AWS Remediation + Ian (UA-1) | USER_ACTION | open |
| T-18 | Postgres: verify dump artifacts for committed runs or label them HASH_ONLY. | Backup DR | EVIDENCE | proposed |
| T-19 | Entra Conditional Access baseline confirmation (UA-2). | Ian | USER_ACTION | open |
| T-20 | M365 PR #20 review at exact SHA. | PR Reviewer | REVIEW | proposed |
| T-21 | Run the full acceptance.yml + all workflows on the integration branch head and record run IDs. | Integrator | FOLLOW_UP | in progress (STEP 1) |
| T-22 | Pester on a domain-joined Windows host: NOT_EXECUTED (no host); keep labelled. | Integrator | NOT_EXECUTED | accepted limitation unless Ian provides a host |
| T-23 | Orgs Terraform parity with CDK (CloudTrail, security services) — static validation only. | AWS Remediation | PARTIAL | proposed |
| T-24 | Refresh job requirements matrix for acceptance + five delivery modules. | Job Matrix | DOC_STALE | proposed |
| T-25 | Refresh FINAL_REPORT / EVIDENCE_MANIFEST / USER_ACTIONS_REQUIRED for this integration. | Final Report | DOC_STALE | proposed |
| T-26 | Owner-auth: enroll human-only key after independent review of the design (UA-6). | Ian | USER_ACTION | not yet actionable |
| T-27 | Final independent whole-repo review packet after merge (Ian routes it). | PR Reviewer | REVIEW | after merge |
| T-28 | Merge integration/completion-20261103 into main (next checkpoint, normal merge, no force). | Integrator | FOLLOW_UP | awaiting STEP 1 report |
