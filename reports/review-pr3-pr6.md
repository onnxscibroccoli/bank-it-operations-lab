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

## Checkpoint 1 (2026-10-28 14:15 EDT): files inspected, unconfirmed items, remaining steps

### Files inspected (PR source, excluding generated evidence/ and cdk.out)
- #3: `reports/review-pr1-pr2.md`, `evidence/shared/**` (validator plus tests). The validator was run against #1 `e494bcf` and #2 `e610015`.
- #4: `identity/entra/{ca_validator.py,baseline.json,README.md}`, `identity/entra/policies/CA001–CA007*.json`, `tests/entra/**` (fixtures INDEX, malformed-*, neg-*, tests).
- #5: `infra/aws-cdk/{bin/app.ts,cdk.json,package.json}`, `lib/{guards,lab-context,least-privilege-key,network-database-stack,secure-storage-stack}.ts`, `test/{helpers,negative-controls.test,network-database-stack.test,secure-storage-stack.test}.ts`, `docs/adr/ADR-0001..0004`, plus synthesized templates and nag reports.
- #6: `infra/orgs/lib/{org-cloudtrail-stack,org-governance-stack,ou-layout,policy-lint,scp-evaluator,scps,security-services-stack,lab-context}.ts`, `scripts/{export-policies,lint-policies}.ts`, `scripts/{nag-gate,parliament}.sh`, `parliament-allowlist.json`, `test/*.test.ts`, `docs/adr/ADR-0001..0003`.

### PostgreSQL false-PASS remediation (priority B)
- VERIFIED: PR #2 run `ci-service-40630856041-1` has 4 false-pass negatives (N01, N04, N05, N06), caused by `transaction_timeout` and the missing relation `lab.ledger_entries`. `NOTE.md:4` is inaccurate.
- VERIFIED: the local-offline run of #2 fails all 6 negatives for the intended reason.
- UNCONFIRMED: none of PRs #3–#6 remediates the CI false-passes. No fix commit on #2 was reviewed. Status: **open**.

### Unconfirmed items
- Whether the encryption SCPs in #6 deny requests that omit the encryption key entirely (behaviour when the Bool key is absent).
- The second parliament allowlist entry in #6, checked against the AWS service reference.
- Live behaviour in AWS, Entra and Access Analyzer. Nothing was run live.
- The Terraform requirement for #6, which comes from the owner's plan and is not in the repo.

### Remaining review steps
1. Review the PostgreSQL false-PASS fix on #2 (or a new PR) once it exists, re-run N01–N06 in CI and confirm each fails for the intended reason.
2. Confirm the absent-key behaviour of the encryption SCPs in #6 against AWS docs or the policy simulator.
3. Re-review #5 after the owner signs off on EX-01..EX-04 and the KMS key-admin statement is fixed. Decide the #1/#5 merge order.
4. Re-review #6 after B6-1 and B6-2 are fixed and the CDK-for-Terraform deviation is documented in the PR.
5. Extend #3's self-log checker to catch A→B→A loops. Add a CA007 baseline rule in #4.
