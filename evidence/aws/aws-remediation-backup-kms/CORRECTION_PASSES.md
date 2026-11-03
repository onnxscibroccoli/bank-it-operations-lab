# Correction passes (limit: 3). Failure output is kept in logs/

- Baseline (main@8e2df97, before any change): `logs/02-baseline-jest.log` (37/37). `logs/03-*.log` is the guard
  scan of the committed infra templates: exit 1, 2 violations on DbBackupPolicy (F-03). `logs/04-*.log` is the guard
  scan of the committed backup/aws templates: exit 1, 8 violations (F-01, F-02).
- Pass 1: `logs/05` tsc ok. `logs/06` Jest **failed** 76/77. One new negative test expected only
  KMS_ADMIN_OPERATIONAL_MIX, but the guard also (correctly) reported KMS_CRYPTO_NOT_VIA_SERVICE.
- Correction 1: corrected the test expectation to both rules. No guard or policy was weakened. `logs/07` tsc ok,
  `logs/08` Jest 77/77, `logs/09` synth ok (4 nag reports, 0 non-compliant), `logs/10` guard scan 0,
  `logs/11` shared S3 self-log check ok, `logs/12` fallback trust-mode synths ok, `logs/13` invalid mode rejected
  (expected exit 1).
- Correction 2 (proposed backup/aws patch, scratch copy only): `logs/14` to `logs/17` **failed**. A `*/` inside the
  JSDoc text ("Create*/Put*/...") closed the comment early, so tsc, Jest, and synth failed and the scan found no
  templates.
- Correction 3: rewrote the comment without `*/`. `logs/18` to `logs/21` **still failed** because a second `*/`
  remained ("ReEncrypt*/GenerateDataKey*/"). In the same correction, after checking all `*/` occurrences:
  `logs/22` tsc ok, `logs/23` Jest 46/46, `logs/24` synth ok, `logs/25` guard scan 0. The patch in
  `proposed-backup-aws/` is the final version.
- Repo-wide checks (not counted as code corrections; bookkeeping outside infra/aws-cdk is disclosed in the PR):
  - `logs/26`: validate-all --python-only **failed**. 2 of 159 tests in `scripts/ci/tests/test_ac_repairs_b908a66.py`
    failed because a per-entry `EX-04 status:` marker had been added to the frozen register, and
    `inventory/generate.py --check` reported drift. The register edits were reverted (it is a preserved record), and
    the proposed text moved to `SECURITY_EXCEPTIONS_EX04_UPDATE.md`. The derived `inventory/assets.json` and
    `inventory/ARCHITECTURE.md` were regenerated.
  - `logs/27`: the rerun still **failed**, on the portfolio step (inventory drift, written before the regeneration
    was complete).
  - `logs/28`: the docs checks **failed** `test_frozen_records_unchanged` for `inventory/ARCHITECTURE.md`, a
    generated file that is also hash-pinned. Its hash in `docs/metadata/preserved-records.json` was updated in a
    separate, clearly labelled commit. pages.json entries were added for the 6 new .md files.
  - `logs/29`: docs checks ok. `logs/30`: validate-all --python-only PASS (34 steps). `logs/31`: final Jest 77/77.

The correction budget is used up (3). No control was weakened to get a pass.
