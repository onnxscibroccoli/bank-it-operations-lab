# Review request: PR #7 candidate `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45` and its tested merges

**Purpose:** independent concurrence on **exactly** this candidate. It contains the repairs for PR #33 (CHANGES REQUIRED on `2e3041a`: D3-a and the nits).

| Role | SHA |
|---|---|
| Candidate (`overnight/integration` head = PR #7 head) | `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45` |
| Base (`main`, verified at runtime) | `7f50348bf1370381615eaed91c02607fe41de2f5` |
| Tested merge, `candidate/main-validation-a9d0f64` (`--no-ff`) | `cbbabfe38e2f35cf2b64301b994c906c10a33584` |
| Tested merge, PR #7 `refs/pull/7/merge` | `172e392b7dee7523d044ef485ed9d46594b3a414` |
| Gate pin (manifest `evidence/acceptance:trusted-gate/gate-manifest.json` @ `da4f14e`) | `af49a27d6cef040478edafe8324d83b919ea9ffb`. This is the gate commit, the candidate's parent, not the candidate. Its `scripts/ci` tree `a87084f`, trusted config `7a65ba5` and `integration-gate.yml` `9723b38` are the **same git objects** as in the candidate. `independent_review: null`, so TRUSTED GATE UNVERIFIED |

Both merges have parents (`7f50348`, `a9d0f64`) and the candidate's tree (`ec09df1`).

> **Nothing transfers.** That covers PR #33 on `2e3041a`, PR #32 on `5a75d9c`, the stale `52e362e`, and every earlier SHA. A verdict counts only if it names `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45`.
>
> For AC1, it must be an APPROVED review on PR #7 with that `commit_id`, from an allow-listed, write-permitted account that is not `onnxscibroccoli`.
>
> For the pin, a qualifying APPROVED review must be on `af49a27…`.

Offline / SIMULATION only. No cloud or tenant calls, no credentials, no deploys.

## Changes since `2e3041a`

| Commit | What |
|---|---|
| `af49a27` (gate) | **D3-a:** `merge_eligibility.py` computes gate trust itself (`verify_trusted_gate.gate_trust_at_runtime`), and any `--gate-trust` file is ignored. For every manifest file the expected hash is `git show <gate_sha>:path`, hashed at runtime. It must equal the manifest and the executing copy: the running `scripts/ci` (no extra files), the `--config` read, and `integration-gate.yml` at `GITHUB_WORKFLOW_SHA`. An unknown workflow commit, or a gate checkout not at the pin, fails closed. `--build` hashes git objects of the pin. The gate checkout now includes `.github/workflows`.<br>**Nit:** every attested `tested_merge` must have parents exactly (main, candidate), checked via `GET /commits/{sha}` or this run's own merge identity.<br>14 new tests (152 total) |
| `a9d0f64` | Records: `INTEGRATION.md` Round 10, `tasks.json` `round10_pr33_repairs`, and the P2 wording now login-bound |

**Not re-pinned to `52e362e`:** its `scripts/ci` and workflow predate the D3-a code. Pinning it would correctly fail the executing-file check.

**`trusted-gate/README.md`:** the `ce69f84` row now reads 21:47 EDT (commit 21:44). `48660b7` is described as the grandparent. A new row records `af49a27`.

## Results (verify)

| Item | Claim |
|---|---|
| Local `validate-all` (PostgreSQL 16.15) | PASS, 46/46 steps, on `cbbabfe` |
| integration-gate: PR run 40806586164 (`172e392`), main-validation 40806583574 (`cbbabfe`), push 40806583044 | Only merge-eligibility fails (NOT ELIGIBLE).<br>The gate's own trust computation reports exactly one reason, "no independently reviewed gate pin". So in CI the executing workflow (`GITHUB_WORKFLOW_SHA` = the tested commit), the running scripts and the config all matched `git show af49a27:…` |
| aws-cdk 40806586095, offline-validation 40806586447 / 40806582288, postgres-restore-evidence 40806586124 | success |
| `scripts/ci/tests` | 152 OK (local and CI) |
| Decisions (`candidates/a9d0f64…/runs/`) | AC3 MET_AT_RUNTIME (both merges). AC1/AC2/AC4/AC5 UNMET. TRUSTED GATE UNVERIFIED. **NOT ELIGIBLE** |

## Questions

1. **D3-a:**
   - Can any gate file's expected hash come from anything other than the pinned commit's git objects?
   - Re-run your probe (fake workflow + updated manifest hash + valid review). See `tests/test_pr33_pin_binding.py`.
   - Is `GITHUB_WORKFLOW_SHA` the right identifier for the executing workflow on `pull_request` and `push`?
2. Is ignoring `--gate-trust` complete, or can any workflow-written file still influence the verdict? Consider `--reviews` / `--identity`, which the workflow also produces. Those are only trustworthy when the executing workflow equals the reviewed pin, and that is exactly what is now bound.
3. **Residual:** a workflow that never invokes the gate at all is stopped only by UA-3. Is that stated accurately?

## Verdict format

`CONCUR` / `CHANGES REQUIRED` / `COMMENT`; the exact SHAs; the reviewer's identity and the date; numbered findings with file:line.

## Review disposition

**NOT YET REQUESTED.** It has been prepared and not sent; Ian will route it.
