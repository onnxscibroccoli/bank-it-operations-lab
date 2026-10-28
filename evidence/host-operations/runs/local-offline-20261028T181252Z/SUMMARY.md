# Host operations -- offline evidence run `local-offline-20261028T181252Z`

> **OFFLINE EVIDENCE. Generated from files in this repository only. No AWS API was called, no host was patched, and no systemd unit was installed, reloaded or started. Example data is marked EXAMPLE DATA. Nothing here describes the state of any account or host.**

| Field | Value |
|---|---|
| Validated commit | `d86a9dd11b153158da9aa7a0eb559bc73a90758b` |
| Branch | `patch-hardening` |
| Scoped tree clean at run | `true` |
| Started (UTC) | 2026-10-28T18:12:52Z |
| Finished (UTC) | 2026-10-28T18:12:57Z |
| AWS calls made | `false` |
| Hosts modified | `false` |
| Steps | 99 PASS / 0 FAIL / 0 SKIPPED |
| Overall | **PASS** |

## Tool versions

- `cfn-lint`: cfn-lint 1.58.0
- `python`: 3.13.5
- `shellcheck`: version: 0.11.0
- `systemd-analyze`: systemd 257 (257.13-1~deb13u1)
- `yamllint`: yamllint 1.38.0

## Exposure: score_units.py vs systemd-analyze security --offline

| Layer | score_units.py | systemd-analyze | systemd rating |
|---|---|---|---|
| root_agent | 9.6 | 9.6 | UNSAFE |
| app_unhardened | 8.8 | 9.2 | UNSAFE |
| app_baseline | 4.8 | 6.8 | MEDIUM |
| app_strict | 0.6 | 1.3 | OK |

Both are offline estimates on staged copies (systemd-analyze in `--user` mode); the ordering is what matters. Run `systemd-analyze security` on the real host as the authority.

## Commands

| # | Step | Kind | Expected | Exit | Result | Log |
|---|---|---|---|---|---|---|
| 1 | `python_version` | env | 0 | 0 | PASS | `logs/01_python_version.log` |
| 2 | `patching_fixture_drift` | drift | 0 | 0 | PASS | `logs/02_patching_fixture_drift.log` |
| 3 | `patching_unit_tests` | test | 0 | 0 | PASS | `logs/03_patching_unit_tests.log` |
| 4 | `hardening_unit_tests` | test | 0 | 0 | PASS | `logs/04_hardening_unit_tests.log` |
| 5 | `examples_marked` | check | 0 | 0 | PASS | `logs/05_examples_marked.log` |
| 6 | `inspect_example_manifest` | inspect | 0 | 0 | PASS | `logs/06_inspect_example_manifest.log` |
| 7 | `print_cli_commands` | dry-run | 0 | 0 | PASS | `logs/07_print_cli_commands.log` |
| 8 | `patch_fixture_malformed_absolute_path` | fixture | 2 | 2 | PASS | `logs/08_patch_fixture_malformed_absolute_path.log` |
| 9 | `patch_fixture_malformed_bad_percent` | fixture | 2 | 2 | PASS | `logs/09_patch_fixture_malformed_bad_percent.log` |
| 10 | `patch_fixture_malformed_baseline_truncated` | fixture | 2 | 2 | PASS | `logs/10_patch_fixture_malformed_baseline_truncated.log` |
| 11 | `patch_fixture_malformed_bool_as_int` | fixture | 2 | 2 | PASS | `logs/11_patch_fixture_malformed_bool_as_int.log` |
| 12 | `patch_fixture_malformed_duplicate_key` | fixture | 2 | 2 | PASS | `logs/12_patch_fixture_malformed_duplicate_key.log` |
| 13 | `patch_fixture_malformed_empty_rings` | fixture | 2 | 2 | PASS | `logs/13_patch_fixture_malformed_empty_rings.log` |
| 14 | `patch_fixture_malformed_missing_rings` | fixture | 2 | 2 | PASS | `logs/14_patch_fixture_malformed_missing_rings.log` |
| 15 | `patch_fixture_malformed_nan` | fixture | 2 | 2 | PASS | `logs/15_patch_fixture_malformed_nan.log` |
| 16 | `patch_fixture_malformed_not_object` | fixture | 2 | 2 | PASS | `logs/16_patch_fixture_malformed_not_object.log` |
| 17 | `patch_fixture_malformed_percent_over_100` | fixture | 2 | 2 | PASS | `logs/17_patch_fixture_malformed_percent_over_100.log` |
| 18 | `patch_fixture_malformed_schema_version` | fixture | 2 | 2 | PASS | `logs/18_patch_fixture_malformed_schema_version.log` |
| 19 | `patch_fixture_malformed_truncated` | fixture | 2 | 2 | PASS | `logs/19_patch_fixture_malformed_truncated.log` |
| 20 | `patch_fixture_malformed_unknown_ring_key` | fixture | 2 | 2 | PASS | `logs/20_patch_fixture_malformed_unknown_ring_key.log` |
| 21 | `patch_fixture_malformed_unknown_top_key` | fixture | 2 | 2 | PASS | `logs/21_patch_fixture_malformed_unknown_top_key.log` |
| 22 | `patch_fixture_malformed_wrong_type` | fixture | 2 | 2 | PASS | `logs/22_patch_fixture_malformed_wrong_type.log` |
| 23 | `patch_fixture_neg_bad_operation` | fixture | 1 | 1 | PASS | `logs/23_patch_fixture_neg_bad_operation.log` |
| 24 | `patch_fixture_neg_bad_reboot` | fixture | 1 | 1 | PASS | `logs/24_patch_fixture_neg_bad_reboot.log` |
| 25 | `patch_fixture_neg_baseline_no_delay` | fixture | 1 | 1 | PASS | `logs/25_patch_fixture_neg_baseline_no_delay.log` |
| 26 | `patch_fixture_neg_baseline_os_mismatch` | fixture | 1 | 1 | PASS | `logs/26_patch_fixture_neg_baseline_os_mismatch.log` |
| 27 | `patch_fixture_neg_canary_concurrency_5` | fixture | 1 | 1 | PASS | `logs/27_patch_fixture_neg_canary_concurrency_5.log` |
| 28 | `patch_fixture_neg_canary_concurrency_percent` | fixture | 1 | 1 | PASS | `logs/28_patch_fixture_neg_canary_concurrency_percent.log` |
| 29 | `patch_fixture_neg_canary_errors` | fixture | 1 | 1 | PASS | `logs/29_patch_fixture_neg_canary_errors.log` |
| 30 | `patch_fixture_neg_canary_gated` | fixture | 1 | 1 | PASS | `logs/30_patch_fixture_neg_canary_gated.log` |
| 31 | `patch_fixture_neg_duplicate_patchgroup` | fixture | 1 | 1 | PASS | `logs/31_patch_fixture_neg_duplicate_patchgroup.log` |
| 32 | `patch_fixture_neg_gate_no_compliance_evidence` | fixture | 1 | 1 | PASS | `logs/32_patch_fixture_neg_gate_no_compliance_evidence.log` |
| 33 | `patch_fixture_neg_gate_wrong_order` | fixture | 1 | 1 | PASS | `logs/33_patch_fixture_neg_gate_wrong_order.log` |
| 34 | `patch_fixture_neg_gated_task_install` | fixture | 1 | 1 | PASS | `logs/34_patch_fixture_neg_gated_task_install.log` |
| 35 | `patch_fixture_neg_missing_baseline_file` | fixture | 1 | 1 | PASS | `logs/35_patch_fixture_neg_missing_baseline_file.log` |
| 36 | `patch_fixture_neg_missing_gate` | fixture | 1 | 1 | PASS | `logs/36_patch_fixture_neg_missing_gate.log` |
| 37 | `patch_fixture_neg_no_approver` | fixture | 1 | 1 | PASS | `logs/37_patch_fixture_neg_no_approver.log` |
| 38 | `patch_fixture_neg_no_escalation_contacts` | fixture | 1 | 1 | PASS | `logs/38_patch_fixture_neg_no_escalation_contacts.log` |
| 39 | `patch_fixture_neg_no_presnapshot` | fixture | 1 | 1 | PASS | `logs/39_patch_fixture_neg_no_presnapshot.log` |
| 40 | `patch_fixture_neg_real_account_id` | fixture | 1 | 1 | PASS | `logs/40_patch_fixture_neg_real_account_id.log` |
| 41 | `patch_fixture_neg_ring_order_gap` | fixture | 1 | 1 | PASS | `logs/41_patch_fixture_neg_ring_order_gap.log` |
| 42 | `patch_fixture_neg_rollback_no_procedure` | fixture | 1 | 1 | PASS | `logs/42_patch_fixture_neg_rollback_no_procedure.log` |
| 43 | `patch_fixture_neg_rollback_too_slow` | fixture | 1 | 1 | PASS | `logs/43_patch_fixture_neg_rollback_too_slow.log` |
| 44 | `patch_fixture_neg_rollback_unknown_strategy` | fixture | 1 | 1 | PASS | `logs/44_patch_fixture_neg_rollback_unknown_strategy.log` |
| 45 | `patch_fixture_neg_short_soak` | fixture | 1 | 1 | PASS | `logs/45_patch_fixture_neg_short_soak.log` |
| 46 | `patch_fixture_neg_task_rate_mismatch` | fixture | 1 | 1 | PASS | `logs/46_patch_fixture_neg_task_rate_mismatch.log` |
| 47 | `patch_fixture_neg_unknown_patchgroup` | fixture | 1 | 1 | PASS | `logs/47_patch_fixture_neg_unknown_patchgroup.log` |
| 48 | `patch_fixture_valid_example_manifest` | fixture | 0 | 0 | PASS | `logs/48_patch_fixture_valid_example_manifest.log` |
| 49 | `patch_fixture_valid_no_window_task` | fixture | 0 | 0 | PASS | `logs/49_patch_fixture_valid_no_window_task.log` |
| 50 | `unit_fixture_valid_hardened_inline` | fixture | 0 | 0 | PASS | `logs/50_unit_fixture_valid_hardened_inline.log` |
| 51 | `unit_fixture_valid_continuation` | fixture | 0 | 0 | PASS | `logs/51_unit_fixture_valid_continuation.log` |
| 52 | `unit_fixture_valid_dropin_strong` | fixture | 0 | 0 | PASS | `logs/52_unit_fixture_valid_dropin_strong.log` |
| 53 | `unit_fixture_valid_target_rhel9` | fixture | 0 | 0 | PASS | `logs/53_unit_fixture_valid_target_rhel9.log` |
| 54 | `unit_fixture_valid_target_debian13` | fixture | 0 | 0 | PASS | `logs/54_unit_fixture_valid_target_debian13.log` |
| 55 | `unit_fixture_neg_unhardened` | fixture | 1 | 1 | PASS | `logs/55_unit_fixture_neg_unhardened.log` |
| 56 | `unit_fixture_neg_root_full_caps` | fixture | 1 | 1 | PASS | `logs/56_unit_fixture_neg_root_full_caps.log` |
| 57 | `unit_fixture_neg_dropin_weakens` | fixture | 1 | 1 | PASS | `logs/57_unit_fixture_neg_dropin_weakens.log` |
| 58 | `unit_fixture_neg_dropin_weakens_arg_order` | fixture | 1 | 1 | PASS | `logs/58_unit_fixture_neg_dropin_weakens_arg_order.log` |
| 59 | `unit_fixture_neg_dropin_adds_sysadmin` | fixture | 1 | 1 | PASS | `logs/59_unit_fixture_neg_dropin_adds_sysadmin.log` |
| 60 | `unit_fixture_neg_target_219` | fixture | 1 | 1 | PASS | `logs/60_unit_fixture_neg_target_219.log` |
| 61 | `unit_fixture_neg_target_rhel8` | fixture | 1 | 1 | PASS | `logs/61_unit_fixture_neg_target_rhel8.log` |
| 62 | `unit_fixture_neg_threshold_tight` | fixture | 1 | 1 | PASS | `logs/62_unit_fixture_neg_threshold_tight.log` |
| 63 | `unit_fixture_malformed_no_section` | fixture | 2 | 2 | PASS | `logs/63_unit_fixture_malformed_no_section.log` |
| 64 | `unit_fixture_malformed_no_service` | fixture | 2 | 2 | PASS | `logs/64_unit_fixture_malformed_no_service.log` |
| 65 | `unit_fixture_malformed_no_execstart` | fixture | 2 | 2 | PASS | `logs/65_unit_fixture_malformed_no_execstart.log` |
| 66 | `unit_fixture_malformed_bad_line` | fixture | 2 | 2 | PASS | `logs/66_unit_fixture_malformed_bad_line.log` |
| 67 | `unit_fixture_malformed_bad_header` | fixture | 2 | 2 | PASS | `logs/67_unit_fixture_malformed_bad_header.log` |
| 68 | `unit_fixture_malformed_unknown_section` | fixture | 2 | 2 | PASS | `logs/68_unit_fixture_malformed_unknown_section.log` |
| 69 | `unit_fixture_malformed_bad_boolean` | fixture | 2 | 2 | PASS | `logs/69_unit_fixture_malformed_bad_boolean.log` |
| 70 | `unit_fixture_malformed_bad_protectsystem` | fixture | 2 | 2 | PASS | `logs/70_unit_fixture_malformed_bad_protectsystem.log` |
| 71 | `unit_fixture_malformed_unknown_capability` | fixture | 2 | 2 | PASS | `logs/71_unit_fixture_malformed_unknown_capability.log` |
| 72 | `unit_fixture_malformed_bad_umask` | fixture | 2 | 2 | PASS | `logs/72_unit_fixture_malformed_bad_umask.log` |
| 73 | `unit_fixture_malformed_dropin_value` | fixture | 2 | 2 | PASS | `logs/73_unit_fixture_malformed_dropin_value.log` |
| 74 | `unit_fixture_malformed_dropin_suffix` | fixture | 2 | 2 | PASS | `logs/74_unit_fixture_malformed_dropin_suffix.log` |
| 75 | `unit_fixture_malformed_unknown_distro` | fixture | 2 | 2 | PASS | `logs/75_unit_fixture_malformed_unknown_distro.log` |
| 76 | `unit_fixture_malformed_missing_file` | fixture | 2 | 2 | PASS | `logs/76_unit_fixture_malformed_missing_file.log` |
| 77 | `score_root_agent` | score | 1 | 1 | PASS | `logs/77_score_root_agent.log` |
| 78 | `score_app_unhardened` | score | 1 | 1 | PASS | `logs/78_score_app_unhardened.log` |
| 79 | `score_app_baseline` | score | 1 | 1 | PASS | `logs/79_score_app_baseline.log` |
| 80 | `score_app_strict` | score | 0 | 0 | PASS | `logs/80_score_app_strict.log` |
| 81 | `score_app_strict_rhel7` | score | 1 | 1 | PASS | `logs/81_score_app_strict_rhel7.log` |
| 82 | `score_app_strict_rhel8` | score | 1 | 1 | PASS | `logs/82_score_app_strict_rhel8.log` |
| 83 | `score_app_strict_ubuntu2004` | score | 1 | 1 | PASS | `logs/83_score_app_strict_ubuntu2004.log` |
| 84 | `score_app_strict_rhel9` | score | 0 | 0 | PASS | `logs/84_score_app_strict_rhel9.log` |
| 85 | `score_app_strict_al2023` | score | 0 | 0 | PASS | `logs/85_score_app_strict_al2023.log` |
| 86 | `score_app_strict_ubuntu2404` | score | 0 | 0 | PASS | `logs/86_score_app_strict_ubuntu2404.log` |
| 87 | `score_app_legacy_rhel7_threshold6` | score | 0 | 0 | PASS | `logs/87_score_app_legacy_rhel7_threshold6.log` |
| 88 | `compat_matrix_render` | render | 0 | 0 | PASS | `logs/88_compat_matrix_render.log` |
| 89 | `cfn_lint` | analyzer | 0 | 0 | PASS | `logs/89_cfn_lint.log` |
| 90 | `yamllint` | analyzer | 0 | 0 | PASS | `logs/90_yamllint.log` |
| 91 | `shellcheck` | analyzer | 0 | 0 | PASS | `logs/91_shellcheck.log` |
| 92 | `sd_verify_root_agent` | analyzer | 0 | 0 | PASS | `logs/92_sd_verify_root_agent.log` |
| 93 | `sd_security_root_agent` | analyzer | 0 | 0 | PASS | `logs/93_sd_security_root_agent.log` |
| 94 | `sd_verify_app_unhardened` | analyzer | 0 | 0 | PASS | `logs/94_sd_verify_app_unhardened.log` |
| 95 | `sd_security_app_unhardened` | analyzer | 0 | 0 | PASS | `logs/95_sd_security_app_unhardened.log` |
| 96 | `sd_verify_app_baseline` | analyzer | 0 | 0 | PASS | `logs/96_sd_verify_app_baseline.log` |
| 97 | `sd_security_app_baseline` | analyzer | 0 | 0 | PASS | `logs/97_sd_security_app_baseline.log` |
| 98 | `sd_verify_app_strict` | analyzer | 0 | 0 | PASS | `logs/98_sd_verify_app_strict.log` |
| 99 | `sd_security_app_strict` | analyzer | 0 | 0 | PASS | `logs/99_sd_security_app_strict.log` |
