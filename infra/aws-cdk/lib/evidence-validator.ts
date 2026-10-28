import { createHash } from 'crypto';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

/** Shape of evidence/aws/evidence-schema.json (BANK-AWS-001). */
export interface EvidenceFileSpec {
  path: string;
  format: string;
  required: boolean;
  description: string;
  rules?: string[];
}
export interface EvidenceSchema {
  schemaVersion: string;
  task: string;
  root: string;
  files: EvidenceFileSpec[];
  logFile: { pattern: string; requiredHeaders: string[]; exitCodeTrailer: string };
  rules: Record<string, string>;
}

export interface ValidationResult {
  ok: boolean;
  errors: string[];
  checked: string[];
}

const sha256 = (p: string): string => createHash('sha256').update(readFileSync(p)).digest('hex');

/** Validate the descriptor itself: every file rule must be defined, paths unique and relative. */
export function validateSchemaShape(schema: EvidenceSchema): string[] {
  const errors: string[] = [];
  if (!/^\d+\.\d+\.\d+$/.test(schema.schemaVersion ?? '')) errors.push('schemaVersion must be semver');
  if (!schema.root || !Array.isArray(schema.files) || schema.files.length === 0) errors.push('root and files[] are required');
  const seen = new Set<string>();
  for (const f of schema.files ?? []) {
    if (!f.path || f.path.startsWith('/') || f.path.includes('..')) errors.push(`invalid path: ${f.path}`);
    if (seen.has(f.path)) errors.push(`duplicate path: ${f.path}`);
    seen.add(f.path);
    for (const r of f.rules ?? []) if (!(r in (schema.rules ?? {}))) errors.push(`${f.path}: undefined rule ${r}`);
  }
  return errors;
}

function parseCsvRow(line: string): string[] {
  const out: string[] = [];
  let cur = '';
  let q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) {
      if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (c === '"') q = false; else cur += c;
    } else if (c === '"') q = true;
    else if (c === ',') { out.push(cur); cur = ''; } else cur += c;
  }
  out.push(cur);
  return out;
}

type RuleFn = (abs: string, ctx: { repoRoot: string; evidenceRoot: string; schema: EvidenceSchema }) => string[];

const RULES: Record<string, RuleFn> = {
  'sha256sums-verify': (abs, { repoRoot }) => {
    const errors: string[] = [];
    const lines = readFileSync(abs, 'utf8').split('\n').filter((l) => l.trim());
    if (lines.length === 0) errors.push('SHA256SUMS is empty');
    for (const l of lines) {
      const m = /^([0-9a-f]{64}) [ *](.+)$/.exec(l);
      if (!m) { errors.push(`SHA256SUMS malformed line: ${l}`); continue; }
      const target = join(repoRoot, m[2]);
      if (!existsSync(target)) errors.push(`SHA256SUMS missing file: ${m[2]}`);
      else if (sha256(target) !== m[1]) errors.push(`SHA256SUMS mismatch: ${m[2]}`);
    }
    return errors;
  },
  'commands-tsv': (abs, { evidenceRoot, schema }) => {
    const errors: string[] = [];
    const trailer = new RegExp(schema.logFile.exitCodeTrailer, 'm');
    const rows = readFileSync(abs, 'utf8').split('\n').filter((l) => l.length > 0);
    if (rows.length === 0) errors.push('COMMANDS.tsv is empty');
    rows.forEach((row, i) => {
      const cols = row.split('\t');
      if (cols.length !== 3) { errors.push(`COMMANDS.tsv row ${i + 1}: expected 3 fields, got ${cols.length}`); return; }
      const [log, code] = cols;
      if (!/^-?\d+$/.test(code)) { errors.push(`COMMANDS.tsv row ${i + 1}: non-integer exit code ${code}`); return; }
      const logPath = join(evidenceRoot, 'logs', log);
      if (!new RegExp(schema.logFile.pattern).test(`logs/${log}`)) errors.push(`COMMANDS.tsv row ${i + 1}: bad log name ${log}`);
      if (!existsSync(logPath)) { errors.push(`COMMANDS.tsv row ${i + 1}: missing log ${log}`); return; }
      const text = readFileSync(logPath, 'utf8');
      for (const h of schema.logFile.requiredHeaders) if (!text.includes(h)) errors.push(`${log}: missing header ${h}`);
      const m = trailer.exec(text);
      if (!m) errors.push(`${log}: missing exit_code trailer`);
      else if (m[1] !== code) errors.push(`${log}: trailer exit ${m[1]} != TSV exit ${code}`);
    });
    return errors;
  },
  'template-env-agnostic': (abs) =>
    /(?<![0-9])[0-9]{12}(?![0-9])/.test(readFileSync(abs, 'utf8')) ? ['template contains a 12-digit account-like literal'] : [],
  'manifest-env-agnostic': (abs) => {
    const m = JSON.parse(readFileSync(abs, 'utf8')) as { artifacts?: Record<string, { type?: string; environment?: string }> };
    const stacks = Object.entries(m.artifacts ?? {}).filter(([, a]) => a.type === 'aws:cloudformation:stack');
    if (stacks.length === 0) return ['manifest has no stack artifacts'];
    return stacks
      .filter(([, a]) => a.environment !== 'aws://unknown-account/unknown-region')
      .map(([k, a]) => `stack ${k} has concrete environment ${a.environment}`);
  },
  'nag-zero-noncompliant': (abs) => {
    const lines = readFileSync(abs, 'utf8').split('\n').filter((l) => l.trim());
    const header = parseCsvRow(lines[0] ?? '');
    const idx = header.indexOf('Compliance');
    if (idx < 0) return ['nag report has no Compliance column'];
    const rows = lines.slice(1).map(parseCsvRow);
    if (rows.length === 0) return ['nag report has no rule rows'];
    const bad = rows.filter((r) => r[idx] === 'Non-Compliant');
    return bad.map((r) => `nag Non-Compliant: ${r[0]} on ${r[1]}`);
  },
  'jest-all-passed': (abs) => {
    const j = JSON.parse(readFileSync(abs, 'utf8')) as { success?: boolean; numFailedTests?: number; numTotalTests?: number };
    const e: string[] = [];
    if (j.success !== true) e.push('jest success is not true');
    if (j.numFailedTests !== 0) e.push(`jest numFailedTests=${j.numFailedTests}`);
    if (!j.numTotalTests) e.push('jest numTotalTests is 0');
    return e;
  },
};

/** Validate an evidence directory against the schema. evidenceRoot defaults to <repoRoot>/<schema.root>. */
export function validateEvidence(repoRoot: string, schema: EvidenceSchema, evidenceRoot = join(repoRoot, schema.root)): ValidationResult {
  const errors = validateSchemaShape(schema);
  const checked: string[] = [];
  for (const f of schema.files) {
    const abs = join(evidenceRoot, f.path);
    if (!existsSync(abs)) { if (f.required) errors.push(`missing required file: ${f.path}`); continue; }
    checked.push(f.path);
    if (f.format === 'json') {
      try { JSON.parse(readFileSync(abs, 'utf8')); } catch { errors.push(`${f.path}: invalid JSON`); continue; }
    }
    for (const r of f.rules ?? []) {
      const fn = RULES[r];
      if (!fn) { errors.push(`${f.path}: no implementation for rule ${r}`); continue; }
      errors.push(...fn(abs, { repoRoot, evidenceRoot, schema }).map((e) => `[${r}] ${e}`));
    }
  }
  return { ok: errors.length === 0, errors, checked };
}

export function loadSchema(path: string): EvidenceSchema {
  return JSON.parse(readFileSync(path, 'utf8')) as EvidenceSchema;
}
