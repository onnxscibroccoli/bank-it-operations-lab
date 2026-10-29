# Host patching (AWS SSM Patch Manager) -- reference examples

> **Example / offline.** Everything here is reference material for review. Nothing in this directory
> calls AWS, and nothing has been applied to any account or host. Identifiers are placeholders
> (`<CANARY_WINDOW_ID>`, `EXAMPLE-...`).

## Layout

| Path | What it is |
|---|---|
| `ssm/patch-baselines-and-windows.cfn.yaml` | CloudFormation example: AL2023 + RHEL patch baselines (delayed auto-approval, `RejectedPatchesAction=BLOCK`), patch groups, and canary -> wave1 -> wave2 maintenance windows running `AWS-RunPatchBaseline`. Gated waves default to `Scan`. |
| `ssm/cli/*.json` | The same resources as `aws ssm ... --cli-input-json` inputs (baselines, patch-group registrations, windows, targets, tasks). |
| `manifests/patch-manifest.example.json` | Patch-cycle manifest: ring order, sizing, soak, approval gates, rollback and escalation references. |
| `procedures/CANARY.md`, `APPROVAL.md`, `ROLLBACK.md`, `ESCALATION.md` | Runbooks for the canary ring, ring gates, rollback and escalation. |
| `tools/inspect_patch_manifest.py` | Dry-run inspector: parses the manifest and the CLI files it references, checks ~25 rollout-safety rules, prints the planned rollout. Never calls AWS. |
| `tools/print-cli-commands.sh` | Echoes the AWS CLI commands (for a change record) without running them. |
| `tests/` | Fixture tests (`make_fixtures.py` generates 42 valid/neg/malformed manifests from the example). |

## Run

```bash
python3 operations/patching/tools/inspect_patch_manifest.py operations/patching/manifests/patch-manifest.example.json --plan
python3 -m unittest discover -s operations/patching/tests -v      # or: python3 -m pytest operations/patching/tests
python3 operations/patching/tests/make_fixtures.py --check         # fixture drift
cfn-lint operations/patching/ssm/patch-baselines-and-windows.cfn.yaml
```

Inspector exit codes: `0` all rules pass, `1` rule failures, `2` malformed input (fail closed).

## Rollout model

1. **canary** (`PatchGroup=canary|canary-rhel`): `Install`, `MaxConcurrency=1`, `MaxErrors=0`, pre-snapshot, 48 h soak.
2. **wave1**: gated on canary sign-off + compliance summary + named approvers; task ships as `Scan`
   and is flipped to `Install` only at gate time (APPROVAL.md).
3. **wave2**: gated on wave1 the same way.

Rules worth knowing: `PM-CANARY-SIZE`/`PM-CANARY-ERRORS` (canary is one host, zero errors),
`PM-GATE-*` (every later ring gated on the previous ring, >= 24 h soak, approvers, compliance
evidence), `PM-TASK-GATED-SCAN` (gated rings ship as Scan), `PM-BASELINE-DELAY` (no zero-delay
auto-approval), `PM-NO-REAL-IDS` (no 12-digit account ids or real `pb-`/`mw-`/`i-` ids).
