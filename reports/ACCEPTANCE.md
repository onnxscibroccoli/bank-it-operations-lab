# Acceptance packet: vertical slice (DRAFT)

Worker D, independent review and integration. Drafted on 2026-10-28 at about 14:55 EDT.
Status: **DRAFT candidate. Not merged to main. No production changes. No AWS, Entra or Graph calls.**

This is a lab acceptance gate. It is not an audit, a certification, or a production sign-off. All results below come from
commands that were actually run: GitHub Actions run IDs are cited, and local runs are labelled as local.

## 1. First executable acceptance command

```bash
bash scripts/acceptance/run.sh <40-hex commit SHA> --out acceptance-out
#   exit 0 = every required check PASS | 1 = any FAIL | 2 = no FAIL but a required check UNKNOWN
python3 scripts/acceptance/verify_results.py acceptance-out      # independent re-derivation of every verdict
```

- `run.sh` refuses anything that is not a full 40-hex SHA. It creates a detached `git worktree` at that SHA and asserts HEAD == SHA
  (`CHECKOUT`). Every check runs inside that worktree, using the target's own tooling.
- CI: `.github/workflows/acceptance.yml`. It triggers on push to `acceptance/vertical-slice`, on PRs to `main`, and on
  `workflow_dispatch` (input `target_sha`). The target is the dispatch SHA if one is given, otherwise the PR head SHA (not
  the synthetic merge commit), otherwise the pushed SHA.
- Jobs:
  - `gate-selftest`: synthetic FAIL, required-UNKNOWN, empty and unknown-verdict sets must not pass.
  - `acceptance`: the full run.
  - `defect-control`: injects CA002 *Require MFA* → report-only into the checked-out target. The job asserts exit 1,
    `ENTRA-02=FAIL` and overall FAIL.

| Group | Checks (all required) | Tooling reused |
|---|---|---|
| AWS static | AWS-00 no creds in env; AWS-01 `npm ci --ignore-scripts`; AWS-02 `tsc`; AWS-03 jest; AWS-04 credential-free `cdk synth --no-lookups`; AWS-05 cdk-nag gate (4 reports, non-empty, 0 Non-Compliant); AWS-06 S3 self-logging; AWS-07 synth drift vs committed templates | `infra/aws-cdk`, `evidence/shared/validate_evidence.py` |
| PostgreSQL recovery | PG-01 fresh offline pg_dump/pg_restore exercise (harness v2, unix-socket cluster); PG-02 `verify_evidence.py --require-artifacts`; PG-03 harness self-test | `tests/integration/postgres` |
| Entra offline | ENTRA-01 unit tests; ENTRA-02 validator on baseline; ENTRA-03 fixture drift; ENTRA-04.n committed evidence `--verify` | `identity/entra`, `tests/entra`, `evidence/entra` |
| Workers A/B/C | ACC-A-01/02 contract tests + fixture drift; ACC-B-01 runner tests, ACC-B-02 runner on `checks.json`; ACC-C-01 adapter tests, ACC-C-02 static-evidence, ACC-C-03 live-offline (exit 4 → UNKNOWN) | `schemas/acceptance`, `tools/acceptance`, `acceptance/modules` |
| Reports / hashes | HASH-n: every committed `evidence/**/SHA256SUMS` (shared `hashes`: no missing file, mismatch, or self-listing); run output hashed and re-verified by `verify_results.py` | shared validator |
| Defect controls | DEFECT-AWS: bucket made to log to itself; DEFECT-ENTRA: CA002 report-only; DEFECT-HASH: one byte appended to an AWS evidence file. Each is **PASS only if** the checker exits nonzero **and** its output matches the intended reason regex. A crash counts as UNKNOWN, not "detected". | as above |

## 2. Branch review verdicts

The review was done from code and CI, not from implementer claims. All three branches are single commits on top of
`overnight/integration` @ `49122f2457aff41f14a3f3dec4ae378ac0147cff` (PR #7). Integrating them therefore brings that history in as the base.

| Branch | Commit | Verdict | Evidence / reasons |
|---|---|---|---|
| `acceptance-contract` (A) | `6a28847b222ad0d32a45a78f7350dee30ddc7749` | **ACCEPT** | Locally: 19 unit tests OK, `make_fixtures.py --check` FIXTURES OK. The schema reuses the shared `_check`/`manifest`/`hashes` instead of a new validator. It fails closed (any FAIL or required UNKNOWN → BLOCKED). Note: `tests/acceptance-contract/fixtures/repo/evidence/acceptance-tampered/SHA256SUMS` is *deliberately* broken. The sweep initially flagged it (HASH-21 FAIL, local). It is now exercised by ACC-A-01 and excluded from the evidence sweep. |
| `acceptance-runner` (B) | `838d537abff7edd3f870c8c3d19d7287dd1dce97` | **ACCEPT** | Locally: 27 unit tests OK; full run PASS with shared-validator OK. Adversarial spot checks: one byte appended to an AWS evidence file → `aws-evidence-hashes-pipeline` FAIL with stages `[1,0]` (pipefail honoured), exit 1. A `bash` check in a modified `checks.json` → REFUSED, exit 2. Limitation: the allowlist (no `npm`/`bash`/PG tools) means it cannot run AWS synth or PG recovery itself, and it records HEAD but does not check out a SHA. `run.sh` covers both. |
| `acceptance-adapters` (C) | `c6aa238ed3a3fe38624e00e60a4a1469f6a49a73` | **ACCEPT WITH INTEGRATION FIX** | Locally: 34 unit tests OK; static-evidence `all` PASS (aws-cdk 5, postgres 14, entra-offline 40 checks). **Defect found:** `postgres --mode live-offline` with no PG binaries printed `PASS ... non_pass=1 (NOT_EXECUTED TOOL_UNAVAILABLE)` and exited **0**, which contradicts its README ("never as PASS"). The cause was `ModuleResult.status` treating PASS+NOT_EXECUTED as PASS. Fixed in `93de4b3` (any NOT_EXECUTED → NOT_EXECUTED, exit 4), with regression test `test_pass_plus_not_executed_is_not_pass`. After the fix, the local result is exit 4. |
| `overnight/integration` base (PR #7) | `49122f2457aff41f14a3f3dec4ae378ac0147cff` | **ACCEPT AS CANDIDATE BASE ONLY** | `run.sh 49122f2…` locally: all AWS, Entra, hash and defect checks PASS; PG-01/02 UNKNOWN (no `initdb` on the review box) → exit 2, as designed. Finding: the shared `postgres-negatives` printed `NEGATIVES OK: 6 negative steps failed for the intended reason` on a run where every step was NOT_RUN (local `validate-all.sh`). It only detects false PASSes, so its OK message overstates. The v2 verifier rejected the same run. |

## 3. CI results (real)

Commit tested: `93de4b3d16da807eb4f86996daf9d65110a83c41` (A+B+C integrated + fix).

| Run | Workflow / event | Conclusion | Notes |
|---|---|---|---|
| [40748705521](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748705521) | acceptance / push, created 14:49:37 EDT | **success** | `acceptance`: `OVERALL=PASS required=43 fail=[] unknown=[]`, `verify_results: OK overall=PASS rows=45`. PG-01 used `/usr/lib/postgresql/18/bin`. `defect-control`: `OVERALL=FAIL` with ENTRA-01..04, ACC-B-02, ACC-C-01..03 FAIL → asserted, job success. `gate-selftest`: success. |
| [40748714760](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748714760) | acceptance / pull_request | **success** | same head SHA |
| [40748714223](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748714223) | aws-cdk / pull_request | **success** | existing PR #5/#7 workflow |
| [40748714695](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748714695) | offline-validation / pull_request | **success** | existing `validate-all.sh --python-only` |
| [40748714361](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748714361) | postgres-restore-evidence / pull_request | **success** | existing harness v2 workflow |
| [40748357905](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748357905) | acceptance / push @ `76442fe` (A+B, before C) | success | superseded |

The commit that adds this file changes HEAD. Its own acceptance run result is recorded in the PR, not here, because the file cannot cite its own run.

## 4. Requirement status

| ID | Requirement | Status | Basis |
|---|---|---|---|
| R1 | Checkout of a specific commit SHA | PASS | `CHECKOUT` in run 40748705521 |
| R2 | AWS static checks | PASS | AWS-00..07 in run 40748705521 |
| R3 | PostgreSQL recovery | PASS | PG-01..03 in run 40748705521 (offline unix-socket cluster, PG 18) |
| R4 | Entra offline validation | PASS | ENTRA-01..04.1 in run 40748705521 |
| R5 | Reports/hashes validated | PASS | HASH-1..17 + `verify_results.py` OK in run 40748705521 |
| R6 | Deliberate defect detected | PASS | DEFECT-AWS/ENTRA/HASH + `defect-control` job in run 40748705521 |
| R7 | Nonzero on FAIL / required UNKNOWN | PASS | `defect-control` exit 1; `gate-selftest` 8/8; local exit 2 on PG UNKNOWN (box without initdb) |
| R8 | Workers A/B/C reviewed + integrated | PASS | §2; ACC-A/B/C in run 40748705521 |

## 5. Open gaps

| Gap | Status |
|---|---|
| `run.sh` results are not yet emitted as an A-contract document (`schemas/acceptance`) and checked with `check_acceptance.py`. No independent `concur` record exists yet. | UNKNOWN |
| C's `contract.py` is a self-declared *provisional* contract, not yet aligned with A's schema | UNKNOWN |
| AWS is static only: synth/nag/tests. Nothing deployed and no account evidence (by design; no AWS mutations allowed) | UNKNOWN (not executed) |
| PostgreSQL is a local pg_dump/pg_restore exercise, not an RDS snapshot/PITR restore | UNKNOWN (not executed) |
| Entra uses synthetic fixtures only. Tenant state is not claimed (`tenantStateClaimed=false`) | UNKNOWN (not executed) |
| Postgres `ARTIFACTS.sha256` files list gitignored dumps, so they cannot be verified from the repo alone (only from the 90-day CI artifacts) | UNKNOWN |
| Shared `postgres-negatives` OK message overstates on an all-NOT_RUN run (see §2). The v2 verifier is authoritative. | FAIL (finding, non-blocking: not a required gate) |
| The PR to `main` carries all of `overnight/integration` (PRs #2–#5 plus coordination files). Merging needs a human decision; this packet does not approve it. | UNKNOWN |
| `REPORT-*` checks confirm reports exist; they do not certify their content | UNKNOWN |
