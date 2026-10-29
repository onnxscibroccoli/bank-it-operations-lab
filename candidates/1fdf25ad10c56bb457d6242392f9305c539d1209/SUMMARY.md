# Acceptance evidence for candidate `1fdf25ad10c56bb457d6242392f9305c539d1209`

This lives outside the candidate tree. Each `runs/<run_id>/` is the `acceptance-decision-<tested_sha>` artifact, downloaded unmodified: run identity, reviews API snapshot, security-exceptions check and decision.
The gate code ran from pinned `4e6fef4f5d05a72378f0e4c5ec75154efe821710` (`main` does not carry the gate yet). The candidate's `scripts/ci` is identical to it (`git diff 4e6fef4 1fdf25a -- scripts/ci` is empty).

Recorded 2026-10-28 ~21:31 EDT by the integrator. This is not a review and not an approval.

## AC decisions per run

| run | event | kind | candidate | base (= main at runtime) | tested | AC1 | AC2 | AC3 | AC4 | AC5 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [40800359209](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800359209) | push | direct | `1fdf25ad10c5` | `-` (`-`) | `1fdf25ad10c5` | UNMET | UNMET | UNMET | UNMET | UNMET | NOT ELIGIBLE |
| [40800364073](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800364073) | pull_request | merge | `1fdf25ad10c5` | `7f50348bf137` (`7f50348bf137`) | `07eea1cefdc1` | UNMET | UNMET | MET_AT_RUNTIME | UNMET | UNMET | NOT ELIGIBLE |
| [40800374574](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800374574) | push | merge | `1fdf25ad10c5` | `7f50348bf137` (`7f50348bf137`) | `85063e80c624` | UNMET | UNMET | MET_AT_RUNTIME | UNMET | UNMET | NOT ELIGIBLE |

- **AC1:** "no APPROVED review on the exact candidate by an account other than the PR author onnxscibroccoli" (reviews API, PR #7).
- **AC2 and AC5:** UNMET, including the BLOCKING USER ACTION UA-1: 5 applied suppressions are tied to PROPOSED EX-01..EX-04.

## All runs for this candidate (per-job results)

- [integration-gate push 40800374574](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800374574) on `candidate/main-validation-1fdf25a` @ `85063e80c624`: **failure**, 18/19 jobs succeeded; not success: merge-eligibility=failure
- [integration-gate pull_request 40800364073](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800364073) on `overnight/integration` @ `1fdf25ad10c5`: **failure**, 18/19 jobs succeeded; not success: merge-eligibility=failure
- [integration-gate push 40800359209](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800359209) on `overnight/integration` @ `1fdf25ad10c5`: **failure**, 18/19 jobs succeeded; not success: merge-eligibility=failure
- [offline-validation pull_request 40800364076](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800364076) on `overnight/integration` @ `1fdf25ad10c5`: **success**, 1/1 jobs succeeded
- [postgres-restore-evidence pull_request 40800363954](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800363954) on `overnight/integration` @ `1fdf25ad10c5`: **success**, 5/5 jobs succeeded
- [aws-cdk pull_request 40800363940](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800363940) on `overnight/integration` @ `1fdf25ad10c5`: **success**, 1/1 jobs succeeded
- [offline-validation push 40800359259](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800359259) on `overnight/integration` @ `1fdf25ad10c5`: **success**, 1/1 jobs succeeded
- [aws-cdk push 40800359350](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800359350) on `overnight/integration` @ `1fdf25ad10c5`: **success**, 1/1 jobs succeeded
