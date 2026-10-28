# FINAL REPORT: bank-it-operations-lab

> **DEADLINE: midnight ET (00:00 EDT, Thursday 2026-10-29), the end of Wednesday 2026-10-28.**
> **Remaining window at commit time (2026-10-28 14:18 EDT): about 9 h 41 min.**
> Status: **not complete.** Nothing is merged into `main`, and no workstream meets every acceptance criterion. Nothing here claims completion that was not verified.

- Repo: https://github.com/onnxscibroccoli/bank-it-operations-lab
- Snapshot: 2026-10-28, about 14:18 EDT (UTC-4). Refreshed for integration head `afb41278`. `main` @ [`7f50348`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/7f50348bf1370381615eaed91c02607fe41de2f5) holds only `README.md` and has not changed since the repo was created.
- **Nothing is merged into `main`. Nothing is deployed. No AWS, Entra or Graph credentials were used.** All 20 PRs (#1–#20) are open drafts, plus one branch with no PR (`backup-dr-aws`), and none has a GitHub review (an approval or request for changes).
- **Evidence labels:**
  - **[re-run]**: re-executed on the box for this report.
  - **[CI]**: a linked GitHub Actions run.
  - **[#14 review]**: the independent review notes in [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) (`reports/review-pr3-pr6.md` @ `981db0a`, which includes checkpoint 1). They were written by a reviewer who is neither the code author nor this automation. They are **not** a GitHub review and **not** a human sign-off.
  - **[PR body]**: taken from the PR text only.
  - **UNVERIFIED**: not checked.
- **Rule: a passing scanner is not enough.** Zero cdk-nag errors, a passing `cfn-s3-selflog` or a passing `sha256sum -c` shows only that a tool ran. Acceptance also needs review of the exact SHA, adjudicated exceptions, docs that match the code, and no blocking findings. #5 is the example: both cdk-nag packs report 0 unsuppressed errors, yet #14 found a KMS privilege-escalation path that the scanner and the repo's own guard (`guards.ts#kmsWildcards`) both miss.
- Companion files: [`USER_ACTIONS_REQUIRED.md`](USER_ACTIONS_REQUIRED.md) and [`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md).

## 1. Per-module acceptance: 5 criteria
- **C1 Review:** an independent reviewer examined the **exact current head SHA**. A human GitHub review is still needed for merge (G1 below).
- **C2 Exceptions:** every suppression, allowlist entry or policy choice is adjudicated by the owner.
- **C3 Checks:** CI and/or a local re-run passes on that SHA, including negative tests that are able to fail (no false PASS).
- **C4 Docs:** the README, PR body and evidence match the code.
- **C5 Findings:** no unresolved blocking findings remain, and no superseded unsafe code is carried.

Key: ✅ met · ⚠️ partial or conditional · ❌ not met · — not applicable

| Module (PR @ head) | C1 Review | C2 Exceptions | C3 Checks | C4 Docs | C5 Findings | Accepted? |
|---|---|---|---|---|---|---|
| BANK-AWS-001 storage ([#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) @ `e494bcf`) | ⚠️ Reviewed at this SHA only by #3's audit; no GitHub review | — | ✅ [CI 40631310661](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631310661). [re-run]: hashes 87/87, Jest 21/21, synth OK | ❌ Describes the self-logging design as secure | ❌ AccessLogsBucket logs to itself ([re-run] `cfn-s3-selflog` ERROR). Superseded by #5 | **No: close as superseded** |
| Postgres backup/restore ([#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) @ `e7399fb`) | ❌ #3 reviewed `e610015`, and the code has changed since. Not covered by #14 | — | ✅ [CI 40741546543](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741546543) and [40741536430](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741536430). [re-run]: 8 hashed run dirs verify. Harness v2 negatives "must fail for declared reason" (fresh run not re-done here) | ✅ PR body updated (now mentions pg 18 vs postgres:16 and the cdk.json behaviour) | ⚠️ The v1 false-PASS run is labeled HISTORICAL-KNOWN-INVALID in `runs/INDEX.md`. The fix is per #7, not re-derived here | **No:** needs review of `e7399fb` |
| Evidence audit and shared validator ([#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) @ `fb36341`) | ⚠️ [#14 review]: **Approve** at exact SHA | — | ✅ [re-run] 13/13. No CI of its own; runs in #7 CI | ✅ | ✅ none blocking | **Conditional:** needs a human GitHub review |
| Entra CA offline ([#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) @ `d302c99`) | ⚠️ [#14 review]: **Approve with comments** at exact SHA | ⚠️ Baseline choices unconfirmed (risk policies report-only, device scope, 12 roles) | ✅ [re-run] 25/25, validator exit 0, evidence verify OK | ✅ | ✅ Non-blocking follow-ups: CA007 baseline rule, failing rule IDs in logs, CI | **Conditional:** owner confirms the baseline and a human reviews |
| AWS remediation VPC+RDS ([#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) @ `099479e`) | ⚠️ [#14 review]: **Request changes** at exact SHA | ⚠️ EX-01..EX-04 **DECIDED** (§3), but EX-01 and EX-04 are conditional and EX-03 is open | ✅ [re-run] hashes 32/32, tsc OK, Jest 33/33, synth OK, `cfn-s3-selflog` OK. Also runs in #7 CI | ❌ The "least-privilege CMK" claim is contradicted by B5-2. "One rule, one resource" is wrong (EX-02 covers 2 resources). The register still says PROPOSED | ❌ **B5-2**: unconditioned `kms:Create*`/`kms:Put*` for account root on 3 CMKs allows CreateGrant/PutKeyPolicy escalation. **B5-1**: suppressions were applied before approval. **B5-3**: conflicts with #1 | **No** |
| Organizations reference ([#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) @ `e5e7f46`) | ⚠️ [#14 review]: **Request changes** at exact SHA | ⚠️ 2 parliament allowlist entries, not adjudicated | ✅ [re-run] hashes 66/66, Jest 49/49, synth OK. **No CI** | ❌ The "hardened S3" README claim is false. The Terraform-to-CDK deviation is undocumented | ❌ **B6-1** S3 self-logging ([re-run] ERROR). **B6-2** exempt-role-name SCP bypass. **B6-3** Terraform plan deviation | **No** |
| Integration ([#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) @ `afb41278`) | ❌ No review of `afb41278` (its own AC1 is UNMET) | ⚠️ Inherits #5 | ✅ [CI] at `afb41278`, all success: aws-cdk [40743023477](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743023477); offline-validation [40743023533](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743023533) and [40743011205](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743011205); postgres-restore-evidence [40743023651](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743023651) (5 jobs: harness self-test, postgres:18 service, offline, the pg18-vs-16 negative control, CDK synth). [re-run] `scripts/validate-all.sh --python-only` at `afb4127`: **PASS (20 steps)**. The full run with CDK and Postgres was not re-run here, though CI covers both | ⚠️ Its own AC4 is PARTIAL | ❌ #7's AC5 still reports "MET" at `afb41278`, but it integrates #5 with unresolved **B5-2** ([#14 review]). #14's checkpoint 1 also lists the #2 false-PASS remediation as **not yet reviewed** | **No** |
| Portfolio case studies ([#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8) @ `6c25c05`) | ❌ None | — | ⚠️ [re-run] citation check (§4): 130/130 GitHub links resolve, all blob/tree/commit links are SHA-pinned, and the 5 cited Actions runs match conclusion and SHA | ⚠️ Prose claims not checked beyond the links | ✅ none found | **No:** needs review |
| Vendor mock, SIMULATION ([#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) @ `88a3785`) | ❌ None | — | ✅ [re-run] 45/45 tests, `check_governance.py` exit 0, both evidence runs verify (12/12 and 14/14). **No CI** | ✅ Labeled SIMULATION; claims no real-vendor compatibility | ✅ none found | **No:** needs review and CI |
| Observability ([#10](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/10) @ `3e40e39`) | ❌ None | — | ✅ [re-run] 64/64 tests, `generate_evidence.py --verify` PASS, SHA256SUMS 44/44. The evidence is for `2613ea2`, a clean tree. **No CI** | ⚠️ Not reviewed beyond the README | UNVERIFIED (no code review done) | **No:** needs review |
| Job requirements matrix ([#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12) @ `31b69db`) | ❌ | — | UNVERIFIED | UNVERIFIED | UNVERIFIED | **No:** opened during the snapshot, not checked |
| Synthetic team model ([#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13) @ `9dc8f1f`) | ❌ | — | UNVERIFIED | UNVERIFIED | UNVERIFIED | **No:** opened during the snapshot, not checked |
| Review notes #3–#6 ([#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) @ `981db0a`) | — (it is the review) | — | Spot-checked: B6-1 and the #5 exception facts agree with this report's [re-run] and template extracts | ✅ | — | Docs only. Summary in §4a |
| Backup/DR AWS (branch [`backup-dr-aws`](https://github.com/onnxscibroccoli/bank-it-operations-lab/tree/backup-dr-aws) @ `10da54f`, **no PR**) | ❌ None | ⚠️ Has its own `SECURITY_EXCEPTIONS.md`, not adjudicated | ⚠️ [re-run] SHA256SUMS 72/72 OK; cost-model tests 8/8; evidence-validator tests 8/8; CDK: tsc OK, Jest OK (46 passed, 46 total), synth OK. **No CI** | ⚠️ Not reviewed | UNVERIFIED | **No.** Pushed about 14:16 EDT. `RECOVERY_EXECUTION_STATUS.json` says **NOT_EXECUTED** for every backup, copy and restore job: no recovery has been demonstrated |
| Learning guide and ADRs ([#15](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/15) @ `52a63c0`) | ❌ | — | ✅ [re-run] all 40 `sha:path` citations exist (`git cat-file -e`). Two more matches are ARN fragments, not citations | UNVERIFIED (prose) | — | **No:** needs review |
| FFIEC AIO control mapping ([#16](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/16) @ `3f82697`) | ❌ | — | ✅ [re-run] 10/10 tests; `validate_mapping.py` reports MAPPING VALID (17 rows, 97 artifacts; OBSERVED=0) | UNVERIFIED (mapping accuracy against FFIEC text) | — | **No:** needs review. Lab only, not an exam or certification |
| Patch rings and hardening ([#17](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/17) @ `5605b78`) | ❌ | — | ✅ [re-run] 18/18 + 9/9 tests; evidence `--verify` PASS (113 inputs); SHA256SUMS 102/102. **No CI** | UNVERIFIED | UNVERIFIED | **No:** needs review |
| Identity governance, Graph fixtures ([#18](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/18) @ `f48e7e3`) | ❌ | — | ✅ [re-run] 65/65 tests; evidence `--verify` OK; SHA256SUMS 49/49. **No CI** | UNVERIFIED | UNVERIFIED | **No:** needs review |
| Hybrid/AD runbooks ([#19](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/19) @ `3397dac`) | ❌ | — | ✅ [re-run] 10/10 tests; `check_hybrid_runbooks.py`: 12 files, 0 findings. The runbooks themselves are marked NOT_EXECUTED | UNVERIFIED | — | **No:** needs review |
| M365/endpoint scenarios ([#20](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/20) @ `86a555a`) | ❌ | — | ⚠️ [re-run] `m365_ops.py`: 13/13 scenarios PASS, 0 mutations executed. **No unit tests and no committed evidence run** (only `.gitignore` under `evidence/m365`) | UNVERIFIED | — | **No:** needs review and evidence |
| Final report ([#11](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/11)) | ❌ | — | — | — | — | Draft |

## 2. Merge policy and per-PR merge-gate status
**Policy (recorded per Ian):** nothing merges into `main` until **all** gates G1–G7 pass for the exact head SHA, and G8–G9 hold. Automation never merges, closes PRs or deploys.
- **G1:** a human reviewer examined and approved the exact head SHA.
- **G2:** every exception is adjudicated.
- **G3:** all checks pass on that SHA.
- **G4:** docs match the code.
- **G5:** integration-tested with the other PRs it ships with.
- **G6:** revalidated against current `main` right before merge.
- **G7:** post-merge verification on `main` (CI plus evidence re-verify), with a revert if it fails.
- **G8:** no false-pass tests.
- **G9:** no superseded unsafe code is carried.

| PR | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 | ❌ | — | ✅ | ❌ | ❌ superseded in #7 | ⚠️ conflicts with #5 | n/a | ✅ | ❌ self-logging | **BLOCKED (close)** |
| #2 | ❌ | — | ✅ | ✅ | ✅ in #7 (`e76d8a4`) | ⚠️ re-check at merge | pending | ⚠️ v2 fixes the v1 false PASSes [#7]; fresh run not re-done here | ✅ | **BLOCKED (G1)** |
| #3 | ❌ (agent approve only) | — | ✅ | ✅ | ✅ in #7 | ⚠️ | pending | ✅ | ✅ | **BLOCKED (G1)** |
| #4 | ❌ (agent approve with comments only) | ⚠️ baseline choices | ✅ | ✅ | ✅ in #7 | ⚠️ | pending | ✅ 19 malformed + negative fixtures fail closed [re-run 25/25] | ✅ | **BLOCKED (G1, G2)** |
| #5 | ❌ (request changes) | ⚠️ EX-01, EX-03, EX-04 not closed | ✅ | ❌ | ✅ in #7 | ⚠️ conflicts with #1 | pending | ⚠️ the allowlist test misses stack-level suppressions [#14] | ✅ | **BLOCKED (G1, G2, G4, B5-2)** |
| #6 | ❌ (request changes) | ⚠️ | ⚠️ no CI | ❌ | ❌ not integrated | ⚠️ | pending | ✅ | ❌ self-logging, SCP bypass | **BLOCKED** |
| #7 | ❌ | ⚠️ | ✅ CI at `afb41278` | ⚠️ | ✅ (it is the integration) | ⚠️ | pending | ⚠️ | ❌ carries #5's B5-2 | **BLOCKED** |
| #8–#10, #12, #13, #15–#20, `backup-dr-aws` | ❌ | — (`backup-dr-aws` has unadjudicated exceptions) | ⚠️ local re-runs only, no CI (#12 and #13 not checked; #20 has no tests) | ⚠️ | ❌ | ⚠️ | pending | ✅ none known where tests exist; UNVERIFIED elsewhere | ✅ | **BLOCKED (G1)**. `backup-dr-aws` has no PR at all |
| #14, #11 | ❌ | — | — | ✅ | — | ⚠️ | pending | — | — | Docs only, BLOCKED (G1) |

G6 note: `main` is still `7f50348`, and GitHub reports every PR as MERGEABLE. #1 and #5 conflict with each other on `infra/aws-cdk/**` (per [#14 review], via `git merge-tree`). G6 has to be redone after any merge.

## 3. Security exception register: EX-01..EX-04 (#5), **DECIDED**
Decision source: the ChatGPT security review as adopted by Ian. The parent agent relayed it on 2026-10-28 at about 14:10 EDT. **This is not yet recorded as a GitHub review or a sign-off in #5.** The "facts checked" column comes from this report's extract of the committed #5 template @ `099479e`.

| ID | Rule / resource | Decision | Condition still open | Facts checked here (template @ `099479e`) |
|---|---|---|---|---|
| EX-01 | NIST.800.53.R5-S3DefaultEncryptionKMS / AccessLogsBucket | **ACCEPTED for the lab, pending bucket-policy verification** | Verify the log-sink bucket policy | SSE-S3 (AES256), all 4 Block Public Access settings, versioning, BucketOwnerEnforced. The policy denies `s3:*` without TLS, and allows `s3:PutObject` only for `logging.s3.amazonaws.com` on `/data-bucket/*`, with `aws:SourceArn` = DataBucket and `aws:SourceAccount` = this account. Not yet signed off |
| EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled / AccessLogsBucket **and** DataBucket | **ACCEPTED as an explicit limitation.** The claim that replication "is impossible in an env-agnostic stack" is **REJECTED** | Reword the #5 register to say "lab limitation", not "not expressible". Also, EX-02 covers 2 resources | Versioning and RETAIN on both buckets. #14: not a DR compensating control |
| EX-03 | AwsSolutions-IAM5 / RdsMonitoringPolicy | **OPEN, pending verification of the exact wildcard scope** | Confirm the scope and decide | Statement 1 grants `logs:CreateLogGroup` and `PutRetentionPolicy` on `…:log-group:RDSOSMetrics`. Statement 2 grants `logs:CreateLogStream`, `PutLogEvents`, `DescribeLogStreams` and `GetLogEvents` on `…:log-group:RDSOSMetrics:log-stream:*`, in this account and region. The role trust is `monitoring.rds.amazonaws.com` with `aws:SourceAccount` |
| EX-04 | AwsSolutions-IAM4 / BackupPlanPostgresRole (AWSBackupServiceRolePolicyForBackup) | **CONDITIONALLY ACCEPTABLE, pending role review** | Review the role | The trust is `backup.amazonaws.com` with **no `aws:SourceAccount` condition**. #14 also notes that the vault has no access policy or Vault Lock and shares the DB CMK |

Independent of the exceptions, **B5-2** (the KMS key-admin escalation) still blocks #5 and #7.

## 4a. PR #14 independent review: summary (`reports/review-pr3-pr6.md` @ `981db0a`)
The reviewer is neither the author nor this automation. The review is local, credential-free and read-only, and it reviewed the exact head SHAs of #3 `fb36341`, #4 `d302c99`, #5 `099479e` and #6 `e5e7f46`. These are review notes, **not a GitHub review or a human sign-off**.

| PR | Verdict | Blocking items |
|---|---|---|
| #3 | **Approve** | none |
| #4 | **Approve with comments** | none. Follow-ups: a CA007 baseline rule, failing rule IDs in the evidence logs, CI |
| #5 | **Request changes** | **B5-1** suppressions were applied while the register said PROPOSED. **B5-2** unconditioned `kms:Create*`/`kms:Put*` for account root on 3 CMKs (CreateGrant/PutKeyPolicy escalation). **B5-3** conflict with #1 on `infra/aws-cdk/**` |
| #6 | **Request changes** | **B6-1** `TrailAccessLogsBucket` logs to itself. **B6-2** any account can create a role with an exempt name and bypass the SCPs. **B6-3** CDK was delivered where the plan asked for Terraform; the deviation is undocumented and the Terraform items are MISSING |

Checkpoint 1 (14:15 EDT) adds:
- The #2 CI false PASSes (N01, N04, N05, N06 in `ci-service-40630856041-1`) are VERIFIED. The remediation is marked **"open / no fix commit reviewed"**, even though #2's harness v2 (`e7399fb`) and #7 claim the fix. Until the reviewer reviews `e7399fb`, treat the fix as **unreviewed**.
- Still unconfirmed:
  - the absent-key behaviour of the #6 encryption SCPs
  - the second parliament allowlist entry
  - all live behaviour
  - the Terraform requirement, which is not in the repo
- Remaining review steps:
  - review the #2 fix
  - check the #6 SCP absent-key behaviour
  - re-review #5 after the EX sign-off and the KMS fix
  - re-review #6 after B6-1 and B6-2 are fixed
  - extend the self-log checker to catch A→B→A loops

## 4. Reviews done for earlier updates (2026-10-28 about 14:25 EDT)
- **#10 observability @ `3e40e39`** [re-run]:
  - `python3 -m unittest discover -s observability/tests` ran 64 tests: OK.
  - `generate_evidence.py --verify` on `runs/local-offline-20261028T180832Z`: VERIFY PASS.
  - `sha256sum -c`: 44/44.
  - `SUMMARY.json` records commit `2613ea2`, clean tree, overall PASS.
  - No CI. A code review was **not** done.
- **#8 portfolio @ `6c25c05`** [re-run]:
  - Every one of the 130 distinct GitHub links in `portfolio/*.md` resolves through the GitHub API (HTTP 200) in onnxscibroccoli/{Grasshopper, helix, broccoli-core, civicpatch, omnikali, broccoli-rish}.
  - The links are 45 blob, 18 tree and 5 commit links (all SHA-pinned), plus 42 PRs, 15 repo roots and 5 Actions runs.
  - All 5 cited runs match their stated conclusion (success) and head SHA: Grasshopper 40667390721 @ `4e5525c`, broccoli-core 39352779867 @ `2d3b595`, civicpatch 40713410326 @ `cd94213`, helix 40687102198 @ `8f68703` and omnikali 40691477149 @ `67108f2`.
  - **Not checked:** whether the prose claims match the cited file contents, and whether "latest run" statements are still current.
- **#9 vendor mock** moved to `88a3785` and was re-run there: 45/45 tests, governance lint OK, 2 evidence runs verify.
- **#2** PR body re-read: it is updated and no longer stale.

## 5. CI summary (all times EDT)
- **`bank-aws-001-cdk`** (#1): 4/4 runs succeeded, 00:07–00:16.
- **`postgres-restore-evidence`** (#2):
  - [40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041) and [40630876341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630876341) at `daf8d82`: **failed** (00:10).
  - Runs at `e610015`, `2aac93c` and `e7399fb`: success (00:12, 14:02, 14:03).
- **#7 `overnight/integration`**:
  - At `876f7b7`: 6/6 runs succeeded (14:03).
  - At `0f57289`: 5/5 runs succeeded (14:10).
  - At **`afb41278`** (current head): 4/4 runs succeeded (14:13). The push event triggered only `offline-validation`; the pull_request event ran all three workflows.
- **No CI** on #3, #4, #5, #6, #8, #9, #10, #12–#20 or `backup-dr-aws`. #3, #4 and #5 are covered only through #7.
- The full run list is in `EVIDENCE_MANIFEST.md`.

## 6. Not verified / known gaps
- Nothing was deployed. No live AWS, Entra, Graph or Access Analyzer validation was run, and no compliance certification is claimed.
- The cdk-nag counts and the #6 parliament/SCP lint results are **[PR body]** or **[#14 review]**; they were not recomputed here.
- #12 and #13 are not reviewed. The prose of #8, #10 and #15–#20 was not reviewed.
- The `backup-dr-aws` CDK results are as stated in §1. No real backup or restore has run (NOT_EXECUTED).
- Actions are pinned by tag, not SHA.
- No PR has a human GitHub review.
