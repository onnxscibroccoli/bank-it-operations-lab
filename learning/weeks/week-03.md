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

## Review findings to work through (from #14, re-verified here)
- **B5-2: KMS key-admin escalation.** Run:
```bash
for t in $PR5/evidence/aws/aws-remediation-vpc-rds/synth/*.template.json; do python3 -c "import json,sys;t=json.load(open(sys.argv[1]))
[print(k,s['Sid'],[a for a in s['Action'] if a in ('kms:Create*','kms:Put*')],'Condition' in s) for k,v in t['Resources'].items() if v['Type']=='AWS::KMS::Key' for s in v['Properties']['KeyPolicy']['Statement'] if s.get('Sid')=='KeyAdministrationByAccountRoot']" $t; done
```
  *Observed (R07):* all three CMKs (`LogsKeyA6AB43B2`, `DatabaseKey7576F140`, `DataKey17AFBB84`) each have `KeyAdministrationByAccountRoot` with `kms:Create*` and `kms:Put*`, and `Condition` is `False`.
  `kms:Create*` covers `kms:CreateGrant` and `kms:Put*` covers `kms:PutKeyPolicy`, so an account principal allowed by IAM could grant itself use of the key.
  `guards.ts#kmsWildcards` only matches `*` and `kms:*`, so it misses this. The PR's "least-privilege CMK" claim is **not proven** (#14 B5-2). There is no fix on any branch.
- **B5-1: suppressions applied before approval.** All 5 are active while `SECURITY_EXCEPTIONS.md` says PROPOSED. #11 records decisions relayed from a security review
  (`reports/final-report@54d6fbd:reports/USER_ACTIONS_REQUIRED.md`: EX-01 ACCEPTED, EX-02 ACCEPTED as a limitation, EX-03 OPEN, EX-04 CONDITIONALLY ACCEPTABLE), **not yet recorded in #5**.
- **Scanner blind spots** (#14): the default-SG custom-resource Lambda, the SAR rotation nested stack, the Backup resources, the VPC endpoint, the flow log and the standalone SG egress rules appear in no NagReport row. "0 findings" does not cover them.
- **Integration status:** #7 integrates #5 and drops #1's copy of `infra/aws-cdk` (`overnight/integration@49122f2:reports/INTEGRATION.md`). Its `validate-all.sh` re-ran tsc, Jest 33/33, synth, the 4-report nag gate, `cfn-s3-selflog` and synth drift: PASS (R05).

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
2. The `Secret` statements are scoped by `kms:ViaService`, but the key-admin statement is not (B5-2). How would you fix B5-2 without locking yourself out of the key?
3. When is a scoped suppression better than code changes?
4. What would you add before deploying (bootstrap, replica stack, Access Analyzer)?

## PENDING / UNEXECUTED
- Template drift note: a fresh synth of `BankItLabNetworkDatabase` with `--no-asset-metadata` differs from the committed template only by
  the `aws:asset:*` Metadata on the rotation Lambda. This is a flag difference, not a code change (E01).
- Any deployment or `cdk diff` against an account: out of scope, never executed.
