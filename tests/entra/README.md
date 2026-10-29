# tests/entra -- Conditional Access validator tests (offline)

```bash
python3 -m unittest discover -s tests/entra -v
```

Python 3 standard library only; no network, tenant or credentials.

- `test_ca_validator.py` -- positive (baseline set passes, Graph envelope passes), baseline negatives
  (missing MFA, MFA bypass via OR, non-compliant device / missing `compliantDevice`, break-glass,
  legacy auth, admin phishing-resistant MFA, risk policy enforcement), fail-closed malformed input,
  rule unit tests and CLI exit codes.
- `make_fixtures.py` -- regenerates `fixtures/` from `identity/entra/policies/` by one targeted mutation
  per fixture. `--check` fails on drift (also asserted by the test suite).
- `fixtures/INDEX.json` -- one-line description of every fixture. Prefixes: `valid-` (exit 0),
  `neg-` (well-formed, baseline FAIL, exit 1), `malformed-` (fail-closed, exit 2).
