# ci-service-40741329107-1

Status: CURRENT (harness v2). Mode: `service`. Overall: **PASS**
(36/36 passed; 0 failed, 0 errors, 0 not run).

| # | step | kind | expected | exit | result | class |
|---|------|------|----------|------|--------|-------|
| 1 | S00_required_tools | setup | zero | 0 | PASS | setup_ok |
| 2 | S03_server_ready | setup | zero | 0 | PASS | setup_ok |
| 3 | S04_client_server_major_match | setup | zero | 0 | PASS | setup_ok |
| 4 | S05_reset_databases | setup | zero | 0 | PASS | setup_ok |
| 5 | S06_create_source | setup | zero | 0 | PASS | setup_ok |
| 6 | S07_seed_source | setup | zero | 0 | PASS | setup_ok |
| 7 | S08_fingerprint_source | setup | zero | 0 | PASS | setup_ok |
| 8 | S09_fingerprint_source_sanity | setup | zero | 0 | PASS | setup_ok |
| 9 | P01_pg_dump_custom | positive | zero | 0 | PASS | positive_ok |
| 10 | P02_pg_restore_list | positive | zero | 0 | PASS | positive_ok |
| 11 | P03_createdb_target | positive | zero | 0 | PASS | positive_ok |
| 12 | P04_pg_restore | positive | zero | 0 | PASS | positive_ok |
| 13 | P05_fingerprint_restored | positive | zero | 0 | PASS | positive_ok |
| 14 | P06_compare_restored | positive | zero | 0 | PASS | positive_ok |
| 15 | P07_pg_dump_plain | positive | zero | 0 | PASS | positive_ok |
| 16 | P08_createdb_plain | positive | zero | 0 | PASS | positive_ok |
| 17 | P09_psql_restore_plain | positive | zero | 0 | PASS | positive_ok |
| 18 | P10_fingerprint_plain | positive | zero | 0 | PASS | positive_ok |
| 19 | P11_compare_plain | positive | zero | 0 | PASS | positive_ok |
| 20 | S_N01_createdb | setup | zero | 0 | PASS | setup_ok |
| 21 | S_N01_make_truncated_dump | setup | zero | 0 | PASS | setup_ok |
| 22 | N01_restore_truncated_dump | negative | nonzero | 1 | PASS | expected_fault_detected |
| 23 | S_N02_make_garbage_file | setup | zero | 0 | PASS | setup_ok |
| 24 | N02_list_garbage_archive | negative | nonzero | 1 | PASS | expected_fault_detected |
| 25 | S_N03_assert_database_absent | setup | zero | 0 | PASS | setup_ok |
| 26 | N03_restore_missing_database | negative | nonzero | 1 | PASS | expected_fault_detected |
| 27 | S_N04_precondition | setup | zero | 0 | PASS | setup_ok |
| 28 | N04_fk_enforced_after_restore | negative | nonzero | 1 | PASS | expected_fault_detected |
| 29 | S_N05_createdb | setup | zero | 0 | PASS | setup_ok |
| 30 | S_N05_first_restore | setup | zero | 0 | PASS | setup_ok |
| 31 | N05_restore_over_existing_objects | negative | nonzero | 1 | PASS | expected_fault_detected |
| 32 | S_N06_createdb | setup | zero | 0 | PASS | setup_ok |
| 33 | S_N06_restore | setup | zero | 0 | PASS | setup_ok |
| 34 | S_N06_tamper_row | setup | zero | 0 | PASS | setup_ok |
| 35 | S_N06_fingerprint_tampered | setup | zero | 0 | PASS | setup_ok |
| 36 | N06_tamper_detected | negative | nonzero | 1 | PASS | expected_fault_detected |
