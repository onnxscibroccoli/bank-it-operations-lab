# Module → requirement map (source-backed)

- **Snapshot:** 2026-10-28, about 21:15 EDT. Deadline: midnight ET (00:00 EDT 2026-10-29).
- **Reference SHAs:** #7 final candidate [`7fe6d72`](https://github.com/onnxscibroccoli/bank-it-operations-lab/tree/7fe6d7281316190d9b39e35a448fb9fb81b92d50) (the #7 head has since moved to `b908a66`; see "Integration state"). Module PRs are cited at their current heads.
- **Wording rule:** every module is **mapped to** a source section. Nothing here claims certification, compliance, or examination readiness. The lab is offline and synthetic: nothing is deployed, and no AWS, Entra, M365 or Graph credentials were ever used.
- **Job requirement IDs** (A1–D4) come from the job requirements matrix ([#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12) @ `31b69db`, plus addendum G on `docs/job-matrix-addendum` @ [`9fb49fa`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/9fb49fa96903bf5b0de58dad7c5741c30d6a7d3d/docs/JOB_REQUIREMENTS_MATRIX.md)). The posting text itself is not in the repo.
- **Labels:** EXECUTED (a CI run URL or evidence hash is cited; offline runs on synthetic data are EXECUTED for the tool, never for a live system), SIMULATION (simulated or fictional system), NOT_EXECUTED (reference only).
- **"Re-run"** = re-executed by the reports agent on 2026-10-28 between 20:20 and 21:10 EDT against the cited SHA (tests, verifiers, `sha256sum -c`).

## 1. Counts

| Measure | Count | Definition and basis |
|---|---|---|
| **Planned** | **22** modules (16 executable, 6 documentation-only) | Every entry in `coordination/modules.json` on #7 @ `b908a66` |
| **Integrated** | **7** | In the #7 final candidate `7fe6d72`: integration-infra (#7), shared evidence validator (#3), Entra offline (#4), AWS CDK (#5), Postgres recovery (#2), M365 (#20 @ `1b3c240`), incident demo (#22 @ `9f21329`). Status `INTEGRATED` in `modules.json` |
| **Verified** | **14** of 16 executable (7 integrated + 7 not integrated); 1 partial; 1 unverified | Re-run here **or** CI green at the exact cited SHA. Integrated 7: CI at `7fe6d72` ([integration-gate 40793225624](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225624), 18 of 19 jobs success; the 19th is merge-eligibility, NOT ELIGIBLE by design) plus local re-run at `7fe6d72`. Not integrated, verified: acceptance #23–#26, vendor-mock #9, observability #10, control-mapping #16, patch-hardening #17, identity-governance #18, hybrid lint #19. **Partial:** backup-dr #21 (cost model and hashes only; its CDK Jest was not run). **Unverified:** orgs #6 (no CI; not re-run) |
| **Independently accepted** | **0** | Approval of the **exact** SHA by a human or an independent reviewer, bound to that SHA (AC1 definition in `tasks.json`). No GitHub review exists on any PR. The #7 final review packet for `7fe6d72` is "prepared, NOT YET REQUESTED". *Not counted:* PR #14's agent review notes approve #3 @ `fb36341` and #4 @ `d302c99` (with comments) and verify #2's harness at `e7399fb`. They are written from the same GitHub account, so `tasks.json` AC1 counts them toward #2's harness only, not toward any #7 head |

## 2. Sources (each fetched and checked about 21:00–21:10 EDT)

Source classes: **regulatory** = law or regulation text; **supervisory** = examiner or agency guidance to banks; **industry** = public standards (NIST is a US federal standard, not binding on banks); **product** = vendor documentation; **project-specific** = this repo's own plans or criteria.

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
| AWS-DOCS | AWS docs: S3 server access logging; RDS Multi-AZ; RDS Enhanced Monitoring; KMS key policies; VPC flow logs; Organizations SCPs; AWS Backup Vault Lock, cross-Region copy, restore testing, encryption; Systems Manager Patch Manager; IAM Identity Center with Microsoft Entra ID | product | <https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html>, <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html>, <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html>, <https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html>, <https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html>, <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html>, <https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html>, <https://docs.aws.amazon.com/aws-backup/latest/devguide/cross-region-backup.html>, <https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html>, <https://docs.aws.amazon.com/aws-backup/latest/devguide/encryption.html>, <https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html>, <https://docs.aws.amazon.com/singlesignon/latest/userguide/idp-microsoft-entra.html> | each HTTP 200 with the topic string present |
| MS-DOCS | Microsoft Learn: Conditional Access overview; Block legacy authentication; Emergency access (break-glass) accounts; Privileged Identity Management; Access reviews; Intune device compliance; Microsoft 365 service health; AD DS overview; Group Policy overview; What is hybrid identity | product | <https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview>, <https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-block-legacy-authentication>, <https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access>, <https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure>, <https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview>, <https://learn.microsoft.com/en-us/intune/device-security/compliance/overview>, <https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health>, <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview>, <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview>, <https://learn.microsoft.com/en-us/entra/identity/hybrid/whatis-hybrid-identity> | each HTTP 200 with the topic string present. The Intune URL redirected from `/intune/intune-service/protect/device-compliance-get-started` |
| PG | PostgreSQL 16 docs: 25.1 *SQL Dump*; `pg_dump`; `pg_restore` | product | <https://www.postgresql.org/docs/16/backup-dump.html>, <https://www.postgresql.org/docs/16/app-pgdump.html>, <https://www.postgresql.org/docs/16/app-pgrestore.html> | HTTP 200, titles present |
| SYSTEMD | `systemd.exec(5)`: sandboxing options such as `ProtectSystem=` | product | <https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html> | HTTP 200, `ProtectSystem` present |
| GH | GitHub Docs: Actions secure use ("full-length commit SHA" pinning); About protected branches (required status checks) | product | <https://docs.github.com/en/actions/reference/security/secure-use>, <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches> | HTTP 200, phrases present |
| CDK-NAG | cdk-nag rule packs (AwsSolutions, NIST 800-53 R5) | product | <https://github.com/cdklabs/cdk-nag> | HTTP 200 |
| PROJ | This repo's acceptance criteria AC1–AC6 (`coordination/tasks.json` on #7) and the #27 completion plan | project-specific | <https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/27> | Read from the repo |
| JOB | The IT Manager posting (JobLeads), via the job matrix | project-specific (external posting) | <https://www.jobleads.com/us/job/information-technology-manager--boston--e57b1e5ed0b5b152dff0ddd60c8e955b2> | Re-read about 20:20 EDT; live |

**Dropped as unverifiable from this box:** CIS Controls v8.1. The page loads (HTTP 200), but the safeguard names are rendered client-side and could not be confirmed, so no CIS section is cited. NIST CSF 2.0 subcategory IDs were not checked, so CSF is not cited.

## 3. Per-module map

Field order: job rows · sources (class) · falsifiable acceptance requirement · implementation paths · check command · evidence (path, SHA, run) · label · limitations · independent-review disposition.

### Integrated in `7fe6d72`

**M1. Integration gate (#7, integration-infra)**
- Job rows: B4, B7, B9.
- Mapped to: GH secure use (product): pin actions to a full-length commit SHA. GH protected branches (product). NIST-53 CM-3 *Configuration Change Control* (industry). PROJ AC1–AC5 (project-specific).
- Acceptance (falsifiable): `merge-eligibility` must exit non-zero unless AC1–AC5 are MET for the exact tested SHA. Any required job that is missing, skipped, cancelled, failed or NOT_EXECUTED must make `final-summary` fail. Every third-party `uses:` must be a 40-hex SHA.
- Paths: `.github/workflows/`, `scripts/ci/`, `scripts/validate-all.sh`, `coordination/`.
- Check: `python3 -m unittest discover -s scripts/ci/tests` (re-run at `7fe6d72`: 43 tests OK) and `scripts/validate-all.sh --python-only` (re-run: PASS, 30 steps).
- Evidence: [integration-gate 40793225624](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225624) and push [40793219129](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793219129) @ `7fe6d72`: 18/19 success; `merge-eligibility` NOT ELIGIBLE (`AC1: UNMET`, `AC2: PARTIAL`, `AC4: PARTIAL`, `AC5: UNMET`).
- Label: **EXECUTED (CI)**.
- Limitations: advisory only, because `main` has no branch protection (404 unset).
- Review: **none**. Packet `coordination/review-requests/PR-7-candidate-7fe6d72.md` prepared, not requested.

**M2. Shared evidence validator (#3)**
- Job rows: B9, C10.
- Mapped to: NIST-53 AU-9 *Protection of Audit Information* (industry). FFIEC-AIO VI.B.7 *Log Management* (supervisory).
- Acceptance: any changed, missing or extra file in an evidence bundle, or a malformed manifest, must make the validator exit non-zero.
- Paths: `evidence/shared/`.
- Check: `python3 -m unittest discover -s evidence/shared/tests` (re-run at `7fe6d72`: 16 OK).
- Evidence: offline-validation [40793225341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225341) @ `7fe6d72`.
- Label: **EXECUTED (CI)**.
- Limitations: integrity check only. It does not prove a log's content is true.
- Review: **approve** (PR #14 agent notes @ `fb36341`; same GitHub account, so not AC1).

**M3. Entra Conditional Access, offline (#4)**
- Job rows: C6, C9.
- Mapped to: MS-DOCS Conditional Access, Block legacy authentication, Emergency access (product). NIST-53 IA-2(1) *Multi-factor Authentication to Privileged Accounts* (industry). FFIEC-AIO-VIA3 (supervisory).
- Acceptance: `ca_validator.py` exits 0 on the baseline policies. Each negative fixture must fail. Report-only or disabled policies never satisfy a requirement. Malformed input exits 2.
- Paths: `identity/entra/`, `tests/entra/`, `evidence/entra/`.
- Check: `python3 identity/entra/ca_validator.py --quiet` (re-run: `overall=PASS exit=0`); `python3 -m unittest discover -s tests/entra` (re-run: 25 OK).
- Evidence: `evidence/entra/runs/local-offline-20261028T150359Z/` @ `d302c99` (46 hashes re-checked OK); CI 40793225341 @ `7fe6d72`.
- Label: **EXECUTED** (offline, synthetic). Tenant: **NOT_EXECUTED**.
- Limitations: no tenant or Graph call. Baseline choices are unconfirmed (UA-2).
- Review: **approve with comments** (PR #14 agent notes @ `d302c99`; not AC1).

**M4. AWS CDK: private VPC, RDS, secure storage (#5)**
- Job rows: A3, B3, C3, C9.
- Mapped to: AWS-WA SEC03-BP02 and SEC08-BP02 (product). AWS-DOCS S3 server access logging, RDS Multi-AZ, RDS Enhanced Monitoring, KMS key policies, VPC flow logs (product). NIST-53 AC-6 and SC-28 (industry). CDK-NAG (product).
- Acceptance: both cdk-nag packs report 0 unsuppressed errors. Only EX-01..EX-04 are suppressed (test `only registered exceptions are suppressed`). No S3 bucket logs to itself (`cfn-s3-selflog`). Synth drift is zero.
- Paths: `infra/aws-cdk/`, `evidence/aws/aws-remediation-vpc-rds/`.
- Check: CI `aws-cdk / synth-and-test` (tsc, Jest, synth, nag gate). Not re-run here at `7fe6d72`.
- Evidence: aws-cdk [40793225339](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225339) @ `7fe6d72`. Synth templates @ `099479e`: `BankItLabSecureStorage` sha256 `0b0eda0f…`, `BankItLabNetworkDatabase` `44d48d2e…`.
- Label: **EXECUTED (CI)** for synth, test and nag. Deployment: **NOT_EXECUTED**.
- Limitations: never deployed. B5-2 (KMS key-admin escalation, which cdk-nag misses) is open. EX-04 is undecided (UA-1).
- Review: **request changes** (PR #14 @ `099479e`: B5-1, B5-2, B5-3).

**M5. PostgreSQL backup/restore harness v2 (#2)**
- Job rows: B15a, B13, C8.
- Mapped to: FFIEC-AIO-VIB4 (supervisory). NIST-53 CP-9(1) *Testing for Reliability and Integrity* and CP-10 (industry). AWS-WA REL09-BP04 (product). PG *SQL Dump*, `pg_dump`, `pg_restore` (product).
- Acceptance: the restored database's row counts and MD5 fingerprints must equal the source's. Each of the 6 corruption or fault negatives must be reported FAIL. A `pg_dump` 18 vs server 16 mismatch must be reported `version_mismatch`, never PASS. Any v1 run must be marked HISTORICAL.
- Paths: `tests/integration/postgres/`, `evidence/postgres/`.
- Check: `python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-service-40741329107-1` (re-run at `7fe6d72`: `cases=36 … problems=0 -> VERIFIED`).
- Evidence: [run 40741329107](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107) @ `2aac93c` (service 36/36, offline 38/38). postgres-restore-evidence [40793225365](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40793225365) @ `7fe6d72`.
- Label: **EXECUTED (CI)** against real PostgreSQL servers.
- Limitations: one synthetic database; logical dumps only; no PITR; no RTO/RPO; no RDS snapshot.
- Review: **remediation verified** (PR #14 checkpoint 2 @ `eb8d259`, for the harness at `e7399fb`; `tasks.json` counts it toward AC1 for this harness only).

**M6. M365 / endpoint scenarios, PLAN_ONLY (#20 @ `1b3c240`)**
- Job rows: C6, B2.
- Mapped to: MS-DOCS Intune device compliance, M365 service health, Emergency access (product). NIST-53 AC-2(3) *Disable Accounts* (industry).
- Acceptance: all 13 scenarios must match their expected verdicts and finding codes. Any plan step with `executed: true`, or `mutationsExecuted` ≠ 0, must fail `check_plan_only.py`.
- Paths: `identity/m365/`, `evidence/m365/`.
- Check: `python3 identity/m365/m365_ops.py` (re-run: `scenarios=13 passed=13 … mutationsExecuted=0`); `python3 -m unittest discover -s identity/m365/tests` (29 OK).
- Evidence: `evidence/m365/runs/local-offline-20261028T181845Z/` (20 hashes OK). CI jobs `m365-*` and `plan-only-assertions` in 40793225624.
- Label: **EXECUTED** (offline, synthetic tenant, PLAN_ONLY).
- Limitations: no tenant; nothing is mutated.
- Review: **none**.

**M7. Incident demo (#22 @ `9f21329`)**
- Job rows: B13, B15b, B8.
- Mapped to: NIST-61 (industry). FFIEC-AIO VI.C.4 *Event, Incident, and Problem Management* (supervisory). FFIEC-BCM V.F.1 *Incident Response* and VII.G.3 *Tabletop Exercise* (supervisory).
- Acceptance: injection, detection, diagnosis, recovery, timeline and simulation labelling must each be PASS. A forged MTTD or a missing detection event must be rejected. Missing PostgreSQL binaries must give NOT_EXECUTED (exit 3) and fail the gate.
- Paths: `scenarios/incident/`, `evidence/incident/`.
- Check: `python3 scenarios/incident/lib/timeline.py --verify evidence/incident/runs/local-20261028T181818Z` (re-run: `VERIFY PASS`); `bash scenarios/incident/selftest.sh evidence/incident/runs/local-20261028T181818Z` (re-run: 0 failures, including `missing_pg_binaries_not_executed (exit 3)`).
- Evidence: run `local-20261028T181818Z` (38 hashes OK); `incident-fresh-run` in 40793225624.
- Label: **SIMULATION**.
- Limitations: loopback lab DB crash. Simulated MTTD 3.584 s and MTTR 8.593 s are not operational metrics.
- Review: **none**.

### Not integrated

**M8. AWS Organizations, SCPs, org trail, GuardDuty, Security Hub (#6 @ `e5e7f46`)**
- Job rows: A4, C4, C9.
- Mapped to: AWS-DOCS Organizations SCPs (product). NIST-53 AC-6 (industry).
- Acceptance: no log bucket logs to itself, and no SCP exemption can be used by an arbitrary role named to match. Both currently **fail** per review (B6-1, B6-2).
- Paths: `infra/orgs/`, `evidence/orgs/`.
- Check: the module's own Jest and lint. **Not run here, no CI.**
- Evidence: `evidence/orgs/SHA256SUMS` @ `e5e7f46` (local, author-reported).
- Label: **NOT_EXECUTED** reference (module status EXCLUDED).
- Limitations: B6-1 and B6-2 are open; CDK vs Terraform is undecided (B6-3).
- Review: **request changes** (PR #14 @ `e5e7f46`).

**M9. Acceptance contract, runner, adapters, vertical slice (#23, #24, #25, #26)**
- Job rows: B9.
- Mapped to: NIST-53 CA-2 *Control Assessments* (industry). PROJ (project-specific).
- Acceptance: a bundle missing a required check must be REJECTED. A required INFO verdict must give FAIL. A TSV/JSON verdict disagreement must be REJECTED.
- Paths: `schemas/acceptance/`, `tests/acceptance-contract/`, `tools/acceptance/`, `acceptance/modules/`, `scripts/acceptance/`.
- Check: `python3 -m unittest discover -s scripts/acceptance/tests` (re-run @ `eb42b23`: 32 OK).
- Evidence: acceptance [40776065038](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40776065038) @ `eb42b23` (`OVERALL=PASS required=44`, `REVIEW_PENDING`). #23–#25: offline-validation [40747710616](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40747710616), [40747893103](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40747893103), [40748526680](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40748526680) at their heads.
- Label: **EXECUTED (CI)**.
- Limitations: C4 decision is not enforced; C5 is open; hardening items are open (FINAL_REPORT §0b).
- Review: **changes required** (PR #27 @ `181bcdd`, C1–C6). The repairs were not re-reviewed.

**M10. Vendor API mock, vendor risk, RACI (#9 @ `d6efb82`)**
- Job rows: B6, B4.
- Mapped to: TPRM life cycle (supervisory). FFIEC-AIO III.E *Oversight of Third-Party Service Providers* (supervisory). NIST-53 SA-9 *External System Services* (industry).
- Acceptance: contract tests must fail on response-schema drift. The governance lint must report 0 findings on the register.
- Paths: `integrations/vendor-mock/`, `governance/vendor-risk/`.
- Check: `(cd integrations/vendor-mock && python3 -m unittest discover -s tests -t .)` (re-run: 45 OK); `python3 -m unittest discover -s governance/vendor-risk/tests` (25 OK).
- Evidence: 3 bundles under `evidence/vendor/runs/` (12, 14 and 15 hashes OK).
- Label: **SIMULATION** (fictional vendor).
- Limitations: no real vendor; no Jack Henry content.
- Review: **none**.

**M11. Observability collector and probes (#10 @ `3e40e39`)**
- Job rows: B5.
- Mapped to: FFIEC-AIO VI.D.1 *Monitoring and Reporting* (supervisory). NIST-53 SI-4 and CA-7 (industry). NIST-137 (industry).
- Acceptance: any probe error, timeout or out-of-bounds result must yield an unhealthy, fail-closed decision.
- Paths: `observability/`.
- Check: `python3 -m unittest discover -s observability/tests` (re-run: 64 OK).
- Evidence: `evidence/observability/runs/local-offline-20261028T180832Z/` (44 hashes OK).
- Label: **EXECUTED** (local, offline; no CI).
- Limitations: synthetic probes; no alerting, dashboard or on-call.
- Review: **none**.

**M12. FFIEC AIO control mapping (#16 @ `3f82697`)**
- Job rows: C9, B9.
- Mapped to: FFIEC-AIO, including VI.A.3 and VI.B.4, which the module cites itself (supervisory).
- Acceptance: the validator must reject mapping rows that lack a section reference or an evidence path.
- Paths: `governance/controls/`.
- Check: `python3 -m unittest discover -s governance/controls/tests` (re-run: 10 OK).
- Evidence: `evidence/control-review/` @ `3f82697`.
- Label: **EXECUTED** (validator). The mapping is a study reference: "mapped to", not compliance.
- Limitations: no examiner or auditor review.
- Review: **none**.

**M13. Patch rings and systemd hardening (#17 @ `5605b78`)**
- Job rows: B12, C8.
- Mapped to: FFIEC-AIO VI.B.3(b) *Patch Management* (supervisory). NIST-40 and NIST-53 SI-2 and CM-6 (industry). AWS-DOCS Patch Manager (product). SYSTEMD (product).
- Acceptance: the patch-manifest inspector must flag non-compliant ring definitions. The unit scorer must lower the score for units without the hardening options.
- Paths: `operations/patching/`, `operations/hardening/`.
- Check: `python3 -m unittest discover -s operations/patching/tests` (9 OK) and `-s operations/hardening/tests` (18 OK).
- Evidence: `evidence/host-operations/runs/local-offline-20261028T181252Z/` (102 hashes OK).
- Label: **EXECUTED** inspectors. Patching: **NOT_EXECUTED**.
- Limitations: no host was patched or hardened.
- Review: **none**.

**M14. Identity governance (#18 @ `f48e7e3`)**
- Job rows: C6, C9, B10.
- Mapped to: MS-DOCS PIM, Access reviews, Emergency access (product). AWS-DOCS IAM Identity Center with Entra ID (product). NIST-53 AC-2 and AC-6 (industry). FFIEC-AIO-VIA3 (supervisory).
- Acceptance: the privileged-role inventory must flag standing (non-PIM) assignments in fixtures. The synthetic guard must refuse non-synthetic tenant IDs.
- Paths: `identity/governance/`, `docs/federation/`.
- Check: `python3 -m unittest discover -s identity/governance/tests` (re-run: 65 OK).
- Evidence: `evidence/identity-governance/runs/local-offline-20261028T181435Z/` (49 hashes OK).
- Label: **EXECUTED** (offline, synthetic Graph fixtures). PIM and federation: **NOT_EXECUTED**.
- Limitations: no tenant.
- Review: **none**.

**M15. Hybrid Windows, AD DS, DNS, GPO runbooks (#19 @ `3397dac`)**
- Job rows: A2, B2, B11, C7.
- Mapped to: MS-DOCS AD DS overview, Group Policy overview, Hybrid identity (product).
- Acceptance: every runbook keeps status NOT_EXECUTED until the listed evidence is committed and two people sign off. The linter must report 0 findings.
- Paths: `docs/runbooks/hybrid/`, `operations/hybrid/`.
- Check: `python3 -m unittest discover -s operations/hybrid/checks` (re-run: "checked 12 files, 0 findings").
- Evidence: `operations/hybrid/EXECUTION_STATUS.md` @ `3397dac`.
- Label: **NOT_EXECUTED** (the linter is EXECUTED).
- Limitations: no Windows or AD environment.
- Review: **none**.

**M16. AWS Backup DR reference and cost model (#21 @ `10da54f`)**
- Job rows: B15b, B12, C3.
- Mapped to: FFIEC-BCM IV.A.3 and V.F.2 (supervisory). NIST-53 CP-9 and CP-10, and NIST-34 (industry). AWS-WA REL09-BP02 and REL09-BP04, and the Cost pillar *Expenditure and usage awareness* (product). AWS-DOCS Vault Lock, cross-Region copy, restore testing, encryption (product).
- Acceptance: each of the 7 recovery items stays NOT_EXECUTED until a job ID and completion time exist. The cost-model tests must pass.
- Paths: `backup/aws/`, `docs/runbooks/aws-backup/`.
- Check: `python3 -m unittest discover -s docs/runbooks/aws-backup/cost-capacity -p 'test_*.py'` (re-run: 8 OK). The CDK Jest in `backup/aws` was **not run here**.
- Evidence: `evidence/backup/aws-backup-dr/RECOVERY_EXECUTION_STATUS.json` (all 7 NOT_EXECUTED); `SHA256SUMS` (72 entries OK, root-relative).
- Label: **NOT_EXECUTED** for recovery. Cost model: EXECUTED (offline).
- Limitations: no AWS account; partially verified.
- Review: **none**.

### Documentation-only modules (no check command; label NOT_EXECUTED)

| Module | PR @ head | Job rows | Source | Review |
|---|---|---|---|---|
| Review notes | #14 @ `eb8d259`, #27 @ `72aa8b7` | B9 | project-specific | these *are* the agent reviews |
| Portfolio case studies | #8 @ `7010d05` | A1, B13 | project-specific (links to other personal repos) | none |
| Final report (this) | #11 | B8, C10 | project-specific | none |
| Job requirements matrix | #12 @ `31b69db` (+ `9fb49fa`) | all | JOB (project-specific) | none |
| Team model, on-call, escalation | #13 @ `9dc8f1f` | B11, B14 | FFIEC-AIO II.B.1(c) *IT Operations Management* (supervisory) | none |
| Learning guide and ADRs | #15 @ `39728db` | C10 | project-specific | none |

## 4. Revised ETA (grounded in the open items)

The critical path to a merge into `main` runs through these items. They come from `tasks.json` on #7 @ `b908a66`, CI run [40798145700](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40798145700) and this report's verification:
1. **AC5 / B5-2:** an AUTONOMOUS_FIX by the aws-cdk module owner. It needs a code change, so a **new candidate** and a new CI run are required.
2. **AC1:** an independent review of that new candidate (lane E). Requesting it is an integrator step. No request has been sent for `7fe6d72`.
3. **AC2:** Ian decides EX-04 (UA-1).
4. **AC4:** Ian confirms the Entra baseline (UA-2).
5. Integrator merge; then G7 verification on `main`.
6. **AC6:** Ian's final portfolio acceptance.

| | Estimate | Basis |
|---|---|---|
| **Earliest** | about 00:30–01:30 EDT Thursday 2026-10-29 (just past the deadline) | Assumes: Ian decides UA-1 and UA-2 now; the B5-2 fix lands within about 1 h; CI on the new candidate takes about 2 min (observed); and an independent review returns within about 1 h. |
| **Likely** | Thursday 2026-10-29, during the day | No review request has been sent for any #7 candidate. Each code change invalidates the previous review. |
| **Main uncertainty** | Independent-review turnaround (AC1) and the B5-2 fix. Neither has an observed start. | |
| **Critical-path owner** | Integrator (#7): new candidate, review request, merge. Owners on the path: the aws-cdk module owner (B5-2), lane E (review) and Ian (UA-1, UA-2, AC6). | |

**Not achievable by midnight on current evidence:** independently accepted modules > 0, or a merge into `main` meeting AC1–AC5.

## 5. Unsourced or weakly sourced items

- **No regulatory (law or regulation) source** is mapped. Banking-regulation alignment is limited to FFIEC and interagency supervisory guidance.
- **Job rows with no lab artifact or source:** A2, A5, A6, B1, B6 (relationship side), B14, B16, C2, C11, C12, D1–D4. Not lab-demonstrable.
- **Not verified:** CIS Controls safeguards (dropped); NIST CSF 2.0 subcategories (not cited).
- **Falsifiable requirements partly stated from module docs:** for M8, M10–M16, the acceptance statements paraphrase each module's README and test names. Their tests were re-run (except M8), but this report did not audit test-by-test that every stated property is asserted.
