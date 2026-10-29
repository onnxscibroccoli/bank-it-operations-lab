# Acceptance evidence for candidate `b908a669b302ff37f2c2ca79ed828f65e5a9f432`

This lives **outside the candidate tree** (orphan branch `evidence/acceptance`), so recording it cannot change the candidate SHA.
Each `runs/<run_id>/` directory is the `acceptance-decision-<tested_sha>` artifact, downloaded unmodified from that GitHub Actions run.
The artifact holds `run-identity.json` (from `scripts/ci/provenance.py`) and `acceptance-decision.json` (from `scripts/ci/merge_eligibility.py`).
To re-check, download the artifact yourself from the run URL and compare.

Recorded 2026-10-28 21:10 EDT by the integrator. This is not a review and not an approval.

## AC decisions per run

| run | event | kind | candidate | base | tested | AC1 | AC2 | AC3 | AC4 | AC5 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [40798139838](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798139838) | push | direct | `b908a669b302` | `-` | `b908a669b302` | UNMET | UNMET | UNMET | UNMET | UNMET | NOT ELIGIBLE |
| [40798145700](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798145700) | pull_request | merge | `b908a669b302` | `7f50348bf137` | `659450c853d6` | UNMET | UNMET | MET_AT_RUNTIME | UNMET | UNMET | NOT ELIGIBLE |
| [40798160682](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798160682) | push | merge | `b908a669b302` | `7f50348bf137` | `c11e0de90270` | UNMET | UNMET | MET_AT_RUNTIME | UNMET | UNMET | NOT ELIGIBLE |

AC2 and AC4 are PARTIAL in `tasks.json`. The decision shows them as UNMET because anything other than a bound MET is not satisfied.

## All runs for this candidate (per-job results)

- [integration-gate push 40798160682](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798160682) on `candidate/main-validation-b908a66` @ `c11e0de90270`: **failure**, 18/19 jobs succeeded; not success: merge-eligibility=failure
- [integration-gate pull_request 40798145700](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798145700) on `overnight/integration` @ `b908a669b302`: **failure**, 18/19 jobs succeeded; not success: merge-eligibility=failure
- [integration-gate push 40798139838](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798139838) on `overnight/integration` @ `b908a669b302`: **failure**, 18/19 jobs succeeded; not success: merge-eligibility=failure
- [offline-validation pull_request 40798145424](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798145424) on `overnight/integration` @ `b908a669b302`: **success**, 1/1 jobs succeeded
- [postgres-restore-evidence pull_request 40798145411](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798145411) on `overnight/integration` @ `b908a669b302`: **success**, 5/5 jobs succeeded
- [aws-cdk pull_request 40798145397](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798145397) on `overnight/integration` @ `b908a669b302`: **success**, 1/1 jobs succeeded
- [offline-validation push 40798139775](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798139775) on `overnight/integration` @ `b908a669b302`: **success**, 1/1 jobs succeeded
- [aws-cdk push 40798139730](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798139730) on `overnight/integration` @ `b908a669b302`: **success**, 1/1 jobs succeeded
