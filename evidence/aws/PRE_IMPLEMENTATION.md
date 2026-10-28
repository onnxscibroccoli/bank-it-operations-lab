# BANK-AWS-001 — Pre-implementation record

- Worker identity: Bank IT Lab AWS CDK agent (id 91cb33dd-f3cd-4d71-b50b-9de09ccd6451)
- Checkout path: /workspace/bank-it-operations-lab
- Branch: bank-aws-001
- Starting commit: none, fresh `git init` (no remote repository found)
- Recorded: 2026-10-27 (America/New_York)

## Repository discovery
- Box filesystem: no directory named `bank-it-operations-lab` or `*bank-it*` under / (maxdepth 5).
- GitHub (gh authenticated as `onnxscibroccoli`): `gh repo view onnxscibroccoli/bank-it-operations-lab` -> "Could not resolve to a Repository"; `gh search repos bank-it-operations-lab` -> only unrelated public repos (blood-bank projects etc.). No org memberships.
- Conclusion: no upstream spec/README/CI/issues available; implementation follows the BANK-AWS-001 brief only.

## Ownership check
- `rg --hidden "infra/aws-cdk|evidence/aws|bank-it-operations-lab|BANK-AWS-001" /workspace` -> no matches.
- No CODEOWNERS / lock / claim files referencing these paths.
- No existing `aws-cdk` directories at maxdepth 4.
- Existing Grasshopper/other workspaces are not touched.

## Scope / rules
- Write only `infra/aws-cdk/**` and `evidence/aws/**`.
- No AWS credentials, no deploy/bootstrap, no lookups, no push, no repo creation. Local commits only.

## Artifact plan
- infra/aws-cdk: package.json (+ package-lock.json, exact pins), tsconfig.json, cdk.json, bin/app.ts, lib/secure-storage-stack.ts, test/secure-storage-stack.test.ts, jest.config.js.
- Stack: KMS CMK (rotation on), data bucket (SSE-KMS, BlockPublicAccess.BLOCK_ALL, enforceSSL, versioning, server access logs), access-logs bucket (SSE-S3, BPA, enforceSSL, versioning). cdk-nag AwsSolutionsChecks verbose aspect. No NagSuppressions applied.
- Tests: template assertions + zero cdk-nag errors/warnings.
- evidence/aws: logs/*.log with exit codes, synthesized template JSON, cdk-nag reports from cdk.out, SHA256SUMS, README (static evidence only).
- Delivery: /workspace/bank-it-operations-lab-BANK-AWS-001.tar.gz + .sha256.
