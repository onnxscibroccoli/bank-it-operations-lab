# Status vocabulary: lifecycle, evidence, registry, and decisions

This repository uses four separate status vocabularies. They answer different questions, so one never implies another. A page can be **In Development** (documentation lifecycle) while describing a module that is **INTEGRATED** (registry) with **STATIC_VALIDATED** evidence and a **Proposed** architecture decision.

## Documentation lifecycle

Source: `STATES` in [the site builder](../../scripts/docs/build.py) and the `lifecycle_status` enum in [the metadata schema](../metadata/schema.json). Shown in the status panel at the top of every page.

| Status | Meaning in this repository | Used now |
|---|---|---|
| Concept, Proposed, Planned | An idea or plan; nothing built yet | Not used by any page at this revision |
| In Development | Maintained, current explanation that may still change | Yes |
| Experimental, Simulated | Exploratory or fictional-input content | Not used by any page |
| Locally Verified, CI Verified, Integration Verified | Backed by a recorded check in that environment; requires evidence in metadata | Not used: every page records verification level "Not established" |
| Production Verified, Stable | Proven in production or declared stable | Not used, and nothing in this lab supports them |
| Deprecated | Superseded but still present | Not used |
| Archived | Preserved historical record; bytes locked by [preserved-records.json](../metadata/preserved-records.json) | Yes |

The separate **verification level** field uses the same words plus "Not established". The builder rejects any level other than "Not established" that lacks evidence references.

## Evidence labels

Source: the [root README](../../README.md#evidence-labels). These label what a recorded result is.

- **EXECUTED_LOCAL / EXECUTED_CI**: the named tool or test ran locally or in GitHub Actions. Not a deployment.
- **STATIC_VALIDATED**: templates or configuration were checked without deploying.
- **SIMULATION**: fictional inputs or an intentionally injected failure.
- **PLAN_ONLY**: proposed actions; no tenant change was made.
- **NOT_EXECUTED / NOT_RUN**: the step was not performed. Hybrid runbooks keep a NOT_EXECUTED banner at the top.

## Module registry states

Source: the `description` and each module's `status` in [coordination/modules.json](../../coordination/modules.json). The registry defines seven states:

- **INTEGRATED**: on the branch, with executable checks. 26 of the 28 registered modules use this state at main `8e2df97`. `review-notes` is NOT_INTEGRATED and `bank-aws-001` is SUPERSEDED. It does not mean reviewed, accepted, or deployed.
- **NOT_INTEGRATED**: an open PR, not on the branch. At `8e2df97` only `review-notes` (PRs #14, #27–#29) is in this state. The `acceptance` module moved to INTEGRATED with PR #40.
- **BLOCKED**: planned, with a recorded technical blocker.
- **SUPERSEDED**: replaced by another module (bank-aws-001, PR #1, by PR #5).
- **NOT_STARTED**: planned, no PR yet.
- **EXCLUDED**: legacy, still counted in the denominator.

Registry state and finding state can disagree. For example, `orgs-security` is INTEGRATED in the registry, while [coordination/tasks.json](../../coordination/tasks.json) still records findings B6-1, B6-2 and B6-3 as blocking. Report both; do not pick one.

## Architecture decision status

Source: the Status line of each record in [docs/adr](../adr/README.md). All seventeen ADRs say **Proposed**. Accepting an ADR is an owner decision; merging the code it describes does not accept it. See [ADR status on main](../adr/STATUS.md).

## Acceptance gate verdicts

Source: [acceptance/INTEGRATION-V2.md](../../acceptance/INTEGRATION-V2.md) and [tools/acceptance/gate](../../tools/acceptance/gate). The offline gate reports **EXECUTION_PASS**, **FAIL** or required **UNKNOWN** for a commit, and `decide.py` reports **REVIEW_PENDING** until there is independent reviewer concurrence. By design the gate never reports ACCEPTED. EXECUTION_PASS means the required checks ran and passed. It does not mean reviewed, accepted, or deployed.

## Words to avoid for unfinished work

Do not describe something as complete, done, fixed, verified or ready unless a named record supports that exact claim. Use instead:

- **Changed on branch, not deployed** for a code or documentation change that is not yet on main or on the live site.
- **Recorded as fixed in `<sha>`** when another record makes the claim and it has not been re-checked.
- **Tool output `VERIFIED` / `PASS`** when quoting a verifier, with the run date and environment.
- **Not run** or **NOT_EXECUTED** for anything that was not executed.

## Words the learning guide uses

The [twelve-week guide](../../learning/README.md) uses plain words in its own sections: **Delivered** (files exist at the cited commit), **Executed** (a command was actually run, recorded in its execution log), and **PENDING / UNEXECUTED** (not run, with the reason). These are descriptions inside a preserved record, not metadata values.
