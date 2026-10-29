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

## Pass 4 (post-review fix B5-2, 2026-10-28 ~21:30 EDT, integration branch)

This pass comes after the original 3-pass limit. It is a fix for independent-review finding B5-2 (PR #30 on candidate `b908a66`), not a nag-driven retry.

| Pass | Trigger | Change | Result |
|------|---------|--------|--------|
| 4 | B5-2: `KeyAdministrationByAccountRoot` granted every account principal `kms:Create*` (which includes `CreateGrant`, so it bypassed the conditioned grant statement) and `kms:Put*` (which includes `PutKeyPolicy`), with no condition | The statement is now `KeyAdministrationByKeyAdminRoleOnly`:<br>• explicit admin actions with no `Create*`/`Put*` wildcard and no `CreateGrant`<br>• `PutKeyPolicy` kept, so the key stays manageable<br>• `ArnEquals aws:PrincipalArn` limited to role `BankItLabKmsKeyAdmin` and the account root user (break-glass)<br>• `BoolIfExists kms:BypassPolicyLockoutSafetyCheck=false`<br><br>A new guard, `KMS_UNCONDITIONED_ADMIN`/`KMS_ADMIN_WILDCARD`, has a negative control plus 2 positive tests | tsc 0, jest 36/36, synth 0, 0 unsuppressed Non-Compliant (logs/11..13) |

The pass-3 outputs it replaces are kept unmodified in `superseded/pass3-pre-B5-2/` (synth, cdk-nag, jest-results.json).
