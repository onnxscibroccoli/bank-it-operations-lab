# Human decision packet, 2026-11-03

This packet covers the decisions that only the repository owner can make. It was rechecked against live state at `main` = `8e2df97b558e69032e52a50ed0adfd311ad04578` on 2026-11-03, 16:55–17:05 EST (UTC-5). Sources are cited per item; the full state read is in [COMPLETION_PASS_2026-11-03.md](COMPLETION_PASS_2026-11-03.md).

The packet adds to the preserved [USER_ACTIONS_REQUIRED.md](USER_ACTIONS_REQUIRED.md) and does not change it. Some steps there name PR #35, which is now merged. Where the two differ, this packet gives the current route.

It recommends; it does not decide. Nothing here is an approval, and no exception or baseline choice is approved by writing it down.

**USER ACTION REQUIRED: 3 — UA-2, UA-3, UA-7.** Source: `coordination/tasks.json@8e2df97`, with status OPEN; `user-actions` job in run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441).

Suggested order: UA-7 first, then UA-3 phase 1 (it can be done at the same time), then UA-2. UA-3 phase 2 comes once a reviewer exists and `merge-eligibility` is green.

## UA-7: Invite an independent reviewer

- **Decision required:** who is the qualified, independent human reviewer for this repository?
- **Live state:**
  - Collaborators: `onnxscibroccoli` only. Invitations: 0. Reviews on all 41 PRs: 0 (`GET /collaborators`, `GET /invitations`, `GET /pulls/<n>/reviews`).
  - Module `final-report` is `UNREVIEWED_DELIVERY_CANDIDATE` (`coordination/modules.json@8e2df97`).
- **Recommended option:** invite one named person who is not the shared author account, with **Write** (collaborator) access.
- **Reason:** AC1 needs independent review of an exact SHA. The author account cannot supply it (`tasks.json` UA-7 `reason`). Without a reviewer, a "1 approval" ruleset (UA-3 phase 2) would block every merge.
- **Risk if not done:** everything on `main` stays unreviewed. AC1, and therefore AC6, can never be met. The acceptance gate stays `REVIEW_PENDING` (run [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024)).
- **Alternatives:**
  - (a) Keep review deferred under the 2026-10-31 directive and label the portfolio "unreviewed lab work". This is honest, but AC1 stays unmet.
  - (b) A second account you control. This is **not** independent (`USER_ACTIONS_REQUIRED.md` section 1, step 1), so it is not recommended.
- **Exact action:**
  - **In the GitHub UI:** Settings → Collaborators (<https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/access>) → **Add people** → exact username → **Write**.
  - **Or with the CLI:** `gh api -X PUT repos/onnxscibroccoli/bank-it-operations-lab/collaborators/<USERNAME> -f permission=push`
  - Then tell the integrator the username so they can prepare CODEOWNERS. The reviewer reviews a frozen SHA, not old PR #7 or #35.

## UA-3: Protect `main` and `evidence/acceptance`

- **Decision required:** enable branch rulesets now, and decide how strict they should be.
- **Live state:**
  - `GET /branches/main/protection` → 404; `GET /branches/evidence%2Facceptance/protection` → 404; `GET /rulesets` → `[]`. No CODEOWNERS file exists.
  - `merge-eligibility` currently **fails on `main`** because of trusted-manifest drift (run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441), job `merge-eligibility`).
- **Recommended option:** a phased setup.
  - **Phase 1 now:** an Active ruleset on both branches that blocks deletion and force-push, with an empty bypass list.
  - **Phase 2:** after UA-7 is done and `merge-eligibility` is green on `main`, add "require PR, 1 approval, dismiss stale, last-push approval, conversation resolution" and require the `final-summary` and `merge-eligibility` checks.
- **Reason:**
  - Phase 1 removes the history-rewrite and deletion risk at no cost.
  - Requiring approvals before a reviewer exists, or requiring a check that fails on `main` today, would block every merge, including the integrator's fix for that check (`USER_ACTIONS_REQUIRED.md` section 2, step 9; `tasks.json` UA-3 `instructions`).
- **Risk:**
  - Until phase 2, the gate stays advisory, and the shared account can push directly to `main` and to the trusted manifest branch.
  - In phase 2, an empty bypass list means even the owner cannot merge without the reviewer.
- **Alternatives:**
  - (a) Apply the full rules in `USER_ACTIONS_REQUIRED.md` section 2 at once. This is correct in the end state, but blocks all merges today.
  - (b) Classic branch protection instead of rulesets. That works, but `USER_ACTIONS_REQUIRED.md` documents rulesets.
  - (c) Defer. The gate stays advisory.
- **Exact action, phase 1:**
  - **In the GitHub UI:** Settings → Rules → Rulesets → New branch ruleset (<https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/rules>). Name `protect-main-and-acceptance`, Enforcement **Active**, bypass empty, targets `main` and `evidence/acceptance`, then enable **Restrict deletions** and **Block force pushes**.
  - **Or with the CLI:**

    ```sh
    gh api -X POST repos/onnxscibroccoli/bank-it-operations-lab/rulesets --input - <<'JSON'
    {"name":"protect-main-and-acceptance","target":"branch","enforcement":"active","bypass_actors":[],
     "conditions":{"ref_name":{"include":["refs/heads/main","refs/heads/evidence/acceptance"],"exclude":[]}},
     "rules":[{"type":"deletion"},{"type":"non_fast_forward"}]}
    JSON
    ```

  - Verify with `gh api repos/onnxscibroccoli/bank-it-operations-lab/rulesets`.
- **Exact action, phase 2** (only after UA-7 is done and `merge-eligibility` is green on `main`):
  - Edit the ruleset, using `gh api -X PUT repos/onnxscibroccoli/bank-it-operations-lab/rulesets/<ID> --input <file>`.
  - Add a `pull_request` rule: `required_approving_review_count: 1`, `dismiss_stale_reviews_on_push: true`, `require_last_push_approval: true`, `required_review_thread_resolution: true`.
  - Add a `required_status_checks` rule with `strict_required_status_checks_policy: true` and the contexts `final-summary` and `merge-eligibility`. Select them in the UI picker so the names match exactly.
  - Do not enable **Restrict updates** without a reviewed working route.

## UA-2: Confirm the Entra Conditional Access baseline

- **Decision required:** keep or change three lab baseline choices:
  - CA005/CA006 risk policies stay report-only
  - CA004 device compliance applies to All users on All apps (break-glass excluded)
  - CA003 uses the 12 privileged role templates in `identity/entra/baseline.json`
- **Live state:** `evidence/entra/BASELINE-CHOICES-PENDING.md@8e2df97` says these "have not been confirmed by the owner". PR [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) is merged, with no decision comment. `tasks.json` UA-2 is OPEN and blocks AC4.
- **Recommended option:** confirm all three as written, for the synthetic lab only.
- **Reason:**
  - Report-only for risk policies is the cautious rollout pattern: it avoids lockouts while the risk signals are evaluated.
  - The scope of device compliance and of the roles is already enforced and tested by the offline validator.
  - The acceptance defect control already proves that weakening CA002 fails (run [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024)).
  - Confirming leaves the evidence untouched; changing a choice requires a new evidence run.
- **Risk:** report-only risk policies do not block risky sign-ins. That is acceptable for a never-deployed lab, but should be stated as a limitation and not carried into a live tenant as-is. This is a lab design approval, not permission to touch a live tenant (`USER_ACTIONS_REQUIRED.md` section 4).
- **Alternatives:**
  - (a) Set CA005/CA006 to enforced. You would have to edit `baseline.json` and the policies, then regenerate the fixtures and add a new evidence run.
  - (b) Narrow device compliance to a pilot group.
  - (c) Change the role list.
  - Each of these needs integrator engineering and a new evidence run. None of them is a user action.
- **Exact action:** tell the integrator "UA-2: keep all three" or the specific changes. To record it in the repo, the integrator adds a dated decision note. That is a decision record, not a formal AC4/AC5 acceptance, which still needs the owner-authentication path (UA-6).

## Not yet actionable (not counted)

| ID | What it is | Why it is not actionable yet (source) | Recommended position when it becomes actionable |
|---|---|---|---|
| UA-1 | Accept, reject or change EX-01..EX-04 | All four are PROPOSED on `main` (`evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md@8e2df97`). Effective approval needs the integrator's frozen packet and a reviewed owner-authentication path (`tasks.json` UA-1) | EX-01: accept after the integrator shows the synthesized access-log bucket policy (TLS-only, `aws:SourceArn`/`SourceAccount`-scoped log delivery). EX-02: accept as an explicit limitation, with a replica-stack design note. EX-03: accept after the synthesized policy shows the wildcard is limited to `RDSOSMetrics` log streams in one account and region. EX-04: **re-decide**. Your earlier "AWS-managed policy OK after role review" applied to a scope that no longer exists. The current scope is a customer-managed `snapshot:awsbackup-*` wildcard whose runtime trust is unverified. None of these is a formal approval until recorded through the reviewed path |
| UA-5 | AC6 final portfolio acceptance | `tasks.json` UA-5: "AC1, AC2, AC4 and AC5 are not met yet". The acceptance gate is `REVIEW_PENDING`, contract `BLOCKED`, 0 reviews (run [41703902024](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902024)) | Decide only after AC1–AC5 are MET for one exact SHA |
| UA-6 | Enroll a human-only owner signing key | `tasks.json` UA-6: no keys enrolled, adapter not activated, independent review of the design pending (`governance/owner-auth/ADR-0008-personal-account-owner-authentication.md`) | Wait for the reviewed design. Keep the private key outside agent access. Never paste it into chat |

## Not user actions (integrator or housekeeping)

- **The `merge-eligibility` failure on `main`.** The trusted manifest on `evidence/acceptance@750de1c` does not include PR #40's change to `scripts/ci/tests/test_module_coverage.py` (run [41703902441](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/41703902441)). A reviewed trusted-manifest update is integrator work.
- **Superseded PRs left open.** PRs #23–#25 are listed as superseded in `modules.json` `acceptance.superseded_prs`, but are still open. Closing them is housekeeping.
- **The integrator handoff for PR #39.** The integrator for this documentation has not been named yet.
