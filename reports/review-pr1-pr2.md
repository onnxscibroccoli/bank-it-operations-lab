# Review: PR #1 and PR #2 (evidence and correctness audit)

- Reviewed: 2026-10-28, about 11:00 EDT. Read-only on both PR branches. Nothing was commented, merged, or pushed to either branch.
- PR #1 at `e494bcfc3986c2d21a4cf92453857f69dbf69ce3`. PR #2 at `e6100154999bd7dc75dc46b69b3928ad9d1f1370`. Base `main` at `7f50348`.
- How: cloned the repo under `/workspace`, recomputed every recorded hash, cross-checked every COMMANDS.tsv row against its log,
  re-ran PR #1's `npm ci`, `tsc`, `jest`, `cdk synth`, and `validate:evidence` with no AWS credentials, parsed every JSON and YAML file,
  and ran the new shared checks in `evidence/shared/` against both bundles.
- Static review only. This is not an audit or a certification, and nothing was deployed.

## Summary

| PR | Title | Author | State | CI at head | Files | Verdict |
|---|---|---|---|---|---|---|
| [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) | BANK-AWS-001: credential-free secure storage stack + evidence | onnxscibroccoli | open, draft, mergeable | `bank-aws-001-cdk` run 40631310661: success | 88 (+8122) | **Accept with changes** |
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | ci: Postgres backup/restore exercise with offline tests and evidence | onnxscibroccoli | open, draft, mergeable | `postgres-restore-evidence` runs 40631027885 and 40631034518: 3/3 jobs success | 86 (+1026) | **Accept with changes** |

Earlier PR #2 runs 40630856041 and 40630876341 failed. That failure is preserved as evidence (see below).

---

## 1. Schemas and hash integrity

### PR #1
- `evidence/aws/SHA256SUMS`: **all 87 entries match** the files at `e494bcf` (recomputed with `sha256sum -c` and with
  `evidence/shared/validate_evidence.py hashes`). It does not list itself, which is correct. Every file the PR adds is covered except
  `SHA256SUMS` itself.
- `evidence/aws/evidence-schema.json` is a custom descriptor, not a JSON Schema. `npm run validate:evidence` re-ran here and printed
  `checked 18 files / EVIDENCE VALID`. All 10 JSON files parse, and the workflow YAML parses.
- Reproducibility: a fresh credential-free `cdk synth` produced a template, `manifest.json`, and NagReport CSV that are
  **byte-identical** to `evidence/aws/synth/*` and `evidence/aws/cdk-nag/*.csv`. Jest passed 21/21, as recorded.
- Circular evidence (minor): `jest-results.json` is written by the same Jest run (log 43, `--outputFile=../../evidence/aws/jest-results.json`)
  that includes `test/evidence-validator.test.ts:37-43` ("committed evidence bundle validates cleanly"). That test hashes the
  **previous** `jest-results.json`, and SHA256SUMS was then regenerated over the new one. So the passing result partly vouches for a file it
  overwrote. Only the CI run, which does not write `jest-results.json`, is an independent check.

### PR #2
- `runs/local-offline-20261028T041038Z/SHA256SUMS`: **39/39 match**, and the run covers every file in its directory.
- `runs/ci-service-40630856041-1/SHA256SUMS`: **36/36 match**. The exception is `NOTE.md`, which is not covered. It was added after the run, and its
  line 6 says so honestly.
- `ARTIFACTS.sha256` for both runs **cannot be checked from the repo**. `runs/*/artifacts/` is gitignored
  (`evidence/postgres/.gitignore:3`), and the dumps exist only as CI artifacts with 30-day retention
  (`postgres-restore-evidence.yml:88`), or not at all for the local run. `verify_evidence.sh:8` skips the check silently when
  `artifacts/` is absent.
- There is no schema for `SUMMARY.json` or COMMANDS.tsv. `verify_evidence.sh` checks the column count and PASS/FAIL only.

## 2. Command log completeness

### PR #1
- `evidence/aws/logs/COMMANDS.tsv`: 48 rows. Every row's exit code **matches** its log's `# exit_code:` trailer, every `*.log` has a
  row, and there are no orphans. Failing logs (05, 06, 08, 12, 13, 15, 22) are kept and explained in `CORRECTION-PASS-{1,2,3}.md`
  and `22-NOTE.md`.
- Provenance gap: `run-cmd.sh` (used for rows 01–23 and 40–44) **does not append to COMMANDS.tsv**. Only `run-git.sh:17` does.
  So 28 of the 48 rows were written outside the wrapper, by hand or by another process, which `README.md:41` does not say.
  The values do agree with the logs.
- The following steps produced committed evidence but have **no command log**:
  - copying `cdk.out/*` into `evidence/aws/synth/` and `cdk-nag/`
  - the CSV-to-JSON conversion that made `AwsSolutions-NagReport.json`
  - each `update-sha256sums.sh` run
  - `git commit`s
  - building the Drive checkpoint tarball
  - the "credential pattern scan clean" claim (`ci/DRIVE_CHECKPOINTS.md:14-15`)
  - the local sha256 behind "match local" (`ci/DRIVE_CHECKPOINTS.md:4`). Log 52 shows only Drive's hashes.
- Overstated header: `run-cmd.sh:11` writes `# env: AWS_* and CDK_DEFAULT_* unset` into every log. Lines 13-14 unset only 7 named
  variables (not, for example, `AWS_ROLE_ARN`, `AWS_WEB_IDENTITY_TOKEN_FILE`, or `AWS_CONTAINER_CREDENTIALS_*`). Log 21 checks only 4.
- The last push and CI run (`e494bcf`, run 40631310661) are not recorded. That is inherent, since a commit cannot contain its own CI result, and
  `ci/RUNS.md:14` discloses it.

### PR #2
- Both runs' COMMANDS.tsv rows agree with their log footers and with expect/result (checked by `validate_evidence.py commands`).
- **False PASSes in the committed failing run.** In `runs/ci-service-40630856041-1`, four negative tests are recorded as PASS even though they
  failed for an unrelated reason:

  | Step | Log | Actual error |
  |---|---|---|
  | N01 | `logs/23_N01_restore_truncated_dump.log:3` | `unrecognized configuration parameter "transaction_timeout"`, not truncation |
  | N04 | `logs/26_N04_fk_enforced_after_restore.log:3` | `relation "lab.ledger_entries" does not exist`. The FK was never tested. |
  | N05 | `logs/27_N05_restore_over_existing_objects.log:3` | `transaction_timeout` on the first restore, not a duplicate object |
  | N06 | `logs/28_N06_tamper_detected.log:3` | `transaction_timeout`. No tamper or diff ever ran. |

  So `NOTE.md:4` ("Negative tests behaved as expected") is **not accurate**. The root cause is in `run_restore_scenario.sh:140,145,146`, where
  negative steps chain setup commands with `&&` inside one `bash -c`, so any setup failure counts as the expected failure. The local
  offline run's six negatives all fail for the intended reason (`validate_evidence.py postgres-negatives` reports OK).
- Neither committed run used the current script. `client_server_major_match` (`run_restore_scenario.sh:111`) was added in `e610015`,
  after both runs, so neither committed `COMMANDS.tsv` has that step. The local run's `ENVIRONMENT.txt` records
  `git_sha=7f50348` (base `main`), not the commit containing the script it ran. The passing CI runs (40631027885 and 40631034518)
  are not committed. They exist only as 30-day artifacts.

## 3. AccessLogsBucket self-logging in PR #1: **present**

- `infra/aws-cdk/lib/secure-storage-stack.ts:26-36` sets `serverAccessLogsPrefix: 'self-access-logs/'` on `AccessLogsBucket` with
  **no** `serverAccessLogsBucket`, so CDK targets the bucket itself. The comment at lines 33-34 says this is intended
  "to satisfy AwsSolutions-S1 without a NagSuppression and without an extra bucket".
- Synthesized result: `evidence/aws/synth/BankItLabSecureStorage.template.json:54-56` has `LoggingConfiguration` with only
  `LogFilePrefix: self-access-logs/` (no `DestinationBucketName`). Around lines 120-150, the bucket policy grants `logging.s3.amazonaws.com`
  `s3:PutObject` on `AccessLogsBucket/self-access-logs/*` with `aws:SourceArn` set to AccessLogsBucket itself.
- Why it matters: AWS says "Your destination bucket should not have server access logging enabled … delivering logs to the source
  bucket will cause an infinite loop of logs and is not recommended"
  (<https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html>). Here every log delivery is a write
  that is itself logged. With versioning on, RETAIN, and **no lifecycle rule**, storage grows without bound. The cdk-nag S1 "Compliant"
  row for AccessLogsBucket (`cdk-nag/AwsSolutions--BankItLabSecureStorage-NagReport.csv:3`) is technically true, but it was met by a
  configuration AWS advises against. Without this, S1 would have needed a documented suppression.
- Disclosure: the behaviour is stated in `evidence/aws/README.md:14` and `ADR-0002…md:15`. However, it is **not** listed under known gaps in the
  PR body, `README.md:51-55`, or `reports/MORNING_REPORT.md:44-50`, and no unit test asserts it either way (`test/secure-storage-stack.test.ts:61-71`).
- Fix (either option):
  - (a) Remove `serverAccessLogsPrefix` from `AccessLogsBucket` and add a `NagSuppressions.addResourceSuppressions(... 'AwsSolutions-S1' ...)`
    with a written reason: "this is the access-log destination; AWS advises against logging it to itself". Add a lifecycle rule (expire and
    noncurrent-version expiry), and a test asserting that AccessLogsBucket has no `LoggingConfiguration`.
  - (b) Send its logs to a separate, minimal third bucket.

  Then update ADR-0002, the README, and the PR body, regenerate the evidence, and run
  `validate_evidence.py cfn-s3-selflog` on the template. It currently reports
  `ERROR AccessLogsBucket83982689: server access logs delivered to itself`.

## 4. Evidence completeness and honesty of claims

### PR #1
- Backed by artifacts and reproduced here:
  - environment-agnostic `aws://unknown-account/unknown-region` (`synth/manifest.json`)
  - KMS rotation, SSE-KMS with bucket key, BPA, TLS-only, versioning, BucketOwnerEnforced, RETAIN
  - 11/11 cdk-nag Compliant with 0 suppressions
  - Jest 21/21
  - CI runs 1-3 (`ci/RUNS.md`) match the GitHub run list
- Honest disclaimers: "static evidence only, not a deployment or certification" (`README.md:3-6`, `MORNING_REPORT.md:3`).
  The known gaps are listed: default KMS key policy, BootstrapVersion, and the cdk-nag 2.x pin.
- Gaps:
  - Self-logging is not listed as a gap (see §3).
  - There are no lifecycle rules on either bucket.
  - The default KMS key policy gives the account root full access, which is disclosed.
  - CI does not check that the committed `synth/` template matches a fresh synth. A drift check would catch stale evidence.
  - CI does not run `validate:evidence` directly, though `npm test` covers it.
- Public-repo exposure, low risk: the Drive folder and file IDs (`ci/DRIVE_CHECKPOINTS.md`, logs 49-52) and the absolute box paths
  (`/workspace/...`, `/home/box/bin/rclone`) are in a public repo. No tokens were found (pattern scan for gh*/github_pat/ya29/AKIA/private keys/
  access_token: only the scrubber regex in `run-git.sh:15`).
- Workflow: `permissions: contents: read`, `persist-credentials: false`, and no secrets, which is good. Actions are pinned by tag, not SHA.

### PR #2
- Accurate: the offline run (30/30 PASS, PG 16.15, unix socket only) is fully backed by its logs and fingerprints. Fingerprints for
  source, custom restore, and plain restore are identical. Tamper changed the `ledger_entries` and `account_balances` hashes as expected.
- **Stale or inaccurate PR body:**
  - It says the service container is `postgres:16`. The workflow now uses `postgres:18` (`postgres-restore-evidence.yml:40`).
  - It says `cdk-synth` is skipped because there is no `cdk.json` "today". PR #1 adds `infra/aws-cdk/cdk.json`, so after both merge this job will
    run against PR #1's app.
- `NOTE.md:4` claim: see §2. The claim is false for N01, N04, N05, and N06.
- A passing service-mode run is not committed. The passing evidence exists only in CI artifacts that expire after 30 days.

## 5. Security and correctness risks

- PR #1:
  - Self-logging (§3) is the main correctness and cost issue.
  - The `run-cmd.sh` environment claim is overstated (§2).
  - The KMS default key policy and missing lifecycle rules are disclosed or minor.
- PR #2:
  - `postgres-restore-evidence.yml:146-147` sets `CDK_DEFAULT_ACCOUNT=000000000000` and `CDK_DEFAULT_REGION=us-east-1`. This contradicts PR #1's
    environment-agnostic design and evidence. It is harmless today, because PR #1's stack sets no `env`, but it could leak a fake account into any future stack that
    reads these variables.
  - `:171` runs `npm ci || npm install` and `npx --yes aws-cdk`. The fallback `npm install` and the `--yes` auto-download can pull
    unpinned packages, and lifecycle scripts run. Use `npm ci --ignore-scripts` and the app's pinned local `aws-cdk`.
  - The cdk-synth job duplicates PR #1's CI without the cdk-nag gate or the credential scrubbing.
  - `actions/checkout@v5` at `:59`, `:102`, and `:149` lacks `persist-credentials: false`.
  - `pull_request` has no branch filter, and `.github/workflows/**` triggers on any workflow change, including PR #1's.
  - `run_restore_scenario.sh:108` uses `cut -c1-2` on `server_version_num`, which is wrong for servers below 10 (minor).
  - Paths are interpolated into single-quoted `bash -c` strings (`:121-146`) and would break on paths containing `'` (minor; not
    reachable from untrusted input in CI).
  - `POSTGRES_PASSWORD: postgres` is an ephemeral CI container credential and is acceptable.

## 6. Proposed tooling improvements

This PR adds the following under `evidence/shared/`:
- `validate_evidence.py` (stdlib only):
  - `hashes`: recomputes sums, rejects self-listing, and reports UNCOVERED files.
  - `commands`: cross-checks COMMANDS.tsv rows against log trailers and reports orphan logs (both TSV formats).
  - `postgres-negatives`: reports FALSE-PASS when a negative step failed for the wrong reason.
  - `cfn-s3-selflog`: detects S3 buckets that log to themselves.
  - `manifest`: structural check against the schema.
- `evidence-manifest.schema.json` (draft 2020-12, meta-validated with `jsonschema`): an optional per-bundle `MANIFEST.json` that must declare
  - the hashes file and its self-exclusion
  - every other uncovered file, with a reason
  - whether TSV rows were written by a wrapper or by hand
  - the producer script's exact commit, or `uncommitted` plus the script's sha256
  - independent anchors such as a CI run or Drive file id
- `negative-expectations.postgres.json`: the required error text for each of N01–N06.
- `tests/test_validate_evidence.py`: 13 unit tests, all passing, using temp dirs only.

Results on the PR heads:

| Check | PR #1 | PR #2 local-offline | PR #2 ci-service (failing run) |
|---|---|---|---|
| hashes | OK 87/87 | OK 39/39 | OK 36/36, NOTE.md uncovered |
| commands | OK 48 rows | OK 30 rows | OK 28 rows |
| postgres-negatives | n/a | OK 6/6 | **4 FALSE-PASS** (N01, N04, N05, N06) |
| cfn-s3-selflog | **ERROR AccessLogsBucket** | n/a | n/a |

Further recommendations for the PR owners. None of these are made here.
1. Have `run-cmd.sh` append to COMMANDS.tsv like `run-git.sh`, and log the copy, convert, hash, and archive steps.
2. Write `jest-results.json` from a separate Jest run that excludes the committed-bundle test, or stop hashing it.
3. In PR #2, make each negative test a single command after separately-checked setup steps, and assert the expected error text, not just a non-zero exit.
4. Record the script's commit or sha256 in `ENVIRONMENT.txt`.
5. Commit one passing service-mode run, or attach its artifact sha256 and Actions run id to `RUNS.md`.
6. Add a CI step that runs `cfn-s3-selflog` and a synth-drift diff for PR #1, and `postgres-negatives` for PR #2.

## Verdicts

- **PR #1: accept with changes.** Hashes, logs, and reproducibility are sound. Before merge:
  - Remove or justify the AccessLogsBucket self-logging and add a lifecycle rule and a test for it (§3).
  - List it in the known gaps.
  - Correct the `run-cmd.sh` environment header and disclose that the run-cmd COMMANDS.tsv rows were written by hand.
- **PR #2: accept with changes.** The offline evidence is sound and CI is green. Before merge:
  - Correct `NOTE.md:4` and the stale PR body.
  - Harden the negative tests against false passes.
  - Remove `CDK_DEFAULT_ACCOUNT/REGION` and the unpinned `npx --yes`/`npm install` fallback from the cdk-synth job, or drop that job in favour of PR #1's workflow.
