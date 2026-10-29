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
| 2026-10-28 21:56 | `5a75d9ca742e28d8f0a18b590b1bfecb5f7b2b03` | candidate `5a75d9ca742e28d8f0a18b590b1bfecb5f7b2b03` | Ian 21:50 alignment. **Self-pin**: gate_sha = the candidate, with no independent review (PR #32 D3). Superseded |
| 2026-10-28 ~22:35 | `48660b725dbf51b51a38d71fcd0150de56214496` | candidate `52e362ead6d4226eb5d0cd177851a19b5a20c344` | PR #32 repairs. The gate commit is the candidate's parent, not the candidate. `independent_review: null`, so the gate reports **TRUSTED GATE UNVERIFIED** and every run is NOT ELIGIBLE until a qualifying review of `48660b725dbf51b51a38d71fcd0150de56214496` is recorded here |

**D3 (PR #32):** a hash match is not trust. The gate is trusted only when `gate_sha` is not the candidate and `independent_review` names an APPROVED GitHub review on `gate_sha` by an allow-listed, write-permitted non-author (verified at runtime by `verify_trusted_gate.py --check-pin`). This branch is **not protected**: it should be (UA-3), because the shared agent account can write it.
