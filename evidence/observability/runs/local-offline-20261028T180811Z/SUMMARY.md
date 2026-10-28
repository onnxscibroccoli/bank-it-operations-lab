# Observability evidence: local-offline-20261028T180811Z

Offline/local only. No network, no cloud calls, no production endpoint or routing changes.

- commit: `728371223c5f095b69b304c2a845b7200b5adf50` (branch `observability`)
- started: 2026-10-28T18:08:11Z, fixed evaluation clock: 2026-10-28T12:01:00Z
- overall: **PASS**

| fixture | overall | exit | HTTP | failed checks | matches expected |
|---|---|---|---|---|---|
| healthy.json | HEALTHY | 0 | 200 | - | yes |
| host-metric-missing.json | UNHEALTHY | 1 | 503 | host:collection_errors, host:metrics_present | yes |
| malformed-bad-status.json | UNHEALTHY | 2 | 503 | payload:valid | yes |
| malformed-duplicate-key.json | UNHEALTHY | 2 | 503 | payload:valid | yes |
| malformed-nan.json | UNHEALTHY | 2 | 503 | payload:valid | yes |
| malformed-truncated.json | UNHEALTHY | 2 | 503 | payload:valid | yes |
| malformed-unknown-key.json | UNHEALTHY | 2 | 503 | payload:valid | yes |
| malformed-wrong-type.json | UNHEALTHY | 2 | 503 | payload:valid | yes |
| missing-probe.json | UNHEALTHY | 1 | 503 | probe:resolver-dns | yes |
| stale.json | UNHEALTHY | 1 | 503 | freshness:host, freshness:payload, freshness:probe:app-http, freshness:probe:db-tcp, freshness:probe:resolver-dns | yes |
| timeout.json | UNHEALTHY | 1 | 503 | probe:db-tcp | yes |
| unhealthy.json | UNHEALTHY | 1 | 503 | host:disk_free_ratio, probe:app-http | yes |
| unknown-status.json | UNHEALTHY | 1 | 503 | probe:resolver-dns | yes |

| # | step | expected | exit | result |
|---|---|---|---|---|
| 1 | python_version | 0 | 0 | PASS |
| 2 | unit_tests | 0 | 0 | PASS |
| 3 | fixture_healthy | 0 | 0 | PASS |
| 4 | fixture_host_metric_missing | 1 | 1 | PASS |
| 5 | fixture_malformed_bad_status | 2 | 2 | PASS |
| 6 | fixture_malformed_duplicate_key | 2 | 2 | PASS |
| 7 | fixture_malformed_nan | 2 | 2 | PASS |
| 8 | fixture_malformed_truncated | 2 | 2 | PASS |
| 9 | fixture_malformed_unknown_key | 2 | 2 | PASS |
| 10 | fixture_malformed_wrong_type | 2 | 2 | PASS |
| 11 | fixture_missing_probe | 1 | 1 | PASS |
| 12 | fixture_stale | 1 | 1 | PASS |
| 13 | fixture_timeout | 1 | 1 | PASS |
| 14 | fixture_unhealthy | 1 | 1 | PASS |
| 15 | fixture_unknown_status | 1 | 1 | PASS |
