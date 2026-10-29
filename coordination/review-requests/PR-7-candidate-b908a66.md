# Review request: PR #7 candidate `b908a669b302ff37f2c2ca79ed828f65e5a9f432` and its tested merges

**Purpose:** independent concurrence on **exactly** this candidate and the merges with `main` that were tested:

| Role | SHA |
|---|---|
| Candidate (`overnight/integration` head = PR #7 head) | `b908a669b302ff37f2c2ca79ed828f65e5a9f432` |
| Base (`main`) | `7f50348bf1370381615eaed91c02607fe41de2f5` |
| Tested merge, `candidate/main-validation-b908a66` (`--no-ff`) | `c11e0de90270fa5834ebb85c28069d3314a5dbf2` |
| Tested merge, GitHub PR #7 synthetic `refs/pull/7/merge` | `659450c853d6e4ff5865ea2c4ad339ce57d4e524` |

Both merges have parents (`7f50348`, `b908a66`), and their trees are identical to the candidate's tree.

> **Earlier reviews and approvals do not transfer.** That includes anything about:
> - the PR #26 head `eb42b23` (tag `checkpoint/eb42b23`)
> - the earlier candidates and heads `82ab7e6`, `02ac2de`, `5f159f1`, `7fe6d72`, `08cdf11`, and the `08cdf11` synthetic merge `771045e`
> - PR #14 and PR #27
> - PR #28, the findings note on `08cdf11` (it is "not an approval" and comes from the same GitHub account)
> - every per-PR review of #2–#5, #20 and #22
>
> A verdict counts only if it names `b908a669b302ff37f2c2ca79ed828f65e5a9f432`. If any code changes, there will be a new candidate and a new request.

Nothing here is secret. The lab is offline, synthetic and SIMULATION: no cloud or tenant calls, no credentials, nothing deployed.

## Where things are

- Code: https://github.com/onnxscibroccoli/bank-it-operations-lab/tree/b908a669b302ff37f2c2ca79ed828f65e5a9f432
- Run evidence lives outside the candidate tree, on branch `evidence/acceptance` under `candidates/b908a669b302ff37f2c2ca79ed828f65e5a9f432/`. It holds GitHub's run artifacts `acceptance-decision-<tested_sha>` (run identity plus decision) and the per-job results.
- This packet sits on the same branch at `coordination/review-requests/PR-7-candidate-b908a66.md`, so writing it did not change the candidate SHA.

## What changed since the previous candidate `7fe6d72` (verify with `git diff --name-status 7fe6d72 b908a66`)

| File | Change |
|---|---|
| `.github/workflows/integration-gate.yml` | merge-eligibility: fetch-depth 2, `provenance.py` step, identity-bound decision uploaded as artifact (90 days) |
| `scripts/ci/provenance.py` (new) | Run identity: candidate, base and tested merge, with parent and event cross-checks |
| `scripts/ci/merge_eligibility.py` | AC3 `COMPUTED_AT_RUNTIME`. MET requires `met_for {candidate_sha, base_sha, tested_sha}`, each full 40-hex, matching the run. Naked or legacy MET is rejected. `--lint-tasks` added |
| `scripts/ci/tests/test_merge_eligibility_binding.py` (new) | 18 regression tests: missing, abbreviated, wrong, non-hex SHA; mixup; runtime AC3 cases; lint |
| `scripts/ci/tests/test_gate_required.py` | Updated for the new CLI; no assertion removed |
| `scripts/validate-all.sh` | New step "tasks lint (no naked MET)" (44 steps) |
| `README.md`, `infra/aws-cdk/README.md`, `evidence/entra/BASELINE-CHOICES-PENDING.md` (new) | AC4 docs: modules, gate behaviour, PR #1 superseded, Entra baseline choices **pending** owner confirmation |
| `coordination/tasks.json`, `reports/INTEGRATION.md`, `coordination/review-requests/*` | Records: AC3 design, AC4 detail, the 7fe6d72 packet (already in `08cdf11`) |

There are no changes to integrated module code, to the evidence runs, or to the M365 or incident modules.

## Claimed results (verify)

| Item | Claim |
|---|---|
| Local `validate-all` (PostgreSQL 16.15) | PASS, 44/44, on the candidate and on `c11e0de` |
| integration-gate on `c11e0de` (run 40798160682), PR #7 synthetic `659450c` (run 40798145700), push of `b908a66` (run 40798139838) | 18 of 19 jobs succeed in each run. merge-eligibility fails by design |
| AC3 decision artifacts | `MET_AT_RUNTIME` for kind=merge identities `c11e0de` and `659450c`. `UNMET` on the direct push run (not tested as a merge with main) |
| Fresh SIMULATION incident run | All six requirements PASS on apt-installed PostgreSQL 18.6. No NOT_EXECUTED items |
| Eligibility | NOT ELIGIBLE. AC1 UNMET (this review), AC2 PARTIAL, AC4 PARTIAL, AC5 UNMET. AC6 is a separate human gate |

## Questions

1. Is AC3 really bound to the tested identity? Could a run for one SHA make another SHA eligible? Check `provenance.py` and `merge_eligibility.py`, and look for parent or event spoofing, a moved base, or abbreviated or case variants.
2. Do the 18 binding regressions cover a missing, abbreviated, wrong or non-hex SHA and a candidate-vs-merge mixup? Is anything else missing?
3. PR #28's finding R1′ remains in part: AC1, AC2 and AC5 are still self-reported fields in `tasks.json`. They now need a full SHA binding and evidence, but the gate does not query GitHub for an approving review or owner approval. Is that acceptable as the documented limit, or must it block?
4. Do the docs now match the code (AC4)? PR #1 is shown as superseded. The Entra choices are listed as pending, not confirmed.
5. Is any check removed or weakened relative to `7fe6d72`?

## Verdict format

Reply with:
- `CONCUR` / `CHANGES REQUIRED` / `COMMENT`
- the exact SHAs `b908a669b302ff37f2c2ca79ed828f65e5a9f432` and the tested merge(s) you checked
- the reviewer's identity and the date
- numbered findings with file and line

A GitHub PR review on PR #7 with `commit_id` = `b908a669…`, from an account other than the author, is the strongest form of evidence for AC1.

## Review disposition

**NOT YET REQUESTED.** It has been prepared and not sent; Ian will route it. No independent review exists for this exact SHA.
