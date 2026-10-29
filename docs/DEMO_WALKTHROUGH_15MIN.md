# 15-minute portfolio demonstration

Target: `delivery/portfolio` (draft PR #35). Record `git rev-parse HEAD` before starting. Use a clone with full history. Python, Bash and Git suffice for the commands below; all are credential-free. Historical evidence verifies historical runs, not a fresh incident.

| Minutes | Demonstration | Meaning |
|---|---|---|
| 0–2 | Read README scope and module inventory | Personal lab; disclose AI assistance and limits |
| 2–4 | Open the current portfolio-validation Actions run, inspect exact SHA and failed/passed jobs | CI evidence; eligibility remains separate |
| 4–6 | Run PostgreSQL evidence verifier below | Real PostgreSQL recovery evidence from a historical lab run |
| 6–8 | Run Entra baseline validator and inspect M365 PLAN_ONLY scenarios | Synthetic identity controls; no tenant mutations |
| 8–10 | Run observability evaluator and vendor contract tests | Offline resilience and fictional vendor behavior |
| 10–12 | Verify incident timeline below | SIMULATION; do not present timings as production performance |
| 12–14 | Show hybrid runbooks, patch rings, team escalation and control mapping | Reference designs and validated inspectors; operations NOT_EXECUTED |
| 14–15 | Open job matrix and delivery report | Explicitly distinguish portfolio evidence from career-history gaps |

```bash
python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-service-40741329107-1
python3 identity/entra/ca_validator.py --quiet
python3 observability/run_healthcheck.py evaluate observability/fixtures/healthy.json --now 2026-10-28T12:01:00Z
(cd integrations/vendor-mock && python3 -m unittest discover -s tests -t .)
bash scripts/ci/incident_checks.sh committed
python3 operations/hybrid/checks/check_hybrid_runbooks.py
```

For the full offline suite run `bash scripts/validate-all.sh --python-only`. For a fresh PostgreSQL incident use the existing `incident-fresh-run` Actions job; missing server binaries must report NOT_EXECUTED and fail, never pass.

Useful references: [team model](../operations/team/README.md), [patching](../operations/patching/README.md), [identity governance](../identity/governance/README.md), [cost estimate](runbooks/aws-backup/cost-capacity/README.md), [job matrix](JOB_REQUIREMENTS_MATRIX.md).
