# Human decision packet, 2026-11-03

This packet sorts every remaining item into the owner's three-phase model and, within each phase, separates two kinds of item:

- **Owner:** an authenticated decision that only the repository owner or account holder can make.
- **Auto:** autonomous engineering that needs nothing from the owner.

The phases are:

- **Phase A, engineering:** code, gate and registry work by agents.
- **Phase B, completion:** consolidation and documentation, plus the minimum owner setup that makes Phase C possible.
- **Phase C, independent acceptance:** independent review of an exact SHA, owner risk acceptance, enforcement of the gate, and final acceptance.

It recommends; it does not decide. **Nothing here is a human approval.** Writing an option down approves no exception, baseline or ruleset.

The packet adds to the preserved [USER_ACTIONS_REQUIRED.md](USER_ACTIONS_REQUIRED.md) and does not change it. The reviewer's materials are in [PHASE_C_REVIEW_PACKAGE_PREP_2026-11-03.md](PHASE_C_REVIEW_PACKAGE_PREP_2026-11-03.md), and the state reads are in [COMPLETION_PASS_2026-11-03.md](COMPLETION_PASS_2026-11-03.md).

- **Main:** `8e2df97b558e69032e52a50ed0adfd311ad04578` (`GET /repos/onnxscibroccoli/bank-it-operations-lab/commits/main`, 18:15 EST).
- **Candidate SHA:** `0ad046825855f2c3e90861981624e2fb8373c24d` (`integration/candidate-20261103c`; CANDIDATE, not integrated; no PR; tested SHA `614d006ae049aed269dc404aa5b84a7c04b55d8e`). Validated against 18:15–18:30 EST.
  - It contains PR #39 at `95765e9`. The earlier revision of this packet (blob `32c6aebb`), the COMPLETION_PASS md/json and both registrations are byte-identical there (`git rev-parse 0ad0468:<path>`).
  - It does **not** yet contain this revision or the Phase C prep sidecar. Carrying them over is Auto task B4.
- The earlier candidate `integration/candidate-20261103b` @ `caa9ce7` is superseded by `-c` (`coordination/INTEGRATION_MANIFEST.md@0ad0468`, source refs).

## Sequencing correction: authorization source

- **What changes:** gate enforcement moves from premature to lifecycle-appropriate.
  - **Now (Phase B):** a baseline ruleset with no deletion and no force-push only.
  - **Deferred until Phase C readiness:** required approvals, CODEOWNERS review and required status checks (including `merge-eligibility`). Phase C readiness means a reviewer has been invited (UA-7), the gate pin has been re-reviewed (B1), and `merge-eligibility` is green on the SHA under review.
- **Source:** **Owner directive relayed to Final Report worker on 2026-11-03 18:13 ET via orchestration chat; not yet recorded in repo.**
- **Where I searched:**
  - `coordination/tasks.json` `rules` and `coordination/INTEGRATION_MANIFEST.{md,json}` on `integration/candidate-20261103c@0ad0468` (latest recorded: t26u 17:00 EST, t27u 17:35 EST; neither covers ruleset sequencing)
  - `coordination/PR_DISPOSITIONS.md@0ad0468` (t28u/t29u, PR dispositions only)
  - `coordination/T16_RECONCILIATION.md@0ad0468`
  - PR #42 body and `acceptance/rulesets/README.md@9589d89` (which says requiring `merge-eligibility` "blocks every merge to main" until T-16 is resolved, but records no owner directive)
  - branches `acceptance/t16-pin-review`, `ci-workflow-hardening`, `aws-remediation-backup-kms`, `design/*`
  - `docs/engineering-first-governance-deferral-20261103`, which points at the same commit as the candidate, `0ad0468`, and has no PR
- **What it is not:** a signed or authenticated approval. Commits and comments from the shared account prove the login, not the person (`coordination/tasks.json@8e2df97` UA-6 `reason`).
- **Recording it in the repo:** a dated `rules` entry, as was done for t26u/t27u. That is Auto task B9.

## USER ACTION REQUIRED: 3 (the smallest actionable set, all Phase B, all actionable now)

1. **UA-7:** invite an independent reviewer.
2. **UA-3 baseline:** a ruleset blocking deletion and force-push.
3. **UA-2:** confirm the Entra baseline.

Source: `coordination/tasks.json` UA-2, UA-3 and UA-7 are `OPEN` on both `main@8e2df97` and the candidate `@0ad0468`. The `user-actions` job in main run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441) prints `USER ACTION REQUIRED: 3 — UA-2; UA-3; UA-7`.

Live state at 18:15–18:30 EST:

- **Rulesets and protection:** `GET /rulesets` → `[]`. `main` and `evidence/acceptance` (`750de1c`) are unprotected.
- **Access:** collaborators `["onnxscibroccoli"]`. Invitations: 0.
- **Reviews:** 0 across all 46 PRs.
- **PR #4:** 0 comments.

## Phase map

| Item | Phase | Kind | Now or blocked by |
|---|---|---|---|
| UA-7 invite reviewer | B (prerequisite for C) | **Owner** | **Now** |
| UA-3 baseline ruleset | B | **Owner** | **Now** |
| UA-2 Entra baseline confirm | B (AC4 docs match code) | **Owner** | **Now** |
| UA-3 full rules (approvals, CODEOWNERS, required checks) | C (enforcement) | Owner | UA-7, B8, B1 |
| UA-1 EX-01..EX-04 risk acceptance | C (AC2) | Owner | Frozen packet (B10), UA-6 |
| UA-6 owner signing key | C (AC2/AC5 binding) | Owner | Independent review of ADR-0008 (needs UA-7) |
| UA-5 AC6 final acceptance | C (last) | Owner | AC1–AC5 MET for one SHA |
| Gate-pin re-review; review of the exact candidate SHA (AC1) | C | Reviewer (not the owner; not counted) | UA-7 |
| B1 trusted-manifest fix (T-16) | A (application in C) | Auto | Applying it needs the reviewer's pin re-review |
| B2 PR dispositions (#15, #23–#25) | B | Auto | #23–#25 HOLD by the Acceptance Integrator; #15 "CLOSE PROPOSED (needs Ian's explicit go-ahead)" (`coordination/PR_DISPOSITIONS.md@0ad0468`). Routine housekeeping, not counted |
| B3 review-notes module | A | Auto | Done on the candidate (`modules.json@0ad0468`: INTEGRATED); not on `main` |
| B4 carry PR #39 into the candidate | B | Auto | `95765e9` is carried; this revision is pending |
| B5 PR #39 description | B | Auto | Done |
| B6 integrator handoff | B | Auto | Note at `/workspace/bank-it-lab-reports/integrator_handoff_packet.md` (box-local) |
| B7 review the candidate's CI-flake fixes | A | Auto | Open |
| B8 CODEOWNERS from `acceptance/rulesets/CODEOWNERS.proposed@9589d89` | A | Auto | Needs the UA-7 name |
| B9 record the 18:13 ET sequencing directive in `tasks.json` `rules` | B | Auto | Integrator (unassigned) |
| B10 frozen Phase C packet (candidate, main, tested merge SHA, run, exception scope) | B → C | Auto | After B1/B4; prep in the Phase C sidecar |

## Owner-only decisions (authenticated)

### Phase B: actionable now

#### B-1. UA-7: Invite an independent reviewer

- **Decision:** name the qualified, independent human reviewer.
- **Recommended option:** one person who is not the shared author account, with **Write** access.
- **Reason:**
  - AC1 requires an APPROVED review on the exact SHA by a non-author account with write permission that is on the trusted allow-list (`coordination/tasks.json@8e2df97`, `acceptance_conditions_for_main.conditions[AC1].binding`).
  - Every Phase C item waits on this.
- **Risk if not done:** Phase C cannot start, and the candidate cannot merge (t26u/t27u, `coordination/tasks.json@0ad0468` `rules`).
- **Risk if done:** the collaborator can push to unprotected branches, so do B-2 the same day.
- **Alternatives:**
  - (a) Keep review deferred and present the work as unreviewed lab work. This is honest, but AC1 stays unmet.
  - (b) A second account you control. This is not independent (`USER_ACTIONS_REQUIRED.md` section 1, step 1).
- **Exact action:**
  - **In the GitHub UI:** <https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/access> → **Add people** → enter the exact username → **Write**.
  - **Or with the CLI:** `gh api -X PUT repos/onnxscibroccoli/bank-it-operations-lab/collaborators/<USERNAME> -f permission=push`
  - **Check:** `gh api repos/onnxscibroccoli/bank-it-operations-lab/invitations`

#### B-2. UA-3 baseline: block deletion and force-push (lifecycle-appropriate enforcement)

- **Decision:** turn on the minimum protection now.
- **Recommended option:** one **Active** ruleset with an empty bypass list, targeting `main` and `evidence/acceptance`, with only **Restrict deletions** and **Block force pushes**.
- **Reason:**
  - It protects the two branches the gate trusts from history rewrite and deletion, and blocks no normal merge.
  - Evaluate mode is refused on this plan (`acceptance/rulesets/api-attempt-20261103.txt@9589d89`: `422 ... Enterprise`).
- **Risk:**
  - The gate stays advisory until the full rules come in Phase C.
  - With an empty bypass list, even the owner cannot force-push. That is intended.
- **Alternatives:**
  - (a) The full prepared rulesets now (`acceptance/rulesets/*.ruleset.json@9589d89`). That blocks every merge, because there is no reviewer and `merge-eligibility` is red: candidate run [41734504240](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734504240) and main run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441).
  - (b) Store the rulesets as `disabled`, which protects nothing.
  - (c) Defer.
- **Exact action:**
  - **In the GitHub UI:** <https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/rules> → **New ruleset → New branch ruleset**.
    - Name: `baseline-no-delete-no-force-push`
    - Enforcement: **Active**
    - Bypass list: empty
    - Target branches: include `main` and `evidence/acceptance`
    - Rules: tick **Restrict deletions** and **Block force pushes** → **Create**.
  - **Or with the CLI:**

    ```sh
    gh api -X POST repos/onnxscibroccoli/bank-it-operations-lab/rulesets --input - <<'JSON'
    {"name":"baseline-no-delete-no-force-push","target":"branch","enforcement":"active","bypass_actors":[],
     "conditions":{"ref_name":{"include":["refs/heads/main","refs/heads/evidence/acceptance"],"exclude":[]}},
     "rules":[{"type":"deletion"},{"type":"non_fast_forward"}]}
    JSON
    ```

  - **Check:** `gh api repos/onnxscibroccoli/bank-it-operations-lab/rulesets`

#### B-3. UA-2: Confirm the Entra Conditional Access baseline

- **Decision:** keep or change three lab choices:
  - CA005/CA006 stay report-only
  - CA004 device compliance applies to All users on All apps (break-glass excluded)
  - CA003 uses the 12 privileged role templates in `identity/entra/baseline.json`
- **Live state:** "have not been confirmed by the owner" (`evidence/entra/BASELINE-CHOICES-PENDING.md@8e2df97`). PR #4 has 0 comments.
- **Recommended option:** confirm all three for the synthetic lab only.
- **Reason:**
  - Report-only is the cautious rollout pattern for risk policies.
  - The validator already enforces the choices as written.
  - The acceptance defect control proves that weakening CA002 fails (run [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024)).
  - Confirming changes no evidence.
- **Risk:** report-only risk policies do not block risky sign-ins. That is acceptable for a never-deployed lab and must stay a stated limitation. This is not permission for any live tenant (`USER_ACTIONS_REQUIRED.md` section 4).
- **Alternatives:** enforce CA005/CA006, narrow CA004, or change the role list. Each needs engineering and a new evidence run.
- **Exact action:**
  - **In the GitHub UI:** comment on <https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4>.
  - **Or with the CLI:** `gh pr comment 4 --repo onnxscibroccoli/bank-it-operations-lab --body "UA-2 decision: keep all three baseline choices for the synthetic lab"`
  - This records the choice. It is not authenticated AC4/AC5 acceptance (UA-6).

### Phase C: blocked (not counted)

| Item | Decision | Blocked by (source) | Recommended option | Risk | Exact action once unblocked |
|---|---|---|---|---|---|
| C-1. UA-3 full rules | On `main`: PR, 1 approval, code-owner review, last-push approval, stale dismissal, thread resolution and strict required checks. On `evidence/acceptance`: linear history | UA-7; B8 (no `.github/CODEOWNERS`); B1 (`merge-eligibility` red); the 18:13 ET sequencing directive (relayed) | Apply PR #42's prepared JSON once that PR is itself reviewed | An empty bypass list plus an unavailable reviewer blocks all merges. A red required check blocks all merges | **UI:** Settings → Rules → Rulesets → **New branch ruleset** (or **Import a ruleset**). **CLI:** `gh api -X POST repos/onnxscibroccoli/bank-it-operations-lab/rulesets --input acceptance/rulesets/main.ruleset.json`, then the same with `evidence-acceptance.ruleset.json` (`enforcement: active`) |
| C-2. UA-1 | Accept, reject or change EX-01..EX-04 (all PROPOSED, `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md@8e2df97`) | B10 frozen packet; C-3 (AC2 binding needs an owner attestation that is not from the PR author or shared account; `tasks.json@8e2df97` AC2 `binding`) | EX-01: accept once the bucket policy is shown. EX-02: accept as an explicit limitation. EX-03: accept once the wildcard scope is shown. EX-04: **re-decide** for the current `snapshot:awsbackup-*` scope; the earlier managed-policy position does not carry over | Deciding before the frozen packet binds the decision to the wrong scope or SHA | Record through the reviewed signing route on the frozen packet (`USER_ACTIONS_REQUIRED.md` section 3) |
| C-3. UA-6 | Enroll a human-only signing key | Independent review of `governance/owner-auth/ADR-0008-personal-account-owner-authentication.md` and its adapter (`tasks.json@8e2df97` UA-6) | Enroll after that review; keep the private key outside agent access | A key that agents can reach makes owner signatures worthless | **UI:** <https://github.com/settings/keys>. **CLI:** `gh ssh-key add <pubkey> --type signing` or `gh gpg-key add <pubkey>`, as the reviewed design specifies |
| C-4. UA-5 | AC6 final portfolio acceptance | AC1–AC5 MET for one exact SHA (`tasks.json@8e2df97` UA-5; AC6 `UNMET`) | Decide only on the exact SHA in the frozen packet | Accepting a moving branch accepts untested code | Review the frozen packet and `reports/INTEGRATION.md` for that SHA; record through the C-3 route |

## Autonomous engineering (nothing required of the owner)

Owners come from `coordination/modules.json@8e2df97` `owner.agent` and `coordination/INTEGRATION_MANIFEST.md@0ad0468`, or are "integrator (unassigned)".

| # | Phase | Task | Live evidence | Owner | State |
|---|---|---|---|---|---|
| B1 | A | Trusted-manifest fix (T-16) | `merge-eligibility` fails on `main` ([41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441)) and on the candidate tested SHA ([41734504240](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41734504240): new `scripts/ci` files not in the manifest). The UNREVIEWED proposal is bound to gate commit `39c71f9` (`coordination/INTEGRATION_MANIFEST.md@0ad0468`). PR #42 @ `8065a44` recommends `a518b03e` (`coordination/T16_RECONCILIATION.md@0ad0468`) | Worker D (independent integrator); the candidate's integrator | Prepared; not applied (t27u) |
| B2 | B | PR dispositions | #15 open, "CLOSE PROPOSED (needs Ian's explicit go-ahead)". #23–#25 open, HOLD (`coordination/PR_DISPOSITIONS.md@0ad0468`; `GET /pulls/<n>`) | Acceptance Integrator (#23–#25); integrator (unassigned) for #15 | Housekeeping. Saying "go ahead" on #15 is optional and not counted |
| B3 | A | review-notes module | INTEGRATED on the candidate; NOT_INTEGRATED on `main` (`modules.json@0ad0468` vs `@8e2df97`) | Bank IT Lab PR Reviewer; integrator | Done on the candidate |
| B4 | B | Carry PR #39 into the candidate | `95765e9` is carried (`coordination/INTEGRATION_MANIFEST.md@0ad0468`). This revision is not yet carried | Integrator of `integration/candidate-*`, author `onnxscibroccoli` (`git log 8e2df97..0ad0468`) | Pending for this revision |
| B5 | B | PR #39 description | Updated | Bank IT Lab Final Report | Done |
| B6 | B | Integrator handoff | `/workspace/bank-it-lab-reports/integrator_handoff_packet.md` | Bank IT Lab Final Report → integrator (unassigned) | Prepared |
| B7 | A | Review the candidate's CI-flake fixes (incident `pg_ctl` retry; docs `browser.mjs`) | `coordination/INTEGRATION_MANIFEST.md@caa9ce7`, "What was taken", carried into `-c` | Bank IT Lab Portfolio Cases; documentation maintainers | Open |
| B8 | A | CODEOWNERS | `acceptance/rulesets/CODEOWNERS.proposed@9589d89`; no `.github/CODEOWNERS` on `main` | integrator (unassigned) | Needs the UA-7 name |
| B9 | B | Record the 18:13 ET sequencing directive as a dated `tasks.json` rule | Not in `coordination/tasks.json@0ad0468` `rules` | integrator (unassigned) | Not done |
| B10 | B → C | Frozen Phase C packet | Prep: [PHASE_C_REVIEW_PACKAGE_PREP_2026-11-03.md](PHASE_C_REVIEW_PACKAGE_PREP_2026-11-03.md) | Bank IT Lab Final Report (prep); integrator (freeze) | Prep drafted |

## Revision history

- **2026-11-03 17:05 EST,** blob `47c191fe3b49f4934a2181e06fcb1f4faacd9a02` (PR #39 `b6e23ba`): first version.
- **2026-11-03 17:45–17:50 EST,** blob `32c6aebb6a66d0670b94b6df890df3a97b6e432b` (PR #39 `95765e9`; carried into candidate `-c`): split into owner-only and autonomous; candidate `caa9ce7` recorded.
- **2026-11-03 18:15–18:30 EST:** restructured by phase (A/B/C); candidate `-c` @ `0ad0468`; sequencing authorization recorded as relayed (not in repo); B9 and B10 added. The count is unchanged at 3.
