#!/usr/bin/env python3
"""Combine per-endpoint OpenAPI YAML files into a single openapi.yaml.

Sources: api-reference/openapi/yaml/*.yaml (one file per endpoint)
Output:  api-reference/openapi.yaml (consumed by Mintlify via docs.json)

Run with: python3 api-reference/openapi/build.py
Or via:   npm run build-openapi
"""
import sys
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


def clean_description(text):
    if not text:
        return text
    lines = [line.rstrip() for line in text.split('\n')]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines)


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

    with open(output_file, 'w') as f:
        yaml.dump(master_doc, f, default_flow_style=False, sort_keys=False, width=80)
    print(f"\nWrote combined API spec to {output_file}")
    return True


if __name__ == "__main__":
    ok = combine_yaml_files(SOURCE_DIR, OUTPUT_FILE)
    sys.exit(0 if ok else 1)
