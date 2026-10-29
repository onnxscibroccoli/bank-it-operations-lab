# local-selftest-v2-20261028T180208Z-B

Status: CURRENT (harness v2). Mode: `service`. Overall: **FAIL**
(2/36 passed; 0 failed, 4 errors, 30 not run).

| # | step | kind | expected | exit | result | class |
|---|------|------|----------|------|--------|-------|
| 1 | N01_restore_truncated_dump | negative | nonzero | 1 | ERROR | version_mismatch |
| 2 | N02_list_garbage_archive | negative | nonzero | 1 | PASS | expected_fault_detected |
| 3 | N03_restore_missing_database | negative | nonzero | 1 | PASS | expected_fault_detected |
| 4 | N04_fk_enforced_after_restore | negative | nonzero | 1 | ERROR | environment_error |
| 5 | N05_restore_over_existing_objects | negative | nonzero | 1 | ERROR | version_mismatch |
| 6 | N06_tamper_detected | negative | nonzero | 1 | ERROR | version_mismatch |
| 7 | S00_required_tools | setup | zero | - | NOT_RUN | missing_test |
| 8 | S03_server_ready | setup | zero | - | NOT_RUN | missing_test |
| 9 | S04_client_server_major_match | setup | zero | - | NOT_RUN | missing_test |
| 10 | S05_reset_databases | setup | zero | - | NOT_RUN | missing_test |
| 11 | S06_create_source | setup | zero | - | NOT_RUN | missing_test |
| 12 | S07_seed_source | setup | zero | - | NOT_RUN | missing_test |
| 13 | S08_fingerprint_source | setup | zero | - | NOT_RUN | missing_test |
| 14 | S09_fingerprint_source_sanity | setup | zero | - | NOT_RUN | missing_test |
| 15 | P01_pg_dump_custom | positive | zero | - | NOT_RUN | missing_test |
| 16 | P02_pg_restore_list | positive | zero | - | NOT_RUN | missing_test |
| 17 | P03_createdb_target | positive | zero | - | NOT_RUN | missing_test |
| 18 | P04_pg_restore | positive | zero | - | NOT_RUN | missing_test |
| 19 | P05_fingerprint_restored | positive | zero | - | NOT_RUN | missing_test |
| 20 | P06_compare_restored | positive | zero | - | NOT_RUN | missing_test |
| 21 | P07_pg_dump_plain | positive | zero | - | NOT_RUN | missing_test |
| 22 | P08_createdb_plain | positive | zero | - | NOT_RUN | missing_test |
| 23 | P09_psql_restore_plain | positive | zero | - | NOT_RUN | missing_test |
| 24 | P10_fingerprint_plain | positive | zero | - | NOT_RUN | missing_test |
| 25 | P11_compare_plain | positive | zero | - | NOT_RUN | missing_test |
| 26 | S_N01_createdb | setup | zero | - | NOT_RUN | missing_test |
| 27 | S_N01_make_truncated_dump | setup | zero | - | NOT_RUN | missing_test |
| 28 | S_N02_make_garbage_file | setup | zero | - | NOT_RUN | missing_test |
| 29 | S_N03_assert_database_absent | setup | zero | - | NOT_RUN | missing_test |
| 30 | S_N04_precondition | setup | zero | - | NOT_RUN | missing_test |
| 31 | S_N05_createdb | setup | zero | - | NOT_RUN | missing_test |
| 32 | S_N05_first_restore | setup | zero | - | NOT_RUN | missing_test |
| 33 | S_N06_createdb | setup | zero | - | NOT_RUN | missing_test |
| 34 | S_N06_restore | setup | zero | - | NOT_RUN | missing_test |
| 35 | S_N06_tamper_row | setup | zero | - | NOT_RUN | missing_test |
| 36 | S_N06_fingerprint_tampered | setup | zero | - | NOT_RUN | missing_test |
