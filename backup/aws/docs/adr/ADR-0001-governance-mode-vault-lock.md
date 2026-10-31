# ADR-0001: Vault Lock in GOVERNANCE mode only (no ChangeableForDays)

Status: accepted for the lab reference.

Context: AWS Backup Vault Lock has two modes. COMPLIANCE mode (set by `ChangeableForDays`, minimum 3 days of grace) becomes
immutable after the grace time: nobody, including AWS, can remove the lock or delete the vault while it holds recovery
points. GOVERNANCE mode can be removed by principals with sufficient IAM permissions.

Decision: both vaults use GOVERNANCE mode with MinRetentionDays 30 / MaxRetentionDays 400. `lockedVault()` throws for any
other mode, `validatePolicy` rejects COMPLIANCE and stray `changeable_for_days`, and `vaultViolations` flags
`ChangeableForDays` in any template. An accidental deployment of this lab therefore never creates an irreversible lock.

Consequences: GOVERNANCE plus the deny-except-break-glass vault access policy protects against routine deletion but not
against a compromised break-glass principal. A production bank vault that needs SEC 17a-4 / FINRA-style WORM should move to
COMPLIANCE mode through a separate, approved change (see `docs/runbooks/aws-backup/RETENTION_AND_DELETION.md`).
