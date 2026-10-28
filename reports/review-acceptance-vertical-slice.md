# Independent review: `acceptance/vertical-slice` @ `eb42b23`

- **HEAD reviewed:** `eb42b23747d5b686d9540c93e445a713b4e56c5d` (PR #26 head; equals `origin/acceptance/vertical-slice`). VERIFIED
- **Against:** the false-acceptance cases C1–C6 in PR #27 (`reports/independent/chatgpt/acceptance-181bcdd-review.md`, candidate `181bcdd`) and the repair commit `17cfaea`.
- **Reviewer:** an independent lane (Lane E). I did not implement any of this code. This note does not approve anything, and I have not commented on, approved or merged any PR.
- **Date:** 2026-10-28 (EDT).

Labels: **VERIFIED** means I re-ran it or read the code at this SHA in this session. **UNVERIFIED** means I did not reproduce it.

## Re-runs at eb42b23 (box, offline)

| Run | Result | Status |
|---|---|---|
| `python3 -m unittest discover -s scripts/acceptance/tests -v` | 32/32 OK: C1Inventory 7, C2Info 4, C3Records 7, C4Decision 4, Control 1, I1 4, I2 5 | VERIFIED |
| `verify_results.py --selftest` | gate 12/12; I1 exhaustive over 11111 sets, 0 violations | VERIFIED |
| PR #27 reproduction probes against this SHA's verifier: required INFO, a single `ARBITRARY` row, JSON≠TSV | `gate` → FAIL; `verify` rc 1; `verify` rc 1 (all three were accepted at 181bcdd) | VERIFIED |
| `run.sh eb42b23… --out /tmp/acc-out` | exit 2, overall UNKNOWN. 41 required PASS, 0 FAIL. UNKNOWN: PG-01, PG-02, ACC-C-03 (no PostgreSQL binaries on the box) | VERIFIED |
| `verify_results.py /tmp/acc-out --sha eb42b23…` / `decide.py` | OK, rows=46 / `EXECUTION_UNKNOWN`, contract BLOCKED (not ACCEPTED) | VERIFIED |
| PR #26 CI at eb42b23 (gate self-test, acceptance @ target SHA, defect control CA002, postgres jobs) | all SUCCESS | VERIFIED (check status). I did not re-download the artifacts: UNVERIFIED |
| PostgreSQL path (PG-01/02, ACC-C-03) with real binaries | not run locally | UNVERIFIED (only CI ran it) |

## Per-case verdicts

| Case | Verdict | Evidence |
|---|---|---|
| **C1:** required-check coverage not verified; an arbitrary single row was accepted | **CLOSED in code. One residual (R2).** | `inventory_errors()` rejects missing, duplicate, arbitrary and downgraded IDs, and group gaps or short groups. `run.sh` records UNKNOWN for any inventory ID it did not run. Negative tests C1Inventory ×7 fail for their declared reason, and the PR #27 probe now gets rc 1. VERIFIED. Residual: the inventory is the candidate's own file (`reviewed_by`: "independent review … PENDING"), and the `--sha` inventory binding fails open (see R2). |
| **C2:** required INFO → PASS | **CLOSED** | `gate()` accepts only PASS/FAIL/UNKNOWN for required rows, so INFO counts as FAIL. The INFO allow-list for advisory rows comes from the inventory. `run.sh` imports the same `gate`. C2Info ×4, selftest and the probe all pass. VERIFIED |
| **C3:** JSON/TSV disagreement undetected; no SHA binding | **CLOSED** | `verify()` checks complete-record equality between TSV and JSON, typed fields, log `# exit_code:` trailers, recomputed overall and counters, a 40-hex `target_sha`, and that CHECKOUT/SOURCE-BINDING name the SHA. `--sha`, `--execution-pass-for` and `--accept-for` bind the result to the SHA. C3Records ×7, I2 ×5 and the probe all pass. VERIFIED |
| **C4:** contract not the final gate; unauthenticated reviews | **PARTIALLY CLOSED (open on authentication)** | `decide.py` passes the bundle through worker A's `check_acceptance.py`. It returns ACCEPTED only on `AUTOMATIC_TECHNICAL_ACCEPTANCE`. With no review it returns REVIEW_PENDING (5); a dispute gives 6; the exact recorder string gives INVALID. CI asserts rc 5. VERIFIED. Still open: reviewer strings are unauthenticated (R1, R3), and main has no branch protection (R5). |
| **C5:** unpinned actions, 30-day retention, head-only testing | **OPEN.** Hygiene and provenance, not a false-accept by itself. | `acceptance.yml` uses `actions/checkout@v5`, `setup-node@v5`, `setup-python@v5` and `upload-artifact@v5` by tag. `retention-days: 30`. `TARGET_SHA` = PR head; there is no main+candidate run. VERIFIED (read). The assurance note lists all of this as a follow-up. |
| **C6:** obsolete coordination wording | **OPEN** (coordinator-owned; out of scope) | The assurance note §C6 defers it to the coordinator. I did not check `coordination/tasks.json` content at this SHA: UNVERIFIED |

## Remaining ways a run could be wrongly accepted

- **R1: a fabricated bundle plus any reviewer string gives ACCEPTED, even for a commit that does not exist.** VERIFIED by probe.
  - Setup: I used the test suite's own `build()` to fabricate a full-PASS bundle for SHA `aaaa…aaaa`, which is not a commit. Its logs just say `output`. I added one review `{"reviewer":"anyone","verdict":"concur"}`.
  - Result: `decide.py --sha aaaa…` exits 0 with `ACCEPTED`.
  - Cause: nothing checks that the SHA exists, that the bundle came from CI (no attestation or run-id binding), or that the reviewer is a distinct GitHub identity.
  - Disclosure: the assurance note concedes this in P1/P3. It is still the main open path, so ACCEPTED is meaningful only when the bundle comes from a trusted CI run.
- **R2: the inventory binding fails open.** VERIFIED by code read. The execution probe was blocked by the box's command reviewer: UNVERIFIED by execution.
  - `git_show_sha256()` returns `None` on any git error: not a repo, SHA missing, or file absent.
  - `verify()` then skips the C1 comparison (`if at is not None and …`).
  - Effect: a copy of the verifier and a weakened inventory run outside git, or for a SHA where the file is absent, are never compared against the committed inventory.
  - Fix: when `--sha` is given, treat `None` as an error.
- **R3: self-review detection is exact-string only.** VERIFIED by probe. `reviewer: "Worker D (recorder)"` → ACCEPTED (exit 0). Only the literal `worker-d scripts/acceptance/run.sh (recorder)` is rejected.
- **R4: `execution_state` is self-reported and unchecked.** VERIFIED by probe.
  - Probe: PG-01 UNKNOWN (overall UNKNOWN) with `results.json.execution_state="EXECUTION_PASS"`.
  - Result: `verify_results.py` OK (rc 0), and `decide.py` prints `execution=EXECUTION_PASS`, which also drives `technically_eligible`.
  - The contract still blocked it (REVIEW_BLOCKED, 6), so this is **not** a false-accept today. The decision record is misreported, though, and the defence-in-depth check at `decide.py:145` relies on the same field.
  - Fix: derive the state from the recomputed `gate()` in `verify()` / `decide.py:130`.
- **R5: no executable merge gate.** VERIFIED via the GitHub API.
  - `main`: `protected: false`, no required status checks, 0 rulesets.
  - The `acceptance` job is green when the decision is REVIEW_PENDING (it asserts rc 5). Nothing stops a merge without review, and a green check could be misread as acceptance.
- **R6: CI trusts the candidate's own verifier and inventory.**
  - VERIFIED (read): the workflow runs `scripts/acceptance/*` from the checked-out PR code. A PR that edits the verifier or inventory grades itself.
  - UNVERIFIED (default `actions/checkout` behaviour, not re-checked): on `pull_request` that checkout is the synthetic merge ref, while `TARGET_SHA` is the head.
  - Needs: a verifier and inventory taken from the base branch, or CODEOWNERS on `scripts/acceptance/`.
- **R7: `postgres-run/` is not covered by the top-level hashes.** VERIFIED by code read.
  - It is excluded from the top-level `SHA256SUMS` and from the `decide.py` staging.
  - It is verified only at run time (PG-02, `verify_evidence.py`). `verify_results.py` never re-checks `postgres-run/SHA256SUMS`, so editing it after the run goes undetected after the fact.
- **Checked and benign** (VERIFIED, read):
  - `run.sh:80` cleanup `|| true`.
  - `run.sh:82` `fetch … || true`: the checkout and the CHECKOUT row are verified afterwards.
  - `run.sh:118` `grep -c … || true`: grep exits 1 when the count is zero; the comparisons that follow still gate.
  - Every `set +e` in `acceptance.yml` captures `rc` and is followed by a `test`. There is no `continue-on-error`. The gate steps run with `if: always()` and assert the exit codes.

## Suggested minimum before treating ACCEPTED as meaningful

1. Bind ACCEPTED to a CI provenance record (run id and artifact attestation). Require the SHA to exist (`git cat-file -e`) (R1).
2. Fail closed on the inventory lookup when `--sha` is given (R2).
3. Replace reviewer strings with a GitHub PR review by an account other than the author on SHA S (R1, R3).
4. Recompute `execution_state` and do not trust the field (R4).
5. Branch protection on `main` that requires a decision state of ACCEPTED, not job-green (R5).
6. Take the verifier and inventory from the base branch (R6).
7. Verify `postgres-run/SHA256SUMS` in `verify_results.py` (R7).
8. Then C5: pin actions to SHAs, retention 7 days, a main+candidate run.

**Overall:** C1–C3 are closed at eb42b23 for the cases PR #27 reproduced. C4 is only partly closed: ACCEPTED is still reachable with a fabricated bundle and an arbitrary reviewer string (R1/R3). C5 and C6 are open. This is a findings note, not an approval.
