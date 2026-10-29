# bank-it-operations-lab

A reproducible IT-operations reference lab. It is built to show, with evidence, the work described in a bank **IT Manager** posting: "Information Technology Manager", AMS Technology Solutions LLC, Boston, hybrid ([JobLeads](https://www.jobleads.com/us/job/information-technology-manager--boston--e57b1e5ed0b5b152dff0ddd60c8e955b2)). The posting text is not stored in this repo. The requirement IDs (A1–D4) come from the [job requirements matrix](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/9fb49fa96903bf5b0de58dad7c5741c30d6a7d3d/docs/JOB_REQUIREMENTS_MATRIX.md).

> **Status at 2026-10-28, about 21:54 EDT: work in progress, nothing merged into `main` (`7f50348`), nothing deployed.**
> - All work is in **open draft PRs**. `main` holds only this README's earlier two-line version.
> - The integration candidate is [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) @ `e9310f3`. **Integrated: 7/25 active modules** (26 registered, 1 superseded; `coordination/modules.json`). Status classes (one per module): integrated 7, verified 7, independently accepted 0, blocked 8, not-started 3; see [`reports/MODULE_REQUIREMENT_MAP.md`](reports/MODULE_REQUIREMENT_MAP.md) §1. Its CI gate runs green on every technical job, and its own merge-eligibility check says **NOT ELIGIBLE**: there is no allow-listed independent review, and the owner has not posted a decision on EX-01..EX-04, AC4 or AC5. That is the gate working, not a failure being hidden.
> - No AWS, Entra ID, Microsoft 365 or Graph credentials were ever used.
> - This is a **personal lab**. It is not evidence of employment, team leadership, banking tenure, or certification. Much of it was produced with AI coding agents under the owner's direction.

## Start here (hiring manager, about 15 minutes)

| If you have | Read |
|---|---|
| 2 minutes | The **evidence labels** below and the **module map** |
| 15 minutes | [`docs/DEMO_WALKTHROUGH_15MIN.md`](docs/DEMO_WALKTHROUGH_15MIN.md): timed walkthrough with links and runnable commands |
| Specific requirements in mind | [Job requirements matrix](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/9fb49fa96903bf5b0de58dad7c5741c30d6a7d3d/docs/JOB_REQUIREMENTS_MATRIX.md) (rows A1–D4; section G covers the newer modules) |
| Sources and acceptance criteria per module | [`reports/MODULE_REQUIREMENT_MAP.md`](reports/MODULE_REQUIREMENT_MAP.md) (job row, authoritative source, falsifiable check, evidence, review status) |
| A status audit | [`reports/FINAL_REPORT.md`](reports/FINAL_REPORT.md), [`reports/USER_ACTIONS_REQUIRED.md`](reports/USER_ACTIONS_REQUIRED.md), [`reports/EVIDENCE_MANIFEST.md`](reports/EVIDENCE_MANIFEST.md) |

## Evidence labels

Every artifact below carries exactly one label.

- **EXECUTED**: it ran. A GitHub Actions run URL or an evidence hash (`SHA256SUMS`) is cited. Offline runs on synthetic data are EXECUTED *for the tool*, never for a live system.
- **SIMULATION**: it ran against a simulated or fictional system. Useful for showing method, not operational evidence.
- **NOT_EXECUTED**: reference material only: runbooks, designs, IaC that was never deployed, documentation.

"Re-run" means the reports agent re-ran the tests or verifier against the cited head on 2026-10-28 at about 20:20 EDT.

## Module map

| Area | PR @ head | Label | Evidence | Job rows |
|---|---|---|---|---|
| Integration gate (combines #3, #5, #4, #2, #20, #22; 7 of 25 active modules) | [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) candidate `e9310f3` | **EXECUTED (CI)** | integration-gate [run 40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048): 18/19 jobs success; merge-eligibility **NOT ELIGIBLE** by design. aws-cdk [40802567002](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567002), postgres [40802567000](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567000), offline-validation [40802567034](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567034): success. `validate-all.sh --python-only` re-run at `e9310f3`: PASS (33 steps) | B4, B7, B9 |
| PostgreSQL backup/restore harness v2 | [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) @ `e7399fb` | **EXECUTED (CI)**, real PostgreSQL servers | [run 40741329107](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107): service 36/36, offline 38/38, version-mismatch control rejected. `verify_evidence.py` re-run on `ci-service-40741329107-1`: VERIFIED, problems=0 | B15a, B5, C8, B13 |
| AWS CDK: private VPC, Multi-AZ RDS, KMS, AWS Backup, cdk-nag (AwsSolutions + NIST 800-53 R5) | [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) @ `099479e` | **EXECUTED (CI)** for synth, Jest and cdk-nag. Deployment **NOT_EXECUTED** | aws-cdk [run 40802567002](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567002). Jest 36/36. Exceptions EX-01..EX-04: owner decisions relayed (EX-02 accepted; EX-01, EX-03 and EX-04 conditional), register still PROPOSED (see FINAL_REPORT §3). Finding B5-2 (KMS escalation path) fixed in #7 @ `80f01d6` | A3, B3, C3, C9 |
| Entra ID Conditional Access validator (synthetic policies) | [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) @ `d302c99` | **EXECUTED** (offline). Tenant **NOT_EXECUTED** | Evidence bundle (46 hashes) re-checked OK; CI offline-validation [40802567034](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567034) | C6, C9 |
| Shared evidence validator | [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) @ `fb36341` | **EXECUTED (CI)** | offline-validation run above | B9, C10 |
| M365 / endpoint operations scenarios (PLAN_ONLY) | [#20](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/20) @ `1b3c240` | **EXECUTED** (offline, synthetic tenant; 0 mutations) | 29 tests re-run OK; CI m365 jobs in run 40802567048 | C6, B2 |
| Incident demo: DB crash → detect → diagnose → restore → timeline | [#22](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/22) @ `9f21329` | **SIMULATION** | `timeline.py --verify` re-run: PASS; 38 hashes OK; fresh CI run in 40802567048 | B13, B15b |
| Acceptance vertical slice | [#26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26) @ `eb42b23` | **EXECUTED (CI)** | [run 40776065038](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776065038): `OVERALL=PASS required=44`, decision `REVIEW_PENDING` | B9 |
| Acceptance contract, runner, adapters | [#23](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/23), [#24](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/24), [#25](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/25) | **EXECUTED (CI)**, not re-run here | offline-validation [40747710616](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40747710616), [40747893103](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40747893103), [40748526680](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748526680) | B9 |
| Observability collector and synthetic probes | [#10](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/10) @ `3e40e39` | **EXECUTED** (local, offline; no CI) | 64 tests re-run OK; bundle 44 hashes OK | B5 |
| Patch rings and systemd hardening | [#17](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/17) @ `5605b78` | **EXECUTED** inspectors (offline; no CI). Patching **NOT_EXECUTED** | 27 tests re-run OK; bundle 102 hashes OK | B12, C8 |
| Identity governance (Graph fixtures, privileged roles, PIM refs) | [#18](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/18) @ `f48e7e3` | **EXECUTED** (offline; no CI). PIM/federation **NOT_EXECUTED** | 65 tests re-run OK; bundle 49 hashes OK | C6, C9 |
| FFIEC AIO control mapping | [#16](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/16) @ `3f82697` | **EXECUTED** validator; the mapping is a study reference, not an attestation | 10 tests re-run OK | C9, B9 |
| Banking-vendor API mock, vendor risk, RACI | [#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) @ `d6efb82` | **SIMULATION** (fictional vendor) | 70 tests re-run OK; 3 bundles OK | B6 |
| AWS Backup DR reference and cost model | [#21](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/21) @ `10da54f` | **NOT_EXECUTED** (all 7 recovery items). Cost model EXECUTED offline | `RECOVERY_EXECUTION_STATUS.json`; cost tests 8 OK | B15b, B12 |
| Windows Server, AD DS, DNS, GPO, hybrid identity runbooks | [#19](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/19) @ `3397dac` | **NOT_EXECUTED** | `operations/hybrid/EXECUTION_STATUS.md`; runbook lint 0 findings | A2, B2, B11 |
| AWS Organizations, SCPs, org trail, GuardDuty, Security Hub | [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) @ `e5e7f46` | **NOT_EXECUTED** reference; local static evidence only; blocked (B6-1, B6-2) | not integrated | A4, C4 |
| Team model, on-call, escalation, management templates | [#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13) @ `9dc8f1f` | **NOT_EXECUTED** (documentation, synthetic team) | n/a | B11, B14 |
| Learning guide and ADRs | [#15](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/15) @ `39728db` | **NOT_EXECUTED** (documentation) | n/a | C10 |
| Case studies from other personal repos | [#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8) @ `7010d05` | **NOT_EXECUTED** here (links to other repos' records) | `portfolio/JOB_ALIGNMENT.md` | A1, B13 |
| Review notes | [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14), [#27](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27)–[#31](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/31) | review documents (AI reviewers, same GitHub account as the author; not approvals). #31 @ `1fdf25a`: CHANGES REQUIRED | n/a | — |

PR [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) is superseded by #5.

## What the lab does not show

Requirements no lab can demonstrate: years of experience, the on-prem → cloud career path, leading 8–10 staff, vendor relationships (including Jack Henry), banking-industry tenure, degree, certifications, availability and physical conditions (matrix rows A2, A5, A6, B1, B6, B14, B16, C2, C11, C12, D1–D4).

Never executed anywhere in the lab: AWS deployment, any Entra/M365/Graph tenant call, AWS backup or DR jobs, Windows/AD environments, a live vendor, a live incident.

## Run it yourself (no credentials needed)

```bash
git clone https://github.com/onnxscibroccoli/bank-it-operations-lab.git
cd bank-it-operations-lab
git checkout e9310f3a94162a5dae31ee1cca9e35452de033ed   # PR #7 integration candidate
scripts/validate-all.sh --python-only                    # stdlib Python checks; re-run PASS (33 steps, ~4 s) at e9310f3
```

Step-by-step commands are in [`docs/DEMO_WALKTHROUGH_15MIN.md`](docs/DEMO_WALKTHROUGH_15MIN.md).
