# tools/acceptance: allowlisted acceptance check runner

Stdlib-only Python, offline, credential-free. It runs the checks in the checked-in
[`checks.json`](checks.json) and writes an evidence bundle. The existing shared validator,
[`evidence/shared/validate_evidence.py`](../../evidence/shared/validate_evidence.py), then
verifies that bundle (`hashes` and `commands --format postgres-10col`). This runner does not
replace that validator. It produces bundles in the layout the validator already understands.

    python3 tools/acceptance/runner.py                      # all checks -> tools/acceptance/runs/local-<UTC>/
    python3 tools/acceptance/runner.py --only python-version --label my-run
    python3 -m unittest discover -s tools/acceptance/tests -v

Exit codes: `0` means every check passed and the bundle validated. `1` means a check failed,
timed out, or failed validation. `2` means the runner refused to start (a bad or
non-allowlisted definition, a path escape, or an uncommitted definition), so nothing ran.

## Bundle layout (`tools/acceptance/runs/<label>/`, gitignored)

| File | Contents |
|---|---|
| `COMMANDS.tsv` | The 10-column layout (`seq step_id kind expected_exit exit_code result started_utc duration_ms log command`) |
| `logs/NN_<id>.log` | argv, cwd, UTC start/end, tool versions, stdout, per-stage stderr, per-stage exit codes, and a final `# exit_code=N ...` trailer |
| `artifacts/<id>/...` | Copies of the declared artifacts. Only regular files inside the repo are copied, and each copy's sha256 is recorded in `RUN.json` |
| `RUN.json` | Run metadata: runner sha256, host and Python, source state (git HEAD, branch, dirty flag, porcelain status), definition sha256 and provenance (tracked/clean), and per-check argv or pipeline, timestamps, exit codes, `timed_out`, and tool versions |
| `SHA256SUMS` | sha256sum(1) over every file above |
| `VALIDATION.log` | Shared validator output. It is written after `SHA256SUMS`, so the hashes don't cover it |

## Safety rules (enforced in `runner.py`, covered in `tests/test_runner.py`)

- **Checks come only from the definition file. They are argv arrays with no shell.** `argv[0]`
  must be a bare name in `ALLOWED_PROGRAMS`: `python3 git sha256sum grep sort head tail wc diff cat true false`.
  Shells and command-runners (`bash`, `sh`, `env`, `xargs`, ...) and paths such as `/usr/bin/x`
  are refused. Unknown keys (`shell`, `command`, ...) are refused too.
- **The definition must be committed.** By default the CLI only runs a definition that lives
  under `tools/acceptance/`, is tracked by git, and is unchanged from HEAD.
  `--allow-uncommitted-checks` overrides this, and `RUN.json` records that it was used.
- **Command output is never executed or trusted.** Captured lines that start with `#` get a
  `| ` prefix, so output cannot forge a log trailer.
- **Timeouts are bounded.** `timeout_s` is required and must be at most 1800. Each check runs
  in its own process group. On timeout the group gets SIGTERM, then SIGKILL 2 s later, and
  the check exits with `124`.
- **Pipelines use pipefail semantics.** The exit code is the rightmost non-zero stage status,
  and every stage's status is recorded. A signal-killed stage reports `128+N`.
- **Paths are confined.** cwd, artifacts, and the run label are resolved relative to their
  root. Absolute paths, `~`, `\`, NUL, `..` components, and a symlink at *any* component are
  rejected, and the resolved path must stay inside the root. New files are created with
  `O_EXCL|O_NOFOLLOW`.
- **The environment is scrubbed.** AWS/Azure/GitHub credential variables are removed and AWS
  config points at `/dev/null`, the same approach `scripts/validate-all.sh` takes.
- **Validation fails closed.** If the shared validator is missing or reports errors, the run fails.
