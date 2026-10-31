# Portfolio delivery report

PR #35 (`delivery/portfolio`) is a reviewable lab portfolio, not an accepted release. The registry reports **24/26 integrated, 27 total entries including one superseded entry**. The two remaining entries are the legacy acceptance slice and external review records; neither is silently counted as delivered. The owner-authentication entry is a verifier prototype, not an operational approval system.

## Delivered

The original integration baseline plus vendor simulation, observability, identity/vendor governance, control mapping, patch/hardening, hybrid runbooks, backup references, Organizations CDK and partial Terraform references, network-edge CDK, endpoint plan generation, and generated inventory/diagrams are assembled. Source provenance is retained in `coordination/modules.json`.

GitHub Actions runs bounded offline validation, CDK build/test/synth for base AWS, backup, Organizations and network-edge, Terraform provider-schema validation, PowerShell Pester behavior tests, and fresh PostgreSQL restore exercises with negative controls. Packaging requires all those jobs to succeed. Each artifact identifies its exact commit; consult that run's results rather than treating a prior green run as evidence for later commits. Workflows do not call paid model APIs or auto-merge.

The local owner-signature suite executes 15 tests, including real Ed25519 signatures, tampered payloads and binding mismatches. OpenSSL 3.x is required. The verifier always reports approvalEffective=false: no key is enrolled, no external signed-decision adapter is activated, and AC1 remains separate.

## Remaining engineering and acceptance limits

- Independent GitHub approval, reviewer enrollment, protected trusted-gate bootstrap/re-pinning and owner decisions remain outstanding. Candidate gate changes are not automatically trusted. A successful portfolio package does not make the integration gate eligible.
- Owner-signature activation still needs a reviewed adapter, trusted key enrollment, revocation and conflicting-decision semantics. Existing login-bound owner policy cannot be satisfied by inviting a second Admin to a personal repository. Do not follow historic instructions that request that.
- EX-04's AWS Backup role trust has an unverified vault SourceArn assumption during AssumeRole. It is a deployment blocker; static tests do not validate AWS runtime behavior. The exception remains proposed.
- Organizations Terraform is a partial reference, not feature parity with CDK and not an applied environment. Network AMI/application/VPN prerequisites and exception decisions remain deployment work.
- Endpoint PowerShell is executed by Pester in Linux CI as a plan generator. No domain-joined Windows execution or tenant mutation occurred.
- Legacy acceptance work and external review records are not integrated. Native independent-principal approval cannot be supplied by an agent using the author's account.

No live AWS, Entra, M365, Graph or banking-vendor system was changed. Incident/vendor data is synthetic. Hybrid runbooks and staff-management examples are NOT_EXECUTED. Costs use illustrative inputs. This portfolio does not establish employment history, banking tenure, regulatory compliance or production readiness.

## Handoff

Use README's credential-free quickstart and `docs/DEMO_WALKTHROUGH_15MIN.md`. Follow `reports/USER_ACTIONS_REQUIRED.md` for the human steps. PR #1 is closed as superseded; main and the old PR #7 review candidate are untouched. The original midnight target passed without an eligible merge; no deadline-completion claim is made.
