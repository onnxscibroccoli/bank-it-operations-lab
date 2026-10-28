# FFIEC IT Examination Handbook, "Architecture, Infrastructure, and Operations" (AIO, June 2021): lab control mapping

> **Read this first.** `bank-it-operations-lab` is a reproducible **lab**, not a bank, a regulated entity, or a production
> environment. This document is an engineering cross-reference from *selected* AIO booklet topics to artifacts that exist in this
> repository. It is **not** an examination, an audit, an assurance report, a compliance certification, or a regulatory opinion,
> and it does not say that any FFIEC expectation is met. The AIO booklet itself says it "does not impose requirements on
> entities"; it describes principles and practices that examiners review.

- Prepared: 2026-10-28 (America/New_York). Branch: `control-mapping`, based on `main` @ `7f50348bf1370381615eaed91c02607fe41de2f5`.
- Machine-readable form: [`ffiec-aio-mapping.csv`](ffiec-aio-mapping.csv) (one line per mapped topic: status, lab claim,
  limitations, organizational dependencies) and [`ffiec-aio-artifacts.csv`](ffiec-aio-artifacts.csv) (one line per referenced
  artifact, pinned to a full commit SHA).
- Validation: [`validate_mapping.py`](validate_mapping.py) checks that every referenced `commit:path` exists in git (and, with
  `--check-branches`, that each commit is on its source branch), statuses come from the allowed set, section ids are real AIO
  section ids, SIMULATION/OBSERVED rows cite evidence output, and this file avoids certification wording. Tests:
  [`tests/test_validate_mapping.py`](tests/test_validate_mapping.py). Captured run:
  [`evidence/control-review/validation-run.log`](../../evidence/control-review/validation-run.log).
- Review notes and coverage counts: [`evidence/control-review/`](../../evidence/control-review/README.md).

## Sources (all retrieved 2026-10-28)

| # | Source | URL | Used for |
|---|---|---|---|
| S1 | FFIEC IT Examination Handbook InfoBase, AIO booklet (authoritative, online) | https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ | Booklet contents; every section id and title used here |
| S2 | AIO section VI.B.4 Backup and Replication Processes (online) | https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/vi-operations/vib-it-operational-processes/vib4-backup-and-replication-processes/ | Section text for AIO-10, AIO-11 |
| S3 | AIO section VI.A.3 Identity and Access Management (online) | https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/vi-operations/via-operational-controls/via3-identity-and-access-management/ | Section text for AIO-08 |
| S4 | FFIEC press release, June 30, 2021 | https://www.ffiec.gov/press/pr063021.htm | Issue date; replaces the July 2004 "Operations" booklet |
| S5 | FFIEC IT Booklets list (official PDF download) | https://ithandbook.ffiec.gov/it-booklets | Location of the official PDF |
| S6 | Copy of the June 2021 AIO booklet PDF hosted by AFSA (**third-party mirror, not authoritative**) | https://afsaonline.org/wp-content/uploads/2021/07/AIO-IT-Booklet.pdf | Booklet page numbers (from its table of contents) and section text; SHA-256 `9f33e1a9a52054eb5ec4c5313c47198064d169f8cc315fdcbce27619aebfccb4` |

The official PDF (S5) returned HTTP 403 to scripted download, so page numbers come from S6 and should be re-checked against S5.
Section-level online URLs are given only where the page was opened and confirmed (S2, S3); for other rows cite S1 with the
section id and page. Section ids, titles and page numbers are copied from the booklet. No booklet text has been turned into a
"control" or a requirement; the "Lab claim" column describes what the lab artifact does, in the lab's own terms.

## Status definitions

| Status | Meaning | Proof needed in the repo |
|---|---|---|
| STATIC | Code, configuration or documentation exists; nothing was executed to exercise it for this topic | the file itself |
| SIMULATION | A dry run, unit test, `cdk synth`, linter, offline validator or ephemeral CI exercise ran against lab code or synthetic data | a committed log/output file (role `evidence`) |
| OBSERVED | Output captured from a real run in a live, non-ephemeral environment that the lab operates | a committed log/output file from that environment |
| NOT_EXECUTED | A configuration or procedure is defined, but the activity it implies (for example a backup job or a restore) has never run | the definition |

Conservative rule: GitHub Actions jobs and ephemeral PostgreSQL service containers count as SIMULATION, not OBSERVED, because they
run lab code on throwaway infrastructure. Nothing in this repository was deployed to AWS or applied to an Entra ID tenant.

## Where the artifacts live

**Everything mapped below is on open, unmerged draft pull requests. `main` contains only `README.md`.** Each artifact is pinned
to the PR head commit current when this mapping was written; if a PR is rebased or amended, re-run the validator.


| PR | Branch | Pinned head | Content |
|---|---|---|---|
| [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) | `bank-aws-001` | `e494bcfc3986c2d21a4cf92453857f69dbf69ce3` | CDK secure storage stack, credential-free CI workflow, evidence |
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | `ci-evidence-postgres` | `e7399fbb538504f723d1fb83e32ce50604807b8e` | Postgres backup/restore exercise (harness v2), CI and offline runs |
| [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) | `review/pr1-pr2-evidence-audit` | `fb3634115cb22b26e717afe2caec69661f56e874` | Written review of PR #1/#2, shared evidence validator |
| [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) | `entra-ca-offline` | `d302c99d95116c39d7aa65937614bccb830f2d6e` | Offline Entra Conditional Access baseline, validator, evidence |
| [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) | `aws-remediation-vpc-rds` | `099479e6d23968adb17762d88d84131998fca07c` | Private VPC + RDS PostgreSQL, AwsSolutions + NIST 800-53 R5 nag, exceptions register |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | `orgs-security-refs` | `e5e7f4604597c7e6e35e69bf0607fe0535d4cdab` | Organizations OU/SCP reference, org CloudTrail, GuardDuty/Security Hub |
| [#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) | `vendor-mock` | `88a37856da05468ecce86b4c5d1e1ac0b8530bc5` | Fictional vendor API mock, vendor-risk templates, outage tabletop scenario, governance lint |
| [#10](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/10) | `observability` | `3e40e39d73da3f0d20bced68651a54ee6c63846c` | Offline host health collector and synthetic probes |
| [#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13) | `team-management` | `9dc8f1f587a69d85b05af0fc28d76f4ed5925d44` | Synthetic team model, on-call, escalation, ticket priority, CAB-style change review |

Open PRs not referenced: #7 `overnight/integration` (an integration branch re-carrying #2-#5; the source PRs are cited
directly instead), #8 `portfolio-cases`, #11 `reports/final-report`, #12 `job-requirements-matrix` (no AIO-relevant artifacts).
Not delivered on any branch, so not referenced: `backup/aws/**` and `docs/runbooks/**` (a `backup/aws` directory exists only as
uncommitted work in a local checkout).

## Summary

Selected topics mapped: **17** rows across 15 AIO sections; 97 artifact references.

| Status | Rows |
|---|---|
| STATIC | 2 |
| SIMULATION | 14 |
| OBSERVED | 0 |
| NOT_EXECUTED | 1 |

| Row | AIO section | Title | Booklet p. | Status | PRs |
|---|---|---|---|---|---|
| AIO-01 | III.A.2(a) | Database Security | 18 | **SIMULATION** | #5 |
| AIO-02 | III.D.1 | Change Management | 35 | **SIMULATION** | #1, #3, #13 |
| AIO-03 | III.F | Resilience | 38 | **SIMULATION** | #5 |
| AIO-04 | III.G | Remote Access | 39 | **SIMULATION** | #4 |
| AIO-05 | V.B.1 | Network | 51 | **SIMULATION** | #5 |
| AIO-06 | V.C.2(a) | Open Source Software | 59 | **STATIC** | #1, #5, #6 |
| AIO-07 | VI.A.2 | Authorization Boundary | 69 | **SIMULATION** | #6 |
| AIO-08 | VI.A.3 | Identity and Access Management | 69 | **SIMULATION** | #4, #5, #6 |
| AIO-09 | VI.B.2 | Configuration Management | 72 | **SIMULATION** | #5, #6 |
| AIO-10 | VI.B.4 | Backup and Replication Processes (logical Postgres backup/restore exercise) | 75 | **SIMULATION** | #2 |
| AIO-11 | VI.B.4 | Backup and Replication Processes (AWS-native RDS backups) | 75 | **NOT_EXECUTED** | #5 |
| AIO-12 | VI.B.7 | Log Management | 77 | **SIMULATION** | #5, #6 |
| AIO-13 | VI.D.1 | Monitoring and Reporting | 84 | **SIMULATION** | #6 |
| AIO-14 | VII.A.5(a) | Access Control Considerations | 92 | **SIMULATION** | #4, #6 |
| AIO-15 | III.E | Oversight of Third-Party Service Providers | 37 | **SIMULATION** | #9 |
| AIO-16 | VI.C.4 | Event, Incident, and Problem Management | 82 | **STATIC** | #13 |
| AIO-17 | VI.D.1 | Monitoring and Reporting (host health collector) | 84 | **SIMULATION** | #10 |

## Mapping detail

### AIO-01 - III.A.2(a) Database Security - **SIMULATION**

- Source: AIO booklet (June 2021) section III.A.2(a), p. 18; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: CDK definition of a private RDS PostgreSQL instance (publiclyAccessible=false; isolated subnets; storage, Performance Insights and generated secret encrypted with a customer-managed KMS key; IAM authentication; SG-to-SG ingress only). Synthesized and unit-tested offline.
- Limitations: Never deployed. No database accounts, default-account handling, password rotation or activity monitoring were exercised against a running database. Tests assert template properties only.
- Organizational dependencies (a real institution must supply): DBA role and accountability; data classification of what the database holds; access request/approval and periodic access recertification; password and privileged-account standards; database activity monitoring and review staffing.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/aws-cdk/lib/network-database-stack.ts` | `099479e6d239` | #5 | RDS PostgreSQL definition |
| test | `infra/aws-cdk/test/network-database-stack.test.ts` | `099479e6d239` | #5 | 'RDS PostgreSQL is private ... encrypted with the CMK' test |
| evidence | `evidence/aws/aws-remediation-vpc-rds/logs/08-pass3-jest.log` | `099479e6d239` | #5 | jest run log (exit 0 per COMMANDS.tsv) |
| evidence | `evidence/aws/aws-remediation-vpc-rds/synth/BankItLabNetworkDatabase.template.json` | `099479e6d239` | #5 | synthesized template |
| evidence | `evidence/aws/aws-remediation-vpc-rds/cdk-nag/NIST.800.53.R5--BankItLabNetworkDatabase-NagReport.csv` | `099479e6d239` | #5 | cdk-nag NIST 800-53 R5 report |

### AIO-02 - III.D.1 Change Management - **SIMULATION**

- Source: AIO booklet (June 2021) section III.D.1, p. 35; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Changes are proposed as pull requests from feature branches; a credential-free GitHub Actions workflow (tsc, jest, cdk synth, cdk-nag gate, evidence hash check) ran on PR #1 and its run records were captured; a separate written review of PR #1/#2 exists.
- Limitations: All six PRs are still open; nothing has been merged to main, so no approved change has reached the baseline. Single author/operator. Branch protection, required reviewers and approval records were not verified. CI runs are of lab code, not of a production change.
- Organizational dependencies (a real institution must supply): Change management policy and change categories; change advisory/approval authority; segregation of duties between author, approver and deployer; emergency change procedure; post-implementation review; change records retention.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `.github/workflows/bank-aws-001-cdk.yml` | `e494bcfc3986` | #1 | credential-free CI workflow |
| evidence | `evidence/aws/ci/RUNS.md` | `e494bcfc3986` | #1 | run ids 40630567160 / 40630990406 / 40631120535 |
| evidence | `evidence/aws/logs/37-gh-run-watch-ci-1.log` | `e494bcfc3986` | #1 | captured gh run watch output for CI run 1 |
| evidence | `evidence/aws/logs/54-gh-run-view-ci-3.log` | `e494bcfc3986` | #1 | captured gh run view output for CI run 3 |
| documentation | `evidence/aws/logs/REBASE-MAP.md` | `e494bcfc3986` | #1 | git history rewrite record |
| documentation | `reports/review-pr1-pr2.md` | `fb3634115cb2` | #3 | written review of PR #1 and PR #2 |
| documentation | `docs/management/change-review.md` | `9dc8f1f587a6` | #13 | synthetic CAB-style change review process (not an institutional policy) |

### AIO-03 - III.F Resilience - **SIMULATION**

- Source: AIO booklet (June 2021) section III.F, p. 38; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Reference design choices that relate to resilience: RDS Multi-AZ and deletion protection, S3 versioning and RETAIN removal policies. Synthesized offline; cross-region replication is explicitly a proposed exception (EX-02).
- Limitations: No failover, AZ loss or recovery test was performed. No cross-region or cross-account copy. Not integrated with any business continuity program. Exception EX-02 is PROPOSED, not approved.
- Organizational dependencies (a real institution must supply): Business continuity management program; business impact analysis with RTO/RPO; resilience testing schedule and lessons-learned process; exception approval authority; third-party (CSP) resilience due diligence.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/aws-cdk/lib/network-database-stack.ts` | `099479e6d239` | #5 | multiAz / deletionProtection / RETAIN |
| implementation | `infra/aws-cdk/lib/secure-storage-stack.ts` | `099479e6d239` | #5 | S3 versioning / RETAIN |
| evidence | `evidence/aws/aws-remediation-vpc-rds/logs/09-pass3-cdk-synth.log` | `099479e6d239` | #5 | final synth log (exit 0) |
| documentation | `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` | `099479e6d239` | #5 | EX-02 (no cross-region replication) PROPOSED |

### AIO-04 - III.G Remote Access - **SIMULATION**

- Source: AIO booklet (June 2021) section III.G, p. 39; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Offline Entra ID Conditional Access baseline that blocks legacy authentication (CA001), requires MFA (CA002) and blocks Microsoft admin portals from untrusted locations for privileged roles (CA007); a fail-closed validator ran against the baseline and against negative/malformed fixtures.
- Limitations: Synthetic fixtures only; no Entra tenant or Microsoft Graph was used, so nothing describes a real tenant's state. No VPN, remote desktop, third-party or customer remote access paths exist in the lab.
- Organizational dependencies (a real institution must supply): Remote access policy and approved methods; named-location (trusted network) ownership; third-party remote access agreements; break-glass account custody and review; licensing for Conditional Access features.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `identity/entra/policies/CA001-Block-Legacy-Authentication-All-Users.json` | `d302c99d9511` | #4 | synthetic CA policy |
| implementation | `identity/entra/policies/CA007-Block-Admin-Portals-From-Untrusted-Locations.json` | `d302c99d9511` | #4 | synthetic CA policy |
| implementation | `identity/entra/ca_validator.py` | `d302c99d9511` | #4 | fail-closed validator |
| evidence | `evidence/entra/runs/local-offline-20261028T150359Z/SUMMARY.md` | `d302c99d9511` | #4 | offline run summary (PASS; tenant state claimed: false) |
| evidence | `evidence/entra/runs/local-offline-20261028T150359Z/logs/04_validate_baseline_policies.log` | `d302c99d9511` | #4 | validator output for baseline policies |

### AIO-05 - V.B.1 Network - **SIMULATION**

- Source: AIO booklet (June 2021) section V.B.1, p. 51; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: CDK VPC with PRIVATE_ISOLATED subnets only (no IGW/NAT/public subnets), restricted default security group, app/db security groups without 0.0.0.0/0, and VPC flow logs to a KMS-encrypted log group. Synthesized and unit-tested offline.
- Limitations: Never deployed; no traffic, routing or reachability was observed. Isolated subnets mean no ingress or egress path for an application has been designed yet. No firewalls, IDS/IPS, DNS or load balancers are modelled.
- Organizational dependencies (a real institution must supply): Network architecture ownership; network diagram and segmentation/trust-level standard; firewall rule review process; network monitoring staffing; connectivity agreements with providers.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/aws-cdk/lib/network-database-stack.ts` | `099479e6d239` | #5 | VPC / security groups / flow logs |
| test | `infra/aws-cdk/test/network-database-stack.test.ts` | `099479e6d239` | #5 | VPC isolation and SG tests |
| evidence | `evidence/aws/aws-remediation-vpc-rds/logs/08-pass3-jest.log` | `099479e6d239` | #5 | jest run log |
| evidence | `evidence/aws/aws-remediation-vpc-rds/synth/BankItLabNetworkDatabase.template.json` | `099479e6d239` | #5 | synthesized template |

### AIO-06 - V.C.2(a) Open Source Software - **STATIC**

- Source: AIO booklet (June 2021) section V.C.2(a), p. 59; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Open source dependencies are pinned through committed package-lock.json files; an ADR records the decision to pin cdk-nag 2.x; parliament findings are gated through a documented allowlist with sources.
- Limitations: No software composition analysis, license review or vulnerability scan of dependencies was run (npm ci is invoked with --no-audit in the recorded commands). No inventory of approved open source components.
- Organizational dependencies (a real institution must supply): Open source acceptable-use policy and approval workflow; license review responsibility; dependency vulnerability monitoring and patch SLAs; software inventory.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| documentation | `infra/aws-cdk/docs/adr/ADR-0001-cdk-nag-2x-pin.md` | `e494bcfc3986` | #1 | dependency pin decision |
| implementation | `infra/aws-cdk/package-lock.json` | `099479e6d239` | #5 | pinned npm dependency tree |
| implementation | `infra/orgs/package-lock.json` | `e5e7f4604597` | #6 | pinned npm dependency tree |
| implementation | `infra/orgs/parliament-allowlist.json` | `e5e7f4604597` | #6 | allowlisted tool findings with sources |

### AIO-07 - VI.A.2 Authorization Boundary - **SIMULATION**

- Source: AIO booklet (June 2021) section VI.A.2, p. 69; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Credential-free AWS Organizations reference: OU layout and service control policies (e.g., region lock, deny leaving the organization) exported to JSON, linted and unit-tested; synthesized offline.
- Limitations: Never applied to any AWS Organization. The offline SCP evaluator is not AWS's policy engine (stated in evidence/orgs/README.md). No ITAM inventory exists to anchor boundaries to real assets.
- Organizational dependencies (a real institution must supply): Definition of system authorization boundaries tied to an IT asset inventory; account/OU ownership; approval authority for SCP changes; validation in a sandbox organization before adoption.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/orgs/lib/ou-layout.ts` | `e5e7f4604597` | #6 | OU layout |
| implementation | `infra/orgs/lib/scps.ts` | `e5e7f4604597` | #6 | SCP source |
| evidence | `evidence/orgs/policies/region-lock.json` | `e5e7f4604597` | #6 | exported SCP |
| evidence | `evidence/orgs/policies/deny-leave-organization.json` | `e5e7f4604597` | #6 | exported SCP |
| evidence | `evidence/orgs/logs/06-jest.log` | `e5e7f4604597` | #6 | jest 49/49 per evidence/orgs/README.md |
| evidence | `evidence/orgs/logs/08-cdk-synth.log` | `e5e7f4604597` | #6 | synth log |

### AIO-08 - VI.A.3 Identity and Access Management - **SIMULATION**

- Source: AIO booklet (June 2021) section VI.A.3, p. 69; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/vi-operations/via-operational-controls/via3-identity-and-access-management/ (retrieved 2026-10-28).
- Lab claim: Offline Conditional Access policies requiring MFA for all users and phishing-resistant MFA for privileged roles, with break-glass exclusions enforced by the validator; an SCP denying root-user actions; KMS key policies built by a least-privilege helper with tests for no wildcard principals.
- Limitations: Synthetic identities and fixtures; no tenant, no AWS account, no real users. Joiner/mover/leaver, access reviews and privileged access management are not modelled.
- Organizational dependencies (a real institution must supply): IAM policy and standards; identity lifecycle tied to HR events; periodic access recertification; privileged access approval and monitoring; break-glass procedures and custody.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `identity/entra/policies/CA002-Require-MFA-All-Users.json` | `d302c99d9511` | #4 | synthetic CA policy |
| implementation | `identity/entra/policies/CA003-Require-Phishing-Resistant-MFA-Admin-Roles.json` | `d302c99d9511` | #4 | synthetic CA policy |
| implementation | `identity/entra/baseline.json` | `d302c99d9511` | #4 | break-glass and privileged-role baseline |
| implementation | `infra/aws-cdk/lib/least-privilege-key.ts` | `099479e6d239` | #5 | KMS key policy helper |
| evidence | `evidence/orgs/policies/deny-root-user.json` | `e5e7f4604597` | #6 | exported SCP |
| evidence | `evidence/entra/runs/local-offline-20261028T150359Z/logs/03_unit_tests.log` | `d302c99d9511` | #4 | validator unit tests output |
| evidence | `evidence/entra/runs/local-offline-20261028T150359Z/validation-report.json` | `d302c99d9511` | #4 | validator report |
| evidence | `evidence/orgs/logs/10-lint-policies.log` | `e5e7f4604597` | #6 | SCP lint output |

### AIO-09 - VI.B.2 Configuration Management - **SIMULATION**

- Source: AIO booklet (June 2021) section VI.B.2, p. 72; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Infrastructure is defined as code; configuration baselines are checked by cdk-nag (AwsSolutions and NIST 800-53 R5 rule packs), static guards and negative-control tests; suppressions are limited to a register of proposed exceptions; evidence bundles carry SHA256SUMS.
- Limitations: Checks evaluate synthesized templates, not deployed resources; no drift detection. The four exceptions (EX-01..EX-04) are PROPOSED and unapproved. Rule packs are tool checks, not an approved institutional baseline.
- Organizational dependencies (a real institution must supply): Configuration management policy; approved secure configuration baselines; exception/risk-acceptance authority; drift monitoring and remediation ownership.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/aws-cdk/lib/guards.ts` | `099479e6d239` | #5 | static template guards |
| test | `infra/aws-cdk/test/negative-controls.test.ts` | `099479e6d239` | #5 | negative-control tests |
| evidence | `evidence/aws/aws-remediation-vpc-rds/cdk-nag/AwsSolutions--BankItLabNetworkDatabase-NagReport.csv` | `099479e6d239` | #5 | cdk-nag AwsSolutions report |
| evidence | `evidence/aws/aws-remediation-vpc-rds/logs/09-pass3-cdk-synth.log` | `099479e6d239` | #5 | synth with nag (exit 0) |
| evidence | `evidence/aws/aws-remediation-vpc-rds/SHA256SUMS` | `099479e6d239` | #5 | evidence bundle hashes |
| documentation | `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` | `099479e6d239` | #5 | EX-01..EX-04 PROPOSED |
| evidence | `evidence/orgs/logs/14-cdk-nag-gate.log` | `e5e7f4604597` | #6 | cdk-nag gate output |

### AIO-10 - VI.B.4 Backup and Replication Processes (logical Postgres backup/restore exercise) - **SIMULATION**

- Source: AIO booklet (June 2021) section VI.B.4, p. 75; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/vi-operations/vib-it-operational-processes/vib4-backup-and-replication-processes/ (retrieved 2026-10-28).
- Lab claim: A scripted pg_dump/pg_restore exercise with fingerprint comparison and negative tests (truncated dump, garbage archive, missing database, FK enforcement, restore over existing objects, tamper detection) ran in GitHub Actions run 40741329107 against an ephemeral PostgreSQL service container and offline, with PASS results and a verifier. An earlier failing run is preserved and marked historical/invalid.
- Limitations: Synthetic seed data on ephemeral CI/sandbox databases; not a production system or backup media. Dumps are gitignored; the CI copies live only in workflow artifacts with limited retention, so ARTIFACTS.sha256 cannot be re-verified from the repo alone. No backup schedule, media inventory, off-site copy or encryption of dumps is exercised.
- Organizational dependencies (a real institution must supply): Backup policy and methodology per system criticality; backup schedules and adherence monitoring; media inventory, off-site storage and access controls; restore testing cadence and sign-off; validation of CSP-performed backups.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `tests/integration/postgres/run_restore_scenario.sh` | `e7399fbb5385` | #2 | restore scenario harness (v2) |
| implementation | `tests/integration/postgres/verify_evidence.py` | `e7399fbb5385` | #2 | run verifier |
| implementation | `.github/workflows/postgres-restore-evidence.yml` | `e7399fbb5385` | #2 | CI workflow |
| evidence | `evidence/postgres/runs/INDEX.md` | `e7399fbb5385` | #2 | run index with CURRENT vs HISTORICAL status |
| evidence | `evidence/postgres/runs/ci-service-40741329107-1/SUMMARY.md` | `e7399fbb5385` | #2 | CI service-container run summary |
| evidence | `evidence/postgres/runs/ci-service-40741329107-1.ci-console/scenario-console.log` | `e7399fbb5385` | #2 | captured CI console output |
| evidence | `evidence/postgres/runs/ci-offline-40741329107-1/SUMMARY.md` | `e7399fbb5385` | #2 | CI offline-mode run summary |
| documentation | `evidence/postgres/runs/ci-service-40630856041-1/NOTE.md` | `e7399fbb5385` | #2 | preserved earlier failing run (historical / known invalid) |

### AIO-11 - VI.B.4 Backup and Replication Processes (AWS-native RDS backups) - **NOT_EXECUTED**

- Source: AIO booklet (June 2021) section VI.B.4, p. 75; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/vi-operations/vib-it-operational-processes/vib4-backup-and-replication-processes/ (retrieved 2026-10-28).
- Lab claim: An AWS Backup plan (CMK-encrypted vault, daily rule) and RDS automated backup retention of 14 days are defined in CDK and appear in the synthesized template.
- Limitations: No backup job, snapshot or restore has ever run: the stack was never deployed. EX-04 (AWS-managed backup service-role policy) is PROPOSED. A separate backup/aws work-in-progress directory seen in another local checkout is uncommitted and is not referenced here.
- Organizational dependencies (a real institution must supply): Same as AIO-10, plus AWS account ownership, vault access policy approval, and evidence of periodic restore tests from AWS Backup.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/aws-cdk/lib/network-database-stack.ts` | `099479e6d239` | #5 | AWS Backup plan + RDS backupRetention 14 days |
| documentation | `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` | `099479e6d239` | #5 | EX-04 PROPOSED |

### AIO-12 - VI.B.7 Log Management - **SIMULATION**

- Source: AIO booklet (June 2021) section VI.B.7, p. 77; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Reference log sources: S3 server access logging into a terminal log bucket that does not log to itself (ADR-0004), VPC flow logs and RDS log exports to KMS-encrypted CloudWatch log groups with 1-year retention, and an organization CloudTrail (multi-region, global service events, log file validation, KMS). Synthesized and nag-checked offline.
- Limitations: No logs were generated, collected, reviewed or retained because nothing was deployed. No log analysis, alerting, SIEM or review procedure exists. Retention values are lab choices, not an approved retention schedule.
- Organizational dependencies (a real institution must supply): Log management policy and retention schedule (including legal/regulatory retention); log review staffing and escalation; SIEM/monitoring tooling; protection of log integrity and access to logs.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/aws-cdk/lib/network-database-stack.ts` | `099479e6d239` | #5 | flow logs + RDS log exports |
| implementation | `infra/aws-cdk/lib/secure-storage-stack.ts` | `099479e6d239` | #5 | S3 server access logging |
| documentation | `infra/aws-cdk/docs/adr/ADR-0004-no-self-logging-log-sink.md` | `099479e6d239` | #5 | log sink decision |
| implementation | `infra/orgs/lib/org-cloudtrail-stack.ts` | `e5e7f4604597` | #6 | organization CloudTrail |
| evidence | `evidence/orgs/synth/BankItLabOrgCloudTrail.template.json` | `e5e7f4604597` | #6 | synthesized template |
| evidence | `evidence/orgs/cdk-nag/AwsSolutions--BankItLabOrgCloudTrail-NagReport.csv` | `e5e7f4604597` | #6 | cdk-nag report |
| evidence | `evidence/aws/aws-remediation-vpc-rds/synth/BankItLabSecureStorage.template.json` | `099479e6d239` | #5 | synthesized template |

### AIO-13 - VI.D.1 Monitoring and Reporting - **SIMULATION**

- Source: AIO booklet (June 2021) section VI.D.1, p. 84; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Delegated-admin reference stack for GuardDuty (detector with protection plans) and Security Hub (FSBP and CIS 3.0.0 standards, finding aggregator, central configuration). Synthesized and unit-tested offline; known coverage gaps documented in ADR-0002.
- Limitations: No findings, metrics or reports were produced. GuardDuty org auto-enable/delegated admin has no CloudFormation resource (ADR-0002). No reporting to senior management or stakeholders exists.
- Organizational dependencies (a real institution must supply): Operations monitoring program; defined reports/KPIs and audience; periodic reporting to senior management; finding triage and remediation ownership.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/orgs/lib/security-services-stack.ts` | `e5e7f4604597` | #6 | GuardDuty / Security Hub reference |
| documentation | `infra/orgs/docs/adr/ADR-0002-delegated-admin-coverage.md` | `e5e7f4604597` | #6 | coverage gaps |
| evidence | `evidence/orgs/synth/BankItLabSecurityServices.template.json` | `e5e7f4604597` | #6 | synthesized template |
| evidence | `evidence/orgs/logs/06-jest.log` | `e5e7f4604597` | #6 | jest output |

### AIO-14 - VII.A.5(a) Access Control Considerations - **SIMULATION**

- Source: AIO booklet (June 2021) section VII.A.5(a), p. 92; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Cloud access-control guardrails expressed as SCPs (protect security services, require encryption, deny public S3) and admin-portal location restriction in Conditional Access; SCPs exported, linted in-repo and with parliament (gated, allowlisted with sources).
- Limitations: Guardrails were never attached to a real organization or tenant. Linting is static; parliament raw output had 2 findings allowlisted as false positives. The shared-responsibility split with the CSP is not documented in the repo.
- Organizational dependencies (a real institution must supply): Cloud access control standard; CSP shared-responsibility review and contract terms; approval of guardrail changes; periodic review of exceptions/allowlists.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `infra/orgs/lib/scps.ts` | `e5e7f4604597` | #6 | SCP source |
| implementation | `infra/orgs/lib/scp-evaluator.ts` | `e5e7f4604597` | #6 | offline SCP evaluator (not AWS's engine) |
| evidence | `evidence/orgs/policies/protect-security-services.json` | `e5e7f4604597` | #6 | exported SCP |
| evidence | `evidence/orgs/policies/require-encryption.json` | `e5e7f4604597` | #6 | exported SCP |
| evidence | `evidence/orgs/policies/deny-public-s3.json` | `e5e7f4604597` | #6 | exported SCP |
| evidence | `evidence/orgs/lint/scp-lint-report.json` | `e5e7f4604597` | #6 | in-repo lint report |
| evidence | `evidence/orgs/logs/13-parliament-gated.log` | `e5e7f4604597` | #6 | parliament gated output |
| implementation | `identity/entra/policies/CA007-Block-Admin-Portals-From-Untrusted-Locations.json` | `d302c99d9511` | #4 | synthetic CA policy |

### AIO-15 - III.E Oversight of Third-Party Service Providers - **SIMULATION**

- Source: AIO booklet (June 2021) section III.E, p. 37; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Vendor-risk templates (assessment, RACI), a filled example for a fictional vendor, a core-banking vendor outage escalation tabletop scenario, and a governance lint (one Accountable per RACI row, required sections, contract placeholders, no invented vendor SLA numbers) that ran with positive and negative cases offline.
- Limitations: Fictional vendor only; no real contract, SLA, SOC report or due-diligence file was reviewed. The tabletop is a written scenario that was linted, not conducted with participants. Control questions are lab placeholders, not AICPA or FFIEC text.
- Organizational dependencies (a real institution must supply): Third-party risk management program; vendor inventory and criticality tiering; contract and SLA review (including data destruction terms); review of independent audit/assurance reports; vendor relationship owners; exit and escalation plans approved by management.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `governance/vendor-risk/check_governance.py` | `88a37856da05` | #9 | governance lint |
| documentation | `governance/vendor-risk/raci-matrix-template.md` | `88a37856da05` | #9 | RACI template |
| documentation | `governance/vendor-risk/examples/acme-core-ledger-SIMULATION-assessment.md` | `88a37856da05` | #9 | fictional vendor assessment |
| documentation | `governance/vendor-risk/scenarios/core-banking-vendor-outage-SIMULATION.md` | `88a37856da05` | #9 | written tabletop scenario |
| test | `governance/vendor-risk/tests/test_check_governance.py` | `88a37856da05` | #9 | lint unit tests |
| evidence | `evidence/vendor/runs/local-offline-20261028T180914Z/SUMMARY.md` | `88a37856da05` | #9 | offline run summary (PASS) |
| evidence | `evidence/vendor/runs/local-offline-20261028T180914Z/logs/06_governance_lint.log` | `88a37856da05` | #9 | lint output |
| evidence | `evidence/vendor/runs/local-offline-20261028T180914Z/logs/09_neg_governance_lint_two_accountable.log` | `88a37856da05` | #9 | negative case output |

### AIO-16 - VI.C.4 Event, Incident, and Problem Management - **STATIC**

- Source: AIO booklet (June 2021) section VI.C.4, p. 82; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Synthetic operations material: ticket priority definitions (impact x urgency) with a triage exercise, an escalation matrix and an on-call model.
- Limitations: Documents only; nothing was executed, no tickets, incidents or problems exist, and all people, IDs and targets are invented (docs/management/DISCLAIMER.md). docs/runbooks/** has not been delivered on any branch.
- Organizational dependencies (a real institution must supply): Incident response and problem management policy; staffed on-call rotation; incident classification approved by management; regulatory and customer notification procedures; post-incident review ownership; ticketing system of record.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| documentation | `docs/management/ticket-priority.md` | `9dc8f1f587a6` | #13 | synthetic priority definitions and triage exercise |
| documentation | `operations/team/escalation-matrix.md` | `9dc8f1f587a6` | #13 | synthetic escalation matrix |
| documentation | `operations/team/on-call.md` | `9dc8f1f587a6` | #13 | synthetic on-call model |
| documentation | `docs/management/DISCLAIMER.md` | `9dc8f1f587a6` | #13 | synthetic-data disclaimer |

### AIO-17 - VI.D.1 Monitoring and Reporting (host health collector) - **SIMULATION**

- Source: AIO booklet (June 2021) section VI.D.1, p. 84; https://ithandbook.ffiec.gov/it-booklets/architecture-infrastructure-and-operations/ (retrieved 2026-10-28).
- Lab claim: Stdlib-only host health collector with bounded synthetic probes and a fail-closed decision; its unit tests and 13 recorded fixtures (healthy, unhealthy, stale, timeout, malformed payloads) were evaluated offline with a fixed clock and every result matched the expected outcome.
- Limitations: Offline fixtures and fake transports only; no real host or endpoint was monitored and no alerting or reporting path exists. Does not cover reporting to senior management.
- Organizational dependencies (a real institution must supply): Monitoring tooling ownership; defined health thresholds and alert routing; operations reports and KPIs for senior management and stakeholders; periodic review of monitoring value.

| Role | Path | Commit | PR | Note |
|---|---|---|---|---|
| implementation | `observability/healthcheck/decision.py` | `3e40e39d73da` | #10 | fail-closed decision |
| implementation | `observability/healthcheck/collector.py` | `3e40e39d73da` | #10 | host collector |
| test | `observability/tests/test_decision.py` | `3e40e39d73da` | #10 | decision tests |
| evidence | `evidence/observability/runs/local-offline-20261028T180832Z/SUMMARY.md` | `3e40e39d73da` | #10 | offline run summary (PASS) |
| evidence | `evidence/observability/runs/local-offline-20261028T180832Z/logs/02_unit_tests.log` | `3e40e39d73da` | #10 | unit test output |
| evidence | `evidence/observability/runs/local-offline-20261028T180832Z/logs/12_fixture_stale.log` | `3e40e39d73da` | #10 | stale-fixture evaluation output |

## AIO topics not mapped (no relevant artifact in the repo)

Reviewed and left out of the table because no committed artifact relates to them. They are gaps for the lab, and most depend
mainly on the organization. See [`evidence/control-review/review-notes.md`](../../evidence/control-review/review-notes.md).

| AIO section (booklet p.) | Why not mapped |
|---|---|
| II.A-II.F Governance (pp. 3-14), incl. II.C Policies, Standards, and Procedures (p. 11) | No approved policies, standards or procedures, board/senior-management reporting, or role definitions for a real entity |
| II.D Internal Audit, Independent Reviews, and Certification Processes (p. 12) | PR #3 is an engineering peer review, not internal audit or an independent review function |
| III.A.1 Data Identification and Classification (p. 16) | No data inventory or classification scheme; all data is synthetic |
| III.B IT Asset Management (pp. 22-27) | No hardware/software inventory, end-of-life tracking or shadow IT process |
| III.C.1 Network Diagrams (p. 30), III.C.2 Data Flow Diagrams (p. 31) | No diagrams committed; network shape exists only as CDK code |
| VII.A.4 Shared Responsibilities (p. 90) | No shared-responsibility matrix for AWS, Microsoft or GitHub |
| VI.B.3 Vulnerability and Patch Management (pp. 73-74) | No vulnerability scanning or patch process; `npm ci` runs with `--no-audit`; RDS `autoMinorVersionUpgrade` is a setting, not a process |
| VI.B.8 Disposal of Data and Media (p. 78) | No sanitization or disposal procedure |
| V.D Environmental Controls (pp. 63-65), V.E Physical Access Controls (p. 66), VI.A.1 Operating Centers (p. 68) | Not applicable to an IaC-only lab; in a cloud deployment these are CSP-performed and would need third-party oversight evidence |
| IV Architecture (pp. 43-48) | No architecture plan or enterprise architecture documents beyond ADRs scoped to individual stacks |

## Limitations

1. **Lab, not a bank.** No regulated entity, customer data, production system, or real tenant or account is involved. All
   identities, vendors, people, tickets and data are synthetic or fictional.
2. **Not an exam opinion.** Mapping a topic to an artifact means only that the artifact is relevant to the topic. It does not
   mean the artifact covers everything the booklet discusses for that topic, and it is not an assessment of adequacy.
3. **No live evidence.** OBSERVED count is 0. Nothing was deployed to AWS or applied to Entra ID; every AWS and Entra row
   describes definitions checked offline.
4. **Unmerged work.** All referenced artifacts are on open draft PRs, pinned to specific SHAs. They may change or be rejected.
5. **Proposed exceptions.** EX-01..EX-04 in PR #5 are PROPOSED and unapproved; a lab has no risk-acceptance authority.
6. **Tool rule packs are not institutional baselines.** cdk-nag AwsSolutions / NIST 800-53 R5 and parliament are tool checks.
7. **Page numbers** come from a third-party copy of the PDF (S6) and should be re-checked against the official PDF (S5).
8. **Selected topics only.** Rows were chosen where a committed artifact exists; the "not mapped" list is not an exhaustive
   gap analysis of the booklet or of Appendix A examination procedures.
