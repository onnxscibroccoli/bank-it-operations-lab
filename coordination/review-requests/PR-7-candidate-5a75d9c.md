# Review request: PR #7 candidate `5a75d9ca742e28d8f0a18b590b1bfecb5f7b2b03` and its tested merges

**Purpose:** independent concurrence on **exactly** this candidate and its tested merges with `main`. It was frozen after Ian's 21:41 recovery directive and 21:50 execution alignment (P1-P5).

| Role | SHA |
|---|---|
| Candidate (`overnight/integration` head = PR #7 head) | `5a75d9ca742e28d8f0a18b590b1bfecb5f7b2b03` |
| Base (`main`, verified at runtime by the gate) | `7f50348bf1370381615eaed91c02607fe41de2f5` |
| Tested merge, `candidate/main-validation-5a75d9c` (`--no-ff`) | `38e82679475a607aa8c109f9f368133d5ea0e21c` |
| Tested merge, GitHub PR #7 synthetic `refs/pull/7/merge` | `decbb08813e3780d048d98fd7c6a8c596eee2dc0` |
| Gate code executed by merge-eligibility (manifest-pinned, hash-verified) | `5a75d9ca742e28d8f0a18b590b1bfecb5f7b2b03`; manifest at `evidence/acceptance:trusted-gate/gate-manifest.json` (commit `274a3b9`) |

Both merges have parents (`7f50348`, `5a75d9c`), and their trees are identical to the candidate's (`ce12bfe`).

> **Earlier reviews and approvals do not transfer.** That covers PR #31's CHANGES REQUIRED on `1fdf25a`, PR #30 on `b908a66`, every note on `e9310f3` (frozen before the 21:50 alignment and superseded), `1fdf25a`, `b908a66`, `a29f4d9`, `08cdf11`/`771045e`, `7fe6d72`, `5f159f1`, `02ac2de`, `82ab7e6` and `eb42b23`, and PRs #14 and #27–#31.
>
> A verdict counts only if it names `5a75d9ca742e28d8f0a18b590b1bfecb5f7b2b03`. For AC1, the review must be a GitHub review on PR #7 that is APPROVED with `commit_id` = `5a75d9ca…`, from an account that is not `onnxscibroccoli`, is on the trusted `reviewer_allowlist` and has Write or higher.

Everything here is offline, synthetic and SIMULATION. There are no cloud or tenant calls, no credentials and no deploys.

## What changed since `1fdf25a` (`git log --oneline 1fdf25a..5a75d9c`)

| Commit | What |
|---|---|
| `ce69f84` | **F4:** an AC1 approver must be on the trusted allow-list, have write/maintain/admin (API), and not be the author.<br>**F5:** any undismissed CHANGES_REQUESTED blocks AC1.<br>**R6:** `verify_trusted_gate.py`.<br>New file `.github/acceptance/trusted-config.json` |
| `e9310f3` | The workflow reads the trusted manifest (main, else `evidence/acceptance`), checks out the gate by SHA and hash-verifies the gate and the candidate's verifier files. Records |
| `5a75d9c` | **P2:** AC2/AC4/AC5 come only from `ACCEPTANCE-ATTESTATION v2` comments. Each binds candidate, main, tested merge(s), criterion, decision, evidence refs and the workflow run (`run.head_sha` is checked through the API, `actions: read`). GitHub authenticates the author and timestamp, and edited comments are ignored. The decision artifact has separate `candidate_produced` and `independent_acceptance` sections.<br>**P3:** exception states PROPOSED / APPROVED / REJECTED / APPROVED_WITH_CONDITIONS / SUPERSEDED (+ CONDITIONS_VERIFIED). Only the owner decides. Scope must equal the applied rule + resources. A conditional approval counts only after it is verified.<br>**P1:** extra regressions. Records (round 8, EX reconciliation) |

**P5 (already in `ce69f84`/`e9310f3`):**
- `orgs-security.blocker.ids` = `[B6-1, B6-2, B6-3]`.
- The DatabaseKey CreateGrant wording in `least-privilege-key.ts:8-10` is fixed.
- README states 7/25.
- Historical checksums are kept (`superseded/pass3-pre-B5-2/`).
- KMS wildcards: `least-privilege-key.ts` has no `kms:Create*` / `kms:Put*` action; the only hit is the comment at `:7`. The committed synth has 0 hits.

## Claimed results (verify)

| Item | Claim |
|---|---|
| Local `validate-all` (PostgreSQL 16.15) | PASS, 46/46 steps, on `38e8267` |
| integration-gate: PR run 40803398543 (`decbb08`), main-validation push 40803394450 (`38e8267`), candidate push 40803392582 | Each run: every job succeeds except merge-eligibility, which fails by design (NOT ELIGIBLE). `TRUSTED GATE VERIFIED` in all three |
| aws-cdk 40803398477, offline-validation 40803398592 / 40803392447, postgres-restore-evidence 40803398499 | success |
| `scripts/ci/tests` | 123 tests OK (local and CI) |
| Decision artifacts (`candidates/5a75d9c…/runs/` on this branch) | AC3 `MET_AT_RUNTIME` for both merges (base = `main` `7f50348`).<br>AC1 UNMET: the allow-list is empty, and there is no qualifying review.<br>AC2 UNMET: EX-01..EX-04 PROPOSED.<br>AC4/AC5 UNMET: no attestation.<br>**NOT ELIGIBLE** |

## Exception reconciliation (nothing approved; no approver invented)

| ID | Register | Suppression | Required scope | State |
|---|---|---|---|---|
| EX-01 | PROPOSED | `infra/aws-cdk/lib/secure-storage-stack.ts:60` | `NIST.800.53.R5-S3DefaultEncryptionKMS AccessLogsBucket83982689` | PROPOSED (reconciled) |
| EX-02 | PROPOSED | `secure-storage-stack.ts:65,72` | `NIST.800.53.R5-S3BucketReplicationEnabled AccessLogsBucket83982689 DataBucketE3889A50` | PROPOSED (reconciled) |
| EX-03 | PROPOSED | `network-database-stack.ts:241-246` | `AwsSolutions-IAM5 RdsMonitoringPolicy5DA8ACAC` | PROPOSED (reconciled) |
| EX-04 | PROPOSED | `network-database-stack.ts:226-234` | `AwsSolutions-IAM4 BackupPlanPostgresRole2A2CEBDF` | **UNRESOLVED** |

## Questions

1. **P1:** can any approval other than an allow-listed, write-permitted non-author APPROVED review on the exact 40-hex SHA satisfy `reviews.ac1_from_reviews`? Consider supersession, dismissal, and CHANGES_REQUESTED on earlier commits.
2. **P2:** can an attestation for another candidate, main, tested merge or run, an edited one, or one by an unauthorized account satisfy AC2/AC4/AC5 (`reviews.attestations`)? Can anything in the candidate tree satisfy them?
3. **P3:** are the state semantics right: latest owner decision wins; APPROVED_WITH_CONDITIONS needs a later CONDITIONS_VERIFIED; SUPERSEDED/REJECTED/PROPOSED never count; scope must match exactly?
4. **P4/R6:** on `pull_request` the job definition comes from the candidate's workflow file. A candidate could remove the verify step. The manifest makes this visible, but only UA-3 enforces it. Is that an acceptable documented limit until UA-3?
5. Was any check removed or weakened relative to `1fdf25a`? Legacy `ACCEPTANCE-DECISION v1` comments are now ignored on purpose.

## Verdict format

`CONCUR` / `CHANGES REQUIRED` / `COMMENT`; the exact SHAs checked; the reviewer's identity and the date; numbered findings with file:line.

## Review disposition

**NOT YET REQUESTED.** It has been prepared and not sent; Ian will route it. No independent review exists for this exact SHA.
