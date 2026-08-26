#!/usr/bin/env python3
"""Verify documented Host CLI invocations against a Vast CLI source checkout.

The verifier imports the CLI's argparse registry and compares command names and
options. It never invokes an API command, reads an API key, creates a rental,
or mutates host/account state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "host-docs-cli-command-check.json"
OUTPUT_MARKDOWN = ROOT / "HOST-DOCS-CLI-COMMAND-CHECK.md"

INVOCATION_RE = re.compile(
    r"(?<![A-Za-z0-9_/-])(vastai|vast)\s+"
    r"([A-Za-z][A-Za-z0-9-]*)"
    r"(?:\s+([A-Za-z][A-Za-z0-9-]*))?"
)
OPTION_RE = re.compile(r"(?<![A-Za-z0-9_])(--?[A-Za-z][A-Za-z0-9_-]*)")
GLOBAL_OPTIONS = {
    "-h",
    "--help",
    "--url",
    "--retry",
    "--explain",
    "--raw",
    "--full",
    "--curl",
    "--api-key",
    "--version",
    "--no-color",
}

REGISTRY_SCRIPT = r"""
import json
from vastai.cli.main import parser
from vastai.cli.commands import (
    instances, offers, machines, teams, keys, endpoints,
    billing, storage, auth, misc, deployments, metrics,
    benchmarks, price_increase, update, uninstall,
)

registry = {}
for name, command_parser in parser.subparsers().choices.items():
    options = set()
    positionals = []
    for action in command_parser._actions:
        if action.option_strings:
            options.update(action.option_strings)
        elif action.dest != "help":
            positionals.append(action.dest)
    registry[name] = {
        "options": sorted(options),
        "positionals": positionals,
        "hidden": bool(getattr(command_parser, "hidden", False)),
    }
print(json.dumps(registry, sort_keys=True))
"""


def git_value(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def load_registry(vast_cli: Path) -> dict[str, dict[str, Any]]:
    result = subprocess.run(
        [sys.executable, "-c", REGISTRY_SCRIPT],
        cwd=vast_cli,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Could not import the Vast CLI command registry:\n" + (result.stderr or result.stdout)
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Vast CLI registry returned invalid JSON: {error}") from error


def source_paths() -> list[Path]:
    return sorted((ROOT / "host").rglob("*.mdx")) + sorted(
        (ROOT / "snippets" / "host").rglob("*.mdx")
    )


def clean_segment(value: str) -> str:
    value = value.replace("`", "").replace("**", "")
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    return re.sub(r"\s+", " ", value).strip(" |])}.,")


def finding_id(file: str, line: int, executable: str, signature: str) -> str:
    raw = f"{file}\0{line}\0{executable}\0{signature}"
    return "cli-" + hashlib.sha256(raw.encode()).hexdigest()[:10]


def extract_invocations(registry: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    command_names = set(registry)

    for path in source_paths():
        relative = path.relative_to(ROOT).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            matches = list(INVOCATION_RE.finditer(line))
            for index, match in enumerate(matches):
                prefix = line[: match.start()].rstrip().casefold()
                if prefix.endswith("from"):
                    continue

                executable, first, second = match.groups()
                if first.isupper():
                    continue
                candidate_two = f"{first} {second}" if second else ""
                if candidate_two in command_names:
                    signature = candidate_two
                elif first in command_names:
                    signature = first
                else:
                    signature = candidate_two or first

                segment_end = matches[index + 1].start() if index + 1 < len(matches) else len(line)
                raw_segment = line[match.start() : segment_end]
                segment = clean_segment(raw_segment)
                flag_source = re.sub(r"'[^']*'|\"[^\"]*\"", "", raw_segment)
                flags = sorted(set(OPTION_RE.findall(flag_source)))
                accepted = set(registry.get(signature, {}).get("options", [])) | GLOBAL_OPTIONS
                unknown_flags = sorted(flag for flag in flags if flag not in accepted)

                if executable != "vastai":
                    status = "wrong-executable"
                    detail = "Use `vastai`; the current packaged console script does not register `vast`."
                elif signature not in command_names:
                    if any(name.startswith(first + " ") for name in command_names):
                        status = "command-family-reference"
                        detail = "This names a registered command family, not a runnable leaf command."
                    elif "..." in raw_segment or first in {"command", "commands"}:
                        status = "incomplete-placeholder"
                        detail = "This is a placeholder reference, not a runnable command line."
                    else:
                        status = "unknown-command"
                        detail = f"`{signature}` is not registered by the selected Vast CLI source."
                elif unknown_flags:
                    status = "unknown-option"
                    detail = "Not registered for this command or globally: " + ", ".join(unknown_flags)
                else:
                    status = "pass"
                    detail = "Executable, command signature, and documented options exist in the selected CLI registry."

                records.append(
                    {
                        "id": finding_id(relative, line_number, executable, signature),
                        "file": relative,
                        "line": line_number,
                        "invocation": segment,
                        "executable": executable,
                        "signature": signature,
                        "flags": flags,
                        "unknown_flags": unknown_flags,
                        "status": status,
                        "detail": detail,
                    }
                )
    return records


def build_result(vast_cli: Path) -> dict[str, Any]:
    registry = load_registry(vast_cli)
    records = extract_invocations(registry)
    status_counts = Counter(record["status"] for record in records)
    unique_signatures = sorted(
        {record["signature"] for record in records if record["signature"] in registry}
    )
    source_revision = git_value(vast_cli, "rev-parse", "HEAD")
    source_branch = git_value(vast_cli, "branch", "--show-current") or "detached"
    source_status = git_value(vast_cli, "status", "--porcelain")
    return {
        "schema_version": 1,
        "vast_cli_source": {
            "revision": source_revision,
            "branch": source_branch,
            "dirty": source_status not in {"", "unknown"},
        },
        "safety": {
            "api_commands_executed": False,
            "credentials_read_or_supplied": False,
            "method": "Imported argparse registrations and compared names/options only.",
        },
        "summary": {
            "source_files_scanned": len(source_paths()),
            "registered_cli_commands": len(registry),
            "documented_invocation_occurrences": len(records),
            "documented_registered_signatures": len(unique_signatures),
            "status_counts": dict(sorted(status_counts.items())),
            "actionable_findings": sum(
                count
                for status, count in status_counts.items()
                if status in {"wrong-executable", "unknown-command", "unknown-option"}
            ),
        },
        "documented_registered_signatures": unique_signatures,
        "records": records,
    }


def markdown_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", "&#123;")
        .replace("}", "&#125;")
        .replace("|", "\\|")
        .replace("\n", "<br />")
    )


def render_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    source = result["vast_cli_source"]
    actionable = [
        record
        for record in result["records"]
        if record["status"] in {"wrong-executable", "unknown-command", "unknown-option"}
    ]
    lines = [
        "# Host Docs CLI registry verification",
        "",
        "> Generated by `scripts/verify_host_cli_commands.py`. No API command was executed.",
        "",
        f"- Vast CLI source: `{source['branch']}@{source['revision']}` (dirty: `{str(source['dirty']).lower()}`)",
        f"- Host page/snippet files scanned: **{summary['source_files_scanned']}**",
        f"- Documented CLI occurrences: **{summary['documented_invocation_occurrences']}**",
        f"- Current registered signatures used by Host Docs: **{summary['documented_registered_signatures']}**",
        f"- Actionable command defects: **{summary['actionable_findings']}**",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python3 -B scripts/verify_host_cli_commands.py --vast-cli /path/to/vast-cli",
        "python3 -B scripts/verify_host_cli_commands.py --vast-cli /path/to/vast-cli --check",
        "```",
        "",
        "The selected checkout should be a clean, explicitly recorded Vast CLI revision. The verifier imports argparse metadata only; it does not authenticate, call the Vast API, or execute a documented operation.",
        "",
        "## Actionable findings",
        "",
    ]
    if actionable:
        lines.extend(["| ID | Location | Invocation | Result |", "|---|---|---|---|"])
        for record in actionable:
            location = f"[{record['file']}:{record['line']}](./{record['file']}#L{record['line']})"
            lines.append(
                f"| {record['id']} | {location} | `{markdown_escape(record['invocation'])}` | "
                f"**{record['status']}** — {markdown_escape(record['detail'])} |"
            )
    else:
        lines.append("No wrong executable, unknown command, or unknown option was found.")

    lines.extend(
        [
            "",
            "## Result counts",
            "",
            "| Status | Occurrences |",
            "|---|---:|",
        ]
    )
    for status, count in summary["status_counts"].items():
        lines.append(f"| {status} | {count} |")

    lines.extend(
        [
            "",
            "## All documented invocation occurrences",
            "",
            "| Location | Signature | Options | Status |",
            "|---|---|---|---|",
        ]
    )
    for record in result["records"]:
        location = f"[{record['file']}:{record['line']}](./{record['file']}#L{record['line']})"
        options = ", ".join(f"`{flag}`" for flag in record["flags"]) or "—"
        lines.append(
            f"| {location} | `{record['executable']} {markdown_escape(record['signature'])}` | "
            f"{options} | {record['status']} |"
        )
    lines.append("")
    return "\n".join(lines)


def outputs(result: dict[str, Any]) -> dict[Path, str]:
    return {
        OUTPUT_JSON: json.dumps(result, indent=2) + "\n",
        OUTPUT_MARKDOWN: render_markdown(result),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vast-cli", type=Path, required=True, help="Vast CLI source checkout")
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs are stale")
    args = parser.parse_args()

    vast_cli = args.vast_cli.expanduser().resolve()
    if not (vast_cli / "vastai" / "cli" / "main.py").exists():
        parser.error(f"not a modular Vast CLI checkout: {vast_cli}")

    try:
        result = build_result(vast_cli)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 2

    rendered = outputs(result)
    if args.check:
        stale = [path for path, content in rendered.items() if not path.exists() or path.read_text() != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(ROOT)}", file=sys.stderr)
            return 2
    else:
        for path, content in rendered.items():
            path.write_text(content)
            print(f"wrote {path.relative_to(ROOT)}")

    actionable = result["summary"]["actionable_findings"]
    if actionable:
        print(f"found {actionable} actionable documented CLI defect(s)", file=sys.stderr)
        return 1
    print(
        f"Host Docs CLI registry check passed for "
        f"{result['summary']['documented_invocation_occurrences']} occurrences."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
