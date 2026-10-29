# 15-minute demo walkthrough

For a hiring manager or interviewer reviewing this lab against the bank **IT Manager** posting (AMS Technology Solutions, Boston; requirement IDs A1–D4 from the [job requirements matrix](https://github.com/onnxscibroccoli/bank-it-operations-lab/blob/9fb49fa96903bf5b0de58dad7c5741c30d6a7d3d/docs/JOB_REQUIREMENTS_MATRIX.md)).

- **Prepared:** 2026-10-28, about 20:30 EDT; re-pinned to the live candidate `1fdf25a` at about 21:50 EDT. **Demo target:** PR [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) integration candidate [`1fdf25a`](https://github.com/onnxscibroccoli/bank-it-operations-lab/tree/1fdf25ad10c56bb457d6242392f9305c539d1209) (draft, not merged, not independently reviewed).
- **Labels:** every step says whether what you see is **EXECUTED** (CI run or evidence hash), **SIMULATION**, or **NOT_EXECUTED** reference. See the [README](../README.md#evidence-labels).
- **Tested:** every command in the "Run" lines was re-run by the reports agent at `1fdf25a` on 2026-10-28 about 21:45 EDT, on Linux with Python 3.13 and no credentials. The output quoted is what it printed. Total command time is under 10 seconds.
- **Needs:** `git`, `python3` (stdlib only), `bash`. PostgreSQL server binaries are only needed for the optional fresh incident run.

## Setup (before the clock starts)

```bash
git clone https://github.com/onnxscibroccoli/bank-it-operations-lab.git
cd bank-it-operations-lab
git checkout 1fdf25ad10c56bb457d6242392f9305c539d1209
```

## Timeline

| Time | Step | Label | Show | Job rows |
|---|---|---|---|---|
| 0:00–1:30 | 1. Framing | — | README module map and "What the lab does not show" | — |
| 1:30–3:30 | 2. The integration gate | EXECUTED (CI) | Run 40800364073 | B4, B7, B9 |
| 3:30–6:00 | 3. Backup validation on real PostgreSQL | EXECUTED (CI) | Run 40741329107 and its evidence | B15a, B13, C8 |
| 6:00–8:00 | 4. AWS architecture and exceptions | EXECUTED (CI) synth/test/nag; deploy NOT_EXECUTED | CDK stacks, cdk-nag, exception register | A3, B3, C3, C9 |
| 8:00–10:00 | 5. Identity: Entra CA and M365 operations | EXECUTED (offline, synthetic) | Validator and PLAN_ONLY scenarios | C6, B2 |
| 10:00–12:30 | 6. Incident response | SIMULATION | Incident report and verified timeline | B13, B15b, B8 |
| 12:30–14:00 | 7. Operations and governance references | mixed, mostly NOT_EXECUTED | #17, #21, #19, #16, #13 | B11, B12, C9 |
| 14:00–15:00 | 8. Gaps and what is still open | — | Matrix gaps, USER_ACTIONS_REQUIRED | all |

### 1. Framing (0:00–1:30)

- Open the [README](../README.md). Read the status box aloud: nothing merged into `main`, nothing deployed, no cloud or tenant credentials ever used, personal lab with AI-agent assistance.
- Point at the three labels. The rest of the demo keeps them visible.

### 2. The integration gate (1:30–3:30), **EXECUTED (CI)**

- Open integration-gate [run 40800364073](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800364073) at `1fdf25a`. 19 jobs: 18 success. `merge-eligibility` **fails on purpose**: AC1 (non-author approval of this exact SHA, read from the GitHub reviews API) UNMET; AC2 and AC5 UNMET because 5 cdk-nag suppressions are tied to exceptions still PROPOSED (UA-1); AC4 UNMET; AC3 MET at runtime.
- Talking point: the gate fails closed. A green scanner is not acceptance; review of the exact SHA is required, and a skipped, cancelled or NOT_EXECUTED check counts as a failure.
- Sibling runs at the same SHA: aws-cdk [40800363940](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800363940), postgres [40800363954](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800363954), offline-validation [40800364076](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40800364076): success.
- Run:
  ```bash
  scripts/validate-all.sh --python-only
  # validate-all: PASS (33 steps)
  ```

### 3. Backup validation on real PostgreSQL (3:30–6:00), **EXECUTED (CI)**

- Open [run 40741329107](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107): `pg_dump`/`pg_restore` against a real PostgreSQL service container, row counts and MD5 fingerprints compared, 6 corruption negatives detected, a version-mismatch negative control rejected.
- Show the RCA trail: the earlier failing [run 40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041) is kept, and `evidence/postgres/runs/ci-service-40630856041-1/NOTE.md` explains the false PASSes that led to harness v2.
- Run:
  ```bash
  python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-service-40741329107-1
  # ... cases=36 positive=11 negative=6 rows=36 problems=0 -> VERIFIED
  ```

### 4. AWS architecture and exceptions (6:00–8:00), **EXECUTED (CI)** for synth/test/nag, **NOT_EXECUTED** for deployment

- Open `infra/aws-cdk/lib/network-database-stack.ts`: isolated subnets, Multi-AZ RDS, IAM DB auth, KMS CMKs, AWS Backup vault.
- Open `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` and the cdk-nag reports. EX-01..EX-04 status: see [FINAL_REPORT §3](../reports/FINAL_REPORT.md).
- Say plainly: these stacks were **never deployed**. Finding B5-2 (a KMS privilege-escalation path that cdk-nag missed, fixed in `80f01d6`) is the example of why a scanner pass is not enough.

### 5. Identity: Entra CA and M365 (8:00–10:00), **EXECUTED** offline on synthetic data

- Run:
  ```bash
  python3 identity/entra/ca_validator.py --quiet
  # overall=PASS exit=0
  python3 identity/m365/m365_ops.py
  # ... overall=PASS scenarios=13 passed=13 failed=0 plannedSteps=43 mutationsExecuted=0
  ```
- Talking points: legacy-auth block, phishing-resistant MFA for admins, break-glass exclusion; onboarding blocked when licenses run out; every M365 action is PLAN_ONLY (`mutationsExecuted=0`). **No tenant was touched.**

### 6. Incident response (10:00–12:30), **SIMULATION**

- Open `evidence/incident/INCIDENT-REPORT-SIMULATION.md`: database crash injected, detected by observability probes, diagnosed, restored, verified, with a timeline. Simulated MTTD 3.584 s, MTTR 8.593 s.
- Run:
  ```bash
  python3 scenarios/incident/lib/timeline.py --verify evidence/incident/runs/local-20261028T181818Z
  # VERIFY PASS (SIMULATION run local-20261028T181818Z)
  ```
- Optional, only if PostgreSQL server binaries are installed: `scenarios/incident/run_incident_demo.sh` makes a fresh run (CI does this in `incident-fresh-run`). Not re-run by the reports agent.
- Say plainly: a simulation shows the method (inject, detect, diagnose, restore, verify, write up). It is not a production incident.

### 7. Operations and governance references (12:30–14:00)

These are on separate draft PRs, not in the `1fdf25a` candidate. Open them in the browser.
- [#17](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/17) patch rings and systemd hardening: inspectors **EXECUTED** offline (27 tests); patching **NOT_EXECUTED**.
- [#21](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/21) AWS Backup DR: `evidence/backup/aws-backup-dr/RECOVERY_EXECUTION_STATUS.json` lists all 7 recovery items as **NOT_EXECUTED**. Cost model EXECUTED offline.
- [#19](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/19) Windows/AD/DNS/GPO runbooks: **NOT_EXECUTED** (`operations/hybrid/EXECUTION_STATUS.md`).
- [#16](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/16) FFIEC AIO control mapping: validator EXECUTED; mapping is a study reference, not an attestation.
- [#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13) escalation matrix and on-call: **NOT_EXECUTED** documentation (synthetic team).

### 8. Gaps and what is still open (14:00–15:00)

- Matrix rows no lab can show: A2, A5, A6, B1, B6, B14, B16, C2, C11, C12, D1–D4. Answer from real history only.
- Open items needing the owner: [`reports/USER_ACTIONS_REQUIRED.md`](../reports/USER_ACTIONS_REQUIRED.md) (independent reviewer for the exact SHA, branch protection on `main`, recording the EX-01..EX-04 decisions in the register (UA-1), Entra baseline, #6 Terraform-vs-CDK, final portfolio acceptance).

## If something does not match

The candidate SHA is fixed, so the outputs above should reproduce exactly. If they do not, treat the lab's claim as unverified and check [`reports/FINAL_REPORT.md`](../reports/FINAL_REPORT.md) for a newer head.
