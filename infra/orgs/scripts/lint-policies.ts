import { mkdirSync, writeFileSync } from 'fs';
import { join } from 'path';
import { lintScp, minifiedLength, SCP_MAX_CHARS } from '../lib/policy-lint';
import { SCPS } from '../lib/scps';

/** Offline SCP lint; writes evidence/orgs/lint/scp-lint-report.json and exits 1 on any ERROR. */
mkdirSync(join(__dirname, '..', '..', '..', 'evidence', 'orgs', 'lint'), { recursive: true });
const report = SCPS.map((s) => ({
  id: s.id, name: s.name, minifiedChars: minifiedLength(s.document), maxChars: SCP_MAX_CHARS,
  statements: s.document.Statement.length, findings: lintScp(s),
}));
const errors = report.flatMap((r) => r.findings).filter((f) => f.severity === 'ERROR').length;
const warnings = report.flatMap((r) => r.findings).filter((f) => f.severity === 'WARNING').length;
writeFileSync(join(__dirname, '..', '..', '..', 'evidence', 'orgs', 'lint', 'scp-lint-report.json'),
  JSON.stringify({ policies: report, errors, warnings }, null, 2) + '\n');
for (const r of report) console.log(`${r.id}: ${r.minifiedChars}/${r.maxChars} chars, ${r.findings.length} findings`);
console.log(`errors=${errors} warnings=${warnings}`);
process.exit(errors > 0 ? 1 : 0);
