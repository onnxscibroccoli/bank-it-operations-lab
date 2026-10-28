# Overnight integration: `overnight/integration`

> **Deadline:** 2026-10-29T00:00:00-04:00 (midnight America/New_York). At commit time (2026-10-28 17:48 EDT), **6h11m** remained.
> **Branch name:** `overnight/integration` is a historical name only. Keep using it and do not rename it.

- Base: `main` @ `7f50348` (contains only `README.md`; verified it was not broken). This agent has merged nothing into `main`, closed no PR, deployed nothing, and made no AWS, Entra or Graph calls.
- Machine-readable status: [`coordination/tasks.json`](../coordination/tasks.json).
- Full validation: `scripts/validate-all.sh` (Node 20, npm, and PostgreSQL binaries via `PG_BIN` or PATH). For the Python-only subset, run `scripts/validate-all.sh --python-only`.

## Merge policy (updated per [PR #27](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27) finding C6)
- **Automated merges into `main` are allowed once independently proven.** That means an independent review approving the *exact* candidate SHA (AC1), with every other acceptance condition (AC2–AC5) met for that same SHA.
- **Final human portfolio acceptance (AC6) is a separate gate.** Technical merge eligibility is not portfolio acceptance.
- **No technical blocker is relaxed.** The following all still block:
  - failing or missing checks
  - unapproved security exceptions
  - the PR #6 self-logging defect
  - docs mismatches
  - the open findings PR #14 B5-1/B5-2 and PR #27 C1–C5
- This replaces the earlier wording "never merge into main from automation" and the requirement for an independent *human* review. This integration agent still does not merge into `main` itself and makes no production changes.

## Per-PR disposition

| PR | Branch @ head | Disposition | Why |
|---|---|---|---|
| [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) | `review/pr1-pr2-evidence-audit` @ `fb36341` | **Integrated** (1st) | Shared, dependency-free tooling (`evidence/shared/`) that later checks rely on. It is the review of #1/#2. |
| [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) | `aws-remediation-vpc-rds` @ `099479e` | **Integrated** (2nd) | Newer `infra/aws-cdk` that includes #1's app and fixes #3's blocking self-logging finding. |
| [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) | `bank-aws-001` @ `e494bcf` | **Superseded by #5** | 14 duplicate `infra/aws-cdk` files. Its top-level `evidence/aws/**` is for the self-logging template, which fails `cfn-s3-selflog`. Only its CI workflow was carried forward, adapted as `.github/workflows/aws-cdk.yml`. |
| [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) | `entra-ca-offline` @ `d302c99` | **Integrated** (3rd) | Disjoint paths, stdlib only, all checks pass. |
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | `ci-evidence-postgres` @ `e7399fb` | **Integrated, harness v2** (4th; re-merged in `e76d8a4`) | The owner's harness v2 (`2aac93c`, `e7399fb`) fixes #3's false-PASS finding. It replaces the interim integration hardening from `f3a8f17`. GitHub CI at `e7399fb`: 5/5 jobs green. |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | `orgs-security-refs` @ `e5e7f46` | **Awaiting changes, not integrated** | `TrailAccessLogsBucket` logs to itself (`infra/orgs/lib/org-cloudtrail-stack.ts:50`), which is the same defect #3 blocked in #1. `cfn-s3-selflog` reports an ERROR on `evidence/orgs/synth/BankItLabOrgCloudTrail.template.json`. The PR is also a self-declared draft. A trial merge was clean, and tsc, Jest 49/49 and synth passed. |

No PR has a formal GitHub review, and none of the open PRs has a review comment. The only review is #3's report (`reports/review-pr1-pr2.md`), which covers #1 and #2. Every integrated PR still needs an independent review of the exact candidate SHA (AC1). PR #14's notes and PR #27's review are recorded below.

## Related PRs verified on 2026-10-28 (~17:45 EDT; recorded, not integrated)
| PR | Exact head | What we found | Disposition |
|---|---|---|---|
| [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) `review/pr3-pr6` | `eb8d259588f2d1ba8a8787cf2c37044617cbcbdb` | **Review notes only** (1 file, `reports/review-pr3-pr6.md`). No GitHub reviews, comments or CI. The author account is the same as every other PR, so the independence is asserted, not demonstrable. Checkpoint 2 verifies PR #2's harness v2 at `2aac93c`/`e7399fb`: the 4 v1 false PASSes are remediated (on replay, N01/N05/N06 → ERROR/version_mismatch and N04 → ERROR/environment_error). The same notes **request changes** on #5 (B5-1, B5-2: both in integrated code) and #6. **Discrepancy:** the claim "verification on PR #14" describes content at `eb8d259` about PR #2's code, not a review of PR #14. | Recorded. Counts toward AC1 **only for PR #2's harness v2**. |
| [#26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26) `acceptance/vertical-slice` | `181bcdd1420d699c37aa928b636b9332aca83e57` | Built on `49122f2` (+99 files). Run [40749373581](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749373581) is on that SHA and succeeded with **3 jobs, 3 success**. The "43 required checks" are internal to the acceptance job (artifact: 43/43 PASS + 2 non-required). Planted defect (CA002 report-only) **detected**: overall FAIL, 35/43, 8 required FAILs incl. ENTRA-02. Other runs on the SHA: [40749387217](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387217), [40749387209](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387209), [40749387223](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387223), [40749387416](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387416), all success. **Discrepancies:** 43 is not a GitHub check count; PR #26 is stale against PR #25 head `ce39504` (integrated `c6aa238`). | Not integrated: **CHANGES REQUIRED** per PR #27 (C1–C5). |
| [#27](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27) `review/chatgpt-acceptance-181bcdd` | `703f6a71840559e98f49b4c897ca5216d4018133` | External ChatGPT review of #26 @ `181bcdd`: **CHANGES REQUIRED**. C1 no required-check inventory; C2 required INFO → PASS; C3 JSON/TSV disagreement undetected; C4 contract approval not the final gate; C5 tag pins, 30-day retention, head-not-merge testing; C6 obsolete coordination wording (fixed here). | Recorded; source of the merge-policy update. |

External review packets (self-contained, verdict requested on the exact SHA): `coordination/review-requests/` (README, PR-14, PR-26).

## File overlap and conflicts
- **#1 and #5** share 14 `infra/aws-cdk/**` files. #5's commit 1 imports #1 @ `e494bcf`, minus `lib/evidence-validator.ts`, `scripts/validate-evidence.ts`, `test/evidence-validator.test.ts` and the `validate:evidence` npm script. #5 is used, and #1's copy is dropped.
- Every other pair is disjoint. #2 and #1 both add `.github/workflows/*`, but with different filenames.
- No textual merge conflicts.

## Integration changes
1. `.github/workflows/aws-cdk.yml`: PR #1's workflow adapted to PR #5.
   - covers both stacks and both cdk-nag packs; requires exactly 4 reports with 0 Non-Compliant
   - uses the evidence path `evidence/aws/aws-remediation-vpc-rds/SHA256SUMS`
   - adds the `cfn-s3-selflog` gate, a synth-drift diff, `npm ci --ignore-scripts`, and a wider credential-variable check
2. `.github/workflows/offline-validation.yml`: runs `scripts/validate-all.sh --python-only`.
3. PR #2 re-merge (`e76d8a4`, merging `e7399fb`):
   - My interim changes to `run_restore_scenario.sh`, `postgres-restore-evidence.yml` and `ci-service-40630856041-1/NOTE.md` (from `f3a8f17`) conflicted with the owner's v2. I resolved all three to the **owner's version**.
   - The interim evidence run `integration-offline-20261028T180134Z` was removed in `e76d8a4`. It was then **restored byte-for-byte** from `fb70afd`, with a `STATUS.json` marking it HISTORICAL-KNOWN-INVALID and a row in `evidence/postgres/runs/INDEX.md`, so that no earlier evidence record is deleted.
   - Every v1 failure record (`ci-service-40630856041-1`) is unchanged from `e610015`, apart from the owner's added NOTE.md text and STATUS.json.
   - The #2 source commit `e7399fbb538504f723d1fb83e32ce50604807b8e` is an ancestor of HEAD. Re-merging it reports "Already up to date".
   - The v2 workflow has its own pinned `cdk-synth` job with no `CDK_DEFAULT_*`, so it overlaps `aws-cdk.yml`. That is harmless.
4. Interface fix between #3 and #2 (`05941a9`): on v2's 12-column `COMMANDS.tsv`, `evidence/shared/validate_evidence.py postgres-negatives` silently reported `NEGATIVES OK: 0 negative steps`.
   - It now finds columns by header name, so it handles v1 and v2.
   - It errors when it finds zero negatives.
   - 2 new unit tests (15/15).
   - It agrees with v2's `verify_evidence.py` on every committed run: 6/6 on the current runs, and 4 false PASSes on the v1 CI run.
5. `infra/aws-cdk/README.md` and `evidence/shared/README.md`: fixed stale paths and stale "not wired into CI" text.
6. `scripts/validate-all.sh`, `.gitignore`, this report, and `coordination/tasks.json`.

## Validation result
I ran `PG_BIN=<conda-forge PG 16.15>/bin scripts/validate-all.sh` on the box with no AWS credentials (Node 20.19.2, Python 3.13.5). Result: **PASS, all 33 steps** (latest run 2026-10-28 ~17:45 EDT, PG 16.15). The full step list is in the draft PR description.
- Shared validator: 16/16 (stricter: a negative that is not PASS is an error).
- Entra:
  - 25/25 tests
  - baseline exit 0
  - fixture drift OK
  - evidence verify OK
- aws-cdk:
  - tsc OK, Jest 33/33, synth OK
  - 4 nag reports with 0 Non-Compliant
  - no S3 self-logging
  - no synth drift
  - SHA256SUMS OK
- Postgres v2:
  - The committed CURRENT runs `ci-service-40741329107-1`, `ci-offline-40741329107-1` and `local-offline-v2-20261028T180208Z` are VERIFIED.
  - `ci-mismatch-control-40741329107-1` is REJECTED, as intended.
  - The v1 runs report HISTORICAL (exit 3).
  - The self-test passes.
  - A fresh offline v2 run passes 38/38 and is verified with `--require-artifacts`.
  - The shared validator cross-check agrees.

## Acceptance conditions for merging PR #7 into `main`
Evaluated at the PR #7 head pushed with this report. Under the merge policy above, an automated merge needs AC1–AC5 MET for the same SHA, and AC6 is a separate gate. Machine-readable copy: `coordination/tasks.json` → `acceptance_conditions_for_main`.

| # | Condition | Status | Detail |
|---|---|---|---|
| AC1 | An independent review (human or independent reviewer, e.g. ChatGPT) approves the **exact** candidate SHA. Provenance must be bound to that SHA, and author or agent self-review does not count. *Reworded per PR #27 C6.* | **UNMET** | No approval for any PR #7 head. PR #14 @ `eb8d259` counts only for PR #2's harness v2, and it requests changes on integrated #5. PR #27 reviewed #26, not #7. |
| AC2 | Security exceptions recorded **and approved**. | **PARTIAL** | EX-01..EX-04 are recorded and test-enforced, but not approved. PR #14 B5-1: the suppressions are already applied. |
| AC3 | All checks pass on that SHA (PR #7 CI + `scripts/validate-all.sh`). | **Met for `afb41278` and `49122f24`; CI pending for this head** | Local `validate-all` PASS 33/33 on this tree. |
| AC4 | Docs match the code. | **PARTIAL** | PR #1 is still open with the superseded design; #4 baseline choices are unconfirmed. |
| AC5 | No unresolved blocking findings in integrated code. | **UNMET** | PR #14 B5-1/B5-2 on integrated #5. Fixed in this commit: the shared `postgres-negatives` reported OK on all-NOT_RUN runs. |
| AC6 | Final human portfolio acceptance (Ian). Separate gate. | **UNMET** | Not requested; it follows AC1–AC5. |

## Open issues / blockers before `main`
- #6 needs the self-logging fix and regenerated evidence. Once that is done it can merge cleanly, because its paths are disjoint.
- #5's security exceptions EX-01..EX-04 need an owner's approval.
- #4's baseline choices need an owner's confirmation: risk policies stay report-only, the device-compliance scope, and the 12 privileged roles.
- #2's v2 `cdk-synth` job duplicates `aws-cdk.yml`. It is not a blocker.
- #1 should be closed as superseded by its owner. Integration did not close it.
- No PR has a GitHub review approving an exact SHA. Review evidence so far is in PR #3, #14 and #27 report files.
- PR #14 B5-1/B5-2 on #5: fix the KMS key-admin statement, and approve or revoke the suppressions.
- PR #27 C1–C5 on #26 (acceptance verifier): required-check inventory, INFO handling, JSON/TSV consistency, contract as final gate, workflow pinning.
- Actions are pinned by tag, not SHA (carried over from #1/#2).
