# ADR-0003: SCP validation without AWS credentials

- Status: Accepted
- Date: 2026-10-28

## Context
IAM Access Analyzer `ValidatePolicy` and the IAM policy simulator are AWS API calls that need credentials, so neither is allowed here.

## Decision
Three offline layers:
1. `lib/policy-lint.ts`: structural linter (Version, unique alphanumeric Sids, Deny-only, no Principal, Action/NotAction
   exclusivity, action and condition-key format, supported operators, Bool values, ARN values, the 5,120-character size quota).
2. `lib/scp-evaluator.ts`: a minimal evaluator used by Jest to assert behaviour. Examples: root denied, exempt roles
   allowed, region lock, and encryption conditions. It follows IAM semantics for missing keys (negated operators and
   `...IfExists` evaluate true).
3. parliament 1.6.4 (duo-labs) over the exported JSON. Its bundled action/condition database is stale, so two findings
   are allowlisted exactly in `parliament-allowlist.json`, with sources. parliament's own `ignore_locations` is broken for
   YAML config in 1.6.4, so `scripts/parliament.sh gated` applies the allowlist itself.

## Defects these checks caught during development
- `require-encryption` first used `StringNotEqualsIfExists` on `s3:x-amz-server-side-encryption`. Under IAM semantics that
  would deny *every* PutObject that does not send the header, which breaks S3 default encryption. The behaviour test caught it.
  Fixed with `StringNotEquals` plus `Null: false`.
- `s3:DeleteBucketPublicAccessBlock` is not an IAM action (flagged by parliament). `DeletePublicAccessBlock` is authorised by
  `s3:PutBucketPublicAccessBlock`, so the entry was removed.
- Attaching all six guard rails to each OU would exceed the 5-SCPs-per-target quota. deny-root-user and
  deny-leave-organization moved to the root. A test enforces the quota per target.

## Consequences
The offline evaluator is not the AWS policy engine. Before adoption, validate the policies with Access Analyzer in a sandbox organization.
