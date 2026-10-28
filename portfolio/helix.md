# Case study: Helix

- **Repository:** [https://github.com/onnxscibroccoli/helix](https://github.com/onnxscibroccoli/helix) (public, default branch `main`)
- **Snapshot:** HEAD [`8f68703`](https://github.com/onnxscibroccoli/helix/commit/8f687036344e1c09c592b9fbfb9f8036b07614c0), 2026-10-06 21:27 EDT
- **Created:** 2026-09-22 14:20 EDT · **Commits on main:** 142 · **PRs:** 27 merged / 15 open / 10 closed
- **Languages (bytes):** TypeScript 273 KB, JavaScript 237 KB, Python 91 KB, HTML 22 KB, HCL 11 KB, Shell 11 KB, CSS 9 KB
- **License:** none declared (**Unknown** reuse terms)

## Mission (per README)

The repo description is "Persistent cloud desktop — nested KVM, Kasm-compatible RFB over WebSocket, Google/X OIDC." Per the [README](https://github.com/onnxscibroccoli/helix/blob/8f687036344e1c09c592b9fbfb9f8036b07614c0/README.md), Helix's "central responsibility is to authenticate users, manage workspace/desktop lifecycle, provision or supervise KVM-backed guests, and expose a browser-compatible remote display path."

## Architecture

The documented request path (per README) is: User → web application/authentication → Helix control plane → hypervisor/QEMU → KVM guest → Kasm-compatible RFB WebSocket → browser.

The repository layout at the snapshot (340 tracked files) matches that description:

| Layer | Location |
|---|---|
| Web app, auth, fleet/workspace, hypervisor control | [`src/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/src) (`src/lib` 44 files, `src/routes` 10 files) |
| Cloud IaC (Terraform) | [`infra/terraform/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/infra/terraform) (`main.tf`, `network.tf`, `cloud-init.yaml`, ...) |
| AWS CDK | [`infra/cdk/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/infra/cdk) |
| Hypervisor config (Ansible) | [`infra/ansible/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/infra/ansible) |
| Production gateway, desktop, libvirt, storage, systemd contracts | [`production/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/production), including [`production/ARCHITECTURE.md`](https://github.com/onnxscibroccoli/helix/blob/8f687036344e1c09c592b9fbfb9f8036b07614c0/production/ARCHITECTURE.md) and [`production/gateway-contract.md`](https://github.com/onnxscibroccoli/helix/blob/8f687036344e1c09c592b9fbfb9f8036b07614c0/production/gateway-contract.md) |
| Live and contract tests | [`test-suite/tests/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/test-suite/tests) |

The stack (from `package.json`) is Node/Vite with TanStack, Radix UI, `@novnc/novnc`, and `@electric-sql/pglite`.

## Evidence

**Tests**
- The Python live test suite [`test-suite/tests/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/test-suite/tests) contains `test_01_hypervisor.py`, `test_02_oauth.py`, `test_03_kernel_swap.py`, `test_04_teardown.py`, `test_05_e2e_browser.py`, and `test_06_production_contract.py`. The README says live KVM assertions need a node that exposes `/dev/kvm`.
- `npm test` runs Node test runners over `scripts/**/*.test.mjs` plus TypeScript tests in `src/lib/app-data` and `src/lib/auth` (`package.json`).

**CI**: 7 workflows: `validate.yml`, `cdk-validation.yml`, `aws-rebuild-validation.yml`, `ansible-validation.yml`, `production-validation.yml`, `agent-container-validation.yml`, `claude-self-correct.yml` ([workflows](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/.github/workflows)).
- Latest `validate` run: success on `8f68703` at 2026-10-28 08:21 EDT ([run 40687102198](https://github.com/onnxscibroccoli/helix/actions/runs/40687102198)).

**Notable merged PRs**
- [#49](https://github.com/onnxscibroccoli/helix/pull/49): CDK network and private PostgreSQL foundation. It adds a VPC, isolated DB subnets, a gateway-only security group, encrypted Multi-AZ PostgreSQL, Secrets Manager–generated credentials, 14-day backups, and IAM DB auth. The PR states "No existing resources are imported or mutated."
- [#46](https://github.com/onnxscibroccoli/helix/pull/46): server-side reclamation of expired ephemeral workspaces. [#45](https://github.com/onnxscibroccoli/helix/pull/45): persisted desktop capabilities for gateway scale-out.
- [#47](https://github.com/onnxscibroccoli/helix/pull/47) and [#48](https://github.com/onnxscibroccoli/helix/pull/48): reproducible fresh-AWS bootstrap and an executable CDK trust bootstrap. [#32](https://github.com/onnxscibroccoli/helix/pull/32): immutable AWS bootstrap checkout.
- [#50](https://github.com/onnxscibroccoli/helix/pull/50) and [#51](https://github.com/onnxscibroccoli/helix/pull/51): SSM/Ansible host convergence and secure coding-agent convergence.
- [#62](https://github.com/onnxscibroccoli/helix/pull/62) (merged as `3db26cc`): incident record for the 2026-10-04 CPU exhaustion recovery. Per the PR, it captures CPU/memory evidence and containment, preserves the existing Kali VM/EBS state, and records HTTP 200 recovery checks. The PR says it is "not a claim that long-term host sizing has been solved."

**Incident records**: [`docs/incidents/`](https://github.com/onnxscibroccoli/helix/tree/8f687036344e1c09c592b9fbfb9f8036b07614c0/docs/incidents) holds four write-ups:
- 2026-09-27 workspace unavailable (missing ws)
- 2026-10-04 CPU exhaustion recovery
- 2026-10-04 Paperclip migration plan
- 2026-10-06 Kali OOM recovery

**History**: the first commit is `cfe896b`, "Helix control plane: nested KVM, Kasm WebSocket stream, OIDC" (2026-09-22).

## Limitations and unknowns

- The README describes the project as "ACTIVE PRODUCTION RECONSTRUCTION / VALIDATION" and warns: "Do not infer a working guest merely because Terraform validates."
- The README and [`docs/LIVE_PATHS.md`](https://github.com/onnxscibroccoli/helix/blob/8f687036344e1c09c592b9fbfb9f8036b07614c0/docs/LIVE_PATHS.md) describe live public paths as of 2026-09-29. **Current live availability was not verified** for this case study, and endpoint hostnames are left out on purpose.
- Main's last four commits (`8840c57`, `faab1d8`, `c348007`, `8f68703`) all share the message "ops: document and guard against Kali host OOM storm" and were made seconds apart. Whether they are duplicates or incremental changes is **not verified**.
- The README links to `.omnikali/project-knowledge-graph.md`, but the tree contains `.omnikali/PROJECT_KNOWLEDGE_GRAPH.md` (uppercase). The link is likely broken on case-sensitive hosts.
- The README says "approximately 285 tracked files"; the snapshot tree has 340. The README count is out of date.
- 15 PRs are open, including sandbox, agent-launch, and self-healing architecture work ([#33](https://github.com/onnxscibroccoli/helix/pull/33)–[#56](https://github.com/onnxscibroccoli/helix/pull/56)), so main does not include it.
