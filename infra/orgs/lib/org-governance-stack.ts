import { CfnParameter, Stack, StackProps } from 'aws-cdk-lib';
import * as organizations from 'aws-cdk-lib/aws-organizations';
import * as securityhub from 'aws-cdk-lib/aws-securityhub';
import { Construct } from 'constructs';
import { OU_LAYOUT } from './ou-layout';
import { ROOT_SCP_IDS, SCPS, scpById } from './scps';

/**
 * Management-account reference stack: OU layout, SCPs attached to OUs, Security Hub delegated admin.
 * Account/root IDs are CloudFormation parameters, so synthesis needs no credentials or lookups.
 * GuardDuty delegated admin has no CloudFormation resource; see docs/adr/ADR-0002.
 */
export class OrgGovernanceStack extends Stack {
  public readonly ous: Record<string, organizations.CfnOrganizationalUnit> = {};
  public readonly policies: Record<string, organizations.CfnPolicy> = {};

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const rootId = new CfnParameter(this, 'OrgRootId', {
      type: 'String',
      description: 'Organization root id (r-xxxx). Supplied at deploy time; never looked up.',
      allowedPattern: '^r-[0-9a-z]{4,32}$',
    });
    const securityAccountId = new CfnParameter(this, 'SecurityToolingAccountId', {
      type: 'String',
      description: '12-digit account id of the Security Tooling (delegated admin) account.',
      allowedPattern: '^\\d{12}$',
    });

    for (const ou of OU_LAYOUT) {
      const parentId = ou.parent ? this.ous[ou.parent].attrId : rootId.valueAsString;
      if (ou.parent && !this.ous[ou.parent]) throw new Error(`parent OU ${ou.parent} must be declared first`);
      this.ous[ou.key] = new organizations.CfnOrganizationalUnit(this, `Ou${ou.key}`, { name: ou.name, parentId });
    }

    for (const def of SCPS) {
      const targets = OU_LAYOUT.filter((o) => o.scps.includes(def.id)).map((o) => this.ous[o.key].attrId);
      if (ROOT_SCP_IDS.includes(def.id)) targets.unshift(rootId.valueAsString);
      this.policies[def.id] = new organizations.CfnPolicy(this, `Scp${pascal(def.id)}`, {
        name: def.name,
        description: def.description,
        type: 'SERVICE_CONTROL_POLICY',
        content: scpById(def.id).document,
        targetIds: targets,
      });
    }

    new securityhub.CfnDelegatedAdmin(this, 'SecurityHubDelegatedAdmin', {
      adminAccountId: securityAccountId.valueAsString,
    });
  }
}

export function pascal(id: string): string {
  return id.split('-').map((p) => p[0].toUpperCase() + p.slice(1)).join('');
}
