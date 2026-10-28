# Week 11: Defending identity and governance (architecture defense 2 of 3)

**Branches:** `$PR4`, `$PR6`. **ADRs:** `docs/adr/0006`, `0007`, `0008`; module ADRs `infra/orgs/docs/adr/ADR-0001..0003` (PR #6).

## Daily exercises
**Day 1: Layered model.** Draw how the two control planes relate, using only delivered artifacts: Entra CA (human sign-in: MFA, device, risk; `identity/entra/policies/`) and AWS SCPs (account-level ceilings; `infra/orgs/lib/scps.ts`).
State what exists and what does not. A federation **walkthrough document** exists (`identity-governance@f48e7e3:docs/federation/entra-to-aws-iam-identity-center.md`: SAML + SCIM + permission sets, validation, rollback, emergency access; plus `saml-vs-scim.md`).
No federation **configuration or code** is delivered or executed.

**Day 2: Break-glass across both planes.** Entra: `baseline.json` breakGlass plus BASE-001. AWS: `EXEMPT_ROLE_ARNS` (`OrgBreakGlass`, `OrgSecurityAdmin`) in `lab-context.ts`. Defend the exemptions, and say what monitoring you would add. Monitoring is not delivered.

**Day 3: Defend ADR-0003 (SCP validation offline).** Show the three layers, the `require-encryption` defect story, the 5-SCP quota test, and the parliament allowlist.

**Day 4: Defend ADR-0002 (delegated admin).** Be explicit: GuardDuty org enablement is a gap, not code, and Security Hub configuration policies are not modelled.

**Day 5: Control mapping.** In `$PR16` (`control-mapping@3f82697`), run `python3 governance/controls/validate_mapping.py && python3 -m unittest discover -s governance/controls/tests`.
- *Observed (R13):* `rows=17 artifacts=97 NOT_EXECUTED=1 OBSERVED=0 SIMULATION=14 STATIC=2`, `MAPPING VALID`, 10 tests OK.
  Defend **why OBSERVED is 0**: nothing in the lab is observed in production. Then run the mock review board (walkthrough below).

## Failure injection and recovery
Live demos: `ca_validator.py` on `neg-mfa-or-bypass.json` (exit 1), the SCP Deny→Allow lint (`NOT_DENY`), and region-lock evaluator outputs (weeks 4 and 6, E08 and E11).
Then show the two gaps a reviewer will raise: CA007 disabled still passes (R08), and the exempt-role bypass B6-2 (R06).

## Answer notes
- "Report-only first" (BASE-007) and "Deny-only SCPs" (policy-lint `NOT_DENY`) are both encoded as tests, not conventions.

## Architecture tradeoffs
- Offline validators: they are fast and safe, but not authoritative. Access Analyzer, the policy simulator, and the Entra What-If tool are the authoritative checks, and all of them need credentials. All are **not executed**.

## Fifteen-minute walkthrough
(3) Two planes and the missing link → (4) CA baseline rules and exit codes → (4) SCP layout and quota → (2) delegated-admin gaps → (2) break-glass.

## Interview questions
1. How do you stop a CA change from locking out all admins?
2. Which SCP would you roll out first, and how would you stage it?
3. What would you need before trusting the offline SCP evaluator's verdicts?

## PENDING / UNEXECUTED
- No Entra ↔ AWS federation configuration (documents only, #18), no break-glass monitoring, no Access Analyzer, no What-If.
- B6-2 and CA007 are unfixed. The FFIEC mapping (#16) is lab material, not an examination.
