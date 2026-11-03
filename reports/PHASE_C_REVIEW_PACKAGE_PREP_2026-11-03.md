# Phase C review package: preparation checklist, 2026-11-03

This is a checklist of the materials an independent reviewer will need in Phase C (independent acceptance). It is **preparation only**:

- It is not the frozen packet. Freezing it is task B10 in [HUMAN_DECISION_PACKET_2026-11-03.md](HUMAN_DECISION_PACKET_2026-11-03.md).
- It is not a review.
- It records **no** human approval.
- The sign-off at the end is blank and **NOT SIGNED**.

Prepared from the state at 18:15–18:30 EST (UTC-5).

**Evidence labels.** In this file, `modules.json` `evidence_class` values are shown as:

- **EXECUTED:** `EXECUTED_CI` or `EXECUTED_LOCAL`.
- **STATIC:** `STATIC_VALIDATED`, or no class declared but checked by an offline CI job.
- **SIMULATION:** `SIMULATION`.
- **NOT_EXECUTED:** never run, including every live AWS, Entra, Graph or M365 target. The lab has no live target that was executed.

## 1. Exact SHAs to review

The reviewer must record the exact full SHA they reviewed. A later push needs a fresh review (`USER_ACTIONS_REQUIRED.md` section 1, step 6).

| What | SHA | Source |
|---|---|---|
| `main` (base) | `8e2df97b558e69032e52a50ed0adfd311ad04578` | `GET /repos/onnxscibroccoli/bank-it-operations-lab/commits/main` |
| Candidate head `integration/candidate-20261103c` (CANDIDATE, no PR) | `0ad046825855f2c3e90861981624e2fb8373c24d` | `git ls-remote`; `coordination/INTEGRATION_MANIFEST.md@0ad0468` |
| Candidate tested SHA (full workflow set) | `614d006ae049aed269dc404aa5b84a7c04b55d8e` | `coordination/INTEGRATION_MANIFEST.md@0ad0468` |
| Proposed gate commit (UNREVIEWED, not applied) | `39c71f9eebf8bb72663515a29b52609d02dceea4` | `coordination/INTEGRATION_MANIFEST.md@0ad0468`. PR #42 @ `8065a44` recommends `a518b03e` instead (`coordination/T16_RECONCILIATION.md@0ad0468`); the reviewer must resolve which one is pinned |
| Current trusted pin | `evidence/acceptance` @ `750de1c694c4912f12bb5bb76a20ba74bc208213` (gate_sha `ea0c235`) | `GET /branches/evidence%2Facceptance`; `acceptance/rulesets/README.md@9589d89` |
| This report's source (PR #39) | head at the time of freezing | `GET /pulls/39` |

**The candidate moves.** Commits after `614d006` on `-c` are records-only (`git log 614d006..0ad0468`). The frozen packet must name a single SHA and give the full run set for it.

## 2. Modules and evidence

Sources: `coordination/modules.json@0ad0468` (28 modules: 27 INTEGRATED, 1 SUPERSEDED) and `@8e2df97` (`review-notes` NOT_INTEGRATED).

**Runs on the candidate tested SHA `614d006`:**

- integration-gate [41734504240](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734504240): 18 of 19 jobs succeed; `merge-eligibility` fails
- acceptance [41734499746](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734499746)
- offline-validation [41734507318](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734507318)
- aws-cdk [41734510352](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734510352)
- postgres-restore-evidence [41734513752](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734513752)
- portfolio-validation [41734516468](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734516468)
- Documentation [41734575819](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734575819)

**Runs on `main`:**

- integration-gate [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441)
- acceptance [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024)
- offline-validation [41703901993](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703901993)
- Documentation [41703901979](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703901979)

| Module | Evidence (labels above) | CI jobs (`modules.json` `ci_jobs`) | Run on tested SHA | Live targets |
|---|---|---|---|---|
| integration-infra | EXECUTED | integration-gate: user-actions, module-registry, final-summary | [41734504240](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734504240) | n/a |
| shared-evidence-validator | EXECUTED | offline-validation: validate | [41734507318](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734507318) | n/a |
| entra-offline | EXECUTED, STATIC | offline-validation: validate | [41734507318](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734507318) | NOT_EXECUTED (no tenant or Graph) |
| aws-cdk | EXECUTED, STATIC | aws-cdk: synth-and-test | [41734510352](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734510352) | NOT_EXECUTED (nothing deployed) |
| postgres-recovery | EXECUTED | postgres-restore-evidence: harness-selftest, restore-exercise-service, restore-exercise-offline | [41734513752](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734513752) | Lab containers only |
| orgs-security | STATIC | portfolio-validation: offline, orgs-static, terraform-static | [41734516468](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734516468) | NOT_EXECUTED |
| acceptance | EXECUTED | acceptance: gate-selftest, acceptance, defect-control. Ends at `REVIEW_PENDING`; never ACCEPTED | [41734499746](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734499746) | n/a |
| review-notes | STATIC (records; agent-authored notes do not satisfy AC1) | none | — | n/a |
| portfolio-cases, final-report, job-requirements-matrix, team-management, learning-guide, hybrid-operations | STATIC | portfolio-validation: offline | [41734516468](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734516468) | NOT_EXECUTED |
| vendor-mock, observability, control-mapping, patch-hardening, identity-governance | STATIC (no class declared; the committed runs under `evidence/vendor/` are SIMULATION-labelled) | portfolio-validation: offline | [41734516468](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734516468) | NOT_EXECUTED |
| m365-endpoint | EXECUTED, plus PLAN_ONLY (shown as NOT_EXECUTED for mutations) | integration-gate: m365-scenario-evaluation, m365-unit-tests, m365-evidence-verification | [41734504240](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734504240) | NOT_EXECUTED |
| backup-dr-aws | STATIC | portfolio-validation: offline, backup-static | [41734516468](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734516468) | NOT_EXECUTED |
| incident-demo | EXECUTED, **SIMULATION** | integration-gate: incident-committed-runs, incident-fresh-run, incident-not-executed-negative | [41734504240](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734504240) | SIMULATION only |
| aws-network-edge, endpoint-windows-automation, inventory-diagrams, owner-authentication | STATIC | portfolio-validation: network-edge, endpoint-pester, offline | [41734516468](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734516468) | NOT_EXECUTED. owner-authentication is a prototype; no key is enrolled |
| knowledge-base | STATIC | Documentation: validate | [41734575819](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734575819) | n/a |
| bank-aws-001 | SUPERSEDED by aws-cdk | — | — | — |

## 3. AC1–AC6 and where the evidence lives

Source: `coordination/tasks.json@8e2df97` `acceptance_conditions_for_main.conditions`. AC1–AC5 are `COMPUTED_AT_RUNTIME` by the trusted `merge-eligibility` gate; an in-tree MET is rejected. AC6 is `UNMET`.

| AC | Criterion (abridged from source) | Where the evidence lives | State now |
|---|---|---|---|
| AC1 | Independent review approves the EXACT candidate SHA. The reviewer is not the author, is on the trusted allow-list and has write permission | GitHub reviews API on the PR for that SHA; `.github/acceptance/trusted-config.json` reviewer allow-list | Unmet: 0 reviews on 46 PRs; no non-author collaborator (UA-7) |
| AC2 | Security exceptions recorded and approved by an owner | `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md`; `scripts/ci/check_exceptions.py`; owner ACCEPTANCE-ATTESTATION comment (not from the author or shared account) | Unmet: EX-01..EX-04 PROPOSED; 0 `ACCEPTANCE-*` comments (`GET /issues/comments`) |
| AC3 | All checks pass on that SHA | integration-gate run for the identity tuple; artifact `acceptance-decision-<tested_sha>`; mirror on `evidence/acceptance` | Unmet on `614d006`: `merge-eligibility` fails ([41734504240](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734504240)) |
| AC4 | Docs match the code (READMEs, PR bodies, INTEGRATION.md, tasks.json) | `reports/INTEGRATION.md`, `coordination/*.json`, Documentation run | Open (UA-2 unconfirmed) |
| AC5 | No unresolved blocking findings | `coordination/tasks.json` `autonomous_blockers`; review records in `reports/review-*.md` (on the candidate) | Open |
| AC6 | Final human portfolio acceptance by Ian, separate from merge eligibility | Owner decision on the frozen SHA | UNMET |

## 4. Open exceptions (`evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md@8e2df97`; unchanged on `0ad0468`)

| ID | Rule and scope | Status in repo |
|---|---|---|
| EX-01 | NIST S3DefaultEncryptionKMS: `AccessLogsBucket` uses SSE-S3 | PROPOSED |
| EX-02 | NIST S3BucketReplicationEnabled: `AccessLogsBucket` and `DataBucket` have no CRR | PROPOSED |
| EX-03 | AwsSolutions-IAM5: `log-group:RDSOSMetrics:log-stream:*` on `RdsMonitoringPolicy` | PROPOSED |
| EX-04 | AwsSolutions-IAM5: `snapshot:awsbackup-*` on `DbBackupPolicy`; runtime role trust unverified | PROPOSED |

`evidence/backup/aws-backup-dr/SECURITY_EXCEPTIONS.md` carries the same "PROPOSED, pending owner approval" status for its own entries.

The owner's conversation positions of 2026-10-28 are not approvals. For the reviewer to check:

- **EX-01:** the bucket policy.
- **EX-02:** that the limitation is stated explicitly.
- **EX-03:** the wildcard scope.
- **EX-04:** a new decision is needed; the old managed-policy scope is gone.

## 5. Known limitations

- **No independent review exists** (0 reviews). `main` carries code merged under the 2026-10-31 development-integration directive (PR #35 body).
- **The gate fails closed and has no trusted pin for current code.** `merge-eligibility` is red on `main` and on the candidate, and the pin proposal is UNREVIEWED.
- **No branch protection or rulesets** (`GET /rulesets` → `[]`), so the gate is advisory.
- **All evidence is offline or CI-only.** No AWS, Entra, Graph or M365 target was deployed or called (NOT_EXECUTED). Incident and vendor runs are SIMULATION.
- **Shared-account authorship.** Every PR, comment and candidate commit is from `onnxscibroccoli`, which proves the login, not the person (`tasks.json@8e2df97` UA-6).
- **Owner signing is a prototype only.** No key is enrolled (`modules.json` owner-authentication `limitations`).
- **Controls are "mapped to" frameworks only.** No certification or compliance is claimed.
- **The 18:13 ET sequencing directive is relayed through chat** and is not yet recorded in the repo (decision packet, "Sequencing correction").

## 6. Reviewer sign-off template (status: NOT SIGNED)

Copy this into a GitHub review on the PR for the exact SHA. Do not fill it in here.

```text
PHASE-C-REVIEW
Status: NOT SIGNED
Reviewer GitHub login: ______________________
Reviewer is not the PR author and not onnxscibroccoli: [ ] yes
Repository permission (write/maintain/admin): ______________________
Candidate SHA reviewed (40 hex): ________________________________________
Base main SHA (40 hex): ________________________________________
Tested merge SHA (40 hex): ________________________________________
Actions run URL(s) for that SHA: ______________________
Gate pin reviewed (gate_sha): ______________________  verdict: [ ] APPROVE [ ] CHANGES REQUIRED
Modules reviewed: ______________________
Exceptions EX-01..EX-04 reviewed (technical opinion only; owner decides): ______________________
Findings (blocking / non-blocking): ______________________
Verdict: [ ] APPROVE  [ ] CHANGES REQUIRED  [ ] COMMENT
Date and time (with zone): ______________________
```

Only a GitHub review submitted by that account on that SHA counts toward AC1 (`tasks.json@8e2df97` AC1 `binding`). Text in this file never does.
