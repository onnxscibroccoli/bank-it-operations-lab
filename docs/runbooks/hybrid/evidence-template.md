# Evidence template (hybrid runbooks)

> **Execution status: NOT_EXECUTED.** This template has not been used yet. No evidence exists for any hybrid runbook.

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Operate local Windows directory services and their connections to cloud identity. Separating directory, name-resolution, policy, and synchronization problems avoids broad changes that obscure the cause.

For example: A user can reach a server by address but not by name, so an operator investigates name resolution before changing account permissions.

Key terms: **AD DS** means active Directory Domain Services: a directory used to manage Windows identities and resources. **DNS** means domain Name System: translates names into resource-location information. **GPO** means group Policy Object: a set of Windows policy settings. **Hybrid identity** means identity management spanning local directory systems and cloud services.

**Before using this reference:** Directory, DNS, policy, and synchronization changes can affect many users. Use the documented permissions and change gates; no live execution is implied.

Start with the [plain-English learning path](../../knowledge/identity.md) or [glossary](../../knowledge/glossary.md). [Current integration and review policy](../../knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->



## Purpose
Make every future execution auditable and repeatable.

## Scope
Any runbook under `docs/runbooks/hybrid/`. Evidence is committed to `evidence/hybrid/<runbook>/<YYYY-MM-DD>/`.

## Preconditions
Gates in [`change-gates.md`](../../../operations/hybrid/change-gates.md) met; no secrets, passwords, tokens, tenant IDs or real personal data in any captured file (redact before commit).

## Procedure
Create `RECORD.md` with:

```markdown
Runbook: <file>            Version/commit: <sha>
Environment: <isolated lab name>     Authorization ref: <ref>
Change ref: <CHG-LAB-xxxx>           Operator: <Pxx>   Reviewer: <Pxx>
Window (America/New_York): <start> – <end>
Execution status: EXECUTED_IN_LAB | PARTIAL | ABORTED

| Step | Command | Expected | Observed | Pass/Fail | Output file |
|------|---------|----------|----------|-----------|-------------|

Deviations:
Rollback used (y/n, why):
Follow-up actions:
```

Store raw command output next to it as `NN-<step>.txt`, plus a `SHA256SUMS` file (`sha256sum * > SHA256SUMS`).

## Verification
`RECORD.md` lists every step, every output file exists, hashes match, and a reviewer has signed off.

## Rollback
If evidence contains a secret: delete the file, rotate the secret, and rewrite history only with the repo owner's approval.

## Evidence
This file is the template; there is no evidence for it.
