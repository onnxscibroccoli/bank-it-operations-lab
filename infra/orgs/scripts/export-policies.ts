import { mkdirSync, writeFileSync } from 'fs';
import { join } from 'path';
import { SCPS } from '../lib/scps';

/** Writes each SCP as pretty JSON to evidence/orgs/policies/<id>.json (offline; no AWS calls). */
const out = join(__dirname, '..', '..', '..', 'evidence', 'orgs', 'policies');
mkdirSync(out, { recursive: true });
for (const s of SCPS) {
  writeFileSync(join(out, `${s.id}.json`), JSON.stringify(s.document, null, 2) + '\n');
  console.log(`wrote ${s.id}.json (${JSON.stringify(s.document).length} chars minified)`);
}
