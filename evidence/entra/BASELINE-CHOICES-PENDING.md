# Entra Conditional Access baseline choices: PENDING owner confirmation

> These are kept here, outside `identity/entra/`, because files in that directory are hash-pinned inputs of the committed
> Entra evidence run (`evidence/entra/generate_evidence.py` HASHED_TREES). Editing `identity/entra/README.md` would invalidate that
> run, and earlier evidence is never overwritten.

These choices are encoded in `identity/entra/baseline.json` and `identity/entra/policies/`. They came from PR #4's open questions and **have not
been confirmed by the owner** (user action UA-2 in `coordination/tasks.json`). The validator enforces them as written:
- the risk policies CA005 and CA006 stay **report-only** while `riskPoliciesMustBeReportOnly` is true (BASE-007)
- device compliance (CA004) applies to **All users on All apps** (break-glass excluded)
- the privileged scope for CA003 is the **12 built-in role templates** listed in `identity/entra/baseline.json`

If the owner changes any of them, update `identity/entra/baseline.json` and the policies, then regenerate the fixtures and add a NEW evidence run alongside the existing one.
