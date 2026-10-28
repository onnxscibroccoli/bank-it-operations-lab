# Evidence run index

Verify a run with: `python3 tests/integration/postgres/verify_evidence.py <dir> [--require-artifacts]`.
Exit codes: 0 = verified, 1 = rejected, 3 = historical.
All times are EDT (UTC-4).

| Run dir | Harness | Status | Result | Source |
|---|---|---|---|---|
| `ci-service-40630856041-1` | v1 | **HISTORICAL-KNOWN-INVALID** | Genuine FAIL of P04–P06 and P09–P11. **False PASS** on N01, N04, N05 and N06. See NOTE.md and STATUS.json | [run 40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041), 2026-10-28 00:10 |
| `local-offline-20261028T041038Z` | v1 | **HISTORICAL-KNOWN-INVALID** | 30/30 "PASS" under v1 rules. The logs show the intended errors, but the run is not valid v2 evidence | sandbox, 2026-10-28 00:10 |
| `ci-service-40741329107-1` | v2 | CURRENT | **PASS 36/36**, 6/6 negatives `expected_fault_detected`, verifier VERIFIED | [run 40741329107](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107) @ `2aac93c`, 2026-10-28 14:02 |
| `ci-offline-40741329107-1` | v2 | CURRENT | **PASS 38/38**, 6/6 negatives `expected_fault_detected`, verifier VERIFIED | same run |
| `ci-mismatch-control-40741329107-1` | v2 | CURRENT, **negative control** | **Expected FAIL**: `S04 ERROR/version_mismatch` (pg_dump 18 vs postgres:16). 33 NOT_RUN, 0 negative PASS. Verifier REJECTED it, as intended | same run |
| `ci-selftest-40741329107-1` | v2 | CURRENT | Self-test **PASS 26/26 assertions**: every deliberate bad case was reported FAIL, ERROR or NOT_RUN | same run |
| `local-offline-v2-20261028T180208Z` | v2 | CURRENT | **PASS 38/38**, verifier VERIFIED (sandbox, PG 16.x conda-forge) | sandbox @ `2aac93c`, 2026-10-28 14:02 |
| `local-selftest-v2-20261028T180208Z` | v2 | CURRENT | Self-test PASS 26/26 | sandbox @ `2aac93c` |

`*.ci-console/` holds the `tee`d console logs from each CI job, which are not part of the hashed run directory.
`artifacts/` (dumps) is gitignored. The CI copies are in the workflow artifacts (90-day retention), and their hashes are in each run's `ARTIFACTS.sha256`.
