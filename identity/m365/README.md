# M365 and endpoint operations: offline scenarios

> **Offline and synthetic only.** Nothing in this directory signs in to Microsoft 365, Entra ID,
> Intune, Exchange Online or Microsoft Graph. It reads no credentials and changes nothing. The tenant
> "Northwind Lab Bank" is fictional: IDs are lab GUIDs (`xxxxxxxx-0000-4000-8000-xxxxxxxxxxxx`),
> domains end in the reserved `.example` TLD, SKUs are prefixed `LAB_`, and every person, device,
> sign-in and service-health issue is made up. Every remediation step is emitted as `PLAN_ONLY`
> with `executed: false`.

## Layout

| Path | Purpose |
|---|---|
| `tenant/tenant.json` | Synthetic tenant snapshot: service plans and their dependencies, workloads, SKUs and seat counts, license groups, users, devices, Intune compliance policies, CA summary (mirrors `identity/entra` CA001-CA007), break-glass accounts and alert rules, service-health issues. Fixed clock `asOfUtc`. |
| `scenarios/*.json` | One scenario per file, each with an input, required audit evidence and a recorded expected verdict and findings |
| `m365_ops.py` | Python 3 stdlib engine: evaluates each scenario, compares the result with its expectation and fails closed on malformed, unsafe or non-synthetic input |
| `runbooks/` | Operator runbooks behind the rules (onboarding, offboarding, access troubleshooting, service-health triage, break-glass) |
| `tests/` | unittest suite and negative fixtures |

## Scenarios

| ID | Type | What it exercises | Expected verdict |
|---|---|---|---|
| M365-ONB-001 | onboarding | E3 via group, compliant Autopilot laptop, TAP on day 1 | READY |
| M365-ONB-002 | onboarding | F3 has no desktop apps (licensing dependency); missing usageLocation inherits the tenant country | BLOCKED |
| M365-ONB-003 | onboarding | E5 seats exhausted (CountViolation); privileged role must be PIM-eligible | BLOCKED |
| M365-OFF-001 | offboarding | Involuntary leaver who is synced from AD DS and under legal hold: disable at source, revoke, hold, transfer, wipe corporate laptop / retire BYOD, then remove licenses | APPROVED |
| M365-OFF-002 | offboarding | Draft runbook that revokes before disabling, removes licenses before retention, wipes a personal phone and misses a laptop | REJECTED |
| M365-ACC-001 | access | AADSTS53000 from CA004: Windows 10 below minimum and BitLocker off, past the grace period | ROOT_CAUSE_IDENTIFIED |
| M365-ACC-002 | access | Intune enrollment fails: license group disables the Entra ID P1 prerequisite | ROOT_CAUSE_IDENTIFIED |
| M365-ACC-003 | access | Mailbox not found: migration-staging group disables the Exchange plan (the incident was already restored) | ROOT_CAUSE_IDENTIFIED |
| M365-ACC-004 | access | AADSTS50079: no MFA method left; verify out of band and issue a TAP | ROOT_CAUSE_IDENTIFIED |
| M365-SH-001 | service health | Six Teams reports during active incident TM-LAB-0001; one reporter separately unlicensed | KNOWN_SERVICE_INCIDENT |
| M365-SH-002 | service health | Exchange reports after the incident was restored; stale device check-in | LOCAL_ISSUE |
| M365-BG-001 | break-glass review | Two cloud-only FIDO2 permanent-GA accounts, CA exclusions, alerting, custody; overdue test; standing GA on an admin | COMPLIANT_WITH_WARNINGS |
| M365-BG-002 | break-glass usage | Use during an MFA outage, with ticket, rotation within 24h and audit review | POST_USE_COMPLETE |

## Rule families

| Prefix | Covers |
|---|---|
| `SCHEMA-*`, `SAFE-*`, `SYN-*` | Strict JSON (duplicate keys, NaN), known keys and references, no secret or execution keys, lab GUIDs, `.example` domains and no URLs. Any violation gives exit 2. |
| `LIC-*` | Workload to service-plan resolution (any-of groups), plan prerequisites, plans disabled by groups, seat exhaustion, usageLocation |
| `DEV-*` | Lab model of Intune compliance: min OS, BitLocker, Secure Boot, Defender, firewall, jailbreak/root, passcode, encryption, 30-day validity period, grace period, unmanaged devices |
| `AUTH-*`, `CA-*` | AADSTS 50053 / 50057 / 50076 / 50079 / 50126 / 53000 / 53003 mapped to diagnosis and remediation; unmapped codes fail closed |
| `SH-*` | Correlates reports with active service-health issues (known incident vs advisory vs recently restored vs local), escalation threshold |
| `OFF-*` | Required leaver steps, source of authority for synced users, disable-then-revoke ordering, retention before license removal, BYOD retire vs corporate wipe, audit export last |
| `BG-*`, `PRIV-*` | Break-glass standard and post-use obligations, standing Global Administrator |
| `AUD-*` | Required audit-evidence categories per scenario type, HR/change approval reference |

The licensing dependency graph is a simplified **lab model** that uses Microsoft plan names for
realism. It is not a statement of Microsoft licensing terms. Check current Microsoft documentation
before relying on it.

## Usage

```bash
python3 identity/m365/m365_ops.py                                   # all scenarios
python3 identity/m365/m365_ops.py identity/m365/scenarios/M365-ACC-001-noncompliant-laptop.json
python3 identity/m365/m365_ops.py --json-out r.json --md-out r.md --quiet
python3 -m unittest discover -s identity/m365/tests -v
python3 evidence/m365/generate_evidence.py                          # see evidence/m365/README.md
```

Exit codes: `0` every scenario matched its expectation, `1` at least one mismatch, `2` the input is
malformed, unsafe or not synthetic (fail-closed, nothing evaluated).
