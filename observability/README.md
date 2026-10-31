# observability -- host health collector + synthetic probes (lab)

<!-- knowledge-introduction -->
**Reading guide — In Development; operational verification is not implied.**

Use health measurements and recorded events to understand whether a service is working. Old or incomplete measurements can give false reassurance; missing information must remain visible.

For example: A saved health report is evaluated before an operator decides whether to send requests to a service.

Key terms: **Probe** means a limited request used to check a particular service behavior. **Metric** means a numerical measurement such as elapsed time or free space. **Log** means a recorded event with context for later inspection. **Fail closed** means refuse the permissive outcome when required checks are missing or fail.

**Before using this reference:** Offline fixture evaluation makes no probes. Live collect mode contacts configured targets and must be scoped deliberately.

Start with the [plain-English learning path](../docs/knowledge/incident.md) or [glossary](../docs/knowledge/glossary.md). [Current integration and review policy](../docs/knowledge/integration-policy.md) supersedes older review-order instructions. The technical material follows in its original order.
<!-- /knowledge-introduction -->


Lightweight, **stdlib-only** (Python >= 3.8) host health collector with bounded synthetic probes and a
**fail-closed** endpoint decision. Lab/reference code: it changes **no production endpoint, load
balancer or routing**, and the tests never touch the network.

```
observability/
  healthcheck/          package (collector, probes, payload validation, decision, JSON-lines logging, CLI)
  run_healthcheck.py    wrapper: python3 observability/run_healthcheck.py <evaluate|collect|host> ...
  config.example.json   example probe config (example.com / example.internal placeholders)
  fixtures/             recorded payloads + EXPECTED.json (fixed clock 2026-10-28T12:01:00Z)
  tests/                offline unittest suite (fake transports, fake host readers, fixed clock)
```

## Usage

```bash
# Evaluate a recorded payload (offline). Result JSON -> stdout, JSON-lines log -> stderr.
python3 observability/run_healthcheck.py evaluate observability/fixtures/healthy.json --now 2026-10-28T12:01:00Z

# Live: host snapshot + probes from a config (makes real HTTP/TCP/DNS calls to the configured targets).
python3 observability/run_healthcheck.py collect --config my-config.json --payload-out payload.json --out result.json --log-file run.jsonl

# Host snapshot only (no probes, no network).
python3 observability/run_healthcheck.py host
```

Exit codes: **0** HEALTHY, **1** UNHEALTHY, **2** malformed payload/config/policy, usage or internal
error (the result is still written and is UNHEALTHY / HTTP 503).

## Fail-closed decision

`overall` is `HEALTHY` (`endpoint_decision = {serve: true, http_status: 200}`) only if **every** check
passes. Anything else -- including anything not anticipated -- is `UNHEALTHY` (`serve: false, 503`):

| condition | result |
|---|---|
| payload unreadable, invalid JSON, duplicate keys, NaN/Infinity, unknown/missing keys, wrong types, unknown status/kind, > 1 MiB | UNHEALTHY, exit 2 |
| no expected probes declared | UNHEALTHY |
| expected probe has no result (missing probe), unexpected or duplicate result | UNHEALTHY |
| probe status `FAIL`, `TIMEOUT`, `ERROR` or `UNKNOWN` | UNHEALTHY |
| probe latency > `max_probe_latency_ms` | UNHEALTHY |
| payload / host / probe timestamp older than `max_age_s` or > `max_future_skew_s` in the future (stale) | UNHEALTHY |
| any host metric null, or any host collection error | UNHEALTHY |
| disk free ratio, load per CPU, available memory ratio outside policy, or inconsistent figures | UNHEALTHY |
| invalid config (bad URL, credentials in URL, timeout/max_bytes out of bounds, > 16 probes, duplicate names) | UNHEALTHY, exit 2 |
| uncaught exception anywhere | UNHEALTHY, exit 2 |

Default policy (`healthcheck/decision.py`, override with `--policy file.json` or `"policy"` in config):
`max_age_s 300`, `max_future_skew_s 30`, `min_disk_free_ratio 0.10`, `max_load_per_cpu 2.0`,
`min_mem_available_ratio 0.10`, `max_probe_latency_ms 5000`. Unknown policy keys are rejected.

## Probe bounds

* `timeout_s` in (0, 10]; enforced both in the transport and as a **hard wall-clock limit** (each probe
  runs in a daemon thread that is abandoned on expiry -> `TIMEOUT`).
* HTTP body read capped at `max_bytes` (<= 64 KiB, default 4 KiB); larger -> `ERROR`.
* At most **16** probes per run; probe names unique, `[A-Za-z0-9-_.]{1,64}`.
* HTTP(S) only, URLs with embedded credentials rejected; query strings are dropped from logged targets.
* Exceptions are reported by type name only (no messages that might carry sensitive detail).
* Transports are injectable: `http(url, timeout_s, max_bytes) -> (status, body)`,
  `tcp(host, port, timeout_s)`, `dns(hostname) -> [addresses]`.

## Privacy

The host collector reads only: 1-minute load average, CPU count, disk usage of one configured path,
`MemAvailable/MemTotal` from `/proc/meminfo`, and `/proc/uptime`. It does **not** collect usernames,
environment variables, process lists or arguments, home paths, hostnames or IP addresses. The JSON-lines
logger refuses keys such as `user`, `env`, `argv`, `home`, `hostname`, `pid`, `cmdline`, `password`, `token`.
Tests assert none of these (nor an env-var sentinel, the current username or home path) appear in output.

## Logs

One JSON object per line, sorted keys: `ts`, `level`, `component`, `event` plus scalar fields. Events:
`config.loaded`, `host.collected`, `probe.result`, `payload.loaded`, `payload.malformed`,
`config.invalid`, `health.decision`, `internal.error`.

## Tests (deterministic, local only)

```bash
python3 -m unittest discover -s observability/tests -v
```

Fixtures (`observability/fixtures`, each covered by tests and by `EXPECTED.json`): `healthy`,
`unhealthy`, `timeout`, `stale`, `missing-probe`, `unknown-status`, `host-metric-missing`, and malformed
payloads (`malformed-truncated`, `-wrong-type`, `-bad-status`, `-unknown-key`, `-nan`, `-duplicate-key`).
Evidence runs: see `evidence/observability/README.md`.
