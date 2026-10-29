# Correction passes (limit: 3). Failure output is kept in logs/ and pass*-nag/.

| Pass | Trigger | Change | Result |
|------|---------|--------|--------|
| 0 (initial) | first synth of the remediated code | n/a | `cdk synth` exit 1: logs/02-pass0-cdk-synth.log, pass0-nag/. 10 errors: LogRetention Lambda (IAM4, IAM5, NIST IAMNoInlinePolicy), SMG4 + NIST SecretsManagerRotationEnabled, NIST RDSInBackupPlan, IAM5 on RDSOSMetrics streams, NIST S3 replication x2, NIST S3DefaultEncryptionKMS on the log sink. |
| 1 | pass 0 errors | Pre-created KMS log groups instead of LogRetention Lambda; secret rotation via Secrets Manager interface endpoint; AWS Backup plan + CMK vault; registered EX-01..EX-03. | `cdk synth` exit 1: logs/04-pass1-cdk-synth.log, pass1-nag/. New: IAM4 on backup selection role; 2 CdkNagValidationFailure warnings (port token on rotation->DB rule); review found rotation/endpoint SGs with 0.0.0.0/0 egress. |
| 2 | pass 1 errors | Dedicated no-egress SGs for rotation and endpoint; pin rotation->DB rule to literal DB_PORT (same port); EX-04 for backup role. | `cdk synth` exit 0, 0 unsuppressed errors/warnings (logs/06-pass2-cdk-synth.log). |
| 3 | template review after pass 2 | Rotation->Secrets Manager endpoint 443 SG-to-SG rule was missing (functional gap, not a nag finding); added it. Narrowed EX-04 suppression to the role resource only. Static guards + Jest suites added. | tsc 0, jest 33/33, synth 0 (logs/07..09). |

Note: before the logged pass-3 Jest run, an unlogged development run of the new test files failed 2 suites because of
test-authoring defects (a CDK cyclic-dependency error in the two-bucket loop fixture; an over-broad EX-04 suppression
that also landed on the BackupSelection). Both were fixed (raw-template loop fixture; suppression scoped to the role).
No control was weakened to make anything pass.
