# Current development and implementation architecture

## Current state

Historical discovery baseline (2026-10-31): main at `7f50348bf1370381615eaed91c02607fe41de2f5` contained only README.md. The initial documentation branch started from delivery/portfolio at `85fbf9d24954ecfdb5cbea30199e212c7daf2c61`, the then-unmerged PR #35 candidate. The owner subsequently directed development integration before independent review; see [the current policy](integration-policy.md). Acceptance evaluators remain unchanged.

The initial delivery tree contains 207 Markdown documents. Discovery covers all tracked file paths, module declarations, documentation, workflows, scripts, and tests. Source inspection is prioritized for recovery, identity, observability, and documentation tooling; it is not a line-by-line audit of every module. The generated inventory preserves module claims without promoting them to new verification.

See the [discovery and capability coverage report](audit.md) for the inventory and gaps.

## Legacy modernization checkpoint

The modernization increment catalogs all 223 current Markdown pages, including 210 formerly unstructured pages. Each legacy page receives a portal reading guide, searchable status, source relationships, terminology, operational limits, and an introductory learning link. Living source pages also receive concise introductions where doing so preserves evidence contracts. The 145 original documents listed in docs/metadata/preserved-records.json remain byte-for-byte unchanged, including evidence-bound README files; their reading guides are rendered from sidecar metadata.

This is an editorial migration, not fresh operational verification of every module. Archived records retain their historical claims and dates. New explanations do not certify cloud deployment, compliance, or production readiness. Metadata validation now requires coverage of every indexed page, valid dates, and existing local evidence references. The glossary adds 68 concise terminology definitions; full expert entries and external references for every additional term remain future work.

## Design decision

Considered MkDocs, a JavaScript application framework, and a small static builder. MkDocs is a mature Markdown/static-hosting option; its usual content layout would need adaptation for this repository's scattered evidence and README files. A full application adds more runtime complexity than the initial experience needs. This increment uses Python-Markdown, an HTML sanitizer, JSON Schema, and plain browser JavaScript: all Markdown stays at its existing source path, build output is static, and search scoring is inspectable. Tradeoff: the project owns its template, link rewriting, and search maintenance.

Data flow: Markdown plus sidecar metadata becomes sanitized HTML, search-index.json, metadata.json, and coverage.json. The browser reads the index locally and ranks token/alias matches. No model or query service is required. Navigation and document reading work without JavaScript; search requires it.

## Reproduce the portal

From the repository root, use Python 3.10+ and Node 20+. Dependency installation needs network access. Building and searching use no credentials. Output goes only to ignored dist/docs.

```bash
python3 -m venv /tmp/bank-docs-venv
. /tmp/bank-docs-venv/bin/activate
python3 -m pip install -r scripts/docs/requirements.txt
python3 -m unittest discover -s scripts/docs/tests
node --test scripts/docs/tests/search.test.mjs
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist/docs
```

Open `http://127.0.0.1:8000`. Stop the server with Ctrl+C. The generated output may be removed after review; do not remove source or evidence directories. Termux needs Python and Node installed; browser automation may require a desktop/CI runner. A localhost server does not publish to the internet.

## Quality and publishing

The documentation workflow pins Ubuntu 24.04 for compatibility with its pinned Playwright browser version, builds and tests on pull requests and documentation pushes, uploads a static-site artifact, and runs browser checks. Pages deployment is restricted to main, runs after validated main documentation pushes or manual deploy requests, and needs GitHub Pages configured with Actions. See [publishing steps](publishing.md). Pages was not enabled at baseline; this document does not claim a public deployment.

## Remaining work

- Maintain the completed metadata/reading-guide migration; all indexed pages require metadata. Historical record bytes are protected by a digest manifest.
- Expand glossary coverage, topic/audience navigation, and additional practical tutorials.
- Complete human keyboard, TalkBack/NVDA, zoom, and cognitive-accessibility reviews; automated checks are only partial evidence.
- Review legacy link and diagram findings, and add robust heading-anchor validation.
- Extend cross-repository retrieval only after separate authorization.
- Reconcile module registry limitations with newer source and independent reviews; preserve any conflicting claims for review.

## Agent restrictions

Follow the owner-directed [integration policy](integration-policy.md); independent review is deferred until after development integration. Do not alter cloud infrastructure. CI build results prove documentation checks only. See the [AI contract](ai.md) and [contribution standard](standards.md).
