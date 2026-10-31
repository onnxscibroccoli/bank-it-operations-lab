# 0013: Patch in rings; gated waves ship as Scan
- Status: **Proposed.** #17 is an open draft, not integrated in #7. EXAMPLE data only. Nothing applied.
- Date: 2026-10-28 (status re-checked 2026-10-28 at 14:24 EDT; learning/execution R15)

## Decision (as implemented)
- `patch-hardening@5605b78:operations/patching/ssm/patch-baselines-and-windows.cfn.yaml`: AL2023 and RHEL baselines with delayed auto-approval and `RejectedPatchesAction=BLOCK`. The rings are canary, then wave1, then wave2.
- The canary runs `Install` with `MaxConcurrency=1`, `MaxErrors=0` and a 48 h soak. Later waves **ship as `Scan`** and are switched to `Install` only at the gate (`procedures/APPROVAL.md`).
- `tools/inspect_patch_manifest.py` enforces this with rules such as `PM-CANARY-SIZE`, `PM-GATE-*` (24 h or more soak, approvers, compliance evidence), `PM-TASK-GATED-SCAN`, `PM-BASELINE-DELAY` and `PM-NO-REAL-IDS`.
- Runbooks: `procedures/{CANARY,APPROVAL,ROLLBACK,ESCALATION}.md`. Hardening is scored offline by `operations/hardening/tools/score_units.py`.

## Consequences
- If an approval is missed, the fleet stays in Scan rather than being patched without approval. The cost is slower rollout.
- Verified here: the plan printed canary, wave1 and wave2 with `overall: PASS`; 9 and 18 tests OK; no fixture drift; evidence PASS (113 inputs) (R10). `cfn-lint` and the AWS CLI were not run.
