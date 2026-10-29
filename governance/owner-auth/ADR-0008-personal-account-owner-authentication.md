# ADR 0008 — Owner authentication on a personal GitHub account

Status: accepted as the lab design. It does not enroll a key, name a reviewer, or satisfy AC1.

## Context

The repository is owned by the personal account `onnxscibroccoli`. GitHub does not provide a second Admin principal inside that account. Inviting a second account as Admin was rejected as unavailable. Agents that push as the owner cannot be a second reviewer. A comment posted with the owner's token is login-bound; it is not proof that Ian made the decision.

Two different decisions were being collapsed:

1. Independent technical review of a candidate SHA (acceptance criterion AC1).
2. Owner disposition of security exceptions and of the portfolio (AC2, AC4, and any exception register).

## Decision

### Independent technical review

AC1 stays a GitHub pull-request review in state `APPROVED` from a user id listed in `reviewer-allowlist.json`. That file is an empty list. Empty means AC1 cannot be met. This design does not invent a username.

A personal repository can add a collaborator with the **Write** role. Write is enough to submit a pull-request review. **Admin is not required** and is not requested. The collaborator must be a person who does not share the owner's credentials. This repository cannot create that person.

`CODEOWNERS` does not name a reviewer who does not exist. Adding a fictional owner would make the file a false control.

### Owner decisions

Owner decisions are detached signatures over a canonical payload, checked by `verify_owner_attestation.py`. The enrolled public-key file is empty. With no enrolled key the verifier returns unattested for every payload, including a well-formed signature from the test fixture. The fixture key is not an owner key and must not be copied into the enrolled file by an agent.

A signature is not a GitHub approval. `merge_eligibility.py` is not changed to treat a signature as AC1.

### Branch-protection bootstrap

Required check names are the jobs in `.github/workflows/integration-gate.yml` that `merge-eligibility` needs. They are listed in `required-checks.json` and a test fails if that list drifts from the workflow.

Do not enable a ruleset whose "restrict updates" list is empty. That locks the owner out with no bypass.

Do not enable "require a pull request review" on `main` until `reviewer-allowlist.json` has at least one user id. On a single-account repository that rule cannot be satisfied by the only person who can merge, and dismissing it later to merge is a silent weakening. The deadlock is explicit: protection waits on a second identity, or the owner records a decision to keep `main` unprotected while signature-based decisions are still unavailable. This ADR does not record that decision.

## Consequences

- AC1, AC2, and AC4 stay unmet.
- No exception in `SECURITY_EXCEPTIONS.md` is approved by this ADR.
- The next human action, if a second reviewer is possible, is an invitation with Write (not Admin) and the addition of that user's numeric id to the allow-list in a commit the reviewer did not author alone. If a second reviewer is not possible, the owner says so; the gate stays red.
