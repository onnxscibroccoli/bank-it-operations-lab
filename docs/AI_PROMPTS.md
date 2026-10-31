# Focused AI prompts for this lab

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Find reliable explanations and keep them aligned with the repository as development continues. Good navigation and explicit limitations help beginners and experienced engineers use the same material.

For example: A contributor changes a module, locates the pages that reference it, and checks whether the explanation or evidence needs updating.

Key terms: **Markdown** means a text format for readable documents with headings, links, lists, and code. **Metadata** means structured information describing a page, such as its topic and verification scope. **Static site** means prepared web files served without an application backend.

**Before using this reference:** Documentation checks do not establish production behavior. Read the current integration policy before interpreting older acceptance instructions.

Start with the [plain-English learning path](knowledge/start.md) or [glossary](knowledge/glossary.md). [Current integration and review policy](knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


Choose **one prompt per task**. Supply the branch/SHA and the relevant file or Actions log. PR #7 is the preserved integration baseline; PR #35 is the newer delivery. If the tool cannot read a source, it must say so rather than infer its contents. Research is guidance, not executed evidence or independent approval.

## 20 GitHub Copilot prompts

1. Inspect this checkout's README and coordination/modules.json. Explain how AWS/CDK, Entra, PostgreSQL and integration checks fit together in five bullets. Cite paths; do not edit files.
2. Read scripts/validate-all.sh. List the Python-only steps separately from steps requiring Node or PostgreSQL. Give me only the first command appropriate to my reported failure.
3. Compare PR #7's exact head with delivery/portfolio. Separate baseline modules from later additions. Do not attribute PR #35 tests to PR #7; report any inaccessible source.
4. Read coordination/modules.json for the module I name. Show its owned paths, registered checks and limitations. Identify one next file to read.
5. Explain the distinction between historical records and runtime acceptance bindings in coordination/tasks.json. Do not treat a stored MET claim as authoritative.
6. Trace AC1 through scripts/ci/reviews.py and merge_eligibility.py. Explain exact-SHA review, reviewer permissions, allow-list and changes-requested behavior. Cite tests.
7. Trace candidate/main/tested-merge provenance through scripts/ci/provenance.py. Explain what a matching parent list proves and what tree-content verification adds on this checkout.
8. Read scripts/ci/verify_trusted_gate.py and the gate manifest. Explain a GATE HASHES REJECTED error without proposing a bypass or automatically trusting candidate changes.
9. Compare applied AWS cdk-nag suppressions with scripts/ci/check_exceptions.py and SECURITY_EXCEPTIONS.md. List mismatched rule/resource scopes; do not approve exceptions.
10. Walk through .github/workflows/aws-cdk.yml in order. Explain which step detects compile errors, security findings, self-logging, synth drift and hash mismatch.
11. For this failing AWS resource, trace the template logical ID to infra/aws-cdk/lib and its test. Propose one minimal fix with a meaningful regression check before editing.
12. Explain identity/entra/ca_validator.py, baseline.json and tests/entra. Separate synthetic policy behavior from claims that require live tenant evidence.
13. Read tests/integration/postgres/verify_evidence.py and selftest_harness.sh. Show how wrong versions and wrong failure reasons are rejected. Identify any unsupported success claim.
14. Read scenarios/incident and the integration workflow. Explain how fresh SIMULATION evidence differs from committed incident evidence and NOT_EXECUTED results.
15. Inspect .github/workflows/portfolio-validation.yml. List package dependencies and explain why a successful package does not satisfy merge eligibility.
16. Inspect operations/endpoint plan generation and Pester tests. Show what actually executes in CI and confirm that no generated plan is described as a tenant mutation.
17. Inspect governance/owner-auth on delivery/portfolio. Separate implemented signature verification from missing enrollment, revocation/conflict rules and gate activation. Never generate an owner approval.
18. Review README and reports/FINAL_REPORT.md against the current tree. Flag stale PR numbers, module counts, runtime prerequisites and execution claims. Suggest targeted documentation edits only.
19. Given this single Actions error, classify it as code, evidence, environment, trust or missing human decision. Cite the first useful log line and give one next action. Stop after that action.
20. Prepare a review checklist for PR #7 at the SHA I provide. Include candidate/base/tested merge, required jobs, independent review, exceptions, docs and unresolved blockers. Do not submit a review or merge.

## 10 Google Gemini research prompts

Ask for official AWS, Microsoft, PostgreSQL, GitHub or tool-maintainer sources, access dates and uncertainty. Keep recommendations distinct from behavior observed in this repository.

1. Research credential-free AWS CDK reference labs. Compare static synthesis, unit assertions and cdk-nag with what only a live deployment can prove. Apply the distinction to bank-it-operations-lab/infra/aws-cdk.
2. Using AWS documentation, analyze S3 access-log destination encryption and recursive self-logging. Explain which constraints should be tested in this lab and which exception claims need qualification.
3. Research AWS Backup service-role AssumeRole context keys. Does a backup-vault SourceArn condition actually work for RDS backup role assumption? Distinguish trust policies from SNS/KMS resource-policy examples; explicitly flag missing evidence.
4. Research Auto Scaling service-linked-role access to customer-managed EBS keys. Identify required crypto and grant permissions and deployment prerequisites relevant to infra/aws-network.
5. Using Microsoft documentation, explain what offline Entra Conditional Access fixtures can and cannot establish. Cover report-only policies, excluded emergency accounts and device-compliance scope.
6. Research PostgreSQL backup/restore compatibility and verification. Propose positive and negative controls for tests/integration/postgres, including mismatched tool/server versions and unexpected-success failures.
7. Research GitHub review dismissal, last-push approval and exact commit binding. Explain personal-repository constraints and why a second owner-controlled account is not independent technical review.
8. Research ways to anchor CI verifier/workflow trust outside an untrusted PR. Compare protected branches, pinned manifests and workflow controls; describe bootstrap and self-approval risks.
9. Research reproducible evidence bundles: producer versions, inputs, checksums, provenance and artifact retention. Explain why a checksum establishes integrity but not truthfulness.
10. Compare practices for low-overload technical documentation: short entry pages, progressive detail, resumable checkpoints and one-task workflows. Propose a repo navigator structure without making clinical treatment claims.

## 10 ChatGPT prompts

1. Use docs/REPO_NAVIGATOR.md to explain this lab in five plain-English bullets. End with one next action. Do not require me to read the full repository.
2. Summarize PR #7 at the exact SHA I provide. Separate its preserved baseline from PR #35's additions and distinguish historical checks from current evidence.
3. Turn this Actions failure into a small task card: observed error, likely source, one command, expected result and a stopping point. Do not invent a root cause.
4. Explain AC1–AC6 using docs/REVIEWER_GUIDE.md. For each, identify who decides, what automation verifies and what evidence is still missing.
5. Compare my README claim with the cited code and test output. Rewrite only unsupported wording, preserving STATIC_VALIDATED, SIMULATION, PLAN_ONLY and NOT_EXECUTED distinctions.
6. Design a regression test for the specific bug I describe in this repository. Explain how it fails before the fix and what behavior it protects; avoid tests that only repeat implementation details.
7. Help review this diff from scripts/ci. Focus on candidate-controlled trust, stale SHA evidence and false approvals. Return findings with file/line, consequence and smallest remedy.
8. Create a 15-minute session for one module in coordination/modules.json. Include one reading task, one validation task and a checkpoint note. Do not add unrelated cleanup.
9. Convert these review findings into an ordered checklist. Separate engineering fixes from owner risk decisions and independent approval. Never mark a blocker resolved merely because it was documented.
10. Write a short handoff from these observed results: branch/SHA, what changed, checks run, remaining limits and next single action. State unknowns and never imply background work will continue unless it is actually scheduled.

## Very short daily prompt

> Inspect my branch/SHA and one relevant Actions check. Tell me what it means in three bullets, give me one next action, and provide a safe stopping point. Do not edit or merge until the task is clear.

## PR #7-only prompt

> Inspect PR #7 at its exact current head. Explain its integrated modules and AC1–AC5 evidence in plain English. Keep PR #35 changes separate. Identify one review question and cite the file or run supporting it. Do not infer approval from old results.

## VS Code Copilot Chat starter

> Use the attached scripts/validate-all.sh, coordination/modules.json and my single error log. Confirm branch/SHA, locate the failing step, and show one next file to inspect. Give a short explanation before proposing an edit. Keep a resumable checkpoint note.
