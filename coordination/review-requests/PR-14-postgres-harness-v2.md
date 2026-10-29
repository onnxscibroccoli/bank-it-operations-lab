# Review request: PR #14, independent verification of the PostgreSQL harness v2 (false-PASS remediation)

**What we need from you:** a verdict on **exact SHA `eb8d259588f2d1ba8a8787cf2c37044617cbcbdb`** (PR #14 head). Choose one of
**ACCEPT**, **ACCEPT WITH CONDITIONS** or **REJECT**, and give reasons tied to the criteria below. A verdict on any other SHA does not count.

You do not need repository access to use this document. Everything below is public at the URLs given, and no secrets are needed. Nothing in this
lab deploys anything or calls AWS, Entra or Microsoft Graph.

## Identifiers
| Item | Value |
|---|---|
| Repository | https://github.com/onnxscibroccoli/bank-it-operations-lab (public) |
| PR under review | https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14 (draft, base `main`, head branch `review/pr3-pr6`) |
| Exact SHA to judge | `eb8d259588f2d1ba8a8787cf2c37044617cbcbdb` |
| Commits in PR | `765787a` review notes; `981db0a` checkpoint 1; `eb8d259` checkpoint 2 (harness v2 verification) |
| Subject of the verification | PR #2 https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2, harness v2 at `2aac93c22d9e5682c42ed08ec79167d93709e1ff` (code) and `e7399fbb538504f723d1fb83e32ce50604807b8e` (committed evidence runs) |
| Where the subject is integrated | PR #7 https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7 (`overnight/integration`); `e7399fb` is an ancestor |

## Scope summary
PR #14 is a **review-notes PR**. It changes one file, **`reports/review-pr3-pr6.md`** (522 lines), and adds no code. That file contains:
1. Verdicts on PRs #3–#6 at their exact heads:
   - #3 `fb36341`: Approve.
   - #4 `d302c99`: Approve with comments.
   - #5 `099479e`: **Request changes**. B5-1: cdk-nag suppressions were applied while the exception register still says PROPOSED. B5-2: the KMS key-admin statement allows grant or key-policy escalation. B5-3: overlap with #1.
   - #6 `e5e7f46`: **Request changes**. B6-1: the CloudTrail access-log bucket logs to itself. B6-2: an exempt-role-name SCP bypass. B6-3: CDK was delivered instead of Terraform, and the deviation is undocumented.
2. "Checkpoint 2", a verification of the PostgreSQL harness v2 that fixes 4 false-PASS negative tests (N01, N04, N05, N06) found in CI run 40630856041.
   Its own conclusion is "Status of priority B: **remediated**", with non-blocking follow-ups.

### The defect being remediated
In harness v1, a negative test counted as PASS whenever its command exited non-zero. In CI run
https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041 the cause of failure was unrelated: pg_dump 18 emitted
`SET transaction_timeout`, which a PostgreSQL 16 server rejects, and a table was missing. Four negatives were still reported as PASS.

Harness v2 makes these changes:
- `tests/integration/postgres/expectations.tsv` declares every case with an expected exit code and a **required reason regex**.
- Setup steps are separately checked cases, and each fault step is one command that depends on its setup (`--needs`).
- Outcomes are classified as unexpected_success or wrong_reason (FAIL); version_mismatch, environment_error, setup_failure or missing_executable (ERROR); and NOT_RUN.
- An independent `verify_evidence.py` re-derives every verdict from the logs.
- A `selftest_harness.sh` with 26 assertions checks deliberate bad cases, replays the run 40630856041 logs, and includes a forged-PASS case.
- A CI negative control runs pg_dump 18 against postgres:16 and must be reported as version_mismatch, never PASS.

## What we checked before sending this (2026-10-28, ~17:45 EDT)
| Claim | Finding |
|---|---|
| PR #14 head is `eb8d259…` | **Confirmed** (`gh pr view 14`) |
| "Independent verification complete on PR #14" | **Partly confirmed.** The verification is in the *content* of `reports/review-pr3-pr6.md` at `eb8d259`. There are **no GitHub reviews, no comments and no CI checks on PR #14**. Every PR in this repo, #14 included, is authored by the same GitHub account (`onnxscibroccoli`). The reviewer's independence ("a reviewer who did not write this code") is asserted in the file and cannot be shown from GitHub metadata. |
| "4 false-PASS cases confirmed eliminated" | **Consistent with the file and with our own runs.** On replay, the file reports N01/N05/N06 → `ERROR/version_mismatch` and N04 → `ERROR/environment_error`, with N02/N03 still PASS. Our local harness self-test at `e7399fb` passes. The shared validator flags the 4 false PASSes in the historical run and accepts the three current v2 runs. |
| Subject CI | Push run https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107 on `2aac93c`: success, 5 jobs. Runs on `e7399fb`: https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741536430 (push, success) and https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741546543 (pull_request, success). |
| Limitation stated by the reviewer | The reviewer did **not** run the PostgreSQL scenario locally, because the box had no PostgreSQL. They relied on CI and on comparing artifacts. We ran it locally: PG 16.15, harness v2, 38/38 PASS, verifier VERIFIED. |

## Files changed in PR #14
- `reports/review-pr3-pr6.md` (only file)

## Files the verification covers (the subject: PR #2 at `2aac93c` / `e7399fb`)
- Code: `tests/integration/postgres/{lib.sh, run_restore_scenario.sh, expectations.tsv, expectations.selftest.tsv, selftest_harness.sh, verify_evidence.py, verify_evidence.sh, seed.sql, fingerprint.sql}`
- Workflow: `.github/workflows/postgres-restore-evidence.yml`
- Evidence: `evidence/postgres/runs/**`, index in `evidence/postgres/runs/INDEX.md`

## How to verify (public clone, no credentials)
```bash
git clone https://github.com/onnxscibroccoli/bank-it-operations-lab && cd bank-it-operations-lab
git checkout eb8d259588f2d1ba8a8787cf2c37044617cbcbdb && less reports/review-pr3-pr6.md     # the notes under review (see "Checkpoint 2")
git checkout e7399fbb538504f723d1fb83e32ce50604807b8e                                       # the subject
bash tests/integration/postgres/selftest_harness.sh; echo $?                                 # expect 0, 26/26 assertions (no DB needed)
python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-service-40741329107-1; echo $?   # expect 0
python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-mismatch-control-40741329107-1; echo $?  # expect 1 (rejected)
python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-service-40630856041-1; echo $?   # expect 3 (historical)
# optional, needs PostgreSQL 16 or 18 binaries: PG_BIN=/path/to/bin bash tests/integration/postgres/run_restore_scenario.sh offline
```
The historical failing run's logs are under `evidence/postgres/runs/ci-service-40630856041-1/logs/`, and the v1 false PASSes are visible on line 3 of each N01, N04, N05 and N06 log.

## Known exceptions and gaps
- There are no GitHub reviews, comments or CI on PR #14 itself, and every PR has the same author account, so independence is asserted rather than demonstrated.
- The reviewer's open follow-ups for PR #2 are all non-blocking:
  1. Environment and version-error regexes are evaluated after the declared reason, so an output that contains both strings could be classified as PASS. There is no self-test case for this.
  2. `verify_evidence.py` trusts the run's own `EXPECTATIONS.tsv` copy instead of comparing it with the repo file or the recorded `sha256_expectations.tsv`.
  3. The `cdk-synth` job reports green when no CDK app exists.
  4. An optional second control could bypass the S04 version gate.
- Our own finding (now fixed on `overnight/integration`, not part of PR #14): the shared `evidence/shared/validate_evidence.py postgres-negatives`
  printed "NEGATIVES OK" for runs whose negatives were all NOT_RUN. It now errors on any negative that is not PASS.
- The PR #14 verdicts on #5 and #6 are **Request changes**. #5 is already integrated in PR #7, so B5-1 and B5-2 are open blockers for PR #7.

## Specific review questions
1. Does Checkpoint 2 show that each of N01, N04, N05 and N06 can no longer be reported PASS when its failure has an unrelated cause? Is the replay of run 40630856041 a sufficient demonstration?
2. Is follow-up (1), the regex-ordering gap, a real false-PASS path? If so, is it blocking?
3. Is follow-up (2), the self-attested `EXPECTATIONS.tsv`, a way to forge a PASS that the verifier would accept?
4. Is the `version-mismatch-control` CI job a meaningful negative control, given that it stops at S04 and never exercises the negatives?
5. Are the verdicts on #5 (B5-1, B5-2) and #6 (B6-1, B6-2) correct and properly evidenced?
6. Is anything in the notes stated as VERIFIED that the cited evidence does not actually support?

## Acceptance criteria (for ACCEPT)
- Every VERIFIED claim in Checkpoint 2 can be reproduced from the public repo at the cited SHAs, using the commands above.
- No path remains by which a negative test that fails for an unrelated reason is reported PASS, or any such path is explicitly listed as a condition.
- The remediation's CI runs (40741329107, 40741536430, 40741546543) are on the cited SHAs and succeeded.
- The notes do not overstate. Limitations, including the PostgreSQL scenario not being run locally by the reviewer and the asserted independence, are disclosed.

Please reply with: `VERDICT for eb8d259588f2d1ba8a8787cf2c37044617cbcbdb: <ACCEPT | ACCEPT WITH CONDITIONS | REJECT>`, followed by your answers to questions 1–6 and any conditions.
