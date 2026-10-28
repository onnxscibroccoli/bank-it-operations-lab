# FINAL REPORT: bank-it-operations-lab

- Repo: https://github.com/onnxscibroccoli/bank-it-operations-lab
- Snapshot: 2026-10-28, about 14:10 EDT (UTC-4). `main` @ [`7f50348`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/7f50348bf1370381615eaed91c02607fe41de2f5) holds only `README.md`.
- **Nothing is merged into `main`. Nothing is deployed. No AWS, Entra or Graph credentials were used.** Every PR (#1–#9) is an open draft. None has a GitHub review or a comment.
- **Rule for this report:** a claim counts as verified only if it links to an Actions run, PR or commit, or if the reporting agent re-ran it on the box for this report (marked **[re-run]**). Anything else is marked **UNVERIFIED**. A claim that comes only from a PR body is marked **[PR body]**.
- The evidence index, with SHA-256 hashes and run URLs, is in [`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md). Blockers are in [`USER_ACTIONS_REQUIRED.md`](USER_ACTIONS_REQUIRED.md).

## Acceptance criteria used
Each workstream was judged against six criteria:
1. A PR exists on a pushed branch.
2. Its evidence `SHA256SUMS` verifies.
3. Its tests, synth or validators pass on re-run.
4. It has CI, and the latest CI run is green.
5. No open blocking review finding remains.
6. A human has reviewed and approved it.

None of the workstreams meets criterion 6. The repo README lists no tasks and the repo has no issues, so the assignment list below comes from the PRs and branches and from the teammate roles named in the brief: PR reviewer, AWS remediation, backup/DR and portfolio cases.

## Status of all assignments

| # | Assignment | PR / branch @ head | CI | Re-run on box for this report | Status |
|---|---|---|---|---|---|
| 1 | BANK-AWS-001 secure storage stack | [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) `bank-aws-001` @ [`e494bcf`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/e494bcfc3986c2d21a4cf92453857f69dbf69ce3) | 4/4 runs succeeded. Latest is [40631310661](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631310661) | **[re-run]** SHA256SUMS 87/87 OK; tsc 0; Jest 21/21; synth 0; synth equals the committed template apart from CDK metadata/path | **RED (superseded).** `AccessLogsBucket` logs to itself. **[re-run]** `cfn-s3-selflog` → ERROR. Replaced by #5 in #7 |
| 2 | Postgres backup/restore exercise | [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) `ci-evidence-postgres` @ [`e7399fb`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/e7399fbb53) | Latest runs [40741546543](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741546543) and [40741536430](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741536430) succeeded. The earlier runs [40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041) and [40630876341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630876341) **failed** | **[re-run]** SHA256SUMS verifies for all 8 hashed run dirs | **GREEN in CI, needs reconciliation.** Harness v2 (`2aac93c`, `e7399fb`) was pushed after #7 integrated `e610015`, so #2 and #7 now differ in `tests/integration/postgres/**`. The PR body is stale |
| 3 | PR reviewer: evidence audit of #1/#2 and shared validator | [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) @ [`fb36341`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/fb3634115cb22b26e717afe2caec69661f56e874) | No CI on the PR branch. The checks run in #7's `offline-validation` ([40741463837](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741463837): success) | **[re-run]** unittest 13/13 OK | **GREEN, not reviewed** |
| 4 | Entra Conditional Access offline validation | [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) @ [`d302c99`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/d302c99d95116c39d7aa65937614bccb830f2d6e) | No CI on the PR branch. Covered by #7's `offline-validation`: success | **[re-run]** unittest 25/25; validator exit 0; `generate_evidence.py --verify` OK; SHA256SUMS 46/46 | **GREEN.** The owner must confirm the baseline choices |
| 5 | AWS remediation: private VPC + RDS, no S3 self-logging, NIST nag | [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) @ [`099479e`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/099479e6d23968adb17762d88d84131998fca07c) | No CI on the PR branch. Covered by #7's `aws-cdk` ([40741463903](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741463903): success) | **[re-run]** SHA256SUMS 32/32; tsc 0; Jest 33/33 (`--runInBand`); synth 0; both templates match the committed ones apart from CDK metadata/path; `cfn-s3-selflog` OK | **GREEN.** EX-01..EX-04 are pending approval |
| 6 | Organizations security reference (OUs, SCPs, org trail, GuardDuty, Security Hub) | [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) @ [`e5e7f46`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/e5e7f4604597c7e6e35e69bf0607fe0535d4cdab) | **No CI** | **[re-run]** SHA256SUMS 66/66; tsc 0; Jest 49/49 (`--runInBand`); synth 0; 3 templates match apart from CDK metadata/path | **RED.** `TrailAccessLogsBucket` logs to itself. **[re-run]** `cfn-s3-selflog` → ERROR `TrailAccessLogsBucket30C0D746`. Not integrated |
| 7 | Integration branch (#3, #5, #4, #2; #1 superseded; #6 held) | [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) `overnight/integration` @ [`876f7b7`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/876f7b79accc6a297bd7f3839e91c0ec546661cb) | 6/6 runs succeeded: aws-cdk [40741463903](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741463903) and [40741456368](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741456368); offline-validation [40741463837](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741463837) and [40741456395](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741456395); postgres [40741464144](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741464144) and [40741456056](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741456056) | **[re-run]** Postgres SHA256SUMS verifies for its 3 run dirs. The full `scripts/validate-all.sh` was **not** re-run | **GREEN in CI.** Needs a human review, and harness v2 from #2 still has to be brought in |
| 8 | Portfolio case studies | [#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8) `portfolio-cases` @ [`6c25c05`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/6c25c05f3c1608bc2fd6427afb3bdbd4cada3571) | Docs only, no CI | The links and SHAs cited in the case studies were **not** re-checked | **UNVERIFIED** (draft docs, 6 files) |
| 9 | Vendor mock (SIMULATION) and vendor-risk/RACI governance | [#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) `vendor-mock` @ [`c1ec227`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/c1ec227aa11bd547b5edb08a863f311e959eee5d) | **No CI** | **[re-run]** unittest 45/45 OK; `generate_evidence.py --verify` PASS; SHA256SUMS 12/12 | **GREEN locally, not in CI.** Labeled as a simulation; no real-vendor compatibility is claimed |
| 10 | Backup/DR (AWS) | **No PR or remote branch.** There is a local box worktree `/workspace/bkp-dr-aws-worker` on branch `backup-dr-aws` with 0 commits and an untracked `backup/` directory | None | Not verifiable | **MISSING.** The work is uncommitted or unpushed. No results can be claimed |
| 11 | Final report (this PR) | `reports/final-report` | None | — | Draft |

## Verified results in detail

### CI (GitHub Actions; all times EDT)
- `bank-aws-001-cdk` succeeded on 4 runs, 00:07–00:16 EDT: [40630567160](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630567160), [40630990406](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630990406), [40631120535](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631120535) and [40631310661](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631310661).
- `postgres-restore-evidence` on `ci-evidence-postgres`:
  - Runs [40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041) and [40630876341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630876341) at `daf8d82` **failed** (00:10–00:11 EDT).
  - Runs [40631027885](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631027885) and [40631034518](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631034518) at `e610015` succeeded.
  - Runs [40741329107](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107) and [40741338458](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741338458) at `2aac93c` succeeded (14:02 EDT).
  - Runs [40741536430](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741536430) and [40741546543](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741546543) at `e7399fb` succeeded (14:03 EDT).
- On `overnight/integration` at `876f7b7`, `aws-cdk`, `offline-validation` and `postgres-restore-evidence` all succeeded on both push and pull_request (6 runs, 14:03 EDT).
- PRs #3, #4, #5, #6, #8 and #9 have **no Actions runs of their own**.

### Re-run on the box for this report (Node 20.19.2, Python 3.13.5; AWS config and credentials files set to /dev/null, IMDS disabled)
- **SHA256SUMS:** every committed bundle verifies with `sha256sum -c`: #1 (87 entries), #2 (8 hashed run dirs), #4 (46), #5 (32), #6 (66), #7 (3 Postgres runs) and #9 (12).
- **CDK:**
  - `npm ci`, `tsc --noEmit` and `cdk synth --no-lookups` exit 0 on #1, #5 and #6.
  - Jest: #1 21/21, #5 33/33, #6 49/49.
  - On the first attempt, #5 and #6 lost suites to jest workers killed by SIGKILL while three builds ran in parallel on the box. Both passed in full when re-run with `--runInBand`. This was a box resource limit, not a test failure.
- **Synth reproducibility:** each re-synthesized template matches the committed evidence once the `CDKMetadata` resource and condition and the `aws:cdk:path` metadata are removed. The byte-level differences come from the evidence being generated with metadata turned off.
- **Python:**
  - #3: 13/13.
  - #4: 25/25, validator exit 0, evidence verify OK.
  - #9: 45/45, evidence verify PASS.
- **S3 self-logging gate** (`evidence/shared/validate_evidence.py cfn-s3-selflog`):
  - #1 template: **ERROR** (`AccessLogsBucket83982689`).
  - #6 org trail template: **ERROR** (`TrailAccessLogsBucket30C0D746`).
  - #5 template: OK (2 buckets).

### Review findings carried forward
These come from [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) `reports/review-pr1-pr2.md` and from #7 `reports/INTEGRATION.md`; this report did not re-derive them.
- #1: S3 self-logging, which is confirmed above. Rated "accept with changes", then superseded by #5.
- #2 at `e610015`: the committed failing CI run `ci-service-40630856041-1` records 4 false PASSes on negative tests (N01, N04, N05, N06).
  - #2's own run index now marks that run **HISTORICAL-KNOWN-INVALID**.
  - Harness v2 runs (`ci-service-40741329107-1`: 36/36; `ci-offline-…`: 38/38) are labeled CURRENT **[PR branch INDEX.md]**.
- #6 repeats the self-logging defect, which is confirmed above.

## Not verified / known gaps
- Nothing was deployed. No live AWS, Entra or Graph state was checked, and no compliance certification is claimed.
- cdk-nag counts (for example #5: 0 unsuppressed errors in both packs) are **[PR body]** plus the committed CSVs. The re-run synth here did not re-check the nag counts separately.
- The parliament/SCP lint results for #6 are **[PR body]** only.
- The portfolio (#8) citations were not re-checked.
- Backup/DR: no evidence exists in the repo.
- Actions are pinned by tag, not SHA **[#7 INTEGRATION.md]**.
- No PR has a human GitHub review.
