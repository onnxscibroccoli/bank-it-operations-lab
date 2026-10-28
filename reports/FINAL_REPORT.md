# FINAL REPORT: bank-it-operations-lab

- Repo: https://github.com/onnxscibroccoli/bank-it-operations-lab
- Snapshot: 2026-10-28, about 14:25 EDT (UTC-4). `main` @ [`7f50348`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/7f50348bf1370381615eaed91c02607fe41de2f5) holds only `README.md` and has not changed since the repo was created.
- **Nothing is merged into `main`. Nothing is deployed. No AWS, Entra or Graph credentials were used.** All 14 PRs (#1–#14) are open drafts, and none has a GitHub review (an approval or request for changes).
- **Evidence labels:**
  - **[re-run]**: re-executed on the box for this report.
  - **[CI]**: a linked GitHub Actions run.
  - **[#14 review]**: the independent review notes in [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) (`reports/review-pr3-pr6.md` @ `765787a`). They were written by a reviewer who is neither the code author nor this automation. They are **not** a GitHub review and **not** a human sign-off.
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
| Integration ([#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) @ `0f57289`) | ❌ No review of `0f57289` (its own AC1 is UNMET) | ⚠️ Inherits #5 | ✅ [CI] at `0f57289`: aws-cdk [40742562106](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742562106) and [40742550274](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742550274); offline-validation [40742561679](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742561679) and [40742550289](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742550289); postgres [40742561967](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742561967), all success. Full `validate-all.sh` not re-run here | ⚠️ Its own AC4 is PARTIAL | ❌ #7's AC5 reports "MET", but it integrates #5, which has unresolved **B5-2** ([#14 review]). **The AC5 status is wrong** | **No** |
| Portfolio case studies ([#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8) @ `6c25c05`) | ❌ None | — | ⚠️ [re-run] citation check (§4): 130/130 GitHub links resolve, all blob/tree/commit links are SHA-pinned, and the 5 cited Actions runs match conclusion and SHA | ⚠️ Prose claims not checked beyond the links | ✅ none found | **No:** needs review |
| Vendor mock, SIMULATION ([#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) @ `88a3785`) | ❌ None | — | ✅ [re-run] 45/45 tests, `check_governance.py` exit 0, both evidence runs verify (12/12 and 14/14). **No CI** | ✅ Labeled SIMULATION; claims no real-vendor compatibility | ✅ none found | **No:** needs review and CI |
| Observability ([#10](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/10) @ `3e40e39`) | ❌ None | — | ✅ [re-run] 64/64 tests, `generate_evidence.py --verify` PASS, SHA256SUMS 44/44. The evidence is for `2613ea2`, a clean tree. **No CI** | ⚠️ Not reviewed beyond the README | UNVERIFIED (no code review done) | **No:** needs review |
| Job requirements matrix ([#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12) @ `31b69db`) | ❌ | — | UNVERIFIED | UNVERIFIED | UNVERIFIED | **No:** opened during the snapshot, not checked |
| Synthetic team model ([#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13) @ `9dc8f1f`) | ❌ | — | UNVERIFIED | UNVERIFIED | UNVERIFIED | **No:** opened during the snapshot, not checked |
| Review notes #3–#6 ([#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) @ `765787a`) | — (it is the review) | — | Spot-checked: its B6-1 and the #5 exception details agree with this report's [re-run] and template extracts | ✅ | — | Docs only |
| Backup/DR | — | — | — | — | — | **MISSING:** no PR or pushed branch. Uncommitted work sits in box worktree `/workspace/bkp-dr-aws-worker` (branch `backup-dr-aws`) |
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
| #7 | ❌ | ⚠️ | ✅ CI at `0f57289` | ⚠️ | ✅ (it is the integration) | ⚠️ | pending | ⚠️ | ❌ carries #5's B5-2 | **BLOCKED** |
| #8, #9, #10, #12, #13 | ❌ | — | ⚠️ #9 and #10 local only, no CI; #8 links only; #12 and #13 not checked | ⚠️ | ❌ | ⚠️ | pending | ✅ none known (#9, #10); UNVERIFIED (#12, #13) | ✅ | **BLOCKED (G1)** |
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

## 4. Reviews done for this update
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
- **No CI** on #3, #4, #5, #6, #8, #9, #10 or #12–#14. #3, #4 and #5 are covered only through #7.
- The full run list is in `EVIDENCE_MANIFEST.md`.

## 6. Not verified / known gaps
- Nothing was deployed. No live AWS, Entra, Graph or Access Analyzer validation was run, and no compliance certification is claimed.
- The cdk-nag counts and the #6 parliament/SCP lint results are **[PR body]** or **[#14 review]**; they were not recomputed here.
- #12 and #13 are not reviewed, and the #10 and #8 prose was not reviewed.
- Backup/DR has no evidence in the repo.
- Actions are pinned by tag, not SHA.
- No PR has a human GitHub review.
