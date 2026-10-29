# Module → requirement map (source-backed)

- **Snapshot:** 2026-10-28, about 21:54 EDT. Deadline: midnight ET (00:00 EDT 2026-10-29).
- **Live candidate:** PR #7 head [`e9310f3`](https://github.com/onnxscibroccoli/bank-it-operations-lab/tree/e9310f3a94162a5dae31ee1cca9e35452de033ed) (`e9310f3a94162a5dae31ee1cca9e35452de033ed`), pushed 21:47 EDT (it replaced `1fdf25a`, pushed 21:25 EDT, during this update). Base and current `main`: `7f50348bf1370381615eaed91c02607fe41de2f5` (unchanged; the gate confirmed `main_sha_at_runtime` = base). The earlier final candidate `7fe6d72` and the interim heads `b908a66` and `1fdf25a` are **superseded**. Module PRs not in #7 are cited at their current heads.
- **Denominator:** `coordination/modules.json` @ `e9310f3` registers **26 modules**. One is SUPERSEDED (`bank-aws-001`, #1, replaced by #5), so there are **25 active modules**. CI prints, in run [40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048): `MODULE COVERAGE: 7/25 integrated (28.0%), functional 7/17; denominator 26 (BLOCKED=1, INTEGRATED=7, NOT_INTEGRATED=14, NOT_STARTED=3, SUPERSEDED=1)`. This replaces this report's earlier figure of 22. That figure left out the 3 NOT_STARTED modules (`aws-network-edge`, `endpoint-windows-automation`, `inventory-diagrams`); the registry also counts the 4 acceptance PRs as one module.
- **Wording rule:** every module is **mapped to** a source section. Nothing here claims certification, compliance, or examination readiness. The lab is offline and synthetic: nothing is deployed, and no AWS, Entra, M365 or Graph credentials were ever used.
- **Job requirement IDs** (A1–D4) come from the job requirements matrix ([#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12) @ `31b69db`, plus addendum G on `docs/job-matrix-addendum` @ [`9fb49fa`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/9fb49fa96903bf5b0de58dad7c5741c30d6a7d3d/docs/JOB_REQUIREMENTS_MATRIX.md)).
- **Labels:** EXECUTED (a CI run URL or evidence hash is cited; offline runs on synthetic data are EXECUTED for the tool, never for a live system), SIMULATION (simulated or fictional system), NOT_EXECUTED (reference only).
- **"Re-run"** = re-executed by the reports agent. For the 7 integrated modules this was at `e9310f3` at about 21:52 EDT. For the others it was at their PR heads between 20:20 and 21:10 EDT.

## 0. Live candidate state (`e9310f3`)

| Item | Value | Source |
|---|---|---|
| Integration gate, pull_request (tested merge `9ff24a4`) | 18/19 jobs success; `merge-eligibility` **NOT ELIGIBLE** | [40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048) |
| Integration gate, push | 18/19 success; merge-eligibility failure | [40802561953](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802561953) |
| main-validation (`candidate/main-validation-e9310f3` = merge `92f52fc`) | 18/19 success; NOT ELIGIBLE | [40802573622](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802573622) |
| aws-cdk | success (Jest **36/36**, 3 suites) | [40802567002](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567002) (PR), [40802561755](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802561755) (push) |
| postgres-restore-evidence | success | [40802567000](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567000) |
| offline-validation | success | [40802567034](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567034) (PR), [40802561784](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802561784) (push) |
| Gate code | `ce69f84`, checked out by SHA from the manifest on `evidence/acceptance` @ `1901342`. `main` lacks the gate, so it is not used. Trusted config: `owner_logins: [onnxscibroccoli]`, **`reviewer_allowlist: []`** | run 40802567048 log; `.github/acceptance/trusted-config.json` |
| AC1 | **UNMET**: "trusted reviewer_allowlist is empty; no APPROVED review on exact candidate … by an allow-listed, write-permitted account other than the PR author" | gate log |
| AC2 | **UNMET**: "BLOCKING USER ACTION UA-1: no owner decision on candidate … for applied exceptions EX-01 EX-02 EX-03 EX-04". `check_exceptions.py` (offline-validation) still reports all 5 suppressions tied to PROPOSED entries | gate log |
| AC3 | **MET_AT_RUNTIME** for run 40802567048 (candidate `e9310f3` merged into `7f50348` as `9ff24a4`) | gate log |
| AC4 | **UNMET**: "no authorized AC4 decision on candidate …" | gate log |
| AC5 | **UNMET**: "no authorized AC5 decision on candidate …" (B5-2 recorded fixed in `80f01d6`) | gate log, `tasks.json` |
| AC6 | UNMET, not yet actionable | `tasks.json` |
| Local re-run at `e9310f3` | `validate-all.sh --python-only` **PASS (33 steps)**; `scripts/ci/tests` **114 OK**; `check_modules.py` OK (26 modules, 807 files claimed); `check_exceptions.py` reports 5 suppressions on PROPOSED exceptions | `/tmp/v/logs/va_e9310f3.log` (box) |
| Latest review | [#31](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/31) @ `eccac83` reviewed the **previous** head `1fdf25a`: CHANGES REQUIRED. It found F4 (any account could approve), F6 (self-referential `met_for`), R6 (candidate-controlled gate) and F7 (approval was a text edit). The new head claims repairs in `ce69f84` ("gate v3") and `e9310f3`: - an AC1 reviewer allow-list with write permission; - AC2/AC4/AC5 decided from authenticated owner decision comments bound to the exact SHA; - the gate code checked out by SHA from a manifest on `evidence/acceptance` and hash-verified.  **`e9310f3` has not been reviewed.** This report re-ran its 114 CI self-tests (OK), but did not audit the repair logic. Every review note is from the author account, so none is AC1 | PR #31 body; commit messages |

## 1. Counts (denominator: 25 active modules)

| Measure | Count | Definition and basis |
|---|---|---|
| **Planned (active)** | **25** (26 registered − 1 SUPERSEDED). By registry category: 17 functional; the other 8 are documentation, review records and the blocked/not-started entries (registry `functional 7/17`) | `coordination/modules.json` @ `e9310f3`, printed by CI |
| **Integrated** | **7** (28.0%) | Registry status INTEGRATED and present in `e9310f3`: `integration-infra` (#7), `shared-evidence-validator` (#3), `entra-offline` (#4), `aws-cdk` (#5), `postgres-recovery` (#2), `m365-endpoint` (#20 @ `1b3c240`), `incident-demo` (#22 @ `9f21329`) |
| **Verified** | **14** of 25: the 7 integrated (CI at `e9310f3` plus local re-run at `e9310f3`), plus 7 not integrated (re-run at their heads): `acceptance` #23–#26, `vendor-mock` #9, `observability` #10, `control-mapping` #16, `patch-hardening` #17, `identity-governance` #18, `hybrid-operations` #19 (linter). **Partial:** `backup-dr-aws` #21. **Unverified:** `orgs-security` #6 (BLOCKED). **No executable check:** 6 documentation/review modules. **Nothing to verify:** 3 NOT_STARTED | Re-run here or CI green at the exact SHA |
| **Independently accepted** | **0** | AC1 definition: a non-author APPROVED GitHub review on the exact SHA, from the reviews API. No such review exists on any PR. Every review record (#14, #27–#31) is written from the PR-author account `onnxscibroccoli` |

### Status class per module (exactly one each; 25 active)

Rule: each active module gets exactly one class, the highest that applies.
1. **independently accepted:** a non-author, allow-listed APPROVED review on the exact SHA. None yet.
2. **integrated:** in #7 @ `e9310f3`, with registry status INTEGRATED.
3. **verified:** not integrated, but its checks were re-run green at its head.
4. **blocked:** open or recorded blocker, or not verifiable as built. This covers the registry's BLOCKED module, partial verification, and documentation or review modules with no executable check. For those, the missing check and review is the blocker.
5. **not-started:** registry NOT_STARTED.

The 7 integrated modules were also re-verified at `e9310f3`. "Verified" in this table means verified **but not integrated**, so the earlier non-exclusive figure "verified 14" equals integrated 7 + verified 7.

**integrated 7 · verified 7 · independently accepted 0 · blocked 8 · not-started 3 = 25**

| # | Registry module | PR | Status class | Basis |
|---|---|---|---|---|
| 1 | `integration-infra` | #7 | **integrated** | in `e9310f3`; CI 18/19 (merge-eligibility NOT ELIGIBLE by design) |
| 2 | `shared-evidence-validator` | #3 | **integrated** | 16 tests re-run at `e9310f3` |
| 3 | `entra-offline` | #4 | **integrated** | 25 tests and validator PASS at `e9310f3` |
| 4 | `aws-cdk` | #5 | **integrated** | CI Jest 36/36; EX-01..EX-04 undecided (UA-1) |
| 5 | `postgres-recovery` | #2 | **integrated** | evidence VERIFIED at `e9310f3` |
| 6 | `m365-endpoint` | #20 | **integrated** | 13/13 scenarios, 29 tests at `e9310f3` |
| 7 | `incident-demo` | #22 | **integrated** | timeline VERIFY PASS (SIMULATION) |
| 8 | `acceptance` | #23–#26 | **verified** | 32 tests and CI at `eb42b23`; #27 CHANGES REQUIRED |
| 9 | `vendor-mock` | #9 | **verified** | 70 tests at `d6efb82` (SIMULATION) |
| 10 | `observability` | #10 | **verified** | 64 tests at `3e40e39` |
| 11 | `control-mapping` | #16 | **verified** | 10 tests at `3f82697` |
| 12 | `patch-hardening` | #17 | **verified** | 27 tests at `5605b78` |
| 13 | `identity-governance` | #18 | **verified** | 65 tests at `f48e7e3` |
| 14 | `hybrid-operations` | #19 | **verified** | runbook linter, 0 findings at `3397dac` (runbooks NOT_EXECUTED) |
| 15 | `orgs-security` | #6 | **blocked** | registry BLOCKED: B6-1, B6-2 open; not re-run |
| 16 | `backup-dr-aws` | #21 | **blocked** | only partly verified (cost tests 8 OK; CDK Jest not run); recovery needs AWS (B1) |
| 17 | `review-notes` | #14, #27–#31 | **blocked** | no executable check; review records only (not acceptance) |
| 18 | `portfolio-cases` | #8 | **blocked** | no executable check; no review |
| 19 | `final-report` | #11 | **blocked** | no executable check; no review (this report) |
| 20 | `job-requirements-matrix` | #12 | **blocked** | no executable check; no review |
| 21 | `team-management` | #13 | **blocked** | no executable check; no review |
| 22 | `learning-guide` | #15 | **blocked** | no executable check; no review |
| 23 | `aws-network-edge` | — | **not-started** | registry NOT_STARTED |
| 24 | `endpoint-windows-automation` | — | **not-started** | registry NOT_STARTED |
| 25 | `inventory-diagrams` | — | **not-started** | registry NOT_STARTED |

## 2. Sources (each fetched and checked about 21:00–21:10 EDT)

Source classes used in this map:
- **supervisory:** US banking-agency guidance to banks, here FFIEC and OCC (the OCC bulletin is interagency OCC/FRB/FDIC guidance). It is guidance, not regulation.
- **industry:** public standards. NIST is a US federal standard and is not binding on banks.
- **product:** vendor documentation (AWS, Microsoft, PostgreSQL, systemd, GitHub, cdk-nag).
- **project-specific (repo-defined):** criteria this repo defines for itself, such as `tasks.json` AC1–AC6, `modules.json`, the exception register and the job matrix. They are not external requirements.
- **regulatory:** statute or regulation text. **None is used.**

**No regulatory source is used.** No statute or regulation text (for example GLBA or 12 CFR) was fetched or mapped.

| Key | Source and section | Class | URL | How verified |
|---|---|---|---|---|
| FFIEC-AIO | FFIEC IT Examination Handbook, *Architecture, Infrastructure, and Operations* (June 2021). Sections used: II.B.1(c), III.C.1, III.D.1, III.E, III.F, VI.A.3, VI.B.3(b), VI.B.4, VI.B.6, VI.B.7, VI.C.4, VI.D.1, VII.A.4 | supervisory | <https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/> | Page and booklet table of contents read (all listed sections present). curl gets HTTP 403 (bot block); read with the fetch tool |
| FFIEC-AIO-VIB4 | same booklet, **VI.B.4 Backup and Replication Processes** ("Processes to regularly test backup copies for readability"; "Capability to restore operations to a previous trusted state") | supervisory | <https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/vi-operations/vib-it-operational-processes/vib4-backup-and-replication-processes/> | Section text read; quoted phrases present |
| FFIEC-AIO-VIA3 | same booklet, **VI.A.3 Identity and Access Management** ("enhanced authentication, especially for privileged access") | supervisory | <https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/vi-operations/via-operational-controls/via3-identity-and-access-management/> | Section text read |
| FFIEC-BCM | FFIEC IT Handbook, *Business Continuity Management*. Sections: IV.A.3 Data Backup and Replication, IV.A.5 Third-Party Service Providers, V.F.1 Incident Response, V.F.2 Disaster Recovery, VII.G.3 Tabletop Exercise, VII.G.4 Tests | supervisory | <https://ithandbook.ffiec.gov/it-booklets/business-continuity-management/> | Booklet table of contents read |
| TPRM | *Interagency Guidance on Third-Party Relationships: Risk Management* (OCC Bulletin 2023-17, June 6, 2023; OCC, FRB, FDIC): third-party risk-management life cycle | supervisory | <https://www.occ.gov/news-issuances/bulletins/2023/bulletin-2023-17.html> | Page read. (The Federal Register copy redirected to a bot-check page from this box) |
| NIST-53 | NIST SP 800-53 Rev. 5. Controls used: AC-2, AC-2(3), AC-6, AU-9, CA-2, CA-7, CM-3, CM-6, CP-9, CP-9(1), CP-10, IA-2(1), IR-4, SA-9, SC-28, SI-2, SI-4 | industry | <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final> | Page HTTP 200; every control ID and title checked in NIST's OSCAL catalog (release 5.2.0, `usnistgov/oscal-content`) |
| NIST-61 | NIST SP 800-61 Rev. 3, *Incident Response Recommendations* | industry | <https://csrc.nist.gov/pubs/sp/800/61/r3/final> | HTTP 200, title present |
| NIST-34 | NIST SP 800-34 Rev. 1, *Contingency Planning Guide* | industry | <https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final> | HTTP 200, title present |
| NIST-40 | NIST SP 800-40 Rev. 4, *Enterprise Patch Management Planning* | industry | <https://csrc.nist.gov/pubs/sp/800/40/r4/final> | HTTP 200, title present |
| NIST-137 | NIST SP 800-137, *Information Security Continuous Monitoring* | industry | <https://csrc.nist.gov/pubs/sp/800/137/final> | HTTP 200, title present |
| AWS-WA | AWS Well-Architected: SEC03-BP02 *Grant least privilege access*; SEC08-BP02 *Enforce encryption at rest*; REL09-BP02 *Secure and encrypt backups*; REL09-BP04 *Perform periodic recovery of the data to verify backup integrity and processes*; Cost pillar *Expenditure and usage awareness* | product | <https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sec_permissions_least_privileges.html>, <https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/protecting-data-at-rest.html>, <https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/back-up-data.html>, <https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_backing_up_data_periodic_recovery_testing_data.html>, <https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/expenditure-and-usage-awareness.html> | HTTP 200; BP IDs and titles present |
| AWS-DOCS | AWS docs: S3 server access logging ("The destination bucket must use Amazon S3 managed keys (SSE-S3)", re-read 21:42 EDT for EX-01); AWS Backup IAM service roles (`AWSBackupServiceRolePolicyForBackup`, re-read 21:42 EDT for EX-04, <https://docs.aws.amazon.com/aws-backup/latest/devguide/iam-service-roles.html>); RDS Multi-AZ; RDS Enhanced Monitoring; KMS key policies; VPC flow logs; Organizations SCPs; AWS Backup Vault Lock, cross-Region copy, restore testing, encryption; Systems Manager Patch Manager; IAM Identity Center with Microsoft Entra ID | product | <https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html>, <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html>, <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html>, <https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html>, <https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html>, <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html>, <https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html>, <https://docs.aws.amazon.com/aws-backup/latest/devguide/cross-region-backup.html>, <https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html>, <https://docs.aws.amazon.com/aws-backup/latest/devguide/encryption.html>, <https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html>, <https://docs.aws.amazon.com/singlesignon/latest/userguide/idp-microsoft-entra.html> | each HTTP 200 with the topic string present |
| MS-DOCS | Microsoft Learn: Conditional Access overview; Block legacy authentication; Emergency access (break-glass) accounts; Privileged Identity Management; Access reviews; Intune device compliance; Microsoft 365 service health; AD DS overview; Group Policy overview; What is hybrid identity | product | <https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview>, <https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-block-legacy-authentication>, <https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access>, <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure>, <https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview>, <https://learn.microsoft.com/en-us/intune/device-security/compliance/overview>, <https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health>, <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview>, <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview>, <https://learn.microsoft.com/en-us/entra/identity/hybrid/whatis-hybrid-identity> | each HTTP 200 with the topic string present. The Intune URL redirected from `/intune/intune-service/protect/device-compliance-get-started` |
| PG | PostgreSQL 16 docs: 25.1 *SQL Dump*; `pg_dump`; `pg_restore` | product | <https://www.postgresql.org/docs/16/backup-dump.html>, <https://www.postgresql.org/docs/16/app-pgdump.html>, <https://www.postgresql.org/docs/16/app-pgrestore.html> | HTTP 200, titles present |
| SYSTEMD | `systemd.exec(5)`: sandboxing options such as `ProtectSystem=` | product | <https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html> | HTTP 200, `ProtectSystem` present |
| GH | GitHub Docs: Actions secure use ("full-length commit SHA" pinning); About protected branches (required status checks) | product | <https://docs.github.com/en/actions/reference/security/secure-use>, <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches> | HTTP 200, phrases present |
| CDK-NAG | cdk-nag rule packs (AwsSolutions, NIST 800-53 R5) | product | <https://github.com/cdklabs/cdk-nag> | HTTP 200 |
| PROJ | Repo-defined criteria: AC1–AC6 (`coordination/tasks.json` @ `e9310f3`), the module registry (`coordination/modules.json` @ `e9310f3`), the exception register (`evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` @ `e9310f3`), the #27 completion plan, and review notes #14 and #27–#31 | **project-specific (repo-defined)** | <https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27> | Read from the repo |
| JOB | The IT Manager posting (JobLeads), via the job matrix | project-specific (an external job posting used as the repo's target; not a control source) | <https://www.jobleads.com/us/job/information-technology-manager--boston--e57b1e5ed0b5b152dff0ddd60c8e955b2> | Re-read about 20:20 EDT; live |

**Dropped as unverifiable from this box:** CIS Controls v8.1. The page loads (HTTP 200), but the safeguard names are rendered client-side and could not be confirmed, so no CIS section is cited. NIST CSF 2.0 subcategory IDs were not checked, so CSF is not cited.

### 2a. Source class per module

| Registry module | Supervisory (FFIEC / OCC) | Industry (NIST) / product | Project-specific (repo-defined) |
|---|---|---|---|
| integration-infra (#7) | none | GH (product); NIST-53 CM-3 | AC1–AC6, modules.json |
| shared-evidence-validator (#3) | FFIEC-AIO VI.B.7 | NIST-53 AU-9 | evidence manifest format |
| entra-offline (#4) | FFIEC-AIO VI.A.3 | MS-DOCS; NIST-53 IA-2(1) | baseline.json choices (UA-2) |
| aws-cdk (#5) | none | AWS-WA, AWS-DOCS, CDK-NAG (product); NIST-53 AC-6, SC-28 | EX-01..EX-04 register |
| postgres-recovery (#2) | FFIEC-AIO VI.B.4 | NIST-53 CP-9(1), CP-10; AWS-WA REL09-BP04; PG | harness v2 contract |
| m365-endpoint (#20) | none | MS-DOCS; NIST-53 AC-2(3) | PLAN_ONLY contract |
| incident-demo (#22) | FFIEC-AIO VI.C.4; FFIEC-BCM V.F.1, VII.G.3 | NIST-61 | required gate outputs |
| orgs-security (#6) | none | AWS-DOCS SCPs; NIST-53 AC-6 | none |
| acceptance (#23–#26) | none | NIST-53 CA-2 | acceptance contract (all criteria repo-defined) |
| vendor-mock (#9) | TPRM (OCC 2023-17); FFIEC-AIO III.E | NIST-53 SA-9 | RACI, vendor register |
| observability (#10) | FFIEC-AIO VI.D.1 | NIST-53 SI-4, CA-7; NIST-137 | probe bounds |
| control-mapping (#16) | FFIEC-AIO (whole booklet) | none | mapping schema |
| patch-hardening (#17) | FFIEC-AIO VI.B.3(b) | NIST-40; NIST-53 SI-2, CM-6; AWS Patch Manager; SYSTEMD | ring definitions |
| identity-governance (#18) | FFIEC-AIO VI.A.3 | MS-DOCS PIM / access reviews; AWS IAM Identity Center; NIST-53 AC-2, AC-6 | fixtures |
| hybrid-operations (#19) | none | MS-DOCS AD DS, GPO, hybrid identity | runbook status rule |
| backup-dr-aws (#21) | FFIEC-BCM IV.A.3, V.F.2 | NIST-53 CP-9, CP-10; NIST-34; AWS-WA; AWS-DOCS Backup | cost model |
| team-management (#13) | FFIEC-AIO II.B.1(c) | none | team model |
| review-notes, portfolio-cases, final-report, job-requirements-matrix, learning-guide | none | none | all project-specific |
| aws-network-edge, endpoint-windows-automation, inventory-diagrams (NOT_STARTED) | **not mapped** (no implementation) | not mapped | registry entry only |

## 3. Per-module map

Field order: job rows · sources (class) · falsifiable acceptance requirement · implementation paths · check command · evidence (path, SHA, run) · label · limitations · independent-review disposition.

### Integrated in the live candidate `e9310f3` (registry INTEGRATED)

**M1. `integration-infra`: integration gate (#7)**
- Job rows: B4, B7, B9.
- Mapped to: GH secure use (product): pin actions to a full-length commit SHA. GH protected branches (product). NIST-53 CM-3 *Configuration Change Control* (industry). PROJ AC1–AC5 (project-specific).
- Acceptance (falsifiable): `merge-eligibility` must exit non-zero unless AC1–AC5 are MET for the exact tested SHA. Any required job that is missing, skipped, cancelled, failed or NOT_EXECUTED must make `final-summary` fail. Every third-party `uses:` must be a 40-hex SHA. AC1 must come from the GitHub reviews API: an APPROVED review on the exact SHA by an allow-listed account with write permission that is not the author. AC2, AC4 and AC5 must come from an owner decision comment bound to the exact SHA. In-tree `MET` is rejected.
- Paths: `.github/workflows/`, `scripts/ci/`, `scripts/validate-all.sh`, `coordination/`.
- Check: `python3 -m unittest discover -s scripts/ci/tests` (re-run at `e9310f3`: 114 tests OK) and `scripts/validate-all.sh --python-only` (re-run at `e9310f3`: PASS, 33 steps).
- Evidence: integration-gate [40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048) (PR), [40802561953](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802561953) (push) and main-validation [40802573622](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802573622) @ `e9310f3`: 18/19 success each; `merge-eligibility` NOT ELIGIBLE (AC1 UNMET, AC2 UNMET, AC3 MET_AT_RUNTIME, AC4 UNMET, AC5 UNMET).
- Label: **EXECUTED (CI)**.
- Limitations: advisory only, because `main` has no branch protection (404 unset).
- Review: **changes required**: [#30](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/30) @ `b908a66` and [#31](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/31) @ `1fdf25a`, from the same account, so not AC1. #31 found F4, F6, R6 and F7 at `1fdf25a`; `e9310f3` claims repairs that have not been reviewed (§0). No non-author review exists, and the reviewer allow-list is empty.

**M2. `shared-evidence-validator` (#3)**
- Job rows: B9, C10.
- Mapped to: NIST-53 AU-9 *Protection of Audit Information* (industry). FFIEC-AIO VI.B.7 *Log Management* (supervisory).
- Acceptance: any changed, missing or extra file in an evidence bundle, or a malformed manifest, must make the validator exit non-zero.
- Paths: `evidence/shared/`.
- Check: `python3 -m unittest discover -s evidence/shared/tests` (re-run at `e9310f3`: 16 OK).
- Evidence: offline-validation [40802567034](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567034) @ `e9310f3`.
- Label: **EXECUTED (CI)**.
- Limitations: integrity check only. It does not prove a log's content is true.
- Review: **approve** (PR #14 agent notes @ `fb36341`; same GitHub account, so not AC1).

**M3. `entra-offline`: Entra Conditional Access, offline (#4)**
- Job rows: C6, C9.
- Mapped to: MS-DOCS Conditional Access, Block legacy authentication, Emergency access (product). NIST-53 IA-2(1) *Multi-factor Authentication to Privileged Accounts* (industry). FFIEC-AIO-VIA3 (supervisory).
- Acceptance: `ca_validator.py` exits 0 on the baseline policies. Each negative fixture must fail. Report-only or disabled policies never satisfy a requirement. Malformed input exits 2.
- Paths: `identity/entra/`, `tests/entra/`, `evidence/entra/`.
- Check: `python3 identity/entra/ca_validator.py --quiet` (re-run: `overall=PASS exit=0`); `python3 -m unittest discover -s tests/entra` (re-run at `e9310f3`: 25 OK).
- Evidence: `evidence/entra/runs/local-offline-20261028T150359Z/` @ `d302c99` (46 hashes re-checked OK); CI 40802567034 @ `e9310f3`. `evidence/entra/BASELINE-CHOICES-PENDING.md` (new at `b908a66`) records the baseline as PENDING.
- Label: **EXECUTED** (offline, synthetic). Tenant: **NOT_EXECUTED**.
- Limitations: no tenant or Graph call. Baseline choices are unconfirmed (UA-2).
- Review: **approve with comments** (PR #14 agent notes @ `d302c99`; not AC1).

**M4. `aws-cdk`: private VPC, RDS, secure storage (#5)**
- Job rows: A3, B3, C3, C9.
- Mapped to: AWS-WA SEC03-BP02 and SEC08-BP02 (product). AWS-DOCS S3 server access logging, RDS Multi-AZ, RDS Enhanced Monitoring, KMS key policies, VPC flow logs (product). NIST-53 AC-6 and SC-28 (industry). CDK-NAG (product).
- Acceptance: both cdk-nag packs report 0 unsuppressed errors. Only EX-01..EX-04 are suppressed (test `only registered exceptions are suppressed`). No S3 bucket logs to itself (`cfn-s3-selflog`). Synth drift is zero.
- Paths: `infra/aws-cdk/`, `evidence/aws/aws-remediation-vpc-rds/`.
- Check: CI `aws-cdk / synth-and-test` (tsc, Jest, synth, nag gate). At `e9310f3`: `sha256sum -c SHA256SUMS` re-run here (44/44 OK); `check_exceptions.py` re-run (5 suppressions tied to PROPOSED EX-01..EX-04). CDK itself was not re-run here.
- Evidence: aws-cdk [40802567002](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567002) @ `e9310f3` (`Tests: 36 passed, 36 total`). Synth templates @ `e9310f3`: `BankItLabSecureStorage` sha256 `9ba9be1d…`, `BankItLabNetworkDatabase` `c3dd0a0c…`. Pre-B5-2 evidence is kept under `superseded/pass3-pre-B5-2/`.
- Label: **EXECUTED (CI)** for synth, test and nag. Deployment: **NOT_EXECUTED**.
- Limitations: never deployed. B5-2 is recorded as fixed in `80f01d6` (least-privilege KMS key admin); #31 confirms the fix, but this report did not audit the key policy. All of EX-01..EX-04 are still **PROPOSED** in the register, so UA-1 blocks AC2 and AC5 (see FINAL_REPORT §3).
- Review: **request changes** (PR #14 @ `099479e`: B5-1, B5-2, B5-3). #31 @ `1fdf25a` reports B5-2 and B5-3 fixed and B5-1 open. Same account, so not AC1.

**M5. `postgres-recovery`: PostgreSQL backup/restore harness v2 (#2)**
- Job rows: B15a, B13, C8.
- Mapped to: FFIEC-AIO-VIB4 (supervisory). NIST-53 CP-9(1) *Testing for Reliability and Integrity* and CP-10 (industry). AWS-WA REL09-BP04 (product). PG *SQL Dump*, `pg_dump`, `pg_restore` (product).
- Acceptance: the restored database's row counts and MD5 fingerprints must equal the source's. Each of the 6 corruption or fault negatives must be reported FAIL. A `pg_dump` 18 vs server 16 mismatch must be reported `version_mismatch`, never PASS. Any v1 run must be marked HISTORICAL.
- Paths: `tests/integration/postgres/`, `evidence/postgres/`.
- Check: `python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-service-40741329107-1` (re-run at `e9310f3`: `cases=36 positive=11 negative=6 rows=36 problems=0 -> VERIFIED`).
- Evidence: [run 40741329107](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107) @ `2aac93c` (service 36/36, offline 38/38). postgres-restore-evidence [40802567000](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567000) @ `e9310f3`.
- Label: **EXECUTED (CI)** against real PostgreSQL servers.
- Limitations: one synthetic database; logical dumps only; no PITR; no RTO/RPO; no RDS snapshot.
- Review: **remediation verified** (PR #14 checkpoint 2 @ `eb8d259`, for the harness at `e7399fb`; `tasks.json` counts it toward AC1 for this harness only).

**M6. `m365-endpoint`: M365 / endpoint scenarios, PLAN_ONLY (#20 @ `1b3c240`)**
- Job rows: C6, B2.
- Mapped to: MS-DOCS Intune device compliance, M365 service health, Emergency access (product). NIST-53 AC-2(3) *Disable Accounts* (industry).
- Acceptance: all 13 scenarios must match their expected verdicts and finding codes. Any plan step with `executed: true`, or `mutationsExecuted` ≠ 0, must fail `check_plan_only.py`.
- Paths: `identity/m365/`, `evidence/m365/`.
- Check: `python3 identity/m365/m365_ops.py` (re-run: `scenarios=13 passed=13 … mutationsExecuted=0`); `python3 -m unittest discover -s identity/m365/tests` (29 OK).
- Evidence: `evidence/m365/runs/local-offline-20261028T181845Z/` (20 hashes OK). CI jobs `m365-*` and `plan-only-assertions` in 40802567048 @ `e9310f3` (local re-run at `e9310f3`: 29 OK).
- Label: **EXECUTED** (offline, synthetic tenant, PLAN_ONLY).
- Limitations: no tenant; nothing is mutated.
- Review: **none**.

**M7. `incident-demo` (#22 @ `9f21329`)**
- Job rows: B13, B15b, B8.
- Mapped to: NIST-61 (industry). FFIEC-AIO VI.C.4 *Event, Incident, and Problem Management* (supervisory). FFIEC-BCM V.F.1 *Incident Response* and VII.G.3 *Tabletop Exercise* (supervisory).
- Acceptance: injection, detection, diagnosis, recovery, timeline and simulation labelling must each be PASS. A forged MTTD or a missing detection event must be rejected. Missing PostgreSQL binaries must give NOT_EXECUTED (exit 3) and fail the gate.
- Paths: `scenarios/incident/`, `evidence/incident/`.
- Check: `python3 scenarios/incident/lib/timeline.py --verify evidence/incident/runs/local-20261028T181818Z` (re-run: `VERIFY PASS`); `bash scenarios/incident/selftest.sh evidence/incident/runs/local-20261028T181818Z` (re-run at `7fe6d72`; at `e9310f3` it ran as validate-all steps 14–15, PASS: 0 failures, including `missing_pg_binaries_not_executed (exit 3)`).
- Evidence: run `local-20261028T181818Z` (38 hashes OK); `incident-fresh-run` in 40802567048 @ `e9310f3`.
- Label: **SIMULATION**.
- Limitations: loopback lab DB crash. Simulated MTTD 3.584 s and MTTR 8.593 s are not operational metrics.
- Review: **none**.

### Not integrated (registry NOT_INTEGRATED or BLOCKED)

**M8. `orgs-security` (BLOCKED): AWS Organizations, SCPs, org trail, GuardDuty, Security Hub (#6 @ `e5e7f46`)**
- Job rows: A4, C4, C9.
- Mapped to: AWS-DOCS Organizations SCPs (product). NIST-53 AC-6 (industry).
- Acceptance: no log bucket logs to itself, and no SCP exemption can be used by an arbitrary role named to match. Both currently **fail** per review (B6-1, B6-2).
- Paths: `infra/orgs/`, `evidence/orgs/`.
- Check: the module's own Jest and lint. **Not run here, no CI.**
- Evidence: `evidence/orgs/SHA256SUMS` @ `e5e7f46` (local, author-reported).
- Label: **NOT_EXECUTED** reference (registry status BLOCKED).
- Limitations: B6-1 and B6-2 are open; CDK vs Terraform is undecided (B6-3).
- Review: **request changes** (PR #14 @ `e5e7f46`).

**M9. `acceptance`: acceptance contract, runner, adapters, vertical slice (#23, #24, #25, #26)**
- Job rows: B9.
- Mapped to: NIST-53 CA-2 *Control Assessments* (industry). PROJ (project-specific).
- Acceptance: a bundle missing a required check must be REJECTED. A required INFO verdict must give FAIL. A TSV/JSON verdict disagreement must be REJECTED.
- Paths: `schemas/acceptance/`, `tests/acceptance-contract/`, `tools/acceptance/`, `acceptance/modules/`, `scripts/acceptance/`.
- Check: `python3 -m unittest discover -s scripts/acceptance/tests` (re-run @ `eb42b23`: 32 OK).
- Evidence: acceptance [40776065038](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776065038) @ `eb42b23` (`OVERALL=PASS required=44`, `REVIEW_PENDING`). #23–#25: offline-validation [40747710616](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40747710616), [40747893103](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40747893103), [40748526680](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748526680) at their heads.
- Label: **EXECUTED (CI)**.
- Limitations: C4 decision is not enforced; C5 is open; hardening items are open (FINAL_REPORT §0b).
- Review: **changes required** (PR #27 @ `181bcdd`, C1–C6). The repairs were not re-reviewed.

**M10. `vendor-mock`: vendor API mock, vendor risk, RACI (#9 @ `d6efb82`)**
- Job rows: B6, B4.
- Mapped to: TPRM life cycle (supervisory). FFIEC-AIO III.E *Oversight of Third-Party Service Providers* (supervisory). NIST-53 SA-9 *External System Services* (industry).
- Acceptance: contract tests must fail on response-schema drift. The governance lint must report 0 findings on the register.
- Paths: `integrations/vendor-mock/`, `governance/vendor-risk/`.
- Check: `(cd integrations/vendor-mock && python3 -m unittest discover -s tests -t .)` (re-run: 45 OK); `python3 -m unittest discover -s governance/vendor-risk/tests` (25 OK).
- Evidence: 3 bundles under `evidence/vendor/runs/` (12, 14 and 15 hashes OK).
- Label: **SIMULATION** (fictional vendor).
- Limitations: no real vendor; no Jack Henry content.
- Review: **none**.

**M11. `observability`: observability collector and probes (#10 @ `3e40e39`)**
- Job rows: B5.
- Mapped to: FFIEC-AIO VI.D.1 *Monitoring and Reporting* (supervisory). NIST-53 SI-4 and CA-7 (industry). NIST-137 (industry).
- Acceptance: any probe error, timeout or out-of-bounds result must yield an unhealthy, fail-closed decision.
- Paths: `observability/`.
- Check: `python3 -m unittest discover -s observability/tests` (re-run: 64 OK).
- Evidence: `evidence/observability/runs/local-offline-20261028T180832Z/` (44 hashes OK).
- Label: **EXECUTED** (local, offline; no CI).
- Limitations: synthetic probes; no alerting, dashboard or on-call.
- Review: **none**.

**M12. `control-mapping`: FFIEC AIO control mapping (#16 @ `3f82697`)**
- Job rows: C9, B9.
- Mapped to: FFIEC-AIO, including VI.A.3 and VI.B.4, which the module cites itself (supervisory).
- Acceptance: the validator must reject mapping rows that lack a section reference or an evidence path.
- Paths: `governance/controls/`.
- Check: `python3 -m unittest discover -s governance/controls/tests` (re-run: 10 OK).
- Evidence: `evidence/control-review/` @ `3f82697`.
- Label: **EXECUTED** (validator). The mapping is a study reference: "mapped to", not compliance.
- Limitations: no examiner or auditor review.
- Review: **none**.

**M13. `patch-hardening`: patch rings and systemd hardening (#17 @ `5605b78`)**
- Job rows: B12, C8.
- Mapped to: FFIEC-AIO VI.B.3(b) *Patch Management* (supervisory). NIST-40 and NIST-53 SI-2 and CM-6 (industry). AWS-DOCS Patch Manager (product). SYSTEMD (product).
- Acceptance: the patch-manifest inspector must flag non-compliant ring definitions. The unit scorer must lower the score for units without the hardening options.
- Paths: `operations/patching/`, `operations/hardening/`.
- Check: `python3 -m unittest discover -s operations/patching/tests` (9 OK) and `-s operations/hardening/tests` (18 OK).
- Evidence: `evidence/host-operations/runs/local-offline-20261028T181252Z/` (102 hashes OK).
- Label: **EXECUTED** inspectors. Patching: **NOT_EXECUTED**.
- Limitations: no host was patched or hardened.
- Review: **none**.

**M14. `identity-governance` (#18 @ `f48e7e3`)**
- Job rows: C6, C9, B10.
- Mapped to: MS-DOCS PIM, Access reviews, Emergency access (product). AWS-DOCS IAM Identity Center with Entra ID (product). NIST-53 AC-2 and AC-6 (industry). FFIEC-AIO-VIA3 (supervisory).
- Acceptance: the privileged-role inventory must flag standing (non-PIM) assignments in fixtures. The synthetic guard must refuse non-synthetic tenant IDs.
- Paths: `identity/governance/`, `docs/federation/`.
- Check: `python3 -m unittest discover -s identity/governance/tests` (re-run: 65 OK).
- Evidence: `evidence/identity-governance/runs/local-offline-20261028T181435Z/` (49 hashes OK).
- Label: **EXECUTED** (offline, synthetic Graph fixtures). PIM and federation: **NOT_EXECUTED**.
- Limitations: no tenant.
- Review: **none**.

**M15. `hybrid-operations`: hybrid Windows, AD DS, DNS, GPO runbooks (#19 @ `3397dac`)**
- Job rows: A2, B2, B11, C7.
- Mapped to: MS-DOCS AD DS overview, Group Policy overview, Hybrid identity (product).
- Acceptance: every runbook keeps status NOT_EXECUTED until the listed evidence is committed and two people sign off. The linter must report 0 findings.
- Paths: `docs/runbooks/hybrid/`, `operations/hybrid/`.
- Check: `python3 -m unittest discover -s operations/hybrid/checks` (re-run: "checked 12 files, 0 findings").
- Evidence: `operations/hybrid/EXECUTION_STATUS.md` @ `3397dac`.
- Label: **NOT_EXECUTED** (the linter is EXECUTED).
- Limitations: no Windows or AD environment.
- Review: **none**.

**M16. `backup-dr-aws`: AWS Backup DR reference and cost model (#21 @ `10da54f`)**
- Job rows: B15b, B12, C3.
- Mapped to: FFIEC-BCM IV.A.3 and V.F.2 (supervisory). NIST-53 CP-9 and CP-10, and NIST-34 (industry). AWS-WA REL09-BP02 and REL09-BP04, and the Cost pillar *Expenditure and usage awareness* (product). AWS-DOCS Vault Lock, cross-Region copy, restore testing, encryption (product).
- Acceptance: each of the 7 recovery items stays NOT_EXECUTED until a job ID and completion time exist. The cost-model tests must pass.
- Paths: `backup/aws/`, `docs/runbooks/aws-backup/`.
- Check: `python3 -m unittest discover -s docs/runbooks/aws-backup/cost-capacity -p 'test_*.py'` (re-run: 8 OK). The CDK Jest in `backup/aws` was **not run here**.
- Evidence: `evidence/backup/aws-backup-dr/RECOVERY_EXECUTION_STATUS.json` (all 7 NOT_EXECUTED); `SHA256SUMS` (72 entries OK, root-relative).
- Label: **NOT_EXECUTED** for recovery. Cost model: EXECUTED (offline).
- Limitations: no AWS account; partially verified.
- Review: **none**.

### Documentation and review-record modules (registry NOT_INTEGRATED; no check command; label NOT_EXECUTED)

| Module | PR @ head | Job rows | Source | Review |
|---|---|---|---|---|
| `review-notes` | #14 @ `eb8d259`, #27 @ `72aa8b7`, #28 @ `fe6f24e`, #29 @ `384c610` (#30 and #31 are new and not yet in the registry) | B9 | project-specific | these *are* the agent reviews |
| `portfolio-cases` | #8 @ `7010d05` | A1, B13 | project-specific (links to other personal repos) | none |
| `final-report` (this) | #11 | B8, C10 | project-specific | none |
| `job-requirements-matrix` | #12 @ `31b69db` (+ `9fb49fa`) | all | JOB (project-specific) | none |
| `team-management` | #13 @ `9dc8f1f` | B11, B14 | FFIEC-AIO II.B.1(c) *IT Operations Management* (supervisory) | none |
| `learning-guide` | #15 @ `39728db` | C10 | project-specific | none |

### Planned, not started (registry NOT_STARTED; counted in the denominator)

| Module | Proposed owner | Source | Evidence | Label |
|---|---|---|---|---|
| `aws-network-edge` | AWS Remediation (proposed) | not mapped (no implementation) | none | NOT_EXECUTED |
| `endpoint-windows-automation` | unassigned | not mapped | none | NOT_EXECUTED |
| `inventory-diagrams` | unassigned | not mapped | none | NOT_EXECUTED |

## 4. Revised ETA (live candidate `e9310f3`)

The path to ELIGIBLE, from `tasks.json` @ `e9310f3` (`path_to_eligible`) and gate run [40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048):
1. **UA-3 (Ian):** protect `main` as specified, then land the gate, manifest and trusted config on `main` through that protection.
2. **Independent reviewer (Ian and the integrator):** add an independent reviewer account as a collaborator with Write, and add its login to `reviewer_allowlist` in the trusted config. **No such account exists today.**
3. **AC1:** that reviewer submits an APPROVED review on PR #7 for the exact candidate SHA. No undismissed CHANGES_REQUESTED may remain.
4. **UA-1, AC4, AC5 (Ian):** Ian posts the `ACCEPTANCE-DECISION v1` comment on PR #7 for the exact SHA. UA-2 (the Entra baseline) has to be settled before Ian can honestly write `AC4: ACCEPT`.
5. Re-run the gate, then the integrator merges; G7 follows. **AC6:** Ian's final acceptance.

| | Estimate | Basis |
|---|---|---|
| **Earliest** | about 01:00–02:30 EDT Thursday 2026-10-29 (after the deadline) | Assumes Ian does UA-3 and the decision comment now, a reviewer account is created and allow-listed within about 1 h, and that reviewer approves the current SHA with no further code change. CI takes about 2 min (observed) |
| **Likely** | Thursday 2026-10-29 during the day | No reviewer account exists, and each new commit needs a new decision comment and review |
| **Main uncertainty** | Who the independent reviewer is (an empty allow-list), and whether `e9310f3`'s unreviewed gate v3 survives review | |
| **Critical-path owner** | The integrator (#7). Also on the path: Ian (UA-1, UA-2, UA-3, reviewer account, AC6) and the independent reviewer | |

**Not achievable by midnight on current evidence:** a merge into `main` meeting AC1–AC5, or any independently accepted module.

## 5. Unsourced or weakly sourced items

- **No regulatory (law or regulation) source** is mapped. Banking-regulation alignment is limited to FFIEC and interagency supervisory guidance.
- **Job rows with no lab artifact or source:** A2, A5, A6, B1, B6 (relationship side), B14, B16, C2, C11, C12, D1–D4. Not lab-demonstrable.
- **Not verified:** CIS Controls safeguards (dropped); NIST CSF 2.0 subcategories (not cited).
- **Falsifiable requirements partly stated from module docs:** for M8 and M10–M16, the acceptance statements paraphrase each module's README and test names. Their tests were re-run (except M8), but this report did not audit test-by-test that every stated property is asserted.
- **The #31 findings F4, F6, R6 and F7** are quoted from the PR #31 body and not re-verified by this report.
- **NOT_STARTED modules** have no source mapping.
- **The denominator correction:** earlier versions of this file said 22 planned. That was wrong. It is 25 active (26 registered), per `modules.json` @ `e9310f3`.
