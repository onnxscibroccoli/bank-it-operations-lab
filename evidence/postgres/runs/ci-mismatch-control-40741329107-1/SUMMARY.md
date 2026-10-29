# ci-mismatch-control-40741329107-1

Status: CURRENT (harness v2). Mode: `service`. Overall: **FAIL**
(2/36 passed; 0 failed, 1 errors, 33 not run).

| # | step | kind | expected | exit | result | class |
|---|------|------|----------|------|--------|-------|
| 1 | S00_required_tools | setup | zero | 0 | PASS | setup_ok |
| 2 | S03_server_ready | setup | zero | 0 | PASS | setup_ok |
| 3 | S04_client_server_major_match | setup | zero | 1 | ERROR | version_mismatch |
| 4 | S05_reset_databases | setup | zero | - | NOT_RUN | dependency_failed:S04_client_server_major_match |
| 5 | S06_create_source | setup | zero | - | NOT_RUN | dependency_failed:S05_reset_databases |
| 6 | S07_seed_source | setup | zero | - | NOT_RUN | dependency_failed:S06_create_source |
| 7 | S08_fingerprint_source | setup | zero | - | NOT_RUN | dependency_failed:S07_seed_source |
| 8 | S09_fingerprint_source_sanity | setup | zero | - | NOT_RUN | dependency_failed:S08_fingerprint_source |
| 9 | P01_pg_dump_custom | positive | zero | - | NOT_RUN | dependency_failed:S09_fingerprint_source_sanity |
| 10 | P02_pg_restore_list | positive | zero | - | NOT_RUN | dependency_failed:P01_pg_dump_custom |
| 11 | P03_createdb_target | positive | zero | - | NOT_RUN | dependency_failed:S09_fingerprint_source_sanity |
| 12 | P04_pg_restore | positive | zero | - | NOT_RUN | dependency_failed:P01_pg_dump_custom |
| 13 | P05_fingerprint_restored | positive | zero | - | NOT_RUN | dependency_failed:P04_pg_restore |
| 14 | P06_compare_restored | positive | zero | - | NOT_RUN | dependency_failed:P05_fingerprint_restored |
| 15 | P07_pg_dump_plain | positive | zero | - | NOT_RUN | dependency_failed:S09_fingerprint_source_sanity |
| 16 | P08_createdb_plain | positive | zero | - | NOT_RUN | dependency_failed:S09_fingerprint_source_sanity |
| 17 | P09_psql_restore_plain | positive | zero | - | NOT_RUN | dependency_failed:P07_pg_dump_plain |
| 18 | P10_fingerprint_plain | positive | zero | - | NOT_RUN | dependency_failed:P09_psql_restore_plain |
| 19 | P11_compare_plain | positive | zero | - | NOT_RUN | dependency_failed:P10_fingerprint_plain |
| 20 | S_N01_createdb | setup | zero | - | NOT_RUN | dependency_failed:S09_fingerprint_source_sanity |
| 21 | S_N01_make_truncated_dump | setup | zero | - | NOT_RUN | dependency_failed:P01_pg_dump_custom |
| 22 | N01_restore_truncated_dump | negative | nonzero | - | NOT_RUN | dependency_failed:S_N01_createdb |
| 23 | S_N02_make_garbage_file | setup | zero | - | NOT_RUN | dependency_failed:S04_client_server_major_match |
| 24 | N02_list_garbage_archive | negative | nonzero | - | NOT_RUN | dependency_failed:S_N02_make_garbage_file |
| 25 | S_N03_assert_database_absent | setup | zero | - | NOT_RUN | dependency_failed:S04_client_server_major_match |
| 26 | N03_restore_missing_database | negative | nonzero | - | NOT_RUN | dependency_failed:S_N03_assert_database_absent |
| 27 | S_N04_precondition | setup | zero | - | NOT_RUN | dependency_failed:P06_compare_restored |
| 28 | N04_fk_enforced_after_restore | negative | nonzero | - | NOT_RUN | dependency_failed:S_N04_precondition |
| 29 | S_N05_createdb | setup | zero | - | NOT_RUN | dependency_failed:S09_fingerprint_source_sanity |
| 30 | S_N05_first_restore | setup | zero | - | NOT_RUN | dependency_failed:S_N05_createdb |
| 31 | N05_restore_over_existing_objects | negative | nonzero | - | NOT_RUN | dependency_failed:S_N05_first_restore |
| 32 | S_N06_createdb | setup | zero | - | NOT_RUN | dependency_failed:S09_fingerprint_source_sanity |
| 33 | S_N06_restore | setup | zero | - | NOT_RUN | dependency_failed:S_N06_createdb |
| 34 | S_N06_tamper_row | setup | zero | - | NOT_RUN | dependency_failed:S_N06_restore |
| 35 | S_N06_fingerprint_tampered | setup | zero | - | NOT_RUN | dependency_failed:S_N06_tamper_row |
| 36 | N06_tamper_detected | negative | nonzero | - | NOT_RUN | dependency_failed:S_N06_fingerprint_tampered |
