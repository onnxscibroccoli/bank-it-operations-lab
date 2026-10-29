# ADR-0002: Delegated administration coverage and gaps

- Status: Accepted
- Date: 2026-10-28

## Decision
- **Security Hub**: `AWS::SecurityHub::DelegatedAdmin` (management account) designates the Security Tooling account.
  In that account: `AWS::SecurityHub::Hub` (no default standards, consolidated control findings), FSBP v1.0.0 and CIS v3.0.0
  `AWS::SecurityHub::Standard`, an `ALL_REGIONS` `FindingAggregator`, and `OrganizationConfiguration` with
  `ConfigurationType: CENTRAL` (central configuration needs the aggregator, so the stack declares that dependency).
  Configuration policies (`AWS::SecurityHub::ConfigurationPolicy` and `PolicyAssociation`) are the next step. They are not modelled yet.
- **GuardDuty**: `AWS::GuardDuty::Detector` with S3, EKS audit, EBS malware, RDS login and Lambda network protection plans.
  CloudFormation has **no resource** for `EnableOrganizationAdminAccount` or `UpdateOrganizationConfiguration`
  (auto-enable). Adopting this would need a custom resource or a runbook step. That step is intentionally not built:
  it would call AWS APIs and needs credentials.
- **CloudTrail**: organization trail created in the management account. A CloudTrail delegated admin is optional and not modelled.

## Consequences
- GuardDuty org-wide enablement is a documented gap, not code.
- Security Hub/GuardDuty resources are regional: deploy per allowed region, with the aggregator only in the home region.
