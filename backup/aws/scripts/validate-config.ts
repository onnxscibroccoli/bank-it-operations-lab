/** Credential-free config check: prints findings as JSON, exits 1 on any error-level finding. */
import { loadPolicy, POLICY_PATH, validatePolicy } from '../lib/policy';

const file = process.argv[2] ?? POLICY_PATH;
const findings = validatePolicy(loadPolicy(file));
const errors = findings.filter((f) => f.level === 'error');
console.log(JSON.stringify({ file, errors: errors.length, warnings: findings.length - errors.length, findings }, null, 2));
process.exit(errors.length ? 1 : 0);
