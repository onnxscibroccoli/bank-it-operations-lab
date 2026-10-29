# ADR 0008 — Human owner decisions on a personal repository

Status: **PROPOSED; verifier prototype implemented, not activated in the acceptance gate.** No key is enrolled and no reviewer is named. No owner decision is inferred from this document.

The personal repository has one owner. A second collaborator cannot be invited as another Admin. All agent lanes use the owner's GitHub identity; that identity alone cannot establish that Ian personally approved a decision.

Independent technical review remains separate: the active gate uses `reviewer_allowlist` in `.github/acceptance/trusted-config.json` from its independently pinned trusted checkout. The empty `reviewer-allowlist.json` here is a design placeholder, not a second active authority. Do not invent CODEOWNERS users or assert a native approval from same-account technical review notes.

## Implemented prototype

`verify_owner_attestation.py` uses standard-library Python and OpenSSL 3.x to validate a detached Ed25519 signature. It requires explicit `--keys` and `--expected` inputs. An independently trusted caller must supply both from outside the candidate; supplying candidate-controlled values proves nothing about authorization.

The signed payload has the exact schema `bank-lab/owner-attestation/v1`, repository, full candidate/main/tested-merge SHAs, workflow run, criterion, exception ID and scope, decision and key fingerprint. The expected binding must match every binding field. Unknown/missing fields, malformed SHAs, bad signatures, unknown keys and changed bindings fail closed. APPROVED and REJECTED decisions can both authenticate; signature validity is not approval. Output always marks `approvalEffective=false` and `mode=VERIFIER_ONLY`.

Tests create ephemeral keys in temporary directories, sign real payloads, and verify positive and tampered cases. These are not owner keys and are never enrolled. No PyNaCl or optional crypto dependency silently determines whether a positive test runs.

## Activation work before this can satisfy AC2/AC4/AC5

1. Ian holds a signing key that agents cannot access; enroll its public key/fingerprint through an independently reviewed trusted channel. Do not ask for or transmit the private key.
2. Define key rotation/revocation and conflict/ordering semantics for multiple signed decisions. The prototype does not decide which of conflicting valid signatures is current.
3. Add an independently reviewed adapter to the trusted acceptance gate that reads signatures from external evidence, supplies API-verified binding and scope, and applies the signed decision. Keep AC1 independent.
4. Re-pin the full verifier, config and workflow manifest after independent review. Add branch rules and verify the permitted evidence-publication route. Do not silently bypass the single-account review deadlock.

The existing login-bound gate remains unchanged and blocked. There is no claim that a signature now clears it. Owner key enrollment and policy approval remain human actions; API wiring/revocation engineering is explicitly not complete.

Reference: [OpenSSL Ed25519 verification](https://docs.openssl.org/3.0/man1/openssl-pkeyutl/).
