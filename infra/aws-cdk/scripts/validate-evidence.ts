#!/usr/bin/env node
/* Validates evidence/aws against evidence/aws/evidence-schema.json. Exit 0 = valid, 1 = invalid. */
import { join, resolve } from 'path';
import { loadSchema, validateEvidence } from '../lib/evidence-validator';

const repoRoot = resolve(process.argv[2] ?? join(__dirname, '..', '..', '..'));
const schema = loadSchema(join(repoRoot, 'evidence', 'aws', 'evidence-schema.json'));
const res = validateEvidence(repoRoot, schema);
console.log(`checked ${res.checked.length} files`);
for (const e of res.errors) console.error(`ERROR ${e}`);
console.log(res.ok ? 'EVIDENCE VALID' : `EVIDENCE INVALID (${res.errors.length} errors)`);
process.exit(res.ok ? 0 : 1);
