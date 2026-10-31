# Investigate why a service stopped working

## Level 1: Everyday explanation

An outage means a service is not working as needed. Monitoring checks whether expected behavior is occurring. Diagnosis gathers clues about why it is failing. Recovery restores service and checks that people can use it again.

For example, a checkout screen may fail because the application cannot reach its database. Restarting everything immediately could destroy useful clues. First record the symptom and time.

## Level 2: Operational responsibilities

Confirm impact, assign an incident owner, record a timeline, communicate factual updates, and verify recovery from the user's perspective. Escalation means involving people with the responsibility or skills to help. The repository's incident escalation is simulated; no notification is sent.

## Level 3: Safe diagnostic tutorial

Objective: interpret a saved healthy observation. Estimated 10 minutes, beginner. Requires Python 3 and repository read access. This command evaluates fictional recorded data without making network probes:

```bash
python3 observability/run_healthcheck.py evaluate observability/fixtures/healthy.json --now 2026-10-28T12:01:00Z
```

Expected: HEALTHY with exit 0, decision output and structured logs. The fixed clock matches the fixture. A different current time can make old observations stale, correctly producing an unhealthy decision. No cleanup is needed.

If the file is missing, check your working directory. If the result is unhealthy, read which check failed. Do not weaken the threshold just to get a green result. The `collect` mode performs real network requests; it is deliberately outside this introductory exercise.

## Level 4: Crash simulation and limitations

The [incident simulation](../../scenarios/incident/README.md) intentionally stops a disposable PostgreSQL database with immediate shutdown, detects failure, restarts it, and compares data fingerprints. **It intentionally interrupts its lab database.** Read its complete prerequisites and isolate it from real services before execution.

The timeline distinguishes mean-time terminology from this single incident's measured detection and restoration intervals. A test of one artificial failure does not prove coverage of all outages or cyberattacks. Inspect [health decision logic](../../observability/healthcheck/decision.py) and [timeline verifier](../../scenarios/incident/lib/timeline.py).

## Agent guidance

Begin with offline evaluate mode. Never change probe destinations, start a crash exercise, or contact a real service just because a search result links here. Preserve timestamps and raw logs. Read [observability reference](../../observability/README.md) for bounds and privacy rules.
