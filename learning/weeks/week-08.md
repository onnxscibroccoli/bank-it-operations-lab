# Week 8: Incident review: a CI failure, false passes, and the fix (resilience and incidents 2 of 3)

**Branches:** `$PR2` (`ci-evidence-postgres@e7399fb`), `$PR3` (`review/pr1-pr2-evidence-audit@fb36341`), `$PR7` (`overnight/integration@49122f2`),
`$PR13` (`team-management@9dc8f1f`), `$PR9` (`vendor-mock@d6efb82`), `$PR22` (`incident-demo@3f13622`).
**Delivered files used:** `evidence/postgres/runs/ci-service-40630856041-1/{NOTE.md,STATUS.json,COMMANDS.tsv,logs/}` and `evidence/postgres/runs/INDEX.md` (#2);
`reports/review-pr1-pr2.md` §2 and `evidence/shared/{validate_evidence.py,negative-expectations.postgres.json}` (#3); `reports/INTEGRATION.md` item 4 and `evidence/shared/validate_evidence.py` (#7);
`docs/management/{ticket-priority,stakeholder-updates,operational-review}.md` and `operations/team/escalation-matrix.md` (#13); `governance/vendor-risk/scenarios/core-banking-vendor-outage-SIMULATION.md` (#9).

## The incident (from delivered evidence)
1. **Failure.** CI run 40630856041: pg_dump 18.6 against a `postgres:16` service. The `SET transaction_timeout` from pg_dump 18 is rejected by PG 16 (`NOTE.md`).
2. **Masked failure.** In that run, harness v1 recorded N01, N04, N05 and N06 as PASS, but they failed for unrelated reasons (#3 §2).
3. **First fix.** `e610015` changed the image to `postgres:18` and added a version check.
4. **Root-cause fix.** Harness v2 (`2aac93c`, `e7399fb`) makes negatives fail for their declared reason, adds a mismatch control job and a self-test, and marks the v1 runs `HISTORICAL-KNOWN-INVALID`.
5. **Second-order defect.** #3's shared checker silently reported `NEGATIVES OK: 0` on v2's 12-column COMMANDS.tsv. #7 (`05941a9`) fixed it to read columns by header name and to fail on zero negatives.

## Daily exercises
**Day 1: Timeline.** Build it from `NOTE.md`, `git log origin/ci-evidence-postgres`, `runs/INDEX.md` (times are EDT), and #7 `reports/INTEGRATION.md`.

**Day 2: Reproduce the detection.** `python3 $PR3/evidence/shared/validate_evidence.py postgres-negatives $PR2/evidence/postgres/runs/ci-service-40630856041-1`
- *Observed (E13, re-checked R03):* 4 × `ERROR FALSE-PASS`.

**Day 3: Reproduce the tool interface bug** (it teaches more than the original incident):
```bash
python3 $PR3/evidence/shared/validate_evidence.py postgres-negatives $PR2/evidence/postgres/runs/ci-offline-40741329107-1   # PR #3 version
python3 $PR7/evidence/shared/validate_evidence.py postgres-negatives $PR7/evidence/postgres/runs/ci-offline-40741329107-1   # PR #7 version
```
- *Observed (R03):* the PR #3 version prints `NEGATIVES OK: 0 negative steps failed for the intended reason` (exit 0). That is a vacuous pass.
  The PR #7 version prints `NEGATIVES OK: 6 negative steps failed for the intended reason`.

**Day 4: The self-test replay.** `selftest_harness.sh` Part B replays run 40630856041's preserved logs through the v2 expectations, and N01/N04/N05/N06 must come out `ERROR/version_mismatch`.
*Observed (R02):* `[PASS] B.N05_was_false_pass expected=ERROR/version_mismatch actual=ERROR/version_mismatch` (and the same for the others). 26/26 assertions.

**Day 5: Run the process side.** Using the synthetic #13 material:
- classify the incident with `docs/management/ticket-priority.md` (P1-P4)
- pick the escalation path in `operations/team/escalation-matrix.md`
- draft a stakeholder update in the style of `docs/management/stakeholder-updates.md`

For a vendor-caused variant, walk through #9's SIMULATION tabletop `core-banking-vendor-outage-SIMULATION.md`. Its content is linted by `check_governance.py` (R12).

## Extension: a live (SIMULATION) incident with real MTTD/MTTR
#22 runs a loopback-only stack built from pinned components: the vendor mock `88a3785`, observability `3e40e39`, and the Postgres seed and fingerprint `e7399fb`.
It crashes the DB (`pg_ctl stop -m immediate`), detects the failure with #10's fail-closed probes, diagnoses, restarts with crash recovery, verifies fingerprints, and writes a timeline (`scenarios/incident/README.md`).
```bash
cd $PR22 && git fetch origin vendor-mock observability ci-evidence-postgres
PG_BIN=$HOME/pg/env/bin scenarios/incident/run_incident_demo.sh
scenarios/incident/selftest.sh evidence/incident/runs/<run_id>
python3 scenarios/incident/lib/timeline.py --verify evidence/incident/runs/<run_id>
```
- *Observed (R18):* `status: PASS`, `steps_total: 19`, `mttd_s: 3.596`, `mttr_s: 8.52`, `time_to_diagnose_s: 0.203`, 4 polls with 1 UNHEALTHY. Selftest gives `0 failure(s)`, and `--verify` gives `VERIFY PASS`.
  The committed run `local-20261028T181818Z` recorded 3.584 s and 8.593 s, so your numbers will differ slightly.
- Failure injection on the evidence: edit `mttr_s` in a `/tmp` copy's `SUMMARY.json`. *Observed (R18):* `VERIFY FAIL: SUMMARY.json metrics do not match values re-derived from events.jsonl/monitor.tsv` plus a hash mismatch, exit 1.
- Write the post-incident review below for **this** incident too, using `evidence/incident/INCIDENT-REPORT-SIMULATION.md` as the model answer.
- Important: move or delete your local run directory afterwards. Never commit it to someone else's branch.

## Failure injection and recovery
- In a `/tmp` copy of a run, change one negative's log so it no longer matches. Then run the v2 verifier (week 7, R01: REJECTED) and the #3 tool on a v1 run (E13: N03 FALSE-PASS).

## Post-incident review template
Summary · Impact · Timeline · Root causes (version skew; test design; checker interface) · What went well (failure evidence preserved; independent review) ·
What went wrong (inaccurate NOTE.md at the time; a vacuous checker pass) · Actions (v2, mismatch control, header-based parsing, fail on zero) · Evidence links.

## Answer notes
- A checker that can pass on zero inputs is a false-pass generator. "Fail on zero" is a general rule.
- Preserving failing evidence byte-identically (with STATUS.json and NOTE.md beside it) let three later reviewers re-derive the story.

## Architecture tradeoffs
- Floating runner images (`ubuntu-latest`) versus pinned ones: v2 handles skew by detecting it (`S04`), not by preventing it.
- One shared checker across bundles versus per-bundle verifiers: the shared one drifted from v2's format. Contract tests between tools are needed.

## Fifteen-minute walkthrough
The failure → the masked false passes → the v2 design → the vacuous checker → #7's fix → the process artifacts (#13).

## Interview questions
1. How do you stop "expected failure" tests from hiding real failures?
2. How would you have caught the `NEGATIVES OK: 0` defect before it shipped?
3. Walk through your P1 comms for this incident.

## PENDING / UNEXECUTED
- #7's checker fix is on #7 only. #3 at `fb36341` still has the vacuous-pass behaviour (R03).
- The #13 and #9 process documents are synthetic or SIMULATION. No real ticket, escalation or vendor contact exists.
- #22 is SIMULATION on loopback with lab-scale data. Its MTTD/MTTR say nothing about production. Escalation is recorded only, and nothing is sent. #22 has no CI.
