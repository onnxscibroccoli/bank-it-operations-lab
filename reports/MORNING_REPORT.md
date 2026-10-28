# MORNING REPORT: BANK-AWS-001 (overnight 2026-10-28)

> Static lab evidence only. No AWS credentials, no deployment, no production change, not a certification.

## Status
- Branch `bank-aws-001` pushed to https://github.com/onnxscibroccoli/bank-it-operations-lab
- Draft PR: https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1 (not merged; main untouched)
- CI workflow `bank-aws-001-cdk`: see Actions runs below.

## Commits (on top of origin/main 7f50348)
See `git log origin/main..bank-aws-001` and `evidence/aws/logs/REBASE-MAP.md`.
| SHA | Summary |
|---|---|
| f24818b | pre-implementation record (was 84e0e1e) |
| 03b93d1 | stack, tests, cdk-nag, static evidence (was 15421c9) |
| 22c72b0 | git/GitHub ops evidence logger and rebase map |
| 88684d1 | credential-free CI workflow |
| af76d20 | evidence schema + validator, ADRs, READMEs, morning report skeleton |
| (next) | CI run record, Drive checkpoint record |

## Actions runs
| Run | Head | Conclusion |
|---|---|---|
| https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630567160 | 88684d1 | success |
| https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630990406 | af76d20 | success |

Full record: `evidence/aws/ci/RUNS.md`. CI correction passes used: 0 of 3.

## Checks (local, credential-free; logs in evidence/aws/logs)
- `npm ci` 0 (log 40), `tsc --noEmit` 0 (41), `cdk synth --no-lookups` 0 (42), Jest 21/21 (43), evidence validator VALID (44).
- cdk-nag AwsSolutions: 11 rules Compliant, 0 Non-Compliant, 0 suppressions. Template unchanged vs. prior evidence.

## Evidence
- `evidence/aws/evidence-schema.json` + `infra/aws-cdk/lib/evidence-validator.ts` (`npm run validate:evidence`).
- `evidence/aws/SHA256SUMS` (regenerated per commit), `evidence/aws/logs/COMMANDS.tsv` (every command + exit code).
- Drive checkpoints: folder `1CqK-pYAFx3bsXI5ggMpvmh-XloO00DwE` (see `evidence/aws/ci/DRIVE_CHECKPOINTS.md`).

## Decisions
- ADR-0001 cdk-nag 2.x pin; ADR-0002 SSE-S3 for access-log bucket; ADR-0003 credential-free env-agnostic synth
  (`infra/aws-cdk/docs/adr/`).

## Gaps / risks
- KMS key policy is the CDK default (account root); not tightened.
- Default synthesizer `BootstrapVersion` parameter/rule remains.
- cdk-nag pinned to 2.x; 3.x migration not done.
- `actions/upload-artifact@v4` Node 20 deprecation annotation; `ubuntu-latest` image migration in progress.
- Evidence hashes recorded before the rebase refer to pre-rebase commit 15421c9.

## Next steps (need a human)
- Review the draft PR; decide on key-policy tightening and cdk-nag 3.x.
- Mark PR ready / merge only by a reviewer.
