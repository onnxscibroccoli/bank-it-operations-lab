# BANK-AWS-001 — AWS CDK static evidence

**STATIC EVIDENCE ONLY.** Everything here comes from local, credential-free `cdk synth` and unit tests.
Nothing was deployed or bootstrapped, and no AWS API was called. No AWS credentials were present
(see logs/21). This is **not** a deployment record, an audit, or a compliance certification. cdk-nag
results are static rule checks on the synthesized template only.

## What was synthesized
Stack `BankItLabSecureStorage` (env-agnostic: `aws://unknown-account/unknown-region`, no lookups):
- `AWS::KMS::Key` DataKey: customer-managed, rotation enabled, Retain.
- `AWS::S3::Bucket` DataBucket: SSE-KMS with DataKey and S3 Bucket Key, BlockPublicAccess all, versioning,
  BucketOwnerEnforced (ACLs disabled), server access logs -> AccessLogsBucket/data-bucket/, Retain.
- `AWS::S3::Bucket` AccessLogsBucket: SSE-S3 (required for S3 access-log targets), BlockPublicAccess all,
  versioning, BucketOwnerEnforced, self access logs under self-access-logs/, Retain.
- Two `AWS::S3::BucketPolicy`s: deny when aws:SecureTransport=false (enforceSSL), plus an allow for
  logging.s3.amazonaws.com s3:PutObject with SourceArn/SourceAccount conditions (feature flag
  `@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy`).
- cdk-nag `AwsSolutionsChecks({verbose:true, reports:true})` applied with `Aspects.of(app)`. Result: 11/11 Compliant,
  0 Non-Compliant, 0 Suppressed. **No NagSuppressions applied** and none are pending review.

## Toolchain (exact, from package-lock.json)
- node v20.19.2, npm 11.21.1
- aws-cdk-lib 2.275.0
- constructs 10.8.1
- cdk-nag 2.38.2
- aws-cdk 2.1146.1
- typescript 5.9.3
- jest 30.5.2
- ts-jest 29.4.15
- ts-node 10.9.2

## Layout
- logs/NN-*.log: one log per command, each with its cwd, command, start and finish times, and `# exit_code:`.
  Failing logs from correction passes are kept unchanged (see logs/CORRECTION-PASS-{1,2,3}.md and logs/22-NOTE.md).
- run-cmd.sh: wrapper that unsets AWS_* and CDK_DEFAULT_*, points AWS config and credentials at /dev/null, and disables IMDS.
- synth/: synthesized template + cloud assembly manifest (copied from infra/aws-cdk/cdk.out).
- cdk-nag/: NagReport CSV (original), JSON conversion, CDK validation-report.json.
- jest-results.json: machine-readable test results (21/21 passed: 12 stack tests + 9 evidence-validator tests, log 43).
- SHA256SUMS: hashes of every tracked file in the owned paths, the CI workflow and reports/MORNING_REPORT.md
  (`sha256sum -c evidence/aws/SHA256SUMS` from repo root; regenerate with update-sha256sums.sh).
- run-git.sh: wrapper for git/gh/rclone commands (logs 30+), scrubs token-like strings, appends COMMANDS.tsv.
- evidence-schema.json: descriptor of this bundle; checked by `npm run validate:evidence` (infra/aws-cdk) and by Jest.
- logs/REBASE-MAP.md: pre/post SHAs after replaying local history onto origin/main.
- ci/: GitHub Actions run records (and failing logs, if any).

## Reproduce (from repo root)
    evidence/aws/run-cmd.sh x npm ci && evidence/aws/run-cmd.sh y npx tsc --noEmit
    evidence/aws/run-cmd.sh z npx jest --ci
    evidence/aws/run-cmd.sh s npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --no-asset-metadata --quiet

## Known gaps
- The synthesized template keeps the default synthesizer's BootstrapVersion parameter and rule. Deploying would
  need a bootstrap, which is out of scope.
- cdk-nag is pinned to 2.38.2, the v2 Aspects API the spec requires. cdk-nag 3.x moved to `Validations.of().addPlugins`.
- No upstream spec existed. The repo was created locally, then replayed onto the GitHub repo's main (see logs/REBASE-MAP.md); CI is now in .github/workflows/bank-aws-001-cdk.yml.
