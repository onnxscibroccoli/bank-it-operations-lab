# systemd hardening directive compatibility matrix

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Reduce the permissions and system features available to a service. Restricting unnecessary privileges can limit the effect of a compromised or defective service.

For example: A background process is given only the filesystem and operating-system access needed for its job.

Key terms: **systemd** means a Linux service manager used to start and supervise processes. **Hardening** means reducing unnecessary permissions, exposure, and risky configuration. **Drop-in** means an additional configuration file that modifies a service definition.

**Before using this reference:** Applying a service restriction can prevent legitimate work. Validate compatibility and recovery on an isolated host first.

Start with the [plain-English learning path](../../docs/knowledge/infrastructure.md) or [glossary](../../docs/knowledge/glossary.md). [Current integration and review policy](../../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


> Generated from [`compat/systemd-directives.json`](compat/systemd-directives.json) by
> `python3 operations/hardening/tools/score_units.py --render-matrix`. Do not edit the table by hand;
> `tests/test_score_units.py` fails if it drifts from the JSON.

**How to read it.** "min systemd" is the upstream version that introduced the directive (from the
`Added in version N` notes in systemd.exec(5) / systemd.resource-control(5)) or, for rows like
`ProtectSystem=strict`, the version that added that value (systemd NEWS). `< 187` means the
directive predates upstream's per-directive annotations and is available on every distro below.
Distro columns use the systemd major version shipped at GA.

**Caveats.**

- Vendors backport. RHEL in particular ships features in older version numbers, so a **no** can be a
  yes on a specific minor release. Confirm on a representative host with
  `systemd-analyze verify <unit>` and `systemctl show -p <Directive> <unit>` before relying on it.
- On a systemd that does not know a directive, the unit **still starts**; systemd only logs
  `Unknown key name ... ignoring`. The hardening line looks applied in review but does nothing. That is
  why `score_units.py --distro <id>` scores the *effective* exposure and fails on unsupported lines.
- `@system-service` (SystemCallFilter group) is listed at 239 from the upstream seccomp group
  history; it is not called out in NEWS, so verify on the target.

Which drop-in to use:

| Target | Drop-ins (see `systemd/dropins/`) |
|---|---|
| systemd 219 (RHEL/CentOS 7, Amazon Linux 2) | `05-hardening-legacy-219.conf` only; expected exposure ~5 (MEDIUM) -> record as accepted risk + migration plan |
| systemd 239 (RHEL 8) | `05-hardening-legacy-219.conf` + the 232/233/235-era lines of `10-`/`20-` (scorer lists exactly which lines are ignored) |
| systemd >= 242 | `10-hardening-baseline.conf` |
| systemd >= 247 | `10-hardening-baseline.conf` + `20-hardening-strict.conf` (+ `30-net-bind-service.conf` only if the service binds < 1024) |

| Directive | min systemd | RHEL / CentOS 7 (219) | Amazon Linux 2 (219) | RHEL 8 (239) | Ubuntu 20.04 (245) | Debian 11 (247) | Ubuntu 22.04 (249) | RHEL 9 (252) | Debian 12 (252) | Amazon Linux 2023 (252) | Ubuntu 24.04 (255) | Debian 13 (257) | RHEL 10 (257) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `AmbientCapabilities=` | 229 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `CapabilityBoundingSet=` | < 187 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `DynamicUser=` | 232 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `IPAddressDeny=` | 235 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `KeyringMode=` | 235 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `LockPersonality=` | 235 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `MemoryDenyWriteExecute=` | 231 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `NoNewPrivileges=` | 187 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `PrivateDevices=` | 209 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `PrivateIPC=` | 248 | **no** | **no** | **no** | **no** | **no** | yes | yes | yes | yes | yes | yes | yes |
| `PrivateNetwork=` | < 187 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `PrivateTmp=` | < 187 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `PrivateTmp=disconnected` | 260 | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** |
| `PrivateUsers=` | 232 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProcSubset=` | 247 | **no** | **no** | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectClock=` | 245 | **no** | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectControlGroups=` | 232 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectControlGroups=private` | 257 | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | yes | yes |
| `ProtectControlGroups=strict` | 257 | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | **no** | yes | yes |
| `ProtectHome=` | 214 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectHome=tmpfs` | 238 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectHostname=` | 242 | **no** | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectKernelLogs=` | 244 | **no** | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectKernelModules=` | 232 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectKernelTunables=` | 232 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectProc=` | 247 | **no** | **no** | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectSystem=` | 214 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ProtectSystem=strict` | 232 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `ReadWritePaths=` | 231 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `RemoveIPC=` | 232 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `RestrictAddressFamilies=` | 211 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `RestrictNamespaces=` | 233 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `RestrictRealtime=` | 231 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `RestrictSUIDSGID=` | 242 | **no** | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `StateDirectory=` | 235 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `SystemCallArchitectures=` | 209 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `SystemCallErrorNumber=` | 209 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `SystemCallFilter=` | 187 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `SystemCallFilter=@system-service` | 239 | **no** | **no** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `UMask=` | < 187 | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
