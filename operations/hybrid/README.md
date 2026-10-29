# operations/hybrid: Windows Server, AD DS, DNS, GPO and hybrid identity

> **Execution status: NOT_EXECUTED.** Nothing here has been run against any environment. No authorized Windows Server, Active Directory, DNS, Group Policy or Microsoft Entra tenant was available. Every command is a reviewed **plan**, not a record of work done. All names (`corp.banklab.example`, `DC01`, `P0x`), addresses (RFC 5737 `192.0.2.0/24`) and tickets are synthetic.

## Contents

| Path | Purpose |
|---|---|
| [`EXECUTION_STATUS.md`](EXECUTION_STATUS.md) | One row per runbook: status, why it was not executed, and the evidence needed before the status can change |
| [`lab-topology.md`](lab-topology.md) | Synthetic reference topology (sites, DCs, DNS, sync server, OU layout) the runbooks assume |
| [`change-gates.md`](change-gates.md) | Pre-execution gates: authorization, change record, backups, maintenance window, two-person rule |
| [`checks/check_hybrid_runbooks.py`](checks/check_hybrid_runbooks.py) | Stdlib-only validator: status banner, required sections, relative links, no secret-like values, no "executed" claims |
| [`checks/test_check_hybrid_runbooks.py`](checks/test_check_hybrid_runbooks.py) | Offline unit tests for the validator |
| [`../../docs/runbooks/hybrid/`](../../docs/runbooks/hybrid/README.md) | The runbooks themselves |

## Run the checks (offline, no credentials)

```bash
python3 operations/hybrid/checks/check_hybrid_runbooks.py
python3 -m unittest discover -s operations/hybrid/checks -p 'test_*.py' -v
```

## What "NOT_EXECUTED" means here

- Commands were written from vendor documentation and reviewed for safety. They were **not** run, so output samples are illustrative only.
- Status changes to `EXECUTED_IN_LAB` only when an authorized, isolated environment exists, the gates in `change-gates.md` are met, and the evidence listed in `EXECUTION_STATUS.md` is committed.
- No entry in this directory may be read as production or customer experience.
