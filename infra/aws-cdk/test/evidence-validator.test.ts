import { createHash } from 'crypto';
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync, appendFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';
import { EvidenceSchema, loadSchema, validateEvidence, validateSchemaShape } from '../lib/evidence-validator';

const repoRoot = join(__dirname, '..', '..', '..');
const schema = loadSchema(join(repoRoot, 'evidence', 'aws', 'evidence-schema.json'));

/** Copy owned paths into a temp "repo" so negative cases never touch real evidence. */
function scratchRepo(): string {
  const dir = mkdtempSync(join(tmpdir(), 'bank-aws-001-ev-'));
  cpSync(join(repoRoot, 'evidence', 'aws'), join(dir, 'evidence', 'aws'), { recursive: true });
  cpSync(join(repoRoot, 'infra', 'aws-cdk'), join(dir, 'infra', 'aws-cdk'), {
    recursive: true,
    filter: (s) => !/node_modules|cdk\.out/.test(s),
  });
  for (const f of ['.github/workflows/bank-aws-001-cdk.yml', 'reports/MORNING_REPORT.md']) {
    try { cpSync(join(repoRoot, f), join(dir, f)); } catch { /* optional */ }
  }
  return dir;
}

describe('evidence schema descriptor', () => {
  test('is well-formed and every referenced rule is defined', () => {
    expect(validateSchemaShape(schema)).toEqual([]);
    expect(schema.task).toBe('BANK-AWS-001');
  });
  test('rejects undefined rules and duplicate paths', () => {
    const bad: EvidenceSchema = { ...schema, files: [...schema.files, { ...schema.files[0], rules: ['nope'] }] };
    const errs = validateSchemaShape(bad);
    expect(errs.some((e) => e.includes('duplicate path'))).toBe(true);
    expect(errs.some((e) => e.includes('undefined rule nope'))).toBe(true);
  });
});

describe('committed evidence bundle', () => {
  test('validates cleanly', () => {
    const res = validateEvidence(repoRoot, schema);
    expect(res.errors).toEqual([]);
    expect(res.ok).toBe(true);
    expect(res.checked.length).toBe(schema.files.length);
  });
});

describe('negative cases (scratch copy)', () => {
  let dir: string;
  beforeEach(() => { dir = scratchRepo(); });
  afterEach(() => rmSync(dir, { recursive: true, force: true }));

  test('detects a missing required file', () => {
    rmSync(join(dir, 'evidence/aws/jest-results.json'));
    expect(validateEvidence(dir, schema).errors).toContain('missing required file: jest-results.json');
  });
  test('detects a tampered file via SHA256SUMS', () => {
    appendFileSync(join(dir, 'evidence/aws/README.md'), '\ntampered\n');
    expect(validateEvidence(dir, schema).errors.some((e) => e.includes('SHA256SUMS mismatch: evidence/aws/README.md'))).toBe(true);
  });
  test('detects a COMMANDS.tsv exit code that disagrees with the log trailer', () => {
    const p = join(dir, 'evidence/aws/logs/COMMANDS.tsv');
    writeFileSync(p, readFileSync(p, 'utf8').replace(/^(01-node-version\.log)\t0\t/m, '$1\t7\t'));
    expect(validateEvidence(dir, schema).errors.some((e) => e.includes('01-node-version.log: trailer exit 0 != TSV exit 7'))).toBe(true);
  });
  test('detects a Non-Compliant cdk-nag row', () => {
    const p = join(dir, 'evidence/aws/cdk-nag/AwsSolutions--BankItLabSecureStorage-NagReport.csv');
    appendFileSync(p, '"AwsSolutions-S10","X/Y","Non-Compliant","N/A","Error","test"\n');
    expect(validateEvidence(dir, schema).errors.some((e) => e.includes('nag Non-Compliant: AwsSolutions-S10'))).toBe(true);
  });
  test('detects a concrete account id in the template', () => {
    const p = join(dir, 'evidence/aws/synth/BankItLabSecureStorage.template.json');
    const t = JSON.parse(readFileSync(p, 'utf8'));
    t.Metadata = { leaked: 'arn:aws:iam::123456789012:root' };
    writeFileSync(p, JSON.stringify(t));
    expect(validateEvidence(dir, schema).errors.some((e) => e.includes('12-digit'))).toBe(true);
  });
  test('sha helper sanity', () => {
    expect(createHash('sha256').update('').digest('hex')).toMatch(/^e3b0c442/);
  });
});
