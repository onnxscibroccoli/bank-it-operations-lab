"""SIMULATION - minimal, stdlib-only validator for the subset of OpenAPI 3.0 / JSON Schema
used by contract/openapi.json. Offline. Not a general-purpose validator."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

CONTRACT_PATH = Path(__file__).resolve().parent.parent / "contract" / "openapi.json"
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


class ContractError(ValueError):
    """SIMULATION - a response did not match the contract."""


def load_contract(path: Path = CONTRACT_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _resolve(contract: dict, node: dict) -> dict:
    while "$ref" in node:
        ref = node["$ref"]
        if not ref.startswith("#/"):
            raise ContractError(f"unsupported $ref {ref}")
        cur = contract
        for part in ref[2:].split("/"):
            cur = cur[part]
        node = cur
    return node


def _type_ok(value, t: str) -> bool:
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def validate(contract: dict, schema: dict, value, path: str = "$") -> None:
    schema = _resolve(contract, schema)
    types = schema.get("type")
    if types is not None:
        tl = types if isinstance(types, list) else [types]
        if not any(_type_ok(value, t) for t in tl):
            raise ContractError(f"{path}: expected type {tl}, got {type(value).__name__}")
    if "enum" in schema and value not in schema["enum"]:
        raise ContractError(f"{path}: {value!r} not in enum {schema['enum']}")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ContractError(f"{path}: {value!r} does not match /{schema['pattern']}/")
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise ContractError(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ContractError(f"{path}: longer than {schema['maxLength']}")
        if schema.get("format") == "date-time":
            if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(Z|[+-]\d\d:\d\d)", value):
                raise ContractError(f"{path}: {value!r} is not RFC 3339 date-time")
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ContractError(f"{path}: invalid date-time {value!r}") from exc
    if _type_ok(value, "number"):
        if "minimum" in schema and value < schema["minimum"]:
            raise ContractError(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            raise ContractError(f"{path}: {value} > maximum {schema['maximum']}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in value:
                raise ContractError(f"{path}: missing required property {req!r}")
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(props))
            if extra:
                raise ContractError(f"{path}: unexpected properties {extra}")
        for key, sub in props.items():
            if key in value:
                validate(contract, sub, value[key], f"{path}.{key}")
    if isinstance(value, list):
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise ContractError(f"{path}: more than {schema['maxItems']} items")
        if "items" in schema:
            for i, item in enumerate(value):
                validate(contract, schema["items"], item, f"{path}[{i}]")


def _match_path(contract: dict, path: str) -> str:
    path = path.split("?", 1)[0]
    for template in contract["paths"]:
        rx = "^" + re.sub(r"\{[^/]+\}", r"[^/]+", template) + "$"
        if re.match(rx, path):
            return template
    raise ContractError(f"path {path!r} not in contract")


def response_schema(contract: dict, method: str, path: str, status: int) -> dict:
    op = contract["paths"][_match_path(contract, path)].get(method.lower())
    if op is None:
        raise ContractError(f"{method} {path} not in contract")
    resp = op["responses"].get(str(status))
    if resp is None:
        raise ContractError(f"{method} {path}: status {status} not declared in contract")
    return resp


def _reject_constant(name):
    raise ContractError(f"non-standard JSON constant {name}")


def validate_response(contract: dict, method: str, path: str, status: int,
                      headers: dict, body: bytes):
    """Validate a raw response against the contract; return the parsed JSON body."""
    resp = response_schema(contract, method, path, status)
    lower = {k.lower(): v for k, v in headers.items()}
    if lower.get("x-simulation") != "SIMULATION":
        raise ContractError("missing or wrong X-Simulation header")
    for hname, hspec in resp.get("headers", {}).items():
        sch = _resolve(contract, hspec)["schema"]
        raw = lower.get(hname.lower())
        if raw is None:
            raise ContractError(f"missing required header {hname}")
        val = raw
        if sch.get("type") == "integer":
            if not re.fullmatch(r"\d+", raw.strip()):
                raise ContractError(f"header {hname}: {raw!r} is not delay-seconds")
            val = int(raw)
        validate(contract, sch, val, f"header:{hname}")
    if "application/json" not in resp.get("content", {}):
        return None
    ctype = lower.get("content-type", "")
    if ctype.split(";")[0].strip().lower() != "application/json":
        raise ContractError(f"unexpected content-type {ctype!r}")
    try:
        parsed = json.loads(body.decode("utf-8"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"malformed JSON body: {exc}") from exc
    validate(contract, resp["content"]["application/json"]["schema"], parsed)
    return parsed
