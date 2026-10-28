# Week 2: S3/KMS controls and evidence integrity (AWS/IaC 2 of 3)

**Branches:** `$PR1` (`bank-aws-001@e494bcf`), `$PR3` (`review/pr1-pr2-evidence-audit@fb36341`).
**Prerequisites:** week 1, Python 3.

**Delivered files used:** `infra/aws-cdk/lib/evidence-validator.ts`, `scripts/validate-evidence.ts`, `evidence/aws/evidence-schema.json`,
`evidence/aws/SHA256SUMS`, `evidence/aws/logs/COMMANDS.tsv`, `evidence/aws/update-sha256sums.sh`, ADR-0002 (SSE-S3 log bucket);
PR #3 `evidence/shared/validate_evidence.py`, `evidence/shared/tests/test_validate_evidence.py`, `reports/review-pr1-pr2.md`.

## Daily exercises
**Day 1: Map controls to tests.** For each test name in `test/secure-storage-stack.test.ts` (TLS-only, BPA, versioning,
ACLs disabled, RETAIN, KMS rotation), find the template lines in `evidence/aws/synth/BankItLabSecureStorage.template.json` that it asserts.

**Day 2: Evidence validator.** `cd $PR1/infra/aws-cdk && npm run -s validate:evidence`
- *Expected:* `checked 18 files` and `EVIDENCE VALID`. (Executed: E02.)

**Day 3: Hashes and command logs** (from `$PR1`):
```bash
sha256sum -c evidence/aws/SHA256SUMS --quiet; echo rc=$?
python3 $PR3/evidence/shared/validate_evidence.py hashes evidence/aws/SHA256SUMS --base . --cover evidence/aws
python3 $PR3/evidence/shared/validate_evidence.py commands evidence/aws/logs/COMMANDS.tsv --format aws-3col
```
- *Expected:* rc 0, `HASHES OK: 87 entries verified`, `COMMANDS OK: 48 rows cross-checked`. (Executed: E02.)

**Day 4: Run the PR #3 tests.** `cd $PR3 && python3 -m unittest discover -s evidence/shared/tests -v`
- *Expected:* 13 tests OK. (Executed: E03.)

**Day 5: Find the defect.** `python3 $PR3/evidence/shared/validate_evidence.py cfn-s3-selflog $PR1/evidence/aws/synth/BankItLabSecureStorage.template.json`
- *Expected:* `ERROR AccessLogsBucket83982689: server access logs delivered to itself`, exit 1. (Executed: E03.)
  Explain why cdk-nag reported S1 "Compliant" for the same bucket (PR #3 §3).

## Failure injection and recovery
1. **Tamper with evidence** (scratch copy):
   `cp -r $PR5/evidence/aws/aws-remediation-vpc-rds /tmp/tamper && sed -i 's/PROPOSED/APPROVED/' /tmp/tamper/SECURITY_EXCEPTIONS.md && (cd /tmp/tamper && sha256sum -c SHA256SUMS)`
   *Expected:* `SECURITY_EXCEPTIONS.md: FAILED`, exit 1. `validate_evidence.py hashes` gives `sha256 mismatch`. (Executed: E06.)
   *Recovery:* delete `/tmp/tamper`. In a real bundle, regenerate the evidence through the logged wrapper. Never re-hash by hand.
2. **Circular evidence** (reading only): PR #3 §1 explains why `jest-results.json` partly vouches for itself. Propose a fix.

## Answer notes
- SSE-S3 on the log bucket is forced by S3 server access logging (ADR-0002). PR #5 records this as exception EX-01 under the NIST pack.
- A hash file proves integrity relative to itself, not provenance. Provenance needs a wrapper that writes the command row (PR #3 §2: `run-cmd.sh` does not).
- Self-logging creates an infinite log loop, and with versioning, RETAIN and no lifecycle rule, storage grows without bound (PR #3 §3).

## Architecture tradeoffs
- CMK everywhere versus service constraints: S3 access logs cannot target SSE-KMS buckets. The options are an exception or a different log path (CloudTrail data events).
- Satisfying a scanner rule versus doing the right thing: S1 was "met" by a configuration AWS advises against.

## Fifteen-minute walkthrough
Show `EVIDENCE VALID`, then tamper with a scratch copy to show detection, then run `cfn-s3-selflog` on the PR #1 template.
Close on "a green scanner is not correctness".

## Interview questions
1. What does SHA256SUMS prove, and what does it not prove?
2. Why can't the S3 access-log target bucket use SSE-KMS?
3. How would you stop evidence from being regenerated to hide a failure?
4. Why did cdk-nag not catch self-logging?

## PENDING / UNEXECUTED
- Writing a `MANIFEST.json` for a bundle and running `validate_evidence.py manifest` on it: no bundle ships a MANIFEST.json, so this is **UNEXECUTED** (P-W2).
