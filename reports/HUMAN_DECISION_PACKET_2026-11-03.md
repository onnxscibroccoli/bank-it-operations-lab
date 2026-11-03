# Human decision packet, 2026-11-03

This packet lists the decisions that only the repository owner (Ian, as account holder of `onnxscibroccoli`) can make, and separates them from engineering work that agents carry out without the owner.

- **Rechecked against:** `main` = `8e2df97b558e69032e52a50ed0adfd311ad04578` (`GET /repos/onnxscibroccoli/bank-it-operations-lab/commits/main`), at 17:36–17:45 EST (UTC-5) on 2026-11-03.
- **Consolidated candidate:** `integration/candidate-20261103b` @ `caa9ce7c1b1538d8da920463db77c93c05fe882b`. It is a CANDIDATE, not integrated; see [COMPLETION_PASS_2026-11-03.md](COMPLETION_PASS_2026-11-03.md).
- **What this is not:** it recommends; it does not decide. Nothing here is an approval, and writing an option down does not approve any exception or baseline choice.
- **Relation to the preserved records:** it adds to [USER_ACTIONS_REQUIRED.md](USER_ACTIONS_REQUIRED.md) and does not change it. Some steps in that file name PR #35, which is now merged; where they differ, this packet gives the current route.

## Smallest actionable set

**USER ACTION REQUIRED: 3.** Do them in this order:

1. **UA-7:** invite one independent reviewer.
2. **UA-3 (baseline):** create one ruleset that blocks deletion and force-push on `main` and `evidence/acceptance`.
3. **UA-2:** confirm the Entra baseline choices.

Source: `coordination/tasks.json@8e2df97`, where UA-2, UA-3 and UA-7 are `OPEN`, and the `user-actions` job in run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441), which prints `USER ACTION REQUIRED: 3 — UA-2; UA-3; UA-7`. The consolidated candidate's `coordination/tasks.json@caa9ce7` has the same statuses.

These three are independent. Each takes minutes, and none needs an agent first. Everything else in section A waits for something listed under "blocked by".

## A. Owner-only authenticated decisions

### A1. UA-7: Invite an independent reviewer (actionable now)

- **Decision:** who is the qualified, independent human reviewer?
- **Live state:**
  - collaborators `["onnxscibroccoli"]` (`GET /collaborators`)
  - invitations 0 (`GET /invitations`)
  - reviews 0 across all 42 PRs (`GET /pulls/<n>/reviews`)
- **Recommended option:** one named person who is not the shared author account, invited with **Write** access.
- **Reason:**
  - The author account cannot provide AC1 (`tasks.json@8e2df97` UA-7 `reason`).
  - GitHub never counts a PR author's own approval (`acceptance/rulesets/README.md@9589d89`, PR #42).
  - The gate-pin re-review (B1) also needs this person.
- **Risk if not done:** AC1, and therefore AC6, can never be met. The acceptance gate stays `REVIEW_PENDING` (run [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024)). The candidate cannot merge under owner directive t26u (`coordination/INTEGRATION_MANIFEST.md@caa9ce7`).
- **Risk if done:** a collaborator with Write access can push to unprotected branches, so do A2 the same day.
- **Alternatives:**
  - (a) Keep review deferred under the 2026-10-31 directive and present the work as unreviewed lab work. This is honest, but AC1 stays unmet.
  - (b) A second account you control. This is not independent (`USER_ACTIONS_REQUIRED.md` section 1, step 1).
- **Exact action:**
  - **In the GitHub UI:** <https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/access> → **Add people** → enter the exact username → choose **Write**.
  - **Or with the CLI:** `gh api -X PUT repos/onnxscibroccoli/bank-it-operations-lab/collaborators/<USERNAME> -f permission=push`
  - **Check:** `gh api repos/onnxscibroccoli/bank-it-operations-lab/invitations`
  - Then tell the integrator the username, so the CODEOWNERS placeholder (`acceptance/rulesets/CODEOWNERS.proposed@9589d89`) can be filled through a PR.

### A2. UA-3 baseline: block deletion and force-push on both branches (actionable now)

- **Decision:** turn on the minimum protection now, or keep both branches unprotected.
- **Live state:**
  - `GET /rulesets` → `[]`
  - `GET /branches/main/protection` → 404
  - `GET /branches/evidence%2Facceptance/protection` → 404 (head `750de1c`)
- **Recommended option:** one **Active** ruleset with an empty bypass list, targeting `main` and `evidence/acceptance`, with only **Restrict deletions** and **Block force pushes**.
- **Reason:**
  - This removes the history-rewrite and deletion risk on the two branches the gate trusts, and blocks no normal merge.
  - Evaluate mode is refused on this plan (`422 ... Enterprise`, in `acceptance/rulesets/api-attempt-20261103.txt@9589d89`). So the only choices are an active rule or no rule.
- **Risk:**
  - The gate stays advisory until A5.
  - With an empty bypass list, even the owner cannot force-push. That is intended.
- **Alternatives:**
  - (a) Apply the full prepared rulesets (`acceptance/rulesets/*.ruleset.json@9589d89`) now. That blocks every merge, because there is no reviewer and `merge-eligibility` is red.
  - (b) Store them with `enforcement: disabled`, which protects nothing.
  - (c) Classic branch protection.
  - (d) Defer.
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

### A3. UA-2: Confirm the Entra Conditional Access baseline (actionable now)

- **Decision:** keep or change three lab choices:
  - CA005/CA006 risk policies stay report-only
  - CA004 device compliance applies to All users on All apps (break-glass excluded)
  - CA003 uses the 12 privileged role templates in `identity/entra/baseline.json`
- **Live state:** `evidence/entra/BASELINE-CHOICES-PENDING.md@8e2df97` says the choices "have not been confirmed by the owner". PR #4 is merged with 0 comments (`GET /issues/4/comments`).
- **Recommended option:** confirm all three as written, for the synthetic lab only.
- **Reason:**
  - Report-only is the cautious rollout pattern for risk policies.
  - The validator already enforces the other two choices.
  - The acceptance defect control proves that weakening CA002 fails (run [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024)).
  - Confirming changes no evidence.
- **Risk:** report-only risk policies do not block risky sign-ins. That is acceptable for a never-deployed lab, but it must stay a stated limitation and not be copied into a live tenant. This is not permission to touch a live tenant (`USER_ACTIONS_REQUIRED.md` section 4).
- **Alternatives:** enforce CA005/CA006, narrow CA004 to a pilot group, or change the role list. Each needs engineering and a new evidence run.
- **Exact action:**
  - **In the GitHub UI:** open <https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4>, comment `UA-2 decision: keep all three baseline choices for the synthetic lab` (or the change you want), and tell the integrator.
  - **Or with the CLI:** `gh pr comment 4 --repo onnxscibroccoli/bank-it-operations-lab --body "UA-2 decision: keep all three baseline choices for the synthetic lab"`
  - A comment from the shared account proves the login, not the person (`tasks.json@8e2df97` UA-6 `reason`). It records the decision but is not formal AC4/AC5 acceptance.

### Owner-only, blocked (not counted)

| ID | Decision | Blocked by (source) | Recommended option | Risk | Exact action once unblocked |
|---|---|---|---|---|---|
| A4. UA-3 full rules | Require PR, 1 approval, code-owner review, last-push approval, stale dismissal, thread resolution, and status checks (strict) on `main`. Require linear history on `evidence/acceptance` | A1 (no second human; `acceptance/rulesets/README.md@9589d89` step 1); `.github/CODEOWNERS` absent on `main`; `merge-eligibility` red (run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441)) until B1 | Apply the prepared JSON from PR #42 as written, after its own review | With an empty bypass list, an unavailable reviewer blocks all merges. Requiring a red check blocks all merges | **UI:** Settings → Rules → Rulesets → New branch ruleset (or **Import a ruleset** with the JSON). **CLI:** `gh api -X POST repos/onnxscibroccoli/bank-it-operations-lab/rulesets --input acceptance/rulesets/main.ruleset.json`, then the same with `evidence-acceptance.ruleset.json` (set `enforcement` to `active`; `acceptance/rulesets/README.md@9589d89`) |
| A5. UA-1 | Accept, reject or change EX-01..EX-04 (all PROPOSED in `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md@8e2df97`) | The integrator's frozen packet (exact candidate, main, tested-merge SHA, run, current scope) and the reviewed owner-authentication path (`tasks.json@8e2df97` UA-1; A6) | EX-01: accept once the synthesized bucket policy is shown. EX-02: accept as an explicit limitation. EX-03: accept once the wildcard is shown limited to `RDSOSMetrics` streams in one account and region. EX-04: **re-decide**. The earlier "AWS-managed policy OK after role review" applied to a scope that is gone; the current scope is `snapshot:awsbackup-*`, with runtime role trust unverified | Accepting before the frozen packet would bind the decision to the wrong scope or SHA | Record the decision through the reviewed signing route on the frozen packet (`USER_ACTIONS_REQUIRED.md` section 3). No placeholder attestations |
| A6. UA-6 | Enroll a human-only owner signing key | Independent review of `governance/owner-auth/ADR-0008-personal-account-owner-authentication.md` and its adapter (`tasks.json@8e2df97` UA-6); A1 | Enroll after that review, with the private key held outside agent access | A key reachable by agents would make owner signatures worthless | **UI:** <https://github.com/settings/keys> → **New SSH key** or **New GPG key**, as the reviewed design specifies. **CLI:** `gh ssh-key add <pubkey> --type signing` or `gh gpg-key add <pubkey>`. Never paste a private key into chat |
| A7. UA-5 | AC6 final portfolio acceptance | AC1–AC5 MET for one exact SHA (`tasks.json@8e2df97` UA-5). The acceptance gate is `REVIEW_PENDING`, contract `BLOCKED` (run [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024)) | Decide only on the exact SHA named in the frozen packet | Accepting a moving branch accepts untested code | Review `reports/INTEGRATION.md` for that SHA. Record through the A6 route |

The independent reviewer, not the owner, does two things after A1: re-review the gate pin (B1), then review the frozen candidate SHA. Neither counts as a user action.

## B. Autonomous engineering tasks (nothing required of the owner)

| # | Task | Live evidence | Owner / teammate | State |
|---|---|---|---|---|
| B1 | Trusted-manifest fix for `merge-eligibility`. `evidence/acceptance@750de1c` pins a stale `scripts/ci/tests/test_module_coverage.py` | `merge-eligibility` fails on `main` (run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441)), on PR #39, and on the candidate (run [41731062507](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41731062507), which also lists the new `scripts/ci` files) | `acceptance` module owner, Worker D (independent integrator) (`coordination/modules.json@8e2df97`). The proposal is in [PR #42](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/42) @ `9589d89` and `coordination/proposed-gate-pin/gate-manifest.json@caa9ce7` (UNREVIEWED, not applied) | Prepared. Applying it is blocked by the reviewer's pin re-review (after A1), per directive t26u |
| B2 | Close superseded PRs #23, #24 and #25 | All three open (`GET /pulls?state=open`). Listed in `acceptance.superseded_prs` (`coordination/modules.json@8e2df97`) | integrator (unassigned) | Not done. Housekeeping |
| B3 | `review-notes` module (the only NOT_INTEGRATED module) | `MODULE COVERAGE: 26/27` (run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441)). The candidate registers it as INTEGRATED: "27 INTEGRATED, 1 SUPERSEDED" (`coordination/INTEGRATION_MANIFEST.md@caa9ce7`) | Bank IT Lab PR Reviewer (module owner); Bank IT Lab Integrator (candidate) | In the candidate; not on `main` |
| B4 | Refresh the candidate with PR #39's current head | The candidate merged #39 at `42d8e96` (`coordination/INTEGRATION_MANIFEST.json@caa9ce7` `source_refs`). #39 has moved on since | integrator (unassigned) | Not done |
| B5 | PR #39 description | Updated in this pass. The prior body is saved at `/workspace/bank-it-lab-reports/pr39_body_before_edit.md` (box-local) | Bank IT Lab Final Report | Done |
| B6 | Integrator handoff for the PR #39 documentation commits | No integrator has been named for the reports | integrator (unassigned) | Waiting for a name. Not an owner decision |
| B7 | Review the CI-flake fixes in the candidate (`scenarios/incident/run_incident_demo.sh` retry; `scripts/docs/tests/browser.mjs`) | `coordination/INTEGRATION_MANIFEST.md@caa9ce7`, "What was taken" | Bank IT Lab Portfolio Cases (incident demo); PR #41 owner, documentation maintainers (browser test) | Open |
| B8 | Fill CODEOWNERS from the proposed file, once A1 provides a name | `acceptance/rulesets/CODEOWNERS.proposed@9589d89`; no `.github/CODEOWNERS` on `main` | integrator (unassigned) | Blocked by A1 (a name is needed) |

## Revision history

- **2026-11-03 17:05 EST,** packet blob `47c191fe3b49f4934a2181e06fcb1f4faacd9a02` at PR #39 `b6e23ba`: first version, with UA-7, UA-3 phases 1–2, UA-2, and the not-yet-actionable items.
- **2026-11-03 17:45 EST:** split into owner-only (A) and autonomous (B). Added the consolidated candidate and PR #42's prepared rulesets. No change to the count.
