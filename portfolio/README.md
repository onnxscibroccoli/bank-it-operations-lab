# Portfolio case studies

Documentation-only case studies for five projects in the `onnxscibroccoli` GitHub account. Each one covers the project's stated mission, its architecture, the evidence you can check (files, commits, PRs, CI runs), and its limits.

## Ground rules

- **Source-grounded.** Every claim links to a file, commit, PR, or Actions run. A claim that comes only from a project's own README is labeled **"per README"**. It shows what the project says about itself, not what was checked independently.
- **Unknowns are marked.** Anything that wasn't verified while writing these pages is labeled **Unknown / not verified**.
- **No secrets.** These pages contain no credentials, tokens, keys, or old credential material. They also leave out live endpoint hostnames on purpose. Where a source document mentions such things, these pages link to the document and don't copy from it.
- **Point-in-time snapshot.** Facts were collected on 2026-10-28 (America/New_York) at the HEAD commits listed below. Later changes in the source repos are not reflected.

## Case studies

| Project | Repository | Snapshot HEAD | Role in the portfolio |
|---|---|---|---|
| [Grasshopper](grasshopper.md) | [onnxscibroccoli/Grasshopper](https://github.com/onnxscibroccoli/Grasshopper) | [`3eef009`](https://github.com/onnxscibroccoli/Grasshopper/commit/3eef009aa4a88f6d81dbd082cd35b90379929518) | Reference agent control plane (locks, tasks, recovery, evidence-gated reconstruction) |
| [Helix](helix.md) | [onnxscibroccoli/helix](https://github.com/onnxscibroccoli/helix) | [`8f68703`](https://github.com/onnxscibroccoli/helix/commit/8f687036344e1c09c592b9fbfb9f8036b07614c0) | Cloud desktop control plane: auth, KVM guests, browser remote display, IaC |
| [Broccoli Core](broccoli-core.md) | [onnxscibroccoli/broccoli-core](https://github.com/onnxscibroccoli/broccoli-core) | [`f66678e`](https://github.com/onnxscibroccoli/broccoli-core/commit/f66678ea9749c6c22519028c39dc00d5c9e3bae1) | Android/Termux automation runtime and hybrid mTLS controller (oldest lineage) |
| [CivicPatch](civicpatch.md) | [onnxscibroccoli/civicpatch](https://github.com/onnxscibroccoli/civicpatch) | [`cd94213`](https://github.com/onnxscibroccoli/civicpatch/commit/cd94213ec2707827aa178794e962e6a4ffc5b74d) | Open civic-information project with bounded GitHub Actions multi-agent development |
| [OmniKali](omnikali.md) | [onnxscibroccoli/omnikali](https://github.com/onnxscibroccoli/omnikali) | [`a5faf9b`](https://github.com/onnxscibroccoli/omnikali/commit/a5faf9b82bedb0057cb3164bebf190bfa199b446) | Fail-closed, health-aware public discovery door (GitHub Pages) |

## How the projects relate (per README)

The Broccoli Core, Grasshopper, Helix, and OmniKali READMEs all point to a shared cross-repository knowledge graph tagged `OMNIKALI-KG-2026-09-28`. Each README links to a `.omnikali/` graph file. Here is how each README describes its own role:

- **Broccoli Core** calls itself "an important ancestor and experimental laboratory for the agent-control lineage, not the current production source of truth" ([README](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/README.md)).
- **Helix** calls itself "the cloud/hypervisor control-plane line, not merely a web UI" ([README](https://github.com/onnxscibroccoli/helix/blob/8f687036344e1c09c592b9fbfb9f8036b07614c0/README.md)).
- **Grasshopper** calls itself "the formal bridge between validated production behavior and an agent-reproducible OmniKali control plane" ([README](https://github.com/onnxscibroccoli/Grasshopper/blob/3eef009aa4a88f6d81dbd082cd35b90379929518/README.md)).
- **OmniKali** (`omnikali` repo) calls itself "OmniKali's stable public name and health-aware discovery layer, not the desktop implementation" ([README](https://github.com/onnxscibroccoli/omnikali/blob/a5faf9b82bedb0057cb3164bebf190bfa199b446/README.md)).
- **CivicPatch** is a separate product. Its README does not reference the OmniKali graph. What it shares with the others is an engineering approach: bounded agent automation behind explicit gates.

## Snapshot metrics (default branch, 2026-10-28)

Commit counts come from the GitHub commits API on the default branch. PR counts cover all states and come from `gh pr list --state all`. Language breakdowns come from the GitHub languages API, which measures bytes, not lines.

| Repo | Created (UTC) | Commits | PRs (merged / open / closed) | Top languages (bytes) | Workflows | License |
|---|---|---|---|---|---|---|
| Grasshopper | 2026-09-26 | 336 | 114 / 54 / 12 | JavaScript, Python, Shell, HCL, Kotlin | 18 | none declared |
| helix | 2026-09-22 | 142 | 27 / 15 / 10 | TypeScript, JavaScript, Python, HTML, HCL | 7 | none declared |
| broccoli-core | 2026-07-18 | 241 | 9 / 15 / 0 | Python, Shell, Roff, Java, Kotlin | 3 | none declared |
| civicpatch | 2026-10-16 | 88 | 20 / 1 / 3 | TypeScript, Python, JavaScript, HTML | 9 | MIT |
| omnikali | 2026-09-21 | 698 | 2 / 5 / 0 | HTML, JavaScript | 2 | none declared |

Most of omnikali's commits are automated `chore: refresh endpoint.json from public health probe` commits made by its probe workflow. They are not hand-written changes.

## Job alignment

[JOB_ALIGNMENT.md](JOB_ALIGNMENT.md) maps every requirement of the target IT Manager posting to evidence in these case studies. Each requirement is marked Strong, Partial, or Gap. The requirement IDs and wording come from [`docs/JOB_REQUIREMENTS_MATRIX.md`](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/31b69db90838f59bfe28f8214dfc51a1c4ffd429/docs/JOB_REQUIREMENTS_MATRIX.md) (draft PR [#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12)). Result: 4 Strong, 20 Partial, 14 Gap. Each case study also has a short **Relevance to role** section.

## Cross-cutting gaps

- **Tests not re-run.** No case study re-runs a project's test suite. Test results come from each project's CI runs or its own README claims.
- **Live records not re-observed.** Grasshopper's production evidence documents and Helix's incident records were read in full, but the live systems they describe were not checked again.
- **AI-agent authorship.** Much of the work in these repositories was produced by AI coding agents under the owner's direction. The evidence shows directed and operated systems, not hand authorship of every change. See the caveats in [JOB_ALIGNMENT.md](JOB_ALIGNMENT.md).
- **Licensing.** Only CivicPatch declares a license, so reuse terms for the other four repositories are **Unknown**.
- **Resolved since the first draft:**
  - Helix's four same-message commits turned out to be four distinct files.
  - CivicPatch's 2026-10-17 live run chain is now verified.
  - Grasshopper's production evidence documents have been read and summarized.
