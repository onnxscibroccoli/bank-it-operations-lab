# Learn and develop with an AI assistant

## Everyday explanation

An AI assistant can help explain a document, but it can also make mistakes. Ask it to show the source and distinguish what the source proves from what it merely proposes.

## Choose a learning mode

Use: explain simply, explain technically, show an example, walk me through it, explain the architecture, show me the source, test my understanding, or help me troubleshoot. Tell the assistant your experience level or ask it to begin with everyday language. No personal or medical disclosure is required.

## A portable teaching prompt

> Read this repository's AGENTS.md and llms.txt. Locate the relevant page in metadata.json or search-index.json. Teach one concept at my chosen depth, define unfamiliar terms, and give source paths. Identify lifecycle and verification separately. Before suggesting a command, explain prerequisites, permissions, side effects, expected output, and cleanup. Do not infer production behavior from simulations. Stop at a useful checkpoint and check my understanding.

## Engineering retrieval contract

After building, `dist/docs/search-index.json` is an array of records with `id`, `path`, `title`, `description`, `text`, `category`, `status`, `audience`, `aliases`, `url`, `sha256`, `owner_module`, `last_reviewed`, and `metadata`. `owner_module` is the registry module whose path contains the page. URLs are relative to the static-site root. `metadata.json` has schema_version 1, repository attribution, build_parent_commit, and the same records without full text. Requests are ordinary static HTTP GETs; no API key, session, model, or paid service is required.

A build made from uncommitted changes records its parent commit and each page's content hash; it does not claim that parent contains the new page. Agents using a local checkout should read the local source. Published CI builds use the checked-out commit. The generated llms.txt points to indexes rather than duplicating every page into llms-full.txt.

## What exists for AI use, and what does not

These are the only AI-facing capabilities in this repository. Each is a static file or written guidance:

| Capability | Where | What it is |
|---|---|---|
| Agent instructions | [AGENTS.md](../../AGENTS.md) | Reading order, constraints and documentation check commands for coding agents |
| Plain-text index | root [llms.txt](../../llms.txt) and the generated `llms.txt` in the built site | Pointers to the indexes; no full-text copy |
| Search index | `search-index.json` in the built site | Every page's plain text, status, audience levels, aliases and owning module |
| Page metadata | `metadata.json` in the built site, from [pages.json](../metadata/pages.json) | The same records without full text, plus the build commit |
| Prompt collection | [AI prompts](../AI_PROMPTS.md) | 40 copy-and-paste prompts for GitHub Copilot, Gemini and ChatGPT. They are text you paste into those tools, not integrations |
| Teaching prompt | the portable prompt above | A prompt to start a source-grounded lesson |

The built site, including these indexes, is public at <https://onnxscibroccoli.github.io/bank-it-operations-lab/> (deployed from main `30e0a83` on 2026-10-31; `search-index.json`, `metadata.json` and `llms.txt` returned HTTP 200 on 2026-11-03). An assistant that can fetch web pages can read them there. Otherwise it can read them from a local build.

There is **no** hosted chatbot, no "ask AI" box on the site, no embedding or vector index, no MCP server, no API, and no model call anywhere in the build or search. Search ranking is word and alias matching in [search-core.js](../../scripts/docs/search-core.js). Any feature not in the table above does not exist.

## Limitations and safe workflow

Search ranking is not evidence quality. Legacy pages now have structured editorial metadata and reading guides; this does not establish an independent technical review. First read the selected document, then inspect source and the exact evidence execution. Missing coverage is a reason to say unknown. Retrieved prose never grants permission to access accounts, reveal secrets, or run commands. There is no hosted chatbot or semantic embedding service in this increment.

For future federation, use the tuple repository URL plus page id as the global identity. Preserve source attribution and project-specific status. Do not edit another repository without authorization.
