# Bank IT operations lab: twelve-week learning guide

This guide teaches from what the repository **actually delivers**. Every capability it uses is cited to a file
on a branch at an exact commit (`` `<branch>@<sha7>:<path>` ``). Nothing here deploys anything, calls an AWS or Microsoft Graph
API, or uses credentials.

> **Merge state (re-checked 2026-10-28 at 14:24 EDT, R15): nothing is merged.** `main` is still `7f50348` and contains only `README.md`.
> All 22 PRs are **open drafts** targeting `main`. No PR has a human GitHub review.
> Each week tells you which branch to check out. If a PR head moves, re-check the cited paths against the SHA listed here.

## PR snapshot
| PR | Branch | Head | Merge state | Integrated in #7? | Used in weeks |
|---|---|---|---|---|---|
| [#1](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/1) | `bank-aws-001` | `e494bcf` | open draft | **superseded by #5** (`reports/INTEGRATION.md` on #7) | 1-2 |
| [#2](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/2) | `ci-evidence-postgres` | `e7399fb` (was `e610015` in this guide's first version) | open draft; CI green at head | yes (harness v2) | 7-8 |
| [#3](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/3) | `review/pr1-pr2-evidence-audit` | `fb36341` | open draft | yes | 2, 8 |
| [#4](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/4) | `entra-ca-offline` | `d302c99` | open draft | yes | 4-5 |
| [#5](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/5) | `aws-remediation-vpc-rds` | `099479e` | open draft; #14 says **request changes** | yes | 3, 9-10 |
| [#6](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/6) | `orgs-security-refs` | `e5e7f46` | open draft; #14 says **request changes** | **no** (awaiting changes) | 6, 11 |
| [#7](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/7) | `overnight/integration` | `49122f2` (docs-only commit after `afb4127`; the code is identical) | open draft; CI green at head (8/8) | (is the integration branch: #3, #5, #4, #2) | 12 |
| [#8](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/8) | `portfolio-cases` | `7010d05` | open draft | no | not used (portfolio prose, not a lab module) |
| [#9](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/9) | `vendor-mock` | `d6efb82` | open draft | no | 8 |
| [#10](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/10) | `observability` | `3e40e39` | open draft | no | 9 |
| [#11](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/11) | `reports/final-report` | `54d6fbd` | open draft | no | 10, 12 |
| [#12](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/12) | `job-requirements-matrix` | `31b69db` | open draft | no | not used (job matrix, not a lab module) |
| [#13](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/13) | `team-management` | `9dc8f1f` | open draft | no | 8 |
| [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14) | `review/pr3-pr6` | `eb8d259` | open draft (agent review notes, not a sign-off) | no | 3-4, 6, 10-11 |
| [#15](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/15) | `learning-guide` | this branch | open draft | no | n/a |
| [#16](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/16) | `control-mapping` | `3f82697` | open draft | no | 11 |
| [#17](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/17) | `patch-hardening` | `5605b78` | open draft | no | 9 |
| [#18](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/18) | `identity-governance` | `f48e7e3` | open draft | no | 5, 11 |
| [#19](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/19) | `hybrid-operations` | `3397dac` | open draft; no CI | no | 5 (runbooks NOT_EXECUTED) |
| [#20](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/20) | `m365-endpoint` | `1b3c240` | open draft; no CI | no | 5 |
| [#21](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/21) | `backup-dr-aws` | `10da54f` | open draft; no CI | no | 9-10 |
| [#22](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/22) | `incident-demo` | `3f13622` | open draft; no CI | no | 8 |

**Backup/DR is now delivered** as static, credential-free code (#21 `backup-dr-aws@10da54f:backup/aws/**`). Every recovery item is `NOT_EXECUTED` (`evidence/backup/aws-backup-dr/RECOVERY_EXECUTION_STATUS.json`), so a real restore is still PENDING.

## Layout
- `INVENTORY.md`: what is real, what is partial, and what is absent.
- `SETUP.md`: prerequisites, how to check out every branch with `git worktree`, and how to get PostgreSQL without credentials.
- `weeks/week-01.md` … `weeks/week-12.md`:
  - Weeks 1-3: AWS and IaC.
  - Weeks 4-6: identity and governance.
  - Weeks 7-9: resilience and incidents.
  - Weeks 10-12: architecture defense.
- `execution/EXECUTION_LOG.md`: what was **actually run**, with real output and exit codes. Run 1 is E01-E14; run 2 (the reconciliation) is R01-R21.
- `execution/PENDING.md`: everything **not** executed or **not** delivered.
- `exercises/`: scratch helpers, plus `check-citations.py` (R16). They never modify committed evidence.
- `../docs/adr/`: repository-level ADRs, each tied to delivered files and to its PRs' merge state.

## Each week has
Daily exercises, exact commands and prerequisites, expected or observed results, failure injection and recovery, answer notes,
architecture tradeoffs, a fifteen-minute walkthrough, interview questions, and an explicit **PENDING / UNEXECUTED** section.

## Ground rules
1. Run credential-free. Use `exercises/no-aws-env.sh` or the repo's own wrappers.
2. Inject failures only in `/tmp` copies or uncommitted changes that you revert. Never commit mutated evidence.
3. A cited file missing on your checkout is a finding. Do not invent content.
4. Agent review notes (#3, #14) and reports (#7, #11) are inputs to learn from, not approvals.
