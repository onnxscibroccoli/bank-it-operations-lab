#!/usr/bin/env python3
"""Emit v1 evidence from an already-written machine-readable test report.

Producer does not execute a test or invent a test count. A separately
authenticated CI workflow must execute tests, produce the report, verify the
manifest against GitHub runtime identity and retain signed artifacts later.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from verify_evidence import (
    configuration_digest, git_source_digest, no_duplicates, read_json,
    safe_file, sha_file, verify, _git_parents
)


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], stderr=subprocess.DEVNULL,
        text=True, timeout=10
    ).strip()


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def generate(args):
    root = Path(args.repo_root).resolve()
    evidence = Path(args.evidence_dir).resolve()
    report_path = safe_file(evidence, args.report, [], "input.report")
    if report_path is None:
        raise ValueError("missing or unsafe input report")
    report = read_json(report_path)
    if not isinstance(report, dict):
        raise ValueError("report must be JSON object")
    now = datetime.now(timezone.utc)
    tested = git(root, "rev-parse", "HEAD")
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    candidate = args.candidate_sha
    base = args.base_sha if event == "pull_request" else None
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "0"))
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if event not in ("push", "pull_request") or not run_id.isdigit() or attempt < 1:
        raise ValueError("missing CI event/run identity; no fabricated local execution allowed")
    if repository != args.repository:
        raise ValueError("repository differs from authenticated CI environment")
    if event == "push" and candidate != tested:
        raise ValueError("push candidate must equal tested SHA")
    if event == "pull_request" and (not base or _git_parents(root, tested) != (base, candidate)):
        raise ValueError("PR synthetic merge parents not bound to base/head")
    if any(report.get(k) != value for k, value in (
        ("runId", run_id), ("runAttempt", attempt), ("testedSha", tested),
        ("candidateSha", candidate), ("event", event)
    )):
        raise ValueError("report identity does not match CI runtime")
    for key in ("tests", "assertions"):
        if type(report.get(key)) is not int or report[key] <= 0:
            raise ValueError("report " + key + " must be positive")
    if type(report.get("skipped")) is not int or report["skipped"] != 0:
        raise ValueError("unplanned skipped tests")
    if type(report.get("failed")) is not int or report["failed"] != 0:
        raise ValueError("executed suite reports failure")
    if type(report.get("exitCode")) is not int or report["exitCode"] != 0:
        raise ValueError("executed command did not succeed")
    if not isinstance(report.get("negativeControls"), list) or not report["negativeControls"]:
        raise ValueError("negative controls must be recorded by the runner")
    start = datetime.fromisoformat(report["startedAt"].replace("Z", "+00:00"))
    finish = datetime.fromisoformat(report["finishedAt"].replace("Z", "+00:00"))
    if start.tzinfo is None or finish.tzinfo is None or not start <= finish <= now:
        raise ValueError("report timestamps are missing, future, or reversed")
    if (now - finish) > timedelta(hours=1):
        raise ValueError("stale report must not be republished as current execution")

    cfg_files = {}
    for name in args.config:
        path = safe_file(root, name, [], "configuration")
        if path is None:
            raise ValueError("unsafe or missing configuration file")
        cfg_files[name] = sha_file(path)
    if not cfg_files:
        raise ValueError("at least one explicit config input required")
    lockfiles = {}
    for name in args.lockfile:
        path = safe_file(root, name, [], "lockfile")
        if path is None:
            raise ValueError("unsafe or missing lockfile")
        lockfiles[name] = sha_file(path)
    source_digest = git_source_digest(root, tested)
    if not source_digest:
        raise ValueError("cannot compute tested source-tree digest")
    tool_versions = {
        "python": platform.python_version(),
        "git": git(root, "--version"),
    }
    own_path = "scripts/ci/emit_evidence.py"
    producer = safe_file(root, own_path, [], "producer")
    if producer is None:
        raise ValueError("producer source absent from current checkout")
    duration_days = args.retention_days
    if not 1 <= duration_days <= 90:
        raise ValueError("GitHub artifact retention must be within 1..90 days")
    manifest = {
        "schemaVersion": "1.0.0",
        "repository": repository,
        "module": args.module,
        "candidateSha": candidate,
        "testedSha": tested,
        "baseSha": base,
        "producer": {"name": own_path, "sourceSha": tested, "sha256": sha_file(producer)},
        "workflow": os.environ.get("GITHUB_WORKFLOW", "unspecified"),
        "runId": run_id,
        "runAttempt": attempt,
        "event": event,
        "environment": {
            "runner": os.environ.get("RUNNER_NAME", "github-hosted-unspecified"),
            "os": os.environ.get("RUNNER_OS", platform.system()),
            "toolVersions": tool_versions,
            "sourceTreeDigest": source_digest,
            "configurationDigest": configuration_digest(cfg_files),
            "configurationFiles": cfg_files,
            "lockfiles": lockfiles,
        },
        "verification": {
            "mode": "EXECUTED_CI" if os.environ.get("GITHUB_ACTIONS") == "true" else "EXECUTED_LOCAL",
            "result": "PASS",
            "checks": [
                {"id": args.check_id, "commandId": args.command_id,
                 "exitCode": report["exitCode"], "testCount": report["tests"],
                 "expectedAssertions": report["assertions"],
                 "skippedTests": report["skipped"],
                 "report": args.report,
                 "negativeControls": report["negativeControls"]},
            ],
        },
        "artifacts": [],
        "limitations": [
            "Artifact digests detect tampering, not authenticity of the runner.",
            "Offline tests do not prove cloud deployment or authenticated device readiness.",
            "Automated verification is not independent review or human acceptance.",
        ],
        "approvalEffective": False,
        "timing": {
            "startedAt": report["startedAt"], "finishedAt": report["finishedAt"],
            "verifiedAt": iso(now),
        },
        "retention": {
            "days": duration_days, "provider": "github-actions",
            "expiresAt": iso(now + timedelta(days=duration_days)),
        },
        "attestations": [],
    }
    for name in [args.report, *args.artifact]:
        if any(a["path"] == name for a in manifest["artifacts"]):
            raise ValueError("duplicate artifact path")
        source = safe_file(evidence, name, [], "artifact")
        if source is None:
            raise ValueError("unsafe or absent artifact")
        manifest["artifacts"].append({
            "path": name, "sha256": sha_file(source), "bytes": source.stat().st_size
        })
    expected = {
        "repository": repository, "candidateSha": candidate,
        "testedSha": tested, "baseSha": base,
        "runId": run_id, "runAttempt": attempt, "event": event,
        "sourceTreeDigest": source_digest,
    }
    errors = verify(manifest, evidence, root, expected=expected,
                    parents=_git_parents(root, tested))
    if errors:
        raise ValueError("invalid generated evidence: " + "; ".join(errors))
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--base-sha")
    parser.add_argument("--config", action="append", default=[])
    parser.add_argument("--lockfile", action="append", default=[])
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--check-id", required=True)
    parser.add_argument("--command-id", required=True)
    parser.add_argument("--retention-days", type=int, default=7)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        manifest = generate(args)
        Path(args.out).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print("EVIDENCE GENERATION FAILED: " + type(error).__name__ + ": " + str(error), file=sys.stderr)
        return 1
    print("EVIDENCE GENERATED: strict schema v1 (authenticated publication separately required)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
