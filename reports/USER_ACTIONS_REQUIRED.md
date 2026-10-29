# Remaining owner actions

Development and test execution are already authorized. Do not ask for another generic permission to commit.

1. Independent reviewer: identify a separate qualified reviewer and invite them as a collaborator. The integrator prepares the protected allow-list and CODEOWNERS changes; no username is invented. The reviewer approves the exact final candidate only after review.
2. Branch protection: configure main and evidence/acceptance using a reviewed bootstrap procedure. Required check names must be verified from actual runs. Avoid a Restrict updates rule with no permitted update route.
3. Owner authentication: the design is recorded in governance/owner-auth (ADR 0008). The reviewer allow-list is empty and no signing key is enrolled, so it is not an active approval path. A personal repository can invite a collaborator with Write; Admin is not required and is not requested. Do not transfer the repository. An owner-account comment made with shared agent credentials is still not a personal decision. AC1 stays unmet until a separate reviewer approves the exact SHA.
4. Exceptions: after the authentication mechanism and final candidate are ready, provide plain-language decisions on each remaining EX-01–EX-04. The integrator must supply fully populated, version-bound attestations. No exception has been approved by this delivery work.
5. Entra baseline: synthetic lab assumptions must remain distinct from authorization for a live tenant.
6. Final portfolio acceptance: only after a reviewable candidate and applicable gates are complete. No action requested yet.

PR #1 supersession is integrator housekeeping, not an inherently human-only task. Technical repairs, source integration, reports, validation and evidence packaging continue autonomously.

Historical v1 attestation templates and old SHAs in earlier report revisions must not be used. The executable trusted gate remains authoritative and fail-closed until a separately reviewed replacement is activated.
