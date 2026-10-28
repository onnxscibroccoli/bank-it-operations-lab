# Acme Core Ledger SIMULATION — offline vendor API mock

> **SIMULATION.** "Acme Core Ledger SIMULATION" is a **fictional** banking vendor invented for this
> lab. Every file, fixture and response here is labelled `SIMULATION`.
>
> **No compatibility claim.** This contract and mock are not derived from, endorsed by, or
> compatible with any real vendor API or product — including Banno / Jack Henry or any other core,
> digital-banking or fintech platform. **No authoritative compatibility evidence exists.** Passing
> these tests says nothing about integrating with a real vendor; that would require the vendor's own
> published contract, a sandbox, and a signed agreement.

## Layout

```
contract/openapi.json     OpenAPI 3.0.3-style contract (SIMULATION; server host is *.invalid)
fixtures/*.json           fictional accounts, transactions, client credentials (no PII, not secrets)
vendor_mock/contract.py   stdlib-only validator for the JSON-Schema subset the contract uses
vendor_mock/mock.py       in-process mock + failure-injection scenarios (no sockets)
vendor_mock/client.py     reference client: OAuth2 client-credentials, timeout, 429/Retry-After, fail-closed validation
vendor_mock/server.py     OPTIONAL loopback-only (127.0.0.1) HTTP wrapper for manual poking; not used by tests
tests/                    offline unittest suite; `tests/_offline.py` blocks socket use for the whole run
```

## Run the tests (offline, Python 3.10+, stdlib only)

```bash
cd integrations/vendor-mock
python3 -m unittest discover -s tests -t . -v
```

Evidence capture: `python3 evidence/vendor/generate_evidence.py` from the repo root
(see `evidence/vendor/README.md`).

## Endpoints (SIMULATION)

| Method | Path | Success | Declared errors |
|---|---|---|---|
| GET | `/v1/health` | 200 `Health` | — |
| POST | `/oauth/token` (client_credentials, form body) | 200 `Token` | 401, 429 |
| GET | `/v1/accounts/{account_id}` | 200 `Account` | 401, 403, 404, 429, 503 |
| GET | `/v1/accounts/{account_id}/transactions?limit&cursor` | 200 `TransactionPage` | 401, 403, 404, 429, 503 |

Every response must carry `X-Simulation: SIMULATION` and a body field `"simulation": "SIMULATION"`.
429 responses must carry `Retry-After` in delay-seconds form (0–3600).

## Client behaviour under test

| Condition | Scenario(s) | Expected client behaviour |
|---|---|---|
| Happy path | `normal` | token fetched once and reused; pagination followed to the end |
| Authentication failure | `auth_invalid_client`, wrong secret, unknown client | `AuthenticationError`; no resource call made; secret never in error text or `repr` |
| Token rejected / expired | `auth_token_rejected`, `auth_token_expired_once` | re-authenticate **once**; then succeed or raise `AuthenticationError` |
| Timeout | `timeout`, `timeout_once`, latency > timeout | bounded retries with exponential backoff (2s, 4s …), then `VendorTimeoutError` |
| Rate limiting | `rate_limit_once`, `rate_limit_always` | sleep exactly `Retry-After`, bounded retries, then `RateLimitedError(retry_after=…)` |
| Excessive Retry-After | `rate_limit_long` (3600s > cap 30s) | fail fast, no sleep |
| Bad / missing Retry-After | `rate_limit_bad_retry_after`, `rate_limit_no_retry_after` | `MalformedResponseError` (contract violation) |
| Malformed responses | `malformed_*` (truncated JSON, missing/extra field, wrong type, NaN, wrong content-type, missing SIMULATION header, undeclared status, non-UTF-8) | `MalformedResponseError`; nothing passed through (e.g. an unexpected `ssn` field is rejected) |

Sleeping is injected, so tests never actually wait. The validator itself is negatively tested
(`ValidatorNegatives`); a mutation check (disabling `additionalProperties` enforcement or the
Retry-After cap) makes the suite fail, so a lenient implementation cannot produce a false PASS.
