# Week 7: Backup and restore you can prove (resilience and incidents 1 of 3)

**Branch:** `$PR2` = `ci-evidence-postgres@e7399fb` (PR #2, harness v2). It was re-pinned from `e610015`. Harness v2 is commits `2aac93c` + `e7399fb`.
Use `$PR3` and `$PR7` for cross-checks.
**Prerequisites:** PostgreSQL binaries with matching client and server majors (`SETUP.md` shows a credential-free conda-forge install). No network or cloud.
**Delivered files used** (all at `e7399fb`): `tests/integration/postgres/{run_restore_scenario.sh,lib.sh,expectations.tsv,expectations.selftest.tsv,verify_evidence.py,verify_evidence.sh,selftest_harness.sh,seed.sql,fingerprint.sql}`,
`tests/integration/README.md`, `evidence/postgres/README.md`, `evidence/postgres/runs/INDEX.md`, `evidence/postgres/runs/{ci-offline-40741329107-1,ci-service-40741329107-1,local-offline-v2-20261028T180208Z}/`,
`.github/workflows/postgres-restore-evidence.yml`.

## Daily exercises
**Day 1: The contract.** Read `expectations.tsv`. Every case has a kind, an expected exit, the modes it runs in, a fail class, and a **required reason regex**.
`seed.sql` loads 50 accounts and 1000 ledger entries (`S08` requires `lab.ledger_entries|1000|<md5>`).
Overall PASS requires exactly one PASS per declared case: 38 offline, 36 service (`tests/integration/README.md`).

**Day 2: Verify committed evidence.**
```bash
cd $PR2
for r in ci-service-40741329107-1 ci-offline-40741329107-1 local-offline-v2-20261028T180208Z ci-mismatch-control-40741329107-1 ci-service-40630856041-1; do
  python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/$r | tail -1; echo "rc=$?"; done
```
- *Observed (R01):* the three CURRENT runs are VERIFIED (36, 38 and 38 cases, 0 problems; exit 0). The mismatch control is `problems=35 -> REJECTED` (exit 1), as intended.
  The v1 runs report `HISTORICAL-KNOWN-INVALID` (exit 3). (In your shell, read `rc` with `${PIPESTATUS[0]}` if you pipe to `tail`.)

**Day 3: Run it yourself.**
```bash
E=$(mktemp -d); PG_BIN=$HOME/pg/env/bin RUN_LABEL=practice EVIDENCE_DIR=$E bash tests/integration/postgres/run_restore_scenario.sh offline; echo rc=$?
python3 tests/integration/postgres/verify_evidence.py $E --require-artifacts
```
- *Observed (R01, PG 16.15):* `overall=PASS passed=38/38 failed=0 errors=0 not_run=0`, then `cases=38 positive=11 negative=6 rows=38 problems=0 -> VERIFIED`.
  All six N01-N06 are `expected_fault_detected`. `ENVIRONMENT.txt` records `git_sha=e7399fbb…`. The tracked tree is unchanged, because evidence went to `$E`.

**Day 4: Fingerprints.** Compare `fingerprints/*.txt` in your run. Explain why row counts alone are not a restore proof, and why `S09_fingerprint_source_sanity` exists.

**Day 5: Restore-time and RPO.** Read `duration_ms` in `COMMANDS.tsv` for the dump and restore steps. Discuss what lab-sized numbers do **not** tell you about production RTO.

## Failure injection and recovery
- **Forged log** (copy of your run): in `logs/*N04*`, replace `23503` and `ledger_entries_account_id_fkey`, then re-verify.
  *Observed (R01c):* `ERROR hash: mismatch: logs/30_N04_fk_enforced_after_restore.log`, `ERROR N04…: reason_regex not found`, and `problems=2 -> REJECTED`, exit 1. *Recovery:* delete the copy.
- **Harness self-test** (no DB): `d=$(mktemp -d); EVIDENCE_DIR=$d bash tests/integration/postgres/selftest_harness.sh`.
  *Observed (R02):* `assertions=26 failed=0`. Deliberate bad cases (unexpected success, wrong reason, a disguised version error, a missing executable, …) are all reported FAIL, ERROR or NOT_RUN.
- **Weakened expectation (the verifier's blind spot, #14 checkpoint 2).** In a `/tmp` copy of your run, set N01's reason regex in the run's own `EXPECTATIONS.tsv` to `.` and re-hash that line in `SHA256SUMS`.
  *Observed (R21):* `problems=0 -> VERIFIED`, exit 0. The verifier trusts the run-local expectations. The tamper is visible only by comparing `sha256_expectations.tsv=` in `ENVIRONMENT.txt` (`70ec3354…`) with the run copy's hash (`66c06325…`), or with the repo's `tests/integration/postgres/expectations.tsv`.
  *Recovery and design lesson:* pin the expectations hash outside the bundle. #14 classes this as non-blocking hardening.
- **Version mismatch.** The CI job `version-mismatch-control` runs pg_dump 18 against `postgres:16`, and the committed run `ci-mismatch-control-40741329107-1` is REJECTED (R01).
  Reproducing it locally needs two PG majors. **UNEXECUTED** (P-W7).

## Answer notes
- v2 counts a negative as PASS only if it fails **and** its output matches the declared reason. Setup runs as separate `S_*` steps with `--needs` dependencies.
- "Skipped means not passed": any declared case that never runs gets `NOT_RUN/missing_test`.

## Architecture tradeoffs
- Strict reason regexes catch false passes, but they couple tests to tool message text. A PG upgrade can turn a real detection into `wrong_reason`.
- Gitignored dumps keep the repo small. CI artifacts keep them for 90 days (`runs/INDEX.md`), and the hashes are in `ARTIFACTS.sha256`.

## Fifteen-minute walkthrough
expectations.tsv → a fresh run → `verify_evidence.py --require-artifacts` → the forged-log rejection → the mismatch control → HISTORICAL v1 runs.

## Interview questions
1. How do you prove a restore is complete and correct?
2. Why must negative tests assert the error text, and what does that cost?
3. What makes an evidence verifier "independent" of the harness?

## PENDING / UNEXECUTED
- P-W7: local reproduction of the version-mismatch control (needs PG 16 and PG 18). Service-container mode was not run locally. It is CI-only here.
- RDS-native or AWS Backup restore: declared in `aws-remediation-vpc-rds@099479e:infra/aws-cdk/lib/network-database-stack.ts` and `backup-dr-aws@10da54f:backup/aws/**` (week 9), never executed.
- The verifier's self-attested expectations gap (R21) is unfixed at `e7399fb`.
