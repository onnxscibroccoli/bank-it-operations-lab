# Assurance note: acceptance-state transition invariants (I1, I2)

Branch `acceptance/vertical-slice`, PR #26. The code commit assessed is `17cfaea3bef13296f4e224f7985f77a963a5bccc`.
Written by Worker D on 2026-10-28 (EDT). Status: **DRAFT. This is not an approval.** No acceptance has been granted: the
state recorded by CI for every candidate is `REVIEW_PENDING`.

History: this note supersedes nothing. `reports/ACCEPTANCE.md` (written at `181bcdd`) is kept and has an addendum added below it.
The independent review of `181bcdd` (PR #27, `reports/independent/chatgpt/acceptance-181bcdd-review.md`) found
C1–C4. Its probes reproduced false-acceptance cases against the verifier as it stood at `181bcdd`. The fixes are listed in §4.

## 1. State model

**Per check** (`results.tsv` / `results.json` rows; file `scripts/acceptance/run.sh`)

`verdict ∈ {PASS, FAIL, UNKNOWN, INFO}`, `required ∈ {yes, no}`.

- `INFO` is allowed only on the advisory id `DEFECT-INJECTED` (see the inventory).
- The required set is fixed by the reviewed inventory `scripts/acceptance/required-checks.v1.json`, version `1.0.0`:
  - 26 fixed ids;
  - group `HASH-1..n` with n ≥ 17;
  - group `ENTRA-04.1..n` with n ≥ 1.

**Execution state of a run**, computed by `gate()`:

| Execution state | `overall` | `run.sh` exit |
|---|---|---|
| `EXECUTION_PASS` | `PASS` | 0 |
| `EXECUTION_FAIL` | `FAIL` | 1 |
| `EXECUTION_UNKNOWN` | `UNKNOWN` | 2 |

**Decision state for (output dir O, commit S)** (`scripts/acceptance/decide.py`):

| Decision state | Exit |
|---|---|
| `ACCEPTED` | 0 |
| `EXECUTION_FAIL` | 1 |
| `INVALID` | 1 |
| `EXECUTION_UNKNOWN` | 2 |
| `REVIEW_PENDING` | 5 |
| `REVIEW_BLOCKED` | 6 |

`verify_results.py O --accept-for S` delegates to `decide.py`. **ACCEPTED(O, S) ⇔ `decide.py O --sha S` exits 0.**

**Transitions** (run once per invocation; nothing is persisted between invocations):

```
run.sh S ──► O (sealed: SHA256SUMS, results.json bound to S)
O ──verify(O, expect_sha=S)──► INVALID                  (any C1/C3/binding/hash error)
   └─ consistent ──► EXECUTION_FAIL | EXECUTION_UNKNOWN | EXECUTION_PASS     (gate())
EXECUTION_PASS ──export to A's contract + check_acceptance.py──►
   contract INVALID                          ──► INVALID
   BLOCKED only by "lacks concurrence"       ──► REVIEW_PENDING   (technically eligible)
   BLOCKED by dispute/other                  ──► REVIEW_BLOCKED
   AUTOMATIC_TECHNICAL_ACCEPTANCE            ──► ACCEPTED         (requires concur findings for S, via --reviews)
```

**Preconditions (trusted base):**

- **P1.** The verifier code is the reviewed copy:
  - `scripts/acceptance/verify_results.py`;
  - `scripts/acceptance/decide.py`;
  - `scripts/acceptance/required-checks.v1.json`;
  - A's `schemas/acceptance/check_acceptance.py`;
  - `evidence/shared/validate_evidence.py`.
- **P2.** `S` is a full 40-hex SHA supplied by the invoker (CI: `TARGET_SHA`), not read from O.
- **P3.** Reviewer findings are supplied only through `--reviews` and are not authenticated (§6).
- **P4.** The state sets above are closed. Any other value is rejected.

## 2. Invariants

- **I1.** For every O and S: if O contains a row with `required=yes` and verdict ≠ `PASS` (in particular `FAIL`, `UNKNOWN` or `INFO`), or O omits a
  required inventory check, then ACCEPTED(O, S) is false.
- **I2.** For every O and every S′ ≠ S, where O was produced by `run.sh S`: ACCEPTED(O, S′) is false. In addition, review findings for S do not
  satisfy the review requirement for S′. A change of source commit therefore needs a new run and a new review.

## 3. Enforcement and evidence

### I1: **ENFORCED** (under P1–P4)

| # | Mechanism | Code |
|---|---|---|
| 1 | Single gate: PASS only if there is at least one required row, every required row is `PASS`, there is no unknown verdict and `required` is in {yes, no}. A required `INFO` gives FAIL. | `verify_results.py` `gate()` (l.42). `run.sh` calls it (l.246: `vr.gate(rows)`); the duplicate gate that existed at `181bcdd` was removed. |
| 2 | Inventory coverage: omitted, duplicate, arbitrary or downgraded rows are rejected, as are groups below min or with gaps. `run.sh` records every inventory id that did not run as `UNKNOWN`. | `verify_results.py` `inventory_errors()` (l.56–91); `run.sh` §3 (l.234–238) |
| 3 | Complete-record check: TSV == JSON for all six fields, typed fields, and counters (`required`, `pass`, `fail`, `unknown`) recomputed. A forged `overall` is rejected. | `verify_results.py` `verify()` (l.109–193) |
| 4 | Verdict re-derived from the `# exit_code:` log trailer. Defect controls must exit nonzero with the intended reason. | `verify()`, log loop |
| 5 | Decision ladder: execution FAIL or UNKNOWN can never reach `ACCEPTED`, whatever reviews are supplied, with a final defence-in-depth check. | `decide.py` `decide()` (l.112–146) |
| 6 | A's contract fails closed: FAIL, required UNKNOWN, missing concurrence or an empty document gives BLOCKED. | `schemas/acceptance/check_acceptance.py` `decide()` (l.226–247) |
| 7 | B's runner returns exit 1 when any of its checks fails. It runs as the required check `ACC-B-02`, so a B failure is a required FAIL. | `tools/acceptance/runner.py` l.447, l.523 |

Tests:

- **Exhaustive gate enumeration:** `verify_results.py --selftest` enumerates all 11 111 result sets of length 0–4 over {PASS, FAIL, UNKNOWN, INFO, SKIPPED} × {yes, no} and asserts `gate()==PASS` ⇔ (at least one required row and all required rows PASS). It finds 0 violations and passes 12/12 fixed cases.
- **`scripts/acceptance/tests/test_invariants.py` (32 tests):**
  - classes `C1Inventory`, `C2Info`, `C3Records` and `I1`;
  - `C4Decision.test_concur_review_of_tested_commit_is_the_only_path_to_accepted`;
  - `I1.test_required_fail_never_accepted_even_with_concur` and `test_required_unknown_never_accepted_even_with_concur`.
- **A's tests:** `tests/acceptance-contract/test_acceptance_contract.py`:
  - `test_fail_blocks_even_with_exception` (l.130);
  - `test_required_unknown_blocks_but_advisory_unknown_does_not` (l.135);
  - `test_empty_document_fails_closed` (l.141).

  These run as `ACC-A-01`.
- **Discrimination check (local):** the C1–C3 test classes were run against the verifier as it stood at `85c66cf`, which already had the INFO fix. 9 of 18 fail (8 failures, 1 error), so the tests distinguish the fixed verifier from the earlier one.

CI evidence: run [40775509497](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40775509497) (push, `17cfaea`, created 17:52 EDT, **success**).

- `gate-selftest`: `I1 exhaustive: 11111 result sets, 0 violations`, `Ran 32 tests … OK`.
- `defect-control`:
  - CA002 report-only injected → `OVERALL=FAIL` (ENTRA-01..04.1, ACC-B-02, ACC-C-01..03 and SOURCE-BINDING FAIL);
  - `decision: EXECUTION_FAIL`;
  - `accept-for … exit=1`.
- `acceptance`: `OVERALL=PASS required=44` → `decision: REVIEW_PENDING (execution=EXECUTION_PASS, contract=BLOCKED, reviews=0)`, so it was **not ACCEPTED**.

Same SHA, triggered by the PR: [40775515456](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40775515456) **success**.

### I2: **PARTIALLY ENFORCED**

Enforced within one decision:

| Mechanism | Code |
|---|---|
| `run.sh` accepts only a 40-hex SHA and checks it out in a detached worktree, asserting HEAD == S | `run.sh` l.36, l.83–89 (`CHECKOUT`) |
| After all checks, the worktree must still be exactly S and clean. A dirty tree (e.g. the defect run) gives a required FAIL. | `run.sh` l.223–230 (`SOURCE-BINDING`) |
| The verifier binds O to the expected S given by the invoker (P2): `target_sha` must be 40-hex, equal S, and be named in the CHECKOUT and SOURCE-BINDING rows. The inventory sha256 must equal its copy at S (`git show S:…`). | `verify_results.py` `verify()` l.173–182 |
| The contract export sets `tested_source_commit = S` and anchors the evidence bundle to S. A rejects a requirement commit ≠ document commit, evidence without an anchor for S, and a review of another commit. | `decide.py` `stage_bundle()` / `export()`; `check_acceptance.py` l.142, l.154, l.207 |
| B records the source state (HEAD, dirty, porcelain) in RUN.json; it is recorded, not enforced | `runner.py` `source_state()` l.318 |

Tests:

- `I2.test_acceptance_does_not_transfer_to_another_commit`, `test_review_of_previous_commit_does_not_carry_over`, `test_rebinding_results_json_to_new_commit_rejected`, `test_dirty_or_moved_worktree_not_accepted`, `test_short_or_symbolic_sha_rejected`.
- `C3Records.test_expected_commit_argument_binds`.
- A's `test_reviewer_must_be_independent_and_review_tested_commit` (l.121).

CI: run 40775509497, step *"I2: EXECUTION_PASS bound to the target SHA only, never to its parent"*. It printed `EXECUTION_PASS … for 17cfaea…`, then `execution-pass-for: REJECTED (inconsistent or unbound output) for 85c66cfa…` with `exit=1 (must be nonzero)`.

Why only PARTIALLY:

- **No persisted acceptance record.** No acceptance record bound to a SHA is committed or stored anywhere. Decisions are re-derived on each run, and the artifacts (`decision.json`, `acceptance-contract.json`) are kept for 30 days. "Invalidation" therefore holds only because acceptance is never carried over: every new SHA starts with no run and no review. Nothing revokes or supersedes an earlier record, because none exists.
- **Nothing outside the gate enforces it.** `main` has no branch protection or rulesets. The API returned *"Branch not protected"* (404) and `[]` on 2026-10-28. So nothing stops a merge of a new commit on the strength of an older commit's green checks. GitHub check runs are per-SHA, but they are not required.
- **The SHA is trusted from the invoker (P2).** If the invoker passes the wrong SHA, the gate can only show that the run and the SHA disagree. That still blocks acceptance, but the binding is only as good as the SHA the caller supplies.
- **Inventory binding needs git.** The binding to the copy at S runs only where `git show S:…` succeeds (in CI it does; otherwise the check is skipped).

## 4. Independent-review findings C1–C4: fix and regression test

| Finding (PR #27) | Fix (commit `17cfaea`) | Regression tests (`scripts/acceptance/tests/test_invariants.py`) |
|---|---|---|
| **C1:** arbitrary single-row bundle accepted; no inventory | Versioned inventory `required-checks.v1.json`. `inventory_errors()` gives exact coverage. `run.sh` records every inventory id. The inventory sha256 is recorded and bound. | `C1Inventory.test_review_probe_arbitrary_single_row_rejected` (the review's own probe), `test_omitted_required_check_rejected`, `test_downgraded_required_flag_rejected`, `test_arbitrary_replacement_rejected`, `test_duplicate_id_rejected`, `test_dynamic_group_gap_and_shortfall_rejected`, `test_inventory_hash_mismatch_rejected` |
| **C2:** `gate(required INFO) == PASS` (also in `run.sh`) | Required rows must be PASS/FAIL/UNKNOWN, and only PASS satisfies them. One gate implementation (`run.sh` imports it). The advisory INFO allow-list comes from the inventory. First fixed in `85c66cf`, unified in `17cfaea`. | `C2Info.test_review_probe_gate_required_info`, `test_required_info_in_full_bundle_rejected`, `test_advisory_info_not_allowed_where_inventory_forbids`, `test_exhaustive_gate_selftest` |
| **C3:** JSON/TSV disagreement accepted; no expected-commit input | Full typed record equality, recomputed counters, and `--sha` / `--execution-pass-for` / `--accept-for` binding to an invoker-supplied SHA | `C3Records.test_review_probe_json_disagrees_minimal` (the review's probe), `test_json_record_disagrees_in_full_bundle_rejected`, `test_counter_disagrees_rejected`, `test_untyped_field_rejected`, `test_forged_overall_rejected`, `test_verdict_flipped_against_log_rejected`, `test_expected_commit_argument_binds` |
| **C4:** contract not the final gate; execution PASS reads as acceptance | `decide.py` exports the real run into A's contract (evidence bundle with a MANIFEST anchored to S), evaluates it with A's unmodified `check_acceptance.py`, and separates EXECUTION_PASS from REVIEW_PENDING. `--accept-for` exits 0 only for ACCEPTED. `run.sh` now prints "execution: … This is NOT acceptance". CI asserts REVIEW_PENDING (exit 5). | `C4Decision.test_execution_pass_without_review_is_review_pending_not_accepted`, `test_concur_review_of_tested_commit_is_the_only_path_to_accepted`, `test_dispute_blocks`, `test_self_review_invalid`; CI step "C4: final decision … = REVIEW_PENDING" in run 40775509497 |

Follow-ups only (not changed here):

- **C5:** pin `actions/*` to full commit SHAs, cut artifact retention to 7 days, and validate the combined candidate against current `main` before any merge.
- **C6:** `coordination/tasks.json` still carries obsolete merge restrictions. The coordinator should update it; this note does not edit coordinator-owned files.

## 5. What "ACCEPTED" would require (none of it exists yet)

1. An `EXECUTION_PASS` run for exact SHA S.
2. Independent `concur` findings with `reviewed_commit = S` from someone other than the recorder (`--reviews`).
3. `decide.py` returning `ACCEPTED`.
4. A human portfolio decision. That decision sits outside this gate, and this note does not provide it.

## 6. Limitations

- **Offline and lab-only.** AWS is checked by synth, cdk-nag and tests only; nothing is deployed and no account is touched. PostgreSQL is a local pg_dump/pg_restore exercise, not an RDS restore. Entra uses synthetic fixtures with `tenantStateClaimed=false`. This note is not an audit, certification or production sign-off.
- **No independent sign-off.** No concur review exists, so every real decision so far is `REVIEW_PENDING`. The `ACCEPTED` path has only been exercised with synthetic reviewer records in unit tests.
- **Reviewer identity is not authenticated.** `--reviews` entries are plain strings. Binding them to GitHub review or commit provenance (for example, an approving PR review by a different account on SHA S) is not implemented.
- **The verifier is trusted (P1).** Hashes in O show the files are consistent with their digests, not that they are authentic. A malicious invoker who controls the verifier code is out of scope. Changes to the inventory or verifier need review like any other code; the inventory's `reviewed_by` says its own independent review is pending.
- **No persisted record and no branch protection** (see I2 above).
- **Head-only testing.** CI tests the PR head, not a merge with current `main` (C5).
- **The I1 exhaustive proof covers `gate()` only**, over result sets of length 0–4. Larger sets rely on `gate()` being a fold over rows. `decide.py`'s ladder is covered by unit tests, not by enumeration.
