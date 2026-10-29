# HISTORICAL / KNOWN-INVALID (harness v1)

This box-local offline run (sandbox, PostgreSQL 16 from conda-forge, 2026-10-28 00:10 EDT) was produced by harness v1. That version
treated **any** non-zero exit of a negative step as the expected failure, and it chained setup and fault in one `bash -c ... && ...`.
So its PASS verdicts could not tell the difference between detecting a fault and a setup failure, a version mismatch, or a missing tool.

What the logs actually show (re-read on 2026-10-28; the PR #3 review reached the same conclusion): all six negatives failed with the intended error text.
N04's log shows the FK message, but SQLSTATE was not captured because v1 did not use `VERBOSITY=verbose`. This run is therefore **not known to be wrong**,
but it is **not valid evidence** under the current rules: no declared reasons, no setup/fault separation, no required-case count, and
`ENVIRONMENT.txt` records `git_sha=7f50348` (base `main`) rather than the script that ran.
Superseded by the harness-v2 runs listed in `../INDEX.md`. The files here are left byte-identical; see `STATUS.json`.
