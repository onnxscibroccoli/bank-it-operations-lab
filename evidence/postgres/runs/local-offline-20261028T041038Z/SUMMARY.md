# Postgres restore exercise: local-offline-20261028T041038Z

Mode: `offline`. Overall: **PASS** (30 passed, 0 failed, 30 steps).

| # | step | kind | expected | exit | result |
|---|------|------|----------|------|--------|
| 1 | offline_initdb | setup | zero | 0 | PASS |
| 2 | offline_start | setup | zero | 0 | PASS |
| 3 | server_ready | setup | zero | 0 | PASS |
| 4 | server_version | setup | zero | 0 | PASS |
| 5 | reset_lab_source | setup | zero | 0 | PASS |
| 6 | reset_lab_restore_ok | setup | zero | 0 | PASS |
| 7 | reset_lab_restore_plain | setup | zero | 0 | PASS |
| 8 | reset_lab_restore_trunc | setup | zero | 0 | PASS |
| 9 | reset_lab_restore_dup | setup | zero | 0 | PASS |
| 10 | reset_lab_restore_tamper | setup | zero | 0 | PASS |
| 11 | create_source | setup | zero | 0 | PASS |
| 12 | seed_source | setup | zero | 0 | PASS |
| 13 | fingerprint_source | setup | zero | 0 | PASS |
| 14 | P01_pg_dump_custom | positive | zero | 0 | PASS |
| 15 | P02_pg_restore_list | positive | zero | 0 | PASS |
| 16 | P03_createdb_target | positive | zero | 0 | PASS |
| 17 | P04_pg_restore | positive | zero | 0 | PASS |
| 18 | P05_fingerprint_restored | positive | zero | 0 | PASS |
| 19 | P06_compare_restored | positive | zero | 0 | PASS |
| 20 | P07_pg_dump_plain | positive | zero | 0 | PASS |
| 21 | P08_createdb_plain | positive | zero | 0 | PASS |
| 22 | P09_psql_restore_plain | positive | zero | 0 | PASS |
| 23 | P10_fingerprint_plain | positive | zero | 0 | PASS |
| 24 | P11_compare_plain | positive | zero | 0 | PASS |
| 25 | N01_restore_truncated_dump | negative | nonzero | 1 | PASS |
| 26 | N02_list_garbage_archive | negative | nonzero | 1 | PASS |
| 27 | N03_restore_missing_database | negative | nonzero | 1 | PASS |
| 28 | N04_fk_enforced_after_restore | negative | nonzero | 1 | PASS |
| 29 | N05_restore_over_existing_objects | negative | nonzero | 1 | PASS |
| 30 | N06_tamper_detected | negative | nonzero | 1 | PASS |
