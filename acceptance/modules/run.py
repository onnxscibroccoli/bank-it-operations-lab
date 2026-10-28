#!/usr/bin/env python3
"""Run acceptance module adapters and emit contract results.

  python3 acceptance/modules/run.py [aws-cdk|postgres|entra-offline|all] [--mode static-evidence|live-offline]
                                    [--json-out FILE]
Exit: 0 PASS, 1 FAIL, 2 ERROR/usage, 4 NOT_EXECUTED (worst across modules). Offline only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from acceptance.modules import aws_cdk, entra_offline, postgres  # noqa: E402
from acceptance.modules.contract import EXIT  # noqa: E402

ADAPTERS = {"aws-cdk": aws_cdk, "postgres": postgres, "entra-offline": entra_offline}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("module", nargs="?", default="all", choices=[*ADAPTERS, "all"])
    ap.add_argument("--mode", default="static-evidence", choices=["static-evidence", "live-offline"])
    ap.add_argument("--json-out")
    a = ap.parse_args(argv)
    names = list(ADAPTERS) if a.module == "all" else [a.module]
    results = [ADAPTERS[n].run(mode=a.mode).to_dict() for n in names]
    for r in results:
        bad = [c for c in r["checks"] if c["status"] != "PASS"]
        print(f"{r['module']:14} {r['mode']:15} {r['status']:12} {r['reason_code']:28} "
              f"checks={len(r['checks'])} non_pass={len(bad)}")
        for c in bad:
            print(f"    {c['status']:12} {c['reason_code']:28} {c['id']}: {c['detail'][:160]}")
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(results if len(results) > 1 else results[0], indent=2) + "\n")
    order = ["PASS", "NOT_EXECUTED", "FAIL", "ERROR"]
    worst = max((r["status"] for r in results), key=order.index)
    return EXIT[worst]


if __name__ == "__main__":
    sys.exit(main())
