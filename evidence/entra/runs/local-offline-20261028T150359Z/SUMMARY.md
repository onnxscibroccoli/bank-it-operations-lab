# Entra Conditional Access -- offline evidence run `local-offline-20261028T150359Z`

> **OFFLINE / SYNTHETIC EVIDENCE. Generated from local JSON fixtures in this repository. No Microsoft Entra ID tenant, Microsoft Graph API or credential was used. Nothing here describes or claims the configuration or state of any tenant.**

| Field | Value |
|---|---|
| Mode | `offline-synthetic` |
| Tenant state claimed | `false` |
| Validated commit | `e8771c9aa09b3e1c60d87b04cd65a266b673eed8` |
| Branch | `entra-ca-offline` |
| Scoped source tree clean at run | `true` |
| Started (UTC) | 2026-10-28T15:03:59Z |
| Finished (UTC) | 2026-10-28T15:04:00Z |
| Python | 3.13.5 |
| Overall | **PASS** |

## Commands

| # | Step | Expected exit | Exit | Result | Log |
|---|---|---|---|---|---|
| 1 | `python_version` | 0 | 0 | PASS | `logs/01_python_version.log` |
| 2 | `fixtures_drift_check` | 0 | 0 | PASS | `logs/02_fixtures_drift_check.log` |
| 3 | `unit_tests` | 0 | 0 | PASS | `logs/03_unit_tests.log` |
| 4 | `validate_baseline_policies` | 0 | 0 | PASS | `logs/04_validate_baseline_policies.log` |
| 5 | `fixture_malformed_bad_guid` | 2 | 2 | PASS | `logs/05_fixture_malformed_bad_guid.log` |
| 6 | `fixture_malformed_bad_operator` | 2 | 2 | PASS | `logs/06_fixture_malformed_bad_operator.log` |
| 7 | `fixture_malformed_bad_risk_level` | 2 | 2 | PASS | `logs/07_fixture_malformed_bad_risk_level.log` |
| 8 | `fixture_malformed_block_combined` | 2 | 2 | PASS | `logs/08_fixture_malformed_block_combined.log` |
| 9 | `fixture_malformed_duplicate_id` | 2 | 2 | PASS | `logs/09_fixture_malformed_duplicate_id.log` |
| 10 | `fixture_malformed_duplicate_key` | 2 | 2 | PASS | `logs/10_fixture_malformed_duplicate_key.log` |
| 11 | `fixture_malformed_empty_grant` | 2 | 2 | PASS | `logs/11_fixture_malformed_empty_grant.log` |
| 12 | `fixture_malformed_empty_set` | 2 | 2 | PASS | `logs/12_fixture_malformed_empty_set.log` |
| 13 | `fixture_malformed_invalid_state` | 2 | 2 | PASS | `logs/13_fixture_malformed_invalid_state.log` |
| 14 | `fixture_malformed_missing_state` | 2 | 2 | PASS | `logs/14_fixture_malformed_missing_state.log` |
| 15 | `fixture_malformed_nan` | 2 | 2 | PASS | `logs/15_fixture_malformed_nan.log` |
| 16 | `fixture_malformed_no_users_target` | 2 | 2 | PASS | `logs/16_fixture_malformed_no_users_target.log` |
| 17 | `fixture_malformed_not_object` | 2 | 2 | PASS | `logs/17_fixture_malformed_not_object.log` |
| 18 | `fixture_malformed_truncated` | 2 | 2 | PASS | `logs/18_fixture_malformed_truncated.log` |
| 19 | `fixture_malformed_unknown_client_app` | 2 | 2 | PASS | `logs/19_fixture_malformed_unknown_client_app.log` |
| 20 | `fixture_malformed_unknown_condition` | 2 | 2 | PASS | `logs/20_fixture_malformed_unknown_condition.log` |
| 21 | `fixture_malformed_unknown_control` | 2 | 2 | PASS | `logs/21_fixture_malformed_unknown_control.log` |
| 22 | `fixture_malformed_unknown_top_key` | 2 | 2 | PASS | `logs/22_fixture_malformed_unknown_top_key.log` |
| 23 | `fixture_malformed_wrong_type` | 2 | 2 | PASS | `logs/23_fixture_malformed_wrong_type.log` |
| 24 | `fixture_neg_admin_role_excluded` | 1 | 1 | PASS | `logs/24_fixture_neg_admin_role_excluded.log` |
| 25 | `fixture_neg_admin_role_missing` | 1 | 1 | PASS | `logs/25_fixture_neg_admin_role_missing.log` |
| 26 | `fixture_neg_admin_weak_strength` | 1 | 1 | PASS | `logs/26_fixture_neg_admin_weak_strength.log` |
| 27 | `fixture_neg_break_glass_included` | 1 | 1 | PASS | `logs/27_fixture_neg_break_glass_included.log` |
| 28 | `fixture_neg_break_glass_not_excluded` | 1 | 1 | PASS | `logs/28_fixture_neg_break_glass_not_excluded.log` |
| 29 | `fixture_neg_device_disabled` | 1 | 1 | PASS | `logs/29_fixture_neg_device_disabled.log` |
| 30 | `fixture_neg_device_or_bypass` | 1 | 1 | PASS | `logs/30_fixture_neg_device_or_bypass.log` |
| 31 | `fixture_neg_legacy_auth_not_blocked` | 1 | 1 | PASS | `logs/31_fixture_neg_legacy_auth_not_blocked.log` |
| 32 | `fixture_neg_legacy_auth_partial` | 1 | 1 | PASS | `logs/32_fixture_neg_legacy_auth_partial.log` |
| 33 | `fixture_neg_mfa_extra_exclusion` | 1 | 1 | PASS | `logs/33_fixture_neg_mfa_extra_exclusion.log` |
| 34 | `fixture_neg_mfa_or_bypass` | 1 | 1 | PASS | `logs/34_fixture_neg_mfa_or_bypass.log` |
| 35 | `fixture_neg_mfa_policy_removed` | 1 | 1 | PASS | `logs/35_fixture_neg_mfa_policy_removed.log` |
| 36 | `fixture_neg_mfa_report_only` | 1 | 1 | PASS | `logs/36_fixture_neg_mfa_report_only.log` |
| 37 | `fixture_neg_missing_compliant_device` | 1 | 1 | PASS | `logs/37_fixture_neg_missing_compliant_device.log` |
| 38 | `fixture_neg_missing_mfa` | 1 | 1 | PASS | `logs/38_fixture_neg_missing_mfa.log` |
| 39 | `fixture_neg_risk_enforced` | 1 | 1 | PASS | `logs/39_fixture_neg_risk_enforced.log` |
| 40 | `fixture_neg_unscoped_block` | 1 | 1 | PASS | `logs/40_fixture_neg_unscoped_block.log` |
| 41 | `fixture_valid_graph_envelope` | 0 | 0 | PASS | `logs/41_fixture_valid_graph_envelope.log` |

## Baseline validation (identity/entra/policies)

| Rule | Category | Result | Title |
|---|---|---|---|
| SCHEMA-001 | schema | PASS | Every input file parses as JSON (no duplicate keys) and the policy set is non-empty |
| SCHEMA-002 | schema | PASS | Each policy has the conditionalAccessPolicy shape: required keys present, no unknown keys, correct types |
| SCHEMA-003 | schema | PASS | state is one of enabled \| disabled \| enabledForReportingButNotEnforced |
| SCHEMA-004 | schema | PASS | conditions (users, applications, clientAppTypes, platforms, locations, risk levels) are well-formed with known values |
| SCHEMA-005 | schema | PASS | grantControls well-formed: operator AND\|OR, known builtInControls, block is exclusive, at least one control |
| SCHEMA-006 | schema | PASS | Policy ids and displayNames are unique across the set |
| BASE-001 | baseline | PASS | Break-glass accounts are excluded from every policy (and never explicitly included) |
| BASE-002 | baseline | PASS | Legacy authentication (exchangeActiveSync + other) is blocked for All users on All apps by an enabled policy |
| BASE-003 | baseline | PASS | An enabled policy requires MFA for All users on All apps (AND semantics, only break-glass excluded) |
| BASE-004 | baseline | PASS | All privileged admin roles require phishing-resistant MFA via an enabled policy with no role exclusions |
| BASE-005 | baseline | PASS | No policy blocks All users without exclusions |
| BASE-006 | baseline | PASS | An enabled policy requires a compliant device for All users on All apps |
| BASE-007 | baseline | PASS | Risk-based policies (sign-in / user risk) are report-only during staged rollout |

## Input hashes (SHA-256)

| Kind | Path | SHA-256 |
|---|---|---|
| evidence-generator | `evidence/entra/generate_evidence.py` | `ada9ce36d4cd3a02eb914df08fa2b57b5d4008c0efa5e466b0a5bd6c0b10e965` |
| doc | `identity/entra/.gitignore` | `862263fa1f46c20f0d1e4dac5ffcc75abd55c08211b2c3864c5f8764b9d87793` |
| doc | `identity/entra/README.md` | `a1d775f9d874b3318175cf09cb19f22b128fe56b0d1086870ad282941fa57992` |
| validator | `identity/entra/baseline.json` | `f5566caf556175ecbc0cb8d0dfbf434f6095c37fd5012476e2ac0143c2f82cbc` |
| validator | `identity/entra/ca_validator.py` | `313dcbc7d31717b7060334d19f31c74f7065718b1f725fe9dce3c0a0ad38a01e` |
| policy-fixture | `identity/entra/policies/CA001-Block-Legacy-Authentication-All-Users.json` | `4f91671c3fb2e07dd286f74dd5e3d8baf789a59d1bf7d04b75b1eecec4100fd1` |
| policy-fixture | `identity/entra/policies/CA002-Require-MFA-All-Users.json` | `e888511acb339629e94d264499652873f58981d07604b48c59c5bc2fac560da0` |
| policy-fixture | `identity/entra/policies/CA003-Require-Phishing-Resistant-MFA-Admin-Roles.json` | `2e76720ba8b66177c4a4973a6c6488afbffd6de2dbcdb824a1e1b4d36a8a4555` |
| policy-fixture | `identity/entra/policies/CA004-Require-Compliant-Device-All-Users.json` | `7fd7710a4109c83d27441c6a0c3300876d3d0dc70ba5ec0dd18bcf008ddef877` |
| policy-fixture | `identity/entra/policies/CA005-Block-High-Sign-In-Risk-ReportOnly.json` | `a9c030d967b905d9f84e89f173b06b804e4ccf96d556f15e137dbee9eabb2ebd` |
| policy-fixture | `identity/entra/policies/CA006-High-User-Risk-Require-Password-Change-ReportOnly.json` | `2d551d9f6d4756c8b891ed4b7360b362de689c19abf5ae185e6911a43f55db87` |
| policy-fixture | `identity/entra/policies/CA007-Block-Admin-Portals-From-Untrusted-Locations.json` | `43e8d8d341b4a7fbe09e0fe7614dc440d92ab0235553523034977a441303d970` |
| doc | `tests/entra/.gitignore` | `862263fa1f46c20f0d1e4dac5ffcc75abd55c08211b2c3864c5f8764b9d87793` |
| doc | `tests/entra/README.md` | `469c6173909b3f40302639cdfa8edc332a155c32e937e5758100b19649600543` |
| test-fixture | `tests/entra/fixtures/INDEX.json` | `cb30cbd8949a2445056950969606a0d459fb3a59e5a82fa77d94bc4ab0ed0e56` |
| test-fixture | `tests/entra/fixtures/malformed-bad-guid.json` | `59a1deef1bd1bfb57147efc3d340e52ee5b42a159617f25f83d8f529f6729ff1` |
| test-fixture | `tests/entra/fixtures/malformed-bad-operator.json` | `9a4e30c9244b00e90d3608c2405335208d8c3acf60c082a659016ced4f4b781b` |
| test-fixture | `tests/entra/fixtures/malformed-bad-risk-level.json` | `c417748a8c4cd851a22e1ec32fdd398b5babb91f3313ebdc3df28585523cdff9` |
| test-fixture | `tests/entra/fixtures/malformed-block-combined.json` | `dec5165bc1698bb7eada15f0b84519e1cdf78bc4a3b85df70f1688969e0f1dc6` |
| test-fixture | `tests/entra/fixtures/malformed-duplicate-id.json` | `3b64688e50b9a38c22a8d256f5fb5583a30f3225d556de3867d6b5e19344a9ab` |
| test-fixture | `tests/entra/fixtures/malformed-duplicate-key.json` | `a09aa98f171ed18233fead930de8db334257c69abc81278345ea215f0e422f51` |
| test-fixture | `tests/entra/fixtures/malformed-empty-grant.json` | `664c6fbebf0efe0d929e97c552802afd2aefa91ff125702f804615ee0f32f12e` |
| test-fixture | `tests/entra/fixtures/malformed-empty-set.json` | `ba6b28ef7d9e13314d4d21bc8fe249beb4f59c92238972d2921789389a2e0d31` |
| test-fixture | `tests/entra/fixtures/malformed-invalid-state.json` | `5a705cda26376404e47c511fb3204f8e7beb133d995f4b5e6b484d994514511b` |
| test-fixture | `tests/entra/fixtures/malformed-missing-state.json` | `26b079333f7c16fc73529317c8f9496bbb29985f8d11c2e50ceefec554ac6a87` |
| test-fixture | `tests/entra/fixtures/malformed-nan.json` | `618401c15240c927e85ffd5f7877b364e88ec1338f9b7686fbea41308ec6882a` |
| test-fixture | `tests/entra/fixtures/malformed-no-users-target.json` | `3f67083aaea4b2b6fe5e1026c09f568aa4a396c51939cdc35c13bf04736de184` |
| test-fixture | `tests/entra/fixtures/malformed-not-object.json` | `b8f781472faad99e1ad27e72709eee89c50597f845cf4b331cd8285fb5b517ba` |
| test-fixture | `tests/entra/fixtures/malformed-truncated.json` | `dcabd2785c492311963543049eedfde307f397abfd68fb26f7f2912e14d3099c` |
| test-fixture | `tests/entra/fixtures/malformed-unknown-client-app.json` | `0ba66299b85a085d06bea5e77a7e222f9b05f0dc4ab4745424c32fc8b32a2ec4` |
| test-fixture | `tests/entra/fixtures/malformed-unknown-condition.json` | `33c8bdd644a5bf9ae9555722c10198dc2d083331511158fa0ebf2bf0aefbf5d6` |
| test-fixture | `tests/entra/fixtures/malformed-unknown-control.json` | `ba8e268a66545dee188a95e6dc0b6955a121e6b06f4be5f79b63b1d1abb00d33` |
| test-fixture | `tests/entra/fixtures/malformed-unknown-top-key.json` | `c9edecb2a9745873c8c9acf9adc863a2bf6e3af9b798a3533e4de07e4ce36f1a` |
| test-fixture | `tests/entra/fixtures/malformed-wrong-type.json` | `1a2881c7407c0d3880b2f95227a6fd253da821ace37ac42bcf3c9be3d41a3d9b` |
| test-fixture | `tests/entra/fixtures/neg-admin-role-excluded.json` | `ca15ef61fdbba874d1ba0dd130a2a0ef14d4f4f3a534fda7c5532a659bf81653` |
| test-fixture | `tests/entra/fixtures/neg-admin-role-missing.json` | `d68c02b71fb8fca9e08bc693d873968f3e454d7a276ae3b0ea11ee25bd5bda39` |
| test-fixture | `tests/entra/fixtures/neg-admin-weak-strength.json` | `3be04de9c6670d83bb83ac857c02d155008e1267f6f1c88fd7c95582da054c70` |
| test-fixture | `tests/entra/fixtures/neg-break-glass-included.json` | `dabb8db5fd7a18cee8e00a96bd9891e3f892c1fc42abcd0fbff491a7ee29fb28` |
| test-fixture | `tests/entra/fixtures/neg-break-glass-not-excluded.json` | `c9b5fe093fd9fc3e86bd174d355cc6be60534064884326beac1a5c66cbd612cd` |
| test-fixture | `tests/entra/fixtures/neg-device-disabled.json` | `5cccf6bf85dacfad26b623676a8a7e0efe7e97165cc1211bad9048463e0f4e4d` |
| test-fixture | `tests/entra/fixtures/neg-device-or-bypass.json` | `2b008ee0142452a483d98c727353f447355ec94c291e0a930d4771ea3d1d791c` |
| test-fixture | `tests/entra/fixtures/neg-legacy-auth-not-blocked.json` | `9b76f563fb639930c4067362f3508d370d1145904256dff77a643b2842f3e473` |
| test-fixture | `tests/entra/fixtures/neg-legacy-auth-partial.json` | `9544430ab3d241f681541d1d6609064a43a1ff4f4bd96539663af78f8da51dbf` |
| test-fixture | `tests/entra/fixtures/neg-mfa-extra-exclusion.json` | `518d09e5c7f428f4bd9f2667a5fbfd333300d3646e02bf7e4333d9f5d663d962` |
| test-fixture | `tests/entra/fixtures/neg-mfa-or-bypass.json` | `33ae69aa0913eb0baa89808859f4c14255762a92b0cf0e78830c7f7554d9c9a9` |
| test-fixture | `tests/entra/fixtures/neg-mfa-policy-removed.json` | `52517d2296b1a0bae9d71e6d808a105b97ccc0b2122424f1e2fa4963b4e1158d` |
| test-fixture | `tests/entra/fixtures/neg-mfa-report-only.json` | `0a685d5a2110a0649d91afa2da047a2926e464df3537e618e0ad3fc578a64738` |
| test-fixture | `tests/entra/fixtures/neg-missing-compliant-device.json` | `761ebd8aa590546805af7e3746073fb1d81a27022b06694d66e32ebd2cd3f600` |
| test-fixture | `tests/entra/fixtures/neg-missing-mfa.json` | `0e74d6e980796e3d12ed52866068a32c677e1a861431d22b6063feb60547d17d` |
| test-fixture | `tests/entra/fixtures/neg-risk-enforced.json` | `70d9c37c41fcec405baa2022950c035f9075d4bcc1b14f163fc169a829bde541` |
| test-fixture | `tests/entra/fixtures/neg-unscoped-block.json` | `032933c16468be1873d0ee501da12306ea676ec196892fcd43d9e68f63dfdbcb` |
| test-fixture | `tests/entra/fixtures/valid-graph-envelope.json` | `efd066a8cd6f8d781e5515697fa2c7039cc911c6f86e43c8c0d4167b6778bc62` |
| test | `tests/entra/make_fixtures.py` | `6cdc3369089776e48de1adf004137e2d4096fac6307d810b1e651e53557a1de5` |
| validator | `tests/entra/test_ca_validator.py` | `69ceca7f003e0e6b08eead10f4b6ef8aac55be5d8ff4a09c4cb217fcc07ed472` |

Verify: `python3 evidence/entra/generate_evidence.py --verify evidence/entra/runs/local-offline-20261028T150359Z`
