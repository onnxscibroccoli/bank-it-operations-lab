# ci-selftest-40741329107-1-A

Status: CURRENT (harness v2). Mode: `selftest`. Overall: **FAIL**
(2/12 passed; 5 failed, 5 errors, 2 not run).

| # | step | kind | expected | exit | result | class |
|---|------|------|----------|------|--------|-------|
| 1 | ST01_control_expected_fault | negative | nonzero | 3 | PASS | expected_fault_detected |
| 2 | ST02_unexpected_success | negative | nonzero | 0 | FAIL | unexpected_success |
| 3 | ST03_wrong_reason | negative | nonzero | 1 | FAIL | wrong_reason |
| 4 | ST04_version_mismatch_masquerade | negative | nonzero | 1 | ERROR | version_mismatch |
| 5 | ST05_missing_executable | negative | nonzero | 127 | ERROR | missing_executable |
| 6 | ST06_setup_failure | setup | zero | 1 | ERROR | setup_failure |
| 7 | ST07_dependent_on_failed_setup | negative | nonzero | - | NOT_RUN | dependency_failed:ST06_setup_failure |
| 8 | ST08_pipeline_failure_hidden_by_tail | positive | zero | 1 | FAIL | positive_failed |
| 9 | ST09_positive_wrong_output | positive | zero | 0 | FAIL | output_mismatch |
| 10 | ST11_run_twice | positive | zero | 0 | PASS | positive_ok |
| 11 | ST11_run_twice | positive | zero | - | FAIL | duplicate_test |
| 12 | ST12_version_gate | setup | zero | 1 | ERROR | version_mismatch |
| 13 | ST99_undeclared | undeclared | - | - | ERROR | undeclared_test |
| 14 | ST10_declared_but_never_run | negative | nonzero | - | NOT_RUN | missing_test |
