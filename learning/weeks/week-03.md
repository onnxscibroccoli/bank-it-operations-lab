# Week 3: Remediation, private VPC + private RDS, NIST pack (AWS/IaC 3 of 3)

**Branch:** `$PR5` = `aws-remediation-vpc-rds@099479e` (PR #5).
**Delivered files used:** `infra/aws-cdk/bin/app.ts` (AwsSolutions + NIST80053R5 Aspects), `lib/network-database-stack.ts`,
`lib/least-privilege-key.ts`, `lib/guards.ts`, `lib/secure-storage-stack.ts`, `test/{negative-controls,network-database-stack,secure-storage-stack}.test.ts`,
`docs/adr/ADR-0004-no-self-logging-log-sink.md`, `evidence/aws/aws-remediation-vpc-rds/{CORRECTION_PASSES.md,SECURITY_EXCEPTIONS.md,pass0-nag/,pass1-nag/,cdk-nag/}`.

## Daily exercises
**Day 1: Read the network stack.** In `network-database-stack.ts`, find: `PRIVATE_ISOLATED` subnets only, `DB_PORT = 5433`,
`multiAz: true`, `deletionProtection: true`, `backupRetention: Duration.days(14)`, PostgreSQL `VER_17_9`, and the Secrets Manager interface endpoint used for rotation.

**Day 2: Tests.** `cd $PR5/infra/aws-cdk && npm ci --no-audit --no-fund && npx tsc --noEmit && npm test`
- *Expected:* `Test Suites: 3 passed`, `Tests: 33 passed`. (Executed: E01. On a heavily loaded box `tsc` took about 22 min. Normally it takes seconds.)

**Day 3: Synth and nag reports.** Synth as in week 1, then count rows per report:
```bash
for f in cdk.out/*NagReport.csv; do echo "$(basename $f) rows=$(tail -n +2 $f|grep -c .) nc=$(grep -c '"Non-Compliant"' $f) sup=$(grep -c '"Suppressed"' $f)"; done
```
- *Expected:* AwsSolutions NetworkDatabase 28/0/2, AwsSolutions SecureStorage 11/0/0, NIST NetworkDatabase 53/0/0, NIST SecureStorage 19/0/3.
  All four CSVs are byte-identical to `evidence/aws/aws-remediation-vpc-rds/cdk-nag/`. (Executed: E01.)

**Day 4: Correction passes.** Diff `pass0-nag/` against `pass1-nag/` and `cdk-nag/`. Explain each change in `CORRECTION_PASSES.md`
(LogRetention Lambda replaced by pre-created log groups; rotation through an endpoint; dedicated no-egress SGs; EX-04).

**Day 5: The exception register.** For EX-01..EX-04, find the matching `NagSuppressions` call and the test
`only registered exceptions are suppressed`.

## Failure injection and recovery
1. **Re-add self-logging** (template copy):
   `python3 $LAB/learning/exercises/inject-s3-selflog.py $PR5/evidence/aws/aws-remediation-vpc-rds/synth/BankItLabSecureStorage.template.json > /tmp/inj.json && python3 $PR3/evidence/shared/validate_evidence.py cfn-s3-selflog /tmp/inj.json`
   *Expected:* `ERROR AccessLogsBucket83982689 … infinite loop`, exit 1. The unmodified template gives `S3 LOGGING OK: 2 buckets checked`. (Executed: E04.)
2. **Make RDS public (scratch tree).** The repo's own negative test does this in memory: `negative-controls.test.ts`,
   "flipping PubliclyAccessible=true on the real DB is caught". It is covered by the 33/33 run.
3. **Open an SG to 0.0.0.0/0** (in memory, `openSecurityGroupRules` test). Covered by 33/33.

## Answer notes
- Guards exist because cdk-nag alone does not catch self-logging. There is a test with that name in `negative-controls.test.ts`.
- `PubliclyAccessible` omitted is treated as a violation, because the CloudFormation default depends on the subnet type (`guards.ts` comment).
- EX-02 (no cross-region replication) is a deployment-design gap, not something solved here.

## Architecture tradeoffs
- Isolated subnets with no NAT means no internet egress. Rotation then needs an interface endpoint and SG-to-SG rules (pass 3 found the missing 443 rule).
- AWS-managed `AWSBackupServiceRolePolicyForBackup` (EX-04) versus a hand-written policy that drifts from AWS updates.
- A non-default port (5433) satisfies AwsSolutions-RDS11, but it is obscurity, not access control.

## Fifteen-minute walkthrough
Template resource counts (4 subnets, 4 SGs, 2 KMS keys, a DB instance, the Backup trio) → guards → the exception register → the "no control weakened" statement in CORRECTION_PASSES.md.

## Interview questions
1. Why does secret rotation need a VPC endpoint in this design?
2. What is the risk of the CDK `Secret` adding account-root key-policy statements, and why is it acceptable here (`kms:ViaService`)?
3. When is a scoped suppression better than code changes?
4. What would you add before deploying (bootstrap, replica stack, Access Analyzer)?

## PENDING / UNEXECUTED
- Template drift note: a fresh synth of `BankItLabNetworkDatabase` with `--no-asset-metadata` differs from the committed template only by
  the `aws:asset:*` Metadata on the rotation Lambda. This is a flag difference, not a code change (E01).
- Any deployment or `cdk diff` against an account: out of scope, never executed.
