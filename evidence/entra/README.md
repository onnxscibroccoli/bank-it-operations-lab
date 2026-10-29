# Entra Conditional Access -- offline evidence

> **Offline / synthetic.** Every run here validates local JSON fixtures in this repository.
> No Microsoft Entra ID tenant, Microsoft Graph API or credential is used, and nothing here
> describes or claims the state of any tenant.

Generate a run (from the repo root, on a clean, committed tree):

```bash
python3 evidence/entra/generate_evidence.py            # -> evidence/entra/runs/local-offline-<UTC>/
python3 evidence/entra/generate_evidence.py --verify evidence/entra/runs/<RUN_LABEL>
```

```
evidence/entra/runs/<RUN_LABEL>/
  SUMMARY.json            commit SHA, branch, UTC timestamps, SHA-256 of every fixture / validator / test
                          file (inputHashes), each command with expected + actual exit code, per-rule results
  SUMMARY.md              human-readable rendering
  validation-report.json  validator report for identity/entra/policies, PASS/FAIL per rule
  validation-report.md
  COMMANDS.tsv            seq, step_id, kind, expected_exit, exit_code, result, started_utc, duration_ms, log, command
  logs/NN_<step>.log      full stdout/stderr per command with exit-code footer
  SHA256SUMS              SHA-256 of every other file in the run directory
```

Commands recorded per run: Python version, fixture drift check, the `tests/entra` unittest suite,
the validator on `identity/entra/policies` (expected exit 0), and the validator on every fixture in
`tests/entra/fixtures` with its expected exit code (`valid-` 0, `neg-` 1, `malformed-` 2) to show
the negative paths and fail-closed behaviour actually fire.

`git.commitSha` is the commit whose `identity/entra` and `tests/entra` content was validated; the
evidence is committed on top of it. `--verify` re-checks `SHA256SUMS` and that every recorded input
hash still matches the working tree.
