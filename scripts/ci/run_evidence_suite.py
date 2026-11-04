#!/usr/bin/env python3
"""Run the narrow evidence-contract suite and persist its actual exit status.

This wrapper fixes the command and test identifiers. It never treats a
non-zero test process, missing negative case, or empty suite as success.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys


NEGATIVE_IDS = (
    "test_negative_01_post_hash_tampering",
    "test_negative_02_candidate_sha_substitution",
    "test_negative_03_required_report_missing",
    "test_negative_04_duplicate_json_key",
    "test_negative_05_directory_traversal",
    "test_negative_06_symlink_outside_bundle",
    "test_negative_07_zero_suite_success",
    "test_negative_08_wrong_expected_failure_reason",
    "test_negative_09_missing_execution_marked_pass",
    "test_negative_10_fabricated_human_approval",
)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def main():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("CI-only report wrapper; no local run may claim EXECUTED_CI")
    evidence = Path("evidence-out")
    evidence.mkdir(exist_ok=True)
    command = [
        sys.executable, "-m", "unittest", "-v",
        "scripts/ci/tests/test_portfolio_evidence.py",
    ]
    started = datetime.now(timezone.utc)
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True,
                                   timeout=60, check=False)
        output = completed.stdout
        returncode = completed.returncode
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or b"").decode("utf8", "replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
        output += "\nSuite timed out before completion\n"
        returncode = 124
    finished = datetime.now(timezone.utc)
    (evidence / "unittest.log").write_text(output)
    match = re.search(r"Ran (\d+) tests? in", output)
    tests = int(match.group(1)) if match else 0
    observed = []
    for name in NEGATIVE_IDS:
        if re.search(re.escape(name) + r" \([^\n]+\) \.\.\. ok", output):
            observed.append({
                "id": name, "status": "REJECTED_AS_EXPECTED",
                "observedReason": "negative-control rejection assertion passed: " + name,
            })
    passed = returncode == 0 and tests > 0 and len(observed) == len(NEGATIVE_IDS)
    if not passed:
        print("NEGATIVE CONTROL / SUITE FAIL: status=" + str(returncode) +
              " tests=" + str(tests) + " verified=" + str(len(observed)), file=sys.stderr)
    data = {
        "runId": os.environ.get("GITHUB_RUN_ID"),
        "runAttempt": int(os.environ.get("GITHUB_RUN_ATTEMPT", "0")),
        "testedSha": os.environ.get("GITHUB_SHA"),
        "candidateSha": os.environ.get("PR_HEAD_SHA") or os.environ.get("GITHUB_SHA"),
        "event": os.environ.get("GITHUB_EVENT_NAME"),
        "startedAt": iso(started), "finishedAt": iso(finished),
        "tests": tests, "assertions": len(observed),
        "skipped": 0, "failed": 0 if passed else 1,
        "exitCode": returncode, "negativeControls": observed,
    }
    (evidence / "report.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
