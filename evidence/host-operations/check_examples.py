#!/usr/bin/env python3
"""Check that every file in evidence/host-operations/examples/ is clearly marked as example data
and carries no real-looking AWS identifiers. Exit 0 ok, 1 problems. Stdlib only."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "examples")
ACCOUNT_ID_RE = re.compile(r"(?<![0-9])[0-9]{12}(?![0-9])")
REAL_ID_RE = re.compile(r"\b(?:pb|mw|i|mi|snap|ami|vol)-[0-9a-f]{8,17}\b")


def main():
    problems = []
    names = sorted(os.listdir(EX))
    for n in names:
        p = os.path.join(EX, n)
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        if ".example." not in n:
            problems.append("%s: filename must contain '.example.'" % n)
        if "EXAMPLE DATA" not in text:
            problems.append("%s: missing 'EXAMPLE DATA' marker" % n)
        if n.endswith(".json"):
            try:
                doc = json.loads(text)
            except ValueError as exc:
                problems.append("%s: invalid JSON: %s" % (n, exc))
                continue
            if not str(doc.get("_exampleData", "")).startswith("EXAMPLE DATA"):
                problems.append("%s: top-level _exampleData marker missing" % n)
        for m in ACCOUNT_ID_RE.findall(text) + REAL_ID_RE.findall(text):
            problems.append("%s: real-looking identifier %s" % (n, m))
    for p in problems:
        print("PROBLEM: %s" % p)
    print("checked %d example files: %s" % (len(names), "FAIL" if problems else "PASS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
