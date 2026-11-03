# Independent review: PR #3, #4, #5, #6 (bank-it-operations-lab)

- Repo: https://github.com/onnxscibroccoli/bank-it-operations-lab. Base `main` = `7f50348` (README only).
- Reviewed 2026-10-28, 13:35–14:10 EDT, by a reviewer who did not write this code. All local, credential-free, read-only.
  Nothing was posted, approved, merged, pushed or deployed. The only change pushed is this notes file, on draft PR branch `review/pr3-pr6`.
- Exact SHAs reviewed. They match each PR's current head:
  - #3 `review/pr1-pr2-evidence-audit` `fb3634115cb22b26e717afe2caec69661f56e874`
  - #4 `entra-ca-offline` `d302c99d95116c39d7aa65937614bccb830f2d6e`
  - #5 `aws-remediation-vpc-rds` `099479e6d23968adb17762d88d84131998fca07c`
  - #6 `orgs-security-refs` `e5e7f4604597c7e6e35e69bf0607fe0535d4cdab`
- Each PR is a draft and mergeable, with **no CI checks, no comments and no reviews** on GitHub. None of them adds a CI workflow. Every "pass" below
  comes from a local re-run in this review, not from CI.
- Environment: Node 20.19.2, npm 11.21.1, Python 3.13; `npm ci --ignore-scripts`. No `AWS_*`/`CDK_DEFAULT_*` variables were set.
- Legend: **VERIFIED** = re-run or recomputed here. **CLAIM** = taken from the PR and not independently checked. **UNVERIFIED** = not checked.

## Summary

| PR | Title | Verdict | Blocking items |
|---|---|---|---|
| [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) | review: evidence audit of PR #1 and PR #2 + shared evidence validator | **Approve** (no blocking items) | none |
| [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) | entra: offline Conditional Access policy validation | **Approve with comments** | none |
| [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) | AWS remediation: private VPC + RDS, remove S3 self-logging, AwsSolutions + NIST 800-53 R5 nag | **Request changes** | B5-1 suppressions applied before approval; B5-2 the KMS key-admin statement allows grant/key-policy escalation; B5-3 conflicts with #1 |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | orgs: credential-free Organizations security reference modules | **Request changes** | B6-1 CloudTrail access-log bucket logs to itself; B6-2 exempt-role-name SCP bypass; B6-3 CDK delivered in place of Terraform, deviation undocumented |

Suppression and skip counts in PR source (logs, synth and fixtures excluded):

| PR | eslint / ts-ignore | noqa | nosec / type: ignore | skipped tests | cdk-nag suppressions | other allowlists |
|---|---|---|---|---|---|---|
| #3 | 0 | 1 | 0 | 0 | 0 | 0 |
| #4 | 0 | 3 | 0 | 0 | 0 | 0 |
| #5 | 0 | 0 | 0 | 0 | **5 entries / 4 exception IDs**, all applied | 0 |
| #6 | 0 | 0 | 0 | 0 | 0 | **2** parliament allowlist entries |

Cross-PR: #1 and #5 both add `infra/aws-cdk/**` on top of `main` and **conflict** (VERIFIED with `git merge-tree`). #3+#4 and #5+#6 merge cleanly.

---

## PR #3: evidence audit of #1/#2 + `evidence/shared` validator

**Scope.** 6 files, +762. Only `reports/review-pr1-pr2.md` and `evidence/shared/**` are touched, as claimed (VERIFIED).

**Re-verification of its claims against #1 `e494bcf` and #2 `e610015` (both still the PR heads).** All checks below were VERIFIED with the PR's own tool:
- #1 `evidence/aws/SHA256SUMS`: 87/87 OK. COMMANDS.tsv: 48 rows OK.
- `cfn-s3-selflog` on #1's template: **ERROR AccessLogsBucket83982689 logs to itself.** Source `secure-storage-stack.ts:33-35` has
  `serverAccessLogsPrefix: 'self-access-logs/'` and no destination.
- #2 `ci-service-40630856041-1`: hashes 36/36 OK, NOTE.md uncovered. **4 FALSE-PASS negatives (N01, N04, N05, N06)**. The log line-3 errors are
  `transaction_timeout` and `relation "lab.ledger_entries" does not exist`. So `NOTE.md:4` ("Negative tests behaved as expected") is inaccurate, as the PR says.
- #2 local-offline run: hashes 39/39, negatives 6/6 fail for the intended reason.
- Unit tests: 13/13 pass.

**Tests.** The tests are meaningful and use temp-dir fixtures for both positive and negative cases (mismatch, self-listing, orphan log, false-pass, self-log by omission and by explicit Ref).

**Gaps (non-blocking).**
- `cfn-s3-selflog` only detects direct self-logging, not A→B→A loops. #5's `guards.ts` does detect loops.
- The manifest check is a hand-rolled subset of JSON Schema, not a full validator.
- None of the checks are wired into CI. The PR body discloses this.
- The report's timestamps are approximate ("about 11:00 EDT").

**Suppressions.**
- `evidence/shared/tests/test_validate_evidence.py:16` `# noqa: E402`: import after a `sys.path` insert. **Justified.**

**Docs.** The PR body, README and report agree.

**Verdict: Approve** (as review notes plus a tool). There are no blocking items. The tool proved useful here: it also flags #6 (see B6-1).

---

## PR #4: Entra Conditional Access offline validation

**Scope.** 102 files, +14,234. Touches only `identity/entra/**`, `tests/entra/**` and `evidence/entra/**` (VERIFIED). It is synthetic and offline, and every artifact
is labelled `mode: offline-synthetic` and `tenantStateClaimed: false`. No tenant or Graph calls were found.

**Source vs generated.**
- Source: 7 policy JSONs, `baseline.json` and `ca_validator.py` (stdlib).
- Generated: 36 fixtures from `make_fixtures.py`. `--check` reports no drift (VERIFIED).
- Generated evidence run: `runs/local-offline-20261028T150359Z`.

**Re-run results (all VERIFIED).**
- 25/25 unit tests pass.
- The baseline exits 0.
- `generate_evidence.py --verify` returns OK.
- `sha256sum -c` passes 46/46, and the hash list covers every file in the run directory.
- **Input hashes:** all 54 `inputHashes` match the bytes at `e8771c9`. The only in-scope file not covered at that commit is `evidence/entra/README.md`.
  `e8771c9..d302c99` adds only `evidence/entra/runs/**`, so the "validated commit e8771c9" provenance holds.

**Negative tests are meaningful.**
- The unit tests assert that the *expected rule* fails (`test_each_negative_fixture_fails_expected_rule`), not just a non-zero exit. Malformed input is reported as `NOT_EVALUATED`.
- My own adversarial mutations of the real policy set were all caught (VERIFIED):

  | Mutation | Rule that failed |
  |---|---|
  | MFA policy excludes an extra group | BASE-003 |
  | MFA policy excludes trusted locations | BASE-003 |
  | MFA policy excludes the Exchange app | BASE-003 |
  | MFA policy limited to browser only | BASE-003 |
  | MFA policy limited to Android only | BASE-003 |
  | Device policy excludes an extra user | BASE-006 |
  | Legacy-auth block set to report-only | BASE-002 |
  | Admin phishing-resistant MFA excludes a user | BASE-004 |

**Gaps (non-blocking).**
- **CA007 (block admin portals from untrusted locations) has no baseline rule.** Setting it to `disabled` still passes (exit 0, VERIFIED).
- The evidence-run fixture steps check only the exit code with `--quiet`, so the evidence alone does not show *which* rule failed. The unit tests do check this.
- No coverage of:
  - session controls (sign-in frequency for admins)
  - guests and external users
  - workload identities
  - named-location definitions
- No CI.

**Suppressions.**
- `evidence/entra/generate_evidence.py:198` `# noqa: E402`: deferred import after `sys.path` setup. **Justified.**
- `tests/entra/test_ca_validator.py:22-23` `# noqa: E402` (×2): same reason. **Justified.**

**Docs.** The PR body counts (7 policies, 25 tests, 36 fixtures, 41 commands, 13 rules) match what I found.

**Verdict: Approve with comments.** Follow-ups: add a baseline rule for CA007, record the failing rule IDs in the evidence logs, and add CI.

---

## PR #5: AWS remediation (VPC + private RDS, S3 self-logging, two nag packs)

**Scope.** 54 files, +9,767, in two commits:
- `74caa12` imports `infra/aws-cdk` from #1 `e494bcf`. VERIFIED: it differs only by removing the 3 evidence-validator files.
- `099479e` is the remediation.

### Re-run (all VERIFIED)
- `tsc` reports 0 errors.
- Jest: **33/33** (`jest-results.json` shows 33 total, 0 pending or todo).
- `cdk synth --no-lookups` exits 0.
- **A fresh synth is byte-identical** to the committed `synth/*.template.json`, `manifest.json`, all four NagReport CSVs and `validation-report.json`.
- `sha256sum -c SHA256SUMS` passes, and every file in the evidence directory is covered.

### S3 recursive logging: absent (VERIFIED in both source and template)
- Source: `lib/secure-storage-stack.ts:33-40`. `AccessLogsBucket` has no `serverAccessLogsBucket` or `serverAccessLogsPrefix`. `DataBucket` logs to
  `AccessLogsBucket` under `data-bucket/` (`:50-51`).
- Generated `BankItLabSecureStorage.template.json`:
  - `AccessLogsBucket83982689` has **no `LoggingConfiguration`**.
  - `DataBucketE3889A50` has `DestinationBucketName: {Ref: AccessLogsBucket83982689}` and prefix `data-bucket/`.
  - The bucket policy lets `logging.s3.amazonaws.com` `s3:PutObject` only to `/data-bucket/*`, with `aws:SourceArn` = DataBucket and `aws:SourceAccount`.
- Independent checks:
  - #3's `cfn-s3-selflog`: "S3 LOGGING OK: 2 buckets checked".
  - #5's own `guards.ts#selfLoggingBuckets` also catches A→B→A loops, and its negative tests do so on a raw-template loop and on a re-mutated real template.
- Remaining gap (non-blocking): **neither bucket has a lifecycle rule.** With versioning and RETAIN on, the log sink grows without bound, and no retention
  period is defined. That matters for a bank's records-retention policy. #3 recommended adding one.

### Private VPC / RDS scope exists (VERIFIED in the template)
- **Network:** 4 isolated subnets (`MapPublicIpOnLaunch: false`), and 4 route tables with **no `AWS::EC2::Route`**. There is no IGW, NAT or EIP.
- **Logging and SGs:** flow logs (ALL) go to a log group with 365-day retention, encrypted with `LogsKey`. `Custom::VpcRestrictDefaultSG` restricts the default SG.
- **RDS:**
  - `PubliclyAccessible: false`, `StorageEncrypted: true` with the CMK (`DatabaseKey`), and Performance Insights encrypted with the CMK
  - `MultiAZ`, `DeletionProtection`, IAM authentication
  - port 5433, `rds.force_ssl=1`, connection/disconnection logging
  - 14-day backups, plus an AWS Backup plan (daily, 35 days)
- **Security groups:** every rule is SG-to-SG (app→DB 5433, rotation→DB 5433, rotation→Secrets Manager endpoint 443). There is no 0.0.0.0/0 rule. The DB SG and endpoint SG have the CDK "disallow all" egress.
- **Secret rotation:** Secrets Manager rotation every 30 days through the SAR single-user rotation app, inside the VPC, using the private Secrets Manager endpoint.

### Did both nag packs actually run? Yes (VERIFIED from output, not claims)
- `bin/app.ts` adds `AwsSolutionsChecks` and `NIST80053R5Checks` with `reports: true`.
- The fresh synth wrote 4 NagReport CSVs (2 packs × 2 stacks), identical to the committed ones:

  | Report | Compliant | Suppressed | Non-compliant | Distinct rules |
  |---|---|---|---|---|
  | AwsSolutions, NetworkDatabase | 26 | 2 | 0 | 12 |
  | AwsSolutions, SecureStorage | 11 | 0 | 0 | 5 |
  | NIST 800-53 R5, NetworkDatabase | 53 | 0 | 0 | 22 |
  | NIST 800-53 R5, SecureStorage | 16 | 3 | 0 | 9 |

- The `logs/0*-cdk-synth.log` files show only "Successfully synthesized"; nag output is not echoed there. The CSVs (and my re-run) are the proof.
- The failing passes are preserved (VERIFIED in `pass0-nag/` and `pass1-nag/`):
  - pass 0: 10 non-compliant results
  - pass 1: 1 non-compliant result (IAM4 on the backup role) and 2 `UNKNOWN` (`CdkNagValidationFailure` on the `{IndirectPort}` rule)
- **Zero unsuppressed vs zero findings:**
  - **Zero findings, nothing suppressed:** AwsSolutions/SecureStorage and NIST/NetworkDatabase.
  - **Zero only after suppressions:** AwsSolutions/NetworkDatabase (2 suppressed) and NIST/SecureStorage (3 suppressed).
  - The PR body's "0 unsuppressed errors" is accurate. It is not "0 findings".
- **Scanner blind spots** (VERIFIED: these resources appear in no NagReport row). "0 findings" does not cover:
  - `CustomVpcRestrictDefaultSGCustomResourceProvider` Lambda and its role. It is a `CfnResource` with `AWSLambdaBasicExecutionRole` and an inline policy; IAM4, IAM5 and NIST IAMNoInlinePolicy would fire if it were evaluated.
  - the SAR rotation application (a nested stack; its Lambda and role are invisible)
  - `BackupVault`, `BackupPlan`, `BackupSelection`
  - `VPCEndpoint`, `FlowLog`
  - the standalone SG egress rules

### Suppression and exception inventory: every one is APPLIED, while the register says "PROPOSED, pending owner approval"

| # | Exception | Rule | Resource (logical ID) | Source | Rationale | Compensating controls (as claimed → reviewer check) | Justified? |
|---|---|---|---|---|---|---|---|
| 1 | EX-01 | NIST.800.53.R5-S3DefaultEncryptionKMS | AccessLogsBucket83982689 | `secure-storage-stack.ts:56-61` | Server-access-log targets support only SSE-S3 | SSE-S3, BPA, TLS-only, versioning, BucketOwnerEnforced, RETAIN, policy scoped by SourceArn/SourceAccount → VERIFIED in the template | **Yes.** AWS S3 docs say the log destination must use SSE-S3. AWS now also offers CloudWatch Logs delivery with KMS, which is a better exit route. |
| 2 | EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled | AccessLogsBucket83982689 | `:62-66` | CRR needs a second region or account | versioning, RETAIN → VERIFIED | Acceptable for the lab. Not a compensating control for DR. |
| 3 | EX-02 | NIST.800.53.R5-S3BucketReplicationEnabled | DataBucketE3889A50 | `:68-74` | same | same | Same. Note the PR body says "each suppression covers one rule on one resource", but EX-02 covers **two** resources. |
| 4 | EX-03 | AwsSolutions-IAM5, appliesTo `...:log-group:RDSOSMetrics:log-stream:*` | RdsMonitoringPolicy5DA8ACAC | `network-database-stack.ts:242-250` | Enhanced Monitoring writes service-named streams | trust is `monitoring.rds.amazonaws.com` + `aws:SourceAccount` → VERIFIED | **Yes**, tightly scoped. |
| 5 | EX-04 | AwsSolutions-IAM4, appliesTo `AWSBackupServiceRolePolicyForBackup` | BackupPlanPostgresRole2A2CEBDF | `network-database-stack.ts:228-238` | AWS-documented service-role policy | "trust limited to backup.amazonaws.com; vault encrypted with DB CMK; vault RETAIN" → VERIFIED. However, the trust has **no `aws:SourceAccount`** condition, the vault has no access policy or Vault Lock, and it shares the DB CMK. | Acceptable, but the compensating controls are overstated. |

- Other suppression forms: 0 eslint-disable, 0 ts-ignore, 0 stack-level `addStackSuppressions`, 0 skipped tests.
- **Already applied?** Yes, all 5 are in source and appear as `Suppressed` in the committed and re-generated NagReports.
- Test gap: the "only registered exceptions are suppressed" tests (`secure-storage-stack.test.ts:81`, `network-database-stack.test.ts:99`) read only
  resource-level `Metadata.cdk_nag`. A future `NagSuppressions.addStackSuppressions` writes template-root metadata (VERIFIED in `cdk-nag/lib/nag-suppressions.js:22-34`),
  so it would bypass that test while the zero-error tests still pass.

### Key and resource policies, checked against the claims
- **Claim:** "the account root can administer the keys but cannot use them for encryption". **Not proven.**
  - Each of the 3 CMKs (`DataKey`, `LogsKey`, `DatabaseKey`) has `KeyAdministrationByAccountRoot`: an *unconditioned* allow to `:root` for `kms:Create*`, `kms:Put*`,
    `kms:Delete*`, `kms:Disable*` and `kms:ScheduleKeyDeletion`.
  - `kms:Create*` includes **`kms:CreateGrant`** and `kms:Put*` includes **`kms:PutKeyPolicy`**. So any IAM principal in the account whose IAM policy allows them can grant itself Decrypt, or rewrite the key policy. That bypasses the `kms:ViaService` restriction.
  - There is no named key-admin role, so there is no separation of duties. AWS's own guardrail IAM-RDS-1 recommends a separate key-administrator role.
  - `guards.ts#kmsWildcards` only matches `*` / `kms:*`, so it misses this.
- What is good:
  - no wildcard principals
  - crypto use is gated by `kms:ViaService` + `kms:CallerAccount`
  - grants for AWS resources only
  - CloudWatch Logs use is scoped by an encryption-context ARN
  - rotation on and RETAIN
- CDK's `Secret` adds two extra `DatabaseKey` statements, scoped to the secretsmanager ViaService. They are disclosed in SECURITY_EXCEPTIONS.md.

### Evidence provenance
- COMMANDS.tsv has 10 rows, written by `run-cmd.sh`, which appends to it. The exit codes match the logs. The failing passes are kept. `CORRECTION_PASSES.md` discloses one unlogged dev Jest run.
- Not logged:
  - the copy from `cdk.out` into `synth/`, `cdk-nag/` and `pass*-nag/`
  - SHA256SUMS generation
  - the git commit
- No commit SHA is recorded anywhere in the evidence. The runs were made in `/workspace/bank-it-ops-remediation`. My byte-identical re-synth at `099479e` closes that gap.
- `jest-results.json` contains absolute build paths (minor).

### Blocking items
- **B5-1** The exception register says every entry is PROPOSED and pending approval, but all 5 suppressions are already applied. The PR's headline "0 unsuppressed" depends on them.
  Either record approver sign-off for EX-01..EX-04, or present the gate as "pass, conditional on approving these exceptions". Also fix the "one rule, one resource" wording (EX-02 covers 2 resources).
- **B5-2** Tighten the key-admin statement:
  - use a named key-admin principal
  - remove `kms:CreateGrant` from the admin actions (or add the `kms:GrantIsForAWSResource` condition)
  - restrict `kms:PutKeyPolicy`
  - add a negative test for unconditioned CreateGrant/PutKeyPolicy

  Until then, the "least-privilege CMK" claim in the PR body and README should be withdrawn.
- **B5-3** Decide the order with #1. They conflict on `infra/aws-cdk/**`. Either close #1, or rebase #5 onto it.

**Non-blocking:**
- lifecycle and retention on both buckets
- backup vault access policy or Vault Lock, and a separate vault key
- `aws:SourceAccount` on the backup role trust
- document the nag blind spots
- harden the allowlist test against stack-level suppressions
- log the copy and hash steps
- add CI

**Verdict: Request changes.**

---

## PR #6: Organizations security reference (CDK)

**Scope.** 67 files, +9,180. Touches only `infra/orgs/**` and `evidence/orgs/**` (VERIFIED).

**Re-run (all VERIFIED).**
- `tsc` passes. Jest: 49/49.
- `cdk synth` exits 0, and the fresh synth is **byte-identical** to the committed `synth/*` and `cdk-nag/*`.
- `sha256sum -c` passes 66/66. Coverage equals `git ls-files infra/orgs evidence/orgs`, minus SHA256SUMS itself.
- No skipped tests.

### Plan deviation: Terraform requested, CDK delivered
- The plan Ian gave asked for **Terraform**. This PR delivers a **TypeScript CDK** package.
  There is no `.tf`, HCL or Terraform/OpenTofu reference anywhere in the PR or any other branch (VERIFIED with `git grep`).
- The deviation is **not acknowledged** in the PR body, the README or ADR-0001. ADR-0001 says only that the "same pins and conventions as `infra/aws-cdk`" were used.
- This review does not rewrite it. It documents the deviation here.
- **Learning objective, assessed:** the security-design objectives are largely met in CDK:
  - OU design
  - SCP authoring, linting and an offline evaluator
  - an org trail
  - GuardDuty and Security Hub delegated-admin thinking

  The Terraform-specific objectives are not met. CDK also caused one real coverage gap: ADR-0002 says CloudFormation has no resource for GuardDuty delegated admin
  or org auto-enable, but the Terraform AWS provider does (`aws_guardduty_organization_admin_account`, `aws_guardduty_organization_configuration`).
- **Terraform-specific coverage (all MISSING):**
  - HCL modules and variables
  - provider/version pinning and `.terraform.lock.hcl`
  - remote state and locking backend
  - `terraform fmt`, `validate` and `plan`
  - tflint, checkov or tfsec scanning
  - `import` of an existing organization
  - `aws_organizations_*`, `aws_guardduty_organization_*` and `aws_securityhub_organization_configuration` / `configuration_policy` resources

### Findings
- **B6-1: S3 self-logging, the same anti-pattern #5 removes.** In `lib/org-cloudtrail-stack.ts:50`, `TrailAccessLogsBucket` has
  `serverAccessLogsPrefix: 'self-access-logs/'` and no destination.
  - Template: `TrailAccessLogsBucket30C0D746` has `LoggingConfiguration: {LogFilePrefix: self-access-logs/}`, and its policy allows `logging.s3` with `SourceArn` = itself.
  - #3's `cfn-s3-selflog` reports **ERROR** (VERIFIED).
  - The "S1 Compliant" rows in the NagReport depend on this.
  - It is not disclosed. The README says "hardened S3 + access-log bucket".
- **B6-2: Exempt-role bypass.**
  - Every guard-rail SCP exempts `arn:aws:iam::*:role/OrgSecurityAdmin` and `.../OrgBreakGlass` in *any* account (`lib/lab-context.ts`, `lib/scps.ts:26`).
  - No SCP restricts `iam:CreateRole`, `UpdateAssumeRolePolicy`, `PutRolePolicy`, `AttachRolePolicy` or `DeleteRole` on those role names. The only `iam:` mention is the region-lock NotAction.
  - So an admin in any guarded account can create a role with one of those names and escape region-lock, protect-security-services, deny-public-s3 and require-encryption.
  - Fix: add a deny on IAM mutations of those role ARNs for non-exempt principals, and add a test.
- **B6-3:** Document the Terraform deviation (above) in the PR body or an ADR, keep the Terraform items marked MISSING, and get an explicit accept or redo decision from the owner.

**Other findings (non-blocking).**
- **Scanner completeness:**
  - Only the AwsSolutions pack ran. There is no NIST/PCI pack, unlike #5.
  - Governance and SecurityServices have **0 NagReport rows**. That means no rules were evaluated, not that there are zero findings. The README states this.
  - CloudTrail has 14 compliant rows.
  - `scripts/nag-gate.sh` counts Non-Compliant and Suppressed rows only, not `UNKNOWN`.
- **Trail KMS key:** CDK's default `:root` `kms:*` statement is unconditioned. This is inconsistent with #5's approach; KMS5 checks rotation only.
- **Trail bucket:**
  - no Object Lock or WORM, which matters for bank audit-log retention
  - the access-log bucket has no lifecycle rule
  - one CloudTrail `PutObject` statement (`/AWSLogs/<account>/*`) lacks `aws:SourceArn`; the org-path statement has it
- **Security Hub:** `OrganizationConfiguration` is `CENTRAL` with `AutoEnable: false` and no configuration policies, so no member account is covered yet. This is disclosed in ADR-0002.
- **GuardDuty:** the org-level part is not modelled. Disclosed.
- **SCPs:**
  - protect-security-services omits `config:PutConfigurationRecorder` and `PutDeliveryChannel`, so the recorder can be re-scoped to nothing
  - Root plus the four guarded OUs are at the **5/5 SCP quota** (4 + FullAWSAccess), which leaves no headroom
  - `Bool rds:StorageEncrypted=false` and `ec2:Encrypted=false` do not deny requests where the key is absent. Validate this in Access Analyzer. **UNVERIFIED.**
  - SCPs never apply to the management account, where the org trail lives
- **Parliament allowlist** (`infra/orgs/parliament-allowlist.json`), 2 entries, each matched exactly on issue, file and detail:
  1. `UNKNOWN_CONDITION_FOR_ACTION` `rds:StorageEncrypted` on `rds:CreateDBInstance` (`require-encryption.json`, line 38 per log 12). **Justified:** the AWS Service Authorization Reference lists `rds:StorageEncrypted` for CreateDBInstance.
  2. `UNKNOWN_CONDITION_FOR_ACTION` `s3:x-amz-object-ownership` on `s3:PutBucketOwnershipControls` (`deny-public-s3.json`, line 47). **Likely justified** (S3 Object Ownership docs). UNVERIFIED against the service reference in this review.

  The raw run (log 12, exit 1) and the gated run (log 13, exit 0) are both committed. cdk-nag suppressions: 0 (VERIFIED by grep and the CSVs).
- **Provenance:**
  - COMMANDS.tsv rows match the logs, but the file has no timestamp column; timestamps are only in the log headers.
  - The copy from `cdk.out` into `evidence/` and the SHA256SUMS update are not logged.
  - `jest-results.json` has absolute paths. Disclosed.
- **Docs:** the PR body counts match. The README claim "hardened S3" is contradicted by B6-1.

**Verdict: Request changes** (B6-1, B6-2, B6-3).

---

## What was not done or not verified
- No CI exists on any of these PRs, so nothing was checked against GitHub Actions results.
- No AWS, Entra or Access Analyzer validation was run. Everything here is static analysis.
- SCP semantics (B6-2, the Bool/absent-key behaviour) were reasoned from policy text and AWS docs, not run in a real organization.
- The Terraform requirement comes from Ian's plan as relayed to this reviewer. No copy of that plan exists in the repo.

---

## Checkpoint 2 (2026-10-28 14:30 EDT): files inspected, PostgreSQL false-PASS remediation, unconfirmed items, remaining steps

Checkpoint 1 was committed as `981db0a`. This checkpoint replaces it: it updates the file list and the remaining steps, and replaces the priority-B subsection with the harness-v2 verification.

### Files inspected (PR source, excluding generated evidence/ and cdk.out)
- #3: `reports/review-pr1-pr2.md`, `evidence/shared/**` (validator plus tests). The validator was run against #1 `e494bcf` and #2 `e610015`.
- #4: `identity/entra/{ca_validator.py,baseline.json,README.md}`, `identity/entra/policies/CA001–CA007*.json`, `tests/entra/**` (fixtures INDEX, malformed-*, neg-*, tests).
- #5: `infra/aws-cdk/{bin/app.ts,cdk.json,package.json}`, `lib/{guards,lab-context,least-privilege-key,network-database-stack,secure-storage-stack}.ts`, `test/{helpers,negative-controls.test,network-database-stack.test,secure-storage-stack.test}.ts`, `docs/adr/ADR-0001..0004`, plus synthesized templates and nag reports.
- #6: `infra/orgs/lib/{org-cloudtrail-stack,org-governance-stack,ou-layout,policy-lint,scp-evaluator,scps,security-services-stack,lab-context}.ts`, `scripts/{export-policies,lint-policies}.ts`, `scripts/{nag-gate,parliament}.sh`, `parliament-allowlist.json`, `test/*.test.ts`, `docs/adr/ADR-0001..0003`.
- #2 / #7 harness v2, reviewed at `2aac93c` and `e7399fb`:
  - `tests/integration/postgres/{lib.sh,run_restore_scenario.sh,expectations.tsv,expectations.selftest.tsv,selftest_harness.sh,verify_evidence.py,verify_evidence.sh}`
  - `.github/workflows/postgres-restore-evidence.yml`
  - `evidence/postgres/runs/INDEX.md`
  - `evidence/postgres/runs/{ci-service,ci-offline,ci-mismatch-control,ci-selftest}-40741329107-1/**` and their `*.ci-console/`
  - `local-offline-v2-20261028T180208Z/**` and `local-selftest-v2-20261028T180208Z/**`
  - `ci-service-40630856041-1/{NOTE.md,STATUS.json,COMMANDS.tsv,logs/23..28_N0*.log}`
  - `local-offline-20261028T041038Z/{NOTE.md,STATUS.json,ENVIRONMENT.txt}`
  - `evidence/postgres/README.md`, `tests/integration/README.md`
  - the GitHub Actions artifacts of run 40741329107, downloaded and compared

### PostgreSQL false-PASS remediation (priority B): harness v2 at `2aac93c` / `e7399fb`

Both commits are on `ci-evidence-postgres` (PR #2's head is `e7399fb`) and are ancestors of PR #7. `git diff e7399fb origin/pr/7` is empty for `tests/integration/`,
the postgres workflow and `evidence/postgres/` (all VERIFIED). `e7399fb` adds only `evidence/postgres/runs/**` on top of `2aac93c` (VERIFIED).

**(a) Is the failure reason now asserted? Yes. VERIFIED by code reading, by running the self-test, and with my own probe.**
- `expectations.tsv` declares 36 cases (38 in offline mode), each with a kind, an expected exit and a `reason_regex`. All six negatives have a specific reason:

  | Negative | Declared reason (regex) |
  |---|---|
  | N01 | `could not read from input file\|unexpected end of file` |
  | N02 | `does not appear to be a valid archive\|input file is too short` |
  | N03 | `database "lab_db_does_not_exist" does not exist` |
  | N04 | `23503: ... violates foreign key constraint "ledger_entries_account_id_fkey"`, using `VERBOSITY=verbose` |
  | N05 | `ERROR: +(schema\|relation\|type\|function) "..." already exists` |
  | N06 | a `-lab.ledger_entries\|1000\|<md5>` diff line |

- `lib.sh` `run_case` decides a negative's result in this order:
  - exit 0 → `FAIL/unexpected_success`
  - no regex declared → `ERROR/no_reason_declared`
  - regex matched in the command's **own output** (never the command line) → `PASS`
  - output matches `transaction_timeout`-style version errors → `ERROR/version_mismatch`
  - output matches `relation "…" does not exist` or other environment errors → `ERROR/environment_error`
  - anything else → `FAIL/wrong_reason`
- Structure that prevents the old failure mode:
  - Every negative is one command, with separately checked `S_N0x` setup steps behind `--needs` dependencies. A setup failure gives `NOT_RUN`, never PASS.
  - The version gate `S04_client_server_major_match` comes before everything else.
  - `pg_restore --exit-on-error` and `psql ON_ERROR_STOP=1` are used, so a single error ends the command.
  - Overall PASS requires exactly one PASS row per declared case. `NOT_RUN`, duplicate and undeclared rows all fail.
- So `transaction_timeout` or a missing relation can no longer produce a PASS. **VERIFIED:** self-test Part B replays the real logs of the bad run 40630856041 through the production expectations. Results:
  - N01, N05, N06 → `ERROR/version_mismatch`
  - N04 → `ERROR/environment_error`
  - N02, N03 → genuine PASS
  - overall exit 1
- `verify_evidence.py` independently re-derives each verdict from the logs. It checks:
  - the exit code agrees with `expect`
  - the regex is found in the output section
  - exactly one row per case, and no undeclared rows
  - `SUMMARY.json` says PASS with the right case count
  - SHA256SUMS matches and covers every file
  - it refuses `HISTORICAL` runs (exit 3)

  Self-test Part C confirms it rejects a forged PASS (VERIFIED).
- **Residual gap (VERIFIED with a probe, non-blocking):** the declared regex is checked *before* the environment/version-error regex. A negative whose output contains **both**
  `unrecognized configuration parameter "transaction_timeout"` and `could not read from input file` is classified PASS. My probe, using `lib.sh` with a synthetic two-line output, returned `PASS/expected_fault_detected`.
  - Self-test ST04 does not cover this. Its masquerade case deliberately mistypes the reason text ("disk ful").
  - In practice the S04 gate and `--exit-on-error` mitigate it.
  - Hardening: for negatives, check the env-error regexes first, or require them to be absent. Add a self-test case where both strings appear. Apply the same rule in `verify_evidence.py`.
- **Second gap (non-blocking):** `verify_evidence.py` trusts the run directory's own `EXPECTATIONS.tsv`. It does not compare it with `tests/integration/postgres/expectations.tsv` or with `sha256_expectations.tsv` in `ENVIRONMENT.txt`, so a run with weakened regexes would still verify.
  I did that comparison by hand: all four v2 scenario runs carry an `EXPECTATIONS.tsv` identical to the repo file filtered by mode (VERIFIED).

**(b) Local runs.**
- `selftest_harness.sh`: exit 0, **26/26 assertions** (VERIFIED, run locally at `e7399fb`). Covered: Part A (12 synthetic cases plus an undeclared one), Part B (replay), Part C (forged PASS).
- `verify_evidence.py` on every committed run directory (VERIFIED):

  | Run | Result |
  |---|---|
  | `ci-service-40741329107-1` | VERIFIED, 36 cases |
  | `ci-offline-40741329107-1` | VERIFIED, 38 cases |
  | `local-offline-v2-20261028T180208Z` | VERIFIED, 38 cases |
  | `ci-mismatch-control-40741329107-1` | REJECTED, 35 problems (correct; see d) |
  | `ci-service-40630856041-1` | HISTORICAL, exit 3 |
  | `local-offline-20261028T041038Z` | HISTORICAL, exit 3 |

  The `*selftest*` and `*.ci-console` directories are REJECTED because they are not scenario runs, which is expected.
- The committed runs exclude `artifacts/`, so artifacts are "NOT CHECKED" locally. With the downloaded CI artifacts,
  `verify_evidence.py --require-artifacts` gives **VERIFIED** for the service and offline runs, with `ARTIFACTS.sha256` OK (VERIFIED).
- **Scenario: UNVERIFIED locally.** No PostgreSQL binaries are on the review box: no `psql`, `pg_dump` or `initdb`, and no `/usr/lib/postgresql`. I relied on the CI run plus the artifact comparison in (c).

**(c) Hashes and provenance (VERIFIED).**
- `sha256sum -c SHA256SUMS` passes for every committed run directory:

  | Run | Entries |
  |---|---|
  | ci-service-40741329107-1 | 46 |
  | ci-offline-40741329107-1 | 48 |
  | ci-mismatch-control-40741329107-1 | 41 |
  | ci-selftest-40741329107-1 | 48 |
  | local-offline-v2 | 48 |
  | local-selftest-v2 | 48 |
  | ci-service-40630856041-1 | 36 |
  | local-offline-20261028T041038Z | 39 |

  Coverage is complete for the v2 runs. In the two historical runs, only the newly added `NOTE.md` and `STATUS.json` are uncovered, which is disclosed. The `*.ci-console/` directories have no SHA256SUMS.
- `ENVIRONMENT.txt` of the three v2 CI scenario runs records:
  - `git_sha = github_sha = 2aac93c22d9e…`
  - `github_run_id=40741329107`, attempt 1
  - `git_tree_dirty=no`
  - pg_dump 18.6

  The recorded `sha256_` values of `lib.sh`, `run_restore_scenario.sh`, `expectations.tsv`, `seed.sql` and `fingerprint.sql` all **equal the files at `2aac93c`**.
  `local-offline-v2` records the same `git_sha` and hashes, with pg_dump 16.15 and empty `github_*` fields (sandbox run). The self-test directory has no ENVIRONMENT.txt.
- `gh run view 40741329107`:
  - workflow `postgres-restore-evidence`, branch `ci-evidence-postgres`
  - head **`2aac93c`**, event push, conclusion success, 2026-10-28 14:02 EDT
  - all 5 jobs succeeded, so the run's commit matches
- I downloaded the run's 4 artifacts. Each committed `ci-*-40741329107-1/` is **byte-identical** to its artifact (`diff -rq`, excluding `artifacts/`), and every `*.ci-console` log is identical to the artifact's console log.

**(d) The mismatch-control run.**
- `version-mismatch-control` is a CI job that deliberately runs the scenario with runner pg_dump 18.6 against a `postgres:16` service. That is the exact condition behind run 40630856041. The job then asserts:
  - the scenario exit code is non-zero
  - `S04` is `ERROR/version_mismatch`
  - **0 negative PASS rows**
  - `SUMMARY.json` overall is FAIL
  - `verify_evidence.py` **rejects** the run
- Committed result (VERIFIED):
  - S04 log: `client_major=18 server_major=16 MISMATCH`
  - 2 PASS (S00, S03), 1 ERROR, 33 NOT_RUN
  - all six negatives `NOT_RUN/dependency_failed`
  - verifier REJECTED
- **It is meaningful, with one limit.** It proves the gate fails closed under the real fault, and that CI goes red if the harness ever reports PASS there.
  Because the gate stops every downstream step, it does *not* exercise the negative classifier on real mismatched output. That part is covered by self-test Part B, which uses the real 40630856041 logs.
  It could be strengthened with a second control that bypasses S04 and asserts N01/N05/N06 come out as `ERROR/version_mismatch`. Note this would currently expose the ordering gap in (a) only if both strings appeared.

**(e) Workflow false-pass paths (VERIFIED by reading `postgres-restore-evidence.yml` at `2aac93c`).**
- No `continue-on-error`. The only `|| true` is in the `pg_ctl stop` cleanup trap.
- Each `set +e` captures `${PIPESTATUS[0]}` through `tee` into a step output. A final `if: always()` gate runs `test rc = 0` for the scenario **and** the verifier (`--require-artifacts` in CI).
  An empty rc (step never ran) fails the `test`.
- The control job's assertions use the default `bash -e`, and a missing `SUMMARY.json` fails the step.
- Permissions are `contents: read` and `persist-credentials: false`. The CDK job now uses `npm ci --ignore-scripts` and `npx --no-install`, with no `CDK_DEFAULT_*`, which addresses #3's earlier findings.
- **One remaining misleading-green path:** when no `cdk.json` exists (true on `ci-evidence-postgres` alone), the `cdk-synth` job prints "skipped (not counted as a pass)" but still finishes **success**, a green check that tested nothing.
  Make it `skipped`, using a job-level `if` or by exiting neutral, or label it in the PR body.

**(f) NOTE.md and STATUS.json corrections for the old runs.**
- `ci-service-40630856041-1`: the correction is **accurate** (VERIFIED).
  - It appends below the original text rather than rewriting it.
  - It correctly says the "Negative tests behaved as expected" sentence is wrong.
  - Its table matches the logs (N01/N05/N06 `transaction_timeout`, N04 `relation "lab.ledger_entries" does not exist`, N02/N03 genuine).
  - Its "v2 verdict on replay" column matches my local self-test exactly.
  - STATUS.json's statement that P04–P06 and P09–P11 failed genuinely matches the old COMMANDS.tsv.
  - `git diff e610015 e7399fb` for that directory adds only NOTE.md (+20) and STATUS.json, so "SUMMARY/COMMANDS/logs/SHA256SUMS byte-identical" holds, and SHA256SUMS still passes.
  - The run time (04:10:48Z = 00:10 EDT) matches `gh run view`.
- `local-offline-20261028T041038Z`: the correction is **accurate** (VERIFIED).
  - It marks the run HISTORICAL without claiming it was wrong.
  - It is consistent with #3's finding that all 6 negatives failed for the intended reason.
  - It correctly notes `ENVIRONMENT.txt git_sha=7f50348` (base `main`).
  - Minor: the "conda-forge PG 16" source of the binaries is a CLAIM. I did not verify it.

**(g) Which PR is the fix meant to land in?**
- The fix is authored on **PR #2** (`ci-evidence-postgres`, "ci: Postgres backup/restore exercise with offline tests and evidence"). Its head is `e7399fb`, it is a draft, and CI run 40741329107 ran on that branch. So #2 is the owning PR (VERIFIED).
- **PR #7** (`overnight/integration`, draft) is an integration PR into `main`. It stacks #3, #5, #4 and #2@`e7399fb`, supersedes #1, and leaves #6 out pending changes.
  - It carries the harness byte-for-byte; the diff against `e7399fb` is empty for the harness, workflow and evidence (VERIFIED).
  - Its head moved during this review, from `0f57289` to `afb4127`. Its latest postgres CI run 40743023651 is green.
  - I did not review the rest of #7's diff (UNVERIFIED).
- Recommendation: land the fix through #2 (or through #7 only as the agreed integration vehicle), and do not cherry-pick it separately.
- **Status of priority B: remediated.** Two non-blocking hardening items remain: the regex/env-error ordering, and the verifier's self-attested `EXPECTATIONS.tsv`. Plus the cosmetic cdk-synth green-on-skip.

### Unconfirmed items
- Whether the encryption SCPs in #6 deny requests that omit the encryption key entirely (behaviour when the Bool key is absent).
- The second parliament allowlist entry in #6, checked against the AWS service reference.
- Live behaviour in AWS, Entra and Access Analyzer. Nothing was run live.
- The Terraform requirement for #6, which comes from the owner's plan and is not in the repo.
- The PostgreSQL scenario was not run locally (no PostgreSQL on the box). It relies on CI run 40741329107 and the artifact comparison.
- The rest of PR #7's integration diff beyond the postgres harness.

### Remaining review steps
1. ~~Review the PostgreSQL false-PASS fix~~ Done (above). Follow-ups for #2:
   - check env/version-error regexes before the declared reason for negatives, and add a self-test case where both strings appear
   - make `verify_evidence.py` compare the run's EXPECTATIONS.tsv with the repo copy or with the `sha256_expectations.tsv` value
   - make `cdk-synth` report skipped rather than success when there is no CDK app
   - optionally, add a control that bypasses S04
2. Confirm the absent-key behaviour of the encryption SCPs in #6 against AWS docs or the policy simulator.
3. Re-review #5 after the owner signs off on EX-01..EX-04 and the KMS key-admin statement is fixed. Decide the #1/#5 merge order. #7 resolves it by superseding #1.
4. Re-review #6 after B6-1 and B6-2 are fixed and the CDK-for-Terraform deviation is documented in the PR.
5. Extend #3's self-log checker to catch A→B→A loops. Add a CA007 baseline rule in #4.
6. Review PR #7 at its exact head SHA, including INTEGRATION.md, the AC1–AC5 claims and `scripts/validate-all.sh`, before any merge to `main`.
7. Optionally, run the PostgreSQL scenario on a box with PG 16/18 binaries to reproduce the CI result locally.
