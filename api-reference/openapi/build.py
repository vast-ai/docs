#!/usr/bin/env python3
"""Combine per-endpoint OpenAPI YAML files into a single openapi.yaml.

Sources: api-reference/openapi/yaml/*.yaml (one file per endpoint)
Output:  api-reference/openapi.yaml (consumed by Mintlify via docs.json)

Run with: python3 api-reference/openapi/build.py
Or via:   npm run build-openapi
"""
import sys
import copy
import re
import yaml
from pathlib import Path

# start, stop, and label instance all PUT to the same API path; instance_management.yaml
# combines them. Skip the originals so we don't double-merge.
YAML_IGNORE_LIST = [
    'launch_instance.yaml',
    'start_instance.yaml',
    'start_instances.yaml',
    'stop_instance.yaml',
    'label_instance.yaml',
]

SCRIPT_DIR = Path(__file__).resolve().parent              # api-reference/openapi/
SOURCE_DIR = SCRIPT_DIR / "yaml"                          # api-reference/openapi/yaml/
OUTPUT_FILE = SCRIPT_DIR.parent / "openapi.yaml"          # api-reference/openapi.yaml
PATH_PARAM_RE = re.compile(r"^\{([^{}]+)\}$")


def clean_description(text):
    if not text:
        return text
    lines = [line.rstrip() for line in text.split('\n')]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines)


def canonicalize_path(path):
    """Normalize paths to avoid duplicate trailing-slash API docs routes."""
    if path != "/" and path.endswith("/"):
        return path.rstrip("/")
    return path


def path_shape(path):
    """Return a path shape where parameter names are ignored."""
    parts = path.split("/")
    return "/".join("{}" if PATH_PARAM_RE.match(part) else part for part in parts)


def path_params(path):
    params = []
    for part in path.split("/"):
        match = PATH_PARAM_RE.match(part)
        if match:
            params.append(match.group(1))
    return params


def rewrite_path_params(node, mapping):
    if isinstance(node, dict):
        if node.get("in") == "path" and node.get("name") in mapping:
            node["name"] = mapping[node["name"]]
        for value in node.values():
            rewrite_path_params(value, mapping)
    elif isinstance(node, list):
        for item in node:
            rewrite_path_params(item, mapping)


def make_operation_id(method, path, operation):
    words = re.findall(r"[A-Za-z0-9]+", operation.get("summary") or "")
    if not words:
        words = [method] + re.findall(r"[A-Za-z0-9]+", path)
    return words[0].lower() + "".join(word[:1].upper() + word[1:] for word in words[1:])


def normalize_schema(node):
    if isinstance(node, dict):
        if node.get("nullable") is True:
            schema_type = node.get("type")
            if isinstance(schema_type, str):
                node["type"] = [schema_type, "null"]
            elif isinstance(schema_type, list) and "null" not in schema_type:
                node["type"] = schema_type + ["null"]
            node.pop("nullable", None)
        else:
            node.pop("nullable", None)

        # Some endpoint files use "msg" where OpenAPI expects an example.
        if "msg" in node and "type" in node:
            node.setdefault("example", node.pop("msg"))

        if isinstance(node.get("required"), list) and isinstance(node.get("properties"), dict):
            node["required"] = [key for key in node["required"] if key in node["properties"]]
            if not node["required"]:
                node.pop("required", None)

        for value in list(node.values()):
            normalize_schema(value)
    elif isinstance(node, list):
        for item in node:
            normalize_schema(item)


def normalize_paths(paths):
    normalized_paths = {}
    shape_to_path = {}
    operation_ids = set()

    for path, path_item in paths.items():
        stripped_path = canonicalize_path(path)
        current_shape = path_shape(stripped_path)
        canonical_path = shape_to_path.setdefault(current_shape, stripped_path)
        current_params = path_params(stripped_path)
        canonical_params = path_params(canonical_path)
        param_mapping = {
            current: canonical_params[index]
            for index, current in enumerate(current_params)
            if index < len(canonical_params) and current != canonical_params[index]
        }
        normalized_item = copy.deepcopy(path_item)
        if param_mapping:
            rewrite_path_params(normalized_item, param_mapping)

        destination = normalized_paths.setdefault(canonical_path, {})
        for method, operation in normalized_item.items():
            if isinstance(operation, dict):
                operation.setdefault("operationId", make_operation_id(method, canonical_path, operation))
                base_operation_id = operation["operationId"]
                suffix = 2
                while operation["operationId"] in operation_ids:
                    operation["operationId"] = f"{base_operation_id}{suffix}"
                    suffix += 1
                operation_ids.add(operation["operationId"])
            destination[method] = operation

    return normalized_paths


def build_master_doc():
    return {
        'openapi': '3.1.0',
        'info': {
            'title': 'Vast.ai API',
            'description': (
                "Vast.ai REST API for managing GPU cloud instances, machine operations, and AI/ML workflows.\n\n"
                "## AI Agent Quick-Start\n\n"
                "Install the CLI skill for your agent (Claude Code, Cursor, Windsurf, etc.):\n"
                "  npx skills add vast-ai/vast-cli\n\n"
                "CLI reference: https://raw.githubusercontent.com/vast-ai/vast-cli/master/vastai/SKILL.md\n"
                "SDK reference: https://raw.githubusercontent.com/vast-ai/vast-cli/master/vastai_sdk/SKILL.md\n\n"
                "## Auth\n"
                "All endpoints require `Authorization: Bearer $VAST_API_KEY`.\n"
                "Get your key at: https://cloud.vast.ai/manage-keys/\n\n"
                "## Key Quirks\n"
                "- `gpu_ram` in CLI = GB; in REST API = MB (CLI auto-converts)\n"
                "- SSH keys must be registered BEFORE creating an instance (VM: no recovery; Docker: can add post-create)\n"
                "- `onstart` field is limited to 4048 characters -- gzip+base64 for longer scripts\n"
                "- `POST /api/v0/asks/{id}/` (create instance) returns `new_contract` as the instance ID, not `id`\n"
                "- Poll trap: if `actual_status` becomes `exited`, `unknown`, or `offline` it will never reach `running` -- destroy and retry"
            ),
            'version': '1.0.0',
            'contact': {
                'name': 'Vast.ai Support',
                'url': 'https://discord.gg/vast'
            },
            'license': {
                'name': 'Vast.ai Terms of Service',
                'url': 'https://vast.ai/terms/'
            }
        },
        'servers': [
            {'url': 'https://console.vast.ai', 'description': 'Production server'}
        ],
        'security': [{'BearerAuth': []}],
        'paths': {},
        'components': {
            'schemas': {},
            'securitySchemes': {
                'BearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'description': 'API key must be provided in the Authorization header'
                }
            }
        }
    }


def combine_yaml_files(source_dir, output_file):
    if not source_dir.exists():
        print(f"Error: source directory does not exist: {source_dir}", file=sys.stderr)
        return False

    yaml_files = sorted(source_dir.glob("*.yaml"))
    if not yaml_files:
        print(f"Error: no YAML files found in {source_dir}", file=sys.stderr)
        return False

    master_doc = build_master_doc()
    errors = []

    for yaml_file in yaml_files:
        if yaml_file.name in YAML_IGNORE_LIST:
            print(f"Skipping ignored file: {yaml_file.name}")
            continue

        print(f"Processing {yaml_file.name}...")
        try:
            with open(yaml_file, 'r') as f:
                spec = yaml.safe_load(f)
        except Exception as e:
            errors.append(f"{yaml_file.name}: {e}")
            continue

        if 'paths' in spec:
            for path, path_item in spec['paths'].items():
                for method in path_item.values():
                    if 'description' in method:
                        method['description'] = clean_description(method['description'])
                    if 'security' in method:
                        method['security'] = [{'BearerAuth': []}]
                    if 'parameters' in method:
                        method['parameters'] = [
                            p for p in method['parameters']
                            if not (p.get('name') == 'api_key' and p.get('in') == 'query')
                        ]
                if path in master_doc['paths']:
                    master_doc['paths'][path].update(path_item)
                else:
                    master_doc['paths'][path] = path_item

        if 'components' in spec and 'schemas' in spec['components']:
            master_doc['components']['schemas'].update(spec['components']['schemas'])

    if errors:
        print("\nErrors during processing:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    master_doc['paths'] = normalize_paths(master_doc['paths'])
    normalize_schema(master_doc)

    with open(output_file, 'w') as f:
        yaml.dump(master_doc, f, default_flow_style=False, sort_keys=False, width=80)
    print(f"\nWrote combined API spec to {output_file}")
    return True


if __name__ == "__main__":
    ok = combine_yaml_files(SOURCE_DIR, OUTPUT_FILE)
    sys.exit(0 if ok else 1)
