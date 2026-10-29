# Case study: CivicPatch

- **Repository:** [https://github.com/onnxscibroccoli/civicpatch](https://github.com/onnxscibroccoli/civicpatch) (public, default branch `main`)
- **Snapshot:** HEAD [`cd94213`](https://github.com/onnxscibroccoli/civicpatch/commit/cd94213ec2707827aa178794e962e6a4ffc5b74d), 2026-10-23 09:41 EDT
- **Created:** 2026-10-16 18:30 EDT · **Commits on main:** 88 · **PRs:** 20 merged / 1 open / 3 closed
- **Languages (bytes):** TypeScript 365 KB, Python 220 KB, JavaScript 177 KB, HTML 26 KB, CSS 10 KB, Shell 6 KB
- **License:** MIT ([`LICENSE`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/LICENSE))

## Mission (per README)

"Make local civic problems visible, understandable, and easier to act on." CivicPatch is described as "an open-source civic participation concept" that helps residents:
- identify a local issue
- find the responsible public body
- find trustworthy public sources
- take a constructive next step

It starts with Massachusetts, where the coverage target is all 351 cities and towns ([README](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/README.md)).

The README is explicit about where the project stands. It is an "Early-stage public project," and the README "does **not** certify a production application, verified Massachusetts coverage, a functioning backend, a complete data pipeline, or a successful live deployment."

## Architecture

There are two parts:

1. **Product and data.** A Vite/TypeScript web app ([`src/`](https://github.com/onnxscibroccoli/civicpatch/tree/cd94213ec2707827aa178794e962e6a4ffc5b74d/src)) and a Massachusetts municipality candidate directory published with GitHub Pages. The directory is refreshed by [`refresh-ma-directory.yml`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/.github/workflows/refresh-ma-directory.yml) and checked by [`check-source-urls.yml`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/.github/workflows/check-source-urls.yml) and [`validate-data.yml`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/.github/workflows/validate-data.yml). Design documents: [`docs/ARCHITECTURE.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/ARCHITECTURE.md), [`docs/DATA-AND-TRUST.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/DATA-AND-TRUST.md), [`docs/AUTOMATED-INGESTION.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/AUTOMATED-INGESTION.md), [`docs/MASSACHUSETTS-COVERAGE.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/MASSACHUSETTS-COVERAGE.md), and [`docs/URL-HEALTH.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/URL-HEALTH.md).
2. **Bounded multi-agent development.** This is a GitHub Actions state machine ([`docs/AGENT-STATE-MACHINE.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/AGENT-STATE-MACHINE.md)) built from fixed, version-controlled workflows: `agent-dispatcher.yml`, `agent-task-ingest.yml`, `agent-gatekeeper.yml`, `bounded-autodev.yml`, `agent-alpha.yml`, and `deploy-pages.yml`. Per the README:
   - Model output goes to a draft PR.
   - A separately permissioned gatekeeper may merge **only** allowlisted Python source, test, and progress files, and only after independent CI and immutable-head checks pass.
   - Public data verification, workflow edits, credentials, and deployment logic are excluded from unattended promotion.
   - Pages has separate preview paths: `/alpha/`, `/beta/`, and production `/`.

## Evidence

**Tests**: 10 Python test modules in [`tests/`](https://github.com/onnxscibroccoli/civicpatch/tree/cd94213ec2707827aa178794e962e6a4ffc5b74d/tests), including:
- `test_ma_directory.py`
- `test_ma_ingestion.py`
- `test_source_url_health.py`
- `test_agent_task_ingest.py`
- `test_autodev.py`
- `test_alpha_workflow_contract.py`

There are also 14 Node/TS tests under `scripts/*.test.mjs` and `src/lib/**.test.ts`.

**CI**: latest `Validate CivicPatch data and report coverage` run succeeded on `cd94213` at 2026-10-28 11:11 EDT ([run 40713410326](https://github.com/onnxscibroccoli/civicpatch/actions/runs/40713410326)). On 2026-10-27/28, the dispatcher, task-ingestion, bounded-autodev, and Alpha workflows also succeeded on `cd94213`. A `Check source URL reachability` run on 2026-10-27 was **cancelled** ([Actions](https://github.com/onnxscibroccoli/civicpatch/actions)).

**Notable PRs**
- [#14](https://github.com/onnxscibroccoli/civicpatch/pull/14) (merged as `8172e14`, +847/−36, 18 files): handed development over to the bounded multi-agent state machine. The PR itself says "a successful pull_request build is not proof that chained workflow_dispatch, Pages preview routing or automatic merge permissions work."
- **The live chain is verified.** [`docs/AGENT-HANDOVER.md`](https://github.com/onnxscibroccoli/civicpatch/blob/cd94213ec2707827aa178794e962e6a4ffc5b74d/docs/AGENT-HANDOVER.md) lists five runs from 2026-10-17. All five were confirmed through the Actions API to have concluded **success**, between 02:27 and 02:28 EDT:
  - dispatcher [39009951716](https://github.com/onnxscibroccoli/civicpatch/actions/runs/39009951716)
  - task ingestion [39009956991](https://github.com/onnxscibroccoli/civicpatch/actions/runs/39009956991)
  - synthesis [39009966302](https://github.com/onnxscibroccoli/civicpatch/actions/runs/39009966302), which opened draft PR [#18](https://github.com/onnxscibroccoli/civicpatch/pull/18)
  - gatekeeper [39009983238](https://github.com/onnxscibroccoli/civicpatch/actions/runs/39009983238)
  - Pages deploy [39010015925](https://github.com/onnxscibroccoli/civicpatch/actions/runs/39010015925)
  
  PR #18 was merged by `app/github-actions` at 2026-10-17 02:28 EDT. The earlier recipe attempt [39009824757](https://github.com/onnxscibroccoli/civicpatch/actions/runs/39009824757) concluded **failure**, as the handover says, which shows a failed gate stopping promotion.
- The handover also records the operating boundaries:
  - **Least-privilege deploy:** a `contents:read` build job, separate from a `pages:write`/`id-token:write` deploy job.
  - **Schedule:** `cron: 19 2,8,14,20 * * *`.
  - **Budget:** "1,860 minutes… covers the worker only." The document warns that this is not the total monthly budget and that external LLM spend is not bounded by runner minutes.
  - **Recovery:** revert the problematic commit on `main` and re-run Pages. Don't force-push `agent/beta`.
  - **Stated limits:** the previews "do not constitute independent cloud environments." Branch protection, spending caps, and post-deploy health checks are listed as future work.
- [#26](https://github.com/onnxscibroccoli/civicpatch/pull/26), [#27](https://github.com/onnxscibroccoli/civicpatch/pull/27), and [#29](https://github.com/onnxscibroccoli/civicpatch/pull/29) are merged autonomous "[Agentic review] Next CivicPatch code-and-test increment" PRs. Main's HEAD `cd94213` is #29.
- [#19](https://github.com/onnxscibroccoli/civicpatch/pull/19): hardened Pages deployment token isolation. [#25](https://github.com/onnxscibroccoli/civicpatch/pull/25): limited URL-health probing to relevant changes, to save CI compute.
- [#5](https://github.com/onnxscibroccoli/civicpatch/pull/5)–[#9](https://github.com/onnxscibroccoli/civicpatch/pull/9): seeded and refreshed the Massachusetts registry. #9 added a regression guard for the Fall River 2026 committee PDF URL.

**History**: the first commit is `b1d6223`, "Export from Grok" (2026-10-16).

## Relevance to role

Requirement IDs refer to [JOB_ALIGNMENT.md](JOB_ALIGNMENT.md).

- **B4 automation and CI/CD (Strong):** a bounded multi-stage GitHub Actions pipeline, with the end-to-end run chain verified above. It includes an immutable-SHA gatekeeper and a fixed file allowlist.
- **C5 job scheduling (Partial):** a cron-scheduled dispatcher with a single active worker and per-job timeouts.
- **B10 / C9 security controls (Partial):** least-privilege separation of the deploy token (PR #19), private-network redirect rejection (folded into #14), and model output treated as untrusted.
- **B11 runbook-style documentation (Partial):** operator controls, pause and restore procedures, and stated limitations in the handover document.
- **Not relevant to:** AWS, Microsoft identity, or banking. This is a GitHub Pages and Actions project.

## Limitations and unknowns

- Per the README, candidate links and structural coverage "are **not** evidence of verified municipal services." How many of the 351 municipalities have verified sources is **Unknown**. See `docs/MASSACHUSETTS-COVERAGE.md` for the project's own metrics, which were not audited here.
- The web app's `package.json` name is `app-builder-workspace`, and its test script matches Helix's. That suggests a shared scaffold. Which parts of `src/` are CivicPatch-specific versus template code is **not verified**.
- Of the three closed PRs, [#12](https://github.com/onnxscibroccoli/civicpatch/pull/12) (private-network redirect rejection) and [#13](https://github.com/onnxscibroccoli/civicpatch/pull/13) (bounded test repair) were closed unmerged. Per #14, their changes were folded into #14.
- The Alpha self-developing site is an isolated experiment. Per the README, it publishes **before** running its smoke check, so failed experiments can be briefly live on `/alpha/`.
