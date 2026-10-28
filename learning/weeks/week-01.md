# Week 1: CDK foundations and credential-free synthesis (AWS/IaC 1 of 3)

**Branch:** `$PR1` = `bank-aws-001@e494bcf` (PR #1). This is the original design, kept for teaching. #7 records it as **superseded by #5** (`overnight/integration@49122f2:reports/INTEGRATION.md`). Week 3 covers the remediated version. **Prerequisites:** Node 20, npm, the `SETUP.md` worktrees. No AWS credentials.

**Delivered files used:** `infra/aws-cdk/bin/app.ts`, `lib/secure-storage-stack.ts`, `lib/lab-context.ts`, `cdk.json`,
`package.json`/`package-lock.json`, `test/secure-storage-stack.test.ts`, `.github/workflows/bank-aws-001-cdk.yml`,
`evidence/aws/run-cmd.sh`, `infra/aws-cdk/docs/adr/ADR-0003-credential-free-env-agnostic-synth.md`.

## Daily exercises
**Day 1: Read the app.** Read `bin/app.ts` and `lib/secure-storage-stack.ts`. List each construct (`DataKey`, `DataBucket`,
`AccessLogsBucket`) and each property that sets a control.
- *Expected:* there is no `env` on the stack, `AwsSolutionsChecks` is added with `Aspects.of(app)`, and the context comes from `LAB_CONTEXT`.

**Day 2: Install and typecheck.**
```bash
cd $PR1/infra/aws-cdk
$LAB/learning/exercises/no-aws-env.sh npm ci --no-audit --no-fund
$LAB/learning/exercises/no-aws-env.sh npx tsc --noEmit; echo "tsc rc=$?"
```
- *Expected:* `tsc rc=0`. (Executed: see `execution/EXECUTION_LOG.md` E01.)

**Day 3: Unit tests.** `npm test`
- *Expected:* `Test Suites: 2 passed`, `Tests: 21 passed` (12 stack + 9 evidence-validator tests). (Executed: E01.)

**Day 4: Credential-free synth.**
```bash
npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --no-asset-metadata --quiet; echo rc=$?
cmp cdk.out/BankItLabSecureStorage.template.json ../../evidence/aws/synth/BankItLabSecureStorage.template.json && echo identical
grep -o '"environment": *"[^"]*"' cdk.out/manifest.json
```
- *Expected:* exit 0, `identical`, and `aws://unknown-account/unknown-region`. (Executed: E01.)

**Day 5: The CI gate.** Read the `cdk-nag gate` step in `.github/workflows/bank-aws-001-cdk.yml` and run it locally:
```bash
f=$(ls cdk.out/*BankItLabSecureStorage-NagReport.csv | head -1)
echo "rows=$(tail -n +2 "$f" | grep -c .) non_compliant=$(grep -c '"Non-Compliant"' "$f")"
```
- *Expected:* `rows=11 non_compliant=0`. (Executed: E01.)

## Failure injection and recovery
1. **Credentials present.** `AWS_ACCESS_KEY_ID=AKIAFAKEFAKEFAKE0000 bash -c '<the "Assert no AWS credentials" step body>'`.
   *Expected:* `AWS credentials present; refusing to continue`, exit 1. (Executed: E05.) *Recovery:* unset the variable.
2. **Break a control (scratch tree only).** In `lib/secure-storage-stack.ts`, change `blockPublicAccess` on `DataBucket` to
   `BlockPublicAccess.BLOCK_ACLS` (line 42 at `e494bcf`), then run `npx jest --ci --verbose`. *Observed (E07):* `Tests: 4 failed, 17 passed`.
   The failures were `cdk-nag AwsSolutions: zero errors`, `data bucket: SSE-KMS with CMK, BPA, versioning, access logs`,
   `every bucket has public access fully blocked and versioning`, and `committed evidence bundle › validates cleanly`.
   The last one fails because `evidence/aws/SHA256SUMS` also hashes the infra source, so a source edit breaks the evidence check too.
   *Recovery:* `git checkout -- lib/`, then re-run to get 21/21.
3. **Wrong cdk-nag major.** Read `evidence/aws/logs/CORRECTION-PASS-1.md`. cdk-nag 3.x broke the Aspects API. Do not
   reproduce this with `npm install`: that rewrites the lockfile.

## Answer notes
- The stack is environment-agnostic because ADR-0003 forbids lookups and account literals. Synth works with no account at all.
- `--no-lookups` makes any `fromLookup` throw instead of calling AWS. That makes the build reproducible.
- The `BootstrapVersion` parameter and rule are still emitted. That is a known gap (`infra/aws-cdk/README.md`, "Known gaps").

## Architecture tradeoffs
- Environment-agnostic stacks are reproducible and safe on any PR, but you cannot use lookups or cross-region references (ADR-0003).
- Exact version pins plus `npm ci` give reproducibility, but upgrades become explicit work (ADR-0001).

## Fifteen-minute walkthrough
1. (3 min) Inventory: `main` is empty, and PR #1 is the base AWS module.
2. (4 min) `bin/app.ts`: show that it sets no env and adds the Aspect.
3. (4 min) Run `npm test` and synth, then show `unknown-account/unknown-region`.
4. (4 min) The CI workflow: `permissions: contents: read`, `persist-credentials: false`, the credential assertion, and the nag gate.

## Interview questions
1. Why does `--no-lookups` matter for a credential-free pipeline?
2. What does `aws://unknown-account/unknown-region` tell a reviewer?
3. What is the limit of "11/11 cdk-nag compliant" as assurance?
4. Why pin `aws-cdk` (the CLI) as a devDependency rather than `npx aws-cdk@latest`?

## PENDING / UNEXECUTED
- CI re-run of `bank-aws-001-cdk`: not triggered. This guide only records the runs in `evidence/aws/ci/RUNS.md`.
