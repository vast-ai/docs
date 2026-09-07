#!/usr/bin/env python3
"""Compare volume-related OpenAPI request fields with an exact Vast CLI checkout."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def function_node(path: Path, name: str) -> ast.FunctionDef:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ValueError(f"{name} not found in {path}")


def payload_contract(path: Path, name: str) -> tuple[str, str, set[str]]:
    node = function_node(path, name)
    keys: set[str] = set()
    method = ""
    endpoint = ""
    for child in ast.walk(node):
        if isinstance(child, ast.Dict):
            for key in child.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    keys.add(key.value)
        if (
            isinstance(child, ast.Assign)
            and len(child.targets) == 1
            and isinstance(child.targets[0], ast.Subscript)
            and isinstance(child.targets[0].slice, ast.Constant)
            and isinstance(child.targets[0].slice.value, str)
        ):
            keys.add(child.targets[0].slice.value)
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr in {"get", "post", "put", "delete"}
            and child.args
            and isinstance(child.args[0], ast.Constant)
            and isinstance(child.args[0].value, str)
        ):
            method = child.func.attr
            endpoint = child.args[0].value
    if not method or not endpoint or not keys:
        raise ValueError(f"could not derive payload contract for {name}")
    return method, endpoint, keys


def openapi_operation(path: Path, endpoint: str, method: str) -> dict[str, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    operation = document.get("paths", {}).get(endpoint, {}).get(method)
    if not isinstance(operation, dict):
        raise ValueError(f"missing {method.upper()} {endpoint} in {path}")
    return operation


def request_properties(operation: dict[str, Any]) -> set[str]:
    schema = operation["requestBody"]["content"]["application/json"]["schema"]
    return set(schema.get("properties", {}))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vast-cli", required=True, type=Path)
    args = parser.parse_args()
    vast_cli = args.vast_cli.resolve()

    checks = [
        (
            vast_cli / "vastai/api/machines.py",
            "list_machine",
            ROOT / "api-reference/openapi/yaml/list_machine.yaml",
        ),
        (
            vast_cli / "vastai/api/storage.py",
            "list_volume",
            ROOT / "api-reference/openapi/yaml/list_volume.yaml",
        ),
        (
            vast_cli / "vastai/api/storage.py",
            "list_volumes",
            ROOT / "api-reference/openapi/yaml/list_volume.yaml",
        ),
        (
            vast_cli / "vastai/api/storage.py",
            "create_volume",
            ROOT / "api-reference/openapi/yaml/rent_volume.yaml",
        ),
    ]

    failures: list[str] = []
    for source, function, specification in checks:
        method, relative_endpoint, expected = payload_contract(source, function)
        endpoint = f"/api/v0{relative_endpoint}"
        operation = openapi_operation(specification, endpoint, method)
        actual = request_properties(operation)
        missing = sorted(expected - actual)
        if missing:
            failures.append(
                f"{specification.relative_to(ROOT)} is missing {function} field(s): "
                + ", ".join(missing)
            )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: volume OpenAPI methods and request fields cover the pinned Vast CLI client payloads")
    print("LIMIT: this static comparison does not prove backend enforcement, runtime behavior, billing, or policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
