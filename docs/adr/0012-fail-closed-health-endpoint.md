# 0012: Fail-closed health endpoint decision
- Status: **Proposed.** #10 is an open draft, not integrated in #7.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- `observability@3e40e39:observability/healthcheck/` evaluates probe results against a policy (defaults in `observability/healthcheck/decision.py` and `observability/README.md`: `max_age_s` 300, `max_probe_latency_ms` 5000, at most 16 probes; unknown policy keys rejected).
- `serve: true`/HTTP 200 only when every required check passes. Anything else, including anything unanticipated, is UNHEALTHY with `serve: false`/HTTP 503 (`observability/README.md`, "Fail-closed decision").
- Exit codes: 0 HEALTHY, 1 UNHEALTHY, 2 malformed input. The result is still written on 2 (`observability/run_healthcheck.py`).
- Evidence binds the decisions to input hashes (`evidence/observability/generate_evidence.py --verify`).

## Consequences
- A stale or malformed payload takes the instance out of rotation. This favours correctness over availability, which suits ledger-facing services, at the cost of spurious 503s if `max_age_s` is set too tight.
- Verified here: 64 tests OK; healthy, stale and malformed-NaN fixtures gave exit 0, 1 and 2 with 200, 503 and 503; VERIFY PASS (R09). Live `collect` mode was not executed.
