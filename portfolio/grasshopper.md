# Case study: Grasshopper

- **Repository:** [https://github.com/onnxscibroccoli/Grasshopper](https://github.com/onnxscibroccoli/Grasshopper) (public, default branch `main`)
- **Snapshot:** HEAD [`3eef009`](https://github.com/onnxscibroccoli/Grasshopper/commit/3eef009aa4a88f6d81dbd082cd35b90379929518), 2026-10-19 21:01 EDT (2026-10-20 01:01 UTC)
- **Created:** 2026-09-25 21:25 EDT · **Commits on main:** 336 · **PRs:** 114 merged / 54 open / 12 closed
- **Languages (bytes):** JavaScript 335 KB, Python 114 KB, Shell 87 KB, HCL 10 KB, Kotlin 10 KB, PL/pgSQL 2 KB
- **License:** none declared (**Unknown** reuse terms)

## Mission (per README)

Grasshopper describes itself as "the clean, reproducible reference implementation of OmniKali: a provider-neutral agent control plane for managing agents, tasks, locks, resources, state, recovery, and execution environments." Its stated north star is that "an authorized agent should eventually be able to reproduce the platform from source with no undocumented operator steps" ([README.md](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/README.md)).

## Architecture

Per the README, the local reference control plane implements agent registration, resource declaration, durable state, exclusive locks, asynchronous task execution, task recovery/reconciliation, deterministic export/import, an authenticated control-plane client, an MCP facade, and executor boundaries. Every source file the README names exists at the snapshot commit:

| Concern | File |
|---|---|
| Domain contracts | [`src/model.mjs`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/src/model.mjs) |
| Atomic state store | [`src/store.mjs`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/src/store.mjs) |
| Execution interface | [`src/executor.mjs`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/src/executor.mjs) |
| Lifecycle / control plane | [`src/control-plane.mjs`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/src/control-plane.mjs) |
| Authenticated client | [`src/clients/grok-control-plane-client.mjs`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/src/clients/grok-control-plane-client.mjs) |
| MCP interface | [`src/mcp/grok-control-plane-tools.mjs`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/src/mcp/grok-control-plane-tools.mjs) |
| CLI | [`bin/omnikali.mjs`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/bin/omnikali.mjs) |

Governance documents an agent must read before making large changes: [`IMPLEMENTATION_SEED.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/IMPLEMENTATION_SEED.md), [`BASE_SYSTEM_PROTECTION.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/BASE_SYSTEM_PROTECTION.md), [`docs/SECURITY_PHASE_MODEL.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/SECURITY_PHASE_MODEL.md), and [`docs/AGENTIC_GITHUB_AUTOMATION.md`](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/docs/AGENTIC_GITHUB_AUTOMATION.md).

Top-level layout at the snapshot (354 tracked files): `docs/` (84), `scripts/` (81), `test/` (78), `reference/` (25), `src/` (19), `.github/` (18), `infra/` (15), `schemas/` (8).

## Evidence

**Tests**
- `package.json` defines `npm test` as `node --test test/*.test.mjs`. There are 35 `test/*.test.mjs` files at the snapshot ([`test/`](https://github.com/onnxscibroccoli/Grasshopper/tree/3eef009aa4a88f6d81dbd082cd35b90379929518/test)).
- Live-acceptance scenarios live in [`scripts/live-acceptance/scenarios/`](https://github.com/onnxscibroccoli/Grasshopper/tree/3eef009aa4a88f6d81dbd082cd35b90379929518/scripts/live-acceptance/scenarios): `normal_exec`, `worker_termination`, `stale_lease_reclaim`, `replacement_completion`, `gateway_restart`, `network_interrupt`, `db_failure`, `duplicate_fencing`. The fencing scenarios include fixtures such as `stale-owner-fenced.json`.

**CI**: 18 workflows in [`.github/workflows/`](https://github.com/onnxscibroccoli/Grasshopper/tree/3eef009aa4a88f6d81dbd082cd35b90379929518/.github/workflows), including `reference-tests.yml`, `bist.yml`, `agentic-reproducibility.yml`, `production-merge-gate.yml`, `security-phase-contract.yml`, and several `ollama-ci-*` workflows.
- Latest `reference-tests` run: success on `4e5525c` at 2026-10-28 05:50 EDT ([run 40667390721](https://github.com/onnxscibroccoli/Grasshopper/actions/runs/40667390721)). That SHA is not main's HEAD; which branch it came from is **Unknown**.
- On 2026-10-28, `BIST`, `Agentic Development Loop`, `Overnight test chain`, and `Ollama CI Observatory` all reported success against main HEAD `3eef009` ([Actions](https://github.com/onnxscibroccoli/Grasshopper/actions)).

**Notable PRs**
- [#204](https://github.com/onnxscibroccoli/Grasshopper/pull/204) (merged as `3eef009`): phone action envelope contract `{device_id, tool, argv, mutating, request_id}` with a fail-closed `decide()` that returns Allow/Block/Escalate. The read-only allowlist is `id`, `getprop`, `whoami`, and the PR adds 15 unit tests. The PR says it is "not wired to broccoli-core or any device; no live mutate." (+85/−0, 3 files)
- [#193](https://github.com/onnxscibroccoli/Grasshopper/pull/193) (merged): containerized Ollama CI self-test, bounded repair, and a workflow-failure observatory.
- [#198](https://github.com/onnxscibroccoli/Grasshopper/pull/198)–[#203](https://github.com/onnxscibroccoli/Grasshopper/pull/203) (merged 2026-10-19): orchestration handoff and Android device evidence records, documentation only.
- Open, unmerged work includes the mTLS Android controller edge client ([#197](https://github.com/onnxscibroccoli/Grasshopper/pull/197)), signed OCI node identity ([#186](https://github.com/onnxscibroccoli/Grasshopper/pull/186)), and a series of Android control-evidence adapters ([#174](https://github.com/onnxscibroccoli/Grasshopper/pull/174)–[#184](https://github.com/onnxscibroccoli/Grasshopper/pull/184)).

**Release**: `broccoli-companion-bootstrap-v0.2.0-20261013`, published 2026-10-13 16:07 EDT ([releases](https://github.com/onnxscibroccoli/Grasshopper/releases)).

**History**: the first commit is `8993248`, "chore: initialize Grasshopper reference implementation" (2026-09-25 21:53 EDT).

## Limitations and unknowns

- The README itself lists these as unproven: "actual reboot survival, authenticated Android/operator access, production device scopes, off-host backup recovery, and complete authenticated desktop acceptance." It also says clean-host production reproduction "remains a separate gate."
- Production acceptance "requires the appropriate credentials and authorized infrastructure and must not be simulated by local fixture tests" (per README). These case studies did not run any live-acceptance scenario.
- The test suite was **not re-run independently** for this case study. Pass/fail status comes from GitHub Actions only.
- 54 PRs are open. Many of them are unmerged feature work, so the main branch does not include those capabilities.
- The README links to `.omnikali/project-knowledge-graph.md`, which exists here. Its contents were not reviewed.
