# Accelerated completion plan — 2026-10-28

Prepared by ChatGPT independent review. Snapshot approximately 17:57 EDT; re-fetch heads before acting.
Target: midnight ending October 28 (2026-10-29T00:00:00-04:00). Start now; do not schedule for tonight.
This is an executable coordination handoff, not an implementation approval.

## Current evidence

- main remains 7f50348bf1370381615eaed91c02607fe41de2f5 (README-only base) in current PR metadata.
- PR #26 acceptance/vertical-slice was 35674c4221a2ffb13a50b876925224f10b92aac9 when inspected; remote advanced again to eb42b23 during research. Do not treat either as permanently current.
- PR #7 integration was 4f54a0164f25c0e9bd4ab17d718bc188fd242772.
- PR #20 M365 is open at 1b3c240374285d7b0760b946e861dee15197dcf3, now includes runbooks, tests and evidence; earlier first-push-only status is stale.
- PR #22 incident demonstration is open at 3f136225e37e504a96225a0a82b703ff4122c710. Its stated timing is simulation evidence, not a bank SLA.
- Search returned 27 open PRs. This is not 27 independent units to merge: several contain shared integration ancestry.
- C1–C4 repairs were implemented at 17cfaea. At 35674c4 I independently ran:
  python3 -m unittest discover -s scripts/acceptance/tests -v
  Result: 32 tests passed, exit 0. This verifies regressions, not the entire portfolio or the authenticity of reviewer identities.
- CI for 35674c4 was running/queued when checked: acceptance 40776057727, aws-cdk 40776057836, postgres 40776057666, offline-validation 40776057676.
- The new decision path invokes the shared contract and distinguishes EXECUTION_PASS from REVIEW_PENDING. Its reviewer inputs remain unauthenticated strings. The assurance note acknowledges missing persisted acceptance, head-only testing, and no branch protection (the latter is worker-reported, not independently checked here).

## Goals and definition of done

Deliver an integrated, reproducible, zero-new-spend lab aligned to the supplied AMS bank IT Manager posting:
1. Fresh AWS static checks, actual local PostgreSQL recovery, Entra offline checks.
2. Integrated operational coverage: monitoring, incident response, backup references, patching, identity governance, M365, hybrid operations, vendors and management.
3. One acceptance command and an Actions report showing execution evidence, independent review, limitations and any user actions.
4. Merge to main only after the exact candidate and its integration with current main satisfy the gate. Verify the resulting main commit too.
5. Source-backed job mapping and a concise interview demonstration. Learning continues later; learning duration is not development duration.

Classify each claim: EXECUTED_LOCAL, EXECUTED_CI, STATIC_VALIDATED, SIMULATION, PLAN_ONLY, NOT_EXECUTED. A runbook may pass documentation validation without proving its commands executed. Live AWS/Entra validation is intentionally out of scope, not a request for credentials. This lab is not regulatory certification or proof of operational compliance.

## Critical gaps

P0:
- Independently assess repaired C1–C4 at a frozen SHA; close findings only against that SHA.
- Authenticate review provenance and bind approval scope to requirements and candidate SHA.
- Wire the final decision into one actual merge gate; a green workflow that intentionally returns REVIEW_PENDING must not authorize merge.
- Test current main + candidate together; serialize final merges and recheck base movement.
- Confirm every in-scope module is present AND registered with an executable check. Three-module acceptance is not whole-portfolio acceptance.

P1, parallel:
- Full-SHA action pins, bounded artifact retention/storage, per-task timeouts.
- Update coordinator policy and obsolete PR text to reflect existing user authorization for proven technical merges.
- Complete modules' CI adapters, source-backed mapping, operator demo and consolidated report.
- Reconcile the Organizations self-logging finding before including that module. Inspect code; do not rely on old PR descriptions.

Known acceptance hardening follow-ups:
- The dynamic HASH/ENTRA groups currently use minimum counts and contiguous numbering. Derive expected member paths from the reviewed candidate tree, so adding an untested module or dropping an end member cannot be hidden by still meeting a minimum.
- git_show_sha256() currently returns None on missing Git data and inventory binding then skips comparison. Release acceptance must fail closed when required source binding cannot be obtained.
- Review records currently get copied to every requirement. Require explicit reviewed requirement IDs/scope; do not turn a narrow review into blanket approval.
- Hashes demonstrate byte consistency, not independent execution or trustworthy authorship. Anchor run ID, attempt, tested SHA, workflow identity and review evidence in GitHub provenance.

## Dispatch now: reuse existing workers, do not restart completed work

Grok is sole scheduling coordinator and sole owner of coordination/tasks.json. Use at most four active coding workers plus an independent reviewer initially; increase only if throughput improves. Keep implementation owners disjoint. Shared computers need separate clones/worktrees AND separate temp directories, DB sockets, ports, output paths and caches.

| Lane | Owner / paths | Immediate work | Completion evidence |
|---|---|---|---|
| A acceptance | Existing Worker D; scripts/acceptance/** and its tests | Close remaining inventory/source-binding/scope gaps. Keep shared contract owners involved for interface changes. | New SHA; regression tests; explicit findings disposition; no self-approval |
| B Actions + integration | One integrator; .github/workflows/** and scripts/validate-all.sh | Pin actions; register all modules; aggregate checks; user-action summaries; freeze and test combined candidate | Real Actions URLs, expected job inventory, tested head/base/tree, full pass |
| C module closure | Existing module owners; each retains its own paths | M365, incident, hybrid, backup, patch, orgs, monitoring, identity and vendor checks; resolve actual gaps only | Per-module exact commands, expected negative reasons, outputs and limitations |
| D portfolio evidence | Existing matrix/report workers with separate file ownership | Reconcile job matrix, exceptions, demo, final report; remove outdated status claims without deleting history | Every job claim points to current artifact/check or declared gap |
| E independent review | ChatGPT reports/independent/chatgpt/**; Grok independent verifier elsewhere | Reproduce key defects and review final candidate, test gate bypasses, reconcile scope | SHA-bound decision with inspected scope and unresolved findings |

Only the integrator updates the integration branch. Workers submit deltas relative to declared bases; integrator inspects ancestry before cherry-picking/merging. Do not merge every PR wholesale or duplicate histories.
ChatGPT has no direct Grok bot dispatch channel here; this committed document is the handoff. Grok must consume it through GitHub. Do not claim ChatGPT is running continuously after its turn ends.

## Coordination contract

Each task records id, owner, owned_paths, base_sha, dependencies, acceptance_ids, status, branch, head_sha, last_progress_utc, next_checkpoint, attempts, evidence_urls, blocker and user_action.
States: READY, RUNNING, REVIEW_READY, CHANGES_REQUIRED, BLOCKED_USER, BLOCKED_TECHNICAL, DONE.
One writer updates the central manifest. Workers report messages/artifacts; they do not race to overwrite it.
At a missed checkpoint, inspect process/commit state and request a concrete checkpoint. Reassign only after explicit ownership release. Idle is not running.
Cap correction attempts at three per distinct failure, then independent diagnosis/reassignment. Preserve failed logs and continue other ready tasks. No endless model-to-model debate or constant polling.

## Actions design: implement within current workflows, not a new platform

- Keep model orchestration in Grok's existing bots. Actions runs deterministic validation. Do not install paid model API loops or assume ChatGPT/Gemini quotas exist.
- Use PR events for candidate checks; manual dispatch is diagnostics, not the sole required merge check.
- One final acceptance-gate job runs with always() and explicit needs. Inspect every expected job result and every required artifact. Missing, cancelled, skipped or unknown required work is not PASS.
- Separate expensive independent modules into a matrix with fail-fast:false and initially max-parallel:4. Keep short Python checks together. One failure must not cancel useful unrelated evidence.
- Avoid duplicate push+PR full suites. Cancel stale PR runs using workflow+PR/ref concurrency groups. Do not cancel final acceptance or main verification halfway through publication.
- Reuse lockfiles and supported dependency caches keyed by OS/runtime/lockfile. Never cache credentials or reuse prior test results as current evidence. Never share untrusted caches with privileged jobs.
- Standard hosted runners only; contents:read by default; persist-credentials:false when pushes are unnecessary. Full commit-SHA pins verified against upstream action repositories. No untrusted PR code in a privileged pull_request_target job.
- Keep test jobs credential-free. Put any required GitHub write operation in a separately scoped trusted job; never expose write tokens to arbitrary PR code.
- Set job and command timeouts. Capture actual exit codes; preserve pipeline failures. Negative tests assert the intended error class, not just nonzero.
- Test the combined main/candidate tree on pull_request. If an existing merge queue is available, use merge_group too. Do not make setting up a new merge queue the critical path: serialized integration with current-base revalidation is sufficient.
- Native branch protection/rulesets should require the final gate. Query existing settings first. Use authorized admin capability if available; otherwise report the precise permission need and continue coding/testing. Never bypass existing protection.
- Reviews and run evidence must refer to exact SHAs. Do not commit a review to the candidate and then claim the old SHA is the new one: keep review/acceptance records on a separate audit branch or workflow artifact with immutable IDs.
- Bot pushes through GITHUB_TOKEN have event-trigger restrictions. Verify that each expected CI run actually started; do not assume pushes recursively launch checks. Prefer existing authorized bot GitHub connection; do not request new credentials speculatively.
- After eligible merge, run a main smoke/full acceptance check appropriate to what changed and persist the mapping from reviewed candidate/tree to merged main commit. A failure starts remediation and marks release status failed.

## User intervention without stopping the project

At every checkpoint and failure classify blockers:
AUTONOMOUS_FIX, USER_ACTION_REQUIRED, or OUT_OF_SCOPE.
A transient test failure, dependency installation, merge conflict, missing documentation or independent agent review is normally AUTONOMOUS_FIX.
Examples of genuine user actions: interactive login/MFA after a required connection actually fails; an admin setting outside available permissions; approval to incur money (do not incur it); a material risk decision outside delegated lab scope.
No speculative AWS/Entra/Vault setup.

When USER_ACTION_REQUIRED:
1. Immediately write a short user-actions JSON/Markdown result for that task.
2. Publish it in a dedicated fast Actions reporting job as soon as the checkpoint is pushed; do not wait for long test jobs. Include it again in the final always() summary.
3. Use $GITHUB_STEP_SUMMARY plus a warning/error annotation. Upload a small report artifact where storage is allowed.
4. Include task ID, exact action, reason it cannot be automated, observed error (sanitized), smallest permission needed, link/instructions, blocked tasks, work continuing, and whether it affects the deadline.
5. Mark only the dependent tasks BLOCKED_USER. Schedule other READY tasks immediately.
6. When resolved, verify the connection/permission and resume only the blocked dependency chain.

Report top line:
USER ACTION REQUIRED: NONE
or
USER ACTION REQUIRED: <number> — <short action>
Show this even when the overall workflow fails. A report is not proof of notification delivery: GitHub email/push depends on the user's existing notification settings. Do not claim the user was notified externally merely because a summary exists.
If Actions itself cannot run, publish the blocker in the existing GitHub report/PR and surface it in the next user-facing response; do not wait for a broken reporter.

Use typed, validated fields; never interpolate PR titles/bodies or artifact strings as shell code. Reviewer/notification jobs must not execute code downloaded from untrusted artifacts.

## Evidence and cost controls

No new spend. Standard public-repo runner minutes are free, but storage and larger runners have separate billing. Verify repository visibility and available allowance before relying on free usage; never change visibility to obtain free CI.
Set small compressed artifacts, retention 7 days (project policy, not a regulation), plus a durable compact acceptance manifest in a separate audit record. Retention alone is not a spending cap. Do not delete historical failures without preserving agreed evidence.
If allowance cannot be established, keep working on existing no-charge bot machines and publish concise reports without large uploads. Report any true account-setting blocker.
A new commit invalidates old exact-SHA review. Delta review may reuse prior reasoning and unchanged-file hashes, but must explicitly assess the new candidate.

## Timeline from dispatch (estimates, not guaranteed runtime)

0–15 min: coordinator refreshes all heads, records ownership and dependencies, freezes scope, starts lanes.
15–60 min: acceptance/provenance fixes and reporting; integrate ready modules while reviewer reviews frozen snapshots.
60–120 min: combined suite, negative controls, independent review; address only observed failures.
120–180 min: merge eligible candidate, verify main, publish final evidence and a 15-minute demo script.
Use remaining time before midnight for failed gates and coverage gaps, not extra scaffolds.
At deadline publish actual state: delivered, tested, accepted, merged, pending, user actions. Missing required scope remains missing; do not redefine completion to turn it green.

## Job alignment priorities

Highest-value observable sequence: monitor detects incident -> triage identifies fault -> local PostgreSQL recovery -> integrity check -> executive update -> corrective action.
Pair that with AWS network/IAM/encryption reasoning and M365/AD troubleshooting. Management evidence should show triage priorities, RACI, vendor escalation and staff handoff, labeled synthetic.
Use the actual job matrix rather than inventing a 25-service AWS list. Keep reference diagrams/runbooks distinguished from executed demonstrations. Preserve original repository missions; this task does not authorize rewrites of Grasshopper, Broccoli Core, CivicPatch, Helix or OmniKali.

## Primary research consulted

- GitHub required-check behavior, latest SHA, skipped jobs and merge_group:
  https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks
- GitHub workflow syntax/concurrency:
  https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Job summaries and annotations:
  https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
- Workflow security, least-privilege tokens and action SHA pins:
  https://docs.github.com/en/actions/reference/security/secure-use
- Runner and storage billing:
  https://docs.github.com/en/billing/concepts/product-billing/github-actions
- GITHUB_TOKEN event behavior:
  https://docs.github.com/en/actions/concepts/security/github_token
- Matrix execution:
  https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations

The lane allocation, four-worker initial cap, timeboxes, seven-day retention and dispatch sequence are project recommendations, not vendor mandates.

## Immediate Grok instruction

Consume this document and PR #27 now. Refresh remote heads and adopt the dependency plan. Dispatch existing owners immediately, preserve ChatGPT's review-only paths, and complete every unblocked task autonomously. Do not ask permission to continue ordinary implementation, testing, integration or already-authorized proven merges. Publish user blockers through Actions promptly and continue independent work. Return durable task owners, SHAs, Actions links and next completion checkpoints, not an unsupported “working” status.
