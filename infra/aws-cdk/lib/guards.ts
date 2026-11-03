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

/** KMS key-policy statements that Allow a wildcard principal, grant kms:* / "*", use kms:Create* / kms:Put*, or grant
 *  CreateGrant / PutKeyPolicy without any condition (B5-2). */
export function kmsWildcards(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type !== 'AWS::KMS::Key') continue;
    for (const s of r.Properties?.KeyPolicy?.Statement ?? []) {
      if (s.Effect !== 'Allow') continue;
      if (isWildcardPrincipal(s.Principal)) out.push({ rule: 'KMS_WILDCARD_PRINCIPAL', resource: id, detail: JSON.stringify(s.Principal) });
      const actions: string[] = Array.isArray(s.Action) ? s.Action : [s.Action];
      if (actions.some((a) => a === '*' || a === 'kms:*')) out.push({ rule: 'KMS_WILDCARD_ACTION', resource: id, detail: actions.join(',') });
      // B5-2: grant-creation / key-policy-writing actions (incl. the Create* / Put* wildcards) must never be unconditioned.
      const sensitive = actions.filter((a) => ['kms:create*', 'kms:put*', 'kms:creategrant', 'kms:putkeypolicy'].includes(String(a).toLowerCase()));
      if (sensitive.length && !(s.Condition && Object.keys(s.Condition).length)) {
        out.push({ rule: 'KMS_UNCONDITIONED_ADMIN', resource: id, detail: sensitive.join(',') });
      }
      if (actions.some((a) => ['kms:create*', 'kms:put*'].includes(String(a).toLowerCase()))) {
        out.push({ rule: 'KMS_ADMIN_WILDCARD', resource: id, detail: actions.join(',') });
      }
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

/* ------------------------------------------------------------------------------------------------------------------
 * KMS admin / operational separation (aws-remediation-backup-kms). Static template checks only: they prove what the
 * synthesized policy text says, NOT how AWS evaluates it at runtime.
 *  - crypto (operational): Encrypt, Decrypt, ReEncrypt*, GenerateDataKey*
 *  - grant delegation (operational, must be GrantIsForAWSResource / ViaService scoped): CreateGrant
 *  - grant lifecycle (kept with CreateGrant, same conditions): ListGrants, RevokeGrant, RetireGrant
 *  - neutral (allowed anywhere): DescribeKey
 *  - administrative: everything else (Create*, Put*, Update*, Enable*, Disable*, Delete*, Get*, List*, Tag/Untag,
 *    ScheduleKeyDeletion, CancelKeyDeletion, Import*, Replicate*, ...)
 * ---------------------------------------------------------------------------------------------------------------- */
const lc = (a: unknown) => String(a).toLowerCase();
const asArray = <T>(v: T | T[] | undefined): T[] => (v === undefined ? [] : Array.isArray(v) ? v : [v]);
const CRYPTO_RE = /^kms:(encrypt\*?|decrypt\*?|reencrypt\*?|reencryptfrom|reencryptto|generatedatakey[a-z]*\*?)$/;
const GRANT_LIFECYCLE = ['kms:listgrants', 'kms:revokegrant', 'kms:retiregrant'];
const NEUTRAL = ['kms:describekey', 'kms:describe*'];
/** Administrative verbs that must never be granted as a wildcard (kms:Delete*, kms:Get*, ...). Describe* and the
 *  operational wildcards (Encrypt*, Decrypt*, ReEncrypt*, GenerateDataKey*) are excluded on purpose. */
const ADMIN_WILDCARD_VERBS = ['create', 'put', 'update', 'enable', 'disable', 'delete', 'get', 'list', 'revoke', 'schedule',
  'cancel', 'tag', 'untag', 'import', 'replicate', 'retire', 'connect', 'disconnect', 'rotate', 'sign', 'verify', 'derive'];

export type KmsActionClass = 'crypto' | 'grant' | 'grant-lifecycle' | 'neutral' | 'admin' | 'wildcard';
export function classifyKmsAction(action: string): KmsActionClass {
  const a = lc(action);
  if (a === '*' || a === 'kms:*') return 'wildcard';
  if (CRYPTO_RE.test(a)) return 'crypto';
  if (a === 'kms:creategrant') return 'grant';
  if (GRANT_LIFECYCLE.includes(a)) return 'grant-lifecycle';
  if (NEUTRAL.includes(a)) return 'neutral';
  return 'admin';
}
const condKeys = (c: any): string[] => Object.values(c ?? {}).flatMap((v: any) => Object.keys(v ?? {}).map(lc));
const condOps = (c: any): string[] => Object.keys(c ?? {});
const grantIsForAwsResource = (c: any): boolean => String(c?.Bool?.['kms:GrantIsForAWSResource']) === 'true';
const isAwsPrincipal = (p: any): boolean => !!p && typeof p === 'object' && 'AWS' in p;
const isServicePrincipal = (p: any): boolean => !!p && typeof p === 'object' && 'Service' in p && !('AWS' in p);

/** Key-policy separation-of-duties checks (complements kmsWildcards). */
export function kmsSeparation(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type !== 'AWS::KMS::Key') continue;
    for (const s of r.Properties?.KeyPolicy?.Statement ?? []) {
      if (s.Effect !== 'Allow') continue;
      const actions: string[] = asArray(s.Action);
      const cls = actions.map(classifyKmsAction);
      const keys = condKeys(s.Condition);
      const sid = s.Sid ?? '(no Sid)';
      const adminWild = actions.filter((a) => {
        const m = /^kms:([a-z]+)\*$/.exec(lc(a));
        return !!m && ADMIN_WILDCARD_VERBS.includes(m[1]);
      });
      if (adminWild.length) out.push({ rule: 'KMS_ADMIN_VERB_WILDCARD', resource: id, detail: `${sid}: ${adminWild.join(',')}` });
      const hasAdmin = cls.includes('admin');
      const hasOperational = cls.includes('crypto') || cls.includes('grant');
      if (hasAdmin && hasOperational) {
        out.push({ rule: 'KMS_ADMIN_OPERATIONAL_MIX', resource: id, detail: `${sid}: ${actions.join(',')}` });
      }
      if (isAwsPrincipal(s.Principal)) {
        if (hasAdmin && !keys.includes('aws:principalarn')) {
          out.push({ rule: 'KMS_ADMIN_UNSCOPED_PRINCIPAL', resource: id, detail: `${sid}: admin actions for an account principal without aws:PrincipalArn` });
        }
        if (cls.includes('crypto') && !keys.includes('kms:viaservice')) {
          out.push({ rule: 'KMS_CRYPTO_NOT_VIA_SERVICE', resource: id, detail: `${sid}: crypto for an account principal without kms:ViaService` });
        }
        if (cls.includes('grant') && !(grantIsForAwsResource(s.Condition) || keys.includes('kms:viaservice'))) {
          out.push({ rule: 'KMS_GRANT_UNSCOPED', resource: id, detail: `${sid}: CreateGrant without kms:GrantIsForAWSResource=true or kms:ViaService` });
        }
        if (actions.some((a) => ['kms:putkeypolicy', 'kms:put*'].includes(lc(a))) && !keys.includes('kms:bypasspolicylockoutsafetycheck')) {
          out.push({ rule: 'KMS_PUTKEYPOLICY_LOCKOUT_BYPASS_ALLOWED', resource: id, detail: `${sid}: PutKeyPolicy without BypassPolicyLockoutSafetyCheck=false` });
        }
      }
      if (isServicePrincipal(s.Principal) && keys.length === 0) {
        out.push({ rule: 'KMS_SERVICE_PRINCIPAL_UNCONDITIONED', resource: id, detail: `${sid}: ${JSON.stringify(s.Principal)}` });
      }
    }
  }
  return out;
}

/** KMS permissions in identity policies (managed or inline, incl. Role.Policies). */
export function iamKmsPermissions(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  const docs: { id: string; doc: any }[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type === 'AWS::IAM::ManagedPolicy' || r.Type === 'AWS::IAM::Policy') docs.push({ id, doc: r.Properties?.PolicyDocument });
    if (r.Type === 'AWS::IAM::Role') for (const p of r.Properties?.Policies ?? []) docs.push({ id, doc: p.PolicyDocument });
  }
  for (const { id, doc } of docs) {
    for (const s of doc?.Statement ?? []) {
      if (s.Effect !== 'Allow') continue;
      const actions: string[] = asArray(s.Action).map(String);
      const kmsActions = actions.filter((a) => a === '*' || lc(a).startsWith('kms:'));
      if (!kmsActions.length) continue;
      const cls = kmsActions.map(classifyKmsAction);
      const sid = s.Sid ?? '(no Sid)';
      if (cls.includes('wildcard')) out.push({ rule: 'IAM_KMS_WILDCARD', resource: id, detail: `${sid}: ${kmsActions.join(',')}` });
      if (cls.includes('admin')) out.push({ rule: 'IAM_KMS_ADMIN_IN_WORKLOAD_POLICY', resource: id, detail: `${sid}: ${kmsActions.join(',')}` });
      if (cls.includes('grant') && !grantIsForAwsResource(s.Condition)) {
        out.push({ rule: 'IAM_KMS_GRANT_NOT_FOR_AWS_RESOURCE', resource: id, detail: `${sid}: CreateGrant without kms:GrantIsForAWSResource=true` });
      }
      if (cls.includes('grant') && cls.includes('crypto')) {
        out.push({ rule: 'IAM_KMS_GRANT_MIXED_WITH_CRYPTO', resource: id, detail: `${sid}: ${kmsActions.join(',')}` });
      }
      if ((cls.includes('crypto') || cls.includes('grant')) && !condKeys(s.Condition).includes('kms:viaservice')) {
        out.push({ rule: 'IAM_KMS_NOT_VIA_SERVICE', resource: id, detail: `${sid}: ${kmsActions.join(',')}` });
      }
      if (asArray(s.Resource).some((x) => x === '*')) {
        out.push({ rule: 'IAM_KMS_RESOURCE_WILDCARD', resource: id, detail: `${sid}: Resource "*"` });
      }
    }
  }
  return out;
}

/** Trust policies of roles assumable by AWS Backup: must pin aws:SourceAccount with a non-IfExists operator, must
 *  not use IfExists on the source keys (that would silently pass when AWS omits the key), and must not trust any
 *  other principal in the same statement. */
export function backupRoleTrust(t: TemplateJson): Violation[] {
  const out: Violation[] = [];
  for (const [id, r] of Object.entries(t.Resources ?? {})) {
    if (r.Type !== 'AWS::IAM::Role') continue;
    for (const s of r.Properties?.AssumeRolePolicyDocument?.Statement ?? []) {
      const svc = asArray(s.Principal?.Service).map(String);
      if (s.Effect !== 'Allow' || !svc.some((x) => x.startsWith('backup.'))) continue;
      const ops = condOps(s.Condition);
      const sa = ops.filter((o) => Object.keys(s.Condition[o] ?? {}).some((k) => lc(k) === 'aws:sourceaccount'));
      if (!sa.some((o) => o === 'StringEquals')) out.push({ rule: 'BACKUP_TRUST_NO_SOURCE_ACCOUNT', resource: id, detail: JSON.stringify(s.Condition ?? {}) });
      for (const o of ops) {
        if (/IfExists$/.test(o) && Object.keys(s.Condition[o] ?? {}).some((k) => lc(k).startsWith('aws:source'))) {
          out.push({ rule: 'BACKUP_TRUST_IFEXISTS', resource: id, detail: `${o} on ${Object.keys(s.Condition[o]).join(',')}` });
        }
      }
      if (svc.length > 1 || s.Principal?.AWS !== undefined || s.Principal === '*') {
        out.push({ rule: 'BACKUP_TRUST_EXTRA_PRINCIPAL', resource: id, detail: JSON.stringify(s.Principal) });
      }
    }
  }
  return out;
}

export function allViolations(t: TemplateJson): Violation[] {
  return [
    ...rdsPublicOrUnencrypted(t), ...selfLoggingBuckets(t), ...kmsWildcards(t), ...openSecurityGroupRules(t),
    ...kmsSeparation(t), ...iamKmsPermissions(t), ...backupRoleTrust(t),
  ];
}
