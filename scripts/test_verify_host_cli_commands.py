#!/usr/bin/env python3
"""Focused regressions for Host Docs CLI signature extraction."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().with_name("verify_host_cli_commands.py")


def load_verifier() -> Any:
    spec = importlib.util.spec_from_file_location("host_docs_cli_verifier", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import CLI verifier from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERIFIER = load_verifier()


class CliExtractionTests(unittest.TestCase):
    def test_multiline_flags_are_checked_as_one_invocation(self) -> None:
        handler_source = {
            "path": "vastai/cli/commands/storage.py",
            "symbol": "list__volume",
            "line_start": 40,
            "line_end": 43,
        }
        registry = {
            "list volume": {
                "options": ["--size", "--price_disk", "--end_date"],
                "positionals": ["id"],
                "handler_source": handler_source,
            }
        }
        text = """```bash
vastai list volume <machine-id> \\
  --size <capacity-gb> \\
  --price_disk <usd-per-gb-month> \\
  --end_date <date>
```
"""

        records = VERIFIER.extract_invocations_from_text("host/example.mdx", text, registry)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["line"], 2)
        self.assertEqual(records[0]["signature"], "list volume")
        self.assertEqual(
            records[0]["flags"],
            ["--end_date", "--price_disk", "--size"],
        )
        self.assertEqual(records[0]["status"], "pass")
        self.assertEqual(records[0]["handler_source"], handler_source)

    def test_unknown_multiline_flag_fails_closed(self) -> None:
        registry = {"list volume": {"options": ["--size"], "positionals": ["id"]}}
        text = "vastai list volume 123 \\\n  --unsupported value\n"

        records = VERIFIER.extract_invocations_from_text("host/example.mdx", text, registry)

        self.assertEqual(records[0]["status"], "unknown-option")
        self.assertEqual(records[0]["unknown_flags"], ["--unsupported"])

    def test_nested_command_substitution_keeps_flags_with_their_own_command(self) -> None:
        registry = {
            "list machines": {"options": ["-e", "--retry"], "positionals": ["ids"]},
            "show machines": {"options": ["-q"], "positionals": []},
        }
        text = (
            "vastai list machines $(vastai show machines -q) "
            "-e 12/31/2024 `--retry` 6\n"
        )

        records = VERIFIER.extract_invocations_from_text("host/example.mdx", text, registry)
        by_signature = {record["signature"]: record for record in records}

        self.assertEqual(by_signature["show machines"]["flags"], ["-q"])
        self.assertEqual(by_signature["show machines"]["status"], "pass")
        self.assertEqual(by_signature["list machines"]["flags"], ["--retry", "-e"])
        self.assertEqual(by_signature["list machines"]["status"], "pass")

    def test_nested_substitution_ignores_quoted_closing_parenthesis(self) -> None:
        registry = {
            "list machines": {"options": ["-e", "--retry"], "positionals": ["ids"]},
            "show machines": {"options": ["-q"], "positionals": []},
        }
        text = (
            '"$(vastai list machines $(vastai show machines -q "literal )") '
            '-e 12/31/2024 --retry 6)"\n'
        )

        records = VERIFIER.extract_invocations_from_text("host/example.mdx", text, registry)
        by_signature = {record["signature"]: record for record in records}

        self.assertEqual(by_signature["show machines"]["flags"], ["-q"])
        self.assertEqual(by_signature["show machines"]["status"], "pass")
        self.assertEqual(by_signature["list machines"]["flags"], ["--retry", "-e"])
        self.assertEqual(by_signature["list machines"]["status"], "pass")

    def test_unknown_nested_outer_and_inner_flags_fail_closed(self) -> None:
        registry = {
            "list machines": {"options": ["-e"], "positionals": ["ids"]},
            "show machines": {"options": ["-q"], "positionals": []},
        }
        text = (
            "vastai list machines $(vastai show machines --unknown-inner) "
            "-e 12/31/2024 --unknown-outer\n"
        )

        records = VERIFIER.extract_invocations_from_text("host/example.mdx", text, registry)
        by_signature = {record["signature"]: record for record in records}

        self.assertEqual(by_signature["show machines"]["unknown_flags"], ["--unknown-inner"])
        self.assertEqual(by_signature["show machines"]["status"], "unknown-option")
        self.assertEqual(by_signature["list machines"]["unknown_flags"], ["--unknown-outer"])
        self.assertEqual(by_signature["list machines"]["status"], "unknown-option")


class CliRegistryTests(unittest.TestCase):
    def test_load_registry_records_handler_path_symbol_and_definition_lines(self) -> None:
        command_modules = (
            "instances",
            "offers",
            "machines",
            "teams",
            "keys",
            "endpoints",
            "billing",
            "storage",
            "auth",
            "misc",
            "deployments",
            "metrics",
            "benchmarks",
            "price_increase",
            "update",
            "uninstall",
        )
        handler_source = """def passthrough(function):
    return function

@passthrough
def create__volume(args):
    return args
"""
        main_source = """from argparse import ArgumentParser
from vastai.cli.commands.storage import create__volume

parser = ArgumentParser()
subcommands = parser.add_subparsers()
parser.subparsers = lambda: subcommands
command_parser = subcommands.add_parser("create volume")
command_parser.add_argument("id")
command_parser.add_argument("--size")
command_parser.set_defaults(func=create__volume)
"""

        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory)
            cli_package = checkout / "vastai" / "cli"
            commands_package = cli_package / "commands"
            commands_package.mkdir(parents=True)
            (checkout / "vastai" / "__init__.py").write_text("", encoding="utf-8")
            (cli_package / "__init__.py").write_text("", encoding="utf-8")
            (commands_package / "__init__.py").write_text("", encoding="utf-8")
            for module_name in command_modules:
                source = handler_source if module_name == "storage" else ""
                (commands_package / f"{module_name}.py").write_text(source, encoding="utf-8")
            (cli_package / "main.py").write_text(main_source, encoding="utf-8")

            registry = VERIFIER.load_registry(checkout)

        self.assertEqual(
            registry["create volume"],
            {
                "hidden": False,
                "options": ["--help", "--size", "-h"],
                "positionals": ["id"],
                "handler_source": {
                    "path": "vastai/cli/commands/storage.py",
                    "symbol": "create__volume",
                    "line_start": 4,
                    "line_end": 5,
                },
            },
        )

    def test_load_registry_fails_closed_when_cli_import_fails(self) -> None:
        failed = subprocess.CompletedProcess(
            args=["python", "-c", "registry"],
            returncode=1,
            stdout="",
            stderr="import failed",
        )

        with mock.patch.object(VERIFIER.subprocess, "run", return_value=failed):
            with self.assertRaisesRegex(RuntimeError, "import failed"):
                VERIFIER.load_registry(Path("/tmp/vast-cli"))

    def test_load_registry_fails_closed_on_invalid_json(self) -> None:
        malformed = subprocess.CompletedProcess(
            args=["python", "-c", "registry"],
            returncode=0,
            stdout="{not-json",
            stderr="",
        )

        with mock.patch.object(VERIFIER.subprocess, "run", return_value=malformed):
            with self.assertRaisesRegex(RuntimeError, "registry returned invalid JSON"):
                VERIFIER.load_registry(Path("/tmp/vast-cli"))

    def test_build_result_uses_schema_version_two_and_retains_handler_source(self) -> None:
        handler_source = {
            "path": "vastai/cli/commands/storage.py",
            "symbol": "list__volume",
            "line_start": 40,
            "line_end": 43,
        }
        registry = {
            "list volume": {
                "options": ["--size"],
                "positionals": ["id"],
                "hidden": False,
                "handler_source": handler_source,
            }
        }
        records = [
            {
                "signature": "list volume",
                "status": "pass",
                "handler_source": handler_source,
            }
        ]

        def fake_git_value(_repo: Path, *args: str) -> str:
            values = {
                ("rev-parse", "HEAD"): "abc123",
                ("branch", "--show-current"): "main",
                ("status", "--porcelain"): "",
            }
            return values[args]

        with (
            mock.patch.object(VERIFIER, "load_registry", return_value=registry),
            mock.patch.object(VERIFIER, "extract_invocations", return_value=records),
            mock.patch.object(VERIFIER, "source_paths", return_value=[Path("host/example.mdx")]),
            mock.patch.object(VERIFIER, "git_value", side_effect=fake_git_value),
        ):
            result = VERIFIER.build_result(Path("/tmp/vast-cli"))

        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(result["records"][0]["handler_source"], handler_source)
        self.assertEqual(result["vast_cli_source"]["revision"], "abc123")
        self.assertFalse(result["vast_cli_source"]["dirty"])

    def test_markdown_links_handler_to_pinned_revision_and_line_range(self) -> None:
        result = {
            "vast_cli_source": {"branch": "main", "revision": "abc123", "dirty": False},
            "summary": {
                "source_files_scanned": 1,
                "documented_invocation_occurrences": 1,
                "documented_registered_signatures": 1,
                "actionable_findings": 0,
                "status_counts": {"pass": 1},
            },
            "records": [
                {
                    "file": "host/example.mdx",
                    "line": 9,
                    "executable": "vastai",
                    "signature": "list volume",
                    "flags": ["--size"],
                    "status": "pass",
                    "handler_source": {
                        "path": "vastai/cli/commands/storage.py",
                        "symbol": "list__volume",
                        "line_start": 40,
                        "line_end": 43,
                    },
                }
            ],
        }

        rendered = VERIFIER.render_markdown(result)

        self.assertIn(
            "https://github.com/vast-ai/vast-cli/blob/abc123/"
            "vastai/cli/commands/storage.py#L40-L43",
            rendered,
        )
        self.assertIn("`list__volume`", rendered)


if __name__ == "__main__":
    unittest.main()
