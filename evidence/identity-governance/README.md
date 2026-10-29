# Identity governance -- offline evidence

> **Offline / synthetic.** Every run here exercises local Microsoft Graph-shaped JSON fixtures in this
> repository. No Microsoft Entra ID tenant, Microsoft Graph API, AWS account or credential is used, and
> nothing here describes or claims the state of any tenant or account.

Generate a run (from the repo root, on a clean, committed tree):

```bash
python3 evidence/identity-governance/generate_evidence.py            # -> evidence/identity-governance/runs/local-offline-<UTC>/
python3 evidence/identity-governance/generate_evidence.py --verify evidence/identity-governance/runs/<RUN_LABEL>
```

```
evidence/identity-governance/runs/<RUN_LABEL>/
  SUMMARY.json            commit SHA, branch, UTC timestamps, SHA-256 of every input file (inputHashes),
                          each command with expected + actual exit code, per-scenario inventory summary
  SUMMARY.md              human-readable rendering
  reports/                inventory-<scenario>.{json,md,csv} (privileged role inventory + findings) for every
                          fixture scenario; access-review-baseline.{json,md}
  COMMANDS.tsv            seq, step_id, kind, expected_exit, exit_code, result, started_utc, duration_ms, log, command
  logs/NN_<step>.log      full stdout/stderr per command with exit-code footer
  SHA256SUMS              SHA-256 of every other file in the run directory
```

Commands recorded per run: Python version, fixture drift check, the `identity/governance/tests` unittest
suite, `inventory.py` on every scenario with its expected exit code (`0` pass, `1` findings, `2`
fail-closed on 401/403, exhausted throttling, paging loop or malformed page), and `access_review.py`
on the baseline decisions (expected `1`: seeded AR findings).

`git.commitSha` is the commit whose `identity/governance` and `docs/federation` content was exercised;
the evidence is committed on top of it. `--verify` re-checks `SHA256SUMS` and that every recorded input
hash still matches the working tree.
