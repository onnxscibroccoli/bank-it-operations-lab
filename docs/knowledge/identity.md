# Control employee permissions

## Level 1: Everyday explanation

Authentication checks who someone is. Authorization determines what they may do. Showing a staff badge is like authentication; being allowed into the records room is like authorization. Neither should automatically imply the other. See [the glossary](glossary.md#authentication) and [authentication background](https://en.wikipedia.org/wiki/Authentication).

Least privilege means giving someone only the access needed for their tasks. Role-based access control (RBAC) assigns permissions to roles, then assigns people to those roles. A receptionist may schedule appointments without changing clinical records. See the [glossary](glossary.md#rbac) and [RBAC overview](https://en.wikipedia.org/wiki/Role-based_access_control).

## Level 2: Operational explanation

Ask managers to confirm access when people join, move roles, or leave. Review powerful administrator access separately. Emergency access needs its own review and safeguards. The same principles apply across industries; the fictional bank examples here are teaching material.

## Level 3: Guided offline exercise

Objective: recognize the difference between expected access and deliberately seeded findings. Estimated 15 minutes; beginner to intermediate. Requires Python 3 and a checkout, no Microsoft account or elevated permissions. The tool reads fictional JSON responses; it cannot change real employee access.

From the repository root:

```bash
python3 identity/governance/inventory.py --scenario baseline --as-of 2026-10-28T12:00:00Z
python3 identity/governance/inventory.py --scenario findings --as-of 2026-10-28T12:00:00Z
```

The first scenario is expected to return exit 0; the second returns exit 1 for seeded high/medium findings. Exit 2 means input/fetch failure, not successful validation. Compare the finding identifiers with the [rules table](../../identity/governance/README.md#rules). The fixed date prevents the teaching fixture from aging into a different result.

These commands print reports without requesting output files, so there is nothing to clean up. A missing file usually means the wrong working directory or an incomplete checkout. Do not add credentials to fix a synthetic fixture failure.

## Level 4: Expert reference

The [client](../../identity/governance/graph_client.py) has only a fixture transport. [Inventory implementation](../../identity/governance/inventory.py) models role assignments and findings; it is not an authenticated Microsoft Graph integration. Inspect [tests](../../identity/governance/tests) for paging, throttling, authorization failures, and malformed data. Real API permissions and licensing need separate review before any live integration.

## Security and further learning

Never paste employee identifiers or access reports into public evidence. Consult the [official role permissions reference](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference) for current Microsoft details. An agent may explain or run this offline exercise, but must not silently substitute a real tenant or infer permission to modify access.
