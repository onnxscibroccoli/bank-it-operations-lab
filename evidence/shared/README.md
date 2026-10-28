# evidence/shared: cross-bundle evidence checks

Stdlib-only Python checks that work on any evidence bundle in this repo (`evidence/aws/**`, `evidence/postgres/runs/**`).
They are read-only: they never modify evidence. Written for the PR #1 / PR #2 review (`reports/review-pr1-pr2.md`).

| File | Purpose |
|---|---|
| `validate_evidence.py` | `hashes`, `commands`, `postgres-negatives`, `cfn-s3-selflog`, `manifest` subcommands (see `--help`). |
| `evidence-manifest.schema.json` | JSON Schema (draft 2020-12) for an optional per-bundle `MANIFEST.json`. It declares hash coverage, exclusions such as the hashes file itself, how COMMANDS.tsv rows were written, and independent anchors. |
| `negative-expectations.postgres.json` | Required error text for each Postgres negative test, so a step that fails for the wrong reason is reported as a FALSE-PASS. |
| `tests/test_validate_evidence.py` | Unit tests that use temp dirs only: `python3 -m unittest discover -s evidence/shared/tests -v` |

Examples (from the repo root, on a checkout of the relevant branch):

    python3 evidence/shared/validate_evidence.py hashes evidence/aws/SHA256SUMS --base . --cover evidence/aws
    python3 evidence/shared/validate_evidence.py commands evidence/aws/logs/COMMANDS.tsv --format aws-3col
    python3 evidence/shared/validate_evidence.py cfn-s3-selflog evidence/aws/synth/BankItLabSecureStorage.template.json
    python3 evidence/shared/validate_evidence.py hashes evidence/postgres/runs/<label>/SHA256SUMS --cover evidence/postgres/runs/<label>
    python3 evidence/shared/validate_evidence.py commands evidence/postgres/runs/<label>/COMMANDS.tsv --format postgres-10col
    python3 evidence/shared/validate_evidence.py postgres-negatives evidence/postgres/runs/<label>

On `overnight/integration` these checks run in CI through `scripts/validate-all.sh` (`.github/workflows/offline-validation.yml`) and `.github/workflows/aws-cdk.yml` (`cfn-s3-selflog`).
`postgres-negatives` reads COMMANDS.tsv by header name, so it understands both the Postgres harness v1 (10-column) and v2 (12-column) layouts. A run with zero negative steps is an error.
For harness v2 runs, the authoritative verifier is `tests/integration/postgres/verify_evidence.py`. This check is an independent cross-check.
