# Case study: Broccoli Core

- **Repository:** [https://github.com/onnxscibroccoli/broccoli-core](https://github.com/onnxscibroccoli/broccoli-core) (public, default branch `main`)
- **Snapshot:** HEAD [`f66678e`](https://github.com/onnxscibroccoli/broccoli-core/commit/f66678ea9749c6c22519028c39dc00d5c9e3bae1), the merge of PR #77 on 2026-10-19 19:44 EDT
- **Created:** 2026-07-18 16:26 EDT · **Commits on main:** 241 · **PRs:** 9 merged / 15 open / 0 closed
- **Languages (bytes):** Python 3.7 MB, Shell 1.5 MB, Roff 0.85 MB, Java 27 KB, Kotlin 7.5 KB (plus small amounts of JS/HCL/TS/AIDL)
- **Tracked files:** 5,547
- **License:** none declared (**Unknown** reuse terms)

## Mission (per README)

The repo description is "Broccoli Core - Android Automation Framework." The [README](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/README.md) describes it as "the oldest and largest automation-oriented repository in this account": an Android/Termux-centric agent runtime, a local execution kernel, provider integrations, UI observation, agent state, operational tooling, and "a very large historical mirror." The README also says it is "**not the current canonical OmniKali production implementation**."

## Architecture

- **Kernel** (per README): `text → classify → resolve schema → execute → confirm`, implemented in [`runtime/kernel.py`](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/runtime/kernel.py), with supporting modules such as `runtime/intent_schema.py`, `runtime/event_bus.py`, and `runtime/journal.py` ([`runtime/`](https://github.com/onnxscibroccoli/broccoli-core/tree/f66678ea9749c6c22519028c39dc00d5c9e3bae1/runtime)).
- **Android transport**: per the README (2026-10-02 status), privileged automation must go through `tools.android_transport.RishTransport` ([`tools/android_transport.py`](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/tools/android_transport.py)). It re-enters the full Termux context and calls the canonical wrapper [`lib/rish_run.sh`](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/lib/rish_run.sh). A fail-closed probe lives at [`lib/rish_transport_probe.sh`](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/lib/rish_transport_probe.sh). AutoJS is an optional adapter ([`scripts/autojs_run.py`](https://github.com/onnxscibroccoli/broccoli-core/blob/f66678ea9749c6c22519028c39dc00d5c9e3bae1/scripts/autojs_run.py)).
- **Hybrid controller** (added in PR #77): [`hybrid/`](https://github.com/onnxscibroccoli/broccoli-core/tree/f66678ea9749c6c22519028c39dc00d5c9e3bae1/hybrid) contains:
  - a Python gRPC server: `hybrid/server/` with `auth.py`, `policy.py`, `registry.py`, `store.py`, `worker.py`, `oci_worker.py`, and `model_runner.py`
  - a protobuf contract: `hybrid/proto/control.proto`
  - a Java Android controller app: `hybrid/android/` with `ControllerService`, `ShellService`, `Enrollment`, `Journal`, and an AIDL `IShell`
  - a PKI provisioning script: `hybrid/scripts/provision-pki.py`
  - a Terraform deploy stub: `hybrid/deploy/main.tf`
- **Historical surface**: `Agent/` (2,167 files, including 292 under `Agent/Broccoli/mirror/`), `BroccoliWorkspaceBackup/` (1,446 files), and `meta/`, `runs/`, `done/`, `fail/`, and `_quarantine/` directories.

## Evidence

**Tests**
- The README says to run the offline suite with `python3 -m unittest discover -s tests -t . -v`. It also claims "On 2026-10-02 the rooted suite passed 136/136 tests on the Android/Termux target" (per README, **not re-run** here). 68 `tests/**/test*.py` files exist at the snapshot.
- The hybrid controller has its own tests: `hybrid/tests/test_auth.py`, `test_policy.py`, `test_registry.py`, `test_store.py`, `test_transport.py`, and `test_worker.py`, plus the Java `CommandsTest.java` ([`hybrid/tests/`](https://github.com/onnxscibroccoli/broccoli-core/tree/f66678ea9749c6c22519028c39dc00d5c9e3bae1/hybrid/tests)).

**CI**: `ci.yml`, `build.yml`, and `edge.yml` ([workflows](https://github.com/onnxscibroccoli/broccoli-core/tree/f66678ea9749c6c22519028c39dc00d5c9e3bae1/.github/workflows)), plus a "Hybrid controller signed APK" workflow.
- `ci` and "Hybrid controller signed APK" both succeeded on `f66678e` at 2026-10-19 19:44 EDT ([Actions](https://github.com/onnxscibroccoli/broccoli-core/actions)). The latest `ci` run is a success on `2d3b595` ([run 39352779867](https://github.com/onnxscibroccoli/broccoli-core/actions/runs/39352779867)). That SHA is not main's HEAD, so it is probably a branch.
- The signed-APK workflow **failed** on `e7f6c73` (2026-10-13 23:23 EDT) and passed on the next commit, `4a7e180`.

**Notable PRs**
- [#77](https://github.com/onnxscibroccoli/broccoli-core/pull/77) (merged, +1,836/−4, 49 files): hybrid controller with signed APK CI. The PR body records a passing workflow run, `apksigner` v2+v3 verification, and a manifest with `live_device_acceptance: NOT_RUN`. It **explicitly does not claim** physical device, Shizuku, or rish bootstrap success, live RDC verification, or a published release.
- Hardening commits inside #77: `2756adf` ("test: exercise actual mTLS gateway and bidirectional gRPC") and `63ac5cb` ("fix(pki): add SKI/AKI and CA keyCertSign so Python 3.13 strict X.509 accepts mTLS chain").
- [#57](https://github.com/onnxscibroccoli/broccoli-core/pull/57)–[#63](https://github.com/onnxscibroccoli/broccoli-core/pull/63) and [#68](https://github.com/onnxscibroccoli/broccoli-core/pull/68) (merged, 2026-10-01 to 2026-10-02) add:
  - fail-closed RDC transport diagnostics
  - the canonical rish wrapper
  - a bounded agent action contract and CLI
  - application inspection primitives
  - an MCP supervisor
  - an RDC→Termux→Rish bridge
  - an AutoJS smoke retry
- The rish transport was later extracted to [onnxscibroccoli/broccoli-rish](https://github.com/onnxscibroccoli/broccoli-rish), which describes itself as "Extracted from broccoli-core; not a rewrite."

## Relevance to role

Requirement IDs refer to [JOB_ALIGNMENT.md](JOB_ALIGNMENT.md).

- **C8 Linux and shell (Strong, shared with Helix):** about 1.5 MB of shell, including the canonical `lib/rish_run.sh` wrapper and a fail-closed `lib/rish_transport_probe.sh`.
- **B2 endpoint automation (Partial):** privileged Android device automation (Rish/Shizuku), plus a hybrid controller with mTLS and gRPC (PR #77). This is Android, not managed corporate endpoints. Live device acceptance is recorded as `NOT_RUN`.
- **B9 evidence discipline (Partial):** PR #77 lists what it does **not** claim (device, Shizuku/rish, RDC, release).
- **Caution for reuse:** the README warns about credential-like historical paths. This repository is the least suitable of the five to show an employer without an audit first.

## Limitations and unknowns

- The README states the repository "does **not**, by itself, prove current production availability, current credentials, current device state, or equivalence with the current OmniKali production system."
- The README warns that "Some historical paths look like credential or secret-storage locations." **This case study did not inspect, copy, or list them.** Anyone reusing this repository should audit it before redistributing it.
- Live device acceptance for the hybrid controller is recorded as `NOT_RUN` (PR #77).
- The 136/136 test claim comes from the README and was not reproduced.
- 15 PRs are open, including an M3 vector store ([#53](https://github.com/onnxscibroccoli/broccoli-core/pull/53)–[#55](https://github.com/onnxscibroccoli/broccoli-core/pull/55)) and a rish controller registry ([#78](https://github.com/onnxscibroccoli/broccoli-core/pull/78)). None of that work is on main.
