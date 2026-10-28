# acceptance/modules: existing-module adapters (Worker C)

Three adapters connect the **existing** module checks to an acceptance result contract. They do **not** rebuild
the modules: each one calls the module's own validator, verifier, test suite and committed evidence, then maps
the outcome to contract fields and reason codes. They run offline only. No AWS, Entra or Graph calls are made,
credential variables are scrubbed (same list as `scripts/validate-all.sh`), and nothing is deployed or mutated.

| Adapter | Wraps (source PR) | Static-evidence checks | Extra live-offline checks |
|---|---|---|---|
| `aws_cdk.py` → `aws-cdk` | `infra/aws-cdk` + `evidence/aws/aws-remediation-vpc-rds` (#5), shared validator (#3) | bundle `SHA256SUMS` (shared `hashes`); recorded Jest run has 0 failures and includes `negative-controls`; exactly 4 cdk-nag reports with 0 Non-Compliant rows; `cfn-s3-selflog` on committed templates | fresh `jest --ci`; credential-free `cdk synth`; nag/self-logging checks on the fresh output; byte-for-byte synth drift against the committed templates |
| `postgres.py` → `postgres` | harness v2 `tests/integration/postgres` + `evidence/postgres/runs` (#2 @ e7399fb), shared validator (#3) | runs are classified from `INDEX.md`; every CURRENT v2 run must be VERIFIED by `verify_evidence.py`, have ≥6 negatives, and pass the shared `postgres-negatives` check; the mismatch control must be REJECTED **with class `version_mismatch`**; HISTORICAL runs must exit 3 | fresh `run_restore_scenario.sh offline` (throwaway unix-socket cluster), then the verifier with `--require-artifacts` and the shared cross-check |
| `entra_offline.py` → `entra-offline` | `identity/entra` + `tests/entra` + `evidence/entra/runs` (#4) | baseline policies PASS; report is `offline-synthetic` with `tenantStateClaimed=false`; every fixture in the module's own `BASELINE_NEGATIVES` / `MALFORMED` maps (imported from `tests/entra/test_ca_validator.py`) is rejected with the expected exit class **and** expected rule id; committed evidence runs pass `generate_evidence.py --verify` | `tests/entra` unittest suite; fixture drift check |

## Contract
No shared acceptance contract existed on any branch when this was written, so `contract.py` defines a
**provisional** one (`bank-it-lab/acceptance-module-result/v0-provisional`). The adapters build results only
through `ModuleResult` and `Check`, so aligning with the shared contract later should only require changes to
`contract.py`. Fields: `contract, module, adapter, source{prs,paths}, mode, status, reason_code, reason_codes,
checks[{id,title,kind,status,reason_code,detail,evidence}], evidence[{path,sha256}], claims{...all false},
started_utc, finished_utc, git_sha`. A failing check must carry a non-`OK` reason code from `REASON_CODES`.

## Run
```bash
python3 acceptance/modules/run.py all                       # static-evidence (stdlib only, ~2 s)
PG_BIN=/path/to/pg/bin python3 acceptance/modules/run.py all --mode live-offline   # needs npm ci in infra/aws-cdk + PG binaries
python3 acceptance/modules/run.py postgres --json-out result.json
python3 -m unittest discover -s acceptance/modules/tests    # adapter tests, including negatives
```
Exit codes: 0 PASS, 1 FAIL, 2 ERROR, 4 NOT_EXECUTED. In live mode, a missing toolchain is reported as
`NOT_EXECUTED/TOOL_UNAVAILABLE` and never as PASS.

## Negative tests (each asserts the specific reason code, and that it is the *only* non-PASS check)
Tests copy the existing evidence to a temp dir, inject one fault and, where needed, re-seal the hashes so that
the fault under test is the only one present. Without the re-seal, every negative would fail on hashes.
- aws-cdk: tampered log → `EVIDENCE_HASH_MISMATCH`; injected Non-Compliant row → `NAG_NON_COMPLIANT`; missing nag
  report → `NAG_REPORT_COUNT`; failed Jest run → `UNIT_TESTS_FAILED`; Jest run missing the `negative-controls` suite → `UNIT_TESTS_FAILED`;
  bucket logging to itself → `S3_SELF_LOGGING`; missing bundle → `EVIDENCE_MISSING`.
- postgres: tampered log → `EVIDENCE_HASH_MISMATCH`; N01 failing with a *different* error → `NEGATIVE_WRONG_REASON`;
  N01 exiting 0 → `NEGATIVE_UNEXPECTED_SUCCESS`; run marked HISTORICAL → `EVIDENCE_HISTORICAL`; control that verifies →
  `CONTROL_NOT_REJECTED`; control rejected for a class other than `version_mismatch` → `NEGATIVE_WRONG_REASON`.
- entra-offline: MFA policy removed → `BASELINE_RULE_FAILED` (BASE-003); malformed policy set → `INPUT_MALFORMED`
  (SCHEMA-001); fixture declared for the wrong rule → `NEGATIVE_WRONG_REASON`; valid fixture declared negative →
  `NEGATIVE_UNEXPECTED_SUCCESS`; malformed fixture declared as baseline-negative (exit 2 vs 1) → `NEGATIVE_WRONG_REASON`;
  no declared negatives → `NEGATIVE_COUNT`; tampered evidence → `EVIDENCE_HASH_MISMATCH`.
