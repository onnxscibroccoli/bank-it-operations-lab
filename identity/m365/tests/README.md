# identity/m365 tests

`python3 -m unittest discover -s identity/m365/tests -v`. This uses the stdlib only, needs no network and uses synthetic data.

- `test_m365_ops.py` contains unit tests for licensing, device compliance, offboarding order, AADSTS mapping, service-health
  correlation, break-glass rules and the fail-closed and safety guards, plus a full-corpus check that every scenario matches its expectation.
- In `fixtures/`, files named `malformed-*.json` must exit **2** (each one targets a different SCHEMA/SAFE/SYN rule), and files named
  `mismatch-*.json` must exit **1** (a valid scenario whose recorded expectation is deliberately wrong).
