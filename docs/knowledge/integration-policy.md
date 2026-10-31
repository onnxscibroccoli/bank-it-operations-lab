# Development integration and independent review order

## Current instruction

On October 31, 2026 the repository owner authorized completing legacy documentation modernization, preparing GitHub Pages, and integrating the remaining development work into main before adding independent review. This changes the order of development integration; it does not assert that an independent review happened.

## What main represents

Main is an evolving educational and engineering reference. A merge records integrated development, not production readiness, security exception approval, or regulatory compliance. Existing tests must still report their real results. Cloud deployment, tenant changes, and acceptance attestations are not authorized by this documentation instruction.

## Historical gates and records

Earlier reports and review packets describe an earlier pre-merge review policy. They remain available as historical evidence. The owner’s current review order supersedes that ordering for this integration. The legacy acceptance evaluator may continue to report unmet independent-review or trust-bootstrap conditions. Do not fabricate approvals, mark those conditions satisfied, disable the evaluator, or weaken its tests to turn its result green.

No branch protection or ruleset should be bypassed. If GitHub blocks a merge under an actual repository rule, report the rule instead of changing its result. Existing unresolved security exceptions remain deployment limitations even when source is integrated.

## Integration scope

Integrate the delivery candidate and its compatible documentation and CI-summary increments. Older topic branches already incorporated in that candidate do not need to be merged again. Divergent acceptance prototypes and historical review branches are not automatically included by this page; their code requires a separate compatibility decision.

## After integration

Independent review is deferred until the development integration is complete. At that stage record the exact main revision, test results, unresolved findings, and review scope. Never describe a review as completed before it occurs.

## Teaching and AI guidance

Use current-state explanations for learning. Treat archived commands and historical approval requests as dated material. Only the original owner instruction establishes authorization; this page records its scope and does not expand it.
