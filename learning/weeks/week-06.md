# Week 6: AWS Organizations guard rails (identity and governance 3 of 3)

**Branch:** `$PR6` = `orgs-security-refs@e5e7f46` (PR #6). **Prerequisites:** Node 20; optionally `pip install parliament==1.6.4 'setuptools<81'`.
**Delivered files used:** `infra/orgs/lib/{scps.ts,ou-layout.ts,lab-context.ts,policy-lint.ts,scp-evaluator.ts,org-governance-stack.ts,org-cloudtrail-stack.ts,security-services-stack.ts}`,
`infra/orgs/scripts/{nag-gate.sh,lint-policies.ts,export-policies.ts,parliament.sh}`, `infra/orgs/parliament-allowlist.json`, `infra/orgs/test/*.test.ts`,
`infra/orgs/docs/adr/ADR-0001..0003`, `evidence/orgs/**`.

## Daily exercises
**Day 1: OU tree and attachments.** From `ou-layout.ts` and `infra/orgs/README.md`: Root gets deny-root-user and deny-leave-organization.
Security, Infrastructure, Workloads and Sandbox get region-lock, protect-security-services, deny-public-s3 and require-encryption. Suspended gets deny-all-suspended.
Explain why the 5-SCPs-per-target quota forced this split (ADR-0003).

**Day 2: Tests and synth.**
```bash
cd $PR6/infra/orgs && npm ci --no-audit --no-fund && npx tsc --noEmit && npm test
npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --no-asset-metadata --quiet && bash scripts/nag-gate.sh
```
- *Expected:* `Tests: 49 passed` (4 suites). The 3 templates are byte-identical to `evidence/orgs/synth/`. Nag gate: CloudTrail 14 rows, Governance and SecurityServices 0 rows,
  `total_non_compliant_or_suppressed=0`. (Executed: E10.)

**Day 3: SCP lint.** `npx ts-node scripts/lint-policies.ts`. *Expected:* `errors=0 warnings=0`, with the largest policy (protect-security-services) at 1891/5120 chars. (Executed: E10.)

**Day 4: Offline evaluator.** Copy `learning/exercises/scp-region-lock.ts` into `infra/orgs/` as `scratch-scp-exercise.ts`, run
`npx ts-node --transpile-only scratch-scp-exercise.ts`, then delete it.
- *Observed (E11):* `ec2:RunInstances in eu-west-1: DenyOutsideAllowedRegions`, then `us-east-1: not denied`, then `eu-west-1 as OrgBreakGlass: not denied`.

**Day 5: parliament.** `PYTHONWARNINGS=ignore PARLIAMENT=<path>/parliament bash scripts/parliament.sh gated`
- *Observed (E12):* the 2 MEDIUM `UNKNOWN_CONDITION_FOR_ACTION` findings are ALLOWLISTED, and `unallowlisted_findings=0`.
  **Without `PYTHONWARNINGS=ignore`** (setuptools 80.10.2 installed), parliament's `pkg_resources` deprecation warning reached the JSON
  stream under `script(1)`, and the gate crashed with `JSONDecodeError` (exit 1). That is an environment fragility in `scripts/parliament.sh`, not a policy finding.

## Failure injection and recovery
- **Deny → Allow** (in memory, same scratch script). *Observed (E11):* `NOT_DENY` ERROR "deny-list strategy: only Effect=Deny statements allowed".
- **The ADR-0003 defect, re-read.** `StringNotEqualsIfExists` on `s3:x-amz-server-side-encryption` would deny every PutObject that relies on default encryption.
  The behaviour test caught it, and `StringNotEquals` + `Null: false` fixed it. Reproducing it would mean editing `scps.ts` in a scratch tree, then `npm test`. **UNEXECUTED** (P-W6).

## Review findings (from #14 and #7, re-verified here)
- **B6-1: the org-trail access-log bucket logs to itself.** This is the same anti-pattern #5 removed from `infra/aws-cdk`.
  `python3 $PR3/evidence/shared/validate_evidence.py cfn-s3-selflog evidence/orgs/synth/BankItLabOrgCloudTrail.template.json`
  *Observed (R06):* `ERROR TrailAccessLogsBucket30C0D746: server access logs delivered to itself (prefix 'self-access-logs/')`, exit 1.
  Source: `infra/orgs/lib/org-cloudtrail-stack.ts:50` (`serverAccessLogsPrefix: 'self-access-logs/'`). Run 1 of this guide (E10) reported the nag gate green but did not run this check. That is a lesson in itself.
  This is why #7 did **not** integrate #6 (`reports/INTEGRATION.md`).
- **B6-2: exempt-role bypass.** `EXEMPT_ROLE_ARNS` (`infra/orgs/lib/lab-context.ts:13`) uses `arn:aws:iam::*:role/OrgSecurityAdmin` and `OrgBreakGlass`, and `grep -n "iam:" infra/orgs/lib/scps.ts` shows only `iam:*` in the region-lock NotAction list (line 32) and the root-ARN condition (line 47) (R06).
  So no SCP stops an admin in a member account from creating a role with an exempt name. Exercise: write the deny statement and an evaluator test for it (notes only).
- **B6-3: Terraform versus CDK.** #14 reports that the plan asked for Terraform. The repo has no `.tf` file on any branch. Treat the Terraform objectives as **not met**.
  Note that the Terraform provider has `aws_guardduty_organization_admin_account`, which addresses the ADR-0002 gap.

## Answer notes
- SCPs never restrict the management account, so root-level guard rails protect member accounts only.
- GuardDuty org admin and auto-enable have no CloudFormation resource, which is a documented gap (ADR-0002). Security Hub configuration policies are not modelled.
- The offline evaluator is not AWS's engine. Access Analyzer validation in a sandbox org is required before adoption (ADR-0003).

## Architecture tradeoffs
- Deny-list SCPs (on top of FullAWSAccess) versus allow-list: deny-list is easier to adopt but needs discipline about exemptions (`EXEMPT_ROLE_ARNS`).
- Exempt roles (`OrgSecurityAdmin`, `OrgBreakGlass`) are both a necessity and the highest-value target. They need monitoring.
- Region lock with global-service exemptions (`REGION_LOCK_EXEMPT_ACTIONS`): it is a maintenance burden as AWS adds services.

## Fifteen-minute walkthrough
OU diagram → quota-driven attachment → run the evaluator script → the parliament allowlist and why each entry is a false positive.

## Interview questions
1. Why can't an SCP protect the management account?
2. How would you test an SCP change before it reaches production OUs?
3. Why is `...IfExists` dangerous on encryption headers?
4. How do you keep break-glass roles from becoming a standing backdoor?

## PENDING / UNEXECUTED
- P-W6 (above). No CI workflow exists for `infra/orgs`. GuardDuty org enablement is not built. Access Analyzer was never run.
- No fix for B6-1, B6-2 or B6-3 exists on any branch at `e5e7f46`. #6 is **not integrated** in #7.
