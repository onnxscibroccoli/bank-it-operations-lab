# 0008: Offline fail-closed Conditional Access validator
- Status: Proposed (PR #4 open draft)
- Date: 2026-10-28

## Decision (as implemented)
- A stdlib-only validator, `entra-ca-offline@d302c99:identity/entra/ca_validator.py`, checks Graph-shaped policies (`identity/entra/policies/`) against `identity/entra/baseline.json`.
- Exit-code contract: 0 means PASS, 1 means a baseline FAIL, and 2 means malformed input. On 2, the baseline rules are `NOT_EVALUATED`, so the validator fails closed.
- 13 rules (SCHEMA-001..006, BASE-001..007). Report-only and disabled policies never satisfy enforcement rules. Risk policies must be report-only while `riskPoliciesMustBeReportOnly` is true.
- 37 mutation-generated fixtures (`tests/entra/make_fixtures.py --check` detects drift) and 25 unit tests (`tests/entra/test_ca_validator.py`).
- Evidence binds results to input hashes (`evidence/entra/generate_evidence.py --verify`).

## Consequences
- Proves nothing about a real tenant. The repo has no Graph client.
- Fixture generation locates policies by displayName prefix, so renaming a policy breaks `make_fixtures.py` (learning/execution E09).
