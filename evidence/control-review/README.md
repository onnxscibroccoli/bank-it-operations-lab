# evidence/control-review

Review notes and validation output for the FFIEC AIO (June 2021) lab control mapping in
[`governance/controls/ffiec-aio-mapping.md`](../../governance/controls/ffiec-aio-mapping.md).

> Lab material. Not an examination, audit, assurance report, compliance certification or regulatory opinion.

| File | Purpose |
|---|---|
| [`review-notes.md`](review-notes.md) | Coverage counts by status, what each status rests on, top gaps, open questions |
| [`validation-run.log`](validation-run.log) | Captured output of the mapping validator (`--check-branches`) and its unit tests |

## Coverage at a glance (17 mapped rows, 15 distinct AIO sections, 97 artifact references)

| Status | Rows | Row ids |
|---|---|---|
| OBSERVED | 0 | - |
| SIMULATION | 14 | AIO-01, 02, 03, 04, 05, 07, 08, 09, 10, 12, 13, 14, 15, 17 |
| STATIC | 2 | AIO-06, AIO-16 |
| NOT_EXECUTED | 1 | AIO-11 |

Plus 10 groups of AIO topics reviewed and listed as **not mapped** (no relevant artifact), in the mapping's last table.

## Reproduce

From the repo root, with the source branches fetched (`git fetch origin`):

    python3 governance/controls/validate_mapping.py --check-branches
    python3 -m unittest discover -s governance/controls/tests -v

Exit code 0 and `MAPPING VALID` mean every referenced `commit:path` exists and the structural checks pass. It does **not** mean
anything about the adequacy of any control.
