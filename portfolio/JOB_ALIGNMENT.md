# Job alignment: IT Manager (AMS Technology Solutions posting)

This file maps each requirement of the target role to evidence in the five [case studies](README.md). It complements the lab's own matrix: that matrix covers the lab's artifacts, and this file covers the case-study projects. A requirement marked **Gap** here may still be covered by lab work, and the reverse is also true.

## Source of the requirements

- **Requirement IDs and wording:** [`docs/JOB_REQUIREMENTS_MATRIX.md`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/31b69db90838f59bfe28f8214dfc51a1c4ffd429/docs/JOB_REQUIREMENTS_MATRIX.md) on branch `job-requirements-matrix` (draft PR [#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12), commit [`31b69db`](https://github.com/onnxscibroccoli/bank-it-operations-lab/commit/31b69db90838f59bfe28f8214dfc51a1c4ffd429)). This file reuses its IDs (A1–D4) unchanged.
- **Posting:** "Information Technology Manager", AMS Technology Solutions LLC, Boston (MA), Hybrid, USD 120,000–190,000 ([JobLeads](https://www.jobleads.com/us/job/information-technology-manager--boston--e57b1e5ed0b5b152dff0ddd60c8e955b2)). The page was re-read on 2026-10-28, and its requirement text matches the matrix. No requirement was added, removed, or reworded beyond light shortening.

## Legend and honesty rules

- **Strong:** a case study cites a verified artifact (a file, commit, PR, or Actions run) that shows the core of the requirement in a running or executed system.
- **Partial:** some of the requirement is shown, or the evidence is design or code only, or it rests on a project's own record of a live event that wasn't re-observed here. A material part is missing.
- **Gap:** no case-study evidence.

**Caveats that apply to every row:**

1. **Personal projects only.** All five are personal projects in the `onnxscibroccoli` account. None of them is evidence of employment, tenure, team size, or employer-scale operations.
2. **AI-agent involvement.** Much of the work was produced by AI coding agents working in these repositories under the owner's direction. Examples:
   - Helix branch names such as `hugo/…` and `codex/…`, and its `claude-self-correct.yml` workflow
   - CivicPatch PRs merged by `app/github-actions`, such as [#18](https://github.com/onnxscibroccoli/civicpatch/pull/18)
   - CivicPatch's first commit, "Export from Grok"
   
   The evidence shows systems that were designed, directed, operated, and documented in these accounts. It does **not** show that the owner hand-wrote each change. Say so in an interview, and be ready to walk through any cited artifact yourself.
3. **Self-recorded live events.** "Live" events (incidents, production observations) are the project's own records, dated in late September and October 2026. They were not re-observed for this file.

## A. Key requirements

| # | Requirement (from matrix) | Status | Case-study evidence | What is missing |
|---|---|---|---|---|
| A1 | 70–80% hands-on senior engineering; "comfortable logging into consoles and actively troubleshooting issues" | **Strong** | Helix OOM incident [`docs/incidents/2026-10-06-kali-oom-recovery.md`](https://github.com/onnxscibroccoli/helix/blob/8f687036344e1c09c592b9fbfb9f8036b07614c0/docs/incidents/2026-10-06-kali-oom-recovery.md): host diagnosed over SSM while the desktop tool timed out, kernel OOM logs collected, guest recovered. CPU exhaustion recovery: [helix#62](https://github.com/onnxscibroccoli/helix/pull/62). Read-only production investigation: Grasshopper [`docs/PRODUCTION_LIVE_EVIDENCE.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_LIVE_EVIDENCE.md) ([Helix](helix.md), [Grasshopper](grasshopper.md)) | Personal single-host AWS environment, not an employer's estate. See caveat 2 on authorship |
| A2 | Hybrid background: on-prem (Windows servers, networks, firewalls, helpdesk), then cloud over 4–5 years | **Gap** | None. The projects date from July–October 2026 (earliest repo created 2026-07-18) | Career history. No Windows, firewall, or helpdesk content |
| A3 | "Strong experience with AWS is critical"; about 25 standard services | **Partial** | A live AWS environment is documented: EC2 KVM host, Multi-AZ RDS PostgreSQL with KMS encryption and Secrets Manager rotation, an SSM-managed host, IAM instance-role scoping, and CloudFront at the edge. Sources: Grasshopper [`PRODUCTION_LIVE_EVIDENCE.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_LIVE_EVIDENCE.md), [`PRODUCTION_CONTRACT_INVENTORY.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_CONTRACT_INVENTORY.md), [`ARCHITECTURE_VERIFICATION_2026-09-29.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/ARCHITECTURE_VERIFICATION_2026-09-29.md). IaC: Helix CDK [#49](https://github.com/onnxscibroccoli/helix/pull/49) and Terraform [`infra/terraform/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/infra/terraform) | Roughly 8–10 services are evidenced, not ~25. Single account. No Lambda, load balancers, VPN, Route 53, or cost tooling found |
| A4 | Operationalizing AWS from scratch (preferred) | **Partial** | Reproducible fresh-account bootstrap [helix#47](https://github.com/onnxscibroccoli/helix/pull/47), executable CDK trust bootstrap [#48](https://github.com/onnxscibroccoli/helix/pull/48), immutable bootstrap checkout [#32](https://github.com/onnxscibroccoli/helix/pull/32) | One workload, not an enterprise landing zone. Sandbox-account isolation PRs [#53](https://github.com/onnxscibroccoli/helix/pull/53) and [#55](https://github.com/onnxscibroccoli/helix/pull/55) are open and unmerged |
| A5 | Oversee a team of 8–10 | **Gap** | None. Directing AI agents is not people management and is not presented as such | Real supervisory history |
| A6 | Financial/banking experience (plus) | **Gap** | None. CivicPatch is a civic, not financial, product | Industry tenure |

## B. Responsibilities

| # | Requirement | Status | Case-study evidence | What is missing |
|---|---|---|---|---|
| B1 | Lead, coach, and develop IT staff | **Gap** | None | People leadership |
| B2 | Hands-on admin of servers, networks, endpoints, virtualization, firewalls, VPN, identity, SaaS, banking apps | **Partial** | Virtualization: libvirt/QEMU/KVM guest lifecycle in Helix ([`production/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/production), incident above). Linux servers and systemd: Helix [`ops/systemd/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/ops/systemd). Identity: OIDC sign-in in Helix (repo description: "Google/X OIDC"). Android endpoint automation: Broccoli Core ([`tools/android_transport.py`](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/tools/android_transport.py)) | No firewalls, VPN, Windows, SaaS administration, or banking applications |
| B3 | AWS architecture, secure configuration, access management, monitoring, cost, availability, scalability, backup, resilience | **Partial** | Design: helix#49 (VPC, isolated DB subnets, gateway-only SG, encrypted Multi-AZ PostgreSQL, backups, IAM DB auth). Findings on the live system: an over-broad DB role and 1-day backup retention ([`PRODUCTION_SECURITY_HARDENING.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_SECURITY_HARDENING.md)). Scoped inline IAM policy with deny checks ([`PRODUCTION_CONTRACT_INVENTORY.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_CONTRACT_INVENTORY.md)) | No AWS cost controls or autoscaling. Hardening items are recorded as **open**. Whether #49 was ever deployed is unknown |
| B4 | Automation: scripting, workflow automation, API integrations, CI/CD, IaC | **Strong** | CivicPatch's bounded Actions state machine, verified by named runs on 2026-10-17 ([`docs/AGENT-HANDOVER.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/AGENT-HANDOVER.md); runs confirmed successful, see [CivicPatch](civicpatch.md)). Grasshopper: 18 workflows. Helix: Terraform, CDK, and Ansible validation workflows. OmniKali: hourly health-probe workflow | No PowerShell. No ticketing or ITSM automation |
| B5 | Monitor systems, backups, and dashboards; assign, escalate, document, resolve | **Partial** | Automated fail-closed health probing ([`probe-endpoint.mjs`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/.github/scripts/probe-endpoint.mjs)). 30-second host memory guard as a systemd timer ([`ops/systemd/omnikali-memory-guard.timer`](https://github.com/onnxscibroccoli/helix/blob/8f687036344e1c09c592b9fbfb9f8036b07614c0/ops/systemd/omnikali-memory-guard.timer)). CI failure observatory ([Grasshopper#193](https://github.com/onnxscibroccoli/Grasshopper/pull/193)) | No alerting, dashboards, ticket assignment, or on-call. Host memory alarms are listed as follow-up in the OOM incident |
| B6 | Vendor management, including Jack Henry | **Gap** | None | Vendor relationships |
| B7 | Lead projects, migrations, and integrations through post-implementation | **Partial** | Helix production reconstruction (142 commits, 27 merged PRs). CivicPatch handover with operator controls and rollback ([`AGENT-HANDOVER.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/AGENT-HANDOVER.md)) | Solo personal projects with no stakeholders or business owners |
| B8 | Operational updates to leadership during incidents and projects | **Partial** | Structured incident write-ups (impact, evidence, root cause, recovery, follow-up) in [`helix/docs/incidents/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/docs/incidents). Handoff records: [Grasshopper#198](https://github.com/onnxscibroccoli/Grasshopper/pull/198) | Written engineering records, not updates delivered to a live audience |
| B9 | Support audits; produce evidence; track remediation to completion | **Partial** | Evidence-first records that withhold secrets: migration files reconciled to the live ledger by SHA-256 ([`PRODUCTION_LIVE_EVIDENCE.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_LIVE_EVIDENCE.md)), executor provenance ([`PRODUCTION_EXECUTOR_PROVENANCE.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_EXECUTOR_PROVENANCE.md)), and a 12-step remediation evidence plan ([`PRODUCTION_SECURITY_HARDENING.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_SECURITY_HARDENING.md)). Broccoli Core PR [#77](https://github.com/onnxscibroccoli/broccoli-core/pull/77) lists what it does **not** claim | No external audit or exam. Remediation is still open, not tracked to completion |
| B10 | Review security alerts and vulnerability findings; remediate and prevent | **Partial** | Least-privilege and credential-handling findings with a required remediation contract (Grasshopper hardening doc). Private/loopback endpoint rejection ([omnikali#2](https://github.com/onnxscibroccoli/omnikali/pull/2)). Private-network redirect rejection, folded into [civicpatch#14](https://github.com/onnxscibroccoli/civicpatch/pull/14). Pages deploy-token isolation ([civicpatch#19](https://github.com/onnxscibroccoli/civicpatch/pull/19)) | No SIEM, EDR, or vulnerability scanner. No GuardDuty or Security Hub |
| B11 | Documentation: diagrams, configurations, inventories, runbooks, escalation, checklists | **Partial** | Text architecture paths (Helix README; Grasshopper [`ARCHITECTURE_VERIFICATION_2026-09-29.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/ARCHITECTURE_VERIFICATION_2026-09-29.md)). Service inventory ([`PRODUCTION_CONTRACT_INVENTORY.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_CONTRACT_INVENTORY.md)). Runbook-style operator controls (CivicPatch handover). Agent contracts ([`omnikali/.github/agents/`](https://github.com/onnxscibroccoli/omnikali/tree/a5faf9b82bedb0057cb3164bebf190bfa199b446/.github/agents)) | No network diagrams, vendor contacts, or operational checklists |
| B12 | Monitoring, capacity planning, patching, lifecycle, cost | **Partial** | A capacity decision from incident evidence: the 4 GiB host is below the safe envelope, with a planned move to 8 GiB during a maintenance window (Helix OOM incident). CI runner-minute budget analysis ("1,860 minutes covers the worker only", CivicPatch handover) | No patching or lifecycle artifacts. No AWS cost management |
| B13 | Technical leadership in complex incidents: RCA, corrective actions, preventive controls, lessons learned | **Strong** | Helix 2026-10-06 SEV-1 OOM incident: root cause (resource overcommit), corrective steps, and a preventive control committed as code: [`ops/omnikali-memory-guard.sh`](https://github.com/onnxscibroccoli/helix/blob/8f687036344e1c09c592b9fbfb9f8036b07614c0/ops/omnikali-memory-guard.sh), with service and timer units in commits `faab1d8`, `c348007`, and `8f68703`. Also helix#62 (CPU exhaustion) | Single-operator incidents on personal infrastructure, with no incident-command or stakeholder dimension |
| B14 | Staff meetings, project checkpoints, operational reviews | **Gap** | None | Real examples only |
| B15 | DR, business continuity, backup validation, incident response, resilience | **Partial** | Failure-injection scenarios in Grasshopper: worker termination, stale lease, gateway restart, network interrupt, DB failure, and duplicate fencing ([`scripts/live-acceptance/scenarios/`](https://github.com/onnxscibroccoli/Grasshopper/tree/3eef009aa4a88f6d81dbd082cd35b90379929518/scripts/live-acceptance/scenarios)). Multi-AZ RDS with deletion protection observed live. CivicPatch revert-based rollback | Per Grasshopper's README, off-host backup recovery is unproven. A working backup-credential read "has not been demonstrated" ([`PRODUCTION_CONTRACT_INVENTORY.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/PRODUCTION_CONTRACT_INVENTORY.md)). No DR plan or RTO/RPO |
| B16 | Complete required training and examinations | **Gap** | None | Not demonstrable |

## C. Knowledge, skills and abilities

| # | Requirement | Status | Case-study evidence | What is missing |
|---|---|---|---|---|
| C1 | Hands-on admin and troubleshooting across infrastructure, apps, endpoints, networks, cloud, and security tools | **Partial** | See A1, B2, B13 | Endpoints and network devices |
| C2 | Leading IT teams while technically engaged | **Gap** | None | People leadership |
| C3 | AWS: EC2, VPC, S3, IAM, RDS, Lambda, networking, LBs, VPN, DNS, monitoring, backup, cost, multi-account | **Partial** | EC2, VPC, IAM, RDS, Secrets Manager, KMS, SSM, CloudFront, and CloudWatch log exports (see A3) | S3 usage not verified. No Lambda, load balancers, VPN, DNS, or cost management. Multi-account work is limited to unmerged Helix PRs |
| C4 | Operationalizing enterprise AWS from scratch (plus) | **Partial** | Same as A4 | Same as A4 |
| C5 | PowerShell, Python, API integrations, job scheduling, configuration management, CloudFormation, CDK, CI/CD, CloudWatch, IaC | **Partial** | Python (Broccoli Core, CivicPatch). CDK (Helix [`infra/cdk/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/infra/cdk)). **Configuration management:** Ansible ([`infra/ansible/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/infra/ansible), `ansible-validation.yml`, [helix#50](https://github.com/onnxscibroccoli/helix/pull/50) SSM Ansible convergence). **Job scheduling:** cron dispatcher (CivicPatch, `19 2,8,14,20 * * *`) and a systemd timer (Helix). CI/CD in all five repos | **No PowerShell.** CloudFormation only through CDK |
| C6 | Microsoft 365, AD, Entra ID, IAM, endpoint management, conditional access | **Gap** | Only generic OIDC sign-in (Helix). No Microsoft identity content | All Microsoft identity items |
| C7 | Banking apps, core systems, SaaS, network gear, firewalls, VPN/WAN, virtualization, Windows, Linux, backup, monitoring | **Partial** | Virtualization (KVM/libvirt/QEMU) and Linux (Helix). Monitoring scripts (OmniKali, Helix) | Banking/core systems, network gear, firewalls, VPN/WAN, Windows |
| C8 | Linux admin: CLI, services, permissions, logs, packages, shell scripting | **Strong** | systemd service and timer units, kernel OOM log analysis, process containment, `virsh` guest control (Helix incident and `ops/`). Shell is Broccoli Core's second-largest language (~1.5 MB), e.g. [`lib/rish_run.sh`](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/lib/rish_run.sh) | Patching and package-management artifacts not found |
| C9 | Banking compliance, IR, vulnerability management, cloud governance, IAM, MFA, encryption, Security Hub, GuardDuty, backup/DR | **Partial** | Encryption at rest (KMS on RDS, observed live). Secrets Manager rotation. Least-privilege findings. Fail-closed gates throughout | No banking-regulation mapping. No MFA, GuardDuty, or Security Hub evidence |
| C10 | Documentation, procedures, runbooks, evidence packages, project plans, executive status | **Partial** | Evidence and provenance records (Grasshopper), incident write-ups (Helix), handover and runbook (CivicPatch) | No project plans or executive-level updates |
| C11 | Communication, vendor management, project management, customer service | **Gap** | None | Not demonstrable from repositories |
| C12 | Competing priorities, independent resolution, calm incident leadership | **Partial** | The incident records show independent diagnosis and resolution (see B13) | Calm leadership of people and handling competing priorities cannot be shown from repositories |

## D. Experience, education, certifications, conditions

| # | Requirement | Status | Note |
|---|---|---|---|
| D1 | 8+ years in IT (5+ progressive) | **Gap** | The projects span July–October 2026 and say nothing about years of experience |
| D2 | Bachelor's degree or equivalent | **Gap** | Not demonstrable |
| D3 | Certifications (preferred) | **Gap** | Not demonstrable. Never present portfolio work as a certification |
| D4 | Off-hours availability, travel, physical conditions | **Gap** | Candidate attestation only |

## Summary

| Status | Count | Rows |
|---|---|---|
| Strong | 4 | A1, B4, B13, C8 |
| Partial | 20 | A3, A4, B2, B3, B5, B7, B8, B9, B10, B11, B12, B15, C1, C3, C4, C5, C7, C9, C10, C12 |
| Gap | 14 | A2, A5, A6, B1, B6, B14, B16, C2, C6, C11, D1, D2, D3, D4 |

The matrix splits B15 into B15a and B15b; this file treats B15 as one row, so there are 38 rows here rather than the matrix's 39.

## Where the case studies add to the lab matrix

The lab matrix lists several items as **missing** that these projects help with, at the levels stated above:

- **Live AWS operations (lab: static only).** Observed live RDS, EC2, and SSM state, plus live incident recovery (Helix, Grasshopper).
- **Configuration management and job scheduling (lab: missing).** Ansible and SSM in Helix; cron and systemd timers in CivicPatch and Helix.
- **Virtualization (lab: missing).** KVM/libvirt/QEMU guest operations in Helix.
- **Incident RCA on a running system (lab: CI-harness defect only).** The Helix OOM incident.

The case studies do **not** help with PowerShell, Windows, Microsoft identity, firewalls, VPN, vendor management, people management, or banking experience.
