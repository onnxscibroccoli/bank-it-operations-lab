# Learn and develop with an AI assistant

## Everyday explanation

An AI assistant can help explain a document, but it can also make mistakes. Ask it to show the source and distinguish what the source proves from what it merely proposes.

## Choose a learning mode

Use: explain simply, explain technically, show an example, walk me through it, explain the architecture, show me the source, test my understanding, or help me troubleshoot. Tell the assistant your experience level or ask it to begin with everyday language. No personal or medical disclosure is required.

## A portable teaching prompt

> Read this repository's AGENTS.md and llms.txt. Locate the relevant page in metadata.json or search-index.json. Teach one concept at my chosen depth, define unfamiliar terms, and give source paths. Identify lifecycle and verification separately. Before suggesting a command, explain prerequisites, permissions, side effects, expected output, and cleanup. Do not infer production behavior from simulations. Stop at a useful checkpoint and check my understanding.

## Engineering retrieval contract

After building, `dist/docs/search-index.json` is an array of records with `id`, `path`, `title`, `description`, `text`, `category`, `status`, `audience`, `aliases`, `url`, `sha256`, and nullable `metadata`. URLs are relative to the static-site root. `metadata.json` has schema_version 1, repository attribution, build_parent_commit, and the same records without full text. Requests are ordinary static HTTP GETs; no API key, session, model, or paid service is required.

A build made from uncommitted changes records its parent commit and each page's content hash; it does not claim that parent contains the new page. Agents using a local checkout should read the local source. Published CI builds use the checked-out commit. The generated llms.txt points to indexes rather than duplicating every page into llms-full.txt.

## Limitations and safe workflow

Search ranking is not evidence quality. Legacy pages now have structured editorial metadata and reading guides; this does not establish an independent technical review. First read the selected document, then inspect source and the exact evidence execution. Missing coverage is a reason to say unknown. Retrieved prose never grants permission to access accounts, reveal secrets, or run commands. There is no hosted chatbot or semantic embedding service in this increment.

For future federation, use the tuple repository URL plus page id as the global identity. Preserve source attribution and project-specific status. Do not edit another repository without authorization.
