# M365 / endpoint operations -- offline evidence run `local-offline-20261028T181845Z`

> **OFFLINE / SYNTHETIC EVIDENCE. Generated from local JSON scenarios in this repository. No Microsoft 365, Entra ID, Intune or Exchange Online tenant, Microsoft Graph API or credential was used, no change was executed anywhere, and nothing here describes or claims the configuration or state of any tenant.**

| Field | Value |
|---|---|
| Mode | `offline-synthetic` |
| Tenant state claimed | `false` |
| Mutations executed | `0` |
| Validated commit | `8452788d69d91373a26d4963f4a8f8547163913a` |
| Branch | `m365-endpoint` |
| Scoped source tree clean at run | `true` |
| Started (UTC) | 2026-10-28T18:18:45Z |
| Finished (UTC) | 2026-10-28T18:18:45Z |
| Python | 3.13.5 |
| Overall | **PASS** |

## Commands

| # | Step | Expected exit | Exit | Result | Log |
|---|---|---|---|---|---|
| 1 | `python_version` | 0 | 0 | PASS | `logs/01_python_version.log` |
| 2 | `unit_tests` | 0 | 0 | PASS | `logs/02_unit_tests.log` |
| 3 | `evaluate_scenarios` | 0 | 0 | PASS | `logs/03_evaluate_scenarios.log` |
| 4 | `fixture_malformed_duplicate_key` | 2 | 2 | PASS | `logs/04_fixture_malformed_duplicate_key.log` |
| 5 | `fixture_malformed_execute_flag` | 2 | 2 | PASS | `logs/05_fixture_malformed_execute_flag.log` |
| 6 | `fixture_malformed_invalid_verdict` | 2 | 2 | PASS | `logs/06_fixture_malformed_invalid_verdict.log` |
| 7 | `fixture_malformed_real_domain` | 2 | 2 | PASS | `logs/07_fixture_malformed_real_domain.log` |
| 8 | `fixture_malformed_real_guid` | 2 | 2 | PASS | `logs/08_fixture_malformed_real_guid.log` |
| 9 | `fixture_malformed_truncated` | 2 | 2 | PASS | `logs/09_fixture_malformed_truncated.log` |
| 10 | `fixture_malformed_unknown_device` | 2 | 2 | PASS | `logs/10_fixture_malformed_unknown_device.log` |
| 11 | `fixture_malformed_unmapped_error_code` | 2 | 2 | PASS | `logs/11_fixture_malformed_unmapped_error_code.log` |
| 12 | `fixture_malformed_url` | 2 | 2 | PASS | `logs/12_fixture_malformed_url.log` |
| 13 | `fixture_mismatch_missing_device_findings` | 1 | 1 | PASS | `logs/13_fixture_mismatch_missing_device_findings.log` |
| 14 | `fixture_mismatch_no_approval` | 1 | 1 | PASS | `logs/14_fixture_mismatch_no_approval.log` |
| 15 | `fixture_mismatch_synced_cloud_disable` | 1 | 1 | PASS | `logs/15_fixture_mismatch_synced_cloud_disable.log` |

## Scenario results (identity/m365/scenarios)

| Scenario | Type | Verdict | Findings | Result |
|---|---|---|---|---|
| M365-ACC-001 | access-troubleshooting | ROOT_CAUSE_IDENTIFIED | CA-DEVICE-NOT-COMPLIANT, DEV-BITLOCKER, DEV-OS-MIN, SH-ADVISORY | PASS |
| M365-ACC-002 | access-troubleshooting | ROOT_CAUSE_IDENTIFIED | LIC-PREREQ, LIC-WORKLOAD-MISSING, SH-ADVISORY | PASS |
| M365-ACC-003 | access-troubleshooting | ROOT_CAUSE_IDENTIFIED | LIC-WORKLOAD-MISSING | PASS |
| M365-ACC-004 | access-troubleshooting | ROOT_CAUSE_IDENTIFIED | AUTH-MFA-REGISTRATION-REQUIRED | PASS |
| M365-BG-001 | break-glass-review | COMPLIANT_WITH_WARNINGS | BG-TEST-OVERDUE, PRIV-STANDING-GA | PASS |
| M365-BG-002 | break-glass-usage | POST_USE_COMPLETE | - | PASS |
| M365-OFF-001 | offboarding | APPROVED | - | PASS |
| M365-OFF-002 | offboarding | REJECTED | OFF-BYOD-WIPE, OFF-LICENSE-BEFORE-RETENTION, OFF-MISSING-STEP, OFF-REVOKE-BEFORE-DISABLE | PASS |
| M365-ONB-001 | onboarding | READY | ONB-MFA-TAP | PASS |
| M365-ONB-002 | onboarding | BLOCKED | LIC-USAGE-LOCATION-INHERITED, LIC-WORKLOAD-MISSING, ONB-MFA-TAP | PASS |
| M365-ONB-003 | onboarding | BLOCKED | LIC-NO-SEATS, ONB-MFA-TAP, ONB-PRIV-ROLE | PASS |
| M365-SH-001 | service-health | KNOWN_SERVICE_INCIDENT | LIC-WORKLOAD-MISSING, SH-KNOWN-INCIDENT | PASS |
| M365-SH-002 | service-health | LOCAL_ISSUE | DEV-STALE-CHECKIN, SH-LOCAL-ISSUE, SH-RESTORED-RECENTLY | PASS |

## Input hashes (SHA-256)

| Kind | Path | SHA-256 |
|---|---|---|
| evidence-generator | `evidence/m365/generate_evidence.py` | `c489f13e2ae2ab91832357fee747aa89ae004c7d6bea1e28e15cc2c9aa524860` |
| doc | `identity/m365/.gitignore` | `862263fa1f46c20f0d1e4dac5ffcc75abd55c08211b2c3864c5f8764b9d87793` |
| doc | `identity/m365/README.md` | `c74afcbb9c6cde9a7710622f80bb0a5dcc5ba2bb47d404e27952b05f66ba6656` |
| engine | `identity/m365/m365_ops.py` | `f9234e927da39c9bc76c1bcc84dd4197059cc225fd30a1975459271be56d273f` |
| doc | `identity/m365/runbooks/README.md` | `9641c8ae5d416a05133a9a468bac2b53b31b8a8313b9c7877a58f85132d3ed30` |
| scenario | `identity/m365/scenarios/M365-ACC-001-noncompliant-laptop.json` | `306c5fa416f0e520412f8f80ca4fdd2c5342e8b58c259663dd5adb1171ad2560` |
| scenario | `identity/m365/scenarios/M365-ACC-002-contractor-intune-license-dependency.json` | `1f242906899488375cde106130af32046127527997e50b34f71119f3d5b2245e` |
| scenario | `identity/m365/scenarios/M365-ACC-003-advisor-no-mailbox-plan.json` | `963af746e68f95b1c85bea5c0d33d93196e6ef1f4cc2369314a3130a320bd959` |
| scenario | `identity/m365/scenarios/M365-ACC-004-treasury-mfa-registration.json` | `97463d62c379df71bfb4a932d9be73211a8b3cb0390828b0fd16b12770ae2155` |
| scenario | `identity/m365/scenarios/M365-BG-001-quarterly-review.json` | `6603576dc019816c9de34f74c42262a12e12bd4ab84b7a46006d6ddd29d8b22c` |
| scenario | `identity/m365/scenarios/M365-BG-002-usage-during-mfa-outage.json` | `9e1607033beb63e7371b429921db1c737d78fddb04be19fcd6b6fb58326ab90c` |
| scenario | `identity/m365/scenarios/M365-OFF-001-involuntary-lender-legal-hold.json` | `4bb3f01695fcfc9962f4b0c447a6ee738b7468ad2037251bcd53d7e86fd2fba5` |
| scenario | `identity/m365/scenarios/M365-OFF-002-voluntary-leaver-bad-runbook.json` | `c881dfc671d26c349301c6bb16c0f97baec5ca75a354553af1507dc30e8f2aae` |
| scenario | `identity/m365/scenarios/M365-ONB-001-new-analyst-e3.json` | `4a298204f9a01f54405ac41416122e868bf19af7fcc8f6b57e0a43cc00574ab4` |
| scenario | `identity/m365/scenarios/M365-ONB-002-teller-f3-desktop-apps.json` | `2c063314c76894afee55bb668f958d4c98571d407a24a19395c94725841515f5` |
| scenario | `identity/m365/scenarios/M365-ONB-003-secops-e5-no-seats.json` | `022c97b05e15c0a4eaed01b8a120a09459945b8f7d775c17fc5578d959a96b67` |
| scenario | `identity/m365/scenarios/M365-SH-001-teams-known-incident.json` | `510aee158ad5a6f3e1897448121987e7dd3ebac3c8281300ed3cc0bcfc16ef1c` |
| scenario | `identity/m365/scenarios/M365-SH-002-exchange-after-restore.json` | `e464689556f3ffd7046ca497eed42e161a0b5d7025edb6b367eefbbef7690708` |
| tenant-fixture | `identity/m365/tenant/tenant.json` | `dc3ba5b0857d65b05f274bd9b50952ed759cb39aa76f1be2b51a63c9928e4a4c` |
| doc | `identity/m365/tests/README.md` | `aaded126f8e3a7cec5da1572c09d39e432321dfe6c30c9e0ffc20ee409aac3a9` |
| test-fixture | `identity/m365/tests/fixtures/malformed-duplicate-key.json` | `407a3ee798ec7b00ccca9dd6cce4ed1fecbf4611de1eae660e06b928142a7002` |
| test-fixture | `identity/m365/tests/fixtures/malformed-execute-flag.json` | `dedbf0ca5f0c9a77ceb0edc82853b2e7ba031ba038ab3e8a016a495fa06c5157` |
| test-fixture | `identity/m365/tests/fixtures/malformed-invalid-verdict.json` | `fb9ee097d5fbb96afd5ca1e68d8d0381c38cc1299cc191ab4bf708e0b4772c2c` |
| test-fixture | `identity/m365/tests/fixtures/malformed-real-domain.json` | `ae5de4ec28719f53f4b2eb45751443714c66690f512db6e2e98c24d2c7d4d82c` |
| test-fixture | `identity/m365/tests/fixtures/malformed-real-guid.json` | `b092f911dbaea3dae21ba3aacb1227963e919877eb66c6be014db4a5e9386c1d` |
| test-fixture | `identity/m365/tests/fixtures/malformed-truncated.json` | `8f6ae4b9bcdeee429aa0d55db732a4848c58fe59d27ca6c541a4bad56e62dd75` |
| test-fixture | `identity/m365/tests/fixtures/malformed-unknown-device.json` | `b10465788cdbd70ba37fdb1d5365cf2c76f80bcbcdfc10d34c2978430de77cad` |
| test-fixture | `identity/m365/tests/fixtures/malformed-unmapped-error-code.json` | `200d5c417a3dc7300dda34f8ad4ee123820aa2ab77c75531f569ff232fa1d793` |
| test-fixture | `identity/m365/tests/fixtures/malformed-url.json` | `375a3795328a564dbb04494b2172f03e1f66064855608800275e9253bca28fa7` |
| test-fixture | `identity/m365/tests/fixtures/mismatch-missing-device-findings.json` | `79639254d6b9bfb11b8bb711eecc92e16fb3854803c83a05fa55ee70f3c17d78` |
| test-fixture | `identity/m365/tests/fixtures/mismatch-no-approval.json` | `29f8c66ace678cff1739bdb565c924521412138a930502fef4121a2942711171` |
| test-fixture | `identity/m365/tests/fixtures/mismatch-synced-cloud-disable.json` | `e512aabbede0f975356e7ba49c1197276f84b0738a8d1bedcbb2df630ae23cd4` |
| engine | `identity/m365/tests/test_m365_ops.py` | `1b81461d7e851a06b0bac56f1cd1f557590460fddd5d156a09d6dfa3e8552832` |

Verify: `python3 evidence/m365/generate_evidence.py --verify evidence/m365/runs/local-offline-20261028T181845Z`
