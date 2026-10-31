# Week 4: Entra ID Conditional Access baseline (identity and governance 1 of 3)

**Branch:** `$PR4` = `entra-ca-offline@d302c99` (PR #4). **Prerequisites:** Python 3 (stdlib only). No tenant, no Graph, no credentials.
**Delivered files used:** `identity/entra/{README.md,baseline.json,ca_validator.py,policies/CA001..CA007*.json}`, `tests/entra/{test_ca_validator.py,make_fixtures.py,fixtures/}`.

All object IDs are synthetic lab GUIDs. Only the built-in role template IDs and authentication-strength IDs are Microsoft constants (`identity/entra/README.md`).

## Daily exercises
**Day 1: Read the baseline.** `baseline.json`: 2 break-glass user IDs, 12 privileged role templates, 3 authentication strengths, and
`riskPoliciesMustBeReportOnly: true`. Map each of CA001-CA007 to the README table (state, users, grant).

**Day 2: Run the validator.** `cd $PR4 && python3 identity/entra/ca_validator.py --quiet --md-out /tmp/ca.md; echo rc=$?`
- *Expected:* rc 0. All 13 rules (SCHEMA-001..006, BASE-001..007) PASS. (Executed: E08.)

**Day 3: Unit tests and fixture drift.**
```bash
python3 -m unittest discover -s tests/entra -v
python3 tests/entra/make_fixtures.py --check; echo rc=$?
```
- *Expected:* `Ran 25 tests … OK` and rc 0. (Executed: E08.)

**Day 4: Negative fixtures.** Run the validator on `tests/entra/fixtures/neg-mfa-or-bypass.json` and on `neg-break-glass-not-excluded.json`.
- *Expected:* exit 1, with BASE-003 FAIL and BASE-001 FAIL respectively. (Executed: E08.)

**Day 5: Fail-closed.** Run on `tests/entra/fixtures/malformed-duplicate-key.json`.
- *Expected:* exit 2, SCHEMA-001 FAIL, and every BASE rule `NOT_EVALUATED`. (Executed: E08.)

## Failure injection and recovery
- **Demote MFA to report-only** (scratch copy):
```bash
rm -rf /tmp/entra && cp -r identity/entra /tmp/entra
python3 -c "import json;p='/tmp/entra/policies/CA002-Require-MFA-All-Users.json';d=json.load(open(p));d['state']='enabledForReportingButNotEnforced';json.dump(d,open(p,'w'),indent=2)"
python3 identity/entra/ca_validator.py /tmp/entra/policies --quiet --md-out /tmp/inj.md; echo rc=$?
```
  *Observed (E08):* `overall=FAIL exit=1`, BASE-003 FAIL. Report-only policies never satisfy BASE-002/003/004/006.
  *Recovery:* delete `/tmp/entra`.

## Review finding (from #14, re-verified)
- **CA007 has no baseline rule.** Copy `identity/entra` to `/tmp`, set `CA007-…json` `state` to `disabled`, then run `ca_validator.py /tmp/…/policies --quiet`.
  *Observed (R08):* `overall=PASS exit=0`. Disabling the admin-portal location block goes undetected. Exercise: write (in notes) the BASE-008 rule you would add.
- #14 lists other gaps: no coverage of session controls, guests, workload identities or named-location definitions. The evidence logs record only exit codes, not which rule failed.

## Answer notes
- Exit code 2 (malformed) is different from 1 (baseline FAIL). A pipeline must never treat "could not parse" as "passed".
- `OR` grant semantics can silently bypass MFA (`neg-mfa-or-bypass`). BASE-003 requires AND semantics.
- Break-glass accounts must be excluded from every policy (BASE-001), so a CA mistake cannot lock out every admin.

## Architecture tradeoffs
- Offline validation of exported JSON versus live Graph reads: it is safe and reproducible, but it proves nothing about a real tenant's state.
- Strict schema (unknown keys rejected) versus forward compatibility with new Graph fields: here, new fields fail closed until the validator is updated.

## Fifteen-minute walkthrough
Baseline → one PASS run → one neg fixture → one malformed fixture → the exit-code contract.

## Interview questions
1. Why exclude break-glass accounts, and how do you monitor them instead?
2. Why should risk-based policies start in report-only?
3. What is the difference between `mfa` and an authentication strength of phishing-resistant MFA?
4. What would it take to point this validator at a real tenant export safely?

## PENDING / UNEXECUTED
- Any live tenant comparison: out of scope. There is no Graph client in the repo.
