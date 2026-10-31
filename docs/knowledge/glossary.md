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

## Additional terminology used in the reading guides

These brief definitions are also used beside source documents. External references remain on the relevant technical pages; missing individual Wikipedia references are not fabricated.

### AD DS

Active Directory Domain Services: a directory used to manage Windows identities and resources.

### ADR

Architecture Decision Record: the context, choice, and consequences of a design decision.

### API

An interface through which programs request operations or information.

### Attestation

A statement made by an identified party about a specific claim.

### Authentication

Checking a claimed identity.

### Authorization

Deciding which actions an identified person or program may perform.

### Backup

A separate copy retained for recovery.

### CAB

Change Advisory Board: a group used to review proposed operational changes.

### CDK

A software toolkit used to define infrastructure in programming languages.

### CI

Continuous Integration: automated checks of proposed changes.

### Canary

A small first group used to observe a change before wider rollout.

### Case study

An explanation of a project’s purpose, design, and evidence.

### CloudFormation

AWS’s template-based resource provisioning service.

### Conditional Access

A policy decision based on signals such as identity, device, and sign-in conditions.

### DNS

Domain Name System: translates names into resource-location information.

### Delegated administrator

An account assigned administration responsibilities for a supported service.

### Drop-in

An additional configuration file that modifies a service definition.

### Endpoint

A user or service device connected to an organization’s systems.

### Escalation

Involving the people with the authority or skills needed to resolve an issue.

### Evidence

Recorded information supporting a specific claim within a stated scope.

### Fail closed

Refuse the permissive outcome when required checks are missing or fail.

### Federation

A trust arrangement that lets one system rely on another system’s identity assertions.

### Fingerprint

A calculated summary used here to compare the lab data before and after restoration.

### Fixture

Controlled example data used to make a test repeatable.

### GPO

Group Policy Object: a set of Windows policy settings.

### Hardening

Reducing unnecessary permissions, exposure, and risky configuration.

### Hybrid identity

Identity management spanning local directory systems and cloud services.

### IAM

Identity and Access Management: controls for who may act on resources.

### Incident

An event that disrupts or threatens expected service.

### Intune

Microsoft’s device and application management service.

### KMS

AWS’s service for managing cryptographic keys.

### Log

A recorded event with context for later inspection.

### M365

Microsoft 365, a collection of productivity and administration services.

### MTTD

Mean time to detect across incidents; a single run supplies one detection interval.

### MTTR

A mean recovery or repair interval whose exact definition must be stated; this lab records its own restoration interval.

### Markdown

A text format for readable documents with headings, links, lists, and code.

### Metadata

Structured information describing a page, such as its topic and verification scope.

### Metric

A numerical measurement such as elapsed time or free space.

### Mock

A controlled substitute for a real component used in a test or demonstration.

### Negative test

A check that intentionally invalid behavior is rejected for the expected reason.

### PIM

Privileged Identity Management controls eligibility and time-limited activation of powerful roles.

### Patch ring

A group of systems assigned a particular rollout stage.

### Plan-only

Produces proposed actions without executing those actions.

### PostgreSQL

Database software that organizes related information in tables.

### Prerequisite

Knowledge, software, permissions, or infrastructure needed before a task.

### Probe

A limited request used to check a particular service behavior.

### RACI

A responsibility table identifying who is responsible, accountable, consulted, and informed.

### RBAC

Role-based access control assigns permissions through roles.

### RDS

AWS’s managed relational database service.

### RPO

Recovery Point Objective: the target amount of recent work that may be lost.

### RTO

Recovery Time Objective: the target time to restore required service.

### Reference

A source used to inspect or learn about a claim.

### Restore

Reconstruct usable information from a saved copy.

### Rollback

A deliberate return to a previous known state.

### S3

AWS object storage for files and other objects.

### SAML

A format and protocol for passing authentication assertions between systems.

### SCIM

A protocol for creating, updating, and removing identity records across systems.

### SCP

Service Control Policy: an AWS Organizations guardrail that limits available permissions rather than granting them.

### SLA

Service Level Agreement: an agreed service obligation with defined scope.

### SSM

AWS Systems Manager, including tools for managed-host operations.

### Simulation

A controlled example that does not establish production behavior.

### Static site

Prepared web files served without an application backend.

### Terraform

A tool that describes and manages infrastructure through configuration.

### Transaction

A group of database changes treated as a unit.

### VPC

A logically isolated cloud network.

### Vault Lock

A retention control on backup recovery points; its behavior depends on mode and configuration.

### Worktree

An additional checkout sharing a Git repository’s history.

### systemd

A Linux service manager used to start and supervise processes.
