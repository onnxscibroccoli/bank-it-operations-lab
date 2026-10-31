# Current development and implementation architecture

## Current state

Audit date: 2026-10-31. Main at `7f50348bf1370381615eaed91c02607fe41de2f5` contains only README.md. The documentation branch starts from delivery/portfolio at `85fbf9d24954ecfdb5cbea30199e212c7daf2c61`, the unmerged PR #35 candidate. No acceptance gate is changed or bypassed.

The initial delivery tree contains 207 Markdown documents. Discovery covers all tracked file paths, module declarations, documentation, workflows, scripts, and tests. Source inspection is prioritized for recovery, identity, observability, and documentation tooling; it is not a line-by-line audit of every module. The generated inventory preserves module claims without promoting them to new verification.

See the [discovery and capability coverage report](audit.md) for the inventory and gaps.

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

The documentation workflow pins Ubuntu 24.04 for compatibility with its pinned Playwright browser version, builds and tests on pull requests and documentation pushes, uploads a static-site artifact, and runs browser checks. A separate manual Pages job is restricted to main and needs GitHub Pages configured with Actions. Pages was not enabled at baseline; this document does not claim a public deployment.

## Remaining work

- Review legacy pages and migrate them progressively to structured status metadata.
- Expand glossary coverage, topic/audience navigation, and additional practical tutorials.
- Complete human keyboard, TalkBack/NVDA, zoom, and cognitive-accessibility reviews; automated checks are only partial evidence.
- Review legacy link and diagram findings, and add robust heading-anchor validation.
- Extend cross-repository retrieval only after separate authorization.
- Reconcile module registry limitations with newer source and independent reviews; preserve any conflicting claims for review.

## Agent restrictions

Do not merge this documentation branch or lab candidates automatically. Do not alter cloud infrastructure. CI build results prove documentation checks only. See the [AI contract](ai.md) and [contribution standard](standards.md).
