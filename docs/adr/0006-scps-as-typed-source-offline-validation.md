# 0006: SCPs as typed source, three offline validation layers, quota-driven attachment
- Status: Proposed (PR #6 open draft)
- Date: 2026-10-28

## Decision (as implemented)
- 7 SCPs as typed JSON in `orgs-security-refs@e5e7f46:infra/orgs/lib/scps.ts`. One source feeds the CDK `AWS::Organizations::Policy`, the exported `evidence/orgs/policies/*.json`, and the linters.
- Validation layers: `lib/policy-lint.ts` (structure, Deny-only, the 5,120-char quota), `lib/scp-evaluator.ts` (behaviour tests), and parliament 1.6.4 with `parliament-allowlist.json` via `scripts/parliament.sh gated`.
- Attachment: deny-root-user and deny-leave-organization on the Root; four guard rails per OU; deny-all-suspended on Suspended. A test enforces ≤5 SCPs per target (`test/scps.test.ts`).
- Module ADR: `infra/orgs/docs/adr/ADR-0003-scp-linting-and-quotas.md`.

## Consequences
- The offline evaluator is not AWS's engine. Access Analyzer in a sandbox org is required before adoption, and it was never run.
- `parliament.sh gated` breaks if a Python warning reaches stdout (setuptools 80.10.2). `PYTHONWARNINGS=ignore` works around it (learning/execution E12).
