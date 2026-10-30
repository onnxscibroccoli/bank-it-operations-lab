# Reviewer guide and copy-ready PR text

## One-page status summary

**Snapshot checked October 30, 2026. Draft portfolio; no eligible release or live deployment claimed.** Recheck GitHub before using this as current approval evidence.

| Item | Meaning |
|---|---|
| Repository | Reproducible AWS, identity, recovery and incident lab; evidence and review gates connect the modules |
| PR #7 | Preserved `overnight/integration` candidate `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45` |
| PR #35 | Newer `delivery/portfolio`; documentation changes after the verified snapshot require their own check results |
| Verified delivery snapshot | `29d618fd620c32e6b85c7ca034a82522e7429e49`; portfolio run [40994364291](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40994364291) passed and produced a package |
| Main observed | `7f50348bf1370381615eaed91c02607fe41de2f5`; no merge performed by this documentation update |
| Scope | 24/26 non-superseded entries integrated on delivery, 27 total including one superseded; not a readiness score |
| Outstanding | Independent approval, trusted gate/protection, owner-authentication activation and applicable owner decisions |
| Deployment limit | EX-04 Backup role trust runtime assumption unresolved; cloud templates remain static references |
| Completed housekeeping | PR #1 closed as superseded; no further owner action to close it |

The portfolio validation passes demonstrate technical checks for the specified commit. They do not approve exceptions, establish independent review, validate a live tenant, or satisfy final human acceptance. PR #7's older `e9310f3` results must not be presented as checks of `a9d0f64` or PR #35.

**Next human actions:** identify a qualified independent reviewer; configure reviewed branch protections; confirm the synthetic Entra baseline choices. Owner signing and final acceptance wait for a usable, independently reviewed path. Engineering work on that path is not something the owner must solve manually. See [detailed instructions](../reports/USER_ACTIONS_REQUIRED.md).

## Templated reviewer checklist

Copy this into review notes. Blank fields and unchecked items are not approval evidence.

```markdown
Candidate PR:
Candidate full SHA:
Main full SHA:
Tested merge SHA:
Actions run URL / attempt:
Reviewer identity / eligibility:
Scope of this review:

- [ ] AC1: I inspected this exact candidate; the approving reviewer is eligible, independent and allow-listed.
- [ ] AC1: No unresolved blocking review request is being ignored.
- [ ] AC2: Every applied exception matches its current rule/resource scope and authorized external decision.
- [ ] AC3: Required jobs ran successfully for this exact candidate/base/tested merge; no skipped job is counted as success.
- [ ] Gate trust: The executing verifier/workflow/config matches its independently reviewed protected pin.
- [ ] AC4: README, PR description, baseline choices and evidence labels match this tree.
- [ ] AC5: Every blocking finding has a verified resolution; tracking a blocker alone does not clear it.
- [ ] I distinguished static checks, simulation, executed tests and NOT_EXECUTED activities.
- [ ] I checked relevant negative controls, not only happy paths.
- [ ] I did not reuse PR #7 approval/evidence for PR #35 or vice versa.

Findings with path and evidence:
Unreviewed scope / limitations:
Decision: changes requested / further review needed / approve via GitHub review
Next action:

AC6 final owner acceptance: separate, not supplied by this checklist.
```

## Short PR #7 body

> Integrates shared evidence (#3), AWS remediation (#5), Entra offline validation (#4), PostgreSQL recovery (#2), and later M365 (#20) and incident simulation (#22) under repository-wide validation and acceptance gates. Review exact-SHA provenance, applied exception decisions, required job results, documentation accuracy and unresolved findings (AC1–AC5). AC6 remains separate human acceptance. This is a preserved draft baseline; the expanded portfolio is PR #35. No merge or live deployment is claimed.

## PR #7 narrative tailored to the repository history

The original integration sequence was #3 → #5 → #4 → #2 on main `7f50348`; #2 uses the owner's harness v2 at `e7399fb`. Later integration added #20 at `1b3c240` and #22 at `9f21329`. #5 supersedes #1's AWS code. Subsequent gate revisions addressed author-account approval, candidate-controlled trust, exact candidate/base/run binding and independently pinned verifier content.

PR #7 remains at `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45`. Its description previously emphasized older `e9310f3` validation. Those figures belong to that older revision. PR #35 contains subsequent module integration and additional fixes; those changes and their passing workflows do not retroactively approve PR #7. Consult the PR's own Checks tab for exact-head evidence.

The review question is both “do the modules work together?” and “does the acceptance gate reject false or stale evidence?” AC1–AC5 require independent review, scoped owner exception decisions, correctly bound checks, truthful docs and closure of blocking findings. Changing a README or marking an item complete in tasks.json cannot satisfy those conditions.

## Short reviewer discussion comment

> Please review this as an integration checkpoint: verify the exact candidate/base/tested-merge identity, independent approval, applied exception scope, trusted gate provenance, required checks and unresolved findings. Distinguish PR #7's preserved baseline from PR #35's expanded delivery. Green portfolio tests do not imply merge eligibility or live deployment. Record unreviewed scope explicitly.

## Tool-error clarification

An “awaiting confirmation / not run yet” message means the operation has not executed; it does not establish a repository permission failure. The interruption observed in this session was an automatic approval-review usage-limit failure, not a finding that the repository was unwritable. Later connector commits succeeded on `delivery/portfolio`. If an operation fails, use its actual error: distinguish confirmation pending, quota/review failure, authentication, permission denial, branch rules and stale expected SHA. Do not weaken branch protections to troubleshoot an unexecuted tool call.
