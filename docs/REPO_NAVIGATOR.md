# Repo navigator — one task at a time

## Start here: fast mode

1. Choose **PR #7** for the preserved integration baseline or **PR #35** for current portfolio delivery.
2. Read [the one-page status](REVIEWER_GUIDE.md#one-page-status-summary).
3. Pick one module or one failed check. Stop there until you have written its next action.

You do not need to understand every file today. This guide is a work organization aid, not medical advice. Take a break whenever you need one; the checkpoint below lets you resume.

## 1. What the repository does

This is a reproducible IT operations reference lab. It demonstrates infrastructure designs, identity-policy checks, database recovery, incident simulations and review controls. It is not a single deployed application or a certification of regulatory compliance.

The modules share **validation and evidence rules**, rather than a single application runtime. AWS templates do not need to provision a database for the local PostgreSQL exercise. Entra fixtures do not connect to that database or call a real tenant. CI (automated checks run by GitHub Actions) assembles their results for review.

- **AWS/CDK:** TypeScript describes infrastructure; CDK turns it into CloudFormation templates. Tests, security rules and evidence comparisons check the design without deploying it.
- **Entra:** Python checks synthetic Conditional Access policies against a lab baseline. It does not establish how a live tenant behaves.
- **PostgreSQL:** scripts create lab data, run backup/restore exercises and verify results. Negative controls deliberately introduce bad conditions to prove the checker rejects them.
- **Integration:** scripts track module ownership, verify evidence and decide whether reviews and checks apply to the exact proposed merge.

This is more complex than one app because a test can pass while evidence is stale, an exception is unapproved, or a review refers to a different commit. A **SHA** is a commit's exact identifier. Candidate SHA, main SHA and tested-merge SHA identify different things; do not substitute one for another.

## 2. File map

Paths below are on `delivery/portfolio`; the four core areas also exist on PR #7. Newer modules must not be attributed to the frozen PR #7 candidate.

| Question | Start here | Then inspect |
|---|---|---|
| What is delivered now? | `reports/FINAL_REPORT.md` | `coordination/modules.json` |
| What must I do personally? | `reports/USER_ACTIONS_REQUIRED.md` | `reports/user-actions.json` |
| What runs validation? | `scripts/validate-all.sh` | `.github/workflows/offline-validation.yml` |
| Where is AWS code? | `infra/aws-cdk/README.md` | `infra/aws-cdk/lib/`, `infra/aws-cdk/test/`, `.github/workflows/aws-cdk.yml` |
| Where is identity logic? | `identity/entra/ca_validator.py` | `identity/entra/baseline.json`, `tests/entra/`, `evidence/entra/` |
| Where is database recovery? | `tests/integration/postgres/run_restore_scenario.sh` | `verify_evidence.py`, `selftest_harness.sh` in that directory; `evidence/postgres/` |
| How is evidence checked? | `evidence/shared/validate_evidence.py` | `evidence/shared/tests/` and module-specific verifiers |
| How are approvals checked? | `scripts/ci/merge_eligibility.py` | `reviews.py`, `provenance.py`, `check_exceptions.py`, `verify_trusted_gate.py` in `scripts/ci/` |
| What is trusted? | `.github/acceptance/trusted-config.json` | manifest and independently pinned gate; `.github/workflows/integration-gate.yml` |
| What is historical? | `reports/INTEGRATION.md` | `coordination/tasks.json` acceptance bindings and dated records |
| What packages the newer portfolio? | `.github/workflows/portfolio-validation.yml` | `scripts/ci/portfolio_checks.sh` |

Other delivery areas include `infra/orgs/`, `infra/aws-network/`, `backup/`, `operations/endpoint/`, `identity/m365/`, `identity/governance/`, `observability/`, `integrations/vendor-mock/`, `governance/`, `inventory/`, and `scenarios/incident/`. Find their registered checks in `coordination/modules.json` before editing.

## 3. PR #7: what to review

PR #7 (`overnight/integration`) combines #3 shared evidence, #5 AWS remediation, #4 Entra and #2 PostgreSQL harness v2, later adding #20 M365 and #22 incident simulation. #5 replaces #1's AWS implementation. PR #1 is now closed, but that does not merge or approve #5 or #7.

The preserved head is `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45`. Its original narrative cites older results at `e9310f3`; those results are historical, not proof for the preserved head. The integration history records successive repairs to review independence, exact-merge binding and trusted-gate verification. Organizations and later portfolio additions belong to PR #35, not this frozen tree.

The significant question is: **can these modules be validated together, and can the gate reject misleading evidence or approvals?** Reviewers should examine both the operational code and the gate that judges it.

Main unknowns: independent exact-head approval, owner exception decisions, whether the running gate is independently trusted, documentation truthfulness and remaining blocking findings. Static cloud checks cannot prove live AWS service behavior. A model review using the author account is not an independent GitHub approval.

## 4. AC1–AC6 in plain English

The executable trusted gate is authoritative. Candidate-written status text cannot approve itself.

| Condition | Meaning | Human verifies | Automation checks |
|---|---|---|---|
| AC1 | Someone independent reviewed this exact candidate | Review quality, independence, unresolved objections | API review SHA, allowed reviewer, write-or-higher permission, decisive review state |
| AC2 | Applied security exceptions have authorized risk decisions | Each current exception, affected resources and compensating controls | Registered suppression scopes and valid externally bound decisions |
| AC3 | Required checks passed for this candidate with this base | Correct run, actual commands and useful tests | Required job results, candidate/base/merge identity and provenance |
| AC4 | Documentation accurately describes the code and status | Claims, baseline choices, supersession and execution labels | Bound external AC4 decision plus supporting structural checks |
| AC5 | No blocking finding remains in the integrated scope | Findings resolved with evidence; no blocker merely renamed | Bound external AC5 decision and AC2 dependency |
| AC6 | Ian accepts the finished portfolio | Final personal acceptance | Not supplied by a model or green CI |

AC1–AC5 together govern technical eligibility. AC6 is separate. Do not mark AC3 satisfied merely because a local command or a portfolio workflow passed. The older login-bound owner policy has a personal-account limitation; the newer signature verifier is only a prototype. Follow the current owner instructions rather than creating a second Admin account or copying old attestations.

## 5. Find a validation failure

First open the failed Actions job and its first failed step. Record the command and first useful error. Later skipped steps are usually consequences, not new bugs. A failing acceptance gate may be working correctly.

| Error or failed step | Probable source | Small next action |
|---|---|---|
| Python import or missing dependency | Wrong working directory/runtime | Compare Python version and directory with workflow |
| Module registry | `coordination/modules.json`, `scripts/ci/check_modules.py` | Find the named unclaimed path or missing registered check |
| Tasks lint | `coordination/tasks.json`, `scripts/ci/` | Remove false/stale acceptance claims; do not fabricate MET |
| Entra tests | `identity/entra/`, `tests/entra/` | Read the named fixture and expected rule |
| Evidence schema/hash mismatch | Module evidence and verifier | Identify changed input/output; regenerate using documented producer, never just change expected hashes to hide drift |
| PostgreSQL verifier/negative control | `tests/integration/postgres/` | Check tool/server versions, actual restore logs and expected failure reason |
| npm install | Module `package-lock.json`, CI Node/npm versions | Match CI runtime before changing a lockfile |
| TypeScript or Jest | `infra/aws-cdk/lib/`, `test/` | Read the first compile error or failed assertion |
| cdk-nag or S3 self-logging | Synthesized templates, security checks | Trace the named resource to its construct; don't add a suppression merely to get green |
| Synth drift | `infra/aws-cdk/cdk.out/` versus committed `evidence/aws/.../synth/` | Compare the exact differing template |
| Gate hashes rejected | Pinned gate/manifest and executing files | Stop release work; request independent review/re-pinning, not a bypass |
| Wrong SHA, missing approval or owner decision | `provenance.py`, `reviews.py`, trusted config | Check the identity tuple and missing external evidence |

Use the failing job to choose a track; do not always run every track in sequence.

### Commands: choose one

Prefer Actions if you do not already have the local tools. For a local offline run from the repository root:

```bash
git rev-parse HEAD
bash scripts/validate-all.sh --python-only
```

This subset needs Python, Git, Bash and, on the delivery branch, OpenSSL 3.x. It checks committed evidence but does not perform all fresh PostgreSQL/CDK exercises.

For AWS, use the runtime in `.github/workflows/aws-cdk.yml`, without AWS credentials configured:

```bash
cd infra/aws-cdk
npm ci --no-audit --no-fund --ignore-scripts
npx tsc --noEmit
npm test
npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --quiet
```

Stop on the first failure. These commands alone do not include every nag, self-logging, drift and hash check in the workflow. Full local validation uses `bash scripts/validate-all.sh` and additionally needs Node/npm and PostgreSQL server binaries; PostgreSQL initialization must run as a non-root user.

## 6. Small-task workflow and development priorities

Use **one question → one file → one check → one note**.

- [ ] Name the branch and exact SHA.
- [ ] Write one goal, such as “understand why merge-eligibility is red.”
- [ ] Open one relevant job or file.
- [ ] Identify whether this is code, evidence, environment or missing approval.
- [ ] If a code fix is needed, change one cause and rerun its focused check.
- [ ] Record the result and stop before expanding scope.

Priority order for this repository:

1. Keep PR #7 and PR #35 evidence separate.
2. Preserve the currently passing technical validation; investigate only an observed failure.
3. Obtain independent review and prepare the trusted-gate bootstrap. An agent can prepare code; it cannot invent the reviewer or their approval.
4. Complete and independently review owner-authentication activation before requesting effective signed decisions.
5. Resolve documented deployment blockers, including EX-04 runtime trust uncertainty, before any deployment claim.
6. Update docs and evidence for the final candidate; recheck its exact SHA. AC6 comes later.

Safe stopping points: after naming the failure, after a focused check, after one fix, or whenever concentration drops. Use this resumable note:

```text
Branch / SHA:
One goal:
File or Actions run:
Observed result:
Changes made (or none):
Next single action:
Stop here; no merge or deployment performed.
```

## 7. Use Copilot as a second brain

Start with architecture, then validation, then one implementation task, then docs and review. Ask it to cite actual paths, show the command it will use and separate observed results from guesses. In VS Code, attach the relevant file and error log; do not paste secrets. If it cannot access GitHub, give it the PR metadata and say which facts it cannot verify.

Keep a human responsible for review and risk decisions. A plausible explanation is not test evidence. Model-generated code must pass checks; changing a test expectation requires explaining why the old expectation was wrong. See [40 focused prompts](AI_PROMPTS.md); choose one, not the entire list.

## 8. First 30 minutes

- **0–5:** Open the one-page status. Choose PR #7 or PR #35. Write the branch and SHA. **Stop point: you know which version you mean.**
- **5–10:** Open that version's Actions checks. Pick one failed job, or the latest successful portfolio run if only orienting. **Stop point: one job selected.**
- **10–15:** Read its first failed step, or one successful validation step. Write the exact command and result. No setup or coding required.
- **15–20:** Open the matching file from the map. Ask one prompt from AI_PROMPTS. **Stop point: one explanation, not a whole-repo review.**
- **20–25:** Write whether the next task is a code fix, evidence repair or human decision. If unclear, write one question; do not guess.
- **25–30:** Save the checkpoint note and stop. A passing check does not require you to find another problem.

The repository demonstrates reproducible operations through code, tests and evidence. PR #7 assembles the original integration baseline; PR #35 extends it into the current portfolio. Your immediate next action is to choose the PR, read one status page and select one check.
