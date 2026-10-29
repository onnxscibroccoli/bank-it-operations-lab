# EVIDENCE MANIFEST

Snapshot: 2026-10-28, about 21:52 EDT for the live-candidate section; the per-branch history below is from about 14:25 EDT. The "verify" column shows the result of `sha256sum -c` re-run on the box for this report. The "hash of SHA256SUMS" column holds the first 16 hex characters of the SHA-256 of the SHA256SUMS file at the listed commit.

## Live candidate: PR #7 @ `e9310f3` (re-verified about 21:52 EDT; the evidence tree is unchanged from `1fdf25a`)

`e9310f3a94162a5dae31ee1cca9e35452de033ed`, base and `main` `7f50348`. Every bundle in the tree was checked with `sha256sum -c` on the box: **20 of 20 OK**. This table supersedes the per-branch rows below for the 7 integrated modules. Those rows are kept as history.

| Commit | Bundle | Entries | Hash of SHA256SUMS (16 hex) | Verify |
|---|---|---|---|---|
| `e9310f3` | `evidence/aws/aws-remediation-vpc-rds` | 44 | `b55711100bf75946` | OK (B5-2 pass 4; pre-fix copy under `superseded/pass3-pre-B5-2/`) |
| `e9310f3` | `evidence/entra/runs/local-offline-20261028T150359Z` | 46 | `ae111bd9f2677a1c` | OK |
| `e9310f3` | `evidence/m365/runs/local-offline-20261028T181845Z` | 20 | `52f3872346ef7113` | OK (PLAN_ONLY) |
| `e9310f3` | `evidence/incident/runs/local-20261028T181818Z` | 38 | `c5c381dc092e7ded` | OK (SIMULATION) |
| `e9310f3` | `evidence/incident/runs/local-20261029T000545Z` | 38 | `03ef3d46e530f75e` | OK (SIMULATION) |
| `e9310f3` | `evidence/postgres/runs/ci-service-40741329107-1` | 46 | `35b754a72a0e2e46` | OK; `verify_evidence.py` VERIFIED |
| `e9310f3` | `evidence/postgres/runs/ci-offline-40741329107-1` | 48 | `8d70475a19e69a61` | OK |
| `e9310f3` | `evidence/postgres/runs/ci-mismatch-control-40741329107-1` | 41 | `35c1acef322b92ae` | OK (negative control; REJECTED as expected) |
| `e9310f3` | `evidence/postgres/runs/ci-selftest-40741329107-1 (+ A/B/C subdirs 17/10/17)` | 48 | `cb6f29645d3c60d0` | OK |
| `e9310f3` | `evidence/postgres/runs/local-offline-v2-20261028T180208Z` | 48 | `b1a24138219376f0` | OK |
| `e9310f3` | `evidence/postgres/runs/local-selftest-v2-20261028T180208Z (+ A/B/C subdirs)` | 48 | `c625d6502091f985` | OK |
| `e9310f3` | `evidence/postgres/runs/ci-service-40630856041-1` | 36 | `598d028da03ec1d9` | OK, HISTORICAL (v1; results invalid) |
| `e9310f3` | `evidence/postgres/runs/local-offline-20261028T041038Z` | 39 | `a068097599f7b23e` | OK, HISTORICAL |
| `e9310f3` | `evidence/postgres/runs/integration-offline-20261028T180134Z` | 48 | `3faf0997635c4ab6` | OK, HISTORICAL (present again at `e9310f3`; reported HISTORICAL by validate-all step 27) |

Actions artifacts of integration-gate [40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048) (sha256 digest from the Actions API, first 16 hex; expiry in UTC):

| Artifact | Bytes | Digest | Expires |
|---|---|---|---|
| `acceptance-decision-9ff24a4…` | 5691 | `b0fd250e65f87c44` | 2027-01-27 |
| `user-actions-9ff24a4…` | 3610 | `ef75c71ec56c7255` | 2026-11-05 |
| `incident-fresh-run-9ff24a4…` | 23731 | `d29320e66dd5df35` | 2026-11-05 |
| `cdk-out` | 35025 | `193e0528f72037ad` | 2026-11-05 |
| `cdk-synth-evidence-40802567048-1` | 1041 | `8e00c5360d4158bd` | 2027-01-27 |
| `postgres-evidence-service-40802567048-1` | 61658 | `3c341083708f08b1` | 2027-01-27 |
| `postgres-evidence-offline-40802567048-1` | 63064 | `575e9c6d1c3a6ff4` | 2027-01-27 |
| `postgres-evidence-mismatch-control-40802567048-1` | 22583 | `4506b5c4acd9c72c` | 2027-01-27 |
| `postgres-evidence-selftest-40802567048-1` | 34025 | `bc03d88a0beafd31` | 2027-01-27 |

CI runs at `e9310f3`:
- integration-gate [40802567048](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567048) (PR) and [40802561953](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802561953) (push)
- main-validation [40802573622](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802573622)
- aws-cdk [40802567002](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567002) / [40802561755](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802561755)
- postgres-restore-evidence [40802567000](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567000)
- offline-validation [40802567034](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802567034) / [40802561784](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40802561784)

Each integration-gate run has 18/19 jobs succeeding; `merge-eligibility` fails, NOT ELIGIBLE.

## Committed evidence bundles (per-branch history)
| Branch @ commit | Bundle (SHA256SUMS) | Entries | Hash of SHA256SUMS | Verify |
|---|---|---|---|---|
| `bank-aws-001` @ `e494bcf` | `evidence/aws/SHA256SUMS` (paths relative to repo root) | 87 | `42f00cd3152a1d6c` | OK |
| `ci-evidence-postgres` @ `e7399fb` | `evidence/postgres/runs/ci-service-40741329107-1/` | 46 | `35b754a72a0e2e46` | OK |
| `ci-evidence-postgres` @ `e7399fb` | `evidence/postgres/runs/ci-offline-40741329107-1/` | 48 | `8d70475a19e69a61` | OK |
| `ci-evidence-postgres` @ `e7399fb` | `evidence/postgres/runs/ci-mismatch-control-40741329107-1/` (negative control, expected FAIL) | 41 | `35c1acef322b92ae` | OK |
| `ci-evidence-postgres` @ `e7399fb` | `evidence/postgres/runs/ci-selftest-40741329107-1/` | 48 | `cb6f29645d3c60d0` | OK |
| `ci-evidence-postgres` @ `e7399fb` | `evidence/postgres/runs/local-offline-v2-20261028T180208Z/` | 48 | `b1a24138219376f0` | OK |
| `ci-evidence-postgres` @ `e7399fb` | `evidence/postgres/runs/local-selftest-v2-20261028T180208Z/` | 48 | `c625d6502091f985` | OK |
| `ci-evidence-postgres` @ `e7399fb` | `evidence/postgres/runs/ci-service-40630856041-1/` (HISTORICAL-KNOWN-INVALID) | 36 | `598d028da03ec1d9` | OK (hashes only; the results are invalid) |
| `ci-evidence-postgres` @ `e7399fb` | `evidence/postgres/runs/local-offline-20261028T041038Z/` (HISTORICAL-KNOWN-INVALID under v2) | 39 | `a068097599f7b23e` | OK |
| `entra-ca-offline` @ `d302c99` | `evidence/entra/runs/local-offline-20261028T150359Z/` | 46 | `ae111bd9f2677a1c` | OK, and `--verify` OK |
| `aws-remediation-vpc-rds` @ `099479e` | `evidence/aws/aws-remediation-vpc-rds/` | 32 | `e9b3cb1f3f22390c` | OK |
| `orgs-security-refs` @ `e5e7f46` | `evidence/orgs/SHA256SUMS` (paths relative to repo root) | 66 | `3dac5c317e577b06` | OK |
| `vendor-mock` @ `c1ec227` | `evidence/vendor/runs/local-offline-20261028T180454Z/` | 12 | `43b2e8cc84b21e0d` | OK, and `--verify` PASS |
| `vendor-mock` @ `88a3785` | `evidence/vendor/runs/local-offline-20261028T180914Z/` | 14 | (not recorded) | OK, and `--verify` PASS |
| `observability` @ `3e40e39` | `evidence/observability/runs/local-offline-20261028T180832Z/` (validates `2613ea2`) | 44 | (not recorded) | OK, and `--verify` PASS |
| `overnight/integration` @ `876f7b7` | `evidence/postgres/runs/integration-offline-20261028T180134Z/` | 48 | `3faf0997635c4ab6` | OK. **Removed** in `e76d8a4` and absent at `0f57289` (the harness v2 re-merge) |

## GitHub Actions artifacts (digest from the Actions API; none expired as of the snapshot)
| Run | Artifact | Size (B) | Digest |
|---|---|---|---|
| [40631310661](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631310661) | cdk-out | 11596 | `sha256:c7efab76a2e1222f25353be1d59f8d07075be241e2f8ce4974476ff41311651c` |
| [40631120535](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631120535) | cdk-out | 11596 | `sha256:7a4418b461b3684463b599ab639d1fcc9f00ee61f9096a8d6a285b3dc760ca39` |
| [40630990406](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630990406) | cdk-out | 11596 | `sha256:bc274252b61835bd482a0547a588cfaf49f06bc4c75195b796beb111dfe74f74` |
| [40630567160](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630567160) | cdk-out | 11596 | `sha256:ebe53a3c576e616289399a6020f60223c03ef6257db7b9df564b19222a0317e5` |
| [40631034518](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631034518) | postgres-evidence-offline-40631034518-1 | 50759 | `sha256:49dae8cd11984eb8ed55fc866a3d08856e7722a94f3acf7b1dd33556cca03fd2` |
| [40631034518](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631034518) | postgres-evidence-service-40631034518-1 | 49465 | `sha256:7472af1e818af3924dfffa30310874a10f1cd285235d62a7fe04aba5357f5e67` |
| [40631027885](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631027885) | postgres-evidence-offline-40631027885-1 | 50766 | `sha256:362e47619df8db6c941db9df152d45d69b10bd1d790c778fbe029aac0725743c` |
| [40631027885](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631027885) | postgres-evidence-service-40631027885-1 | 49490 | `sha256:2ef8a4630c373fd30017a6d74d2c79eab15f4d94563d2dfd7a3287452ac98c06` |
| [40630876341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630876341) (failed) | postgres-evidence-service-40630876341-1 | 49046 | `sha256:373b971c2a7b9b7c06a2bb3ca4f61b9906909ef60877fc3578f05b01d9e64e34` |
| [40630876341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630876341) (failed) | postgres-evidence-offline-40630876341-1 | 50341 | `sha256:348298362a923790155904a750ce043b8d446185dd632aa48201e31bd28154da` |
| [40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041) (failed) | postgres-evidence-service-40630856041-1 | 49034 | `sha256:7caf8368cb649a55057721f855107d83030ef36febe931963fd4e94343307435` |
| [40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041) (failed) | postgres-evidence-offline-40630856041-1 | 50348 | `sha256:abdf9d9218fb0482bbf09dd38f65f5605da4555a800a1cebbd4fe170a612051c` |

The artifacts of the 14:02–14:03 EDT runs (40741…) were not listed in this snapshot. See each run page.

## All Actions runs (newest first; createdAt is in UTC, so subtract 4 h for EDT)
| Run | Workflow | Branch | Head | Event | Conclusion | Created (UTC) |
|---|---|---|---|---|---|---|
| [40741546543](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741546543) | postgres-restore-evidence | `ci-evidence-postgres` | `e7399fb` | pull_request | **success** | 2026-10-28T18:03:34Z |
| [40741536430](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741536430) | postgres-restore-evidence | `ci-evidence-postgres` | `e7399fb` | push | **success** | 2026-10-28T18:03:30Z |
| [40741464144](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741464144) | postgres-restore-evidence | `overnight/integration` | `876f7b7` | pull_request | **success** | 2026-10-28T18:03:03Z |
| [40741463903](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741463903) | aws-cdk | `overnight/integration` | `876f7b7` | pull_request | **success** | 2026-10-28T18:03:03Z |
| [40741463837](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741463837) | offline-validation | `overnight/integration` | `876f7b7` | pull_request | **success** | 2026-10-28T18:03:03Z |
| [40741456395](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741456395) | offline-validation | `overnight/integration` | `876f7b7` | push | **success** | 2026-10-28T18:03:00Z |
| [40741456368](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741456368) | aws-cdk | `overnight/integration` | `876f7b7` | push | **success** | 2026-10-28T18:03:00Z |
| [40741456056](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741456056) | postgres-restore-evidence | `overnight/integration` | `876f7b7` | push | **success** | 2026-10-28T18:03:00Z |
| [40741338458](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741338458) | postgres-restore-evidence | `ci-evidence-postgres` | `2aac93c` | pull_request | **success** | 2026-10-28T18:02:15Z |
| [40741329107](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40741329107) | postgres-restore-evidence | `ci-evidence-postgres` | `2aac93c` | push | **success** | 2026-10-28T18:02:12Z |
| [40631310661](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631310661) | bank-aws-001-cdk | `bank-aws-001` | `e494bcf` | pull_request | **success** | 2026-10-28T04:15:36Z |
| [40631120535](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631120535) | bank-aws-001-cdk | `bank-aws-001` | `25ba2f6` | pull_request | **success** | 2026-10-28T04:13:39Z |
| [40631034518](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631034518) | postgres-restore-evidence | `ci-evidence-postgres` | `e610015` | pull_request | **success** | 2026-10-28T04:12:42Z |
| [40631027885](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40631027885) | postgres-restore-evidence | `ci-evidence-postgres` | `e610015` | push | **success** | 2026-10-28T04:12:38Z |
| [40630990406](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630990406) | bank-aws-001-cdk | `bank-aws-001` | `af76d20` | pull_request | **success** | 2026-10-28T04:12:16Z |
| [40630876341](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630876341) | postgres-restore-evidence | `ci-evidence-postgres` | `daf8d82` | pull_request | **failure** | 2026-10-28T04:11:00Z |
| [40630856041](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630856041) | postgres-restore-evidence | `ci-evidence-postgres` | `daf8d82` | push | **failure** | 2026-10-28T04:10:48Z |
| [40630567160](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40630567160) | bank-aws-001-cdk | `bank-aws-001` | `88684d1` | pull_request | **success** | 2026-10-28T04:07:51Z |

### Runs added since the first snapshot (#7 `overnight/integration` @ `0f57289`, 2026-10-28 about 14:10 EDT)
| Run | Workflow | Conclusion |
|---|---|---|
| [40742562106](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742562106) | aws-cdk | **success** |
| [40742550274](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742550274) | aws-cdk | **success** |
| [40742561679](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742561679) | offline-validation | **success** |
| [40742550289](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742550289) | offline-validation | **success** |
| [40742561967](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40742561967) | postgres-restore-evidence | **success** |

### Refresh at integration head `afb41278` (2026-10-28 about 14:20 EDT)
| Run | Workflow | Event | Conclusion |
|---|---|---|---|
| [40743023477](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743023477) | aws-cdk | pull_request | **success** |
| [40743023533](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743023533) | offline-validation | pull_request | **success** |
| [40743011205](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743011205) | offline-validation | push | **success** |
| [40743023651](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743023651) | postgres-restore-evidence (5 jobs) | pull_request | **success** |

| Branch @ commit | Bundle | Verify [re-run] |
|---|---|---|
| `overnight/integration` @ `afb4127` | `evidence/postgres/runs/integration-offline-20261028T180134Z/` (restored, HISTORICAL-KNOWN-INVALID) | covered by `validate-all.sh --python-only`: PASS |
| `backup-dr-aws` @ `10da54f` | `evidence/backup/aws-backup-dr/SHA256SUMS` (repo-root relative) | 72/72 OK |
| `patch-hardening` @ `5605b78` | `evidence/host-operations/runs/local-offline-20261028T181252Z/` | 102/102 OK, `--verify` PASS |
| `identity-governance` @ `f48e7e3` | `evidence/identity-governance/runs/local-offline-20261028T181435Z/` | 49/49 OK, `--verify` OK |
| `m365-endpoint` @ `86a555a` | none committed | — |

### Refresh at about 17:45 EDT (verified this update)
| Item | Run / bundle | Head | Result |
|---|---|---|---|
| #26 acceptance (push) | [40749373581](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749373581) | `181bcdd` | **success**. Acceptance job OVERALL=PASS (43 required), verify_results OK; defect-control job OVERALL=FAIL as intended |
| #26 acceptance (PR) | [40749387217](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387217) | `181bcdd` | success |
| #26 aws-cdk / offline-validation / postgres (PR) | [40749387209](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387209), [40749387223](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387223), [40749387416](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40749387416) | `181bcdd` | success |
| #7 at its new head | [40743606730](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743606730), [40743606409](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743606409), [40743592407](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743592407), [40743606483](https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/runs/40743606483) | `49122f2` | success |
| #2 harness v2 | `selftest_harness.sh` [re-run] | `e7399fb` | 26/26 assertions |
| #22 SIMULATION | `evidence/incident/runs/local-20261028T181818Z/SHA256SUMS` | `3f13622` | 38/38 OK; `timeline.py --verify` PASS; selftest 4/4 |
