# Observability -- offline evidence

> **Offline / synthetic.** Runs here execute the `observability/` unit tests and evaluate the
> committed fixtures with a fixed clock. No network, no cloud API, no production endpoint, and
> no routing change is involved; nothing here describes the state of any real system.

```bash
python3 evidence/observability/generate_evidence.py          # -> evidence/observability/runs/local-offline-<UTC>/
python3 evidence/observability/generate_evidence.py --verify evidence/observability/runs/<RUN_LABEL>
```

```
runs/<RUN_LABEL>/
  SUMMARY.json   commit SHA, branch, UTC timestamps, SHA-256 of every observability/ input,
                 each command with expected + actual exit code, per-fixture outcome
  SUMMARY.md     human-readable rendering
  COMMANDS.tsv   seq, step_id, kind, expected_exit, exit_code, result, started_utc, duration_ms, log, command
  logs/NN_*.log  full stdout/stderr per command (the unit-test log is logs/02_unit_tests.log)
  results/<fixture>.result.json   sample JSON result per fixture
  results/<fixture>.log.jsonl     sample JSON-lines log per fixture
  SHA256SUMS     SHA-256 of every other file in the run directory
```

`git.commitSha` is the commit whose `observability/` content was exercised; the evidence is
committed on top of it. `--verify` re-checks `SHA256SUMS` and that every recorded input hash still
matches the working tree. Child processes get a minimal environment (PATH, locale only).
