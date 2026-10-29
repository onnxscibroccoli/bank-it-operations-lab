# M365 / endpoint operations: offline evidence

> **Offline and synthetic.** Every run here evaluates the local JSON scenarios in `identity/m365`. No Microsoft 365,
> Entra ID, Intune or Exchange Online tenant, Microsoft Graph API or credential is used. Nothing is executed against
> any tenant (`mutationsExecuted: 0`), and nothing here describes or claims the state of any tenant.

Generate a run from the repo root on a clean, committed tree:

```bash
python3 evidence/m365/generate_evidence.py            # -> evidence/m365/runs/local-offline-<UTC>/
python3 evidence/m365/generate_evidence.py --verify evidence/m365/runs/<RUN_LABEL>
```

```
evidence/m365/runs/<RUN_LABEL>/
  SUMMARY.json            commit SHA, branch, UTC timestamps, SHA-256 of every identity/m365 input (inputHashes),
                          each command with expected and actual exit code, per-scenario verdicts and findings
  SUMMARY.md              human-readable rendering
  validation-report.json  full engine report: findings, PLAN_ONLY steps and audit-evidence coverage per scenario
  validation-report.md
  COMMANDS.tsv            seq, step_id, kind, expected_exit, exit_code, result, started_utc, duration_ms, log, command
  logs/NN_<step>.log      full stdout/stderr per command, with an exit-code footer
  SHA256SUMS              SHA-256 of every other file in the run directory
```

Each run records these commands:
- the Python version;
- the `identity/m365/tests` unittest suite;
- the engine over every scenario (expected exit 0);
- the engine on every negative fixture with its expected exit code (`mismatch-` 1, `malformed-` 2). This shows that the
  expectation check and the fail-closed SCHEMA/SAFE/SYN guards actually fire.

`git.commitSha` is the commit whose `identity/m365` content was evaluated. The evidence itself is committed on top of it.
`--verify` re-checks `SHA256SUMS` and confirms that every recorded input hash still matches the working tree.

The audit evidence that each scenario requires (approvals, identity changes, session revocation, device actions,
mailbox retention, license removal, sign-in logs, service-health snapshots, break-glass test records) is listed per
scenario in `validation-report.md` under "Audit evidence".
