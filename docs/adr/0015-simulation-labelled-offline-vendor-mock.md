# 0015: Vendor integration is a SIMULATION-labelled, socket-blocked mock
- Status: **Proposed.** #9 is an open draft, not integrated in #7.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- `vendor-mock@d6efb82:integrations/vendor-mock/`: a fictional "Acme Core Ledger SIMULATION" vendor. Every response must carry `X-Simulation: SIMULATION`, and the contract host is `*.invalid` (`contract/openapi.json`).
- `vendor_mock/mock.py` injects failures in-process, with no sockets. `tests/_offline.py` blocks socket use for the whole test run.
- The client rejects malformed responses (`MalformedResponseError`), including an unexpected `ssn` field, so nothing is passed through (`integrations/vendor-mock/README.md`).
- Governance: `governance/vendor-risk/` templates and SIMULATION examples, checked by `check_governance.py`.

## Consequences
- The client cannot drift into contacting a real vendor. Contract fidelity to any real vendor is unproven.
- `d6efb82` adds the vendor-escalation tabletop and makes `check_governance.py` enforce the real-versus-fictional vendor distinction.
- Verified here: the documented invocation (`-t .`) passes 45 tests, while plain `discover` fails with a module-path error (R12). At `d6efb82`, the governance tests pass 25/25, the lint passes and evidence verify passes (R12).
