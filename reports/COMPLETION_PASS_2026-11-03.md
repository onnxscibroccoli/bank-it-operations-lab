# Completion pass, 2026-11-03

This is a dated status record for the repository. It does not replace any earlier report. The [portfolio delivery report](FINAL_REPORT.md), the [manual actions list](USER_ACTIONS_REQUIRED.md) and [user-actions.json](user-actions.json) are preserved historical records, hash-locked in `docs/metadata/preserved-records.json`. In line with `docs/knowledge/standards.md` ("Add a current explanation in sidecar metadata or a new document, preserving the original record"), the current explanation goes in this document, its machine-readable sidecar [completion-pass-2026-11-03.json](completion-pass-2026-11-03.json), and the [human decision packet](HUMAN_DECISION_PACKET_2026-11-03.md), not in the frozen files.

- **Revision checked:** `main` = `8e2df97b558e69032e52a50ed0adfd311ad04578` (source: `GET /repos/onnxscibroccoli/bank-it-operations-lab/commits/main`, read 2026-11-03 17:03 EST).
- **When checked:** 2026-11-03, 16:55–17:05 EST (UTC-5), using the GitHub REST API (`gh` CLI) and Actions run logs. Nothing was executed against cloud or identity targets.
- **Evidence labels:** EXECUTED = ran in GitHub Actions at the cited SHA; STATIC = read from a file or API response; SIMULATION and NOT_EXECUTED as defined in `coordination/modules.json` `evidence_classes`.
- **Limitations:** this is a point-in-time read of repository state. It is not a review, an approval, an attestation, or a production verification. Controls are "mapped to" frameworks only; no certification or compliance is claimed.

Sections are newest first. The 16:55–17:05 EST read and the 13:22–13:26 EST read at `main` `30e0a83` are kept below without changes to their facts.

## Latest update: three-phase model, `main` `8e2df97`, candidate `-c` `0ad0468` (18:15–18:30 EST)

### Main and candidate (STATIC + EXECUTED)

- **`main`** is still `8e2df97b558e69032e52a50ed0adfd311ad04578` (`GET /repos/onnxscibroccoli/bank-it-operations-lab/commits/main`, 18:15 EST). Runs at that SHA are unchanged: integration-gate failure (`merge-eligibility`), plus acceptance, offline-validation and Documentation success.
- **Newest candidate:** `integration/candidate-20261103c` @ `0ad046825855f2c3e90861981624e2fb8373c24d`, status **CANDIDATE, not integrated**.
  - It has no PR (`GET /pulls?state=all&head=onnxscibroccoli:integration/candidate-20261103c` → `[]`). It is 46 commits ahead of `main` and 0 behind.
  - It was created under owner directives t26u/t27u: do not merge to `main`, do not apply the proposed pin (`coordination/tasks.json@0ad0468` `rules`; `coordination/INTEGRATION_MANIFEST.md@0ad0468`).
  - Branch `docs/engineering-first-governance-deferral-20261103` points at the same commit and has no PR.
- **Candidate runs:**
  - **Tested SHA `614d006ae049aed269dc404aa5b84a7c04b55d8e`:**
    - integration-gate [41734504240](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734504240): failure, 18 of 19 jobs succeed. `merge-eligibility`: "files in scripts/ci not in the trusted manifest".
    - success: acceptance [41734499746](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734499746), offline-validation [41734507318](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734507318), aws-cdk [41734510352](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734510352), postgres [41734513752](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734513752), portfolio [41734516468](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734516468), Documentation [41734575819](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734575819).
  - **Head `0ad0468`** (records-only commits after `614d006`): Documentation push [41735193146](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41735193146) success.
- **Our sidecars on the candidate** (`git rev-parse 0ad0468:<path>` vs PR #39 `95765e9`):
  - The packet (`32c6aebb`), COMPLETION_PASS md (`40382000`) and json (`9846c950`) are **byte-identical**.
  - The `final-report` paths and both `pages.json` entries are identical.
  - Not yet on the candidate: this pass's revisions and `reports/PHASE_C_REVIEW_PACKAGE_PREP_2026-11-03.md`.
- **Locked files on the candidate:** `FINAL_REPORT.md`, `USER_ACTIONS_REQUIRED.md` and `user-actions.json` are identical to `main`. `preserved-records.json` keeps all 145 `main` entries unchanged and adds 10 (155 in total).
- **New PRs since the last read:** #43 `ci-workflow-hardening`, #44 `aws-remediation-backup-kms`, #45 and #46 (`design/*`). PR #42 moved to `8065a44`. Totals: 46 PRs, 0 reviews. 12 issue comments; the newest is a PR #15 disposition note by `onnxscibroccoli`, and none is an `ACCEPTANCE-*` decision.

### Locked files (STATIC, 18:20 EST)

sha256 is identical on `main@8e2df97` and on the PR #39 branch for each file:

- `reports/FINAL_REPORT.md`: `79462a8e4eaa941050e32e4b2fb605287ca275273bde39a2652a46fb7a55d8e6`. Matches `preserved-records.json`.
- `reports/USER_ACTIONS_REQUIRED.md`: `70762916c660dc0266ed95cb95cef67002e6af0bcf63c40e9402e2bd1222453a`. Matches.
- `reports/user-actions.json`: `4d5efd2f4a883b4084de5e3a1a59f44be574728286c9024d3a0305d910562391`. Not listed in the manifest.
- `docs/metadata/preserved-records.json`: `7ce2f2e6f927f3d6dfa07883e43275c659c8046a2ee6ecc0e1d19aa2e68922bc`.

### Three-phase status

- **Phase A (engineering):** B1 (T-16 pin, prepared, not applied), B3 (review-notes, done on the candidate), B7 and B8.
- **Phase B (completion):** the owner items UA-7, UA-3 baseline and UA-2, all actionable now; plus the autonomous tasks B2, B4, B5, B6, B9 and B10.
- **Phase C (independent acceptance):** UA-3 full rules, UA-1, UA-6 and UA-5, all blocked; plus the reviewer's pin re-review and SHA review.
- **Sequencing correction** (baseline ruleset now; approvals and required checks deferred until Phase C readiness): **Owner directive relayed to Final Report worker on 2026-11-03 18:13 ET via orchestration chat; not yet recorded in repo.** No matching record exists in `coordination/tasks.json@0ad0468`, `coordination/INTEGRATION_MANIFEST.*@0ad0468`, `coordination/PR_DISPOSITIONS.md@0ad0468`, `coordination/T16_RECONCILIATION.md@0ad0468` or the PR #42 body. It is not a signed approval.
- **Live owner-item recheck:** `GET /rulesets` → `[]`. Both branches are unprotected. Collaborators `["onnxscibroccoli"]`. Invitations: 0. PR #4 has 0 comments.

**USER ACTION REQUIRED: 3 — UA-7 invite an independent reviewer; UA-3 baseline ruleset; UA-2 confirm the Entra baseline.** Details are in [HUMAN_DECISION_PACKET_2026-11-03.md](HUMAN_DECISION_PACKET_2026-11-03.md). Reviewer materials are in [PHASE_C_REVIEW_PACKAGE_PREP_2026-11-03.md](PHASE_C_REVIEW_PACKAGE_PREP_2026-11-03.md).

## Update at `main` `8e2df97` (17:36–17:45 EST, kept for history)

### Main (STATIC)

`main` has not moved: `8e2df97b558e69032e52a50ed0adfd311ad04578` (`GET /repos/onnxscibroccoli/bank-it-operations-lab/commits/main`, 17:36 EST). Nothing new to merge into PR #39.

### Consolidated candidate: CANDIDATE, not integrated (STATIC + EXECUTED)

Sources: `git ls-remote` branch list; `GET /pulls?state=all&head=onnxscibroccoli:integration/candidate-20261103b` → `[]`; `GET /actions/runs?head_sha=<sha>`; `coordination/INTEGRATION_MANIFEST.md@caa9ce7`.

- **Branch:** `integration/candidate-20261103b` @ `caa9ce7c1b1538d8da920463db77c93c05fe882b` (17:32 EST). It is 32 commits ahead of `main` and 0 behind, and changes 51 files. **No PR is open for it.**
- **Owner directive t26u (17:00 EST):** "Do not merge into `main`" until AC1 independent review and the gate-pin re-review are done.
- **What it consolidates:**
  - review records from PRs #14 and #27–#34
  - PR #41 @ `d8d7711`
  - **PR #39 @ `42d8e96`**, the 30e0a83-era sidecar, not the current head
  - review-notes registry work re-applied from `integration/completion-20261103` (@ `3c417d9`, not merged wholesale)
  - two CI-flake fixes
  - an **UNREVIEWED, not applied** gate-pin proposal, gate_sha `a518b03`
- **Sidecar coverage on the candidate** (`git rev-parse caa9ce7:<path>`; `coordination/modules.json@caa9ce7`; `docs/metadata/pages.json@caa9ce7`):
  - `reports/HUMAN_DECISION_PACKET_2026-11-03.md` is **missing**.
  - `reports/COMPLETION_PASS_2026-11-03.md` (`f1be850`) and `reports/completion-pass-2026-11-03.json` (`55f51c2`) are the `42d8e96` versions describing `main` `30e0a83`.
  - In `final-report.paths`, the packet is missing.
  - In `pages.json`, the packet entry is missing, and the COMPLETION_PASS entry is the 30e0a83 one.
  - Carrying them over is integrator task B4 in the decision packet.
- **Registry on the candidate:** 27 INTEGRATED, 1 SUPERSEDED (as claimed in its manifest).
- **Locked files on the candidate:** `reports/FINAL_REPORT.md`, `reports/USER_ACTIONS_REQUIRED.md` and `reports/user-actions.json` are identical to `main` (`git diff origin/main caa9ce7`). `docs/metadata/preserved-records.json` is changed **append-only**: 10 new review-record entries, with no existing hash altered.
- **Tested SHA `308512714690ba20a6d9003fcd0731b88fffd596`:**
  - success: acceptance [41731058945](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731058945), offline-validation [41731065623](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731065623), aws-cdk [41731069473](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731069473), postgres-restore-evidence [41731073799](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731073799), portfolio-validation [41731076403](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731076403), Documentation [41731137053](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731137053)
  - **failure:** integration-gate [41731062507](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731062507). In `merge-eligibility`, the stale `test_module_coverage.py` pin and the new `scripts/ci` files are not in the trusted manifest.
- **Head `caa9ce7`** (a records-only commit): Documentation [41731695130](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731695130) and offline-validation [41731694035](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731694035) both succeed.

**Other open PRs since the last read** (`GET /pulls?state=open&sort=created`):

- [PR #42](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/42) (`acceptance/t16-pin-review` @ `9589d89`, opened 17:08 EST, not draft):
  - It is a T-16 stale-pin review package, a proposal only, with ruleset JSON prepared but not activated.
  - Checks: 37 pass, 1 skipped, `merge-eligibility` fails ([job](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41728197004/job/126240348994)). Reviews: 0.
- [PR #41](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/41) now has head `70535c5` (draft).
  - Checks: 37 pass, 1 skipped, `merge-eligibility` fails ([job](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41728066988/job/126239935831)). Reviews: 0.
- **Totals:** 42 PRs. Reviews: 0 (`GET /pulls/<n>/reviews`, every PR). Issue comments: 11, with 0 `ACCEPTANCE-*` decisions.

### Locked files, rechecked (STATIC)

At 17:37 EST, sha256 on `main@8e2df97` equals sha256 on the PR #39 branch for each file. All four are unchanged since the earlier read:

- `reports/FINAL_REPORT.md`: `79462a8e…d8e6`. Matches `preserved-records.json`.
- `reports/USER_ACTIONS_REQUIRED.md`: `70762916…453a`. Matches.
- `reports/user-actions.json`: `4d5efd2f…2391`. Not in the manifest; identical to `main`.
- `docs/metadata/preserved-records.json`: `7ce2f2e6…22bc`. Identical to `main`.

### Live recheck of owner items (STATIC)

- **Protection:** `GET /rulesets` → `[]`. `main` and `evidence/acceptance` protection both return 404. `evidence/acceptance` head is `750de1c`.
- **Access:** collaborators `["onnxscibroccoli"]`. Invitations: 0.
- **Entra baseline:** `evidence/entra/BASELINE-CHOICES-PENDING.md@8e2df97` is still not confirmed. PR #4 has 0 comments.
- **Exceptions:** EX-01..EX-04 are still PROPOSED (`evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md@8e2df97`).
- **User actions:** `tasks.json` on both `main@8e2df97` and the candidate `caa9ce7` shows UA-2/3/7 OPEN, UA-1/5/6 NOT_YET_ACTIONABLE, and UA-4 RESOLVED.

### Outstanding decisions

**USER ACTION REQUIRED: 3 — UA-7 invite an independent reviewer; UA-3 baseline ruleset (no deletion, no force-push) on `main` and `evidence/acceptance`; UA-2 confirm the Entra baseline.**

- **Blocked owner decisions:** the full UA-3 rules, UA-1, UA-6 and UA-5.
- **Autonomous engineering tasks:** B1–B8.
- Both lists, with recommendations, risks and exact actions, are in [HUMAN_DECISION_PACKET_2026-11-03.md](HUMAN_DECISION_PACKET_2026-11-03.md), sections A and B.

## Read at `main` `8e2df97` (16:55–17:05 EST, kept for history)

### What PR #40 changed (STATIC)

Source: `GET /repos/onnxscibroccoli/bank-it-operations-lab/pulls/40`; `git diff --stat 30e0a83 8e2df97`.

- [PR #40](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/40) ("acceptance: integration v2 on current main (A contract, B runner, C adapters, D gate; fail-closed v2; never ACCEPTED)") was merged by `onnxscibroccoli` on 2026-11-03 at 14:30 EST. The merge commit `8e2df97` has parents `30e0a83` (old `main`) and `8c662d7` (#40 head). It brings in 26 commits and changes 111 files (+15,575 / −18).
- **What it adds:**
  - `tools/acceptance/` (runner and the gate in `tools/acceptance/gate/`)
  - `acceptance/modules/` (aws-cdk, postgres, entra-offline adapters and `emit_shared.py`)
  - `schemas/acceptance/`
  - `tests/acceptance-contract/` (fixtures and tests)
  - the `scripts/acceptance/run.sh` compatibility shim
  - `.github/workflows/acceptance.yml`
  - `acceptance/INTEGRATION-V2.md`
  - `reports/ACCEPTANCE.md`
  - `reports/ACCEPTANCE_INVARIANT_ASSURANCE.md`
- **Metadata:** it registers module `acceptance` as `INTEGRATED` in `coordination/modules.json` (prs 23–26, record `acceptance/INTEGRATION-V2.md`). It updates one assertion in `scripts/ci/tests/test_module_coverage.py` and adds `docs/metadata/pages.json` entries.
- [PR #26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26) (`acceptance/vertical-slice`) now shows as merged (2026-11-03 14:30 EST) because its head is contained in `main`.
- The gate it adds stops at `EXECUTION_PASS` + `REVIEW_PENDING` and has no ACCEPTED state (`coordination/modules.json@8e2df97`, module `acceptance`, `limitations`).

### Preserved records (STATIC)

Each locked file on PR #39's merged head is byte-identical to `main@8e2df97`, with the same git blob. Its sha256 equals the value in `docs/metadata/preserved-records.json@8e2df97`.

| File | git blob | sha256 | Matches `preserved-records.json` |
|---|---|---|---|
| `reports/FINAL_REPORT.md` | `e6f97a7d264798a4ae4188d19b27cfc6e0838bfa` | `79462a8e4eaa941050e32e4b2fb605287ca275273bde39a2652a46fb7a55d8e6` | yes |
| `reports/USER_ACTIONS_REQUIRED.md` | `3516dcfbd633c1f70ced41cc1c45f352d537033c` | `70762916c660dc0266ed95cb95cef67002e6af0bcf63c40e9402e2bd1222453a` | yes |
| `reports/user-actions.json` | `dcc3f0835d96b6d25718e505e6d94518bd8653ad` | `4d5efd2f4a883b4084de5e3a1a59f44be574728286c9024d3a0305d910562391` | not listed in the manifest (it lists `.md` records). Its blob is identical to `main` |
| `docs/metadata/preserved-records.json` | `426bb3f4550e9476c7ac06ae57a7030d41284a29` | `7ce2f2e6f927f3d6dfa07883e43275c659c8046a2ee6ecc0e1d19aa2e68922bc` | n/a (the manifest itself). Its blob is identical to `main` |

None of these files was modified. Their last change on `main` is `58aaa94` (`git log origin/main -- <files>`).

### Module coverage (STATIC + EXECUTED)

- `coordination/modules.json@8e2df97` lists 28 modules:
  - 26 `INTEGRATED`
  - 1 `NOT_INTEGRATED`: `review-notes`, review records kept on their own branches by plan
  - 1 `SUPERSEDED`: `bank-aws-001`, superseded by `aws-cdk`
- The `module-registry` job in run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441) printed (EXECUTED): `MODULE COVERAGE: 26/27 integrated (96.3%), functional 19/19; denominator 28 (INTEGRATED=26, NOT_INTEGRATED=1, SUPERSEDED=1)`. That is up from 25/27 at `30e0a83`; the change is the `acceptance` module.
- `coordination/tasks.json@8e2df97` user actions:
  - **OPEN:** UA-2, UA-3, UA-7
  - **NOT_YET_ACTIONABLE:** UA-1, UA-5, UA-6
  - **RESOLVED:** UA-4 (PR #1 closed)
- "Integrated" means present on `main` and registered. It does not mean reviewed: `final-report` still records `review_status: UNREVIEWED_DELIVERY_CANDIDATE`.

### Actions runs on `main` at `8e2df97` (EXECUTED)

Source: `GET /repos/onnxscibroccoli/bank-it-operations-lab/actions/runs?head_sha=8e2df97b558e69032e52a50ed0adfd311ad04578`.

| Workflow | Run | Event | Result |
|---|---|---|---|
| integration-gate | [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441) | push | **failure**: 19 of 20 jobs succeed, including `final-summary`, `aws-cdk / synth-and-test` and all five `postgres / *` jobs. `merge-eligibility` fails |
| acceptance | [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024) | push | success. Gate output: `decision: REVIEW_PENDING (execution=EXECUTION_PASS, contract=BLOCKED, reviews=0)`. The defect control (CA002 forced report-only) reports `execution: FAIL`, as designed |
| offline-validation | [41703901993](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703901993) | push | success |
| Documentation knowledge base | [41703901979](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703901979) | push | success |
| aws-cdk, postgres-restore-evidence | no standalone run at `8e2df97` | — | Their jobs ran inside integration-gate 41703902441 (success) |
| portfolio-validation | no run at `8e2df97` | — | By design: `.github/workflows/portfolio-validation.yml` triggers on push to `delivery/**` and on PRs, not on push to `main`. It runs on PR #39 |

`merge-eligibility` (job 126154892822) prints `ERROR candidate: scripts/ci/tests/test_module_coverage.py differs from the trusted manifest (candidate modifies the verifier without a matching trusted update)`. The trusted manifest is read from `evidence/acceptance` (head `750de1c694c4912f12bb5bb76a20ba74bc208213`). PR #40 changed that test file, so the gate never reached an ELIGIBLE decision for `8e2df97`. Updating the trusted manifest is reviewed integrator work, not a user step. At `30e0a83` the same job failed for the same reason (manifest drift), with a longer file list.

`user-actions` and `module-registry` both print `USER ACTION REQUIRED: 3 — UA-2; UA-3; UA-7`.

### PR states and reviews (STATIC)

Source: `GET /pulls?state=all`, `GET /pulls/<n>/reviews` for every PR, `GET /issues/comments`, `GET /pulls/comments`.

- 41 PRs in total:
  - **Merged (13):** #2, #3, #4, #5, #7, #20, #22, #26, #35, #36, #37, #38, #40
  - **Closed, not merged (1):** #1
  - **Open (27):** #6, #8–#19, #21, #23–#25, #27–#34, #39 (this PR, draft) and #41
- [PR #41](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/41) (`docs-platform`, draft, opened 2026-11-03 13:42 EST) is new since the earlier read.
- #23, #24 and #25 remain open even though `modules.json` lists them in `acceptance.superseded_prs`. Closing them is housekeeping, not a user action.
- **Reviews: 0** across all 41 PRs. **Inline review comments: 0.**
- Issue/PR comments: 11 (latest 2026-10-29 23:15 EDT). None begins with `ACCEPTANCE-DECISION` or `ACCEPTANCE-ATTESTATION`.
- Collaborators: `onnxscibroccoli` (admin) only. Pending invitations: 0 (`GET /collaborators`, `GET /invitations`).

### Branch protection and rulesets (STATIC)

| Check | Result |
|---|---|
| `GET /branches/main/protection` | 404 "Branch not protected" |
| `GET /branches/evidence%2Facceptance/protection` | 404 "Branch not protected" |
| `GET /branches/main` | `protected: false` |
| `GET /branches/evidence%2Facceptance` | head `750de1c`, `protected: false` |
| `GET /rulesets` | `[]` |
| CODEOWNERS | none at `.github/CODEOWNERS`, `CODEOWNERS` or `docs/CODEOWNERS` on `8e2df97` |

The repository is public and user-owned, so rulesets are available (`GET /repos/onnxscibroccoli/bank-it-operations-lab`: `visibility: public`).

### Exceptions EX-01..EX-04 as on `main` (STATIC)

Source: `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md@8e2df97`. The file is unchanged by #40.

The register says: "Status of every entry: **PROPOSED, pending owner approval.**" `evidence/backup/aws-backup-dr/SECURITY_EXCEPTIONS.md@8e2df97` has the same status line for its own entries.

| ID | Scope on `main` | Status on `main` | Ian's relayed position (2026-10-28, conversation only, not recorded in the repo as approval) |
|---|---|---|---|
| EX-01 | NIST S3DefaultEncryptionKMS on `AccessLogsBucket` (SSE-S3) | PROPOSED | Acceptable for the lab, pending verification of the bucket policy |
| EX-02 | NIST S3BucketReplicationEnabled on `AccessLogsBucket`, `DataBucket` | PROPOSED | Acceptable as an explicit limitation. Reject the claim that env-agnostic makes a reference implementation impossible |
| EX-03 | AwsSolutions-IAM5 `log-group:RDSOSMetrics:log-stream:*` on `RdsMonitoringPolicy` | PROPOSED | Needs exact verification of the wildcard's scope |
| EX-04 | AwsSolutions-IAM5 `snapshot:awsbackup-*` on `DbBackupPolicy` (replaces the earlier AWS-managed policy form) | PROPOSED | "AWS-managed policy OK after role review" was given for the old scope. The managed policy is gone, so that position does not carry over |

`coordination/tasks.json@8e2df97` UA-1: "Exceptions remain proposed; EX-04 runtime role trust unverified."

### Limitations

- No independent review exists for any merged code (0 reviews). `main` carries code merged under the owner's 2026-10-31 development-integration directive (PR #35 body).
- `merge-eligibility` fails on `main` because of trusted-manifest drift, so no SHA on `main` has a gate ELIGIBLE decision.
- The acceptance gate ends at `REVIEW_PENDING`, with contract `BLOCKED` and 0 reviews. Nothing is ACCEPTED.
- `main` and `evidence/acceptance` are unprotected, so every gate is advisory.
- All evidence is offline or CI-only. AWS, Entra and M365 targets were never deployed or queried live (NOT_EXECUTED for live targets). Incident and vendor demos are SIMULATION.
- EX-01..EX-04 are PROPOSED. The Entra baseline is unconfirmed (`evidence/entra/BASELINE-CHOICES-PENDING.md@8e2df97`).

### Outstanding decisions and USER ACTION REQUIRED

**USER ACTION REQUIRED: 3 — UA-2 Entra baseline; UA-3 protect `main` and `evidence/acceptance`; UA-7 invite an independent reviewer.** This matches `coordination/tasks.json@8e2df97` and run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441). Each item was rechecked live at 16:55–17:05 EST, and none is resolved.

- **Not yet actionable (not counted):** UA-1 (EX-01..EX-04), UA-5 (AC6 final acceptance), UA-6 (owner signing key).
- **Integrator work (not user actions):**
  - the trusted-manifest update for `merge-eligibility`
  - closing superseded #23–#25
  - the integrator handoff for this documentation
- For options, recommendations, risks and exact steps, see [HUMAN_DECISION_PACKET_2026-11-03.md](HUMAN_DECISION_PACKET_2026-11-03.md).

## Earlier read at `main` `30e0a83` (13:22–13:26 EST, superseded; kept for history)

All facts below come from GitHub API and Actions log checks on 2026-11-03 between 13:22 and 13:26 EST (UTC-5). Times from October 31 are given in EDT (UTC-4), which was still in effect then. 

### Main and what merged since `7f50348`

- **`main` = `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6`.** It is the merge commit of [PR #35](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/35) (`delivery/portfolio` → `main`), merged by `onnxscibroccoli` on 2026-10-31 at 17:09 EDT. `main` is 71 commits ahead of `7f50348` and 0 behind. Its tree is identical to #35's head `aa6a38b` (compare: 0 files changed).
- **Merged** (state MERGED; all merged 2026-10-31 between 17:03 and 17:09 EDT, by `onnxscibroccoli`, through #35):
  - #35, which went to `main`;
  - #36, #37 and #38, which went into `delivery/portfolio`;
  - #7 (head `a9d0f64`), #2, #3, #4, #5, #20 and #22. These show as merged because their head commits are contained in `main`.
- **Closed, not merged:** #1, on 2026-10-29 (superseded by #5).
- **Still open:** #6, #8–#19, #21 and #23–#34. That includes this report's old PR #11 (head `d500ccf`) and the review-note PRs #14 and #27–#34.
- **PR #35 states the basis for the merge:** "The repository owner explicitly directed development integration before independent review on 2026-10-31. Independent review remains deferred and has not been represented as completed. This merge is development integration, not production approval."

### Actions runs on `main` at `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6` (post-merge verification)

| Workflow | Run | Event | Result |
|---|---|---|---|
| integration-gate | [41242239019](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242239019) | push | **failure**: 19 of 20 jobs succeed, including `final-summary`; `merge-eligibility` fails |
| aws-cdk | [41242238866](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242238866) | push | success |
| postgres-restore-evidence | [41242238836](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242238836) | push | success |
| offline-validation | [41242238892](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242238892) | push | success |
| Documentation knowledge base | [41242238902](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242238902), [41242873936](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242873936), [41243377081](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41243377081) | push, workflow_dispatch ×2 | success (`validate`, `deploy`). GitHub Pages is live at <https://onnxscibroccoli.github.io/bank-it-operations-lab/> |
| portfolio-validation | **no run at the `main` SHA** | — | The last runs were on #35's head `aa6a38b`, which has the same tree: [41242207712](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242207712) (push) and [41242212716](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242212716) (pull_request), both success. That counts as verification of the same tree, not a run on `main` |

The integration-gate run on `main` prints these lines:
- `MODULE COVERAGE: 25/27 integrated (92.6%), functional 18/19; denominator 28 (INTEGRATED=25, NOT_INTEGRATED=2, SUPERSEDED=1)`
- `USER ACTION REQUIRED: 3 — UA-2; UA-3; UA-7`

`merge-eligibility` ran the trusted gate `af49a27` and failed with `ERROR candidate: scripts/ci/… differs from the trusted manifest`. The files named are `provenance.py`, `reviews.py`, five gate tests, and three new portfolio scripts that are not in the manifest. **The gate never reached an ELIGIBLE decision for the merged code.** The merge happened outside the gate, on the owner's development-integration directive.

### Review, protection, exceptions, identity and decisions

| Item | Live evidence | State |
|---|---|---|
| Reviewer approvals | `GET /pulls/<n>/reviews` for every PR #1–#38 returns **0 reviews**. The only collaborator is `onnxscibroccoli` (admin), and there are no pending invitations | **No independent approval exists.** AC1/G1 were not met for the merged code |
| Branch protection / rulesets | `GET /branches/main/protection` → 404 "Branch not protected". `GET /branches/evidence%2Facceptance/protection` → 404. `GET /rulesets` → `[]`. `branches/main.protected = false` | **Unprotected** |
| Exception register on `main` (`evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md`) | "Status of every entry: **PROPOSED, pending owner approval.**" There are no per-entry status lines. EX-04 is now re-scoped: AwsSolutions-IAM5 `snapshot:awsbackup-*` on `DbBackupPolicy`, replacing the earlier IAM4 managed-policy form | **EX-01..EX-04 PROPOSED**; none approved. The conditional decisions Ian relayed on 2026-10-28 (section 3 of [USER_ACTIONS_REQUIRED.md](USER_ACTIONS_REQUIRED.md)) stay conditional. EX-04's scope changed after that relay, so the relayed EX-04 condition does not carry over automatically |
| Entra baseline | `evidence/entra/BASELINE-CHOICES-PENDING.md` on `main`: "**have not been confirmed by the owner**". PR #4 has 0 comments | **Pending** (UA-2) |
| Acceptance decision comments | All 11 issue and PR comments in the repo were read (10 on #7, 1 on #11; all by `onnxscibroccoli`). **None** begins with `ACCEPTANCE-DECISION` or `ACCEPTANCE-ATTESTATION`. Comments on #7 marked "Checkpoint only. Not a review, not an approval" are status notes. There are 0 inline review comments | **No recorded acceptance decision** |
| `coordination/tasks.json` on `main` | UA-1 NOT_YET_ACTIONABLE (exceptions; "effective approval awaits the final bound packet and reviewed owner-authentication path"). UA-2 OPEN. UA-3 OPEN. UA-4 RESOLVED (PR #1 closed). UA-5 NOT_YET_ACTIONABLE (AC6). UA-6 NOT_YET_ACTIONABLE (owner signing key). UA-7 OPEN (independent reviewer) | Matches the CI top line |

### Remaining human steps

**USER ACTION REQUIRED: 3 — UA-2 Entra baseline; UA-3 protect main and evidence/acceptance; UA-7 invite an independent reviewer.** This matches the integration-gate run on `main` ([41242239019](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242239019)). Each item was checked live on 2026-11-03 at about 13:25 EST.

| ID | Action | Live evidence it is still open | How |
|---|---|---|---|
| **UA-2** | Confirm or change the lab's Entra CA baseline: risk policies report-only, device compliance on All users / All apps, 12 privileged roles | `BASELINE-CHOICES-PENDING.md` on `main` says not confirmed. PR #4 has 0 comments | [USER_ACTIONS_REQUIRED.md](USER_ACTIONS_REQUIRED.md) section 4 |
| **UA-3** | Protect `main` and `evidence/acceptance` | Both return 404 "Branch not protected"; rulesets `[]` | [USER_ACTIONS_REQUIRED.md](USER_ACTIONS_REQUIRED.md) section 2. `main` now carries merged code, so protection affects every future change |
| **UA-7** | Invite a qualified independent human reviewer and give their exact GitHub username | Collaborators: only `onnxscibroccoli`; 0 invitations; 0 reviews on PRs #1–#38 | [USER_ACTIONS_REQUIRED.md](USER_ACTIONS_REQUIRED.md) section 1 |

**Waiting, not yet actionable** (`tasks.json` on `main`; not counted):
- **UA-1:** EX-01..EX-04 are all PROPOSED on `main`. EX-04 was re-scoped after the 2026-10-28 relay, so Ian's earlier conditional decision on EX-04 needs a fresh look against the new scope. The gate says effective approval needs the bound packet and a reviewed owner-authentication path.
- **UA-5:** final human portfolio acceptance (AC6).
- **UA-6:** enroll an owner signing key after the activation design is reviewed.

**Facts to know, not actions:**
- The code is already on `main` without independent review, by Ian's 2026-10-31 development-integration directive.
- The gate on `main` reports `merge-eligibility` failing, because candidate gate files differ from the trusted manifest. That is engineering work for the integrator, not a user step.
- portfolio-validation has not run at the `main` SHA itself; it ran on the identical tree at `aa6a38b`.
