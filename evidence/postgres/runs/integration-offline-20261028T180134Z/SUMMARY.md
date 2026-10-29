# Postgres restore exercise: integration-offline-20261028T180134Z

Mode: `offline`. Overall: **PASS** (39 passed, 0 failed, 39 steps).

| # | step | kind | expected | exit | result |
|---|------|------|----------|------|--------|
| 1 | offline_initdb | setup | zero | 0 | PASS |
| 2 | offline_start | setup | zero | 0 | PASS |
| 3 | server_ready | setup | zero | 0 | PASS |
| 4 | server_version | setup | zero | 0 | PASS |
| 5 | client_server_major_match | setup | zero | 0 | PASS |
| 6 | reset_lab_source | setup | zero | 0 | PASS |
| 7 | reset_lab_restore_ok | setup | zero | 0 | PASS |
| 8 | reset_lab_restore_plain | setup | zero | 0 | PASS |
| 9 | reset_lab_restore_trunc | setup | zero | 0 | PASS |
| 10 | reset_lab_restore_dup | setup | zero | 0 | PASS |
| 11 | reset_lab_restore_tamper | setup | zero | 0 | PASS |
| 12 | create_source | setup | zero | 0 | PASS |
| 13 | seed_source | setup | zero | 0 | PASS |
| 14 | fingerprint_source | setup | zero | 0 | PASS |
| 15 | P01_pg_dump_custom | positive | zero | 0 | PASS |
| 16 | P02_pg_restore_list | positive | zero | 0 | PASS |
| 17 | P03_createdb_target | positive | zero | 0 | PASS |
| 18 | P04_pg_restore | positive | zero | 0 | PASS |
| 19 | P05_fingerprint_restored | positive | zero | 0 | PASS |
| 20 | P06_compare_restored | positive | zero | 0 | PASS |
| 21 | P07_pg_dump_plain | positive | zero | 0 | PASS |
| 22 | P08_createdb_plain | positive | zero | 0 | PASS |
| 23 | P09_psql_restore_plain | positive | zero | 0 | PASS |
| 24 | P10_fingerprint_plain | positive | zero | 0 | PASS |
| 25 | P11_compare_plain | positive | zero | 0 | PASS |
| 26 | N01_setup_createdb | setup | zero | 0 | PASS |
| 27 | N01_restore_truncated_dump | negative | nonzero | 1 | PASS |
| 28 | N02_list_garbage_archive | negative | nonzero | 1 | PASS |
| 29 | N03_restore_missing_database | negative | nonzero | 1 | PASS |
| 30 | N04_setup_table_present | setup | zero | 0 | PASS |
| 31 | N04_fk_enforced_after_restore | negative | nonzero | 1 | PASS |
| 32 | N05_setup_createdb | setup | zero | 0 | PASS |
| 33 | N05_setup_first_restore | setup | zero | 0 | PASS |
| 34 | N05_restore_over_existing_objects | negative | nonzero | 1 | PASS |
| 35 | N06_setup_createdb | setup | zero | 0 | PASS |
| 36 | N06_setup_restore | setup | zero | 0 | PASS |
| 37 | N06_setup_tamper | setup | zero | 0 | PASS |
| 38 | N06_setup_fingerprint | setup | zero | 0 | PASS |
| 39 | N06_tamper_detected | negative | nonzero | 1 | PASS |
