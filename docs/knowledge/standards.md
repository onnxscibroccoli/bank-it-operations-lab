# Documentation contribution and metadata standard

## Purpose and contribution workflow

Meet readers at their current understanding. Explain why a topic matters, define its first unfamiliar terms, then progressively expose operational and engineering detail. Keep meaningful historical detail and original URLs.

For a new major page, add a Markdown document and an entry in `docs/metadata/pages.json`. Include everyday, operational, engineering, and expert explanations; prerequisites; expected results; troubleshooting; security and side effects; further learning; and agent guidance. Mark a section not applicable with a reason rather than inventing a lab.

## Metadata contract

The JSON schema in [schema.json](../metadata/schema.json) validates required fields. `lifecycle_status` describes development; `verification` independently describes evidence, scope, last_verified, and evidence references. Unknown dates stay null. Never auto-promote status. Each source_files entry must exist. Page ids must remain unique and stable.

Permitted lifecycle vocabulary: Concept, Proposed, Planned, In Development, Experimental, Simulated, Locally Verified, CI Verified, Integration Verified, Production Verified, Stable, Deprecated, Archived. These are not a ladder. Verification can also be Not established. Stable requires separately documented maintenance criteria; production claims require identified production evidence.

Legacy documents are rendered and indexed with an explicit unreviewed notice. They are not silently assigned a maturity level. Curated pages fail on broken local file links; legacy findings appear in coverage.json. Anchor validation and comprehensive legacy modernization remain work items.

## Accessible content rules

Use meaningful headings and link text. Define terms near their first use and link the glossary. Give every diagram an equivalent written account of its relationships. Label code fences and explain their effect before commands. Use simple table headers. Do not rely on color, hover, or pointer-only controls. Follow [WCAG 2.2](https://www.w3.org/TR/WCAG22/); automated checks cannot establish conformance.

## Validation and review

Run the commands in the [development guide](development.md). Review the generated coverage and accessibility reports. Record command, date, revision, environment, and limitations. Changes to source should identify affected documents, terminology, tutorial impact, and evidence freshness in the PR template. Reports flag likely omissions; unrelated code edits need not create artificial documentation changes.

External links are checked separately with timeouts and retries. Network failures are reported, not treated as proof that a destination is invalid. Review authoritative sources for operational and regulatory claims. Wikipedia provides supplementary introductions, not verification of local implementation.

## Page template

Start with a title and plain-English purpose. Add why it matters and a realistic example, then prerequisites, terminology, progressive depth, walkthrough if implemented, expected results, troubleshooting, security, source links, and agent restrictions. The generated status panel displays metadata directly, avoiding a second contradictory status declaration.

## Preserved records and legacy reading guides

Every indexed Markdown file needs an entry in docs/metadata/pages.json. Use reading_guide for context around preserved historical source; its fields are validated by schema.json. Keep terminology consistent with docs/metadata/terminology.json and the human glossary. last_reviewed is an editorial date, while verification.last_verified requires actual scoped evidence.

Files listed in docs/metadata/preserved-records.json are historical or evidence-bound inputs. Do not update their hashes merely to silence a test. Add a current explanation in sidecar metadata or a new document, preserving the original record. Keep NOT_EXECUTED banners at the top of hybrid runbooks.
