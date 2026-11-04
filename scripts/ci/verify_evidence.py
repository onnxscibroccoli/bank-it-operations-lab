#!/usr/bin/env python3
"""Strict portfolio-evidence-v1 verifier. This does not grant human acceptance.

Stdlib only, for NEW bundles. Historical evidence remains owned by the
separate evidence/shared compatibility validator.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
FIELD = re.compile(r"^[A-Za-z0-9._/-]+$")


class EvidenceError(ValueError):
    pass


def no_duplicates(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise EvidenceError("duplicate JSON key: " + key)
        data[key] = value
    return data


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicates,
                      parse_constant=lambda c: (_ for _ in ()).throw(EvidenceError("non-JSON number")))


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_object(item, fields, label, errors, required=None):
    if not isinstance(item, dict):
        errors.append(label + ": expected object")
        return {}
    unknown = sorted(set(item) - set(fields))
    missing = sorted(set(required if required is not None else fields) - set(item))
    if unknown:
        errors.append(label + ": unknown fields " + ", ".join(unknown))
    if missing:
        errors.append(label + ": missing fields " + ", ".join(missing))
    return item


def sha(value, label, errors, length=40):
    if not isinstance(value, str) or not (HEX40 if length == 40 else HEX64).fullmatch(value):
        errors.append(label + ": invalid sha" + str(length))
        return False
    return True


def safe_file(root, relative, errors, label):
    if not isinstance(relative, str) or not relative or not FIELD.fullmatch(relative):
        errors.append(label + ": unsafe path")
        return None
    parts = PurePosixPath(relative).parts
    if relative.startswith("/") or any(part in (".", "..") for part in parts):
        errors.append(label + ": unsafe traversal")
        return None
    path = Path(root)
    for part in parts:
        path = path / part
        if path.is_symlink():
            errors.append(label + ": symlink traversal not permitted")
            return None
    if not path.is_file():
        errors.append(label + ": file missing")
        return None
    return path


def configuration_digest(hashes):
    # Canonical mapping: path + NUL + SHA256 + LF, sorted by UTF-8 path.
    return hashlib.sha256(b"".join(
        k.encode("utf-8") + b"\x00" + hashes[k].encode("ascii") + b"\n"
        for k in sorted(hashes)
    )).hexdigest()


def git_source_digest(root, tested):
    try:
        tree = subprocess.check_output(
            ["git", "-C", str(root), "ls-tree", "-r", "--full-tree", "-z", tested],
            stderr=subprocess.DEVNULL, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return hashlib.sha256(tree).hexdigest()


def parse_time(value, label, errors):
    if not isinstance(value, str):
        errors.append(label + ": timestamp is not a string")
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("timezone missing")
        return dt.astimezone(timezone.utc)
    except ValueError:
        errors.append(label + ": invalid timezone-aware timestamp")
        return None


def verify(payload, evidence_dir, repo_root, *, expected, parents=None):
    errors = []
    root_fields = {
        "schemaVersion", "repository", "module", "candidateSha", "testedSha",
        "baseSha", "producer", "workflow", "runId", "runAttempt", "event",
        "environment", "verification", "artifacts", "limitations",
        "approvalEffective", "timing", "retention", "attestations",
    }
    p = strict_object(payload, root_fields, "root", errors)
    if p.get("schemaVersion") != "1.0.0":
        errors.append("root: incorrect schema version")
    if not isinstance(p.get("repository"), str) or not REPO.fullmatch(p["repository"]):
        errors.append("root: invalid repository")
    if not isinstance(p.get("module"), str) or not p["module"]:
        errors.append("root: module missing")
    for field in ("candidateSha", "testedSha"):
        sha(p.get(field), field, errors)
    if p.get("baseSha") is not None:
        sha(p["baseSha"], "baseSha", errors)
    if p.get("event") not in ("pull_request", "push"):
        errors.append("event: unknown")
    if not isinstance(p.get("runId"), str) or not p["runId"].isdigit():
        errors.append("runId: invalid")
    if type(p.get("runAttempt")) is not int or p["runAttempt"] < 1:
        errors.append("runAttempt: invalid")
    if not isinstance(p.get("workflow"), str) or not p["workflow"]:
        errors.append("workflow: missing")
    if p.get("approvalEffective") is not False:
        errors.append("approvalEffective: candidate evidence cannot grant human approval")

    if p.get("event") == "push" and (p.get("baseSha") is not None or
                                       p.get("candidateSha") != p.get("testedSha")):
        errors.append("direct push must have candidateSha=testedSha and baseSha=null")
    if p.get("event") == "pull_request":
        if p.get("baseSha") is None or p.get("candidateSha") == p.get("testedSha"):
            errors.append("pull request must bind a distinct two-parent tested merge")
        if parents is None or tuple(parents) != (p.get("baseSha"), p.get("candidateSha")):
            errors.append("tested merge parents differ from baseSha/candidateSha")

    if not isinstance(expected, dict) or not expected:
        errors.append("independent expected execution identity is required")
    else:
        for field in ("repository", "candidateSha", "testedSha", "baseSha", "runId",
                      "runAttempt", "event"):
            if field not in expected or expected[field] != p.get(field):
                errors.append(field + ": mismatched expected execution identity")

    producer = strict_object(p.get("producer"), {"name", "sourceSha", "sha256"},
                             "producer", errors)
    if producer.get("sourceSha") != p.get("testedSha"):
        errors.append("producer.sourceSha must identify actual tested revision")
    sha(producer.get("sha256"), "producer.sha256", errors, 64)
    source = safe_file(repo_root, producer.get("name"), errors, "producer.name")
    if source is not None and sha_file(source) != producer.get("sha256"):
        errors.append("producer: script source hash mismatch")

    env = strict_object(p.get("environment"),
                        {"runner", "os", "toolVersions", "sourceTreeDigest",
                         "configurationDigest", "configurationFiles", "lockfiles"},
                        "environment", errors)
    for field in ("runner", "os"):
        if not isinstance(env.get(field), str) or not env[field]:
            errors.append("environment." + field + ": empty")
    tools = env.get("toolVersions")
    if not isinstance(tools, dict) or not tools or any(
        not isinstance(k, str) or not isinstance(v, str) or not v for k, v in tools.items()
    ):
        errors.append("environment.toolVersions: must record non-empty versions")
    sha(env.get("sourceTreeDigest"), "environment.sourceTreeDigest", errors, 64)
    sha(env.get("configurationDigest"), "environment.configurationDigest", errors, 64)
    expected_tree = expected.get("sourceTreeDigest") if isinstance(expected, dict) else None
    if not expected_tree or expected_tree != env.get("sourceTreeDigest"):
        errors.append("source-tree digest differs from independently computed identity")
    for field in ("configurationFiles", "lockfiles"):
        files = env.get(field)
        if not isinstance(files, dict):
            errors.append("environment." + field + ": expected mapping")
            continue
        for path, digest in files.items():
            sha(digest, field + ":" + path, errors, 64)
            f = safe_file(repo_root, path, errors, field + ":" + path)
            if f is not None and sha_file(f) != digest:
                errors.append(field + ":" + path + ": digest mismatch")
    conf = env.get("configurationFiles")
    if not isinstance(conf, dict) or not conf:
        errors.append("environment.configurationFiles must not be empty")
    elif env.get("configurationDigest") != configuration_digest(conf):
        errors.append("environment.configurationDigest: invalid canonical digest")

    verification = strict_object(p.get("verification"),
                                 {"mode", "result", "checks"}, "verification", errors)
    if verification.get("mode") != "EXECUTED_CI" or verification.get("result") != "PASS":
        errors.append("release-grade strict verification requires EXECUTED_CI/PASS")
    checks = verification.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append("verification.checks: no test records")
        checks = []
    artifacts = p.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts: empty")
        artifacts = []
    artifact_paths = set()
    for item in artifacts:
        art = strict_object(item, {"path", "sha256", "bytes"}, "artifact", errors)
        name = art.get("path")
        if name in artifact_paths:
            errors.append("artifact: duplicate path")
        artifact_paths.add(name)
        sha(art.get("sha256"), "artifact.sha256", errors, 64)
        if type(art.get("bytes")) is not int or art["bytes"] < 1:
            errors.append("artifact.bytes: invalid")
        f = safe_file(evidence_dir, name, errors, "artifact:" + str(name))
        if f is not None:
            if sha_file(f) != art.get("sha256") or f.stat().st_size != art.get("bytes"):
                errors.append("artifact:" + str(name) + ": hash or size mismatch")

    seen_checks = set()
    for item in checks:
        check = strict_object(item,
            {"id", "commandId", "exitCode", "testCount", "expectedAssertions",
             "skippedTests", "report", "negativeControls"}, "check", errors)
        if check.get("id") in seen_checks:
            errors.append("duplicate test check id")
        seen_checks.add(check.get("id"))
        if type(check.get("exitCode")) is not int or check["exitCode"] != 0:
            errors.append("check: execution exit is not zero")
        for field in ("testCount", "expectedAssertions"):
            if type(check.get(field)) is not int or check[field] <= 0:
                errors.append("check." + field + ": must be positive")
        if type(check.get("skippedTests")) is not int or check["skippedTests"] != 0:
            errors.append("check: unexpected skipped tests")
        if not isinstance(check.get("commandId"), str) or not check["commandId"]:
            errors.append("check: missing command identifier")
        report = check.get("report")
        if report not in artifact_paths:
            errors.append("check: missing report artifact")
        file = safe_file(evidence_dir, report, errors, "check.report")
        negatives = check.get("negativeControls")
        if not isinstance(negatives, list) or not negatives:
            errors.append("check: missing negative controls")
            negatives = []
        ids = set()
        for n in negatives:
            n = strict_object(n, {"id", "status", "observedReason"}, "negative", errors)
            if n.get("id") in ids:
                errors.append("negative: duplicate id")
            ids.add(n.get("id"))
            if n.get("status") != "REJECTED_AS_EXPECTED" or not n.get("observedReason"):
                errors.append("negative: not rejected for an explicit reason")
        if file is None:
            continue
        try:
            data = read_json(file)
        except (ValueError, OSError, UnicodeError) as exc:
            errors.append("check report JSON invalid: " + type(exc).__name__)
            continue
        if not isinstance(data, dict) or any(
            data.get(key) != check.get(expected_key)
            for key, expected_key in (
                ("tests", "testCount"), ("assertions", "expectedAssertions"),
                ("skipped", "skippedTests"), ("exitCode", "exitCode"))
        ) or data.get("failed") != 0:
            errors.append("check: test report counts/exit mismatch")
        if not isinstance(data.get("negativeControls"), list):
            errors.append("check: negative control evidence missing from report")
        else:
            recorded = {(n.get("id"), n.get("status"), n.get("observedReason"))
                        for n in data["negativeControls"] if isinstance(n, dict)}
            expected_neg = {(n.get("id"), n.get("status"), n.get("observedReason"))
                            for n in negatives if isinstance(n, dict)}
            if recorded != expected_neg:
                errors.append("check: negative control reason/outcome mismatch")
    limitations = p.get("limitations")
    if not isinstance(limitations, list) or any(not isinstance(s, str) for s in limitations):
        errors.append("limitations: invalid")
    att = p.get("attestations")
    if not isinstance(att, list):
        errors.append("attestations: must be a list")
    else:
        for a in att:
            a = strict_object(a, {"type", "reference"}, "attestation", errors)
            if a.get("type") not in ("github-artifact-attestation", "external") or not a.get("reference"):
                errors.append("attestation: invalid reference")
    timing = strict_object(p.get("timing"),
                           {"startedAt", "finishedAt", "verifiedAt"}, "timing", errors)
    start = parse_time(timing.get("startedAt"), "startedAt", errors)
    finished = parse_time(timing.get("finishedAt"), "finishedAt", errors)
    verified = parse_time(timing.get("verifiedAt"), "verifiedAt", errors)
    if start and finished and verified and not start <= finished <= verified:
        errors.append("timing: non-monotonic timestamps")
    retention = strict_object(p.get("retention"),
                               {"days", "provider", "expiresAt"}, "retention", errors)
    days = retention.get("days")
    if type(days) is not int or days < 1 or days > 90:
        errors.append("retention: days must be 1..90")
    if retention.get("provider") not in ("github-actions", "external-object-store"):
        errors.append("retention: invalid provider")
    expiry = parse_time(retention.get("expiresAt"), "expiresAt", errors)
    if verified and expiry and expiry <= verified:
        errors.append("retention: evidence already expired")
    return sorted(set(errors))


def _git_parents(root, sha_ref):
    try:
        text = subprocess.check_output(
            ["git", "-C", str(root), "rev-list", "--parents", "-n", "1", sha_ref],
            stderr=subprocess.DEVNULL, text=True, timeout=10
        ).strip().split()
        return tuple(text[1:]) if text and text[0] == sha_ref else None
    except (OSError, subprocess.SubprocessError):
        return None


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--expected-repository", required=True)
    parser.add_argument("--expected-candidate-sha", required=True)
    parser.add_argument("--expected-tested-sha", required=True)
    parser.add_argument("--expected-base-sha", default="")
    parser.add_argument("--expected-run-id", required=True)
    parser.add_argument("--expected-run-attempt", type=int, required=True)
    parser.add_argument("--expected-event", choices=["push", "pull_request"], required=True)
    args = parser.parse_args(argv)
    try:
        p = read_json(args.manifest)
        tested = args.expected_tested_sha
        trusted_tree = git_source_digest(args.repo_root, tested)
        expected = {
            "repository": args.expected_repository,
            "candidateSha": args.expected_candidate_sha,
            "testedSha": tested,
            "baseSha": args.expected_base_sha or None,
            "runId": args.expected_run_id,
            "runAttempt": args.expected_run_attempt,
            "event": args.expected_event,
            "sourceTreeDigest": trusted_tree,
        }
        issues = verify(p, args.evidence_dir, args.repo_root,
                        expected=expected, parents=_git_parents(args.repo_root, tested))
    except (EvidenceError, OSError, ValueError, json.JSONDecodeError) as error:
        issues = ["manifest parse failure: " + type(error).__name__]
    for issue in issues:
        print("INVALID: " + issue)
    if issues:
        print("STRICT EVIDENCE FAIL", file=sys.stderr)
        return 1
    print("STRICT EVIDENCE PASS: structured contents verified (not cryptographic execution authenticity)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
