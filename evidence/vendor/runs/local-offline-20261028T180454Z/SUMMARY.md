# SIMULATION evidence run `local-offline-20261028T180454Z`

> Fictional vendor 'Acme Core Ledger SIMULATION'. Offline; no network, no real vendor, no customer data. No authoritative compatibility evidence exists for any real vendor or product (including Banno / Jack Henry).

- commit `77d0c941af346180426445d2eda619f2d401252e` on `vendor-mock` (inputs dirty: False)
- Python 3.13.5; started 2026-10-28T18:04:54.746555+00:00
- **Overall: PASS**

| # | Step | Kind | Expected exit | Exit | Result | Log |
|---|---|---|---|---|---|---|
| 1 | python_version | env | 0 | 0 | PASS | `logs/01_python_version.log` |
| 2 | contract_json_parses | check | 0 | 0 | PASS | `logs/02_contract_json_parses.log` |
| 3 | unit_tests | test | 0 | 0 | PASS | `logs/03_unit_tests.log` |
| 4 | simulation_label_scan | check | 0 | 0 | PASS | `logs/04_simulation_label_scan.log` |
| 5 | governance_lint | check | 0 | 0 | PASS | `logs/05_governance_lint.log` |
| 6 | neg_governance_lint_blank_raci_template | negative | 1 | 1 | PASS | `logs/06_neg_governance_lint_blank_raci_template.log` |
| 7 | neg_governance_lint_two_accountable | negative | 1 | 1 | PASS | `logs/07_neg_governance_lint_two_accountable.log` |
| 8 | neg_mutation_validator_ignores_extra_fields | negative | 1 | 1 | PASS | `logs/08_neg_mutation_validator_ignores_extra_fields.log` |
| 9 | neg_mutation_client_ignores_retry_after_cap | negative | 1 | 1 | PASS | `logs/09_neg_mutation_client_ignores_retry_after_cap.log` |
