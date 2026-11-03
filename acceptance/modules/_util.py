"""Shared helpers for the acceptance adapters (stdlib only)."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]

# Same scrub list as scripts/validate-all.sh: adapters never see cloud credentials.
_SCRUB = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_PROFILE", "AWS_ROLE_ARN",
          "AWS_WEB_IDENTITY_TOKEN_FILE", "AWS_CONTAINER_CREDENTIALS_FULL_URI",
          "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI", "CDK_DEFAULT_ACCOUNT", "CDK_DEFAULT_REGION",
          "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID")


def offline_env(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in _SCRUB}
    env.update({"AWS_EC2_METADATA_DISABLED": "true", "AWS_CONFIG_FILE": "/dev/null",
                "AWS_SHARED_CREDENTIALS_FILE": "/dev/null", "CDK_DISABLE_CLI_TELEMETRY": "true"})
    env.update(extra or {})
    return env


def run(argv: Sequence[str], cwd: Optional[Path] = None, timeout: int = 900,
        env: Optional[Dict[str, str]] = None) -> Tuple[int, str]:
    """Run a command offline; return (exit_code, combined stdout+stderr)."""
    p = subprocess.run(list(argv), cwd=str(cwd or ROOT), env=env or offline_env(), timeout=timeout,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout


def py(*args: str, cwd: Optional[Path] = None, timeout: int = 300) -> Tuple[int, str]:
    return run([sys.executable, *args], cwd=cwd, timeout=timeout)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def evidence_entries(paths: List[Path]) -> List[Dict[str, str]]:
    return [{"path": rel(p), "sha256": sha256(p)} for p in paths if Path(p).is_file()]


def git_sha() -> Optional[str]:
    try:
        rc, out = run(["git", "rev-parse", "HEAD"], timeout=10)
        return out.strip() if rc == 0 else None
    except Exception:
        return None
