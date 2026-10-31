# Review request: PR #26, acceptance vertical slice (first executable acceptance command)

**What we need from you:** a verdict on **exact SHA `181bcdd1420d699c37aa928b636b9332aca83e57`** (PR #26 head). Choose one of
**ACCEPT**, **ACCEPT WITH CONDITIONS** or **REJECT**, and give reasons tied to the criteria below. A verdict on any other SHA does not count.

You do not need repository access to use this document. Everything below is public at the URLs given, and no secrets are needed. Nothing in this
lab deploys anything or calls AWS, Entra or Microsoft Graph. This is a lab acceptance gate, not an audit or certification.

## Identifiers
| Item | Value |
|---|---|
| Repository | https://github.com/onnxscibroccoli/bank-it-operations-lab (public) |
| PR under review | https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26 (draft, base `main`, head branch `acceptance/vertical-slice`) |
| Exact SHA to judge | `181bcdd1420d699c37aa928b636b9332aca83e57` |
| Built on | `overnight/integration` @ `49122f2457aff41f14a3f3dec4ae378ac0147cff` (PR #7). That commit is an ancestor, so PR #26's diff against `main` also contains all of PR #7. |
| Components integrated | A `acceptance-contract` @ `6a28847` (PR #23); B `acceptance-runner` @ `838d537` (PR #24); C `acceptance-adapters` @ `c6aa238` (PR #25), plus integration fix `93de4b3` |

## Prior external review of this exact SHA (read first)
PR #27 (https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27, head `703f6a71840559e98f49b4c897ca5216d4018133`, file
`reports/independent/chatgpt/acceptance-181bcdd-review.md`) already reviewed `181bcdd` and concluded **CHANGES REQUIRED**:
- **C1 (High):** `verify_results.py` accepts a self-consistent bundle that contains only an arbitrary required PASS check. There is no trusted required-check inventory.
- **C2 (High):** `gate([{required: yes, verdict: INFO}]) == PASS`.
- **C3 (Medium):** JSON and TSV verdicts can disagree without detection, and the target SHA is not bound to a trusted expected input.
- **C4 (High):** contract approval is not the executable final gate, and review identity strings are not authenticated approval.
- **C5 (Medium):** actions are pinned by tag, not SHA; retention is 30 days, not 7; CI tests the PR head, not the merged candidate.
- **C6:** coordination wording was obsolete. That is now updated on `overnight/integration`.

As of this writing, `181bcdd` is still the PR #26 head, so **none of C1–C5 has been fixed at this SHA**. Please treat this request as a
second opinion on `181bcdd`: confirm or dispute C1–C5, and add anything they miss. If the head moves, a fresh request is needed for the new SHA.

## Scope summary
- The PR adds a single acceptance command, `bash scripts/acceptance/run.sh <40-hex SHA> --out <dir>`, which works as follows:
  - It creates a detached git worktree at that SHA and asserts that HEAD equals the SHA.
  - It runs every check inside that worktree with the target's own tooling.
  - Exit codes: 0 = every required check PASS; 1 = any FAIL; 2 = no FAIL, but some required check is UNKNOWN.
- `scripts/acceptance/verify_results.py` independently re-derives every verdict from the output.
- CI workflow `.github/workflows/acceptance.yml` has three jobs:
  - `gate-selftest`: synthetic FAIL, required-UNKNOWN and empty sets must not pass.
  - `acceptance`: the full run at the target SHA.
  - `defect-control`: injects a planted defect, CA002 "Require MFA" flipped to report-only, and asserts that acceptance FAILS.
- Check groups (43 required):
  - AWS static: AWS-00..07
  - PostgreSQL recovery (harness v2): PG-01..03
  - Entra offline: ENTRA-01..04.n
  - Components A/B/C: ACC-A/B/C-*
  - Evidence hash sweep: HASH-n
  - In-run defect controls (DEFECT-AWS, DEFECT-ENTRA, DEFECT-HASH). Each passes only if the checker exits non-zero **and** its output matches the intended-reason regex.
- `reports/ACCEPTANCE.md` contains component verdicts written by "Worker D": A ACCEPT, B ACCEPT, C ACCEPT WITH INTEGRATION FIX.

## Files changed relative to its base `49122f2` (99 files, all added, +13,240 lines)
- `.github/workflows/acceptance.yml`
- `scripts/acceptance/run.sh`, `scripts/acceptance/verify_results.py`
- `schemas/acceptance/{README.md, acceptance-requirements.schema.json, check_acceptance.py}` (A)
- `tests/acceptance-contract/**` (74 files: tests and synthetic fixtures, including a *deliberately* tampered `SHA256SUMS` fixture) (A)
- `tools/acceptance/**` (5 files: allowlisted runner + tests) (B)
- `acceptance/modules/**` (13 files: aws_cdk, postgres, entra_offline adapters, contract, run, tests) (C)
- `reports/ACCEPTANCE.md`

Relative to `main`, the PR shows 710 files, because it includes PR #7. The GitHub UI lists only the first 100.

## What we verified before sending this (2026-10-28, ~17:45 EDT; read-only via the GitHub API)
| Claim | Finding |
|---|---|
| PR #26 head is `181bcdd` | **Confirmed** |
| Actions run 40749373581 passed | **Confirmed.** https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749373581 is workflow `acceptance`, event push, head_sha `181bcdd1420d699c37aa928b636b9332aca83e57`, conclusion **success**, attempt 1 (14:53–14:56 EDT). |
| "All 43 required checks passed" | **Confirmed, with a precision note.** The run has **3 GitHub jobs**, not 43, and all 3 succeeded. The "43" are *internal* required checks in the `acceptance` job. The artifact `acceptance-40749373581-1/results.json` shows `overall=PASS, required=43, pass=43`. It has 45 rows: 43 required, all PASS, plus 2 non-required, also PASS. |
| "Caught the planted defect" | **Confirmed.** The artifact `acceptance-defect-40749373581-1/results.json` shows `injected_defect=entra-mfa-report-only`, `overall=FAIL`, `required=43`, `pass=35`. The 8 required FAILs are ENTRA-01, ENTRA-02, ENTRA-03, ENTRA-04.1, ACC-B-02, ACC-C-01, ACC-C-02 and ACC-C-03, and the console says `acceptance: FAIL for 181bcdd…`. The `defect-control` job asserted that failure and succeeded. The in-run DEFECT-AWS, DEFECT-ENTRA and DEFECT-HASH controls all PASS (defect detected for the intended reason). |
| Other CI on `181bcdd` | All success: acceptance (PR) https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387217 (3/3 jobs); aws-cdk https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387209 (1/1); offline-validation https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387223 (1/1); postgres-restore-evidence https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387416 (5/5). |
| Reviews | **No GitHub reviews or comments.** The external review in PR #27 says CHANGES REQUIRED (see above). Component verdicts appear only in `reports/ACCEPTANCE.md`, written by the integrator ("Worker D"). Every PR has the same author account. |
| Component freshness | **Discrepancy.** PR #25 (`acceptance-adapters`) now has head `ce39504` (14:48 EDT). PR #26 integrated the older `c6aa238`, so 4 files and 287 lines from PR #25 (e.g. `acceptance/modules/tests/test_emit_shared.py`) are **not** in PR #26. |

## How to verify (public clone, no credentials)
```bash
git clone https://github.com/onnxscibroccoli/bank-it-operations-lab && cd bank-it-operations-lab
git checkout 181bcdd1420d699c37aa928b636b9332aca83e57
bash scripts/acceptance/run.sh 181bcdd1420d699c37aa928b636b9332aca83e57 --out /tmp/acc; echo $?   # 0 expected; 2 if no PostgreSQL binaries (PG checks UNKNOWN)
python3 scripts/acceptance/verify_results.py /tmp/acc                                              # independent re-derivation
less reports/ACCEPTANCE.md .github/workflows/acceptance.yml
# CI artifacts (results.json, SUMMARY.md, console logs) for run 40749373581 can be downloaded from its run page.
```
Needs Node 20 + npm and Python 3.12+. Optional: PostgreSQL 16 or 18 binaries (`PG_BIN`) for PG-01/02.

## Known exceptions and gaps
- The PR has no GitHub review, and every PR shares the same author account, so its component verdicts are self-reported by the integrator.
- It is stale against PR #25 head `ce39504` (see above).
- Inherited from PR #7, these items are still open:
  - AWS security exceptions EX-01..EX-04 are recorded but not approved.
  - PR #14's review rates PR #5 (integrated) **Request changes**: B5-1 (suppressions applied before approval) and B5-2 (KMS key-admin escalation).
  - PR #6 is excluded because of an S3 self-logging finding.
- The defect-control job injects only one planted defect (Entra CA002). The AWS, Entra and hash defects are exercised inside the run, not as separate failing CI jobs.
- `reports/ACCEPTANCE.md` notes that the shared `postgres-negatives` could print OK for all-NOT_RUN runs. That is fixed on `overnight/integration` after `49122f2` and is **not** in PR #26.
- ACC-C-03 live-offline returns exit 4 → UNKNOWN when there are no PostgreSQL binaries. This is by design, and it blocks a PASS.

## Specific review questions
1. Does `run.sh` actually bind every check to the target SHA, using a worktree and asserting HEAD, so that no check reads the caller's working tree?
2. Is the fail-closed rule sound, with any FAIL → exit 1 and any required UNKNOWN → exit 2? Can a crash or a skipped check ever count as PASS?
3. Are the DEFECT-* controls and the `defect-control` job meaningful? Would the planted CA002 defect be missed if ENTRA-02 were silently skipped?
4. Is excluding the deliberately tampered fixture under `tests/acceptance-contract/fixtures/**` from the HASH sweep justified, or does it open a blind spot?
5. Is the integration fix `93de4b3` (PASS + NOT_EXECUTED → NOT_EXECUTED) correct, and does its regression test cover it?
6. Is the 43-check required set enough to call this a vertical slice of the lab, given the AWS static checks, PostgreSQL recovery and Entra offline? What is missing?
7. Does `verify_results.py` independently re-derive verdicts, or does it trust `results.json`?

## Acceptance criteria (for ACCEPT)
- Reproducible: at the exact SHA, `run.sh` exits 0 with the stated tools, and `verify_results.py` agrees.
- Fail-closed: no path by which a FAIL, UNKNOWN, crash or skipped required check yields overall PASS.
- The defect controls detect their defects for the intended reason, and CI goes red if they do not.
- The CI runs cited above are on `181bcdd` and succeeded.
- `reports/ACCEPTANCE.md` does not overstate. Its gaps, including the component staleness and the inherited PR #5/#6 findings, are disclosed or are listed by you as conditions.

Please reply with: `VERDICT for 181bcdd1420d699c37aa928b636b9332aca83e57: <ACCEPT | ACCEPT WITH CONDITIONS | REJECT>`, followed by your answers to questions 1–7 and any conditions.
