# Static asset and architecture inventory

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Find reliable explanations and keep them aligned with the repository as development continues. Good navigation and explicit limitations help beginners and experienced engineers use the same material.

For example: A contributor changes a module, locates the pages that reference it, and checks whether the explanation or evidence needs updating.

Key terms: **Markdown** means a text format for readable documents with headings, links, lists, and code. **Metadata** means structured information describing a page, such as its topic and verification scope. **Static site** means prepared web files served without an application backend.

**Before using this reference:** Documentation checks do not establish production behavior. Read the current integration policy before interpreting older acceptance instructions.

Start with the [plain-English learning path](../docs/knowledge/start.md) or [glossary](../docs/knowledge/glossary.md). [Current integration and review policy](../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


`assets.json` and `ARCHITECTURE.md` are derived from the committed CDK-synthesized templates in `evidence/aws/aws-remediation-vpc-rds/synth`. They are not a discovery scan of a live account. Source SHA-256 hashes bind every record to its input template.

Run `python3 inventory/generate.py --check` to detect drift. Run without `--check` to regenerate after reviewing template changes. Tests: `python3 -m unittest discover -s inventory/tests`.

References, GetAtt and DependsOn are shown. Parameter values, implicit service dependencies and Fn::Sub strings are not interpreted. The existing AWS synthesis workflow compares fresh output to committed templates; the inventory check then compares those templates to the generated files.
