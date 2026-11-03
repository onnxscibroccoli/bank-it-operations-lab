#!/usr/bin/env python3
"""Acceptance check runner for bank-it-operations-lab (stdlib only, offline, credential-free).

Runs the checks declared in a checked-in, allowlisted definition file (default
tools/acceptance/checks.json) and writes an evidence bundle that the existing shared
validator (evidence/shared/validate_evidence.py) then verifies:

  <run-dir>/COMMANDS.tsv   10-column layout (validate_evidence.py commands --format postgres-10col)
  <run-dir>/logs/NN_<id>.log   argv, stdout, stderr, per-stage exit codes, "# exit_code=N ..." trailer
  <run-dir>/artifacts/<id>/... copies of declared artifacts (regular files inside the repo only)
  <run-dir>/RUN.json       run + per-check metadata (argv, UTC timestamps, tool versions, source state)
  <run-dir>/SHA256SUMS     sha256sum(1) over every file above (validate_evidence.py hashes)
  <run-dir>/VALIDATION.log output of the shared validator (written after SHA256SUMS; not hashed)

Safety properties:
  * Commands come ONLY from the definition file, as argv arrays (no shell, no string
    interpolation). argv[0] must be a bare program name in ALLOWED_PROGRAMS; shells and
    interpreters-with-eval (bash, sh, env, xargs, ...) are not allowlisted. Nothing read from
    a command's output or from an artifact is ever executed.
  * Every check has a bounded timeout; on expiry the whole process group gets SIGTERM, then
    SIGKILL after a grace period. Timeout exit code is 124 (as timeout(1)).
  * Pipelines use pipefail semantics: the exit code is the rightmost non-zero stage status.
  * Evidence/artifact paths are repo- or workspace-relative; absolute paths, '..' components
    and symlinks on any component are rejected, and the resolved path must stay inside the
    allowed root.

Exit codes: 0 all checks passed and the bundle validated; 1 a check failed or validation
failed; 2 usage / definition / path-safety error (nothing executed).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
DEFAULT_CHECKS = HERE / "checks.json"
DEFAULT_WORKSPACE = HERE / "runs"
SHARED_VALIDATOR_REL = "evidence/shared/validate_evidence.py"
RUNNER_VERSION = "0.1.0"
TIMEOUT_EXIT = 124
KILL_GRACE_S = 2.0
MAX_TIMEOUT_S = 1800

# Programs a check may invoke. Deliberately excludes shells and anything that runs a string as
# a command (bash, sh, env, xargs, find -exec, eval, sudo, ssh, curl, aws, az, ...).
ALLOWED_PROGRAMS = frozenset({
    "python3", "git", "sha256sum", "grep", "sort", "head", "tail", "wc", "diff", "cat", "true", "false",
})
# How to ask each allowlisted program for its version (bounded, captured per check).
VERSION_ARGS = {
    "python3": ["--version"], "git": ["--version"], "sha256sum": ["--version"], "grep": ["--version"],
    "sort": ["--version"], "head": ["--version"], "tail": ["--version"], "wc": ["--version"],
    "diff": ["--version"], "cat": ["--version"],
}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
CHECK_KEYS = {"id", "description", "argv", "pipeline", "timeout_s", "expect", "cwd", "artifacts"}
SCRUB_ENV = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_PROFILE", "AWS_DEFAULT_PROFILE",
             "AWS_ROLE_ARN", "AWS_WEB_IDENTITY_TOKEN_FILE", "AWS_CONTAINER_CREDENTIALS_FULL_URI",
             "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI", "AZURE_CLIENT_SECRET", "GITHUB_TOKEN", "GH_TOKEN")


class DefinitionError(ValueError):
    """The check definition file is invalid or asks for something not allowlisted."""


class PathEscapeError(ValueError):
    """A path would resolve outside its allowed root."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# ----------------------------------------------------------------------------- path confinement
def confine(root: Path, rel: str, *, must_exist: bool = False) -> Path:
    """Resolve repo/workspace-relative `rel` under `root`, refusing any escape.

    Rejects: non-strings, empty, NUL, absolute paths, backslashes, '..' components, and a symlink
    at ANY existing component (so a link cannot redirect a write or read outside the root).
    """
    if not isinstance(rel, str) or not rel or "\x00" in rel or "\\" in rel:
        raise PathEscapeError(f"invalid path {rel!r}")
    p = PurePosixPath(rel)
    if p.is_absolute() or rel.startswith("~"):
        raise PathEscapeError(f"absolute path not allowed: {rel!r}")
    if any(part == ".." for part in p.parts):
        raise PathEscapeError(f"'..' traversal not allowed: {rel!r}")
    root_r = Path(root).resolve(strict=True)
    cur = root_r
    for part in p.parts:
        if part == ".":
            continue
        cur = cur / part
        if cur.is_symlink():
            raise PathEscapeError(f"symlink in path not allowed: {rel!r} ({cur} is a symlink)")
        if not cur.exists():
            if must_exist:
                raise PathEscapeError(f"path does not exist: {rel!r}")
            break
    final = (root_r / p).resolve(strict=False)
    if final != root_r and root_r not in final.parents:
        raise PathEscapeError(f"path escapes {root_r}: {rel!r}")
    return final


def _safe_write(path: Path, data: bytes) -> None:
    """Create a new file without following a symlink at the final component."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


# ----------------------------------------------------------------------------- definition loading
def _validate_argv(argv, where: str) -> list[str]:
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) for a in argv):
        raise DefinitionError(f"{where}: argv must be a non-empty array of strings")
    if any("\x00" in a for a in argv):
        raise DefinitionError(f"{where}: NUL byte in argv")
    prog = argv[0]
    if "/" in prog or prog not in ALLOWED_PROGRAMS:
        raise DefinitionError(f"{where}: program {prog!r} is not allowlisted (allowed: {sorted(ALLOWED_PROGRAMS)})")
    return list(argv)


def load_definition(path: Path, repo_root: Path) -> dict:
    """Parse and strictly validate a check definition. Raises DefinitionError; executes nothing."""
    path = Path(path)
    if path.is_symlink():
        raise DefinitionError(f"{path}: definition file must not be a symlink")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise DefinitionError(f"{path}: cannot read definition: {e}") from e
    if not isinstance(doc, dict) or doc.get("schema") != "bank-it-operations-lab/acceptance-checks@1":
        raise DefinitionError(f"{path}: schema must be 'bank-it-operations-lab/acceptance-checks@1'")
    checks = doc.get("checks")
    if not isinstance(checks, list) or not checks:
        raise DefinitionError(f"{path}: 'checks' must be a non-empty array")
    seen: set[str] = set()
    out = []
    for i, c in enumerate(checks):
        where = f"{path.name}: checks[{i}]"
        if not isinstance(c, dict):
            raise DefinitionError(f"{where}: must be an object")
        extra = set(c) - CHECK_KEYS
        if extra:
            raise DefinitionError(f"{where}: unknown keys {sorted(extra)}")
        cid = c.get("id")
        if not isinstance(cid, str) or not ID_RE.match(cid):
            raise DefinitionError(f"{where}: id must match {ID_RE.pattern}")
        if cid in seen:
            raise DefinitionError(f"{where}: duplicate id {cid!r}")
        seen.add(cid)
        where = f"{path.name}: check {cid}"
        if ("argv" in c) == ("pipeline" in c):
            raise DefinitionError(f"{where}: exactly one of 'argv' or 'pipeline' is required")
        if "argv" in c:
            stages = [_validate_argv(c["argv"], where)]
        else:
            pl = c["pipeline"]
            if not isinstance(pl, list) or len(pl) < 2:
                raise DefinitionError(f"{where}: pipeline must be an array of >= 2 argv arrays")
            stages = [_validate_argv(s, f"{where} stage {n}") for n, s in enumerate(pl)]
        t = c.get("timeout_s")
        if not isinstance(t, (int, float)) or isinstance(t, bool) or not (0 < t <= MAX_TIMEOUT_S):
            raise DefinitionError(f"{where}: timeout_s is required, 0 < timeout_s <= {MAX_TIMEOUT_S}")
        expect = c.get("expect", "zero")
        if expect not in ("zero", "nonzero"):
            raise DefinitionError(f"{where}: expect must be 'zero' or 'nonzero'")
        cwd_rel = c.get("cwd", ".")
        try:
            cwd = confine(repo_root, cwd_rel, must_exist=True)
        except PathEscapeError as e:
            raise DefinitionError(f"{where}: cwd: {e}") from e
        arts = c.get("artifacts", [])
        if not isinstance(arts, list) or not all(isinstance(a, str) for a in arts):
            raise DefinitionError(f"{where}: artifacts must be an array of repo-relative paths")
        for a in arts:
            try:
                confine(repo_root, a)
            except PathEscapeError as e:
                raise DefinitionError(f"{where}: artifact: {e}") from e
        out.append({"id": cid, "description": str(c.get("description", "")), "stages": stages,
                    "timeout_s": float(t), "expect": expect, "cwd_rel": cwd_rel, "cwd": cwd, "artifacts": arts})
    return {"path": path, "checks": out}


# ----------------------------------------------------------------------------- execution
def _clean_env() -> dict:
    env = {k: v for k, v in os.environ.items() if k not in SCRUB_ENV}
    env.update({"LC_ALL": "C.UTF-8", "AWS_EC2_METADATA_DISABLED": "true", "AWS_CONFIG_FILE": "/dev/null",
                "AWS_SHARED_CREDENTIALS_FILE": "/dev/null", "PYTHONDONTWRITEBYTECODE": "1", "GIT_TERMINAL_PROMPT": "0"})
    return env


def _resolve(prog: str) -> str:
    if prog == "python3":
        return sys.executable  # the interpreter running the runner, recorded in versions
    found = shutil.which(prog)
    if not found:
        raise FileNotFoundError(f"allowlisted program {prog!r} not found on PATH")
    return found


def _status(rc: int) -> int:
    return 128 - rc if rc < 0 else rc  # signal N -> 128+N, as a shell reports it


def run_stages(stages: list[list[str]], cwd: Path, timeout_s: float, stdout_path: Path, stderr_dir: Path) -> dict:
    """Run one argv or a pipeline in its own process group with a hard timeout.

    Returns {"exit_code", "stage_exit_codes", "timed_out"}; exit_code follows pipefail.
    """
    env = _clean_env()
    procs: list[subprocess.Popen] = []
    errs = []
    out_f = open(stdout_path, "xb")
    pgid = None
    try:
        prev = None
        for n, argv in enumerate(stages):
            last = n == len(stages) - 1
            err_f = open(stderr_dir / f"stderr.{n}", "xb")
            errs.append(err_f)
            kw = {"process_group": 0} if pgid is None else {"process_group": pgid}
            try:
                p = subprocess.Popen([_resolve(argv[0])] + argv[1:], cwd=cwd, env=env, shell=False,
                                     stdin=prev.stdout if prev else subprocess.DEVNULL,
                                     stdout=out_f if last else subprocess.PIPE, stderr=err_f,
                                     close_fds=True, **kw)
            except (OSError, FileNotFoundError) as e:
                err_f.write(f"runner: cannot start stage {n}: {e}\n".encode())
                _kill_group(pgid)
                for q in procs:
                    q.wait()
                return {"exit_code": 127, "stage_exit_codes": [_status(q.returncode) for q in procs] + [127],
                        "timed_out": False}
            if pgid is None:
                pgid = p.pid
            if prev is not None:
                prev.stdout.close()  # so the upstream stage gets SIGPIPE if downstream exits
            procs.append(p)
            prev = p
        deadline = time.monotonic() + timeout_s
        timed_out = False
        for p in procs:
            remaining = deadline - time.monotonic()
            try:
                p.wait(timeout=max(remaining, 0.001))
            except subprocess.TimeoutExpired:
                timed_out = True
                break
        if timed_out:
            _kill_group(pgid)
            for p in procs:
                p.wait()
        else:
            _kill_group(pgid, term_only=True, quiet=True)  # reap stragglers left in the group
        codes = [_status(p.returncode) for p in procs]
        if timed_out:
            rc = TIMEOUT_EXIT
        else:
            nonzero = [c for c in codes if c != 0]
            rc = nonzero[-1] if nonzero else 0  # pipefail: rightmost non-zero
        return {"exit_code": rc, "stage_exit_codes": codes, "timed_out": timed_out}
    finally:
        out_f.close()
        for f in errs:
            f.close()


def _kill_group(pgid, term_only: bool = False, quiet: bool = False) -> None:
    if pgid is None:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    if term_only:
        return
    end = time.monotonic() + KILL_GRACE_S
    while time.monotonic() < end:
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def tool_version(prog: str) -> str:
    if prog not in VERSION_ARGS:
        return "n/a"
    try:
        r = subprocess.run([_resolve(prog)] + VERSION_ARGS[prog], capture_output=True, timeout=5, env=_clean_env())
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"unavailable ({e.__class__.__name__})"
    text = (r.stdout or r.stderr).decode(errors="replace").strip().splitlines()
    return text[0] if text else f"unknown (exit {r.returncode})"


def source_state(repo_root: Path) -> dict:
    def git(*args):
        try:
            r = subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True, timeout=15, env=_clean_env())
            return r.returncode, r.stdout.decode(errors="replace").strip()
        except (OSError, subprocess.TimeoutExpired):
            return 1, ""
    rc, head = git("rev-parse", "HEAD")
    if rc != 0:
        return {"git": False, "head": None, "branch": None, "dirty": None, "status_porcelain": []}
    _, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    _, status = git("status", "--porcelain=v1", "--untracked-files=normal")
    lines = [l for l in status.splitlines() if l]
    return {"git": True, "head": head, "branch": branch, "dirty": bool(lines), "status_porcelain": lines}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def definition_provenance(path: Path, repo_root: Path) -> dict:
    """Whether the definition file is tracked by git and unmodified at HEAD."""
    try:
        rel = str(Path(path).resolve().relative_to(Path(repo_root).resolve()))
    except ValueError:
        return {"path": str(path), "tracked": False, "clean": False}
    def ok(*args):
        try:
            return subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True, timeout=15).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False
    tracked = ok("ls-files", "--error-unmatch", "--", rel)
    clean = tracked and ok("diff", "--quiet", "HEAD", "--", rel)
    return {"path": rel, "tracked": tracked, "clean": clean}


def _copy_artifact(repo_root: Path, rel: str, dest_root: Path) -> dict:
    try:
        src = confine(repo_root, rel, must_exist=True)
    except PathEscapeError as e:
        return {"path": rel, "status": "REJECTED", "reason": str(e)}
    if not src.is_file() or src.is_symlink():
        return {"path": rel, "status": "REJECTED", "reason": "not a regular file"}
    dest_root.mkdir(parents=True, exist_ok=True)
    dest = confine(dest_root, rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "rb") as f:
        _safe_write(dest, f.read())
    return {"path": rel, "status": "COPIED", "sha256": sha256_file(dest), "bytes": dest.stat().st_size}


def run_checks(definition: dict, repo_root: Path, workspace: Path, label: str, *,
               validator: Path | None = None, provenance: dict | None = None) -> dict:
    """Execute every check, write the evidence bundle, then validate it with the shared validator."""
    if not LABEL_RE.match(label):
        raise PathEscapeError(f"invalid run label {label!r}")
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    if workspace.is_symlink():
        raise PathEscapeError(f"workspace must not be a symlink: {workspace}")
    run_dir = confine(workspace, label)
    if run_dir.exists():
        raise PathEscapeError(f"run directory already exists: {run_dir}")
    run_dir.mkdir()
    (run_dir / "logs").mkdir()
    tmp = run_dir / ".tmp"
    tmp.mkdir()

    run_meta = {
        "schema": "bank-it-operations-lab/acceptance-run@1",
        "runner": {"path": "tools/acceptance/runner.py", "version": RUNNER_VERSION, "sha256": sha256_file(Path(__file__))},
        "label": label,
        "started_utc": utc_now(),
        "host": {"python": sys.version.split()[0], "python_executable": sys.executable,
                 "platform": platform.platform(), "machine": platform.machine()},
        "source": source_state(repo_root),
        "definition": dict(provenance or {}, sha256=sha256_file(definition["path"])),
        "checks": [],
    }
    tsv = ["seq\tstep_id\tkind\texpected_exit\texit_code\tresult\tstarted_utc\tduration_ms\tlog\tcommand"]
    versions_cache: dict[str, str] = {}
    all_ok = True
    for seq, c in enumerate(definition["checks"], 1):
        progs = sorted({s[0] for s in c["stages"]})
        versions = {p: versions_cache.setdefault(p, tool_version(p)) for p in progs}
        sdir = tmp / c["id"]
        sdir.mkdir()
        started = utc_now()
        t0 = time.monotonic()
        res = run_stages(c["stages"], c["cwd"], c["timeout_s"], sdir / "stdout", sdir)
        dur_ms = int((time.monotonic() - t0) * 1000)
        ended = utc_now()
        rc = res["exit_code"]
        ok = (not res["timed_out"]) and ((rc == 0) if c["expect"] == "zero" else (rc != 0))
        result = "PASS" if ok else ("TIMEOUT" if res["timed_out"] else "FAIL")
        all_ok &= ok
        arts = [_copy_artifact(repo_root, a, confine(run_dir, f"artifacts/{c['id']}")) for a in c["artifacts"]]
        if any(a["status"] != "COPIED" for a in arts):
            all_ok = False
            result = "FAIL" if result == "PASS" else result
        log_rel = f"logs/{seq:02d}_{c['id']}.log"
        cmd_display = " | ".join(json.dumps(s) for s in c["stages"])
        parts = [f"$ {cmd_display}\n", f"# cwd: {c['cwd_rel']}\n", f"# started_utc: {started}\n",
                 f"# ended_utc: {ended}\n", f"# timeout_s: {c['timeout_s']:g}\n",
                 f"# versions: {json.dumps(versions)}\n", "--- stdout ---\n"]
        body = (sdir / "stdout").read_bytes().decode(errors="replace")
        parts.append(_neutralise(body))
        for n in range(len(c["stages"])):
            parts.append(f"--- stderr stage {n} ---\n")
            parts.append(_neutralise((sdir / f"stderr.{n}").read_bytes().decode(errors="replace")))
        parts.append(f"# stage_exit_codes: {res['stage_exit_codes']}\n")
        parts.append(f"# exit_code={rc} expected={c['expect']} result={result} timed_out={str(res['timed_out']).lower()} "
                     f"started_utc={started} duration_ms={dur_ms}\n")
        _safe_write(run_dir / log_rel, "".join(parts).encode())
        tsv.append("\t".join([str(seq), c["id"], "acceptance", c["expect"], str(rc), result if result != "TIMEOUT" else "FAIL",
                              started, str(dur_ms), log_rel, cmd_display.replace("\t", " ")]))
        run_meta["checks"].append({
            "seq": seq, "id": c["id"], "description": c["description"], "argv": c["stages"][0] if len(c["stages"]) == 1 else None,
            "pipeline": c["stages"] if len(c["stages"]) > 1 else None, "cwd": c["cwd_rel"], "timeout_s": c["timeout_s"],
            "expect": c["expect"], "started_utc": started, "ended_utc": ended, "duration_ms": dur_ms,
            "exit_code": rc, "stage_exit_codes": res["stage_exit_codes"], "timed_out": res["timed_out"], "result": result,
            "tool_versions": versions, "log": log_rel, "log_sha256": sha256_file(run_dir / log_rel), "artifacts": arts,
        })
    shutil.rmtree(tmp)
    run_meta["ended_utc"] = utc_now()
    run_meta["result"] = "PASS" if all_ok else "FAIL"
    _safe_write(run_dir / "COMMANDS.tsv", ("\n".join(tsv) + "\n").encode())
    _safe_write(run_dir / "RUN.json", (json.dumps(run_meta, indent=2, sort_keys=True) + "\n").encode())
    files = sorted(p for p in run_dir.rglob("*") if p.is_file())
    _safe_write(run_dir / "SHA256SUMS",
                "".join(f"{sha256_file(p)}  {p.relative_to(run_dir).as_posix()}\n" for p in files).encode())
    val = validate_bundle(run_dir, repo_root, validator)
    run_meta["validation"] = val
    return {"run_dir": run_dir, "meta": run_meta, "ok": all_ok and val["ok"]}


def _neutralise(text: str) -> str:
    """Prefix any captured line that looks like a trailer so command output cannot forge one."""
    if text and not text.endswith("\n"):
        text += "\n"
    return "".join(("| " + l if l.startswith("#") else l) for l in text.splitlines(keepends=True))


def validate_bundle(run_dir: Path, repo_root: Path, validator: Path | None = None) -> dict:
    """Reuse evidence/shared/validate_evidence.py (hashes + commands) on the bundle. Fail closed."""
    validator = Path(validator) if validator else Path(repo_root) / SHARED_VALIDATOR_REL
    if not validator.is_file():
        log = f"shared validator not found at {validator}; bundle NOT validated\n"
        _safe_write(run_dir / "VALIDATION.log", log.encode())
        return {"ok": False, "validator": str(validator), "steps": []}
    steps = [["hashes", str(run_dir / "SHA256SUMS"), "--base", str(run_dir), "--cover", str(run_dir)],
             ["commands", str(run_dir / "COMMANDS.tsv"), "--format", "postgres-10col"]]
    out, results = [], []
    for s in steps:
        argv = [sys.executable, str(validator), *s]
        try:
            r = subprocess.run(argv, capture_output=True, timeout=120, env=_clean_env())
            rc, text = r.returncode, (r.stdout + r.stderr).decode(errors="replace")
        except subprocess.TimeoutExpired:
            rc, text = TIMEOUT_EXIT, "validator timed out\n"
        out.append(f"$ {json.dumps(argv)}\n{text}# exit_code={rc}\n")
        results.append({"argv": argv, "exit_code": rc})
    _safe_write(run_dir / "VALIDATION.log", "".join(out).encode())
    return {"ok": all(r["exit_code"] == 0 for r in results), "validator": str(validator), "steps": results}


# ----------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checks", default=str(DEFAULT_CHECKS.relative_to(REPO_ROOT)),
                    help="repo-relative definition file under tools/acceptance/ (default: %(default)s)")
    ap.add_argument("--label", default="local-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    ap.add_argument("--only", action="append", metavar="ID", help="run only these check ids")
    ap.add_argument("--allow-uncommitted-checks", action="store_true",
                    help="run a definition that is not committed/clean at HEAD (recorded in RUN.json)")
    a = ap.parse_args(argv)
    try:
        acc_root = confine(REPO_ROOT, "tools/acceptance", must_exist=True)
        checks_path = confine(REPO_ROOT, a.checks, must_exist=True)
        if acc_root not in checks_path.parents:
            raise PathEscapeError(f"definition must live under tools/acceptance/: {a.checks!r}")
        prov = definition_provenance(checks_path, REPO_ROOT)
        if not prov["clean"] and not a.allow_uncommitted_checks:
            raise DefinitionError(f"{a.checks}: definition is not committed and unmodified at HEAD "
                                  "(commit it, or pass --allow-uncommitted-checks)")
        d = load_definition(checks_path, REPO_ROOT)
        if a.only:
            unknown = set(a.only) - {c["id"] for c in d["checks"]}
            if unknown:
                raise DefinitionError(f"unknown check ids: {sorted(unknown)}")
            d["checks"] = [c for c in d["checks"] if c["id"] in a.only]
        DEFAULT_WORKSPACE.mkdir(exist_ok=True)
        res = run_checks(d, REPO_ROOT, DEFAULT_WORKSPACE, a.label, provenance=prov)
    except (DefinitionError, PathEscapeError) as e:
        print(f"acceptance: REFUSED: {e}", file=sys.stderr)
        return 2
    for c in res["meta"]["checks"]:
        print(f"{c['result']:7} {c['id']} exit={c['exit_code']} stages={c['stage_exit_codes']} {c['duration_ms']}ms")
    v = res["meta"]["validation"]
    print(f"shared validator: {'OK' if v['ok'] else 'FAILED'} (see {res['run_dir'] / 'VALIDATION.log'})")
    print(f"acceptance: {'PASS' if res['ok'] else 'FAIL'}  bundle={os.path.relpath(res['run_dir'], REPO_ROOT)}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
