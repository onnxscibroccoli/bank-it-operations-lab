import { PolicyDocument, ScpDefinition, Statement } from './scps';

/** AWS Organizations quota: max SCP document size (characters, whitespace stripped). */
export const SCP_MAX_CHARS = 5120;
/** Max SCPs directly attached to one OU/account (Organizations quota). */
export const SCP_MAX_PER_TARGET = 5;

const SUPPORTED_OPERATORS = new Set([
  'StringEquals', 'StringNotEquals', 'StringLike', 'StringNotLike', 'StringNotEqualsIfExists', 'StringEqualsIfExists',
  'ArnLike', 'ArnNotLike', 'ArnEquals', 'ArnNotEquals', 'Bool', 'Null',
]);
const ACTION_RE = /^(\*|[a-z0-9-]+:[A-Za-z0-9*]+)$/;
const SID_RE = /^[A-Za-z0-9]+$/;

export interface Finding {
  policy: string;
  sid?: string;
  severity: 'ERROR' | 'WARNING';
  code: string;
  message: string;
}

const asArray = <T>(v: T | T[] | undefined): T[] => (v === undefined ? [] : Array.isArray(v) ? v : [v]);

export function minifiedLength(d: PolicyDocument): number {
  return JSON.stringify(d).length;
}

/** Offline, structural SCP linter (no AWS API; Access Analyzer ValidatePolicy would need credentials). */
export function lintScp(def: ScpDefinition): Finding[] {
  const f: Finding[] = [];
  const add = (severity: Finding['severity'], code: string, message: string, sid?: string) =>
    f.push({ policy: def.id, sid, severity, code, message });
  const d = def.document;
  if (d.Version !== '2012-10-17') add('ERROR', 'VERSION', 'Version must be 2012-10-17');
  if (!Array.isArray(d.Statement) || d.Statement.length === 0) add('ERROR', 'NO_STATEMENTS', 'Statement must be a non-empty array');
  const len = minifiedLength(d);
  if (len > SCP_MAX_CHARS) add('ERROR', 'TOO_LARGE', `minified size ${len} > ${SCP_MAX_CHARS}`);
  const sids = new Set<string>();
  for (const s of d.Statement ?? []) lintStatement(s, sids, add);
  return f;
}

function lintStatement(
  s: Statement,
  sids: Set<string>,
  add: (sev: Finding['severity'], code: string, msg: string, sid?: string) => void,
): void {
  const sid = s.Sid;
  if (!sid || !SID_RE.test(sid)) add('ERROR', 'SID_FORMAT', `Sid must be alphanumeric: ${sid}`, sid);
  if (sids.has(sid)) add('ERROR', 'SID_DUPLICATE', `duplicate Sid ${sid}`, sid);
  sids.add(sid);
  if (s.Effect !== 'Deny') add('ERROR', 'NOT_DENY', 'deny-list strategy: only Effect=Deny statements allowed', sid);
  if ('Principal' in s || 'NotPrincipal' in s) add('ERROR', 'PRINCIPAL', 'SCPs do not support Principal/NotPrincipal', sid);
  const hasA = s.Action !== undefined;
  const hasNA = s.NotAction !== undefined;
  if (hasA === hasNA) add('ERROR', 'ACTION_XOR', 'exactly one of Action/NotAction required', sid);
  for (const a of [...asArray(s.Action), ...asArray(s.NotAction)]) {
    if (!ACTION_RE.test(a)) add('ERROR', 'ACTION_FORMAT', `bad action ${a}`, sid);
  }
  const acts = asArray(s.Action);
  if (new Set(acts).size !== acts.length) add('WARNING', 'ACTION_DUPLICATE', 'duplicate actions', sid);
  if (s.Resource === undefined && s.NotResource === undefined) add('ERROR', 'NO_RESOURCE', 'Resource required', sid);
  for (const [op, kv] of Object.entries(s.Condition ?? {})) {
    if (!SUPPORTED_OPERATORS.has(op)) add('ERROR', 'CONDITION_OPERATOR', `unsupported operator ${op}`, sid);
    for (const [k, v] of Object.entries(kv)) {
      if (!/^[a-z0-9-]+:[A-Za-z0-9-_/]+$/.test(k)) add('ERROR', 'CONDITION_KEY', `bad condition key ${k}`, sid);
      if (op === 'Bool' && !['true', 'false', true, false].includes(v as never)) add('ERROR', 'BOOL_VALUE', `Bool ${k}=${String(v)}`, sid);
      if (op.startsWith('Arn')) {
        for (const arn of asArray(v as string | string[])) {
          if (!String(arn).startsWith('arn:')) add('ERROR', 'ARN_VALUE', `not an ARN: ${String(arn)}`, sid);
        }
      }
    }
  }
  if (s.Action === '*' && !s.Condition) add('WARNING', 'UNCONDITIONAL_DENY_ALL', 'unconditional Deny * (lockout risk)', sid);
}
