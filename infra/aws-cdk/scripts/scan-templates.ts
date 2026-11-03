/**
 * Read-only static scan of synthesized CloudFormation templates with lib/guards.ts.
 * Usage: npx ts-node scripts/scan-templates.ts <template.json>...   Exit 1 if any violation is found.
 * Static evidence only: a clean scan does NOT prove how AWS evaluates these policies at runtime.
 */
import { readFileSync } from 'fs';
import { allViolations } from '../lib/guards';

let total = 0;
for (const f of process.argv.slice(2)) {
  const v = allViolations(JSON.parse(readFileSync(f, 'utf8')));
  total += v.length;
  console.log(`${f}: ${v.length} violation(s)`);
  for (const x of v) console.log(`  ${x.rule}\t${x.resource}\t${x.detail}`);
}
console.log(`TOTAL ${total}`);
process.exit(total ? 1 : 0);
