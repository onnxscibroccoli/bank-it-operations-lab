# infra/orgs: AWS Organizations security reference modules

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Organize permissions and security administration across multiple cloud accounts. Central guardrails reduce accidental drift, but their scope and exceptions must be understood.

For example: A central team defines a guardrail that member accounts cannot exceed, then reviews where administration is delegated.

Key terms: **SCP** means service Control Policy: an AWS Organizations guardrail that limits available permissions rather than granting them. **Delegated administrator** means an account assigned administration responsibilities for a supported service. **Terraform** means a tool that describes and manages infrastructure through configuration.

**Before using this reference:** No live Organizations changes, Terraform apply, or service enablement is established by these documents.

Start with the [plain-English learning path](../../docs/knowledge/infrastructure.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


**Reference only. This code is never deployed.** It synthesizes CloudFormation and lints SCPs offline, with no AWS
credentials. Account, root and organization IDs are CloudFormation parameters, so nothing is looked up.

| Stack / module | Deploy target (if ever adopted) | Contents |
| --- | --- | --- |
| `lib/scps.ts` | n/a (policy-as-code) | 7 SCPs: deny-root-user, deny-leave-organization, region-lock, protect-security-services (CloudTrail/GuardDuty/Security Hub/Config), deny-public-s3, require-encryption, deny-all-suspended |
| `lib/ou-layout.ts` | n/a | OU tree: Security, Infrastructure, Workloads/{Prod,NonProd}, Sandbox, Suspended |
| `BankItLabOrgGovernance` | management account | OUs, `AWS::Organizations::Policy` SCPs attached to the root and OUs, `AWS::SecurityHub::DelegatedAdmin` |
| `BankItLabOrgCloudTrail` | management account (or CloudTrail delegated admin) | Organization trail: multi-region, global events, log-file validation, CMK (rotation), hardened S3 + access-log bucket, CloudWatch Logs with 1-year retention |
| `BankItLabSecurityServices` | Security Tooling (delegated admin) account, per region | GuardDuty detector with protection plans; Security Hub hub, FSBP v1.0.0 and CIS v3.0.0 standards, all-regions finding aggregator, CENTRAL organization configuration |

## SCP attachment (quota: at most 5 SCPs per target, including `FullAWSAccess`)
- Root: deny-root-user, deny-leave-organization (applies to member accounts only; SCPs never restrict the management account).
- Security, Infrastructure, Workloads, Sandbox: region-lock, protect-security-services, deny-public-s3, require-encryption.
  Workloads/Prod and Workloads/NonProd inherit them.
- Suspended: deny-all-suspended.
- Exempt principals (`OrgSecurityAdmin`, `OrgBreakGlass` roles) are listed in `lib/lab-context.ts`.

## Tests and checks (all offline)
    npm ci
    npx tsc --noEmit
    npm test                      # Jest: CDK assertions, cdk-nag, SCP lint, SCP behaviour (offline evaluator)
    npm run synth                 # cdk synth --no-lookups ... (AwsSolutionsChecks writes NagReport CSVs)
    bash scripts/nag-gate.sh      # 0 Non-Compliant, 0 Suppressed
    npm run export:policies       # evidence/orgs/policies/*.json
    npm run lint:policies         # evidence/orgs/lint/scp-lint-report.json
    scripts/parliament.sh gated   # third-party linter (parliament 1.6.4), allowlist in parliament-allowlist.json

Run these through `evidence/orgs/run-cmd.sh <log> <cmd>` to record evidence with a credential-free environment.

## Design notes
See `docs/adr/`. Toolchain pins match `infra/aws-cdk` (aws-cdk-lib 2.275.0, cdk-nag 2.38.2, jest 30, TypeScript 5.9).
