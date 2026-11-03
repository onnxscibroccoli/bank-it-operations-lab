# Portfolio delivery report

PR #35 (`delivery/portfolio`) is a reviewable lab portfolio, not an accepted release. The registry reports **24/26 integrated, 27 total entries including one superseded entry**. The two remaining entries are the legacy acceptance slice and external review records; neither is silently counted as delivered. The owner-authentication entry is a verifier prototype, not an operational approval system.

## Delivered

The original integration baseline plus vendor simulation, observability, identity/vendor governance, control mapping, patch/hardening, hybrid runbooks, backup references, Organizations CDK and partial Terraform references, network-edge CDK, endpoint plan generation, and generated inventory/diagrams are assembled. Source provenance is retained in `coordination/modules.json`.

GitHub Actions runs bounded offline validation, CDK build/test/synth for base AWS, backup, Organizations and network-edge, Terraform provider-schema validation, PowerShell Pester behavior tests, and fresh PostgreSQL restore exercises with negative controls. Packaging requires all those jobs to succeed. Each artifact identifies its exact commit; consult that run's results rather than treating a prior green run as evidence for later commits. Workflows do not call paid model APIs or auto-merge.

The local owner-signature suite executes 15 tests, including real Ed25519 signatures, tampered payloads and binding mismatches. OpenSSL 3.x is required. The verifier always reports approvalEffective=false: no key is enrolled, no external signed-decision adapter is activated, and AC1 remains separate.

## Remaining engineering and acceptance limits

- Independent GitHub approval, reviewer enrollment, protected trusted-gate bootstrap/re-pinning and owner decisions remain outstanding. Candidate gate changes are not automatically trusted. A successful portfolio package does not make the integration gate eligible.
- Owner-signature activation still needs a reviewed adapter, trusted key enrollment, revocation and conflicting-decision semantics. Existing login-bound owner policy cannot be satisfied by inviting a second Admin to a personal repository. Do not follow historic instructions that request that.
- EX-04's AWS Backup role trust has an unverified vault SourceArn assumption during AssumeRole. It is a deployment blocker; static tests do not validate AWS runtime behavior. The exception remains proposed.
- Organizations Terraform is a partial reference, not feature parity with CDK and not an applied environment. Network AMI/application/VPN prerequisites and exception decisions remain deployment work.
- Endpoint PowerShell is executed by Pester in Linux CI as a plan generator. No domain-joined Windows execution or tenant mutation occurred.
- Legacy acceptance work and external review records are not integrated. Native independent-principal approval cannot be supplied by an agent using the author's account.

No live AWS, Entra, M365, Graph or banking-vendor system was changed. Incident/vendor data is synthetic. Hybrid runbooks and staff-management examples are NOT_EXECUTED. Costs use illustrative inputs. This portfolio does not establish employment history, banking tenure, regulatory compliance or production readiness.

## Handoff

Use README's credential-free quickstart and `docs/DEMO_WALKTHROUGH_15MIN.md`. Follow `reports/USER_ACTIONS_REQUIRED.md` for the human steps. PR #1 is closed as superseded; main and the old PR #7 review candidate are untouched. The original midnight target passed without an eligible merge; no deadline-completion claim is made.

## Completion pass, 2026-11-03 (13:25 EST)

All facts below come from GitHub API and Actions log checks on 2026-11-03 between 13:22 and 13:26 EST (UTC-5). Times from October 31 are given in EDT (UTC-4), which was still in effect then. This section adds to the record above and does not replace it. Nothing above was edited.

### Main and what merged since `7f50348`

- **`main` = `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6`.** It is the merge commit of [PR #35](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/35) (`delivery/portfolio` → `main`), merged by `onnxscibroccoli` on 2026-10-31 at 17:09 EDT. `main` is 71 commits ahead of `7f50348` and 0 behind. Its tree is identical to #35's head `aa6a38b` (compare: 0 files changed).
- **Merged** (state MERGED; all merged 2026-10-31 between 17:03 and 17:09 EDT, by `onnxscibroccoli`, through #35):
  - #35, which went to `main`;
  - #36, #37 and #38, which went into `delivery/portfolio`;
  - #7 (head `a9d0f64`), #2, #3, #4, #5, #20 and #22. These show as merged because their head commits are contained in `main`.
- **Closed, not merged:** #1, on 2026-10-29 (superseded by #5).
- **Still open:** #6, #8–#19, #21 and #23–#34. That includes this report's old PR #11 (head `d500ccf`) and the review-note PRs #14 and #27–#34.
- **PR #35 states the basis for the merge:** "The repository owner explicitly directed development integration before independent review on 2026-10-31. Independent review remains deferred and has not been represented as completed. This merge is development integration, not production approval."

### Actions runs on `main` at `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6` (post-merge verification)

| Workflow | Run | Event | Result |
|---|---|---|---|
| integration-gate | [41242239019](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242239019) | push | **failure**: 19 of 20 jobs succeed, including `final-summary`; `merge-eligibility` fails |
| aws-cdk | [41242238866](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242238866) | push | success |
| postgres-restore-evidence | [41242238836](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242238836) | push | success |
| offline-validation | [41242238892](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242238892) | push | success |
| Documentation knowledge base | [41242238902](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242238902), [41242873936](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242873936), [41243377081](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41243377081) | push, workflow_dispatch ×2 | success (`validate`, `deploy`). GitHub Pages is live at <https://onnxscibroccoli.github.io/bank-it-operations-lab/> |
| portfolio-validation | **no run at the `main` SHA** | — | The last runs were on #35's head `aa6a38b`, which has the same tree: [41242207712](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242207712) (push) and [41242212716](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242212716) (pull_request), both success. That counts as verification of the same tree, not a run on `main` |

The integration-gate run on `main` prints these lines:
- `MODULE COVERAGE: 25/27 integrated (92.6%), functional 18/19; denominator 28 (INTEGRATED=25, NOT_INTEGRATED=2, SUPERSEDED=1)`
- `USER ACTION REQUIRED: 3 — UA-2; UA-3; UA-7`

`merge-eligibility` ran the trusted gate `af49a27` and failed with `ERROR candidate: scripts/ci/… differs from the trusted manifest`. The files named are `provenance.py`, `reviews.py`, five gate tests, and three new portfolio scripts that are not in the manifest. **The gate never reached an ELIGIBLE decision for the merged code.** The merge happened outside the gate, on the owner's development-integration directive.

### Review, protection, exceptions, identity and decisions

| Item | Live evidence | State |
|---|---|---|
| Reviewer approvals | `GET /pulls/<n>/reviews` for every PR #1–#38 returns **0 reviews**. The only collaborator is `onnxscibroccoli` (admin), and there are no pending invitations | **No independent approval exists.** AC1/G1 were not met for the merged code |
| Branch protection / rulesets | `GET /branches/main/protection` → 404 "Branch not protected". `GET /branches/evidence%2Facceptance/protection` → 404. `GET /rulesets` → `[]`. `branches/main.protected = false` | **Unprotected** |
| Exception register on `main` (`evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md`) | "Status of every entry: **PROPOSED, pending owner approval.**" There are no per-entry status lines. EX-04 is now re-scoped: AwsSolutions-IAM5 `snapshot:awsbackup-*` on `DbBackupPolicy`, replacing the earlier IAM4 managed-policy form | **EX-01..EX-04 PROPOSED**; none approved. The conditional decisions Ian relayed on 2026-10-28 (§3 above) stay conditional. EX-04's scope changed after that relay, so the relayed EX-04 condition does not carry over automatically |
| Entra baseline | `evidence/entra/BASELINE-CHOICES-PENDING.md` on `main`: "**have not been confirmed by the owner**". PR #4 has 0 comments | **Pending** (UA-2) |
| Acceptance decision comments | All 11 issue and PR comments in the repo were read (10 on #7, 1 on #11; all by `onnxscibroccoli`). **None** begins with `ACCEPTANCE-DECISION` or `ACCEPTANCE-ATTESTATION`. Comments on #7 marked "Checkpoint only. Not a review, not an approval" are status notes. There are 0 inline review comments | **No recorded acceptance decision** |
| `coordination/tasks.json` on `main` | UA-1 NOT_YET_ACTIONABLE (exceptions; "effective approval awaits the final bound packet and reviewed owner-authentication path"). UA-2 OPEN. UA-3 OPEN. UA-4 RESOLVED (PR #1 closed). UA-5 NOT_YET_ACTIONABLE (AC6). UA-6 NOT_YET_ACTIONABLE (owner signing key). UA-7 OPEN (independent reviewer) | Matches the CI top line |

### Remaining human steps

**USER ACTION REQUIRED: 3 — UA-2 Entra baseline; UA-3 protect main and evidence/acceptance; UA-7 invite an independent reviewer.** This matches the integration-gate run on `main` ([41242239019](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41242239019)). Each item was checked live on 2026-11-03 at about 13:25 EST.

| ID | Action | Live evidence it is still open | How |
|---|---|---|---|
| **UA-2** | Confirm or change the lab's Entra CA baseline: risk policies report-only, device compliance on All users / All apps, 12 privileged roles | `BASELINE-CHOICES-PENDING.md` on `main` says not confirmed. PR #4 has 0 comments | Section 4 above |
| **UA-3** | Protect `main` and `evidence/acceptance` | Both return 404 "Branch not protected"; rulesets `[]` | Section 2 above. `main` now carries merged code, so protection affects every future change |
| **UA-7** | Invite a qualified independent human reviewer and give their exact GitHub username | Collaborators: only `onnxscibroccoli`; 0 invitations; 0 reviews on PRs #1–#38 | Section 1 above |

**Waiting, not yet actionable** (`tasks.json` on `main`; not counted):
- **UA-1:** EX-01..EX-04 are all PROPOSED on `main`. EX-04 was re-scoped after the 2026-10-28 relay, so Ian's earlier conditional decision on EX-04 needs a fresh look against the new scope. The gate says effective approval needs the bound packet and a reviewed owner-authentication path.
- **UA-5:** final human portfolio acceptance (AC6).
- **UA-6:** enroll an owner signing key after the activation design is reviewed.

**Facts to know, not actions:**
- The code is already on `main` without independent review, by Ian's 2026-10-31 development-integration directive.
- The gate on `main` reports `merge-eligibility` failing, because candidate gate files differ from the trusted manifest. That is engineering work for the integrator, not a user step.
- portfolio-validation has not run at the `main` SHA itself; it ran on the identical tree at `aa6a38b`.
