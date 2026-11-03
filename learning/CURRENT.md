# Reading the twelve-week guide on main

The [twelve-week guide](README.md) and its [weekly pages](weeks/week-01.md) were written on 2026-10-28 (commits `52a63c0` and `39728db`, finished 14:33 EDT), while every module was still an open draft pull request. They are preserved records: their bytes are locked by [preserved-records.json](../docs/metadata/preserved-records.json) and are not edited. This page tells you what has changed since, so you can follow the guide from main.

Checked on 2026-11-03 against main `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6`.

## What changed

- **Modules are on main now.** The guide says main contains only `README.md` and tells you to check out each PR branch. Since 2026-10-31 (merged at 17:09 EDT through PR #35), every module that [coordination/modules.json](../coordination/modules.json) marks INTEGRATED is on main at the path the guide cites. You can usually skip the `git checkout <branch>` step and work from main.
- **Pull request states changed.** Merged: #2, #3, #4, #5, #7, #20, #22 and the integration PRs #35–#38. Closed: #1 (superseded by #5). Still open drafts, with their content on main through #35: #6, #8–#19 and #21. The registry marks review notes (#14) and the acceptance runner (#23–#26) NOT_INTEGRATED. Those files are not on main.
- **Module-relative paths.** Weekly pages often cite paths like `lib/guards.ts` or `test/secure-storage-stack.test.ts`. They are relative to the module directory, for example `infra/aws-cdk/`.
- **Test counts moved.** The guide records 33 CDK tests for PR #5 at `099479e`. On main, `cd infra/aws-cdk && npm ci && npx jest` reported 3 suites and 37 tests passing on 2026-11-03. Treat the guide's counts as values for its pinned commit.

## Cited paths that are not on main

A check of all 98 `branch@sha:path` citations in `learning/**` and `docs/adr/**` against the main tree found 82 paths present and 16 citations to these 8 missing paths:

| Missing path | Came from | Where cited | Use on main instead |
|---|---|---|---|
| `.github/workflows/bank-aws-001-cdk.yml` | PR #1 (closed) | SETUP, ADR 0001 | [.github/workflows/aws-cdk.yml](../.github/workflows/aws-cdk.yml) |
| `evidence/aws/run-cmd.sh`, `evidence/aws/SHA256SUMS`, `evidence/aws/logs/CORRECTION-PASS-1.md` | PR #1 (closed) | SETUP, ADRs 0001, 0002, 0010 | [evidence/aws/aws-remediation-vpc-rds](../evidence/aws/aws-remediation-vpc-rds/README.md) and its `CORRECTION_PASSES.md` |
| `infra/aws-cdk/lib/evidence-validator.ts` | PR #1 (closed) | ADR 0010 | [evidence/shared](../evidence/shared/README.md) |
| `evidence/orgs/run-cmd.sh`, `evidence/orgs/SHA256SUMS` | PR #6 branch layout | SETUP, ADRs 0001, 0010 | `evidence/orgs/policies` on main; the run-script layout differs |
| `reports/review-pr3-pr6.md` | PR #14 (NOT_INTEGRATED) | INVENTORY, week 12, ADRs 0003, 0004, 0009 | Read it on PR #14; [reports/INTEGRATION.md](../reports/INTEGRATION.md) summarises its findings |

Weeks 1 and 2 are built around PR #1's evidence layout, which never reached main. Do the same exercises against `infra/aws-cdk` and `evidence/aws/aws-remediation-vpc-rds`, or check out `bank-aws-001` at the pinned commit to follow them exactly.

## Findings the guide describes as open

These are records, not a fresh security review:

- **B5-2 (KMS key-admin escalation, PR #5).** Recorded as fixed in `80f01d6` by [coordination/tasks.json](../coordination/tasks.json) and [reports/INTEGRATION.md](../reports/INTEGRATION.md). That commit is an ancestor of main, and `infra/aws-cdk/lib/least-privilege-key.ts` contains the `KeyAdministrationByKeyAdminRoleOnly` statement. The registry's `aws-cdk` limitation text still says "B5-1/B5-2 open". The two records disagree.
- **The same pattern in backup keys (PR #21).** `backup/aws/lib/backup-key.ts` still grants `kms:Create*` and `kms:Put*` to the account root in a statement its comment says was copied from the pre-fix pattern. This was not re-reviewed here.
- **B6-1, B6-2, B6-3 (Organizations, PR #6).** Still listed as blocking in `coordination/tasks.json`.
- **CA007 gap (Entra, PR #4).** The PENDING list records "CA007: no baseline rule (R08)". Not re-checked in this pass.

## Re-run on 2026-11-03

These ran on a Linux workstation without credentials. The commands are in [Tutorials](../docs/knowledge/tutorials.md):

- `bash scripts/validate-all.sh --python-only`: PASS, 34 steps.
- Entra validator tests: 25 OK. Vendor mock tests: 45 OK. AWS CDK jest: 37 passed.
- PostgreSQL evidence verify: VERIFIED (38 cases). A tampered copy was REJECTED.
- Incident timeline verify: PASS for both recorded runs.

## Still pending

The guide's own [PENDING list](execution/PENDING.md) still applies. In addition, the live PostgreSQL scenario and the incident crash demo were not run here, because the workstation has no PostgreSQL server binaries. No AWS or Microsoft Graph call was made. Weeks 6 and 9 code-level failure injections remain unexecuted.
