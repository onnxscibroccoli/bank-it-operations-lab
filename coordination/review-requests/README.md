# External review requests

Each file stands on its own. It is written for a reviewer who has no access to this repo's internals, and it asks for a verdict on **one exact SHA**.
Nothing in these files is secret. They are safe to paste into an external reviewer, for example ChatGPT.

| Request | PR | Exact SHA | Status |
|---|---|---|---|
| [PR-14-postgres-harness-v2.md](PR-14-postgres-harness-v2.md) | [#14](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/14): independent review notes, incl. PostgreSQL harness v2 verification | `eb8d259588f2d1ba8a8787cf2c37044617cbcbdb` | prepared, not yet sent; verdict pending |
| [PR-26-acceptance-vertical-slice.md](PR-26-acceptance-vertical-slice.md) | [#26](https://github.com/onnxscibroccoli/bank-it-operations-lab/pull/26): acceptance vertical slice | `181bcdd1420d699c37aa928b636b9332aca83e57` | prepared, not yet sent; **prior external review PR #27 = CHANGES REQUIRED (C1–C5)**, so this is a second opinion |

Rules:
- A verdict counts only for the SHA named in the request.
- If the PR head moves, the request must be regenerated.
- Record each verdict, with the reviewer, the date and the SHA, in `coordination/tasks.json` → `review_requests`.
