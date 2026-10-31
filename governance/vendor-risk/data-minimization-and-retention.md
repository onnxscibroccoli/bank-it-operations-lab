# Data minimization and retention notes — vendor integrations

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Define responsibilities and risks when an organization depends on an external service. Clear ownership and retained evidence help an organization respond without sending unnecessary sensitive data.

For example: During an outage, the team uses an escalation record to distinguish its responsibilities from the fictional vendor’s responsibilities.

Key terms: **API** means an interface through which programs request operations or information. **RACI** means a responsibility table identifying who is responsible, accountable, consulted, and informed. **Mock** means a controlled substitute for a real component used in a test or demonstration.

**Before using this reference:** Do not send fictional escalation examples as real messages or copy personal data into public exercise records.

Start with the [plain-English learning path](../../docs/knowledge/governance.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Lab guidance (SIMULATION context). Not legal advice; actual retention periods come from the
> institution's records-retention schedule and applicable law/regulation, which this lab does not
> assert.

## Minimization principles

1. **Request only what the use case needs.** Each field in an integration contract needs a named
   purpose in the assessment (§2/§8). No purpose → not requested, not stored.
2. **Prefer reduced forms.** Masked account numbers (`****0101`), opaque IDs, minor-unit amounts,
   tokens instead of PANs/SSNs, aggregates instead of line items where possible.
3. **Fail closed on unexpected data.** Clients validate responses with `additionalProperties: false`;
   an unexpected field (e.g. `ssn`) causes rejection rather than silent ingestion. Implemented and
   tested in `integrations/vendor-mock` (`malformed_extra_field`).
4. **No secrets or customer data in logs, errors or test evidence.** Errors carry status, error code
   and request ID only. Tested: the client secret never appears in exception text or `repr`.
5. **Test with synthetic data only.** All fixtures are fictional and labelled `SIMULATION`.
6. **Scope access.** Separate OAuth scopes per data domain (`accounts:read`, `transactions:read`);
   missing scope → 403 (tested).

## Retention notes (placeholders to be set per records schedule)

| Data | Our side | Vendor side | Deletion method / evidence |
|---|---|---|---|
| Access tokens | memory only; never persisted | per vendor token TTL (`expires_in`) | expiry; revoke on exit |
| Client credentials | secret manager; rotate every `<N>` days | vendor IdP | revoke at exit, confirm in writing |
| API request/response logs | metadata only (method, path template, status, request ID, latency); `<N>` days | `<vendor log retention>` | log lifecycle policy |
| Account / transaction data cached by integration | `<minimum needed; prefer no cache>` | system of record | cache TTL; purge at exit |
| Assessment & evidence artefacts | per third-party risk program, `<N>` years | — | records schedule |
| Data returned at exit | until migration verified | certified deletion incl. backups & subprocessors within `<N>` days | deletion certificate |
