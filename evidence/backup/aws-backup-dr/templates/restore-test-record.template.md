# Restore test record: <run_label>

Status: **NOT_EXECUTED** (one of NOT_EXECUTED | EXECUTED_PASS | EXECUTED_FAIL | ABORTED)

| Field | Value |
|---|---|
| Scenario (RTO_RPO.md) | |
| Change ticket / approver | |
| Operator / verifier | |
| Region / vault | |
| Recovery point ARN / created (UTC) | |
| Restore job ID | |
| Restore target identifier | |

## Timeline (UTC)
| Step | Time | Log |
|---|---|---|
| R0 declared | | |
| R3 restore started | | |
| R4 restore completed | | |
| V6 validated | | |

## Validation
| Check | Result | Log |
|---|---|---|
| V1 properties (private, encrypted, CMK, subnet group) | NOT_EXECUTED | |
| V2 TLS connectivity from inside the VPC | NOT_EXECUTED | |
| V3 fingerprints match reference | NOT_EXECUTED | |
| V4 RPO measured from restored data | NOT_EXECUTED | |
| V5 application smoke test | NOT_EXECUTED | |
| V7 negative check | NOT_EXECUTED | |

## Observed (only with logs attached)
- RPO (minutes): NOT_EXECUTED
- RTO (minutes): NOT_EXECUTED
- Copy lag (minutes, DR only): NOT_EXECUTED

Compared with the HYPOTHESIS targets in RTO_RPO.md: <met / missed / n/a>

## Cleanup
- C1 restored resource deleted: NOT_EXECUTED
- C2 no leftovers: NOT_EXECUTED

Attach `COMMANDS.tsv`, `logs/`, and `SHA256SUMS` in this run directory.
