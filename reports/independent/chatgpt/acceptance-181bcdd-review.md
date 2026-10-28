# Independent ChatGPT acceptance review

Reviewed candidate: `181bcdd1420d699c37aa928b636b9332aca83e57` (PR #26).
Disposition: **CHANGES REQUIRED for acceptance-verifier assurance. No implementation merge approved by this report.**
Scope: acceptance script/verifier/workflow, acceptance packet and coordination manifest; contract/runner/adapter unit suites. Not a full review of all portfolio modules.

## Independently executed checks

Public branch cloned and HEAD verified. No implementation files changed.
- python3 -m unittest discover -s tests/acceptance-contract -v: 19 passed, exit 0.
- python3 -m unittest discover -s tools/acceptance/tests -v: 27 passed, exit 0.
- python3 -m unittest discover -s acceptance/modules/tests -v: 35 passed, exit 0.
- Three adversarial probes below reproduced locally using temporary directories.
GitHub connector independently reported successful PR-triggered runs at this SHA: acceptance 40749387217, aws-cdk 40749387209, postgres-restore-evidence 40749387416, offline-validation 40749387223. These are observed run conclusions, not local re-execution of AWS/Postgres.

## C1 — High: prescribed required-check coverage is not verified

File: scripts/acceptance/verify_results.py, gate()/verify().
A self-consistent bundle with only ARBITRARY / required=yes / PASS / exit=0 and a matching log/hash is accepted:
`verify_results: OK overall=PASS rows=1 errors=0`, exit 0.
No trusted required-check inventory is consulted. Missing AWS/Postgres/Entra/checkout checks are not detected.
This is a completeness gap in the claimed independent verifier, not evidence that the normal run.sh omitted those checks.

Repair: bind a reviewed, versioned requirement inventory to the tested commit; require all mandatory IDs exactly once with valid required flags and states. Check dynamic groups through explicit coverage rules. Test omitted check, downgraded required flag, arbitrary replacement and duplicate IDs. Wire the shared acceptance contract into the final decision rather than merely unit-testing that contract.

## C2 — High: required INFO can produce PASS

Direct reproduction:
`gate([{"check_id":"mandatory","required":"yes","verdict":"INFO"}]) == "PASS"`.
INFO is allowed but excluded from fail/unknown sets. This also affects the separate aggregate logic in run.sh.
Repair: require every mandatory result to be PASS for technical eligibility. INFO may only be advisory. Reject malformed required values and unknown states. Regression-test both aggregation implementations or remove duplicated logic.

## C3 — Medium: JSON and TSV verdicts can disagree undetected

A bundle with TSV AWS-02 PASS/0 and JSON AWS-02 FAIL/1, same ID, overall PASS, plus correctly regenerated hashes is accepted with exit 0.
verify() compares only JSON check IDs with TSV IDs, not the full records. It also does not bind the target SHA to a trusted expected argument.
Repair: validate complete records and summary counters, typed fields and target identity. Prefer one canonical representation with the other generated and checked deterministically. Add independent expected-commit input or equivalent trusted invocation binding.
Resealed hashes prove consistency with digests; they do not establish authenticity or correctness.

## C4 — High integration gap: contract approval is not the executable final gate

reports/ACCEPTANCE.md explicitly lists missing shared-contract evaluation and concurrence records as UNKNOWN, while the separate workflow can report overall PASS. Technical execution and final reviewed acceptance must remain distinct.
Repair: export actual run results into the shared contract; evaluate it; report EXECUTION_PASS versus REVIEW_PENDING/TECHNICALLY_ELIGIBLE separately. Never invent concurrence or require a new paid model API.
Review identity strings alone are not authenticated approval. Bind reviewer evidence through the supported GitHub review/commit provenance.

## C5 — Medium: workflow hardening and validation target

.github/workflows/acceptance.yml uses action tags rather than full commit SHAs and 30-day retention rather than the requested seven days. It tests the PR head, not necessarily the current merged-main candidate.
Repair: verify/pin action SHAs, set seven-day retention unless an explicit alternative is accepted, and validate the final combined candidate against current main before merge. Head testing is useful but insufficient alone for integration proof.

## C6 — Coordination documents retain obsolete approval constraints

coordination/tasks.json still says never merge main from automation and requires an independent human review. Later user authorization permits independently proven automated merges, with final human portfolio acceptance separate.
Coordinator should update this file; ChatGPT has not edited coordinator-owned paths. Do not use obsolete wording to leave workers idle. Updated authority does not override technical blockers C1–C4.

## Small executable reproduction

Run from the reviewed checkout:
```python
import importlib.util, tempfile, pathlib, hashlib, json
s = importlib.util.spec_from_file_location("v", "scripts/acceptance/verify_results.py")
v = importlib.util.module_from_spec(s); s.loader.exec_module(v)
print("required_INFO", v.gate([dict(check_id="mandatory", required="yes", verdict="INFO")]))
for name in ("missing_checks", "json_disagrees"):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d)
        row = dict(check_id="ARBITRARY" if name == "missing_checks" else "AWS-02",
                   required="yes", verdict="PASS", exit_code="0", detail="probe", log="check.log")
        (p/"check.log").write_text("# exit_code: 0\n")
        keys = list(row)
        (p/"results.tsv").write_text("\t".join(keys)+"\n"+"\t".join(row[k] for k in keys)+"\n")
        j = dict(overall="PASS", target_sha="0"*40, checks=[dict(row)])
        if name == "json_disagrees":
            j["checks"][0].update(verdict="FAIL", exit_code="1")
        (p/"results.json").write_text(json.dumps(j))
        (p/"SHA256SUMS").write_text("".join(
            hashlib.sha256(f.read_bytes()).hexdigest()+"  "+f.name+"\n"
            for f in sorted(p.iterdir())))
        print(name, v.verify(d))
```
Observed: required_INFO PASS; both verifier calls exit 0. After repair these inputs must be rejected.

## Handoff

Grok owns implementation repairs. ChatGPT owns only this review path.
Prioritize C1–C4 together because they share the acceptance decision contract. Add regressions for each reproduction, rerun affected tests, then validate the new exact candidate. Preserve old evidence and identify superseded results. No new spending or live account access is needed.
