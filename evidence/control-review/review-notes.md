# Review notes: FFIEC AIO lab control mapping

- Date: 2026-10-28 (America/New_York). Reviewer: lab automation, acting for the repository owner. Not an independent review.
- Scope: `main` @ `7f50348` (README only) plus the open draft PRs cited in the mapping (#1, #2, #3, #4, #5, #6, #9, #10, #13),
  each pinned to a head SHA. #7, #8, #11 and #12 were inventoried and not cited (integration copy / not AIO-relevant).
- Source: FFIEC IT Examination Handbook, AIO booklet, June 2021 (sources S1-S6 in the mapping). Section ids and page numbers
  were copied from the booklet; nothing was paraphrased into a requirement.

## 1. Counts

| Status | Rows | What the status rests on in this repo |
|---|---|---|
| OBSERVED | 0 | Nothing ran in a live environment the lab operates. No AWS deployment, no Entra tenant, no real host monitored. |
| SIMULATION | 14 | `cdk synth` / Jest / cdk-nag logs (PR #1, #5, #6); offline validators with negative fixtures (PR #4, #9, #10); a GitHub Actions + ephemeral Postgres backup/restore exercise (PR #2, run 40741329107). |
| STATIC | 2 | Pinned lockfiles and ADR for open source (AIO-06); synthetic incident/priority/escalation documents (AIO-16). |
| NOT_EXECUTED | 1 | AWS Backup plan and RDS backup retention are defined, but no backup job or restore has ever run (AIO-11). |

SIMULATION is the ceiling for everything in the repo today. The difference between "the definition synthesizes and its
tests pass" and "the control operates" is the main thing a reader should take away.

## 2. Top gaps

1. **No live evidence (OBSERVED = 0).** Nothing has been deployed or applied, so no AIO topic has operating evidence.
   First candidates: deploy PR #5 to a sandbox account and capture a real RDS snapshot + restore (would move AIO-11 off
   NOT_EXECUTED), and capture real CloudTrail / flow log delivery (AIO-12).
2. **Nothing merged.** `main` holds only a README; every mapped artifact is on an open draft PR. Change management (AIO-02)
   has CI runs and a written peer review but no approved, merged change.
3. **Governance layer absent (II.A-II.F, esp. II.C).** No approved policies, standards or procedures. Synthetic process
   documents (PR #13) and vendor templates (PR #9) are teaching examples, not adopted policy.
4. **Asset inventory, diagrams, data classification (III.A.1, III.B, III.C.1, III.C.2).** Not present. AIO VI.A.2 ties
   authorization boundaries to ITAM inventories, so AIO-07 has no inventory to anchor to.
5. **Vulnerability and patch management (VI.B.3).** No scanning; dependency installs run with `npm ci --no-audit`.
6. **Third-party oversight is fictional (III.E, VII.A.4).** PR #9 models a fictional vendor; there is no shared-responsibility
   matrix or review of real CSP assurance reports for AWS, Microsoft or GitHub.
7. **Incident management is documents only (VI.C.4).** `docs/runbooks/**` was never delivered; no exercise was run.
8. **Backup/DR AWS work not committed.** A `backup/aws` directory exists only as uncommitted work in a local checkout and is
   not referenced.
9. **Proposed exceptions EX-01..EX-04 (PR #5)** have no approver.

## 3. Evidence-quality notes found while mapping

- PR #2: the first CI run (40630856041) failed and its v1 harness also gave false passes on negatives;
  `evidence/postgres/runs/INDEX.md` marks it and the v1 local run HISTORICAL-KNOWN-INVALID. The mapping cites only the v2
  runs as evidence and the old run only as documentation.
- PR #2: dump files are gitignored; their hashes (`ARTIFACTS.sha256`) cannot be re-verified from the repo alone once the CI
  artifact retention expires.
- PR #1: `reports/review-pr1-pr2.md` (PR #3) notes that `jest-results.json` is partly self-referential and that some
  `COMMANDS.tsv` rows were not written by the wrapper. AIO-02 relies on the captured `gh run watch/view` logs, not on that file.
- PR #6: the offline SCP evaluator is not AWS's policy engine (stated in `evidence/orgs/README.md`).
- PR #2 head moved (e610015 -> e7399fb) during this work; other PRs may also move. Pins are full SHAs and the validator
  rechecks them.
- Page numbers come from a third-party copy of the booklet PDF because the official PDF refused scripted download.

## 4. Open questions for the owner

- Should OBSERVED evidence come from a sandbox AWS account / Entra test tenant? That needs credentials and approvals the lab
  does not have today.
- Which open PRs are intended to merge? Once merged, the pins should move to `main` SHAs.
- Should the mapping cover Appendix A examination procedures (objectives) as well as narrative sections?
