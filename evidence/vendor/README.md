# Vendor integration evidence — SIMULATION

> **SIMULATION.** Every run here exercises the **fictional** "Acme Core Ledger SIMULATION" mock and
> the lab's vendor-risk documents, offline, with synthetic data. No real vendor, network endpoint,
> credential or customer data is involved. **No authoritative compatibility evidence exists** for any
> real vendor or product (including Banno / Jack Henry); this evidence shows only that the lab
> client behaves correctly against the lab's own fictional contract.

## Generate / verify

```bash
python3 evidence/vendor/generate_evidence.py          # requires committed inputs; -> runs/local-offline-<UTC>/
python3 evidence/vendor/generate_evidence.py --verify evidence/vendor/runs/<RUN_LABEL>
```

```
runs/<RUN_LABEL>/
  SUMMARY.json   commit, branch, UTC times, Python, SHA-256 of every input file, per-step expected/actual exit
  SUMMARY.md     human-readable rendering
  COMMANDS.tsv   seq, step_id, kind, expected_exit, exit_code, result, started_utc, duration_ms, log, command
  logs/NN_*.log  full stdout/stderr per step with exit-code footer
  SHA256SUMS     SHA-256 of every other file in the run directory
```

Steps: Python version; contract JSON parses; full unittest suite (`-v`, 45 tests); SIMULATION-label
scan over `integrations/vendor-mock` and `governance/vendor-risk`; governance lint; and four
**negative** steps that must exit 1 — lint of the blank RACI template, lint of a RACI with two
Accountables, and two mutation runs (validator ignoring extra fields; client ignoring the
Retry-After cap) proving the suite catches a lenient implementation (no false PASS).

## Evidence → control mapping (SIMULATION; control IDs refer to `governance/vendor-risk`)

| Control / question | What the evidence shows | Where |
|---|---|---|
| A1/A2 Access — authentication & least privilege | invalid client, wrong secret, unknown client → `AuthenticationError`, no resource call; rejected token re-auth once then fail; missing scope → 403 | `unit_tests` log: `AuthenticationFailure.*`, `HappyPath.test_not_found_and_forbidden`, `test_insufficient_scope_is_403` |
| A3 Credential handling | client secret never appears in exception text or `repr` | `test_secret_never_leaks_into_errors_or_repr` |
| B6 / C7 Availability — timeout behaviour | bounded retries with exponential backoff, then `VendorTimeoutError`; transient timeout recovers | `Timeout.*` |
| B6 / C7 Availability — rate limiting | 429 honours `Retry-After`, bounded retries; excessive Retry-After fails fast; bad/missing Retry-After rejected | `RateLimiting.*`, `ValidatorNegatives.test_raw_response_negatives` |
| C9 Processing integrity — fail closed | 9 malformed classes × 2 endpoints all raise `MalformedResponseError` | `MalformedResponses.*` |
| C11 Integration contract | every mock response and fixture validates against `contract/openapi.json`; validator rejects each violation class | `test_contract.py` (`MockResponsesMatchContract`, `Fixtures`, `ValidatorNegatives`) |
| C11 Test effectiveness | mutants of validator and client make the suite fail | `neg_mutation_*` logs (expected exit 1) |
| §2 / §8 Data minimization | unexpected `ssn` field rejected, not passed through; masked account-number pattern enforced | `test_extra_pii_field_is_rejected_not_passed_through`, `test_pattern_unmasked_account_number` |
| Offline / synthetic-only | sockets blocked for the whole test run; all fixtures and documents labelled SIMULATION | `Offline.test_sockets_are_blocked`, `simulation_label_scan` |
| RACI accountability | exactly one Accountable per activity; lint fails on blank template / duplicate A | `governance_lint`, `neg_governance_lint_*` |
| C1, C6, E1–E7, X1–X6 | **Not evidenced by tests** — documentary/contractual controls; see findings F1–F5 in the SIMULATION assessment | `governance/vendor-risk/examples/` |

## CI

`main` has no CI workflow and `.github/**` is outside this change's ownership, so the suite is not
wired into CI here. Suggested job step (for an owner of `.github/**`):
`cd integrations/vendor-mock && python3 -m unittest discover -s tests -t .`
