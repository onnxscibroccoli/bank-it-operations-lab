# Case study: OmniKali (public door)

- **Repository:** [https://github.com/onnxscibroccoli/omnikali](https://github.com/onnxscibroccoli/omnikali) (public, default branch `main`)
- **Snapshot:** HEAD [`a5faf9b`](https://github.com/onnxscibroccoli/omnikali/commit/a5faf9b82bedb0057cb3164bebf190bfa199b446), 2026-10-28 08:52 EDT
- **Created:** 2026-09-21 18:03 EDT · **Commits on main:** 698, mostly automated probe refreshes · **PRs:** 2 merged / 5 open
- **Languages (bytes):** HTML 12.8 KB, JavaScript 2.4 KB · **Tracked files:** 26
- **License:** none declared (**Unknown** reuse terms)

> **Scope note:** "OmniKali" is also the umbrella name for the wider platform lineage (see Grasshopper, Helix, and the private `kali-node` and `grasshopper-kubernetes` repos). This case study covers only the public `omnikali` repository. The private repositories are out of scope and were not reviewed.

## Mission (per README)

The repo description is "Permanent GitHub Pages door for OmniKali Track B. Health-aware discovery only — not the Kali VM, not omnikali-link." The [README](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/README.md) states that the repository "implements **service discovery and safe public routing**, not the workstation itself." Its key rule is: "A healthy local loopback service is not enough to publish an external endpoint."

## Architecture

- [`index.html`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/index.html) is the public door. It reads [`endpoint.json`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/endpoint.json), adds a cache-busting timestamp, and health-probes candidate origins. It shows a connect target only when the expected health or readiness condition holds (per README).
- [`.github/scripts/probe-endpoint.mjs`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/.github/scripts/probe-endpoint.mjs), run by [`probe.yml`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/.github/workflows/probe.yml), re-reads `endpoint.json` from GitHub's network and calls each candidate's `/api/public/health`. It uses an 8-second timeout and `redirect: "manual"`, and it rejects any of these:
  - non-200 responses
  - non-JSON responses
  - a Cloudflare "Port … is not found" body
  - a body where `service !== "omnikali"`
  
  A candidate counts as live only if `rfb === true` or `status === "ready"`.
- [`scripts/validate-endpoint-record.mjs`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/scripts/validate-endpoint-record.mjs) and its test [`scripts/validate-endpoint-record.test.mjs`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/scripts/validate-endpoint-record.test.mjs) were added in PR #2. They reject non-HTTPS, private, and loopback endpoints.
- [`pages.yml`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/.github/workflows/pages.yml) publishes the site.
- [`.github/agents/`](https://github.com/onnxscibroccoli/omnikali/tree/a5faf9b82bedb0057cb3164bebf190bfa199b446/.github/agents) holds agent contracts: `connection-machine`, `ingress`, `kvm`, `nats`, `orchestrator`, `pages`, `recovery`, `supervisor`, `swarm`.

## Evidence

- **CI**: `Probe OmniKali gateway` runs about hourly. On 2026-10-28 the probe succeeded repeatedly; the latest is [run 40691477149](https://github.com/onnxscibroccoli/omnikali/actions/runs/40691477149) on `67108f2`, at 2026-10-28 08:52 EDT. Each successful refresh commits `chore: refresh endpoint.json from public health probe`.
- **Merged PRs:**
  - [#1](https://github.com/onnxscibroccoli/omnikali/pull/1): "Fix OmniKali public door for live gateway"
  - [#2](https://github.com/onnxscibroccoli/omnikali/pull/2) (merged as `86f2532`, +51/−0): "Co-develop: add fail-closed endpoint validation"
- **Open PRs:**
  - [#6](https://github.com/onnxscibroccoli/omnikali/pull/6): "fix: probe must not rewrite endpoint.json when nothing changed." This would cut down the automated commit churn.
  - [#7](https://github.com/onnxscibroccoli/omnikali/pull/7): retire direct physical Rish launch docs
  - [#3](https://github.com/onnxscibroccoli/omnikali/pull/3)–[#5](https://github.com/onnxscibroccoli/omnikali/pull/5): architecture and evidence records
- **Docs:**
  - [`docs/ARCHITECTURE_VERIFICATION_2026-09-29.md`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/docs/ARCHITECTURE_VERIFICATION_2026-09-29.md)
  - [`docs/PRODUCTION_READINESS.md`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/docs/PRODUCTION_READINESS.md)
  - [`docs/LIVE_PATHS.md`](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/docs/LIVE_PATHS.md)
- **History**: the first commit is `3d5743a`, "Initial commit" (2026-09-21).

## Relevance to role

Requirement IDs refer to [JOB_ALIGNMENT.md](JOB_ALIGNMENT.md).

- **B5 monitoring (Partial):** a scheduled external health probe with fail-closed criteria. It requires HTTP 200 and JSON with the expected service identity, rejects Cloudflare "port not found" bodies, and does not follow redirects. It publishes a target only when the probe establishes health. There is no alerting or ticketing.
- **B10 secure configuration (Partial):** endpoint-record validation that rejects non-HTTPS, private, and loopback targets (PR #2).
- **C5 job scheduling and CI/CD (Partial):** an hourly probe workflow plus Pages publication.
- **Not shown:** any workstation or infrastructure operation. This repository is the discovery layer only.

## Limitations and unknowns

- This repository is only a discovery layer. It does not prove the desktop or workstation behind it works. The README itself says to distinguish "QEMU is running" from "RFB is usable," and "gateway is reachable" from "authenticated desktop is usable."
- A successful probe run means the workflow finished. Whether the gateway was healthy at a given time can only be read from the committed `endpoint.json` history. **Current gateway health was not checked** for this case study, and the endpoint record is linked, not copied.
- The README says "Approximately 20 tracked files"; the snapshot has 26.
- The README links to `.omnikali/project-knowledge-graph.md`, but the tree contains `.omnikali/PROJECT_KNOWLEDGE_GRAPH.md` (uppercase). The link is likely broken.
- The commit count of 698 is inflated by automated probe commits and is not a measure of development effort. Open PR #6 addresses the churn.
