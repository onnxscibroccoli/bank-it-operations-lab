/**
 * Static guards over synthesized CloudFormation templates. Used by Jest (negative + positive tests) so that a
 * regression (public RDS, a bucket that logs to itself, a wildcard KMS key-policy principal) fails the build.
 */
type Resources = Record<string, { Type: string; Properties?: any }>;
export interface TemplateJson { Resources?: Resources }

export interface Violation { rule: string; resource: string; detail: string }

const refOf = (v: any): string | undefined => (v && typeof v === 'object' && typeof v.Ref === 'string' ? v.Ref : undefined);

/** RDS instances/clusters that are publicly accessible, or not explicitly private, or unencrypted. */
export function rdsPublicOrUnencrypted(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type !== 'AWS::RDS::DBInstance') continue;
    const p = r.Properties ?? {};
    // CloudFormation defaults PubliclyAccessible based on subnet type, so anything but an explicit false is a violation.
    if (p.PubliclyAccessible !== false) out.push({ rule: 'RDS_PUBLIC', resource: id, detail: `PubliclyAccessible=${JSON.stringify(p.PubliclyAccessible)}` });
    if (p.StorageEncrypted !== true) out.push({ rule: 'RDS_UNENCRYPTED', resource: id, detail: 'StorageEncrypted is not true' });
    if (p.StorageEncrypted === true && p.KmsKeyId === undefined) out.push({ rule: 'RDS_NO_CMK', resource: id, detail: 'no customer-managed KmsKeyId' });
  }
  return out;
}

/** S3 buckets whose server access logs are delivered to themselves (directly, by Ref, or by a log loop). */
export function selfLoggingBuckets(t: TemplateJson): Violation[] {
  const res = t.Resources ?? {};
  const dest: Record<string, string | undefined> = {};
  for (const [id, r] of Object.entries(res)) {
    if (r.Type !== 'AWS::S3::Bucket') continue;
    const lc = r.Properties?.LoggingConfiguration;
    if (!lc) { dest[id] = undefined; continue; }
    // LoggingConfiguration with no DestinationBucketName means "log to this same bucket".
    dest[id] = lc.DestinationBucketName === undefined ? id : refOf(lc.DestinationBucketName) ?? `external:${JSON.stringify(lc.DestinationBucketName)}`;
  }
  const out: Violation[] = [];
  for (const start of Object.keys(dest)) {
    const seen = new Set<string>();
    let cur: string | undefined = start;
    while (cur && dest.hasOwnProperty(cur) && !seen.has(cur)) { seen.add(cur); cur = dest[cur]; }
    if (cur && seen.has(cur) && cur === start) {
      out.push({ rule: 'S3_SELF_LOGGING', resource: start, detail: `access-log chain loops back: ${[...seen].join(' -> ')} -> ${start}` });
    }
  }
  return out;
}

const isWildcardPrincipal = (p: any): boolean => {
  if (p === '*') return true;
  if (p && typeof p === 'object') {
    for (const v of Object.values(p)) {
      const arr = Array.isArray(v) ? v : [v];
      if (arr.some((x) => x === '*')) return true;
    }
  }
  return false;
};

/** KMS key-policy statements that Allow a wildcard principal, or grant kms:* / "*" actions. */
export function kmsWildcards(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type !== 'AWS::KMS::Key') continue;
    for (const s of r.Properties?.KeyPolicy?.Statement ?? []) {
      if (s.Effect !== 'Allow') continue;
      if (isWildcardPrincipal(s.Principal)) out.push({ rule: 'KMS_WILDCARD_PRINCIPAL', resource: id, detail: JSON.stringify(s.Principal) });
      const actions: string[] = Array.isArray(s.Action) ? s.Action : [s.Action];
      if (actions.some((a) => a === '*' || a === 'kms:*')) out.push({ rule: 'KMS_WILDCARD_ACTION', resource: id, detail: actions.join(',') });
    }
  }
  return out;
}

/** Security group rules open to the internet (0.0.0.0/0 or ::/0), inline or standalone. */
export function openSecurityGroupRules(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  const check = (id: string, rule: any, dir: string) => {
    if (rule?.CidrIp === '0.0.0.0/0' || rule?.CidrIpv6 === '::/0') out.push({ rule: `SG_OPEN_${dir}`, resource: id, detail: JSON.stringify(rule) });
  };
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type === 'AWS::EC2::SecurityGroup') {
      (r.Properties?.SecurityGroupIngress ?? []).forEach((x: any) => check(id, x, 'INGRESS'));
      (r.Properties?.SecurityGroupEgress ?? []).forEach((x: any) => check(id, x, 'EGRESS'));
    }
    if (r.Type === 'AWS::EC2::SecurityGroupIngress') check(id, r.Properties, 'INGRESS');
    if (r.Type === 'AWS::EC2::SecurityGroupEgress') check(id, r.Properties, 'EGRESS');
  }
  return out;
}

export function allViolations(t: TemplateJson): Violation[] {
  return [...rdsPublicOrUnencrypted(t), ...selfLoggingBuckets(t), ...kmsWildcards(t), ...openSecurityGroupRules(t)];
}
