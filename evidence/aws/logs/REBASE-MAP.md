# Rebase onto origin/main (history mapping)

The local repo was created with `git init` before the GitHub repo existed, so its history was
unrelated to `origin/main` (7f50348 "Initial commit", README.md only). To give the PR a common
base, the two local commits were replayed with `git rebase --root --onto origin/main` (log 33).
Tree contents of infra/aws-cdk/** and evidence/aws/** are byte-identical; the only tree difference is
the README.md inherited from main.

| Commit | Pre-rebase SHA | Post-rebase SHA |
|---|---|---|
| pre-implementation record | 84e0e1e | f24818b |
| stack, tests, cdk-nag, evidence | 15421c96d7884aa4224716de8cdf761d1e5f758b | 03b93d1c9be34ea03dea4018d1c96166b5be1452 |

Hashes recorded earlier against 15421c9 (archive sha256 5c4202c4…e2aa, SHA256SUMS) refer to the
pre-rebase commit. A local branch `backup/bank-aws-001-pre-rebase` keeps it (not pushed).
