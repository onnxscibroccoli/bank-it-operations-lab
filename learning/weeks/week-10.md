# Week 10: Defending the storage and logging architecture (architecture defense 1 of 3)

**Branches:** `$PR1`, `$PR3`, `$PR5`. **ADRs:** `docs/adr/0003`, `0004`, `0005`, and the module ADRs `infra/aws-cdk/docs/adr/ADR-0002` (PR #1) and `ADR-0004` (PR #5, Proposed, supersedes part of ADR-0002).

## Daily exercises
**Day 1: Decision history.** Read ADR-0002 (PR #1) and then ADR-0004 (PR #5). Write one paragraph on why the `self-access-logs/` decision was reversed, citing PR #3 §3 and the AWS quote it contains.

**Day 2: Defend EX-01.** Prepare a 3-minute defense of SSE-S3 on the log sink: the constraint, the compensating controls, and the exit criteria (`SECURITY_EXCEPTIONS.md`).

**Day 3: Attack the design.** As a reviewer, list the weaknesses that the repo itself admits: no lifecycle rules (PR #3 §4), the default KMS key policy on PR #1 (`infra/aws-cdk/README.md`, "Known gaps"),
EX-02 (no replication), and actions pinned by tag, not SHA (PR #3 §4).

**Day 4: Run the proofs live.** Use the week 2/3 commands: PR #1 `cfn-s3-selflog` gives ERROR, and PR #5 gives `S3 LOGGING OK`, `jest 33/33`. Executed: E03, E04, E01.

**Day 5: Mock review board.** 15-minute walkthrough (below), then 10 minutes of the interview questions.

## Failure injection and recovery
Live-demo the injected self-logging template (week 3) and the evidence tamper (week 2). The recovery story is: guard → test → ADR → exception register.

## Answer notes
- The strongest argument is not "the scanner is green". It is "a guard exists for the thing the scanner misses, and a negative test proves it" (`negative-controls.test.ts`).

## Architecture tradeoffs
- One-way log chain (ADR-0004) versus a third bucket: fewer resources and no recursion, but the sink itself is not access-logged. ADR-0004 suggests CloudTrail S3 data events if that is needed.

## Fifteen-minute walkthrough
(2) Context and constraints → (4) ADR-0002 to ADR-0004 history → (4) guards and the negative test → (3) exceptions EX-01/EX-02 → (2) open risks.

## Interview questions
1. Why reverse an accepted ADR rather than suppress the finding?
2. How do you audit access to the log sink itself?
3. What is your plan for lifecycle and retention on versioned, retained buckets?

## PENDING / UNEXECUTED
- ADR-0004 and the exception register are **Proposed / pending owner approval**. Nothing here is merged.
