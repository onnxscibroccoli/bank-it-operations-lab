# trusted-gate

`gate-manifest.json` is the trusted manifest read by the integration-gate `merge-eligibility` job (R6, PR #30/#31). It is never read from the candidate:

- **`gate_sha`** is the commit whose `scripts/ci` and `.github/acceptance/trusted-config.json` the gate checks out **by SHA** and executes or reads.
- **`files`** holds the sha256 of every verifier file and of `.github/workflows/integration-gate.yml`.
  - The trusted checkout must match them.
  - So must the candidate's copies. A candidate that changes the verifier, the allow-list or the workflow without a matching update here is rejected.

`.github/acceptance/gate-manifest.json` on `main` takes precedence once it exists, after UA-3. Each update is a normal commit here, and the history is kept.

| Date (EDT) | gate_sha | Workflow from | Note |
|---|---|---|---|
| 2026-10-28 ~22:05 | `ce69f84b3333e1d8da99deb03d17f1457464d962` | candidate `e9310f3a94162a5dae31ee1cca9e35452de033ed` | PR #31 repairs (F4/F5/F6/F7/R6) |
