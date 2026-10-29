# Host operations -- evidence

> **Offline / example.** Nothing in this directory came from a real AWS account or host. Files in
> `examples/` are hand-written **EXAMPLE DATA** showing the shape of patch evidence; files in `runs/`
> are real outputs of local, offline commands (parsers, fixture tests, linters, `systemd-analyze`
> on staged copies) and nothing else.

## examples/ (EXAMPLE DATA)

| File | Shape of |
|---|---|
| `describe-instance-patch-states.canary.example.json` | `aws ssm describe-instance-patch-states-for-patch-group` after the canary install |
| `list-compliance-summaries.example.json` | `aws ssm list-compliance-summaries` (Patch) between canary and wave1 -- the `compliance-summary` gate evidence |
| `describe-maintenance-window-executions.example.json` | window execution history incl. a `MaxErrors=0` stop |
| `run-patch-baseline-output.example.txt` | abridged `AWS-RunPatchBaseline` Install output |
| `canary-signoff.example.md` | the `canary-signoff` gate evidence record |
| `rollback-drill.example.md` | a rollback entry (ROLLBACK.md "Afterwards") |

`check_examples.py` enforces: filename contains `.example.`, content carries the `EXAMPLE DATA`
marker (JSON: top-level `_exampleData`), and no 12-digit account ids or real-format
`i-`/`pb-`/`mw-`/`snap-`/`ami-`/`vol-` ids.

## runs/ (offline evidence)

```bash
python3 evidence/host-operations/generate_evidence.py            # -> runs/local-offline-<UTC>/
python3 evidence/host-operations/generate_evidence.py --verify evidence/host-operations/runs/<RUN_LABEL>
```

Layout follows the lab's other offline bundles (e.g. the Entra CA run): `SUMMARY.json`,
`SUMMARY.md`, `COMMANDS.tsv` (10 columns), `logs/NN_<step>.log`, `SHA256SUMS`. Each run records:
both unit-test suites, patch fixture drift, the example-marker check, the manifest inspector on the
example manifest and on all 42 patch fixtures with expected exit codes, the unit scorer on all 27
hardening fixture cases, shipped units per drop-in layer and per distro target, the compatibility
matrix render, `cfn-lint` / `yamllint` / `shellcheck` (SKIPPED if not installed, never PASS), and
`systemd-analyze --user verify` + `security --offline=true` on temporary staged copies with a
side-by-side exposure comparison.

`git.commitSha` is the commit whose inputs were checked; the run is committed on top of it.
`--verify` re-checks `SHA256SUMS` and that every input hash still matches the working tree.
