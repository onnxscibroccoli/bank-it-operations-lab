# evidence/orgs: Organizations security reference, static evidence

**STATIC EVIDENCE ONLY.** Everything here comes from local, credential-free `tsc`, Jest, `cdk synth --no-lookups`,
cdk-nag and offline SCP linters. Nothing was deployed or bootstrapped, and no AWS API was called (logs/01 shows the
credential state). This is **not** a deployment record, an audit, or a compliance certification.

## Results (2026-10-28, America/New_York)
| Check | Log | Result |
| --- | --- | --- |
| No AWS credentials in env | logs/01 | all unset; config/credentials -> /dev/null; IMDS disabled; aws cli not installed |
| Typecheck | logs/05 | `tsc --noEmit` exit 0 |
| Unit tests | logs/06, jest-results.json | 49/49 passed (4 suites: SCPs 26, governance 9, CloudTrail 8, security services 6) |
| Synth (3 stacks) | logs/08, synth/ | exit 0; env-agnostic (`aws://unknown-account/unknown-region`) |
| cdk-nag AwsSolutions | logs/14, cdk-nag/ | 0 Non-Compliant, 0 Suppressed, no NagSuppressions in source |
| SCP export | logs/09, policies/ | 7 policies, largest 1,891 / 5,120 chars |
| In-repo SCP lint | logs/10, lint/scp-lint-report.json | 0 errors, 0 warnings |
| parliament 1.6.4 raw | logs/12 | 2 MEDIUM findings (exit 1), both false positives from parliament's stale database |
| parliament gated | logs/13 | 0 non-allowlisted findings (2 allowlisted with sources in infra/orgs/parliament-allowlist.json) |
| No hard-coded account ids | logs/15 | none in lib/, bin/, synth/, policies/ |

cdk-nag coverage note: AwsSolutions has no rules for Organizations, GuardDuty or Security Hub resource types. Those two
reports have 0 rows. Unit tests cover those stacks instead. The CloudTrail stack has 14 Compliant rule rows.

## Layout
- run-cmd.sh: credential-free wrapper (runs in infra/orgs, logs cwd/command/start/finish/exit code, appends logs/COMMANDS.tsv).
- no-credentials-check.sh: reports whether AWS credential variables are set (never prints values).
- update-sha256sums.sh / SHA256SUMS: hashes of every tracked file in infra/orgs and evidence/orgs except SHA256SUMS
  (verify from repo root: `sha256sum -c evidence/orgs/SHA256SUMS`).
- synth/: synthesized templates + manifest. cdk-nag/: NagReport CSVs + validation-report.json.
- policies/: exported SCP JSON (source: infra/orgs/lib/scps.ts). lint/: in-repo lint report.

## Reproduce (from repo root; parliament needs `pip install parliament==1.6.4 'setuptools<81'`)
    evidence/orgs/run-cmd.sh 04-npm-ci npm ci --no-audit --no-fund
    evidence/orgs/run-cmd.sh 05-tsc-noemit npx tsc --noEmit
    evidence/orgs/run-cmd.sh 06-jest npx jest --ci --json --outputFile=../../evidence/orgs/jest-results.json
    evidence/orgs/run-cmd.sh 08-cdk-synth npx cdk synth --no-lookups --no-version-reporting --no-path-metadata --no-asset-metadata --quiet
    evidence/orgs/run-cmd.sh 14-cdk-nag-gate bash scripts/nag-gate.sh
    evidence/orgs/run-cmd.sh 09-export-policies npx ts-node scripts/export-policies.ts
    evidence/orgs/run-cmd.sh 10-lint-policies npx ts-node scripts/lint-policies.ts
    evidence/orgs/run-cmd.sh 13-parliament-gated scripts/parliament.sh gated

## Known gaps
- GuardDuty delegated admin and org auto-enable have no CloudFormation resource (infra/orgs/docs/adr/ADR-0002).
- Security Hub configuration policies are not modelled yet.
- The offline SCP evaluator is not AWS's policy engine. Before adoption, validate with IAM Access Analyzer in a sandbox org.
- No CI workflow: `.github/**` is outside the allowed paths for this change.
- jest-results.json contains absolute paths from the build machine (/workspace/...).
