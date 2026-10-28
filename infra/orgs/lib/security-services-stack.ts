import { Stack, StackProps } from 'aws-cdk-lib';
import * as guardduty from 'aws-cdk-lib/aws-guardduty';
import * as securityhub from 'aws-cdk-lib/aws-securityhub';
import { Construct } from 'constructs';

/** Security Hub standards enabled in the delegated admin (Security Tooling) account. */
export const SECURITY_HUB_STANDARDS = {
  FoundationalBestPractices: 'standards/aws-foundational-security-best-practices/v/1.0.0',
  CisFoundations300: 'standards/cis-aws-foundations-benchmark/v/3.0.0',
} as const;

/** GuardDuty protection plans enabled on the detector. */
export const GUARDDUTY_FEATURES = [
  'S3_DATA_EVENTS', 'EKS_AUDIT_LOGS', 'EBS_MALWARE_PROTECTION', 'RDS_LOGIN_EVENTS', 'LAMBDA_NETWORK_LOGS',
];

/**
 * Delegated-admin (Security Tooling account) reference stack: GuardDuty detector, Security Hub hub,
 * standards, cross-region finding aggregator and central organization configuration.
 * Per-region: deploy once per allowed region (aggregator only in the home region).
 */
export class SecurityServicesStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    new guardduty.CfnDetector(this, 'GuardDutyDetector', {
      enable: true,
      findingPublishingFrequency: 'FIFTEEN_MINUTES',
      features: GUARDDUTY_FEATURES.map((name) => ({ name, status: 'ENABLED' })),
    });

    const hub = new securityhub.CfnHub(this, 'SecurityHub', {
      enableDefaultStandards: false,
      controlFindingGenerator: 'SECURITY_CONTROL',
      autoEnableControls: true,
    });

    for (const [name, path] of Object.entries(SECURITY_HUB_STANDARDS)) {
      const std = new securityhub.CfnStandard(this, `Standard${name}`, {
        standardsArn: `arn:${this.partition}:securityhub:${this.region}::${path}`,
      });
      std.addResourceDependency(hub);
    }

    const aggregator = new securityhub.CfnFindingAggregator(this, 'FindingAggregator', {
      regionLinkingMode: 'ALL_REGIONS',
    });
    aggregator.addResourceDependency(hub);

    const orgConfig = new securityhub.CfnOrganizationConfiguration(this, 'OrganizationConfiguration', {
      autoEnable: false,
      autoEnableStandards: 'NONE',
      configurationType: 'CENTRAL',
    });
    orgConfig.addResourceDependency(aggregator);
  }
}
