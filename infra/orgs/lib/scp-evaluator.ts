import { PolicyDocument, Statement } from './scps';

/**
 * Tiny, offline SCP evaluator for unit tests. Supports only the operators used in this repo's SCPs.
 * Not a substitute for the IAM policy simulator; documents intent and catches regressions.
 */
export interface RequestContext {
  action: string;
  /** Condition keys present on the request (absent keys are omitted). */
  keys: Record<string, string | boolean>;
}

const asArray = <T>(v: T | T[] | undefined): T[] => (v === undefined ? [] : Array.isArray(v) ? v : [v]);

function globToRe(glob: string, ci: boolean): RegExp {
  const esc = glob.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.');
  return new RegExp(`^${esc}$`, ci ? 'i' : '');
}
const actionMatches = (pattern: string, action: string) => globToRe(pattern, true).test(action);

function condHolds(op: string, key: string, expected: unknown, ctx: RequestContext): boolean {
  const present = Object.prototype.hasOwnProperty.call(ctx.keys, key);
  const actual = present ? String(ctx.keys[key]) : undefined;
  const values = asArray(expected as string | string[]).map(String);
  switch (op) {
    case 'StringEquals': case 'ArnEquals':
      return present && values.includes(actual!);
    case 'StringNotEquals': case 'ArnNotEquals':
      // IAM: a missing key makes a negated operator evaluate true.
      return !present || !values.includes(actual!);
    case 'StringNotEqualsIfExists':
      return !present || !values.includes(actual!);
    case 'StringLike': case 'ArnLike':
      return present && values.some((v) => globToRe(v, false).test(actual!));
    case 'StringNotLike': case 'ArnNotLike':
      return !present || !values.some((v) => globToRe(v, false).test(actual!));
    case 'Bool':
      return present && values.includes(actual!.toLowerCase());
    case 'Null':
      return values.includes(String(!present));
    default:
      throw new Error(`operator ${op} not supported by test evaluator`);
  }
}

export function statementDenies(s: Statement, ctx: RequestContext): boolean {
  if (s.Effect !== 'Deny') return false;
  const inAction = s.Action !== undefined
    ? asArray(s.Action).some((p) => actionMatches(p, ctx.action))
    : !asArray(s.NotAction).some((p) => actionMatches(p, ctx.action));
  if (!inAction) return false;
  for (const [op, kv] of Object.entries(s.Condition ?? {})) {
    for (const [k, v] of Object.entries(kv)) if (!condHolds(op, k, v, ctx)) return false;
  }
  return true;
}

/** Returns the Sid of the first denying statement, or undefined if the request is not denied. */
export function deniedBy(doc: PolicyDocument, ctx: RequestContext): string | undefined {
  return doc.Statement.find((s) => statementDenies(s, ctx))?.Sid;
}
