# schemas/acceptance: machine-readable acceptance contract

| File | Purpose |
|---|---|
| `acceptance-requirements.schema.json` | JSON Schema (draft 2020-12) for an acceptance document: stable requirement IDs, scope, rationale, source (`job_description` / `vendor_guidance` / `project_decision` / `standard` + reference), exact 40-hex tested commit, check command + expected result + execution state + observation, evidence refs, assumptions, exclusions, verification method, result, exception disposition, independent reviewer findings. `evidence_refs[].sha256` is a `$ref` into `evidence/shared/evidence-manifest.schema.json`. |
| `check_acceptance.py` | Contract checks. **Not a new validator:** structure is checked with the shared stdlib checker `evidence/shared/validate_evidence.py` (`_check`), and every evidence ref is resolved through the shared `manifest` and `hashes` subcommands. It adds only relationship rules and the aggregate decision. |

Tests and SYNTHETIC fixtures live in `tests/acceptance-contract/`.

    python3 schemas/acceptance/check_acceptance.py DOC.json [--repo-root DIR] [--json]
    python3 -m unittest discover -s tests/acceptance-contract -v
    python3 tests/acceptance-contract/make_fixtures.py --check

## Evidence refs
`{manifest, artifact, sha256}`. A ref resolves only if all of these hold:
1. the `MANIFEST.json` exists and passes `validate_evidence.py manifest`, and sits in its `bundle.root`;
2. the bundle hashes file passes `validate_evidence.py hashes`;
3. the artifact is inside the bundle root, exists, matches `sha256`, and is listed with that hash in the hashes file;
4. the manifest has a `git-commit` anchor equal to the document's `tested_source_commit`.

## Rules (error code → rule)
| Code | Rule |
|---|---|
| `E_SCHEMA` | Structure, enums, patterns (40-hex commit, ID format), required fields, unknown keys, booleans and real dates. |
| `E_RESULT_NEEDS_EVIDENCE` | PASS or FAIL with no evidence refs. |
| `E_EVIDENCE_UNRESOLVED` / `_MANIFEST_INVALID` / `_BUNDLE_HASHES` / `_HASH_MISMATCH` / `_NOT_COVERED` / `_COMMIT_MISMATCH` | Evidence ref does not resolve as above. |
| `E_RESULT_NOT_EXECUTED` | `skipped` or `unavailable` must be UNKNOWN; `not_run` must be UNKNOWN or NOT_APPLICABLE. |
| `E_RESULT_NO_OBSERVATION` / `E_RESULT_INCONSISTENT` | `executed` needs `observed`; PASS iff observed exit (and `output_contains`, if set) meets the expectation, FAIL otherwise; NOT_APPLICABLE cannot have been executed. |
| `E_RATIONALE_REQUIRED` | NOT_APPLICABLE and UNKNOWN need a non-blank `result_rationale`. |
| `E_EXCEPTION_MALFORMED` | Exception only on FAIL/UNKNOWN; `expires_on` required (except `rejected`) and after `approved_on`; `compensating_control` text for that disposition; approver ≠ recorder. |
| `E_REVIEWER_NOT_INDEPENDENT` / `E_REVIEW_COMMIT_MISMATCH` | Reviewer ≠ recorder; reviewed commit = tested commit. |
| `E_COMMIT_MISMATCH` / `E_DUPLICATE_ID` | Requirement commit = document commit; IDs unique. |

## Aggregate decision (valid documents only, fail closed)
`BLOCKED` (exit 4) if any FAIL, any required UNKNOWN, a required PASS without an independent `concur` or with a `dispute`, or no requirements. Exceptions are recorded for the human decision but never unblock. Otherwise `AUTOMATIC_TECHNICAL_ACCEPTANCE` (exit 0). Invalid documents: `INVALID` (exit 1). This is a lab gate, not an audit, certification or production sign-off.
