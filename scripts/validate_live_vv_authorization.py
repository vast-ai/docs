#!/usr/bin/env python3
"""Validate a restricted outside-Git Host Docs live V&V authorization record.

The command emits only a bounded non-secret projection. It never prints the completed
record, approver name, target details, credential state, or cleanup contact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import FormatChecker
from jsonschema.validators import validator_for


REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "verification/live-vv-authorization.schema.json"
CLASS_TO_DECISION = {
    "host-read-only": "host_read_only",
    "host-privileged-read-only": "host_privileged_read_only",
    "wan": "wan",
    "host-mutating": "host_mutating",
    "host-self-test": "host_self_test",
    "paid": "paid",
}
SECRET_VALUE_RE = re.compile(
    r"(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|\bBearer\s+[A-Za-z0-9._~-]+|"
    r"\b(?:api[_-]?key|token|password|secret)\s*[=:]\s*\S+|\b[0-9a-fA-F]{64}\b)",
    re.IGNORECASE,
)


class AuthorizationError(RuntimeError):
    """The restricted authorization record is unsafe, invalid, or inapplicable."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuthorizationError(message)


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def parse_time(value: str, field: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise AuthorizationError(f"{field} is not a valid ISO-8601 date-time") from exc
    require(parsed.tzinfo is not None, f"{field} must include a timezone offset")
    return parsed.astimezone(timezone.utc)


def walk_strings(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def load_and_validate(path: Path) -> tuple[dict[str, Any], bytes]:
    require(path.is_absolute(), "authorization path must be absolute")
    require(not path.is_symlink(), "authorization record must not be a symbolic link")
    resolved = path.resolve(strict=True)
    require(not is_within(resolved, REPO.resolve()), "authorization record must be stored outside Git/repository")
    mode = stat.S_IMODE(resolved.stat().st_mode)
    require(mode & 0o077 == 0, f"authorization record permissions must deny group/other access; got {mode:04o}")
    raw = resolved.read_bytes()
    require(len(raw) <= 128 * 1024, "authorization record is unexpectedly large")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorizationError(f"authorization record is not valid UTF-8 JSON: {exc}") from exc
    require(isinstance(value, dict), "authorization record top level must be an object")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    errors = sorted(validator_class(schema, format_checker=FormatChecker()).iter_errors(value), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        location = "$" + "".join(f"[{part!r}]" for part in first.path)
        raise AuthorizationError(f"schema validation failed at {location}: {first.message}")
    for location, text in walk_strings(value):
        require(not SECRET_VALUE_RE.search(text), f"credential-shaped value is forbidden at {location}")
    require(value["approver"]["full_name"].strip(), "approver full name is empty")
    require(value["approver"]["exact_role"].strip(), "approver exact role is empty")
    return value, raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="absolute path to the restricted outside-Git record")
    parser.add_argument("--class", dest="operation_class", choices=sorted(CLASS_TO_DECISION), required=True)
    parser.add_argument("--require-active-window", action="store_true")
    args = parser.parse_args()
    value, raw = load_and_validate(args.record)
    decision_key = CLASS_TO_DECISION[args.operation_class]
    require(value["decision"][decision_key] == "APPROVED", f"{args.operation_class} is not approved")
    start = parse_time(value["window"]["start"], "window.start")
    end = parse_time(value["window"]["end"], "window.end")
    require(start < end, "authorization window end must be after start")
    if args.require_active_window:
        now = datetime.now(timezone.utc)
        require(start <= now <= end, "authorization is outside its approved time window")
    projection = {
        "authorization_id": value["authorization_id"],
        "operation_class": args.operation_class,
        "decision": "APPROVED",
        "record_sha256": hashlib.sha256(raw).hexdigest(),
        "schema_sha256": hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(),
        "window_start": value["window"]["start"],
        "window_end": value["window"]["end"],
        "window_timezone": value["window"]["timezone"],
        "target_alias": value["target"]["target_alias"],
    }
    if args.operation_class == "paid":
        projection["max_spend_usd"] = value["paid"]["max_spend_usd"]
        projection["max_runtime_minutes"] = value["paid"]["max_runtime_minutes"]
    if args.operation_class == "host-self-test":
        projection["max_runtime_minutes"] = value["host_self_test"]["max_runtime_minutes"]
    if args.operation_class == "wan":
        projection["approved_protocols"] = value["wan"]["approved_protocols"]
    print(json.dumps(projection, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuthorizationError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
