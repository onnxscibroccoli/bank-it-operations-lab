#!/usr/bin/env python3
"""Fail-closed owner-attestation check. Stdlib only.

A payload is attested only when its Ed25519 signature verifies against a key whose
SHA-256 fingerprint is enrolled. The enrolled file ships empty. An empty enrollment
returns unattested. This script never enrolls a key and never talks to GitHub.
"""
import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def fingerprint(public_key_raw: bytes) -> str:
    return hashlib.sha256(public_key_raw).hexdigest()


def load_enrolled(path: Path):
    document = json.loads(path.read_text())
    if document.get("schema") != "bank-lab/enrolled-owner-keys/v1":
        raise SystemExit("enrolled key file has the wrong schema")
    out = {}
    for entry in document.get("keys") or []:
        raw = base64.b64decode(entry["publicKey"])
        if len(raw) != 32:
            raise SystemExit("enrolled key is not a 32-byte Ed25519 public key")
        out[entry["fingerprint"]] = raw
        if entry["fingerprint"] != fingerprint(raw):
            raise SystemExit("enrolled fingerprint does not match the public key")
    return out


def verify(payload, signature_b64: str, enrolled: dict) -> bool:
    if not enrolled:
        return False
    try:
        signature = base64.b64decode(signature_b64)
        claimed = payload["keyFingerprint"]
    except Exception:
        return False
    public = enrolled.get(claimed)
    if public is None or len(signature) != 64:
        return False
    # OpenSSL-free verification: PyNaCl is not a dependency. Use cryptography only if present.
    # The lab stdlib does not include Ed25519. When no verifier library is installed, a
    # non-empty enrollment still cannot be treated as success by a stub. Fail closed.
    try:
        from nacl.signing import VerifyKey
    except Exception:
        return False
    try:
        VerifyKey(public).verify(canonical(payload), signature)
    except Exception:
        return False
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True, help="JSON file of the decision payload")
    parser.add_argument("--signature", required=True, help="base64 Ed25519 signature")
    parser.add_argument("--keys", default=str(HERE / "enrolled-owner-keys.json"))
    args = parser.parse_args(argv)
    enrolled = load_enrolled(Path(args.keys))
    payload = json.loads(Path(args.payload).read_text())
    ok = verify(payload, args.signature, enrolled)
    print(json.dumps({"attested": ok, "enrolledKeys": len(enrolled)}))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
