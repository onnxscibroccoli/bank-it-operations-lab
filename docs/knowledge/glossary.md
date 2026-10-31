# Technical glossary in everyday language

A glossary explains terms without requiring you to leave the topic permanently. Definitions are educational; they do not claim the lab implements every concept.

## backup

**Backup.** Plain English: A separate copy kept so information can be recovered.

Technical: A recovery copy captured at a point in time with a defined retention and restoration method.

Example: Keep a copy before a migration.

Operational consideration: Test restores and protect copies from the same failure as the original.

Related learning and terminology: [backup, restore, RPO, and RTO](recovery.md).

Further learning: [official PostgreSQL backup and restore guide](https://www.postgresql.org/docs/current/backup.html), inspected 2026-10-31. Additional per-term references remain under review.

## restore

**Restore.** Plain English: Put saved information back into usable form.

Technical: Reconstruct data or service state from a backup and validate the result.

Example: Load a saved database into an isolated lab.

Operational consideration: A completed command does not prove application correctness.

Related learning and terminology: [backup, restore, RPO, and RTO](recovery.md).

Further learning: [official PostgreSQL backup and restore guide](https://www.postgresql.org/docs/current/backup.html), inspected 2026-10-31. Additional per-term references remain under review.

## rpo

**Recovery Point Objective (RPO).** Plain English: How much recent work you can afford to lose.

Technical: A target maximum tolerable data-loss interval after disruption.

Example: A one-hour target needs an appropriate recovery design.

Operational consideration: A target is not a measured achievement.

Related learning and terminology: [backup, restore, RPO, and RTO](recovery.md).

## rto

**Recovery Time Objective (RTO).** Plain English: How quickly a service should be usable again.

Technical: A target interval for restoring required service after disruption.

Example: Restore an appointment system within the agreed window.

Operational consideration: Measure full service recovery, not just process startup.

Related learning and terminology: [backup, restore, RPO, and RTO](recovery.md).

## authentication

**Authentication.** Plain English: Check who someone is.

Technical: Validate a claimed identity using appropriate authenticators.

Example: Verify a sign-in.

Operational consideration: Authentication alone does not grant permission.

Related learning and terminology: [authentication, authorization, RBAC, and least privilege](identity.md).

## authorization

**Authorization.** Plain English: Decide what someone may do.

Technical: Evaluate policy for an authenticated or otherwise identified actor and requested action.

Example: Allow a clerk to read a record.

Operational consideration: Check permissions for each protected operation.

Related learning and terminology: [authentication, authorization, RBAC, and least privilege](identity.md).

## rbac

**Role-Based Access Control (RBAC).** Plain English: Give access through a job or responsibility role.

Technical: Assign permissions to roles and users to those roles.

Example: Assign scheduling permission to a receptionist role.

Operational consideration: Review role membership and excessive combined permissions.

Related learning and terminology: [authentication, authorization, RBAC, and least privilege](identity.md).

Further learning: [Wikipedia RBAC](https://en.wikipedia.org/wiki/Role-based_access_control) and [Microsoft role reference](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference). Destinations inspected 2026-10-31.

## least-privilege

**Least privilege.** Plain English: Give only the access needed for the task.

Technical: Limit privileges in scope and duration to authorized operational needs.

Example: Grant temporary maintenance access.

Operational consideration: Review old access when responsibilities change.

Related learning and terminology: [authentication, authorization, RBAC, and least privilege](identity.md).

## api

**Application Programming Interface (API).** Plain English: A defined way programs ask each other to do things.

Technical: A contract describing operations, inputs, outputs, and error behavior between software components.

Example: Request a user list from a directory service.

Operational consideration: Apply authentication, authorization, and request limits.

Related learning and terminology: [authentication, authorization, RBAC, and least privilege](identity.md).

## iac

**Infrastructure as Code (IaC).** Plain English: Describe computing resources in reviewable files.

Technical: Manage infrastructure definitions through versioned declarative or programmatic configuration.

Example: Review a cloud network template.

Operational consideration: A template check does not prove live operation.

Related learning and terminology: [infrastructure](infrastructure.md).

## ci

**Continuous Integration (CI).** Plain English: Automatically check changes as they are combined.

Technical: Integrate changes frequently with automated build and validation feedback.

Example: Run documentation tests on a pull request.

Operational consideration: Test execution is not deployment approval.

Related learning and terminology: [development](development.md).

## observability

**Observability.** Plain English: Use system signals to understand what is happening.

Technical: Infer internal behavior from outputs such as logs, metrics, and traces.

Example: Compare failed probes with timestamps.

Operational consideration: Avoid secrets and personal data in logs.

Related learning and terminology: [incident](incident.md).

## incident

**Incident response.** Plain English: Organize the response when something goes wrong.

Technical: Coordinate detection, triage, containment or recovery, and follow-up according to the incident.

Example: Investigate a failed database connection.

Operational consideration: Preserve evidence and avoid uncontrolled interventions.

Related learning and terminology: [incident](incident.md).

## transaction

**Database transaction.** Plain English: A group of changes treated as one unit.

Technical: A database operation group with defined commit, rollback, and isolation behavior.

Example: Transfer an amount between two accounts together.

Operational consideration: Use the database guarantees correctly; application errors remain possible.

Related learning and terminology: [backup, restore, RPO, and RTO](recovery.md).

Further learning: [official PostgreSQL backup and restore guide](https://www.postgresql.org/docs/current/backup.html), inspected 2026-10-31. Additional per-term references remain under review.

## audit

**Audit logging.** Plain English: Keep a record of important actions.

Technical: Record attributable events supporting review and investigation with integrity and retention controls.

Example: Record who approved an access change.

Operational consideration: Logs require access controls and appropriate retention.

Related learning and terminology: [governance](governance.md).

## Coverage limitation

This initial glossary covers fifteen terms. Per-entry authoritative and Wikipedia references, machine-readable individual entries, and the broader terminology inventory remain incomplete. Do not guess article URLs to fill those fields.
