# Tutorials: offline exercises you can run today

Each tutorial below uses only files already in this repository. None needs a cloud account, a Microsoft tenant, or credentials, and none changes anything outside your checkout. They are ordered from beginner to engineer. Run every command from the repository root.

**Execution record.** Every command on this page was run on 2026-11-03 against main `30e0a832e16ca1fe44cf7bbb0b8fc7c0abf469b6` on a Linux workstation with Python 3.13.5 and Node 24.22.1. The observed results are quoted. That is a local run of fictional or recorded data. It is not CI, a deployment, or production verification. CI uses Python 3.12 and Node 22, so versions may differ.

## 1. Find access problems in a fictional directory (beginner, about 15 minutes)

Needs Python 3. Explained in [Control employee permissions](identity.md).

```bash
python3 identity/governance/inventory.py --scenario baseline --as-of 2026-10-28T12:00:00Z
python3 identity/governance/inventory.py --scenario findings --as-of 2026-10-28T12:00:00Z
```

Expected and observed: the first exits 0; the second exits 1 because the fixture seeds high and medium findings. Exit 2 would mean an input failure. Compare the finding IDs with the [rules table](../../identity/governance/README.md#rules). Nothing to clean up.

## 2. Read a saved health observation (beginner, about 10 minutes)

Needs Python 3. Explained in [Investigate an outage](incident.md).

```bash
python3 observability/run_healthcheck.py evaluate observability/fixtures/healthy.json --now 2026-10-28T12:01:00Z
```

Observed: structured log lines ending in `"overall":"HEALTHY"` and exit 0. The fixed `--now` keeps the fixture fresh. Do not use `collect` mode here: it makes real network requests.

## 3. Check a recorded database restore (operator, about 10 minutes)

Needs Python 3. Explained in [Backups and recovery](recovery.md).

```bash
python3 tests/integration/postgres/verify_evidence.py evidence/postgres/runs/ci-offline-40741329107-1
```

Observed: `cases=38 positive=11 negative=6 rows=38 problems=0 -> VERIFIED`, exit 0, and `artifacts: NOT CHECKED` because the dump files live in the CI artifact, not the repository. This checks the recorded bundle. It does not restore a database.

**Failure injection.** Copy the bundle outside the repository, damage the copy, and confirm the verifier notices. Never edit the original evidence.

```bash
mkdir -p /tmp/restore-tamper && cp -r evidence/postgres/runs/ci-offline-40741329107-1 /tmp/restore-tamper/run
echo x >> /tmp/restore-tamper/run/COMMANDS.tsv
python3 tests/integration/postgres/verify_evidence.py /tmp/restore-tamper/run
```

Observed: `ERROR hash: mismatch: COMMANDS.tsv`, `problems=2 -> REJECTED`, exit 1. Recovery: delete the copy with `rm -r /tmp/restore-tamper`. The original bundle still verifies.

## 4. Verify a recorded incident timeline (operator, about 5 minutes)

Needs Python 3. Explained in [Investigate an outage](incident.md).

```bash
python3 scenarios/incident/lib/timeline.py --verify evidence/incident/runs/local-20261029T000545Z
```

Observed: `VERIFY PASS (SIMULATION run local-20261029T000545Z)`. The same passes for `local-20261028T181818Z`. Pass the run directory, not the `.console` directory next to it: the `.console` path fails with `FileNotFoundError ... events.jsonl`.

The live crash demonstration (`scenarios/incident/run_incident_demo.sh`) was **not run** for this page. It needs PostgreSQL server binaries (`initdb`, `pg_ctl`, `postgres`), and the workstation had only client tools. Read the [simulation README](../../scenarios/incident/README.md) in full first: it deliberately crashes its lab database.

## 5. Run module test suites (engineer, 5–20 minutes)

| Module | Command | Needs | Observed 2026-11-03 |
|---|---|---|---|
| Entra Conditional Access validator | `python3 -m unittest discover -s tests/entra -v` | Python 3 | 25 tests OK |
| Vendor API mock (SIMULATION) | `cd integrations/vendor-mock && python3 -m unittest discover -s tests -t . -v` | Python 3 | 45 tests OK |
| AWS CDK static checks | `cd infra/aws-cdk && npm ci && npx jest` | Node 20+, network for npm | 3 suites, 37 tests passed; nothing deployed |
| Whole offline regression | `bash scripts/validate-all.sh --python-only` | Python 3.10+, OpenSSL 3, Git, Bash | `validate-all: PASS (34 steps)` |

`npm ci` writes `infra/aws-cdk/node_modules`, which Git ignores. Remove it when you are done if you need the disk space. Never run `cdk deploy`; no page in this knowledge base authorizes deployment.

## 6. Follow the twelve-week guide (all levels)

The [twelve-week assimilation guide](../../learning/README.md) has daily exercises, failure injection, answer notes, interview questions and explicit PENDING sections. It was written while modules were still open pull requests. Read [the twelve-week guide on main](../../learning/CURRENT.md) first for which of its paths and branches have moved.

## 7. Build this knowledge base (contributor)

See [Reproduce the portal](development.md#reproduce-the-portal). Problems are covered in [Troubleshooting](troubleshooting.md).

## Not yet available

- No tutorial deploys to AWS or connects to Microsoft Graph. Those are out of scope and are not planned for this documentation.
- No tutorial runs a real RDS or AWS Backup restore, so there are no measured recovery-time or data-loss figures.
- An executable Terraform walkthrough for `infra/orgs/terraform` has not been written.
