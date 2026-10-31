# How backups and database recovery work

## Level 1: Everyday explanation

A backup is a separate copy of information kept so it can be recovered. A restore puts saved information back into a usable system. Like a spare key, a backup is valuable only if it actually works when needed. [Glossary](glossary.md#backup) and [Wikipedia introduction to backups](https://en.wikipedia.org/wiki/Backup).

PostgreSQL is software that stores organized information in related tables. See [PostgreSQL backup documentation](https://www.postgresql.org/docs/current/backup.html). A crashed database does not always need backup restoration: it may recover from its transaction records. This repository has separate restore and crash-recovery exercises.

## Level 2: Operational explanation

A company might need yesterday's customer records after an accidental deletion. Recovery Point Objective (RPO) sets the tolerable amount of lost recent work; Recovery Time Objective (RTO) sets the target time to restore service. They are targets, not measured guarantees.

Following a cyberattack, recovery also requires investigation, containment, clean systems, and confidence that backups are trustworthy. This lab does not demonstrate end-to-end cyberattack recovery.

## Level 3: Engineering explanation

The existing harness creates synthetic account and ledger data, exports it with pg_dump, restores it, and compares row counts and fingerprints. It tests invalid input and rejected operations as well as success. A negative test passes only when failure occurs for the expected reason. [Harness reference](../../tests/integration/README.md).

## Practical exercise: inspect existing restore evidence

Learning objective: distinguish a reported PASS from evidence checked by a verifier. Allow roughly 15–25 minutes; beginner with command-line help. Requires Python 3, a checkout of this documentation branch, and read access. No cloud credentials or database server are needed for this inspection.

From the repository root:

```bash
python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-offline-40741329107-1
```

Read the output and process exit status. A zero status means the verifier accepted the committed bundle within its checks; it does not rerun the database or recover an application. The archived dump files are not included, so this does not verify their availability. See [original evidence index](../../evidence/postgres/runs/INDEX.md).

If verification fails, inspect the named missing file, checksum, or case before trusting the result. Do not edit evidence to make it pass. No cleanup is required because this command reads the bundle.

## Level 4: Expert reference and restrictions

Inspect [run_restore_scenario.sh](../../tests/integration/postgres/run_restore_scenario.sh), [verifier](../../tests/integration/postgres/verify_evidence.py), and [test expectations](../../tests/integration/postgres/expectations.tsv). Full execution requires compatible PostgreSQL client/server tools and a non-root user. Read the harness before running it; use an isolated disposable lab with synthetic data, never production connection variables.

Known limitations: this exercise is not a full-service recovery, cross-region failover, ransomware recovery, or production RTO/RPO demonstration. For an outage walkthrough see [incident response](incident.md). Agents must preserve the original run identity and distinguish re-verifying a bundle from executing a new restore.
